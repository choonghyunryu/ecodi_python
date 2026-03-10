import os
import re
import pandas as pd
import importlib.resources
from typing import Any, List, Optional, Dict
import sqlalchemy
from sqlalchemy import create_engine, text, inspect, insert
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.exc import SQLAlchemyError

from ecodi.env import (
    get_env
)

from ecodi.dbms import (
    meta_connect,
    ods_connect,
    data_connect,
    db_connect,
    get_connection,
    ddl_from_text,
    db_settable,
    getquery
)


def mapp_name2mega(mega_cd=None, mega_nm=None):
    """
    Replicates the behavior of the R function `mapp_name2mega`.

    Parameters
    ----------
    mega_cd : scalar or list‑like
        Mega code(s). Must be provided.
    mega_nm : scalar or list‑like
        Mega name(s). Must be provided.

    Returns
    -------
    pandas.DataFrame
        The left‑joined table of the provided mega information with the base
        information extracted from `bit_spatial.mega`.
    """
    # Validate inputs
    if mega_cd is None or mega_nm is None:
        raise ValueError("Both 'mega_cd' and 'mega_nm' must be provided.")

    # Build the input data frame
    mega_info = pd.DataFrame({
        "mega_cd": pd.Series(mega_cd),
        "mega_nm": pd.Series(mega_nm)
    })

    sql = "select mega_cd as base_cd, mega_nm as base_nm from ecodi_meta.mt_region_mega"
    
    mega_base = getquery(sql, schema = "meta", dbms = get_env("ecoDI_DBMS"))

    # Perform the left join on mega_nm (from mega_info) and base_nm (from mega_base)
    result = pd.merge(
        mega_info,
        mega_base,
        how="left",
        left_on="mega_nm",
        right_on="base_nm",
        suffixes=("", "_drop")  # avoid duplicate column names
    ).drop(columns=['base_nm'])

    return result


