import os
import json
import re
import logging
import time
from typing import Any, List, Optional, Dict
import pandas as pd
import requests
import itertools
from datetime import datetime

from ecodi.env import (
    init_env,
    ecoDI_env,
    get_sysenv,
    set_env,
    unset_env,
    get_env,
    ecoDI_env,
    init_env,
    encode_base64,
    decode_base64,
    initial_meta
)

from ecodi.dbms import (
    _match_arg,
    _build_connection_string,
    db_connect,
    meta_connect,
    ods_connect,
    data_connect,
    is_connected,
    db_close,
    query_from_file,
    get_connection,
    getquery,
    deletequery,
    is_tabled,
    db_settable,
    db_load_csv,
    db_send_query
)

  
# ----------------------------------------------------------------------
# Core translation functions
# ----------------------------------------------------------------------
def desc_kosis_stats(
    tbl_id: Optional[str] = None,
    org_id: Optional[str] = None,
    type_: str = "TBL",
    api_key: Optional[str] = None,
    verbose: bool = False,
) -> pd.DataFrame:
    """
    Retrieve KOSIS table metadata and optionally prune columns for ITEM type.

    Parameters
    ----------
    tbl_id : str, optional
        Table identifier (required).
    org_id : str, optional
        Organization identifier (required).
    type_ : str, default "TBL"
        One of {"TBL","ORG","PRD","ITM","CMMT","UNIT","SOURCE","NCD"}.
    api_key : str, optional
        KOSIS API key. If omitted, taken from the KOSIS_API_KEY environment variable.
    verbose : bool, default False
        If True, prints the constructed API URL.

    Returns
    -------
    pd.DataFrame
        The parsed JSON response. For non‑data‑frame results the raw object
        (e.g., dict) is returned.
    """
    if tbl_id is None or org_id is None:
        raise ValueError("Both 'tbl_id' and 'org_id' must be provided.")

    if api_key is None:
        api_key = os.getenv("KOSIS_API_KEY")

    if not api_key:
        raise ValueError("API key is missing. Please provide a valid KOSIS API key.")

    allowed_types = {
        "TBL", "ORG", "PRD", "ITM", "CMMT",
        "UNIT", "SOURCE", "NCD"
    }
    if type_ not in allowed_types:
        raise ValueError(f"type must be one of {allowed_types}")

    api_url = (
        "https://kosis.kr/openapi/statisticsData.do"
        "?method=getMeta"
        f"&apiKey={api_key}"
        f"&format=json"
        f"&type={type_}"
        f"&orgId={org_id}"
        f"&tblId={tbl_id}"
        "&jsonVD=Y"
    )

    if verbose:
        logging.info(f"KOSIS API URL: {api_url}")

    response = requests.get(api_url)
    response.raise_for_status()
    raw_text = response.text

    # Try to parse the JSON; if it fails, escape backslashes and retry.
    try:
        df_desc = pd.json_normalize(json.loads(raw_text))
    except json.JSONDecodeError:
        escaped_text = re.sub(r"\\", r"\\\\", raw_text)
        df_desc = pd.json_normalize(json.loads(escaped_text))

    # When the result is not a DataFrame, return the raw JSON object.
    if not isinstance(df_desc, pd.DataFrame) or df_desc.empty:
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            return escaped_text  # fallback

    # Special handling for ITEM type (ITM)
    if type_ == "ITM":
        desired_columns = [
            "ORG_ID", "OBJ_ID", "OBJ_NM", "OBJ_ID_SN", "OBJ_NM_ENG",
            "UP_ITM_ID", "ITM_NM", "ITM_ID", "ITM_NM_ENG",
            "UNIT_ID", "UNIT_NM", "UNIT_ENG_NM",
        ]
        existing = [col for col in desired_columns if col in df_desc.columns]
        df_desc = df_desc[existing]

    return df_desc


def from_meta_kosisdesc(
    tbl_id: Optional[str] = None,
    org_id: Optional[str] = None,
    type_: str = "TBL",
    verbose: bool = False,
) -> pd.DataFrame:
    """
    Retrieve previously stored KOSIS metadata from the `ecodi_meta`
    database.

    Parameters
    ----------
    tbl_id : str, optional
        Table identifier (required).
    org_id : str, optional
        Organization identifier (required).
    type_ : str, default "TBL"
        One of {"TBL","ORG","PRD","ITM","CMMT","UNIT","SOURCE","NCD"}.
    verbose : bool, default False
        If True, prints the generated SQL query.

    Returns
    -------
    pd.DataFrame
        The metadata record(s) without the audit columns.
    """
    if tbl_id is None or org_id is None:
        raise ValueError("Both 'tbl_id' and 'org_id' must be provided.")

    if not is_connected("meta"):
        db_connect("meta")

    allowed_types = {
        "TBL", "ORG", "PRD", "ITM", "CMMT",
        "UNIT", "SOURCE", "NCD"
    }
    if type_ not in allowed_types:
        raise ValueError(f"type must be one of {allowed_types}")

    sql = (
        f"SELECT *\n"
        f"  FROM ecodi_meta.mt_kosis_{type_.lower()}\n"
        f" WHERE tbl_id = '{tbl_id}'\n"
        f"   AND org_id = '{org_id}'"
    )

    if verbose:
        logging.info(f"Running SQL query:\n{sql}")

    result = getquery(sql)

    # Drop typical audit columns if present
    audit_cols = ["cret_dt", "cret_nm", "mdfy_dt", "mdfy_nm"]
    cols_to_keep = [c for c in result.columns if c not in audit_cols]
    result = result[cols_to_keep]

    return result


def get_kosis_indexpl(
    ind_id: Optional[str] = None,
    api_key: Optional[str] = None,
    verbose: bool = False,
    **kwargs,
) -> pd.DataFrame:
    """
    Retrieve KOSIS indicator (index) information.

    Parameters
    ----------
    ind_id : str, optional
        Indicator identifier (required).
    api_key : str, optional
        KOSIS API key. If omitted, taken from the KOSIS_API_KEY environment variable.
    verbose : bool, default False
        If True, prints the constructed API URL.
    **kwargs
        Additional arguments kept for API compatibility (ignored in this implementation).

    Returns
    -------
    pd.DataFrame
        A tidy DataFrame with six standardized columns.
    """
    if ind_id is None:
        raise ValueError("'ind_id' must be provided.")

    if api_key is None:
        api_key = os.getenv("KOSIS_API_KEY")

    if not api_key:
        raise ValueError("API key is missing. Please provide a valid KOSIS API key.")

    api_url = (
        "https://kosis.kr/openapi/pkNumberService.do"
        "?method=getList"
        f"&apiKey={api_key}"
        f"&format=json"
        f"&jipyoId={ind_id}"
        "&jsonVD=Y"
    )

    if verbose:
        logging.info(f"KOSIS API URL: {api_url}")

    response = requests.get(api_url)
    response.raise_for_status()
    result_json = response.json()

    # If the result is not a list/dict that can be turned into a DataFrame, return it directly.
    if not isinstance(result_json, (list, dict)):
        return result_json

    df = pd.json_normalize(result_json)

    # Ensure the six expected columns exist
    expected_cols = [
        "jipyoId",
        "jipyoNm",
        "jipyoExplan",
        "jipyoExplan1",
        "jipyoExplan2",
        "jipyoExplan3",
    ]

    missing = [c for c in expected_cols if c not in df.columns]
    for col in missing:
        df[col] = pd.NA

    df = df[expected_cols]

    df.columns = [
        "IND_ID",
        "IND_NM",
        "IND_TITLE",
        "IND_DEFINE",
        "IND_EXPRSN",
        "IND_SRC",
    ]

    return df



# ----------------------------------------------------------------------
# Main function
# ----------------------------------------------------------------------
def get_kosis_stats(
    tbl_id: Optional[str] = None,
    org_id: Optional[str] = None,
    objL1: str = "",
    objL2: str = "",
    objL3: str = "",
    objL4: str = "",
    objL5: str = "",
    objL6: str = "",
    objL7: str = "",
    objL8: str = "",
    all_obj: bool = True,
    start_prd: Optional[str] = None,
    end_prd: Optional[str] = None,
    all_prd: bool = False,
    period_se: List[str] = None,
    auto_period: bool = True,
    api_key: Optional[str] = None,
    verbose: bool = False,
    **_: Any,
) -> pd.DataFrame:
    """
    Retrieve KOSIS statistical data.

    Mirrors the behaviour of the original R function `get_kosis_stats`.
    """

    # ------------------------------------------------------------------
    # Argument preparation & validation
    # ------------------------------------------------------------------
    period_se = period_se or ["M", "Y", "H", "Q", "D", "F", "IR"]
    period_se = period_se[0] if isinstance(period_se, list) else period_se  # match.arg behaviour

    if tbl_id is None or org_id is None:
        raise ValueError("Both `tbl_id` and `org_id` must be provided.")

    api_key = api_key or os.getenv("KOSIS_API_KEY", "")
    if not api_key:
        raise ValueError("API key is missing. Set `api_key` argument or KOSIS_API_KEY env var.")

    # ------------------------------------------------------------------
    # ITEM (ITM) metadata
    # ------------------------------------------------------------------
    df_itm = desc_kosis_stats(tbl_id=tbl_id, org_id=org_id, type_="ITM", verbose=verbose)

    if df_itm.empty:
        raise ValueError("No ITEM metadata returned.")

    # itmId = concatenated ITM_ID values where OBJ_ID == "ITEM"
    itm_filter = df_itm["OBJ_ID"] == "ITEM"
    itm_id_series = df_itm.loc[itm_filter, "ITM_ID"]
    itmId = "+".join(itm_id_series.astype(str).tolist())

    if not itmId:
        raise ValueError("Item ID string is empty – cannot continue.")

    # ------------------------------------------------------------------
    # Optional object level handling
    # ------------------------------------------------------------------
    # Prepare a mutable mapping for objL1 … objL8 that can be overridden later
    obj_levels: Dict[int, str] = {
        1: objL1, 2: objL2, 3: objL3, 4: objL4,
        5: objL5, 6: objL6, 7: objL7, 8: objL8,
    }

    if all_obj:
        # Distinct non‑NA OBJ_ID_SN values
        obj_sn_series = df_itm["OBJ_ID_SN"].dropna().unique()

        for idx, obj_sn in enumerate(obj_sn_series, start=1):
            # Concatenate ITM_ID for the current OBJ_ID_SN
            mask = df_itm["OBJ_ID_SN"] == obj_sn
            itm_ids = df_itm.loc[mask, "ITM_ID"]
            param_str = "+".join(itm_ids.astype(str).tolist())

            # Truncate long parameter strings
            if len(param_str) >= 500:
                param_str = "ALL"

            # Assign to the appropriate objL* variable (if within 1‑8)
            if idx <= 8:
                obj_levels[idx] = param_str

    # ------------------------------------------------------------------
    # PERIOD (PRD) metadata
    # ------------------------------------------------------------------
    df_prd = desc_kosis_stats(tbl_id=tbl_id, org_id=org_id, type_="PRD", verbose=verbose)
    df_prd.columns = df_prd.columns.str.lower()
    df_prd.rename(columns={df_prd.columns[0]: "prd_nm"}, inplace=True)

    df_prd_se = getquery(sql="select prd_se as prd_nm, prd_cd as prd_se from mt_kosis_prdse", schema="meta")

    if auto_period:
        period_se = ["M", "Y", "H", "Q", "D", "F", "IR"]

    # Merge period selection metadata
    df_prd = (
        df_prd_se.merge(df_prd, how="inner", left_on="prd_nm", right_on="prd_nm")
        .loc[lambda d: d["prd_se"].isin(period_se)]
        .assign(
            strt_prd_de=lambda d: d["strt_prd_de"].apply(lambda x: re.sub(r"[^0-9]", "", str(x))),
            end_prd_de=lambda d: d["end_prd_de"].apply(lambda x: re.sub(r"[^0-9]", "", str(x))),
        )
        .reset_index(drop=True)
    )

    if not auto_period and df_prd.empty:
        raise ValueError("No period metadata after filtering.")

    # ------------------------------------------------------------------
    # Determine start / end period and newest period count
    # ------------------------------------------------------------------
    newest_prdcnt = 0

    if all_prd:
        start_prd = df_prd.at[0, "strt_prd_de"]
        end_prd = df_prd.at[0, "end_prd_de"]
    else:
        if start_prd is None and end_prd is None:
            newest_prdcnt = 2
        else:
            if start_prd is None:
                start_prd = df_prd.at[0, "strt_prd_de"]
            if end_prd is None:
                end_prd = df_prd.at[0, "end_prd_de"]

    prd_se = df_prd.at[0, "prd_se"]

    # ------------------------------------------------------------------
    # Build request URL
    # ------------------------------------------------------------------
    base_url = (
        "https://kosis.kr/openapi/Param/statisticsParameterData.do"
        "?method=getList&apiKey={api_key}&format=json&orgId={org_id}"
        "&tblId={tbl_id}&objL1={objL1}&itmId={itmId}&prdSe={prd_se}"
    ).format(
        api_key=api_key,
        org_id=org_id,
        tbl_id=tbl_id,
        objL1=obj_levels.get(1, ""),
        itmId=itmId,
        prd_se=prd_se,
    )

    # Append remaining objL* parameters (2‑8) and request flags
    base_url += (
        "&objL2={objL2}&objL3={objL3}&objL4={objL4}"
        "&objL5={objL5}&objL6={objL6}&objL7={objL7}&objL8={objL8}"
        "&jsonVD=Y"
    ).format(
        objL2=obj_levels.get(2, ""),
        objL3=obj_levels.get(3, ""),
        objL4=obj_levels.get(4, ""),
        objL5=obj_levels.get(5, ""),
        objL6=obj_levels.get(6, ""),
        objL7=obj_levels.get(7, ""),
        objL8=obj_levels.get(8, ""),
    )

    if newest_prdcnt == 0:
        base_url += f"&startPrdDe={start_prd}&endPrdDe={end_prd}"
    else:
        base_url += f"&newEstPrdCnt={newest_prdcnt}"

    if verbose:
        print(f"KOSIS API URL: {api_url}")

    # ------------------------------------------------------------------
    # Request data
    # ------------------------------------------------------------------
    response = requests.get(base_url)
    response.raise_for_status()
    json_content = response.json()

    # If the returned JSON is not a tabular structure, return it as‑is
    if not isinstance(json_content, list) or not all(isinstance(item, dict) for item in json_content):
        return json_content

    df_desc = pd.json_normalize(json_content)

    if not isinstance(df_desc, pd.DataFrame):
        return json_content

    # ------------------------------------------------------------------
    # Column selection logic (mirrors original R code)
    # ------------------------------------------------------------------
    base_stats = ["ORG_ID", "TBL_ID", "TBL_NM"]
    for x in range(1, 9):
        base_stats.extend(
            [
                f"C{x}",
                f"C{x}_OBJ_NM",
                f"C{x}_OBJ_NM_ENG",
                f"C{x}_NM",
                f"C{x}_NM_ENG",
            ]
        )

    extra_stats = [
        "ITM_ID", "ITM_NM", "ITM_NM_ENG", "UNIT_ID", "UNIT_NM",
        "UNIT_NM_ENG", "PRD_SE", "PRD_DE", "DT", "LST_CHN_DE",
    ]

    all_possible = base_stats + extra_stats
    valid_columns = [col for col in all_possible if col in df_desc.columns]

    # Return the dataframe limited to the selected columns
    return df_desc[valid_columns].copy()
  

