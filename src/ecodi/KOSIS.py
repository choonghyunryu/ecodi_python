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
  

import os
import re
import itertools
from typing import Any, List, Optional, Dict

import pandas as pd
import requests



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


import os
import logging
import requests
import pandas as pd


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
  

def db_settable(name: str, value: pd.DataFrame, append: bool, schema: str) -> bool:
    """Insert a DataFrame into a DB table. Returns True on success."""
    raise NotImplementedError("`db_settable` must be implemented.")

def db_send_query(sql: str, schema: str) -> None:
    """Execute a non‑SELECT statement (e.g., INSERT)."""
    raise NotImplementedError("`db_send_query` must be implemented.")

def db_commit(schema: str) -> None:
    """Commit the current transaction for the given schema."""
    raise NotImplementedError("`db_commit` must be implemented.")
# ----------------------------------------------------------------------


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
    dbinfo = base64.b64decode(encoded_info).decode()
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

    if dbms.lower() == "mysql":
        db_commit(log_schema)

    if verbose:
        logging.info(
            f"Imported record count: {rcnt}, column count: {ccnt}, status: {status}"
        )

    # Return the success flag (True when data was appended)
    return is_ok
  
  
# Exported symbols (similar to R's @export)
__all__ = [
    "desc_kosis_stats",
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
]