def mapp_name2cty(cty_cd: str | None = None, cty_nm: str | None = None) -> pd.DataFrame:
    """
    Build a county information table based on a county code (`cty_cd`) and a county name (`cty_nm`).

    Parameters
    ----------
    cty_cd : str, optional
        The full county code (e.g., "27720").
    cty_nm : str, optional
        The county name (e.g., "군위군").

    Returns
    -------
    pd.DataFrame
        A DataFrame that contains the merged information from ``mapp2mega`` and
        the base county table (``bitSpatial.cty``).  The final columns are:

        - mega_cd : str  – the higher‑level (mega) code
        - mega_nm : str  – the higher‑level name
        - cty_cd  : str  – the original county code (potentially corrected)
        - cty_nm  : str  – the (possibly corrected) county name
        - base_cd : str  – the base code from ``bitSpatial.cty``
        - base_nm : str  – the base name from ``bitSpatial.cty``
    """
    # ------------------------------------------------------------
    # 1. Argument validation
    # ------------------------------------------------------------
    if cty_cd is None or cty_nm is None:
        raise ValueError("Both 'cty_cd' and 'cty_nm' must be provided.")

    # ------------------------------------------------------------
    # 2. Create the initial table
    # ------------------------------------------------------------
    cty_info = pd.DataFrame({
        "mega_cd": [cd[:2] for cd in cty_cd],   # first two characters
        "cty_cd": cty_cd,
        "cty_nm": cty_nm
    })

    # ------------------------------------------------------------
    # 3. Join with the mega‑code mapping (mapp2mega)
    # ------------------------------------------------------------
    # write.csv(ecoDI::mapp2mega, 
    #          file = "/Users/choonghyunryu/Documents/05_analytics/ecodi_python/src/ecodi/dbms/mapp2mega.csv", 
    #          row.names = FALSE)
    
    # Source path inside the installed ecoDI package:
    # <package_root>/dbms/mapp2mega.csv
    try:
        # `files` returns a Traversable object; we convert it to a string path.
        source_dir = importlib.resources.files("ecodi").joinpath("dbms")
        source_path = os.path.join(str(source_dir), "mapp2mega.csv")
    except Exception as exc:
        raise ImportError("Could not locate the ecoDI package files.") from exc
    
    mapp2mega = pd.read_csv(source_path)
    
    cty_info['mega_cd'] = cty_info['mega_cd'].astype(str)
    mapp2mega['mega_cd'] = mapp2mega['mega_cd'].astype(str)
    mapp2mega['base_cd'] = mapp2mega['base_cd'].astype(str)
    
    cty_info = cty_info.merge(
        mapp2mega,
        how="left",
        left_on="mega_cd",
        right_on="mega_cd",
        suffixes=("", "_map")
    ).drop(columns=['mega_cd'])  # drop the mega_nm from the mapping table if not needed

    # Rename the column coming from `mapp2mega` (assumed to be `base_cd`) to `mega_cd`
    if "base_cd" in cty_info.columns:
        cty_info = cty_info.rename(columns={"base_cd": "mega_cd"})
    else:
        # If the mapping table uses a different name for the mega code,
        # fall back to the original column.
        pass

    # Keep only the needed columns (order as in the R pipeline)
    cty_info = cty_info[["mega_cd", "cty_cd", "cty_nm"]]

    # ------------------------------------------------------------
    # 4. Apply name corrections (the long series of `mutate` calls)
    # ------------------------------------------------------------
    # Mapping of (mega_cd, old_name) -> new_name
    name_corrections = [
        ("28", "남구", "미추홀구"),
        ("41", "장안구", "수원시 장안구"),
        ("41", "권선구", "수원시 권선구"),
        ("41", "팔달구", "수원시 팔달구"),
        ("41", "영통구", "수원시 영통구"),
        ("41", "수정구", "성남시 수정구"),
        ("41", "중원구", "성남시 중원구"),
        ("41", "분당구", "성남시 분당구"),
        ("41", "만안구", "안양시 만안구"),
        ("41", "동안구", "안양시 동안구"),
        ("41", "원미구", "부천시 원미구"),
        ("41", "소사구", "부천시 소사구"),
        ("41", "오정구", "부천시 오정구"),
        ("41", "상록구", "안산시 상록구"),
        ("41", "단원구", "안산시 단원구"),
        ("41", "덕양구", "고양시 덕양구"),
        ("41", "일산동구", "고양시 일산동구"),
        ("41", "일산서구", "고양시 일산서구"),
        ("41", "처인구", "용인시 처인구"),
        ("41", "기흥구", "용인시 기흥구"),
        ("41", "수지구", "용인시 수지구"),
        ("43", "상당구", "청주시 상당구"),
        ("43", "서원구", "청주시 서원구"),
        ("43", "흥덕구", "청주시 흥덕구"),
        ("43", "청원구", "청주시 청원구"),
        ("44", "동남구", "천안시 동남구"),
        ("44", "서북구", "천안시 서북구"),
        ("52", "완산구", "전주시 완산구"),
        ("52", "덕진구", "전주시 덕진구"),
        ("47", "남구", "포항시 남구"),
        ("47", "북구", "포항시 북구"),
        ("48", "의창구", "창원시 의창구"),
        ("48", "성산구", "창원시 성산구"),
        ("48", "마산합포구", "창원시 마산합포구"),
        ("48", "마산회원구", "창원시 마산회원구"),
        ("48", "진해구", "창원시 진해구"),
    ]
    
    cty_info = cty_info.reset_index(drop=True)  # 중복 인덱스 제거
                                  
    for mega_cd, old_nm, new_nm in name_corrections:
        mask = (cty_info["mega_cd"] == mega_cd) & (cty_info["cty_nm"] == old_nm)
        cty_info.loc[mask, "cty_nm"] = new_nm

    # ------------------------------------------------------------
    # 5. Special handling for 군위군 (merged into Daegu on 2023‑07‑01)
    # ------------------------------------------------------------
    # mega_cd -> "27", cty_cd -> "27720" when cty_nm == "군위군"
    mask_gunwi = cty_info["cty_nm"] == "군위군"
    cty_info.loc[mask_gunwi, "mega_cd"] = "27"
    cty_info.loc[mask_gunwi, "cty_cd"] = "27720"

    # ------------------------------------------------------------
    # 6. Load base county table
    # ------------------------------------------------------------
    sql = "select mega_cd, mega_nm, cty_cd as base_cd, cty_nm as base_nm from ecodi_meta.mt_region_cty"
    
    cty_base = getquery(sql, schema = "meta", dbms = get_env("ecoDI_DBMS"))
    
    # ------------------------------------------------------------
    # 7. Final left join with the base table
    # ------------------------------------------------------------
    result = cty_info.merge(
        cty_base,
        how="left",
        left_on=["mega_cd", "cty_nm"],
        right_on=["mega_cd", "base_nm"]
    )

    result = result[["mega_cd", "cty_cd", "cty_nm", "mega_nm", "base_cd"]]

    return result