def get_kosis_info(
    tbl_id: Optional[str] = None,
    org_id: Optional[str] = None,
    api_key: Optional[str] = None,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Retrieve various KOSIS metadata for a given table and organization.

    Parameters
    ----------
    tbl_id : str, optional
        Identifier of the KOSIS table.
    org_id : str, optional
        Identifier of the KOSIS organization.
    api_key : str, optional
        API key for KOSIS. If not supplied, the environment variable
        ``KOSIS_API_KEY`` is used.
    verbose : bool, default False
        If ``True`` enables verbose output in the underlying API calls.
    **kwargs
        Additional arguments passed to ``desc_kosis_stats`` (kept for
        compatibility with the original R ``...`` argument).

    Returns
    -------
    dict
        A dictionary containing the metadata objects for the requested
        table, organization, items, products, comments, units, sources,
        and non‑code dimensions.
    """
    # Resolve API key from environment if not explicitly provided
    if api_key is None:
        api_key = os.getenv("KOSIS_API_KEY")

    # Validate required arguments
    if tbl_id is None or org_id is None:
        raise ValueError("Both 'tbl_id' and 'org_id' must be provided.")

    # Helper to call the (assumed) Python version of `desc_kosis_stats`
    def _fetch(type_name: str) -> Any:
        return desc_kosis_stats(
            tbl_id=tbl_id,
            org_id=org_id,
            type_=type_name,
            api_key=api_key,
            verbose=verbose,
        )

    # Retrieve each piece of information
    info_tbl = _fetch("TBL")
    info_org = _fetch("ORG")
    info_itm = _fetch("ITM")
    info_prd = _fetch("PRD")
    info_cmt = _fetch("CMMT")
    info_unt = _fetch("UNIT")
    info_src = _fetch("SOURCE")
    info_ncd = _fetch("NCD")

    # Assemble results in a dictionary (mirrors R's named list)
    return {
        "info_tbl": info_tbl,
        "info_org": info_org,
        "info_itm": info_itm,
        "info_prd": info_prd,
        "info_cmt": info_cmt,
        "info_unt": info_unt,
        "info_src": info_src,
        "info_ncd": info_ncd,
    }


def get_kosis_explanation(
    stat_id: str | None = None,
    api_key: str | None = None,
    verbose: bool = False,
    **kwargs,
) -> pd.DataFrame | dict:
    """
    Retrieve KOSIS statistics explanation data.

    Parameters
    ----------
    stat_id : str, required
        The statistic ID to query.
    api_key : str, optional
        KOSIS API key. If not supplied, the function reads the
        ``KOSIS_API_KEY`` environment variable.
    verbose : bool, default False
        If True, prints the request URL.
    **kwargs
        Additional parameters are ignored (kept for API compatibility).

    Returns
    -------
    pd.DataFrame
        DataFrame with the requested fields and a ``STAT_ID`` column.
    dict
        Raw JSON response when the result cannot be interpreted as a table.
    """
    if stat_id is None:
        raise ValueError("'stat_id' must be provided.")

    # Resolve API key
    if api_key is None:
        api_key = os.getenv("KOSIS_API_KEY")
    if not api_key:
        raise ValueError("API key not supplied and KOSIS_API_KEY env variable is empty.")

    # Build request URL
    base_url = (
        "https://kosis.kr/openapi/statisticsExplData.do"
        "?method=getList"
        f"&apiKey={api_key}"
        "&format=json"
    )
    api_url = (
        f"{base_url}"
        f"&statId={stat_id}"
        "&metaItm=All"
        "&jsonVD=Y"
        "&jsonMVD=Y"
    )

    if verbose:
        logging.info(f"KOSIS API URL: {api_url}")

    # Perform request
    response = requests.get(api_url, timeout=30)
    response.raise_for_status()
    result_json = response.json()

    # If the JSON is not a list of records, return it unchanged
    if not isinstance(result_json, (list, tuple)):
        return result_json

    # Convert to DataFrame
    df = pd.DataFrame(result_json)

    # Expected column names from the API
    api_columns = [
        "statsNm",
        "statsKind",
        "statsEnd",
        "statsContinue",
        "basisLaw",
        "writingPurps",
        "examinPd",
        "statsPeriod",
        "writingSystem",
        "writingTel",
        "statsField",
        "examinObjrange",
        "examinObjArea",
        "josaUnit",
        "applyGroup",
        "josaItm",
        "pubPeriod",
        "pubExtent",
        "pubDate",
        "publictMth",
        "examinTrgetPd",
        "dataUserNote",
        "mainTermExpl",
        "dataCollectMth",
        "examinHistory",
        "confmNo",
        "confmDt",
    ]

    # Identify missing columns and add them with NA (NaN) values
    missing_columns = [col for col in api_columns if col not in df.columns]
    for col in missing_columns:
        df[col] = pd.NA

    # Keep only the columns we care about, in the defined order
    df = df[api_columns]

    # Rename to the upper‑case constant style used in the original R code
    rename_map = {
        "statsNm": "STAT_NM",
        "statsKind": "STAT_KIND",
        "statsEnd": "STAT_END",
        "statsContinue": "STAT_CONTINUE",
        "basisLaw": "BASIS_LAW",
        "writingPurps": "WRITING_PURPS",
        "examinPd": "EXAMIN_PD",
        "statsPeriod": "STAT_PERIOD",
        "writingSystem": "WRITING_SYSTEM",
        "writingTel": "WRITING_TEL",
        "statsField": "STAT_FIELD",
        "examinObjrange": "EXAMIN_OBJRANGE",
        "examinObjArea": "EXAMIN_OBJAREA",
        "josaUnit": "JOSA_UNIT",
        "applyGroup": "APPLY_GROUP",
        "josaItm": "JOSA_ITM",
        "pubPeriod": "PUB_PERIOD",
        "pubExtent": "PUB_EXTENT",
        "pubDate": "PUB_DATE",
        "publictMth": "PUBLICT_MTH",
        "examinTrgetPd": "EXAMIN_TRGET_PD",
        "dataUserNote": "DATA_USER_NOTE",
        "mainTermExpl": "MAIN_TERM_EXPL",
        "dataCollectMth": "DATA_COLLECT_MTH",
        "examinHistory": "EXAMIN_HISTORY",
        "confmNo": "CONFM_NO",
        "confmDt": "CONFM_DATE",
    }
    df = df.rename(columns=rename_map)

    # Attach the provided STAT_ID as a new column
    df.insert(0, "STAT_ID", stat_id)

    return df
  


# ----------------------------------------------------------------------
# Function: kosis_stats_list
# ----------------------------------------------------------------------
def kosis_stats_list(vw_cd: Optional[str] = None) -> pd.DataFrame:
    """
    Retrieve statistics list. If `vw_cd` is not supplied the function returns
    the top‑level value‑sets; otherwise it returns the children of the given
    `vw_cd`.

    Parameters
    ----------
    vw_cd : str or None, default None
        Parent value‑set code.

    Returns
    -------
    pd.DataFrame
        Result of the SQL query.
    """
    if vw_cd is None:
        sql = """
            SELECT value_set AS vw_cd,
                   value_set_desc AS vw_nm
            FROM ecodi_meta.mt_api_paramset
            WHERE param_seq = 2;
        """
    else:
        sql = f"""
            SELECT value_set AS parent_id,
                   value_set_desc AS parent_nm
            FROM ecodi_meta.mt_api_paramset
            WHERE param_seq = 3
              AND parent_set = '{vw_cd}';
        """
    return getquery(sql, schema="meta")


# ----------------------------------------------------------------------
# Function: kosis_list_level1
# ----------------------------------------------------------------------
DEFAULT_VW_CD_LEVEL1: List[str] = [
    "MT_ZTITLE", "MT_OTITLE", "MT_GTITLE01", "MT_GTITLE02", "MT_GTITLE03",
    "MT_CHOSUN_TITLE", "MT_RTITLE", "MT_HANKUK_TITLE", "MT_BUKHAN",
    "MT_STOP_TITLE", "MT_TM1_TITLE", "MT_TM2_TITLE"
]

def kosis_list_level1(vw_cd: Optional[str] = None) -> pd.DataFrame:
    """
    List level‑1 statistics for a selected `vw_cd`.

    Parameters
    ----------
    vw_cd : str or None, default None
        One of the predefined statistic codes. If omitted, the first code in
        `DEFAULT_VW_CD_LEVEL1` is used.

    Returns
    -------
    pd.DataFrame
        Result of the SQL query.
    """
    # Resolve the argument similarly to R's `match.arg`
    if vw_cd is None:
        vw_cd = DEFAULT_VW_CD_LEVEL1[0]
    elif vw_cd not in DEFAULT_VW_CD_LEVEL1:
        raise ValueError(f"`vw_cd` must be one of {DEFAULT_VW_CD_LEVEL1}")

    sql = f"""
        SELECT vw_cd,
               vw_nm,
               list_id,
               list_nm
        FROM ecodi_meta.mt_kosis_stat
        WHERE 1 = 1
          AND tbl_id = ''
          AND parent_id = ''
          AND vw_cd = '{vw_cd}'
        GROUP BY vw_cd, vw_nm, list_id, list_nm
        ORDER BY list_id;
    """
    return getquery(sql, schema="meta")


# ----------------------------------------------------------------------
# Function: kosis_list_parent
# ----------------------------------------------------------------------
def kosis_list_parent(vw_cd: Optional[str] = None,
                      parent_id: Optional[str] = None) -> pd.DataFrame:
    """
    Retrieve statistics for a specific parent identifier.

    Parameters
    ----------
    vw_cd : str or None, default None
        One of the predefined statistic codes (same set as `kosis_list_level1`).
        If omitted, the first code in the default list is used.
    parent_id : str, required
        Identifier of the parent record. Must be supplied.

    Returns
    -------
    pd.DataFrame
        Result of the SQL query.
    """
    if vw_cd is None:
        vw_cd = DEFAULT_VW_CD_LEVEL1[0]
    elif vw_cd not in DEFAULT_VW_CD_LEVEL1:
        raise ValueError(f"`vw_cd` must be one of {DEFAULT_VW_CD_LEVEL1}")

    if parent_id is None:
        raise ValueError("'parent_id' must be provided.")

    sql = f"""
        SELECT parent_id,
               vw_cd,
               vw_nm,
               list_id,
               list_nm,
               org_id,
               tbl_id,
               tbl_nm,
               stat_id,
               send_de,
               rec_tbl_se
        FROM ecodi_meta.mt_kosis_stat
        WHERE 1 = 1
          AND tbl_id = ''
          AND parent_id = '{parent_id}'
          AND vw_cd = '{vw_cd}';
    """
    return getquery(sql, schema="meta")
  
  
def kosis_list_stats(
    vw_cd: str = "MT_ZTITLE",
    parent_id: Optional[str] = None,
    parent_nm: Optional[str] = None,
    recursive: bool = False,
    verbose: bool = False,
) -> pd.DataFrame:
    """
    Retrieve KOSIS statistics metadata.

    Parameters
    ----------
    vw_cd : str
        View code. Must be one of the allowed values.
    parent_id : str
        Identifier of the parent node (required).
    parent_nm : str, optional
        Name of the parent node. If omitted it will be fetched from the DB.
    recursive : bool, default False
        When ``True`` the function walks the hierarchy recursively.
    verbose : bool, default False
        Verbosity flag (currently only used for printing info messages).

    Returns
    -------
    pd.DataFrame
        A data‑frame whose first column is ``parent_nm`` followed by the
        remaining columns from the underlying ``mt_kosis_stat`` table.
    """
    # ------------------------------------------------------------------
    # Argument validation (mirrors R's match.arg)
    # ------------------------------------------------------------------
    allowed_vw = [
        "MT_ZTITLE", "MT_OTITLE", "MT_GTITLE01", "MT_GTITLE02",
        "MT_GTITLE03", "MT_CHOSUN_TITLE", "MT_RTITLE",
        "MT_HANKUK_TITLE", "MT_BUKHAN", "MT_STOP_TITLE",
        "MT_TM1_TITLE", "MT_TM2_TITLE",
    ]
    if vw_cd not in allowed_vw:
        raise ValueError(f"vw_cd must be one of {allowed_vw}")

    if parent_id is None:
        raise ValueError("'parent_id' must be provided.")

    # --------------------------------------------------------------
    # Resolve parent name if it was not supplied
    # --------------------------------------------------------------
    if parent_nm is None:
        sql = f"""
            SELECT list_nm AS parent_nm
            FROM ecodi_meta.mt_kosis_stat
            WHERE 1 = 1
              AND list_id = '{parent_id}'
              AND vw_cd = '{vw_cd}';
            """
        # getquery returns a DataFrame; we keep only the scalar value
        parent_nm_df = getquery(sql, schema="meta").loc[:, "parent_nm"]
        if parent_nm_df.empty:
            raise ValueError("Parent name not found in the database.")
        parent_nm = parent_nm_df.iloc[0]

    # --------------------------------------------------------------
    # Non‑recursive mode
    # --------------------------------------------------------------
    if not recursive:
        sql = f"""
            SELECT parent_id, vw_cd, vw_nm, list_id, list_nm, org_id,
                   tbl_id, tbl_nm, stat_id, send_de, rec_tbl_se,
                   '' AS path_nm
            FROM ecodi_meta.mt_kosis_stat
            WHERE 1 = 1
              AND tbl_id <> ''
              AND parent_id = '{parent_id}'
              AND vw_cd = '{vw_cd}';
            """
        result = getquery(sql, schema="meta")

        if result.empty:
            raise ValueError(
                "Data not found. Please set 'recursive=True' to retrieve all "
                "statistics information under the specified parent ID."
            )

        # add the parent name as the last column (mirrors dplyr::mutate)
        result["parent_nm"] = parent_nm

        # move the newly added column to the first position
        cols = result.columns.tolist()
        result = result[[cols[-1]] + cols[:-1]]

        return result

    # --------------------------------------------------------------
    # Recursive mode
    # --------------------------------------------------------------
    sql = f"""
        SELECT parent_id, vw_cd, vw_nm, list_id, list_nm, org_id,
               tbl_id, tbl_nm, stat_id, send_de, rec_tbl_se
        FROM ecodi_meta.mt_kosis_stat
        WHERE 1 = 1
          AND parent_id = '{parent_id}'
          AND vw_cd = '{vw_cd}';
        """
    result = getquery(sql, schema="meta")

    if result.empty:
        raise ValueError(
            "Data not found. Please set 'recursive=True' to retrieve all "
            "statistics information under the specified parent ID."
        )

    # Build hierarchical name (parent_nm > list_nm) when list_nm exists
    result["parent_nm"] = result.apply(
        lambda row: parent_nm
        if pd.isna(row["list_nm"])
        else f'{parent_nm} > {row["list_nm"]}',
        axis=1,
    )

    # Separate rows that contain actual statistics (tbl_id != '') from
    # those that are just containers (tbl_id == '')
    is_stats_list = result[result["tbl_id"] != ""].copy()
    no_stats_list = result[result["tbl_id"] == ""].copy()

    # Recurse into each container node
    if not no_stats_list.empty:
        for _, row in no_stats_list.iterrows():
            if verbose:
                print(
                    f"Processing recursive parent_id: {row['list_id']}"
                )
            # Recursive call – note that we pass the already‑computed
            # hierarchical name for the child as ``parent_nm``.
            temp_result = kosis_list_stats(
                vw_cd=vw_cd,
                parent_id=row["list_id"],
                parent_nm=row["parent_nm"],
                recursive=True,
                verbose=verbose,
            )
            is_stats_list = pd.concat([is_stats_list, temp_result], ignore_index=True)

    # Re‑order columns: bring ``parent_nm`` to the front
    cols = is_stats_list.columns.tolist()
    is_stats_list = is_stats_list[[cols[-1]] + cols[:-1]]

    return is_stats_list


def kosis_org_list(org_id: Optional[str] = None, is_short: bool = True) -> pd.DataFrame:
    """
    Retrieve organization metadata from the KOSIS catalog.

    Parameters
    ----------
    org_id : str, optional
        When supplied the query is limited to this identifier.
    is_short : bool, default True
        If ``True`` only ``org_id`` and ``org_nm`` are returned;
        otherwise all columns except a few audit columns are returned.

    Returns
    -------
    pd.DataFrame
        The queried organization information.
    """
    if org_id is None:
        sql = """
            SELECT *
            FROM ecodi_meta.mt_kosis_org
            ORDER BY org_nm;
            """
    else:
        sql = f"""
            SELECT *
            FROM ecodi_meta.mt_kosis_org
            WHERE 1 = 1
              AND org_id = '{org_id}';
            """

    df = getquery(sql, schema="meta")

    if is_short:
        # Keep only the two identifier columns
        result = df.loc[:, ["org_id", "org_nm"]]
    else:
        # Drop internal audit columns if they exist
        drop_cols = {"cret_dt", "cret_nm", "mdfy_dt", "mdfy_nm"}
        existing_drop = [c for c in drop_cols if c in df.columns]
        result = df.drop(columns=existing_drop)

    return result


def import_kosis_indexpl(
    ind_id: Optional[str] = None,
    sleep_seconds: int = 0,
    verbose: bool = True,
    dbms: str = get_env("ecoDI_DBMS")
) -> bool:
    """
    Import KOSIS index explanation data into the `mt_kosis_indexpl` table
    and log the operation in `mt_log_dataimp`.

    Parameters
    ----------
    ind_id : str
        Identifier of the KOSIS index to import (required).
    sleep_seconds : int, default 0
        Optional pause before starting the import.
    verbose : bool, default True
        Whether to print informational messages.
    dbms : str
        Database management system; defaults to the value of the
        `ecoDI_DBMS` environment variable.
    Returns
    -------
    bool
        ``True`` if the data was successfully appended, ``False`` otherwise.
    """
    if ind_id is None:
        raise ValueError("'ind_id' must be provided.")

    schema = "meta"

    # Optional sleep before starting the import
    if sleep_seconds:
        time.sleep(sleep_seconds)

    if verbose:
        logging.info(f"Importing KOSIS index explain for index ID: {ind_id}")

    # Initialise status tracking
    is_ok = False
    set_env("STATUS", "1")
    set_env("EMSG", "")

    start_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ------------------------------------------------------------------
    # Retrieve the explanation data
    # ------------------------------------------------------------------
    try:
        explain_info = get_kosis_indexpl(ind_id=ind_id, verbose=verbose)
    except Exception as exc:
        # If the helper raises, we treat it as a failure and store the message
        set_env("STATUS", "0")
        set_env("EMSG", str(exc))
        explain_info = pd.DataFrame()

    if not isinstance(explain_info, pd.DataFrame):
        # Assume the returned object contains an ``errMsg`` attribute
        error_msg = getattr(explain_info, "errMsg", "Unknown error")
        set_env("STATUS", "0")
        set_env("EMSG", error_msg)
        df_data = pd.DataFrame()
    else:
        df_data = explain_info

    # ------------------------------------------------------------------
    # Gather connection / user information
    # ------------------------------------------------------------------
    uid = get_env("USERNAME")
    # Decode the base‑64 encoded DB information string
    encoded_info = get_env(f"{schema.upper()}_INFO")
    dbinfo = decode_base64(encoded_info)
    dbid = dbinfo.split(":")[0]

    table_id = "mt_kosis_indexpl"
    table_nm = "KOSIS 지표설명"

    # ------------------------------------------------------------------
    # No data case – just log the attempt
    # ------------------------------------------------------------------
    if df_data.empty:
        if verbose:
            logging.info(
                f"No data retrieved for index ID: {ind_id}. Import operation aborted."
            )
        end_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "0"
        rcnt = ccnt = 0
        emsg = get_env("EMSG")
        schema_nm = f"ecodi_{schema}"
        insert_sql = (
            f"INSERT INTO ecodi_meta.mt_log_dataimp "
            f"(user_id, db_id, schema_nm, start_dt, end_dt, data_id, "
            f"table_id, table_nm, api_params, record_cnt, column_cnt, "
            f"status, error_msg, cret_nm) VALUES ("
            f"'{uid}', '{dbid}', '{schema_nm}', '{start_dt}', '{end_dt}', "
            f"'', '{table_id.upper()}', '{table_nm}', 'explain for {ind_id}', "
            f"{rcnt}, {ccnt}, '{status}', '{emsg}', '{uid}');"
        )
    else:
        # ------------------------------------------------------------------
        # Normal case – ensure DB connection and load data
        # ------------------------------------------------------------------
        if not is_connected(schema):
            db_connect(schema)

        # Count rows before inserting
        cnt_before_query = f"SELECT COUNT(*) FROM ecodi_meta.{table_id}"
        cnt_before = getquery(cnt_before_query, schema).iloc[0, 0]

        # Append the DataFrame to the target table
        is_ok = db_settable(
            name=table_id,
            value=df_data,
            append=True,
            schema=schema
        )

        # Count rows after inserting
        cnt_after_query = f"SELECT COUNT(*) FROM ecodi_meta.{table_id}"
        cnt_after = getquery(cnt_after_query, schema).iloc[0, 0]

        end_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = get_env("STATUS")
        emsg = get_env("EMSG")
        rcnt = int(cnt_after - cnt_before)
        ccnt = 0 if status == "0" else df_data.shape[1]

        schema_nm = f"ecodi_{schema}"
        insert_sql = (
            f"INSERT INTO ecodi_meta.mt_log_dataimp "
            f"(user_id, db_id, schema_nm, start_dt, end_dt, data_id, "
            f"table_id, table_nm, api_params, record_cnt, column_cnt, "
            f"status, error_msg, cret_nm) VALUES ("
            f"'{uid}', '{dbid}', '{schema_nm}', '{start_dt}', '{end_dt}', "
            f"'', '{table_id.upper()}', '{table_nm}', 'explain for {ind_id}', "
            f"{rcnt}, {ccnt}, '{status}', '{emsg}', '{uid}');"
        )

        # Close the connection for the working schema
        db_close(schema)

    # ------------------------------------------------------------------
    # Write the log entry into mt_log_dataimp
    # ------------------------------------------------------------------
    log_schema = "meta"
    db_connect(log_schema)
    db_send_query(insert_sql, log_schema)
        
    if verbose:
        logging.info(
            f"Imported record count: {rcnt}, column count: {ccnt}, status: {status}"
        )

    # Return the success flag (True when data was appended)
    return is_ok
  


def import_kosis_statexpl(
    stat_id: Optional[str] = None,
    sleep_seconds: int = 0,
    verbose: bool = True,
    dbms: str = get_env("ecoDI_DBMS")
) -> bool:
    """
    Import KOSIS index explanation data into the `mt_kosis_statexpl` table
    and log the operation in `mt_log_dataimp`.

    Parameters
    ----------
    stat_id : str
        Identifier of the KOSIS stat explain to import (required).
    sleep_seconds : int, default 0
        Optional pause before starting the import.
    verbose : bool, default True
        Whether to print informational messages.
    dbms : str
        Database management system; defaults to the value of the
        `ecoDI_DBMS` environment variable.
    Returns
    -------
    bool
        ``True`` if the data was successfully appended, ``False`` otherwise.
    """
    if stat_id is None:
        raise ValueError("'stat_id' must be provided.")

    schema = "meta"

    # Optional sleep before starting the import
    if sleep_seconds:
        time.sleep(sleep_seconds)

    if verbose:
        logging.info(f"Importing KOSIS stat explain for stat ID: {stat_id}")

    # Initialise status tracking
    is_ok = False
    set_env("STATUS", "1")
    set_env("EMSG", "")

    start_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ------------------------------------------------------------------
    # Retrieve the explanation data
    # ------------------------------------------------------------------
    try:
        explain_info = get_kosis_explanation(stat_id=stat_id, verbose=verbose)
    except Exception as exc:
        # If the helper raises, we treat it as a failure and store the message
        set_env("STATUS", "0")
        set_env("EMSG", str(exc))
        explain_info = pd.DataFrame()

    if not isinstance(explain_info, pd.DataFrame):
        # Assume the returned object contains an ``errMsg`` attribute
        error_msg = getattr(explain_info, "errMsg", "Unknown error")
        set_env("STATUS", "0")
        set_env("EMSG", error_msg)
        df_data = pd.DataFrame()
    else:
        df_data = explain_info

    # ------------------------------------------------------------------
    # Gather connection / user information
    # ------------------------------------------------------------------
    uid = get_env("USERNAME")
    # Decode the base‑64 encoded DB information string
    encoded_info = get_env(f"{schema.upper()}_INFO")
    dbinfo = decode_base64(encoded_info)
    dbid = dbinfo.split(":")[0]

    table_id = "mt_kosis_statexpl"
    table_nm = "KOSIS 통계조사 설명"

    # ------------------------------------------------------------------
    # No data case – just log the attempt
    # ------------------------------------------------------------------
    if df_data.empty:
        if verbose:
            logging.info(
                f"No data retrieved for table ID: {table_id}. Import operation aborted."
            )
        end_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "0"
        rcnt = ccnt = 0
        emsg = get_env("EMSG")
        schema_nm = f"ecodi_{schema}"
        insert_sql = (
            f"INSERT INTO ecodi_meta.mt_log_dataimp "
            f"(user_id, db_id, schema_nm, start_dt, end_dt, data_id, "
            f"table_id, table_nm, api_params, record_cnt, column_cnt, "
            f"status, error_msg, cret_nm) VALUES ("
            f"'{uid}', '{dbid}', '{schema_nm}', '{start_dt}', '{end_dt}', "
            f"'', '{table_id.upper()}', '{table_nm}', 'explain for {stat_id}', "
            f"{rcnt}, {ccnt}, '{status}', '{emsg}', '{uid}');"
        )
    else:
        # ------------------------------------------------------------------
        # Normal case – ensure DB connection and load data
        # ------------------------------------------------------------------
        if not is_connected(schema):
            db_connect(schema)

        # Count rows before inserting
        cnt_before_query = f"SELECT COUNT(*) FROM ecodi_meta.{table_id}"
        cnt_before = getquery(cnt_before_query, schema).iloc[0, 0]

        # Append the DataFrame to the target table
        is_ok = db_settable(
            name=table_id,
            value=df_data,
            append=True,
            schema=schema
        )

        # Count rows after inserting
        cnt_after_query = f"SELECT COUNT(*) FROM ecodi_meta.{table_id}"
        cnt_after = getquery(cnt_after_query, schema).iloc[0, 0]

        end_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = get_env("STATUS")
        emsg = get_env("EMSG")
        rcnt = int(cnt_after - cnt_before)
        ccnt = 0 if status == "0" else df_data.shape[1]

        schema_nm = f"ecodi_{schema}"
        insert_sql = (
            f"INSERT INTO ecodi_meta.mt_log_dataimp "
            f"(user_id, db_id, schema_nm, start_dt, end_dt, data_id, "
            f"table_id, table_nm, api_params, record_cnt, column_cnt, "
            f"status, error_msg, cret_nm) VALUES ("
            f"'{uid}', '{dbid}', '{schema_nm}', '{start_dt}', '{end_dt}', "
            f"'', '{table_id.upper()}', '{table_nm}', 'explain for {stat_id}', "
            f"{rcnt}, {ccnt}, '{status}', '{emsg}', '{uid}');"
        )

        # Close the connection for the working schema
        db_close(schema)

    # ------------------------------------------------------------------
    # Write the log entry into mt_log_dataimp
    # ------------------------------------------------------------------
    log_schema = "meta"
    db_connect(log_schema)
    db_send_query(insert_sql, log_schema)
        
    if verbose:
        logging.info(
            f"Imported record count: {rcnt}, column count: {ccnt}, status: {status}"
        )

    # Return the success flag (True when data was appended)
    return is_ok
  
  
def import_kosis_item(
    tbl_id: Optional[str] = None,
    org_id: Optional[str] = None,
    sleep_seconds: int = 0,
    verbose: bool = True,
    dbms: str = get_env("ecoDI_DBMS")
) -> bool:
    """
    Import KOSIS item data into the `import_kosis_item` table
    and log the operation in `mt_log_dataimp`.

    Parameters
    ----------
    tbl_id : str
        Identifier of the KOSIS table to import (required).
    org_id : str
        Identifier of the KOSIS organization to import (required).        
    sleep_seconds : int, default 0
        Optional pause before starting the import.
    verbose : bool, default True
        Whether to print informational messages.
    dbms : str
        Database management system; defaults to the value of the
        `ecoDI_DBMS` environment variable.
    Returns
    -------
    bool
        ``True`` if the data was successfully appended, ``False`` otherwise.
    """
    if tbl_id is None or org_id is None:
        raise ValueError("'tbl_id' and 'org_id' must be provided.")

    schema = "meta"

    # Optional sleep before starting the import
    if sleep_seconds:
        time.sleep(sleep_seconds)

    if verbose:
        logging.info(f"Importing KOSIS item imformation for table ID: {tbl_id}")

    # Initialise status tracking
    is_ok = False
    set_env("STATUS", "1")
    set_env("EMSG", "")

    start_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ------------------------------------------------------------------
    # Retrieve the item data
    # ------------------------------------------------------------------
    try:
        item_info = desc_kosis_stats(tbl_id=tbl_id, org_id=org_id, 
                                     type_="ITM", verbose=verbose)
    except Exception as exc:
        # If the helper raises, we treat it as a failure and store the message
        set_env("STATUS", "0")
        set_env("EMSG", str(exc))
        item_info = pd.DataFrame()

    if not isinstance(item_info, pd.DataFrame):
        # Try to obtain the error message – it may be an attribute or a dict key.
        emsg = getattr(item_info, "errMsg", None) or item_info.get("errMsg") if isinstance(item_info, dict) else None
    
        set_env("STATUS", "0")
        set_env("EMSG", emsg if emsg is not None else "")
    
        df_data = item_info                     # keep the original (error) object
    else:
        # Build a new DataFrame that adds the identifying columns and a sequence number.
        # `itm_seq` mimics R's `seq_len(nrow(item_info))`.
        additional_cols = pd.DataFrame({
            "tbl_id": tbl_id,
            "org_id": org_id,
            "itm_seq": range(1, len(item_info) + 1)   # 1‑based sequence
        })
    
        # Concatenate the extra columns with the original data.
        df_data = pd.concat([additional_cols, item_info.reset_index(drop=True)], axis=1)
    
        # Remove the column `ORG_ID` if it exists (equivalent to `select(-ORG_ID)` in R).
        if "ORG_ID" in df_data.columns:
            df_data = df_data.drop(columns="ORG_ID")

    # ------------------------------------------------------------------
    # Gather connection / user information
    # ------------------------------------------------------------------
    uid = get_env("USERNAME")
    # Decode the base‑64 encoded DB information string
    encoded_info = get_env(f"{schema.upper()}_INFO")
    dbinfo = decode_base64(encoded_info)
    dbid = dbinfo.split(":")[0]

    table_id = "mt_kosis_itm"
    table_nm = "KOSIS 데이터 항목 정보"

    # ------------------------------------------------------------------
    # No data case – just log the attempt
    # ------------------------------------------------------------------
    if df_data.empty:
        if verbose:
            logging.info(
                f"No data retrieved for table ID: {table_id}. Import operation aborted."
            )
        end_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "0"
        rcnt = ccnt = 0
        emsg = get_env("EMSG")
        schema_nm = f"ecodi_{schema}"
        insert_sql = (
            f"INSERT INTO ecodi_meta.mt_log_dataimp "
            f"(user_id, db_id, schema_nm, start_dt, end_dt, data_id, "
            f"table_id, table_nm, api_params, record_cnt, column_cnt, "
            f"status, error_msg, cret_nm) VALUES ("
            f"'{uid}', '{dbid}', '{schema_nm}', '{start_dt}', '{end_dt}', "
            f"'', '{table_id.upper()}', '{table_nm}', '{tbl_id}', "
            f"{rcnt}, {ccnt}, '{status}', '{emsg}', '{uid}');"
        )
    else:
        # ------------------------------------------------------------------
        # Normal case – ensure DB connection and load data
        # ------------------------------------------------------------------
        if not is_connected(schema):
            db_connect(schema)

        # Count rows before inserting
        cnt_before_query = f"SELECT COUNT(*) FROM ecodi_meta.{table_id}"
        cnt_before = getquery(cnt_before_query, schema).iloc[0, 0]
    
        # Append the DataFrame to the target table
        is_ok = db_settable(
            name=table_id,
            value=df_data,
            append=True,
            schema=schema
        )

        # Count rows after inserting
        cnt_after_query = f"SELECT COUNT(*) FROM ecodi_meta.{table_id}"
        cnt_after = getquery(cnt_after_query, schema).iloc[0, 0]

        end_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = get_env("STATUS")
        emsg = get_env("EMSG")
        rcnt = int(cnt_after - cnt_before)
        ccnt = 0 if status == "0" else df_data.shape[1]

        schema_nm = f"ecodi_{schema}"
        insert_sql = (
            f"INSERT INTO ecodi_meta.mt_log_dataimp "
            f"(user_id, db_id, schema_nm, start_dt, end_dt, data_id, "
            f"table_id, table_nm, api_params, record_cnt, column_cnt, "
            f"status, error_msg, cret_nm) VALUES ("
            f"'{uid}', '{dbid}', '{schema_nm}', '{start_dt}', '{end_dt}', "
            f"'', '{table_id.upper()}', '{table_nm}', '{tbl_id}', "
            f"{rcnt}, {ccnt}, '{status}', '{emsg}', '{uid}');"
        )

        # Close the connection for the working schema
        db_close(schema)

    # ------------------------------------------------------------------
    # Write the log entry into mt_log_dataimp
    # ------------------------------------------------------------------
    log_schema = "meta"
    db_connect(log_schema)
    db_send_query(insert_sql, log_schema)
        
    if verbose:
        logging.info(
            f"Imported record count: {rcnt}, column count: {ccnt}, status: {status}"
        )

    # Return the success flag (True when data was appended)
    return is_ok
  

  
def import_kosis_tbl(
    tbl_id: Optional[str] = None,
    org_id: Optional[str] = None,
    sleep_seconds: int = 0,
    verbose: bool = True,
    dbms: str = get_env("ecoDI_DBMS")
) -> bool:
    """
    Import KOSIS data table information into the `mt_kosis_tbl` table
    and log the operation in `mt_log_dataimp`.

    Parameters
    ----------
    tbl_id : str
        Identifier of the KOSIS table to import (required).
    org_id : str
        Identifier of the KOSIS organization to import (required).        
    sleep_seconds : int, default 0
        Optional pause before starting the import.
    verbose : bool, default True
        Whether to print informational messages.
    dbms : str
        Database management system; defaults to the value of the
        `ecoDI_DBMS` environment variable.
    Returns
    -------
    bool
        ``True`` if the data was successfully appended, ``False`` otherwise.
    """
    if tbl_id is None or org_id is None:
        raise ValueError("'tbl_id' and 'org_id' must be provided.")

    schema = "meta"

    # Optional sleep before starting the import
    if sleep_seconds:
        time.sleep(sleep_seconds)

    if verbose:
        logging.info(f"Importing KOSIS data table imformation for table ID: {tbl_id}")

    # Initialise status tracking
    is_ok = False
    set_env("STATUS", "1")
    set_env("EMSG", "")

    start_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ------------------------------------------------------------------
    # Retrieve the item data
    # ------------------------------------------------------------------
    try:
        tbl_info = desc_kosis_stats(tbl_id=tbl_id, org_id=org_id, 
                                     type_="TBL", verbose=verbose)
    except Exception as exc:
        # If the helper raises, we treat it as a failure and store the message
        set_env("STATUS", "0")
        set_env("EMSG", str(exc))
        item_info = pd.DataFrame()

    # ----------------------------------------------------------------------
    # Case 1: `tbl_info` is NOT a DataFrame → treat it as an error object
    # ----------------------------------------------------------------------
    if not isinstance(tbl_info, pd.DataFrame):
        # Assume the error information is stored under the key 'errMsg'
        error_message = tbl_info.get("errMsg", "Unknown error")
        set_env("STATUS", "0")
        set_env("EMSG", error_message)
    
        df_data = pd.DataFrame(tbl_info)  # keep the error info as a DataFrame
    else:
        # ------------------------------------------------------------------
        # Case 2: `tbl_info` is a DataFrame → combine it with the ID fields
        # ------------------------------------------------------------------
        # Create a DataFrame that contains the two ID columns and then
        # attaches all columns from `tbl_info`.
        df_data = pd.concat(
            [
                pd.Series([tbl_id], name="tbl_id"),
                pd.Series([org_id], name="org_id"),
                tbl_info.reset_index(drop=True)
            ],
            axis=1
        )
    
        # If the resulting table has exactly three columns, add an empty
        # `TBL_NM_ENG` column (mirrors the R `NA` assignment).
        if df_data.shape[1] == 3:
            df_data["TBL_NM_ENG"] = ' '
    
        # Keep only the required columns, preserving order.
        columns_to_keep = ["tbl_id", "org_id", "TBL_NM", "TBL_NM_ENG"]
        df_data = df_data.loc[:, columns_to_keep]

    # ------------------------------------------------------------------
    # Gather connection / user information
    # ------------------------------------------------------------------
    uid = get_env("USERNAME")
    # Decode the base‑64 encoded DB information string
    encoded_info = get_env(f"{schema.upper()}_INFO")
    dbinfo = decode_base64(encoded_info)
    dbid = dbinfo.split(":")[0]

    table_id = "mt_kosis_tbl"
    table_nm = "KOSIS 데이터 명칭 정보"

    # ------------------------------------------------------------------
    # No data case – just log the attempt
    # ------------------------------------------------------------------
    if df_data.empty:
        if verbose:
            logging.info(
                f"No data retrieved for table ID: {table_id}. Import operation aborted."
            )
        end_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "0"
        rcnt = ccnt = 0
        emsg = get_env("EMSG")
        schema_nm = f"ecodi_{schema}"
        insert_sql = (
            f"INSERT INTO ecodi_meta.mt_log_dataimp "
            f"(user_id, db_id, schema_nm, start_dt, end_dt, data_id, "
            f"table_id, table_nm, api_params, record_cnt, column_cnt, "
            f"status, error_msg, cret_nm) VALUES ("
            f"'{uid}', '{dbid}', '{schema_nm}', '{start_dt}', '{end_dt}', "
            f"'', '{table_id.upper()}', '{table_nm}', '{tbl_id}', "
            f"{rcnt}, {ccnt}, '{status}', '{emsg}', '{uid}');"
        )
    else:
        # ------------------------------------------------------------------
        # Normal case – ensure DB connection and load data
        # ------------------------------------------------------------------
        if not is_connected(schema):
            db_connect(schema)

        # Count rows before inserting
        cnt_before_query = f"SELECT COUNT(*) FROM ecodi_meta.{table_id}"
        cnt_before = getquery(cnt_before_query, schema).iloc[0, 0]
    
        # Append the DataFrame to the target table
        is_ok = db_settable(
            name=table_id,
            value=df_data,
            append=True,
            schema=schema
        )

        # Count rows after inserting
        cnt_after_query = f"SELECT COUNT(*) FROM ecodi_meta.{table_id}"
        cnt_after = getquery(cnt_after_query, schema).iloc[0, 0]

        end_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = get_env("STATUS")
        emsg = get_env("EMSG")
        rcnt = int(cnt_after - cnt_before)
        ccnt = 0 if status == "0" else df_data.shape[1]

        schema_nm = f"ecodi_{schema}"
        insert_sql = (
            f"INSERT INTO ecodi_meta.mt_log_dataimp "
            f"(user_id, db_id, schema_nm, start_dt, end_dt, data_id, "
            f"table_id, table_nm, api_params, record_cnt, column_cnt, "
            f"status, error_msg, cret_nm) VALUES ("
            f"'{uid}', '{dbid}', '{schema_nm}', '{start_dt}', '{end_dt}', "
            f"'', '{table_id.upper()}', '{table_nm}', '{tbl_id}', "
            f"{rcnt}, {ccnt}, '{status}', '{emsg}', '{uid}');"
        )

        # Close the connection for the working schema
        db_close(schema)

    # ------------------------------------------------------------------
    # Write the log entry into mt_log_dataimp
    # ------------------------------------------------------------------
    log_schema = "meta"
    db_connect(log_schema)
    db_send_query(insert_sql, log_schema)
        
    if verbose:
        logging.info(
            f"Imported record count: {rcnt}, column count: {ccnt}, status: {status}"
        )

    # Return the success flag (True when data was appended)
    return is_ok
  


def import_kosis_prd(
    tbl_id: Optional[str] = None,
    org_id: Optional[str] = None,
    sleep_seconds: int = 0,
    verbose: bool = True,
    dbms: str = get_env("ecoDI_DBMS")
) -> bool:
    """
    Import KOSIS data prd information into the `mt_kosis_prd` table
    and log the operation in `mt_log_dataimp`.

    Parameters
    ----------
    tbl_id : str
        Identifier of the KOSIS table to import (required).
    org_id : str
        Identifier of the KOSIS organization to import (required).        
    sleep_seconds : int, default 0
        Optional pause before starting the import.
    verbose : bool, default True
        Whether to print informational messages.
    dbms : str
        Database management system; defaults to the value of the
        `ecoDI_DBMS` environment variable.
    Returns
    -------
    bool
        ``True`` if the data was successfully appended, ``False`` otherwise.
    """
    if tbl_id is None or org_id is None:
        raise ValueError("'tbl_id' and 'org_id' must be provided.")

    schema = "meta"

    # Optional sleep before starting the import
    if sleep_seconds:
        time.sleep(sleep_seconds)

    if verbose:
        logging.info(f"Importing KOSIS data prd information for table ID: {tbl_id}")

    # Initialise status tracking
    is_ok = False
    set_env("STATUS", "1")
    set_env("EMSG", "")

    start_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ------------------------------------------------------------------
    # Retrieve the item data
    # ------------------------------------------------------------------
    try:
        prd_info = desc_kosis_stats(tbl_id=tbl_id, org_id=org_id, 
                                     type_="PRD", verbose=verbose)
    except Exception as exc:
        # If the helper raises, we treat it as a failure and store the message
        set_env("STATUS", "0")
        set_env("EMSG", str(exc))
        item_info = pd.DataFrame()

    # ----------------------------------------------------------------------
    # Case 1: `prd_info` is NOT a DataFrame → treat it as an error object
    # ----------------------------------------------------------------------
    if not isinstance(prd_info, pd.DataFrame):
        # Extract the error message (default to empty string if not present)
        emsg = prd_info.get("errMsg", "Unknown error")
        # Set environment variables to indicate failure
        set_env["STATUS"] = "0"
        set_env["EMSG"] = str(emsg)
        
        # Propagate the original (non‑DataFrame) result
        df_data = prd_info
    else:
        # Build the additional columns that need to be added to the result
        extra_columns = pd.DataFrame({
            "tbl_id": [tbl_id] * len(prd_info),
            "org_id": [org_id] * len(prd_info),
            "prd_cd": [""] * len(prd_info)
        })
        
        # Concatenate the extra columns with the data returned from the function
        # `reset_index(drop=True)` ensures the row indices align correctly
        df_data = pd.concat([extra_columns, prd_info.reset_index(drop=True)], axis=1)

    # ------------------------------------------------------------------
    # Gather connection / user information
    # ------------------------------------------------------------------
    uid = get_env("USERNAME")
    # Decode the base‑64 encoded DB information string
    encoded_info = get_env(f"{schema.upper()}_INFO")
    dbinfo = decode_base64(encoded_info)
    dbid = dbinfo.split(":")[0]

    table_id = "mt_kosis_prd"
    table_nm = "KOSIS 데이터 집계 주기/기간 정보"

    # ------------------------------------------------------------------
    # No data case – just log the attempt
    # ------------------------------------------------------------------
    if df_data.empty:
        if verbose:
            logging.info(
                f"No data retrieved for table ID: {table_id}. Import operation aborted."
            )
        end_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "0"
        rcnt = ccnt = 0
        emsg = get_env("EMSG")
        schema_nm = f"ecodi_{schema}"
        insert_sql = (
            f"INSERT INTO ecodi_meta.mt_log_dataimp "
            f"(user_id, db_id, schema_nm, start_dt, end_dt, data_id, "
            f"table_id, table_nm, api_params, record_cnt, column_cnt, "
            f"status, error_msg, cret_nm) VALUES ("
            f"'{uid}', '{dbid}', '{schema_nm}', '{start_dt}', '{end_dt}', "
            f"'', '{table_id.upper()}', '{table_nm}', '{tbl_id}', "
            f"{rcnt}, {ccnt}, '{status}', '{emsg}', '{uid}');"
        )
    else:
        # ------------------------------------------------------------------
        # Normal case – ensure DB connection and load data
        # ------------------------------------------------------------------
        if not is_connected(schema):
            db_connect(schema)

        # Count rows before inserting
        cnt_before_query = f"SELECT COUNT(*) FROM ecodi_meta.{table_id}"
        cnt_before = getquery(cnt_before_query, schema).iloc[0, 0]
    
        # Append the DataFrame to the target table
        is_ok = db_settable(
            name=table_id,
            value=df_data,
            append=True,
            schema=schema
        )

        # Count rows after inserting
        cnt_after_query = f"SELECT COUNT(*) FROM ecodi_meta.{table_id}"
        cnt_after = getquery(cnt_after_query, schema).iloc[0, 0]

        end_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = get_env("STATUS")
        emsg = get_env("EMSG")
        rcnt = int(cnt_after - cnt_before)
        ccnt = 0 if status == "0" else df_data.shape[1]

        schema_nm = f"ecodi_{schema}"
        insert_sql = (
            f"INSERT INTO ecodi_meta.mt_log_dataimp "
            f"(user_id, db_id, schema_nm, start_dt, end_dt, data_id, "
            f"table_id, table_nm, api_params, record_cnt, column_cnt, "
            f"status, error_msg, cret_nm) VALUES ("
            f"'{uid}', '{dbid}', '{schema_nm}', '{start_dt}', '{end_dt}', "
            f"'', '{table_id.upper()}', '{table_nm}', '{tbl_id}', "
            f"{rcnt}, {ccnt}, '{status}', '{emsg}', '{uid}');"
        )

        # Close the connection for the working schema
        db_close(schema)

    # ------------------------------------------------------------------
    # Write the log entry into mt_log_dataimp
    # ------------------------------------------------------------------
    log_schema = "meta"
    db_connect(log_schema)
    db_send_query(insert_sql, log_schema)
        
    if verbose:
        logging.info(
            f"Imported record count: {rcnt}, column count: {ccnt}, status: {status}"
        )

    # Return the success flag (True when data was appended)
    return is_ok
  

def import_kosis_src(
    tbl_id: Optional[str] = None,
    org_id: Optional[str] = None,
    sleep_seconds: int = 0,
    verbose: bool = True,
    dbms: str = get_env("ecoDI_DBMS")
) -> bool:
    """
    Import KOSIS data prd information into the `mt_kosis_src` table
    and log the operation in `mt_log_dataimp`.

    Parameters
    ----------
    tbl_id : str
        Identifier of the KOSIS scouce to import (required).
    org_id : str
        Identifier of the KOSIS scouce to import (required).        
    sleep_seconds : int, default 0
        Optional pause before starting the import.
    verbose : bool, default True
        Whether to print informational messages.
    dbms : str
        Database management system; defaults to the value of the
        `ecoDI_DBMS` environment variable.
    Returns
    -------
    bool
        ``True`` if the data was successfully appended, ``False`` otherwise.
    """
    if tbl_id is None or org_id is None:
        raise ValueError("'tbl_id' and 'org_id' must be provided.")

    schema = "meta"

    # Optional sleep before starting the import
    if sleep_seconds:
        time.sleep(sleep_seconds)

    if verbose:
        logging.info(f"Importing KOSIS data scorce information for table ID: {tbl_id}")

    # Initialise status tracking
    is_ok = False
    set_env("STATUS", "1")
    set_env("EMSG", "")

    start_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ------------------------------------------------------------------
    # Retrieve the item data
    # ------------------------------------------------------------------
    try:
        src_info = desc_kosis_stats(tbl_id=tbl_id, org_id=org_id, 
                                     type_="SOURCE", verbose=verbose)
    except Exception as exc:
        # If the helper raises, we treat it as a failure and store the message
        set_env("STATUS", "0")
        set_env("EMSG", str(exc))
        item_info = pd.DataFrame()

    # ----------------------------------------------------------------------
    # Case 1: `src_info` is NOT a DataFrame → treat it as an error object
    # ----------------------------------------------------------------------
    if not isinstance(src_info, pd.DataFrame):
        # Extract the error message (default to empty string if not present)
        emsg = src_info.get("errMsg", "Unknown error")
        # Set environment variables to indicate failure
        set_env["STATUS"] = "0"
        set_env["EMSG"] = str(emsg)
        
        # Propagate the original (non‑DataFrame) result
        df_data = src_info
    else:
        # Build the additional columns that need to be added to the result
        extra_columns = pd.DataFrame({
            "tbl_id": [tbl_id] * len(src_info),
            "org_id": [org_id] * len(src_info)
        })
        
        # Concatenate the extra columns with the data returned from the function
        # `reset_index(drop=True)` ensures the row indices align correctly
        df_data = pd.concat([extra_columns, src_info.reset_index(drop=True)], axis=1)

    # ------------------------------------------------------------------
    # Gather connection / user information
    # ------------------------------------------------------------------
    uid = get_env("USERNAME")
    # Decode the base‑64 encoded DB information string
    encoded_info = get_env(f"{schema.upper()}_INFO")
    dbinfo = decode_base64(encoded_info)
    dbid = dbinfo.split(":")[0]

    table_id = "mt_kosis_src"
    table_nm = "KOSIS 데이터 출처 정보"

    # ------------------------------------------------------------------
    # No data case – just log the attempt
    # ------------------------------------------------------------------
    if df_data.empty:
        if verbose:
            logging.info(
                f"No data retrieved for table ID: {table_id}. Import operation aborted."
            )
        end_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "0"
        rcnt = ccnt = 0
        emsg = get_env("EMSG")
        schema_nm = f"ecodi_{schema}"
        insert_sql = (
            f"INSERT INTO ecodi_meta.mt_log_dataimp "
            f"(user_id, db_id, schema_nm, start_dt, end_dt, data_id, "
            f"table_id, table_nm, api_params, record_cnt, column_cnt, "
            f"status, error_msg, cret_nm) VALUES ("
            f"'{uid}', '{dbid}', '{schema_nm}', '{start_dt}', '{end_dt}', "
            f"'', '{table_id.upper()}', '{table_nm}', '{tbl_id}', "
            f"{rcnt}, {ccnt}, '{status}', '{emsg}', '{uid}');"
        )
    else:
        # ------------------------------------------------------------------
        # Normal case – ensure DB connection and load data
        # ------------------------------------------------------------------
        if not is_connected(schema):
            db_connect(schema)

        # Count rows before inserting
        cnt_before_query = f"SELECT COUNT(*) FROM ecodi_meta.{table_id}"
        cnt_before = getquery(cnt_before_query, schema).iloc[0, 0]
    
        # Append the DataFrame to the target table
        is_ok = db_settable(
            name=table_id,
            value=df_data,
            append=True,
            schema=schema
        )

        # Count rows after inserting
        cnt_after_query = f"SELECT COUNT(*) FROM ecodi_meta.{table_id}"
        cnt_after = getquery(cnt_after_query, schema).iloc[0, 0]

        end_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = get_env("STATUS")
        emsg = get_env("EMSG")
        rcnt = int(cnt_after - cnt_before)
        ccnt = 0 if status == "0" else df_data.shape[1]

        schema_nm = f"ecodi_{schema}"
        insert_sql = (
            f"INSERT INTO ecodi_meta.mt_log_dataimp "
            f"(user_id, db_id, schema_nm, start_dt, end_dt, data_id, "
            f"table_id, table_nm, api_params, record_cnt, column_cnt, "
            f"status, error_msg, cret_nm) VALUES ("
            f"'{uid}', '{dbid}', '{schema_nm}', '{start_dt}', '{end_dt}', "
            f"'', '{table_id.upper()}', '{table_nm}', '{tbl_id}', "
            f"{rcnt}, {ccnt}, '{status}', '{emsg}', '{uid}');"
        )

        # Close the connection for the working schema
        db_close(schema)

    # ------------------------------------------------------------------
    # Write the log entry into mt_log_dataimp
    # ------------------------------------------------------------------
    log_schema = "meta"
    db_connect(log_schema)
    db_send_query(insert_sql, log_schema)
        
    if verbose:
        logging.info(
            f"Imported record count: {rcnt}, column count: {ccnt}, status: {status}"
        )

    # Return the success flag (True when data was appended)
    return is_ok
    
    
# Assume get_kosis_info is defined elsewhere and returns a dict with
# keys: info_itm (DataFrame), info_tbl, info_prd, info_src, info_cmt, info_ncd
# The structure of those sub‑objects mirrors the R version.

def tab_kosis_desc(tbl_id: str | None = None, org_id: str | None = None) -> pd.DataFrame:
    """
    Replicates the behaviour of the R function `tab_kosis_desc`.
    Returns a transposed DataFrame (each field as a row) containing
    dataset description information.
    """
    # ------------------------------------------------------------
    # 1. Retrieve meta‑information
    # ------------------------------------------------------------
    info = get_kosis_info(tbl_id=tbl_id, org_id=org_id)

    itm = info["info_itm"]                     # pandas DataFrame

    # ------------------------------------------------------------
    # 2. Attribute (non‑ITEM) processing
    # ------------------------------------------------------------
    # values for the attribute column
    attr_var = itm.loc[itm["OBJ_ID"] != "ITEM", "ITM_NM"].tolist()

    # attribute name – take the first distinct OBJ_NM value
    attr_nm_series = itm.loc[itm["OBJ_ID"] != "ITEM", "OBJ_NM"].drop_duplicates()
    attr_nm = attr_nm_series.iloc[0] if not attr_nm_series.empty else ""

    # Build the HTML snippet (item1) according to the length of attr_var
    if len(attr_var) > 10:
        part1 = ", ".join(attr_var[:5])
        part2 = ", ".join(attr_var[5:10])
        item1 = f"<b>{attr_nm} ({len(attr_var)}개)</b><br>{part1}<br>{part2}, ..."
    elif len(attr_var) <= 5:
        part = ", ".join(attr_var[:5])
        item1 = f"<b>{attr_nm} ({len(attr_var)}개)</b><br>{part}"
        item1 = item1.replace(", NA", "")
    else:  # 6‑10 items
        part1 = ", ".join(attr_var[:5])
        part2 = ", ".join(attr_var[5:10])
        item1 = f"<b>{attr_nm} ({len(attr_var)}개)</b><br>{part1}<br>{part2}"
        item1 = item1.replace(", NA", "")

    # ------------------------------------------------------------
    # 3. ITEM metrics processing
    # ------------------------------------------------------------
    metric = (
        itm.loc[itm["OBJ_ID"] == "ITEM", "ITM_NM"]
        .str.replace("＜br＞", " ", regex=False)
        .tolist()
    )
    item2 = f"<b>항목 ({len(metric)}개)</b><br>{'<br>'.join(metric)}"

    # ------------------------------------------------------------
    # 4. Assemble final description DataFrame
    # ------------------------------------------------------------
    description = pd.DataFrame({
        "데이터명":      [info["info_tbl"]["TBL_NM"].iloc[0]],
        "수록기간":      [f"{info['info_prd']['PRD_SE'].iloc[0]} "
                         f"{info['info_prd']['STRT_PRD_DE'].iloc[0]}~{info['info_prd']['END_PRD_DE'].iloc[0]}"],
        "출처":        [f"{info['info_src']['JOSA_NM'].iloc[0]} {info['info_src']['DEPT_PHONE'].iloc[0]}"],
        "분류및항목":    [f"{item1}<br>{item2}"],
        "제공처":      [info["info_src"]["DEPT_NM"].iloc[0]],
        "주석":        ["<br>".join(info["info_cmt"]["CMMT_DC"])],
        "갱신일자":    [info["info_ncd"]["SEND_DE"].max()]   # assumes a pandas Series
    })

    # Transpose so that each field becomes a row (as in the R version)
    return description.T
  
  
def mk_kosis_ddl_info(obj: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Generate a DataFrame containing KOSIS DDL information (id, name, type)
    and keep only the rows whose ``id`` matches a column name of ``obj``.

    Parameters
    ----------
    obj : pd.DataFrame, optional
        Source DataFrame whose column names determine which rows are kept.
        If ``None`` an empty DataFrame with the appropriate columns is returned.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns ``id``, ``nm`` and ``type``.
    """
    # Return an empty result when no source DataFrame is supplied
    if obj is None:
        return pd.DataFrame(columns=["id", "nm", "type"])

    # ------------------------------------------------------------------
    # 1) Build the list of IDs
    # ------------------------------------------------------------------
    id_fields = ["ORG_ID", "TBL_ID", "TBL_NM"]
    for i in range(1, 9):          # 1 through 8 inclusive
        id_fields.extend([
            f"C{i}",
            f"C{i}_OBJ_NM",
            f"C{i}_OBJ_NM_ENG",
            f"C{i}_NM",
            f"C{i}_NM_ENG"
        ])
    id_fields.extend([
        "ITM_ID", "ITM_NM", "ITM_NM_ENG",
        "UNIT_ID", "UNIT_NM", "UNIT_NM_ENG",
        "PRD_SE", "PRD_DE", "DT", "LST_CHN_DE"
    ])

    # ------------------------------------------------------------------
    # 2) Build the list of Korean names (nm)
    # ------------------------------------------------------------------
    nm_fields = ["기관코드", "통계표ID", "통계표명"]
    for i in range(1, 9):
        nm_fields.extend([
            f"분류값 ID{i}",
            f"분류명{i}",
            f"분류 영문명{i}",
            f"분류값 명{i}",
            f"분류값 영문명{i}"
        ])
    nm_fields.extend([
        "항목 ID", "항목명", "항목영문명",
        "단위ID", "단위명", "단위영문명",
        "수록주기", "수록시점", "수치값", "최종수정일"
    ])

    # ------------------------------------------------------------------
    # 3) Build the list of SQL types
    # ------------------------------------------------------------------
    type_fields = ["VARCHAR(40)", "VARCHAR(40)", "VARCHAR(300)"]
    for _ in range(1, 9):
        type_fields.extend([
            "VARCHAR(40)",
            "VARCHAR(300)",
            "VARCHAR(300)",
            "VARCHAR(300)",
            "VARCHAR(300)"
        ])
    type_fields.extend([
        "VARCHAR(40)", "VARCHAR(300)", "VARCHAR(300)",
        "VARCHAR(40)", "VARCHAR(100)", "VARCHAR(100)",
        "VARCHAR(20)", "VARCHAR(10)", "NUMERIC", "DATE"
    ])

    # ------------------------------------------------------------------
    # 4) Assemble the DataFrame
    # ------------------------------------------------------------------
    kosis_ddl_info = pd.DataFrame({
        "id":   id_fields,
        "nm":   nm_fields,
        "type": type_fields
    })

    # Keep only rows whose ``id`` exists among the column names of ``obj``
    column_names = list(obj.columns)
    kosis_ddl_info = kosis_ddl_info[kosis_ddl_info["id"].isin(column_names)].copy()

    # Convert ``id`` to lower‑case to mimic the R ``mutate(id = tolower(id))``
    kosis_ddl_info["id"] = kosis_ddl_info["id"].str.lower()

    # Reset index for a tidy result
    kosis_ddl_info.reset_index(drop=True, inplace=True)

    return kosis_ddl_info
  

def mk_kosis_ddl(
    obj: pd.DataFrame,
    schema: str = "ods",
    dbms: str = None
) -> str:
    """
    Generate a CREATE TABLE DDL statement for KOSIS tables in either MySQL or PostgreSQL.

    Parameters
    ----------
    obj : pd.DataFrame
        Input metadata table containing at least the columns `TBL_ID`, `TBL_NM`,
        and the column definitions used by ``mk_kosis_ddl_info``.
    schema : str, optional
        Target schema name. Must be one of ``"ods"``, ``"meta"``, ``"data"``.
    dbms : str, optional
        Target DBMS. Must be one of ``"mysql"``, ``"postgresql"``.
        The default is read from the ``ecoDI_DBMS`` environment variable.

    Returns
    -------
    str
        The complete DDL script.
    """
    # ----------------------------------------------------------------------
    # Argument validation (similar to R's match.arg)
    # ----------------------------------------------------------------------
    valid_schemas = {"ods", "meta", "data"}
    if schema not in valid_schemas:
        raise ValueError(f"`schema` must be one of {valid_schemas}, got '{schema}'.")

    dbms = get_env("ecoDI_DBMS")
    valid_dbms = {"mysql", "postgresql"}
    if dbms not in valid_dbms:
        raise ValueError(f"`dbms` must be one of {valid_dbms}, got '{dbms}'.")

    # ----------------------------------------------------------------------
    # Basic information extraction
    # ----------------------------------------------------------------------
    tbl_id = obj.iloc[0]["TBL_ID"]
    tbl_nm = obj.iloc[0]["TBL_NM"]
    tab_names = list(obj.columns)

    # ``mk_kosis_ddl_info`` is assumed to exist elsewhere and to return a
    # pandas DataFrame with columns: ``id``, ``type``, ``nm``.
    kosis_ddl_info: pd.DataFrame = mk_kosis_ddl_info(obj=obj)

    # ----------------------------------------------------------------------
    # Helper to decide which rows receive a NOT NULL constraint
    # (first 3 rows and the last 4 rows, mimicking the R logic)
    # ----------------------------------------------------------------------
    n_rows = len(kosis_ddl_info)
    not_null_indices = {0, 1, 2, n_rows - 1, n_rows - 2, n_rows - 3, n_rows - 4}

    # ----------------------------------------------------------------------
    # Primary‑key column list (lower‑cased and filtered by presence in obj)
    # ----------------------------------------------------------------------
    pk_candidates = [
        "ORG_ID",
        "TBL_ID",
        "C1",
        "C2",
        "C3",
        "C4",
        "C5",
        "C6",
        "C7",
        "C8",
        "ITM_ID",
        "PRD_DE",
    ]
    pk_columns = [col.lower() for col in pk_candidates if col in tab_names]
    pk_clause = ", ".join(pk_columns)

    # ----------------------------------------------------------------------
    # DDL construction
    # ----------------------------------------------------------------------
    if dbms == "mysql":
        ddl = f"CREATE TABLE IF NOT EXISTS ecodi_{schema}.{tbl_id} (\n"

        for i, row in kosis_ddl_info.iterrows():
            column_def = (
                f"    {row['id']} {row['type']}"
                + (" NOT NULL" if i in not_null_indices else "")
                + f" COMMENT '{row['nm']}',"
            )
            ddl += column_def + "\n"

        # Additional audit columns
        ddl += "    cret_dt DATETIME NOT NULL COMMENT '생성일시',\n"
        ddl += "    cret_nm VARCHAR(10) NOT NULL COMMENT '생성자',\n"
        ddl += "    mdfy_dt DATETIME COMMENT '수정일시',\n"
        ddl += "    mdfy_nm VARCHAR(10) COMMENT '수정자',\n"

        # Primary‑key constraint
        ddl += f"    CONSTRAINT {tbl_id}_pkey PRIMARY KEY({pk_clause})\n"
        ddl += ");\n\n"

        # Table comment
        ddl += f"ALTER TABLE ecodi_{schema}.{tbl_id} COMMENT = '{tbl_nm}';"

    else:  # postgresql
        ddl = f"CREATE TABLE IF NOT EXISTS ecodi_{schema}.{tbl_id} (\n"

        for i, row in kosis_ddl_info.iterrows():
            column_def = (
                f"    {row['id']} {row['type']}"
                + (" NOT NULL" if i in not_null_indices else "")
                + ","
            )
            ddl += column_def + "\n"

        # Additional audit columns
        ddl += "    cret_dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,\n"
        ddl += "    cret_nm VARCHAR(20) NOT NULL,\n"
        ddl += "    mdfy_dt TIMESTAMP,\n"
        ddl += "    mdfy_nm VARCHAR(20),\n"

        # Primary‑key constraint
        ddl += f"    CONSTRAINT {tbl_id}_pkey PRIMARY KEY({pk_clause})\n"
        ddl += ");\n\n"

        # Table comment
        ddl += f"COMMENT ON TABLE ecodi_{schema}.{tbl_id} IS '{tbl_nm}';\n"

        # Column comments for each KOSIS field
        for _, row in kosis_ddl_info.iterrows():
            ddl += (
                f"COMMENT ON COLUMN ecodi_{schema}.{tbl_id}.{row['id']} "
                f"IS '{row['nm']}';\n"
            )

        # Audit column comments
        ddl += f"COMMENT ON COLUMN ecodi_{schema}.{tbl_id}.cret_dt IS '생성일시';\n"
        ddl += f"COMMENT ON COLUMN ecodi_{schema}.{tbl_id}.cret_nm IS '생성자';\n"
        ddl += f"COMMENT ON COLUMN ecodi_{schema}.{tbl_id}.mdfy_dt IS '수정일시';\n"
        ddl += f"COMMENT ON COLUMN ecodi_{schema}.{tbl_id}.mdfy_nm IS '수정자';\n"

    return ddl
  

def insert_kosis_list(
    org_id: str = None,
    tbl_id: str = None,
    tbl_nm: str = None,
    is_region_mega: str = "N",
    is_region_cty: str = "N",
    is_region_admi: str = "N",
    is_age_lc: str = "N",
    is_age_10: str = "N",
    is_age_5: str = "N",
    period_se: str = "D"
):
    """
    Register a KOSIS table in the external data list.
    Mirrors the behavior of the original R function `insert_kosis_list`.
    """
    # ------------------------------------------------------------------
    # Argument validation
    # ------------------------------------------------------------------
    if org_id is None or tbl_id is None:
        raise ValueError("'org_id' and 'tbl_id' must be provided.")

    # ------------------------------------------------------------------
    # Period code translation (matches R's named vector + match.arg)
    # ------------------------------------------------------------------
    period_map = {
        "일": "D", "월": "M", "분기": "Q", "반기": "H", "년": "Y",
        "2년": "F", "3년": "F", "4년": "F", "5년": "F",
        "10년": "F", "부정기": "IR"
    }

    # If the user supplied a Korean key, translate; otherwise assume they gave the code already.
    period_se = period_map.get(period_se, period_se).upper()
    if period_se not in {"D", "M", "Q", "H", "Y", "F", "IR"}:
        raise ValueError(f"Invalid period_se value: {period_se}")

    schema = "meta"

    # ------------------------------------------------------------------
    # Check whether the same raw_table_id already exists
    # ------------------------------------------------------------------
    sql = f"""
        SELECT data_id
          FROM ecodi_meta.mt_data_list
         WHERE raw_table_id = '{tbl_id}';
    """
    existing_data_id = getquery(sql)

    if not existing_data_id.empty:
        err = "99"
        err_msg = "동일 데이터로 이미 수집된 테이블이 있습니다."
        return {"err": err, "errMsg": err_msg}

    # ------------------------------------------------------------------
    # Generate a new data_id
    # ------------------------------------------------------------------
    sql = """
        SELECT MAX(data_id) AS data_id
          FROM ecodi_meta.mt_data_list
    """
    latest_id_df = getquery(sql)
    latest_id = latest_id_df["data_id"].iloc[0] if not latest_id_df.empty else None

    # Extract numeric part, increment, and pad to 4 digits
    if latest_id is not None and isinstance(latest_id, str):
        numeric_part = int(latest_id[2:6]) + 1   # characters 3‑6 (0‑based index)
    else:
        numeric_part = 1

    data_id_new = f"DA{str(numeric_part).zfill(4)}"

    # ------------------------------------------------------------------
    # Retrieve provider (organization) info
    # ------------------------------------------------------------------
    sql = f"""
        SELECT org_nm, org_nm_eng
          FROM ecodi_meta.mt_kosis_org
         WHERE org_id = '{org_id}'
    """
    result_org = getquery(sql)

    # ------------------------------------------------------------------
    # Retrieve source (department) info
    # ------------------------------------------------------------------
    sql = f"""
        SELECT dept_nm, dept_phone
          FROM ecodi_meta.mt_kosis_src
         WHERE tbl_id = '{tbl_id}'
           AND org_id = '{org_id}'
    """
    result_src = getquery(sql)

    # ------------------------------------------------------------------
    # Retrieve period (start / end) info
    # ------------------------------------------------------------------
    sql = f"""
        SELECT strt_prd_de, end_prd_de
          FROM ecodi_meta.mt_kosis_prd
         WHERE tbl_id = '{tbl_id}'
           AND org_id = '{org_id}'
    """
    result_prd = getquery(sql)

    # ------------------------------------------------------------------
    # Metadata for the insert statement
    # ------------------------------------------------------------------
    uid = get_env("USERNAME")
    sdt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Safeguard: pick first row if multiples are returned
    org_nm = result_org["org_nm"].iloc[0] if not result_org.empty else ""
    org_nm_eng = result_org["org_nm_eng"].iloc[0] if not result_org.empty else ""
    dept_nm = result_src["dept_nm"].iloc[0] if not result_src.empty else ""
    dept_phone = result_src["dept_phone"].iloc[0] if not result_src.empty else ""
    end_prd_de = result_prd["end_prd_de"].iloc[0] if not result_prd.empty else ""
    strt_prd_de = result_prd["strt_prd_de"].iloc[0] if not result_prd.empty else ""

    # ------------------------------------------------------------------
    # Build and execute the INSERT statement
    # ------------------------------------------------------------------
    insert_sql = f"""
        INSERT INTO ecodi_meta.mt_data_list
          (data_id, raw_site_id, api_url_id, data_nm, raw_table_id, raw_table_nm,
           raw_schema_nm, site_page_url, site_page_nm, prvdr_nm, prvdr_nm_eng,
           prvdr_dept_nm, prvdr_phone, prvdr_cycle, data_end_pov, data_start_pov,
           pov_region_mega, pov_region_cty, pov_region_admi,
           pov_age_lc, pov_age_10, pov_age_5,
           cret_dt, cret_nm)
        VALUES
          ('{data_id_new}', 'RS0001', 'AU0002', '{tbl_nm}', '{tbl_id}', '{tbl_nm}',
           'ecodi_ods', 'https://kosis.kr/openapi/Param/statisticsParameterData.do',
           'KOSIS 통계자료 조회 서비스',
           '{org_nm}', '{org_nm_eng}',
           '{dept_nm}', '{dept_phone}', '{period_se}',
           '{end_prd_de}', '{strt_prd_de}',
           '{is_region_mega}', '{is_region_cty}', '{is_region_admi}',
           '{is_age_lc}', '{is_age_10}', '{is_age_5}',
           '{sdt}', '{uid}');
    """

    log_schema = "meta"
    db_connect(log_schema)
    db_send_query(insert_sql, log_schema)

    # ------------------------------------------------------------------
    # Close resources (handled automatically by context managers)
    # ------------------------------------------------------------------
    db_close(schema)

    # Return a success flag (mirroring the R function which returns nothing on success)
    return {"err": "0", "errMsg": "Success", "data_id": data_id_new}
  


def insert_kosis_item(
    obj: Optional[pd.DataFrame] = None,
    dbms: str = None
) -> Optional[Dict[str, str]]:
    """
    Insert KOSIS items into the meta database.

    Parameters
    ----------
    obj : pandas.DataFrame, optional
        Input data containing at least columns 'TBL_ID', 'UNIT_NM', and the
        fields used by ``mk_kosis_ddl_info``.
    dbms : str
        Database management system ('mysql' or 'postgresql').

    Returns
    -------
    dict or None
        Returns a dictionary with ``err`` and ``errMsg`` when an early
        validation fails; otherwise returns ``None``.
    """
    if obj is None:
        raise ValueError("'obj' must be provided.")

    dbms = get_env("ecoDI_DBMS")
    valid_dbms = {"mysql", "postgresql"}
    if dbms not in valid_dbms:
        raise ValueError(f"`dbms` must be one of {valid_dbms}, got '{dbms}'.")
      
    # ------------------------------------------------------------------
    # 1. Resolve table identifier
    # ------------------------------------------------------------------
    schema = "meta"
    tbl_id = obj.iloc[0]["TBL_ID"]

    # ------------------------------------------------------------------
    # 2. Verify that the parent record exists in mt_data_list
    # ------------------------------------------------------------------
    # 테이블 이름으로 데이터 아이디 조회
    sql = f"""
        SELECT data_id 
          FROM ecodi_meta.mt_data_list
         WHERE raw_table_id = '{tbl_id}';
    """
    data_id_df = getquery(sql.strip())
    if data_id_df.empty:
        return {"err": "99",
                "errMsg": "부모 테이블인 ecodi_meta.mt_data_list에 해당 데이터가 존재하지 않습니다."}
    data_id = data_id_df["data_id"].iloc[0]

    # ------------------------------------------------------------------
    # 3. Check that the same data has not already been collected
    # ------------------------------------------------------------------
    # 기존 동일 테이블 이름으로 데이터 아이디 조회    
    sql = f"""
        SELECT item.data_id 
          FROM ecodi_meta.mt_data_list list
          RIGHT JOIN ecodi_meta.mt_data_item item
            ON list.data_id = item.data_id
         WHERE raw_table_id = '{tbl_id}';
    """
    existing_df = getquery(sql.strip())
    if not existing_df.empty:
        return {"err": "99",
                "errMsg": "동일 데이터로 이미 수집된 정보(ecodi_meta.mt_data_item)가 있습니다."}

    # ------------------------------------------------------------------
    # 4. Prepare additional metadata
    # ------------------------------------------------------------------
    unit_nm = ", ".join(obj["UNIT_NM"].dropna().unique())
    uid = get_env("USERNAME")
    sdt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ------------------------------------------------------------------
    # 5. Build the KOSIS DDL information DataFrame
    # ------------------------------------------------------------------
    kosis_ddl_info = (
        mk_kosis_ddl_info(obj=obj)
        .assign(
            data_item_unit_clss=lambda df: df["nm"].apply(
                lambda x: unit_nm if x == "수치값" else ""
            ),
            data_item_unit=lambda df: df["nm"].apply(
                lambda x: 1 if x == "수치값" else pd.NA
            ),
            pov_region="",
            pov_age="",
            data_item_desc="",
            data_id=data_id,
            cret_dt=sdt,
            cret_nm=uid,
        )
    )

    # Rename columns to match target table names
    df_data_item = (
        kosis_ddl_info.rename(
            columns={
                "id": "data_item",
                "nm": "data_item_nm",
                "type": "data_item_type",
            }
        )
        .loc[
            :,
            [
                "data_id",
                "data_item",
                "data_item_nm",
                "pov_region",
                "pov_age",
                "data_item_type",
                "data_item_unit_clss",
                "data_item_unit",
                "data_item_desc",
                "cret_dt",
                "cret_nm",
            ],
        ]
        .copy()
    )

    # ------------------------------------------------------------------
    # 6. Insert into the meta database
    # ------------------------------------------------------------------
    table_id = "mt_data_item"
    table_nm = "외부 데이터 항목 정보"

    if not is_connected(schema):
        db_connect(schema)

    # Count rows before insertion
    cnt_before_sql = f"SELECT COUNT(*) FROM ecodi_meta.{table_id}"
    cnt_before = getquery(cnt_before_sql, schema=schema).iloc[0, 0]

    # Insert the rows
    db_settable(name=table_id, value=df_data_item, append=True, schema=schema)

    # Count rows after insertion
    cnt_after = getquery(cnt_before_sql, schema=schema).iloc[0, 0]

    # ------------------------------------------------------------------
    # 7. Log the import operation
    # ------------------------------------------------------------------
    edt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = get_env("STATUS")
    emsg = get_env("EMSG")

    rcnt = cnt_after - cnt_before
    ccnt = 0 if status == "0" else df_data_item.shape[1]

    # Decode DB info to obtain dbid (mirrors R's base64decode + rawToChar)
    encoded_info = get_env(f"{schema.upper()}_INFO")
    dbinfo = decode_base64(encoded_info)
    dbid = dbinfo.split(":")[0]

    schema_nm = f"ecodi_{schema}"

    if dbms == "mysql":
        isql = f"""
        INSERT INTO ecodi_meta.mt_log_dataimp 
        SET user_id = '{uid}', db_id = '{table_id}', schema_nm = '{schema_nm}', start_dt = '{sdt}', 
            end_dt = '{edt}', data_id = '', table_id = '{table_id.upper()}',
            table_nm = '{table_nm}', api_params = 'import to data items table for {table_id}',
            record_cnt = {rcnt}, column_cnt = {ccnt}, status = '{status}', 
            error_msg = '{emsg}', cret_nm = '{uid}';
        """
    elif dbms == "postgresql":
        isql = f"""
        INSERT INTO ecodi_meta.mt_log_dataimp 
        (user_id, db_id, schema_nm, start_dt, end_dt, data_id,
         table_id, table_nm, api_params, record_cnt, column_cnt, 
         status, error_msg, cret_nm)
        VALUES ('{uid}', '{dbid}', '{schema_nm}', '{sdt}', '{edt}', 
                '', '{table_id.upper()}', '{table_nm}', 'import to data items table for {table_id}',
                {rcnt}, {ccnt}, '{status}', '{emsg}', '{uid}');
        """
    else:
        raise ValueError(f"Unsupported DBMS: {dbms}")

    # Execute the logging statement (assuming getquery can also run non‑SELECT)
    log_schema = "meta"
    db_connect(log_schema)
    db_send_query(isql, log_schema)

    # ------------------------------------------------------------------
    # 8. Clean‑up
    # ------------------------------------------------------------------
    db_close(schema)

    # Function returns None on successful completion
    return None
  
  
def insert_kosis_cmmt(tbl_id: str = None, org_id: str = None,
                      dbms: str = None) -> dict:
    """
    Insert KOSIS comment information into the `mt_data_comment` table.

    Returns a dictionary with keys `err` and `errMsg` when an error occurs,
    otherwise returns an empty dict.
    """
    # ------------------------------------------------------------------
    # 1. Validate required arguments
    # ------------------------------------------------------------------
    if tbl_id is None or org_id is None:
        raise ValueError("'tbl_id' and 'org_id' must be provided.")

    schema = "meta"
    
    dbms = get_env("ecoDI_DBMS")
    valid_dbms = {"mysql", "postgresql"}
    if dbms not in valid_dbms:
        raise ValueError(f"`dbms` must be one of {valid_dbms}, got '{dbms}'.")

    # ------------------------------------------------------------------
    # 2. Get the primary data_id from mt_data_list
    # ------------------------------------------------------------------
    sql = f"""
        SELECT data_id
          FROM ecodi_meta.mt_data_list
         WHERE raw_table_id = '{tbl_id}';
    """
    data_id_df = getquery(sql.strip(), schema=schema)

    if data_id_df.empty:
        return {"err": "99",
                "errMsg": "부모 테이블인 ecodi_meta.mt_data_list에 해당 데이터가 존재하지 않습니다."}

    data_id = data_id_df.iloc[0]["data_id"]

    # ------------------------------------------------------------------
    # 3. Ensure no comment already exists for this table
    # ------------------------------------------------------------------
    sql = f"""
        SELECT cmmt.data_id
          FROM ecodi_meta.mt_data_list list
          RIGHT JOIN ecodi_meta.mt_data_comment cmmt
                 ON list.data_id = cmmt.data_id
         WHERE raw_table_id = '{tbl_id}';
    """
    existing_df = getquery(sql.strip(), schema=schema)

    if not existing_df.empty:
        return {"err": "99",
                "errMsg": "동일 데이터로 이미 수집된 정보(ecodi_meta.mt_data_comment)가 있습니다."}

    # ------------------------------------------------------------------
    # 4. Retrieve comment data via the KOSIS API wrapper
    # ------------------------------------------------------------------
    result_cmmt = desc_kosis_stats(tbl_id=tbl_id, org_id=org_id, type_="CMMT")

    if not isinstance(result_cmmt, pd.DataFrame) or result_cmmt.empty:
        return {"err": "99",
                "errMsg": "KOSIS 데이터 주석 정보를 조회할 수 없습니다."}

    # Combine non‑empty comment strings with a <br> separator
    comment_series = result_cmmt.loc[result_cmmt["CMMT_DC"] != "", "CMMT_DC"]
    cmmt_dc = "<br>".join(comment_series.astype(str).tolist())

    # ------------------------------------------------------------------
    # 5. Build the comment record to be inserted
    # ------------------------------------------------------------------
    uid = get_env("USERNAME")
    sdt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    comment_info = pd.DataFrame({
        "data_id":      [data_id],
        "data_comment": [cmmt_dc],
        "cret_dt":      [sdt],
        "cret_nm":      [uid]
    })

    table_id = "mt_data_comment"
    table_nm = "외부데이터 주석 정보"

    # ------------------------------------------------------------------
    # 6. Ensure DB connection
    # ------------------------------------------------------------------
    if not is_connected(schema):
        db_connect(schema)

    # ------------------------------------------------------------------
    # 7. Record row count before insertion
    # ------------------------------------------------------------------
    cnt_before = getquery(
        f"SELECT COUNT(*) FROM ecodi_meta.{table_id}",
        schema=schema
    ).iloc[0, 0]

    # ------------------------------------------------------------------
    # 8. Insert the comment record (append = True)
    # ------------------------------------------------------------------
    db_settable(name=table_id, value=comment_info, append=True, schema=schema)

    # ------------------------------------------------------------------
    # 9. Record row count after insertion
    # ------------------------------------------------------------------
    cnt_after = getquery(
        f"SELECT COUNT(*) FROM ecodi_meta.{table_id}",
        schema=schema
    ).iloc[0, 0]

    # ------------------------------------------------------------------
    # 10. Build log entry
    # ------------------------------------------------------------------
    edt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = get_env("STATUS")
    emsg = get_env("EMSG")

    rcnt = cnt_after - cnt_before                     # records added
    ccnt = 0 if status == "0" else comment_info.shape[1]  # column count for log

    schema_nm = f"ecodi_{schema}"

    # Decode the INFO environment variable (base64) and extract DB id
    dbinfo_encoded = get_env(f"{schema.upper()}_INFO")
    dbinfo = decode_base64(dbinfo_encoded)
    dbid = dbinfo.split(":")[0]

    # ------------------------------------------------------------------
    # 11. Compose the appropriate INSERT statement depending on DBMS
    # ------------------------------------------------------------------
    if dbms.lower() == "mysql":
        log_sql = f"""
            INSERT INTO ecodi_meta.mt_log_dataimp
            SET user_id = '{uid}',
                db_id = '{table_id}',
                schema_nm = '{schema_nm}',
                start_dt = '{sdt}',
                end_dt = '{edt}',
                data_id = '',
                table_id = '{table_id.upper()}',
                table_nm = '{table_nm}',
                api_params = 'import to data comment table for {tbl_id}',
                record_cnt = {rcnt},
                column_cnt = {ccnt},
                status = '{status}',
                error_msg = '{emsg}',
                cret_nm = '{uid}';
        """
    elif dbms.lower() == "postgresql":
        log_sql = f"""
            INSERT INTO ecodi_meta.mt_log_dataimp
            (user_id, db_id, schema_nm, start_dt, end_dt, data_id,
             table_id, table_nm, api_params, record_cnt, column_cnt,
             status, error_msg, cret_nm)
            VALUES ('{uid}', '{dbid}', '{schema_nm}', '{sdt}', '{edt}',
                    '',
                    '{table_id.upper()}', '{table_nm}',
                    'import to data comment table for {tbl_id}',
                    {rcnt}, {ccnt},
                    '{status}', '{emsg}', '{uid}');
        """
    else:
        raise ValueError(f"Unsupported DBMS: {dbms}")

    # Execute the log insertion
    log_schema = "meta"
    db_connect(log_schema)
    db_send_query(log_sql, log_schema)

    # ------------------------------------------------------------------
    # 12. Clean up
    # ------------------------------------------------------------------
    db_close(schema)

    # Successful completion – return empty dict (mirrors R's lack of return)
    return None
  

def insert_kosis_update(tbl_id: str = None, org_id: str = None,
                       dbms: str = get_env("ecoDI_DBMS")) -> dict:
    """
    Replicates the behaviour of the original R ``insert_kosis_update`` function.
    Returns a dictionary with ``err`` and ``errMsg`` when an error occurs,
    otherwise returns an empty dict.
    """
    # ------------------------------------------------------------------
    # 0) Validate required arguments
    # ------------------------------------------------------------------
    if tbl_id is None or org_id is None:
        raise ValueError("'tbl_id' and 'org_id' must be provided.")

    schema = "meta"
    
    dbms = get_env("ecoDI_DBMS")
    valid_dbms = {"mysql", "postgresql"}
    if dbms not in valid_dbms:
        raise ValueError(f"`dbms` must be one of {valid_dbms}, got '{dbms}'.")
      
    # ------------------------------------------------------------------
    # 1) Retrieve the data_id for the requested raw table
    # ------------------------------------------------------------------
    # 테이블 이름으로 데이터 아이디 조회
    sql = f"""
        SELECT data_id
          FROM ecodi_meta.mt_data_list
         WHERE raw_table_id = '{tbl_id}';
    """
    data_id_df = getquery(sql, schema=schema)

    if data_id_df.empty:
        return {"err": "99", "errMsg": "부모 테이블인 ecodi_meta.mt_data_list에 해당 데이터가 존재하지 않습니다."}
    data_id = data_id_df.iloc[0]["data_id"]

    # ------------------------------------------------------------------
    # 2) Check whether an update entry already exists
    # ------------------------------------------------------------------
    # 기존 동일 테이블 이름으로 데이터 아이디 조회
    sql = f"""
        SELECT max(udt.data_id) AS data_id
          FROM ecodi_meta.mt_data_list list
          RIGHT JOIN ecodi_meta.mt_data_update udt
                 ON list.data_id = udt.data_id
         WHERE raw_table_id = '{tbl_id}';
    """
    existing_df = getquery(sql, schema=schema)

    if not existing_df.empty and pd.notna(existing_df.iloc[0]["data_id"]):
        return {"err": "99", "errMsg": "동일 데이터로 이미 수집된 정보(ecodi_meta.mt_data_update)가 있습니다."}

    # ------------------------------------------------------------------
    # 3) Obtain the NCD statistics
    # ------------------------------------------------------------------
    result_ncd = desc_kosis_stats(tbl_id=tbl_id, org_id=org_id, type_="NCD")

    if not isinstance(result_ncd, pd.DataFrame) or result_ncd.empty:
        return {"err": "99", "errMsg": "KOSIS 데이터 갱신 정보를 조회할 수 없습니다."}

    # ------------------------------------------------------------------
    # 4) Normalise the period column (PRD_SE)
    # ------------------------------------------------------------------
    # Mapping used in the original R `case_when`
    period_map = {
        "일": "D",
        "월": "M",
        "분기": "Q",
        "반기": "H",
        "년": "Y"
    }
    multi_year = {"2년", "3년", "4년", "5년", "10년"}

    # Drop ORG_NM if it exists
    result_ncd = result_ncd.drop(columns=["ORG_NM"], errors="ignore")

    def map_prd_se(val):
        if val in period_map:
            return period_map[val]
        if val in multi_year:
            return "F"
        return "IR"

    result_ncd["PRD_SE"] = result_ncd["PRD_SE"].apply(map_prd_se)

    # ------------------------------------------------------------------
    # 5) Build the update information DataFrame
    # ------------------------------------------------------------------
    uid = get_env("USERNAME")
    sdt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    update_info = (
        result_ncd
        .assign(data_id=data_id,
                cret_dt=sdt,
                cret_nm=uid)
        .loc[:, ["data_id", "PRD_SE", "PRD_DE", "SEND_DE", "cret_dt", "cret_nm"]]
        .rename(columns={
            "PRD_SE": "data_prvdr_cycle",
            "PRD_DE": "data_base_pov",
            "SEND_DE": "data_update_date"
        })
    )

    # ------------------------------------------------------------------
    # 6) Insert the new rows into the meta table
    # ------------------------------------------------------------------
    table_id = "mt_data_update"
    table_nm = "외부데이터 업데이트 정보"

    if not is_connected(schema):
        db_connect(schema)

    # Count rows before insertion
    cnt_before = (
        getquery(f"SELECT COUNT(*) FROM ecodi_meta.{table_id}", schema=schema)
        .iloc[0, 0]
    )

    # Append the new rows
    db_settable(name=table_id, value=update_info, append=True, schema=schema)

    # Count rows after insertion
    cnt_after = (
        getquery(f"SELECT COUNT(*) FROM ecodi_meta.{table_id}", schema=schema)
        .iloc[0, 0]
    )

    # ------------------------------------------------------------------
    # 7) Log the operation
    # ------------------------------------------------------------------
    edt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = get_env("STATUS")
    emsg = get_env("EMSG")

    rcnt = cnt_after - cnt_before
    ccnt = 0 if status == "0" else update_info.shape[1]

    schema_nm = f"ecodi_{schema}"

    # Decode DB information
    dbinfo_enc = get_env(f"{schema.upper()}_INFO")
    dbinfo = decode_base64(dbinfo_enc)
    dbid = dbinfo.split(":")[0]

    if dbms == "mysql":
        log_sql = f"""
            INSERT INTO ecodi_meta.mt_log_dataimp 
            SET user_id = '{uid}', db_id = '{table_id}', schema_nm = '{schema_nm}',
                start_dt = '{sdt}', end_dt = '{edt}', data_id = '',
                table_id = '{table_id.upper()}', table_nm = '{table_nm}',
                api_params = 'import to data update table for {tbl_id}',
                record_cnt = {rcnt}, column_cnt = {ccnt},
                status = '{status}', error_msg = '{emsg}', cret_nm = '{uid}';
        """
    elif dbms == "postgresql":
        log_sql = f"""
            INSERT INTO ecodi_meta.mt_log_dataimp
            (user_id, db_id, schema_nm, start_dt, end_dt, data_id,
             table_id, table_nm, api_params, record_cnt, column_cnt,
             status, error_msg, cret_nm)
            VALUES ('{uid}', '{dbid}', '{schema_nm}', '{sdt}', '{edt}',
                    '', '{table_id.upper()}', '{table_nm}',
                    'import to data update table for {tbl_id}',
                    {rcnt}, {ccnt}, '{status}', '{emsg}', '{uid}');
        """
    else:
        raise ValueError(f"Unsupported DBMS: {dbms}")

    # Execute the log insertion
    log_schema = "meta"
    db_connect(log_schema)
    db_send_query(log_sql, log_schema)

    # ------------------------------------------------------------------
    # 8) Clean up
    # ------------------------------------------------------------------
    db_close(schema)

    # No error – return an empty dict for consistency with the R version
    return None
  

def insert_kosis_paramset(
    tbl_id: Optional[str] = None,
    org_id: Optional[str] = None,
    api_url_id: str = "AU0002",
    objL1: str = "", objL2: str = "", objL3: str = "", objL4: str = "",
    objL5: str = "", objL6: str = "", objL7: str = "", objL8: str = "",
    all_obj: bool = True,
    start_prd: Optional[str] = None,
    end_prd: Optional[str] = None,
    all_prd: bool = False,
    period_se: Optional[List[str]] = None,
    auto_period: bool = True,
    verbose: bool = False,
    dbms: Optional[str] = None,
) -> Optional[dict]:
    """
    KOSIS API 파라미터 셋을 DB에 삽입하는 함수.
    
    Parameters
    ----------
    tbl_id      : KOSIS 테이블 ID
    org_id      : KOSIS 기관 ID
    api_url_id  : API URL ID (기본값 "AU0002")
    objL1~objL8 : 객체 레벨 파라미터
    all_obj     : 모든 객체 파라미터 자동 설정 여부
    start_prd   : 수집 시작 기간
    end_prd     : 수집 종료 기간
    all_prd     : 전체 기간 수집 여부
    period_se   : 기간 구분 코드 리스트
    auto_period : 기간 구분 자동 설정 여부
    verbose     : 상세 출력 여부
    dbms        : DBMS 종류 ("mysql" | "postgresql")
    """
    if period_se is None:
        period_se = ["M", "Y", "H", "Q", "D", "F", "IR"]

    if dbms is None:
        dbms = get_env("ecoDI_DBMS")

    # ── 입력값 검증 ────────────────────────────────────────────────
    if tbl_id is None or org_id is None:
        raise ValueError("'tbl_id' and 'org_id' must be provided.")

    schema = "meta"

    # ── 테이블 이름으로 data_id 조회 ───────────────────────────────
    sql = f"""
        SELECT data_id
          FROM ecodi_meta.mt_data_list
         WHERE raw_table_id = '{tbl_id}';
    """
    data_id_df = getquery(sql)

    if len(data_id_df) == 0:
        return {"err": "99", "errMsg": "부모 테이블인 ecodi_meta.mt_data_list에 해당 데이터가 존재하지 않습니다."}

    data_id = data_id_df["data_id"].iloc[0]

    # ── 기존 동일 테이블에 대한 파라미터셋 존재 여부 확인 ──────────
    sql = f"""
        SELECT MAX(pram.data_id) AS data_id
          FROM ecodi_meta.mt_data_list list
     RIGHT JOIN ecodi_meta.mt_api_paramset pram
            ON list.data_id = pram.data_id
         WHERE raw_table_id = '{tbl_id}';
    """
    existing_data_id_df = getquery(sql)

    if len(existing_data_id_df) > 0 and pd.notna(existing_data_id_df["data_id"].iloc[0]):
        return {"err": "99", "errMsg": "동일 데이터로 이미 수집된 정보(ecodi_meta.mt_api_paramset)가 있습니다."}

    # ── API 파라미터 항목 조회 ─────────────────────────────────────
    sql = f"""
        SELECT param_seq, param_id, param_nm,
               default_value, is_must, is_key,
               is_constant, is_list
          FROM ecodi_meta.mt_api_param
         WHERE api_url_id = '{api_url_id}';
    """
    params = getquery(sql)

    # ── ITM 메타 조회 및 itmId 생성 ───────────────────────────────
    df_itm = from_meta_kosisdesc(tbl_id=tbl_id, org_id=org_id, type_="ITM")
    itmId = "+".join(
        df_itm[df_itm["obj_id"] == "ITEM"]["itm_id"].tolist()
    )

    # ── all_obj 옵션: 각 obj_id_sn 별 itm_id 문자열 생성 후 objLn에 할당
    obj_params = {
        "objL1": objL1, "objL2": objL2, "objL3": objL3, "objL4": objL4,
        "objL5": objL5, "objL6": objL6, "objL7": objL7, "objL8": objL8,
    }

    if all_obj:
        obj_id_sns = (
            df_itm[df_itm["obj_id_sn"].notna()]["obj_id_sn"]
            .drop_duplicates()
            .tolist()
        )

        for i, sn in enumerate(obj_id_sns, start=1):
            param_str = "+".join(
                df_itm[df_itm["obj_id_sn"] == sn]["itm_id"].tolist()
            )
            if len(param_str) >= 500:
                param_str = "ALL"
            obj_params[f"objL{i}"] = param_str

    # ── 기간 정보 조회 ─────────────────────────────────────────────
    df_prd = desc_kosis_stats(tbl_id=tbl_id, org_id=org_id, type_="PRD", verbose=verbose)
    df_prd.columns = [col.lower() for col in df_prd.columns]
    df_prd = df_prd.rename(columns={df_prd.columns[0]: "prd_nm"})

    df_prd_se = getquery(
        sql="SELECT prd_se AS prd_nm, prd_cd AS prd_se FROM mt_kosis_prdse",
        schema="meta"
    )

    if auto_period:
        period_se = ["M", "Y", "H", "Q", "D", "F", "IR"]

    df_prd = (
        df_prd_se
        .merge(df_prd, on="prd_nm", how="inner")
        .loc[lambda d: d["prd_se"].isin(period_se)]
        .assign(
            strt_prd_de=lambda d: d["strt_prd_de"].str.replace(r"[^0-9]", "", regex=True),
            end_prd_de=lambda d: d["end_prd_de"].str.replace(r"[^0-9]", "", regex=True),
        )
    )

    if not auto_period and len(df_prd) == 0:
        raise ValueError("No period information found for the given 'tbl_id', 'org_id', and 'period_se'.")

    # ── 기간 범위 설정 ─────────────────────────────────────────────
    newest_prdcnt = 0
    if all_prd:
        start_prd = df_prd["strt_prd_de"].iloc[0]
        end_prd   = df_prd["end_prd_de"].iloc[0]
    else:
        if start_prd is None and end_prd is None:
            newest_prdcnt = 2
        else:
            if start_prd is None:
                start_prd = df_prd["strt_prd_de"].iloc[0]
            if end_prd is None:
                end_prd = df_prd["end_prd_de"].iloc[0]

    prd_se_val = df_prd["prd_se"].iloc[0]

    # ── params_set 데이터프레임 생성 ──────────────────────────────
    now_str = str(datetime.now())[:19]
    uid = get_env("USERNAME")

    params_set = pd.DataFrame({
        "data_id":        data_id,
        "api_url_id":     api_url_id,
        "param_seq":      params["param_seq"],
        "value_seq":      1,
        "value_set":      "",
        "value_set_desc": params["param_nm"],
        "parent_set":     "",
        "cret_dt":        now_str,
        "cret_nm":        uid,
        "param_id":       params["param_id"],
    })

    # default_value 병합 및 고정값 세팅
    default_vals = params[params["default_value"] != ""][["param_seq", "default_value"]]
    params_set = params_set.merge(default_vals, on="param_seq", how="left")

    def apply_value(row):
        val = row["value_set"]
        if pd.notna(row.get("default_value")) and row["default_value"] != "":
            val = row["default_value"]

        mapping = {
            "orgId":      org_id,
            "tblId":      tbl_id,
            "prdSe":      prd_se_val,
            "startPrdDe": start_prd,
            "endPrdDe":   end_prd,
        }
        if row["param_id"] in mapping and mapping[row["param_id"]] is not None:
            val = mapping[row["param_id"]]

        return val if pd.notna(val) else ""

    params_set["value_set"] = params_set.apply(apply_value, axis=1)
    params_set = params_set.drop(columns=["default_value"], errors="ignore")

    # ── objLn 등 로컬 변수 기반으로 value_set 덮어쓰기 ─────────────
    local_vars = {**obj_params, "itmId": itmId}

    for i, row in params_set.iterrows():
        if row["param_id"] in local_vars:
            params_set.at[i, "value_set"] = local_vars[row["param_id"]]

    params_set = params_set.drop(columns=["param_id"])

    # ── DB 연결 및 데이터 삽입 ─────────────────────────────────────
    table_id = "mt_api_paramset"
    table_nm = "API 호출 파라미터 값 목록"

    if not is_connected(schema):
        db_connect(schema)

    sdt = str(datetime.now())[:19]

    cnt_before = getquery(f"SELECT COUNT(*) FROM ecodi_meta.{table_id}", schema=schema).iloc[0, 0]

    is_ok = db_settable(name=table_id, value=params_set, append=True, schema=schema)

    cnt_after = getquery(f"SELECT COUNT(*) FROM ecodi_meta.{table_id}", schema=schema).iloc[0, 0]

    edt = str(datetime.now())[:19]

    # ── 로그 기록 ──────────────────────────────────────────────────
    status = get_env("STATUS")
    emsg   = str(get_env("EMSG")).replace("'", "\\'")

    rcnt  = cnt_after - cnt_before
    ccnt  = 0 if status == "0" else len(params_set.columns)
    schema_nm = f"ecodi_{schema}"

    dbinfo = decode_base64(get_env(f"{schema.upper()}_INFO"))
    dbid   = dbinfo.split(":")[0]

    if dbms == "mysql":
        isql = f"""
            INSERT INTO ecodi_meta.mt_log_dataimp
            SET user_id = '{uid}', db_id = '{table_id}', schema_nm = '{schema_nm}',
                start_dt = '{sdt}', end_dt = '{edt}', data_id = '',
                table_id = '{table_id.upper()}', table_nm = '{table_nm}',
                api_params = 'import to api paramset table for {tbl_id}',
                record_cnt = {rcnt}, column_cnt = {ccnt},
                status = '{status}', error_msg = '{emsg}', cret_nm = '{uid}';
        """
    elif dbms == "postgresql":
        isql = f"""
            INSERT INTO ecodi_meta.mt_log_dataimp
            (user_id, db_id, schema_nm, start_dt, end_dt, data_id,
             table_id, table_nm, api_params, record_cnt, column_cnt,
             status, error_msg, cret_nm)
            VALUES ('{uid}', '{dbid}', '{schema_nm}', '{sdt}', '{edt}',
                    '', '{table_id.upper()}', '{table_nm}',
                    'import to api paramset table for {tbl_id}',
                    {rcnt}, {ccnt}, '{status}', '{emsg}', '{uid}');
        """

    # Execute the log insertion
    log_schema = "meta"
    db_connect(log_schema)
    db_send_query(isql, log_schema)
    
    db_close(schema)
    


def reorg_kosis_data(
    data_set: Optional[pd.DataFrame] = None,
    region_item: Optional[str] = None,
    age_item: bool = False,
    pivot_items: Optional[List[str]] = None,
    region_level: int = 3,
    age_level: int = 1,
    atomic: bool = False,
    tbl_id: Optional[str] = None,
    org_id: Optional[str] = None,
) -> pd.DataFrame:
    # 입력값 검증
    if data_set is None or len(data_set) == 0:
        raise ValueError("'data_set' must be provided and cannot be empty.")

    if region_item is not None and (region_level < 0 or region_level > 3):
        raise ValueError("'region_item' must be in 0, 1, 2, 3.")

    # 기본 컬럼명 설정
    base_names = ["PRD_SE", "PRD_DE", "ITM_ID", "DT"]

    # C1~C10, C1_NM~C10_NM 컬럼명 생성
    items = []
    for x in range(1, 11):
        items.extend([f"C{x}", f"C{x}_NM"])

    items = base_names + items

    # 실제 데이터셋에 존재하는 컬럼만 필터링
    items = [col for col in items if col in data_set.columns]

    tbl_id = data_set["TBL_ID"].iloc[0]   # First value of the TBL_ID column
    org_id = data_set["ORG_ID"].iloc[0]   # First value of the ORG_ID column

    # pivot_items가 없을 경우 desc_kosis_stats 함수로 조회 (별도 구현 필요)
    if pivot_items is None:
        stats = desc_kosis_stats(tbl_id=tbl_id, org_id=org_id, type_="ITM")
        pivot_items = (
            stats[stats["OBJ_ID"] == "ITEM"]["ITM_ID"]
            .drop_duplicates()
            .tolist()
        )

    # 데이터 재구성
    df_reorg = (
        data_set[items]
        .loc[data_set["ITM_ID"].isin(pivot_items)]
        .pivot_table(index=[c for c in items if c not in ["ITM_ID", "DT"]],
                     columns="ITM_ID",
                     values="DT",
                     aggfunc="first")
        .reset_index()
    )
    df_reorg.columns.name = None
    df_reorg = df_reorg.rename(columns={"PRD_SE": "BASE_DT_CD", "PRD_DE": "BASE_DT"})

    # region_item 기반 필터링
    if region_item is not None:
        if region_level == 0:
            df_reorg = df_reorg[df_reorg[region_item] == "00"]
        else:
            region_length_map = {1: 2, 2: 5, 3: 8}
            target_len = region_length_map.get(region_level, 8)

            df_reorg = df_reorg[
                (df_reorg[region_item].str.len() == target_len) &
                (df_reorg[region_item] != "00")
            ]

    # atomic 필터링: 전체 합계(000...0) 행 제거
    if atomic:
        zero_patterns = {"0", "00", "000", "0000", "00000", "000000", "0000000", "00000000"}
        attr_cols = [col for col in df_reorg.columns if col in [f"C{i}" for i in range(1, 11)]]

        for col in attr_cols:
            df_reorg = df_reorg[~df_reorg[col].isin(zero_patterns)]

    return df_reorg
  
  
# Exported symbols (similar to R's @export)
__all__ = [
    "desc_kosis_stats",
    "get_kosis_stats",
    "from_meta_kosisdesc",
    "get_kosis_indexpl",
    "get_kosis_info",
    "get_kosis_explanation",
    "kosis_stats_list",
    "kosis_list_level1",
    "kosis_list_parent",
    "kosis_list_stats",
    "kosis_org_list",
    "import_kosis_indexpl",
    "import_kosis_statexpl",
    "import_kosis_item",
    "import_kosis_tbl",
    "import_kosis_prd",
    "import_kosis_src",
    "tab_kosis_desc",
    "mk_kosis_ddl_info",
    "mk_kosis_ddl",
    "insert_kosis_list",
    "insert_kosis_item",
    "insert_kosis_cmmt",
    "insert_kosis_update",
    "insert_kosis_paramset",
    "reorg_kosis_data",
]