def ods2data(
    data_id: Optional[str] = None,
    to_metric: Optional[Any] = None,
    to_attr: Optional[Any] = None,
    region_var: Optional[str] = None,
    wider_var: Optional[str] = None,
    is_mega: bool = False,
    is_cty: bool = False,
    is_admi: bool = False,
) -> Dict[str, Any]:
    """
    Replicates the behaviour of the original R `ods2data` function using
    pandas for data manipulation.
    """

    # ------------------------------------------------------------------
    # 1. Validate input
    # ------------------------------------------------------------------
    if data_id is None:
        raise ValueError("`data_id` must be provided.")

    # ------------------------------------------------------------------
    # 2. Retrieve metadata tables
    # ------------------------------------------------------------------
    sql_table_info = f"""
        SELECT raw_table_id,
               raw_table_nm, 
               raw_schema_nm,
               pov_region_mega,
               pov_region_cty,
               pov_region_admi,
               pov_age_lc,
               pov_age_10,
               pov_age_10
        FROM ecodi_meta.mt_data_list
        WHERE data_id = '{data_id}';
    """
    table_info = getquery(sql_table_info, schema="meta")

    sql_itm_info = f"""
        SELECT *
        FROM ecodi_meta.mt_data_item
        WHERE data_id = '{data_id}';
    """
    itm_info = getquery(sql_itm_info, schema="meta")

    # ------------------------------------------------------------------
    # 3. Retrieve raw data
    # ------------------------------------------------------------------
    raw_schema = table_info.at[0, "raw_schema_nm"]
    raw_table = table_info.at[0, "raw_table_id"]
    sql_raw = f"SELECT * FROM {raw_schema}.{raw_table};"
    raw_data = getquery(sql_raw, schema="meta")

    # ------------------------------------------------------------------
    # 4. If `to_metric` is not supplied, reshape to a wide format
    # ------------------------------------------------------------------
    convert_data: pd.DataFrame
    if to_metric is None:
        # a) Drop the columns that are not needed
        cols_to_drop = [
            "org_id", "tbl_id", "lst_chn_de", "prd_se",
            "tbl_nm", "itm_nm", "unit_nm",
            "cret_dt", "cret_nm", "mdfy_dt", "mdfy_nm"
        ]
        convert_data = raw_data.drop(columns=cols_to_drop, errors="ignore")

        # b) Remove columns containing “_eng” or “obj_nm”
        eng_cols = [c for c in convert_data.columns if "_eng" in c]
        obj_cols = [c for c in convert_data.columns if "obj_nm" in c]
        convert_data = convert_data.drop(columns=eng_cols + obj_cols, errors="ignore")

        # c) Pivot wider (R: pivot_wider(names_from = "itm_id", values_from = "dt"))
        id_cols = [c for c in convert_data.columns if c not in {"itm_id", "dt"}]
        convert_data = (
            convert_data.pivot(index=id_cols, columns="itm_id", values="dt")
            .reset_index()
        )
        # flatten possible MultiIndex column names
        convert_data.columns = [
            f"{col}" if not isinstance(col, tuple) else "_".join(col).strip()
            for col in convert_data.columns
        ]

    # ------------------------------------------------------------------
    # 5. Region handling (mega / county / administration)
    # ------------------------------------------------------------------
    if region_var is not None:
        region_var_nm = f"{region_var}_nm"

        if is_mega:
            # rename
            convert_data = convert_data.rename(
                columns={region_var: "mega_cd", region_var_nm: "mega_nm"}
            )
            # filter numeric range
            convert_data = convert_data[
                convert_data["mega_cd"]
                .astype(int)
                .between(11, 99, inclusive="both")
            ]

            mega_info = mapp_name2mega(convert_data["mega_cd"], convert_data["mega_nm"])
            # mutate
            convert_data["mega_cd"] = mega_info["base_cd"].values
            convert_data["mega_nm"] = mega_info["mega_nm"].values

        elif is_cty:
            # rename
            convert_data = convert_data.rename(
                columns={region_var: "cty_cd", region_var_nm: "cty_nm"}
            )
            # filter numeric range
            convert_data = convert_data[
                convert_data["cty_cd"]
                .astype(int)
                .between(11000, 99999, inclusive="both")
            ]

            cty_info = mapp_name2cty(convert_data["cty_cd"], convert_data["cty_nm"])
            # mutate and reorder columns
            convert_data["mega_cd"] = cty_info["mega_cd"].values
            convert_data["mega_nm"] = cty_info["mega_nm"].values
            convert_data["cty_cd"] = cty_info["base_cd"].values
            convert_data["cty_nm"] = cty_info["cty_nm"].values

            # bring mega columns to the front (mirroring R's dplyr::select)
            cols = ["mega_cd", "mega_nm"] + [
                c for c in convert_data.columns if c not in {"mega_cd", "mega_nm"}
            ]
            convert_data = convert_data[cols]

        elif is_admi:
            # rename and filter
            convert_data = convert_data.rename(
                columns={region_var: "admi_cd", region_var_nm: "admi_nm"}
            )
            convert_data = convert_data[
                convert_data["admi_cd"]
                .astype(int)
                .between(11_000_000, 99_999_999, inclusive="both")
            ]

    # ------------------------------------------------------------------
    # 6. Wider‑variable handling
    # ------------------------------------------------------------------
    wider_info = None
    if wider_var is not None:
        # distinct item identifiers from the original raw data
        item_id = raw_data["itm_id"].drop_duplicates().iloc[0]
        item_nm = raw_data["itm_nm"].drop_duplicates().iloc[0]

        # distinct values for the wider dimension
        wider_element_id = (
            raw_data[wider_var].drop_duplicates().iloc[0]
        )
        wider_element_nm = (
            raw_data[f"{wider_var}_nm"].drop_duplicates().iloc[0]
        )

        wider_id = f"{item_id}_{wider_element_id}"
        wider_nm = f"{item_nm}_{wider_element_nm}"
        wider_info = pd.DataFrame(
            {"itm_id": [wider_id], "itm_nm": [wider_nm]}
        )

        # remove the name column of the wider variable before pivoting
        convert_data = convert_data.drop(columns=[f"{wider_var}_nm"], errors="ignore")

        # pivot wider using the value of `wider_var` as the new column suffix
        id_cols = [
            c
            for c in convert_data.columns
            if c not in {wider_var, item_id}
        ]
        pivoted = (
            convert_data.pivot(index=id_cols, columns=wider_var, values=item_id)
            .reset_index()
        )
        # flatten multi‑level column names (e.g., dt_1, dt_2, …)
        pivoted.columns = [
            f"{col}_{wider_var}" if isinstance(col, (int, str)) and col not in id_cols else col
            for col in pivoted.columns
        ]
        convert_data = pivoted

    # ------------------------------------------------------------------
    # 7. Final tidy‑up: rename, upper‑case, order
    # ------------------------------------------------------------------
    convert_data = convert_data.rename(columns={"prd_de": "BASE_PERIOD"})
    convert_data.columns = [c.upper() for c in convert_data.columns]

    # Ensure BASE_PERIOD is the first column
    cols = ["BASE_PERIOD"] + [c for c in convert_data.columns if c != "BASE_PERIOD"]
    convert_data = convert_data[cols]

    # ------------------------------------------------------------------
    # 8. Return result as a dictionary (mirrors the R list)
    # ------------------------------------------------------------------
    return {
        "table_info": table_info,
        "itm_info": itm_info,
        "data": convert_data,
        "wider_info": wider_info,
    }
    
def mk_mart_ddl_info(
    obj: Optional[Dict[str, Any]] = None,
    column_class: Optional[List[str]] = None,
    is_pk: Optional[List[str]] = None,
    is_fk: Optional[List[str]] = None,
    is_null: Optional[List[str]] = None,
    pov_region: Optional[List[str]] = None,
    metric_unit: Optional[List[Any]] = None,
    dbms: str = get_env("ecoDI_DBMS")
) -> Dict[str, Any]:
    """
    Build DDL information for a given object.

    Parameters
    ----------
    obj : dict
        Must contain ``table_info`` (with ``raw_table_id`` and ``raw_table_nm``)
        and ``data`` (a pandas.DataFrame). Optional keys: ``wider_info``.
    column_class, is_pk, is_fk, is_null, pov_region, metric_unit :
        Optional user‑supplied vectors. If ``None`` they are generated.
    dbms : str
        Target DBMS (e.g., ``'postgresql'``). Determines numeric type.

    Returns
    -------
    dict
        ``tab_id``, ``tab_nm``, primary‑key list ``pk`` and a DataFrame
        ``ddl_info`` describing each column.
    """
    # ------------------------------------------------------------------ #
    # Basic table identifiers
    # ------------------------------------------------------------------ #
    origin_tbl_id = obj["table_info"]["raw_table_id"].iloc[0]
    tab_df: pd.DataFrame = obj["data"]
    col_names = list(tab_df.columns)

    # ------------------------------------------------------------------ #
    # Table ID postfix (based on presence of specific columns)
    # ------------------------------------------------------------------ #
    if "ADMI_NM" in col_names:
        id_postfix = "_ADMI"
    elif "CTY_NM" in col_names:
        id_postfix = "_CTY"
    elif "MEGA_NM" in col_names:
        id_postfix = "_MEGA"
    else:
        id_postfix = ""

    tbl_id = f"{origin_tbl_id}{id_postfix}"

    # ------------------------------------------------------------------ #
    # Table name postfix (Korean level names)
    # ------------------------------------------------------------------ #
    if "ADMI_NM" in col_names:
        name_postfix = "_읍면동레벨"
    elif "CTY_NM" in col_names:
        name_postfix = "_시군구레벨"
    elif "MEGA_NM" in col_names:
        name_postfix = "_시도레벨"
    else:
        name_postfix = ""

    tab_nm = f"{obj['table_info']['raw_table_nm'].iloc[0]}{name_postfix}"

    # ------------------------------------------------------------------ #
    # Column identifiers and their Korean display names
    # ------------------------------------------------------------------ #
    id_stats = list(tab_df.columns)

    replace_map_display = {
        "BASE_PERIOD": "집계시점",
        "MEGA_CD": "시도코드",
        "MEGA_NM": "시도명",
        "CTY_CD": "군구코드",
        "CTY_NM": "시군구명",
        "ADMI_CD": "읍면동코드",
        "ADMI_NM": "읍면동명",
    }

    def replace_multiple(text: str, mapping: Dict[str, str]) -> str:
        for src, tgt in mapping.items():
            text = text.replace(src, tgt)
        return text

    nm_stats = [replace_multiple(col, replace_map_display) for col in id_stats]

    # ------------------------------------------------------------------ #
    # Retrieve metric column IDs from metadata
    # ------------------------------------------------------------------ #
    sql = f"""
        SELECT itm_id,
               itm_nm 
          FROM ecodi_meta.mt_kosis_itm
         WHERE tbl_id = '{origin_tbl_id}'
           AND obj_id = 'ITEM';
    """
    metric_column = getquery(sql, schema="meta")  # expects columns itm_id, itm_nm

    # Allow overriding by ``wider_info`` if supplied
    if obj.get("wider_info") is not None:
        metric_column = obj["wider_info"]

    metric_ids = set(metric_column["itm_id"])

    # Primary‑key candidates: columns that are **not** metric columns
    pk = list(set(id_stats) - metric_ids)

    # Replace metric column IDs in ``nm_stats`` with their proper names
    itm_lookup = dict(zip(metric_column["itm_id"], metric_column["itm_nm"]))
    nm_stats = [
        itm_lookup.get(col, name) for col, name in zip(id_stats, nm_stats)
    ]

    # ------------------------------------------------------------------ #
    # Column SQL data types
    # ------------------------------------------------------------------ #
    replace_map_type = {
        "BASE_PERIOD": "VARCHAR(10)",
        "MEGA_CD": "VARCHAR(2)",
        "MEGA_NM": "VARCHAR(20)",
        "CTY_CD": "VARCHAR(5)",
        "CTY_NM": "VARCHAR(20)",
        "ADMI_CD": "VARCHAR(8)",
        "ADMI_NM": "VARCHAR(20)",
    }

    type_stats = [replace_multiple(col, replace_map_type) for col in id_stats]

    # Adjust metric columns to numeric types depending on DBMS
    numeric_type = "NUMERIC" if dbms == "postgresql" else "DOUBLE"
    type_stats = [
        numeric_type if col in metric_ids else t
        for col, t in zip(id_stats, type_stats)
    ]

    # ------------------------------------------------------------------ #
    # Column classes (MTRC, DTTM, ATTR, NAME, etc.)
    # ------------------------------------------------------------------ #
    if column_class is None:
        replace_map_class = {
            "BASE_PERIOD": "DTTM",
            "MEGA_CD": "ATTR",
            "MEGA_NM": "NAME",
            "CTY_CD": "ATTR",
            "CTY_NM": "NAME",
            "ADMI_CD": "ATTR",
            "ADMI_NM": "NAME",
        }
        column_class = [replace_multiple(col, replace_map_class) for col in id_stats]
        # Override with "MTRC" for metric columns
        column_class = [
            "MTRC" if col in metric_ids else cls
            for col, cls in zip(id_stats, column_class)
        ]

    # ------------------------------------------------------------------ #
    # Primary‑key flag
    # ------------------------------------------------------------------ #
    if is_pk is None:
        is_pk = ["Y" if col in pk else "N" for col in id_stats]

    # ------------------------------------------------------------------ #
    # Foreign‑key flag
    # ------------------------------------------------------------------ #
    if is_fk is None:
        is_fk = [
            "N" if cls in {"MTRC", "DTTM", "NAME"} else "Y"
            for cls in column_class
        ]

    # ------------------------------------------------------------------ #
    # NULLability flag (always "N" in the original function)
    # ------------------------------------------------------------------ #
    if is_null is None:
        is_null = ["N"] * len(id_stats)

    # ------------------------------------------------------------------ #
    # Point‑of‑view (region) classification
    # ------------------------------------------------------------------ #
    if pov_region is None:
        pov_region = []
        for col in id_stats:
            if col in {"MEGA_CD", "MEGA_NM"}:
                pov_region.append("MEGA")
            elif col in {"CTY_CD", "CTY_NM"}:
                pov_region.append("CTY")
            elif col in {"ADMI_CD", "ADMI_NM"}:
                pov_region.append("ADMI")
            else:
                pov_region.append("")

    # ------------------------------------------------------------------ #
    # Metric unit (1 for metric columns, otherwise NaN)
    # ------------------------------------------------------------------ #
    if metric_unit is None:
        metric_unit = [1 if cls == "MTRC" else pd.NA for cls in column_class]

    # ------------------------------------------------------------------ #
    # Assemble the DDL information DataFrame
    # ------------------------------------------------------------------ #
    ddl_info = pd.DataFrame(
        {
            "id": id_stats,
            "nm": nm_stats,
            "type": type_stats,
            "class": column_class,
            "is_pk": is_pk,
            "is_fk": is_fk,
            "is_null": is_null,
            "pov_region": pov_region,
            "metric_unit": metric_unit,
        }
    )

    return {
        "tab_id": tbl_id,
        "tab_nm": tab_nm,
        "pk": pk,
        "ddl_info": ddl_info,
    }
    

def mk_mart_ddl(
    obj: Optional[Any] = None,
    column_class: Optional[Any] = None,
    is_pk: Optional[Any] = None,
    is_fk: Optional[Any] = None,
    is_null: Optional[Any] = None,
    pov_region: Optional[Any] = None,
    metric_unit: Optional[Any] = None,
    schema: str = "data",
    dbms: str = None
) -> str:
    """
    Build a DDL statement for a data mart table.

    Parameters
    ----------
    obj, column_class, is_pk, is_fk, is_null, pov_region, metric_unit :
        Arguments passed straight through to ``mk_mart_ddl_info``.
    schema : str, optional
        One of ``'data'``, ``'ods'`` or ``'meta'``.  Defaults to ``'data'``.
    dbms : str, optional
        Target database management system.  If omitted, the value is read
        from the environment variable ``ecoDI_DBMS``.

    Returns
    -------
    str
        The complete DDL statement (including comments) for the chosen DBMS.
    """

    # ------------------------------------------------------------------
    # Resolve default arguments
    # ------------------------------------------------------------------
    allowed_schemas = {"data", "ods", "meta"}
    if schema not in allowed_schemas:
        raise ValueError(f"schema must be one of {allowed_schemas}")

    dbms = get_env("ecoDI_DBMS") if dbms is None else dbms

    # ------------------------------------------------------------------
    # Retrieve metadata about the table (implementation is assumed to exist)
    # ------------------------------------------------------------------
    result: Dict[str, Any] = mk_mart_ddl_info(
        obj=obj,
        column_class=column_class,
        is_pk=is_pk,
        is_fk=is_fk,
        is_null=is_null,
        pov_region=pov_region,
        metric_unit=metric_unit,
    )

    tab_id: str = result["tab_id"]
    ddl_info: pd.DataFrame = result["ddl_info"]       # expected columns: id, type, is_null, nm
    tab_name: str = result["tab_nm"]
    pk_columns: List[str] = result["pk"]             # list of primary‑key column names

    # ------------------------------------------------------------------
    # Helper to produce a column definition line
    # ------------------------------------------------------------------
    def column_definition(row) -> str:
        col_name = row["id"].lower()
        col_type = row["type"]
        nullable = "" if row["is_null"] == "N" else ""
        # For MySQL we add a trailing comma later; for PostgreSQL the comma is added when joining.
        return f"{col_name} {col_type}{' NOT NULL' if row['is_null'] == 'N' else ''}"

    # ------------------------------------------------------------------
    # MySQL DDL generation
    # ------------------------------------------------------------------
    if dbms == "mysql":
        # Base CREATE TABLE line
        ddl_lines: List[str] = [
            f"CREATE TABLE IF NOT EXISTS ecodi_{schema}.{tab_id} ("
        ]

        # Column definitions from `ddl_info`
        for _, row in ddl_info.iterrows():
            ddl_lines.append(
                f"    {column_definition(row)} COMMENT '{row['nm']}',"
            )

        # Additional audit columns
        ddl_lines.extend(
            [
                "    cret_dt DATETIME NOT NULL COMMENT '생성일시',",
                "    cret_nm VARCHAR(10) NOT NULL COMMENT '생성자',",
                "    mdfy_dt DATETIME COMMENT '수정일시',",
                "    mdfy_nm VARCHAR(10) COMMENT '수정자',",
            ]
        )

        # Primary‑key constraint
        pk_clause = ", ".join(pk_columns)
        ddl_lines.append(
            f"    CONSTRAINT {tab_id}_pkey PRIMARY KEY({pk_clause})"
        )
        ddl_lines.append(");")                       # close CREATE TABLE

        # Table comment
        ddl_lines.append(
            f"ALTER TABLE ecodi_{schema}.{tab_id} COMMENT = '{tab_name}';"
        )

        ddl = "\n".join(ddl_lines) + "\n"

    # ------------------------------------------------------------------
    # PostgreSQL DDL generation
    # ------------------------------------------------------------------
    elif dbms == "postgresql":
        tab_id_lc = tab_id.lower()

        # Base CREATE TABLE line
        ddl_lines: List[str] = [
            f"CREATE TABLE IF NOT EXISTS ecodi_{schema}.{tab_id_lc} ("
        ]

        # Column definitions from `ddl_info`
        for _, row in ddl_info.iterrows():
            ddl_lines.append(
                f"    {column_definition(row)},"
            )

        # Additional audit columns (with commas already handled)
        ddl_lines.extend(
            [
                "    cret_dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,",
                "    cret_nm VARCHAR(20) NOT NULL,",
                "    mdfy_dt TIMESTAMP,",
                "    mdfy_nm VARCHAR(20),",
            ]
        )

        # Primary‑key constraint
        pk_clause = ", ".join(col.lower() for col in pk_columns)
        ddl_lines.append(
            f"    CONSTRAINT {tab_id_lc}_pkey PRIMARY KEY({pk_clause})"
        )
        ddl_lines.append(");")  # close CREATE TABLE

        # Table comment
        ddl_lines.append(
            f"COMMENT ON TABLE ecodi_{schema}.{tab_id_lc} IS '{tab_name}';"
        )

        # Column comments
        for _, row in ddl_info.iterrows():
            col_name_lc = row["id"].lower()
            ddl_lines.append(
                f"COMMENT ON COLUMN ecodi_{schema}.{tab_id_lc}.{col_name_lc} IS '{row['nm']}';"
            )

        # Audit column comments (Korean descriptions kept as in the original)
        ddl_lines.extend(
            [
                f"COMMENT ON COLUMN ecodi_{schema}.{tab_id_lc}.cret_dt IS '생성일시';",
                f"COMMENT ON COLUMN ecodi_{schema}.{tab_id_lc}.cret_nm IS '생성자';",
                f"COMMENT ON COLUMN ecodi_{schema}.{tab_id_lc}.mdfy_dt IS '수정일시';",
                f"COMMENT ON COLUMN ecodi_{schema}.{tab_id_lc}.mdfy_nm IS '수정자';",
            ]
        )

        ddl = "\n".join(ddl_lines) + "\n"

    else:
        raise ValueError("Unsupported dbms. Expected 'mysql' or 'postgresql'.")

    return ddl
  

def mk_mart_table(obj=None, column_class=None, is_pk=None, is_fk=None,
                  is_null=None, pov_region=None, pov_age=None, subject=None,
                  sub_subject=None, metric_unit=None, table_desc=None,
                  schema="data", dbms: str = None):

    valid_schemas = ["data", "ods", "meta"]
    if schema not in valid_schemas:
        raise ValueError(f"Invalid 'schema': {schema}. Must be one of {valid_schemas}.")

    schema_nm = f"ecodi_{schema}"
    pov_region = "" if pov_region is None else pov_region
    pov_age = "" if pov_age is None else pov_age
    table_desc = "" if table_desc is None else table_desc

    if pov_region != "" and pov_region not in ["MEGA", "CTY", "ADMI"]:
        raise ValueError(f"Invalid 'pov_region' parameter: {pov_region}. "
                         f"It must be one of 'MEGA', 'CTY', 'ADMI'.")

    if pov_age != "" and pov_age not in ["AGE05", "AGE10", "AGELC"]:
        raise ValueError(f"Invalid 'pov_age' parameter: {pov_age}. "
                         f"It must be one of 'AGE05', 'AGE10', 'AGELC'.")

    if (obj is None or not isinstance(obj, dict) or
            not all(k in obj for k in ["table_info", "itm_info", "data"])):
        raise ValueError("Invalid 'obj' parameter. It must be a metadata object returned by 'ods2data()'.")

    if len(obj["data"]) == 0:
        raise ValueError("The 'obj' parameter contains no data to create a mart table.")

    if not isinstance(obj["data"], pd.DataFrame):
        raise TypeError("The 'data' component of 'obj' must be a DataFrame.")

    if sub_subject is None:
        raise ValueError("The 'sub_subject' parameter is required but was not provided.")

    # DDL 정보 생성
    ddl_info = mk_mart_ddl_info(
        obj=obj, column_class=column_class, is_pk=is_pk, is_fk=is_fk,
        is_null=is_null, pov_region=pov_region, metric_unit=metric_unit)

    dbms = get_env("ecoDI_DBMS") if dbms is None else dbms
    
    ddl_statement = mk_mart_ddl(
        obj=obj, column_class=column_class, is_pk=is_pk, is_fk=is_fk,
        is_null=is_null, pov_region=pov_region, metric_unit=metric_unit,
        schema=schema, dbms=dbms)

    db_connect(schema)
    conn = get_env(f"{schema.upper()}_CON")

    ddl_from_text(conn, ddl_statement)

    ## 데이터 마트 테이블 생성 -------------------------------------------------
    is_ok = db_settable(name=ddl_info["tab_id"], value=obj["data"],
                        append=True, schema=schema)

    ## MT_TABLE_COLUMN 메타 테이블에 정보 삽입 ---------------------------------
    schema = "meta"
    db_connect(schema)

    tab_column = ddl_info["ddl_info"]
    tab_column = tab_column.rename(columns={'class': 'column_clss'})
    uid = get_env("USERNAME")

    isql = "" 
    
    engine = get_env(f"{schema.upper()}_CON")
    
    for i, row in enumerate(tab_column.itertuples(), start=1):
        column_type = re.sub(r"\(.*", "", row.type)
        column_len = re.sub(r"\D", "", row.type)
        column_unit = 0 if pd.isna(row.metric_unit) else row.metric_unit
        
        if dbms == "mysql":
            isql = f"""INSERT INTO ecodi_meta.mt_table_column
                        SET table_id = '{ddl_info["tab_id"]}',
                            column_seq = {i},
                            column_id = '{row.id}',
                            column_nm = '{row.nm}',
                            pov_region = '{row.pov_region}',
                            column_type = '{column_type}',
                            column_len = '{column_len}',
                            column_null = '{row.is_null}',
                            column_pk = '{row.is_pk}',
                            column_fk = '{row.is_fk}',
                            column_clss = '{row.column_clss}',
                            column_unit = {column_unit},
                            cret_nm = '{uid}';"""
        elif dbms == "postgresql":
            isql = f"""INSERT INTO ecodi_meta.mt_table_column
                        (table_id, column_seq, column_id, column_nm, pov_region,
                         column_type, column_len, column_null, column_pk,
                         column_fk, column_clss, column_unit, cret_nm)
                        VALUES ('{ddl_info["tab_id"]}', {i}, '{row.id}',
                         '{row.nm}', '{row.pov_region}', '{column_type}',
                         '{column_len}', '{row.is_null}', '{row.is_pk}',
                         '{row.is_fk}', '{row.column_clss}', {column_unit}, '{uid}');"""
        
        try:
            with engine.begin() as conn:
                conn.execute(text(isql))
        except SQLAlchemyError as e:
            # Logging failures are intentionally ignored here, mirroring the original script.
            pass


    ## MT_TABLE_COMMENT 메타 테이블에 정보 삽입 --------------------------------
    data_id = obj["itm_info"]["data_id"].iloc[0]
    table_id = ddl_info["tab_id"]

    sql = f"""SELECT data_comment
                FROM ecodi_meta.mt_data_comment
               WHERE data_id = '{data_id}';"""

    comment_info = getquery(sql, schema="meta")["data_comment"].tolist()

    for i, comment in enumerate(comment_info, start=1):
        if dbms == "mysql":
            isql = f"""INSERT INTO ecodi_meta.mt_table_comment
                        SET table_id = '{table_id}',
                            comment_seq = {i},
                            table_comment = '{comment}',
                            cret_nm = '{uid}';"""
        elif dbms == "postgresql":
            isql = f"""INSERT INTO ecodi_meta.mt_table_comment
                        (table_id, comment_seq, table_comment, cret_nm)
                        VALUES ('{table_id}', {i}, '{comment}', '{uid}');"""

        try:
            with engine.begin() as conn:
                conn.execute(text(isql))
        except SQLAlchemyError as e:
            # Logging failures are intentionally ignored here, mirroring the original script.
            pass
          

    ## MT_TABLE_UPDATE 메타 테이블에 정보 삽입 ---------------------------------
    sql = f"""SELECT data_prvdr_cycle,
                     data_base_pov,
                     data_update_date
                FROM ecodi_meta.mt_data_update
               WHERE data_id = '{data_id}';"""

    update_info = getquery(sql, schema="meta")

    isql = "" 
    
    for i, row in enumerate(update_info.itertuples(), start=1):
        if dbms == "mysql":
            isql = f"""INSERT INTO ecodi_meta.mt_table_update
                        SET table_id = '{table_id}',
                            update_seq = {i},
                            prvdr_cycle = '{row.data_prvdr_cycle}',
                            data_base_pov = '{row.data_base_pov}',
                            update_date = '{row.data_update_date}',
                            cret_nm = '{uid}';"""
        elif dbms == "postgresql":
            isql = f"""INSERT INTO ecodi_meta.mt_table_update
                        (table_id, update_seq, prvdr_cycle, data_base_pov,
                         update_date, cret_nm)
                        VALUES ('{table_id}', {i}, '{row.data_prvdr_cycle}',
                         '{row.data_base_pov}', '{row.data_update_date}', '{uid}');"""

        try:
            with engine.begin() as conn:
                conn.execute(text(isql))
        except SQLAlchemyError as e:
            # Logging failures are intentionally ignored here, mirroring the original script.
            pass
            

    ## MT_TABLE_LIST 메타 테이블에 정보 삽입 -----------------------------------
    sql = f"""SELECT code_encode, code_decode
                FROM ecodi_meta.mt_code_list
               WHERE code_id = 'C00004';"""

    subject_info = getquery(sql, schema="meta")

    if subject not in subject_info["code_encode"].values:
        valid = ", ".join(subject_info["code_encode"].tolist())
        raise ValueError(f"Invalid 'subject' parameter: {subject}. "
                         f"It must be one of {valid}.")

    isql = "" 
    
    if dbms == "mysql":
        isql = f"""INSERT INTO ecodi_meta.mt_table_list
                    SET table_id = '{table_id}',
                        schema_nm = '{schema_nm}',
                        data_id = '{data_id}',
                        table_nm = '{ddl_info["tab_nm"]}',
                        table_subclss = '{subject}',
                        pov_region = '{pov_region}',
                        table_desc = '{table_desc}',
                        cret_nm = '{uid}';"""
    elif dbms == "postgresql":
        isql = f"""INSERT INTO ecodi_meta.mt_table_list
                    (table_id, schema_nm, data_id, table_nm, table_subclss,
                     pov_region, table_desc, cret_nm)
                    VALUES ('{table_id}', '{schema_nm}', '{data_id}',
                            '{ddl_info["tab_nm"]}', '{subject}', '{pov_region}',
                            '{table_desc}', '{uid}');"""

    try:
        with engine.begin() as conn:
            conn.execute(text(isql))
    except SQLAlchemyError as e:
        # Logging failures are intentionally ignored here, mirroring the original script.
        pass

    ## MT_TABLE_CLSS 메타 테이블에 정보 삽입 -----------------------------------
    sql = f"""SELECT code_encode, code_decode
                FROM ecodi_meta.mt_code_list
               WHERE parent_id = 'C00004'
                 AND parent_encode = '{subject}';"""

    sub_subject_info = getquery(sql, schema="meta")

    if sub_subject not in sub_subject_info["code_encode"].values:
        valid = ", ".join(sub_subject_info["code_encode"].tolist())
        raise ValueError(f"Invalid 'sub_subject' parameter: {sub_subject}. "
                         f"It must be one of {valid}.")

    subject_nm = subject_info.loc[
        subject_info["code_encode"] == subject, "code_decode"].iloc[0]

    sub_subject_nm = sub_subject_info.loc[
        sub_subject_info["code_encode"] == sub_subject, "code_decode"].iloc[0]

    isql = "" 
    
    if dbms == "mysql":
        isql = f"""INSERT INTO ecodi_meta.mt_table_clss
                    SET table_id = '{table_id}',
                        clss_seq = 1,
                        table_clss = '{subject}',
                        table_subclss = '{sub_subject}',
                        table_clss_nm = '{subject_nm}',
                        table_subclss_nm = '{sub_subject_nm}',
                        cret_nm = '{uid}';"""
    elif dbms == "postgresql":
        isql = f"""INSERT INTO ecodi_meta.mt_table_clss
                    (table_id, clss_seq, table_clss, table_subclss,
                     table_clss_nm, table_subclss_nm, cret_nm)
                    VALUES ('{table_id}', 1, '{subject}', '{sub_subject}',
                     '{subject_nm}', '{sub_subject_nm}', '{uid}');"""

    try:
        with engine.begin() as conn:
            conn.execute(text(isql))
    except SQLAlchemyError as e:
        # Logging failures are intentionally ignored here, mirroring the original script.
        pass

    if dbms == "mysql":
        get_env(f"{schema.upper()}_CON").connect().commit()

    return is_ok
  
  
# Exported symbols (similar to R's @export)
__all__ = [
    "mapp_name2mega",
    "mapp_name2cty",
    "ods2data",
    "mk_mart_ddl_info",
    "mk_mart_ddl",
    "mk_mart_table"
]
