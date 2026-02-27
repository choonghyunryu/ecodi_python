import os
import base64
from typing import Optional, Any, List, Dict
import sqlalchemy
from sqlalchemy import create_engine, text, inspect, insert
from sqlalchemy import MetaData
from sqlalchemy import Table, Column, DateTime, Integer, String
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import requests
import datetime
import time
import logging
from urllib.parse import urlencode

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
    _read_sql_file,
    _split_sql_statements,    
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
    query_from_file,
    ddl_from_text
)

# ----------------------------------------------------------------------
# Functions that map directly from the R source
# ----------------------------------------------------------------------

def from_meta_apiurl(api_url_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve rows from `mt_api_url` optionally filtered by `api_url_id`."""
    if not is_connected("meta"):
        db_connect("meta")

    if api_url_id is None:
        sql = "SELECT * FROM mt_api_url"
    else:
        sql = f"SELECT * FROM mt_api_url WHERE api_url_id = '{api_url_id}'"

    return getquery(sql)


def from_meta_param(api_url_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve rows from `mt_api_param` optionally filtered by `api_url_id`."""
    if not is_connected("meta"):
        db_connect("meta")

    if api_url_id is None:
        sql = "SELECT * FROM mt_api_param ORDER BY api_url_id, param_seq"
    else:
        sql = (
            f"SELECT * FROM mt_api_param "
            f"WHERE api_url_id = '{api_url_id}' "
            f"ORDER BY param_seq"
        )

    return getquery(sql)


def from_meta_apikey(api_key_id: Optional[str] = None) -> Optional[str]:
    """Fetch and decode the encrypted API key for a given `api_key_id`."""
    if not is_connected("meta"):
        db_connect("meta")

    user_id = get_env("USERNAME")
    user_id_enc = encode_base64(user_id)

    # Ensure connection (re‑checking as in the original R code)
    if not is_connected("meta"):
        db_connect("meta")

    sql = (
        f"SELECT key_enc FROM mt_api_key "
        f"WHERE key_id = '{api_key_id}' "
        f"AND user_id_enc = '{user_id_enc}'"
    )
    result = getquery(sql)

    if len(result) == 0:
        return None

    return decode_base64(result.get("key_enc")[0])


def set_apikey_env(api_key_id: Optional[str] = None) -> None:
    """Store the retrieved API key in the process environment."""
    api_key = from_meta_apikey(api_key_id=api_key_id)

    if api_key is None:
        raise RuntimeError(
            f"API key for API Key ID {api_key_id} not found. "
            "Please register your API key first."
        )

    env_var_name = f"{api_key_id}_API_KEY"
    os.environ[env_var_name] = api_key
    # Function returns None (equivalent to R's invisible())


def from_meta_datalist(data_id: Optional[str] = None) -> pd.DataFrame:
    """Retrieve data list rows, optionally filtered by `data_id`."""
    if not is_connected("meta"):
        db_connect("meta")

    if data_id is not None:
        sql = f"SELECT * FROM mt_data_list WHERE data_id = '{data_id}'"
    else:
        sql = "SELECT * FROM mt_data_list"

    return getquery(sql)


def from_meta_pramset(
    api_url_id: Optional[str] = None,
    param_seq: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Retrieve parameter set rows with flexible filtering."""
    if not is_connected("meta"):
        db_connect("meta")

    if api_url_id is not None and param_seq is not None:
        sql = (
            f"SELECT * FROM mt_api_paramset "
            f"WHERE api_url_id = '{api_url_id}' "
            f"AND param_seq = {param_seq} "
            f"ORDER BY value_seq"
        )
    elif api_url_id is not None and param_seq is None:
        sql = (
            f"SELECT * FROM mt_api_paramset "
            f"WHERE api_url_id = '{api_url_id}' "
            f"ORDER BY value_seq"
        )
    elif api_url_id is None and param_seq is not None:
        raise ValueError(
            "When 'param_seq' is provided, 'api_url_id' must also be provided."
        )
    else:
        sql = (
            "SELECT * FROM mt_api_paramset "
            "ORDER BY api_url_id, param_seq, value_seq"
        )

    return getquery(sql)


def from_meta_result(api_url_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch result rows, optionally filtered by `api_url_id`."""
    if not is_connected("meta"):
        db_connect("meta")

    if api_url_id is None:
        sql = "SELECT * FROM mt_api_result"
    else:
        sql = f"SELECT * FROM mt_api_result WHERE api_url_id = '{api_url_id}'"

    return getquery(sql)
  

def from_meta_ddl(
    data_id=None,
    is_postfix=True,
    schema="data",
    dbms: str | None = None
):
    if data_id is None:
        raise ValueError("'data_id' must be provided.")

    if not is_connected("meta"):
        db_connect("meta")

    if schema not in ("data", "ods", "meta"):
        raise ValueError("schema must be one of ('data', 'ods', 'meta')")

    if dbms is None:
        dbms = get_env("ecoDI_DBMS")
    if dbms not in {"mysql", "postgresql"}:
        raise ValueError("`dbms` must be either 'mysql' or 'postgresql'")
      
    # 메타 정보 조회
    data_info = from_meta_datalist(data_id=data_id)
    table_id = data_info.at[0, "raw_table_id"].lower()
    table_nm = data_info.at[0, "data_nm"]
    api_url_id = data_info.at[0, "api_url_id"]

    result_info = from_meta_result(api_url_id=api_url_id)

    # Primary Key 컬럼 추출
    primary_key_cols = (
        result_info[result_info["is_pk"] == "Y"]["result_id"]
        .str.lower()
        .tolist()
    )

    pk_variable = ",".join(primary_key_cols)

    ddl = ""

    # -----------------------------
    # MySQL
    # -----------------------------
    if dbms == "mysql":
        sql = f"CREATE TABLE IF NOT EXISTS ecodi_{schema}.{table_id} ( "
        pk = f"CONSTRAINT {table_id}_pkey PRIMARY KEY ({pk_variable}) "

        post_fix = """
        cret_dt DATETIME DEFAULT now() NOT NULL COMMENT '생성일시',
        cret_nm VARCHAR(20) NOT NULL COMMENT '생성자',
        mdfy_dt DATETIME COMMENT '수정일시',
        mdfy_nm VARCHAR(20) COMMENT '수정자'
        """

        for i, row in result_info.iterrows():
            column_nm = row["result_id"].lower()
            data_type = row["data_type"]
            data_length = row["data_len"]
            is_missing = row["is_missing"]
            comment_txt = row["result_nm"]

            sql += f"  {column_nm} {data_type}"

            if data_length and data_length > 0:
                sql += f"({int(data_length)})"

            if is_missing != "Y":
                sql += " NOT NULL"

            sql += f" COMMENT '{comment_txt}'"

            if i < len(result_info) - 1:
                sql += ", "
            else:
                if primary_key_cols:
                    if is_postfix:
                        sql += f", {post_fix}, {pk} );"
                    else:
                        sql += f", {pk} );"
                else:
                    if is_postfix:
                        sql += f", {post_fix} );"
                    else:
                        sql += " );"

        ddl = f"{sql} ALTER TABLE ecodi_{schema}.{table_id} COMMENT = '{table_nm}';"

    # -----------------------------
    # PostgreSQL
    # -----------------------------
    elif dbms == "postgresql":
        sql = f"CREATE TABLE IF NOT EXISTS ecodi_{schema}.{table_id} ( "
        pk = f"CONSTRAINT {table_id}_pkey PRIMARY KEY ({pk_variable}) "

        post_fix = """
        cret_dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        cret_nm VARCHAR(20) NOT NULL,
        mdfy_dt TIMESTAMP,
        mdfy_nm VARCHAR(20)
        """

        for i, row in result_info.iterrows():
            column_nm = row["result_id"].lower()
            data_type = row["data_type"]
            data_length = row["data_len"]
            is_missing = row["is_missing"]

            sql += f"  {column_nm} {data_type}"

            if data_length and data_length > 0:
                sql += f"({int(data_length)})"

            if is_missing != "Y":
                sql += " NOT NULL"

            if i < len(result_info) - 1:
                sql += ", "
            else:
                if primary_key_cols:
                    if is_postfix:
                        sql += f", {post_fix}, {pk} );"
                    else:
                        sql += f", {pk} );"
                else:
                    if is_postfix:
                        sql += f", {post_fix} );"
                    else:
                        sql += " );"

        ddl = f"{sql}\n\nCOMMENT ON TABLE ecodi_{schema}.{table_id} IS '{table_nm}';"

        for _, row in result_info.iterrows():
            ddl += (
                f"\nCOMMENT ON COLUMN ecodi_{schema}.{table_id}."
                f"{row['result_id']} IS '{row['result_nm']}';"
            )

        ddl += f"""
        COMMENT ON COLUMN ecodi_{schema}.{table_id}.cret_dt IS '생성일시';
        COMMENT ON COLUMN ecodi_{schema}.{table_id}.cret_nm IS '생성자';
        COMMENT ON COLUMN ecodi_{schema}.{table_id}.mdfy_dt IS '수정일시';
        COMMENT ON COLUMN ecodi_{schema}.{table_id}.mdfy_nm IS '수정자';
        """

    else:
        raise ValueError(f"Unsupported DBMS type: {dbms}")

    return ddl


# ----------------------------------------------------------------------
# Helper functions (place‑holders).  They must be implemented elsewhere
# ----------------------------------------------------------------------
# from_meta_datalist(data_id) -> DataFrame
# from_meta_apiurl(api_url_id) -> DataFrame
# from_meta_apikey(api_key_id) -> scalar (e.g., string) or None
# from_meta_param(api_url_id) -> DataFrame
# from_meta_result(api_url_id) -> DataFrame
# ----------------------------------------------------------------------


def get_api_url(data_id=None, **kwargs):
    """
    Build the full API call URL for a given data_id.
    Additional parameters are supplied via **kwargs.
    """
    if data_id is None:
        raise ValueError("'data_id' must be provided.")

    # ------------------------------------------------------------------
    # Retrieve data list information
    # ------------------------------------------------------------------
    data_list = from_meta_datalist(data_id)
    if data_list.empty:
        raise ValueError(f"Data ID {data_id} not found in data list meta database.")

    api_url_id = data_list["api_url_id"].iloc[0]

    # ------------------------------------------------------------------
    # Retrieve API URL information
    # ------------------------------------------------------------------
    api_url = from_meta_apiurl(api_url_id)
    if api_url.empty:
        raise ValueError(f"Data ID {data_id} not found in api url meta database.")

    base_url = api_url["call_url"].iloc[0]
    is_usekey = api_url["is_usekey"].iloc[0]
    api_key_id = api_url["key_id"].iloc[0]

    # ------------------------------------------------------------------
    # Retrieve API key if needed
    # ------------------------------------------------------------------
    api_key = None
    if is_usekey == "Y":
        api_key = from_meta_apikey(api_key_id)
        if api_key is None or pd.isna(api_key):
            raise ValueError(
                f"API key for API Key ID {api_key_id} not found. Please register your API key first."
            )

    # ------------------------------------------------------------------
    # Retrieve API parameter information
    # ------------------------------------------------------------------
    params = from_meta_param(api_url_id)

    # parameters that are marked as key (is_key == "Y")
    key_params = (
        params.loc[params["is_key"] == "Y", "param_id"]
        .astype(str)
        .tolist()
    )

    query_params = {}

    # iterate over each parameter definition
    for _, row in params.iterrows():
        param_id = str(row["param_id"])
        default_value = row["default_value"]

        if param_id in key_params:
            # Use API key for key parameters
            query_params[param_id] = api_key
        else:
            # Use supplied argument if present, otherwise default
            if param_id in kwargs:
                query_params[param_id] = kwargs[param_id]
            else:
                query_params[param_id] = default_value

    # ------------------------------------------------------------------
    # Build final URL
    # ------------------------------------------------------------------
    query_string = urlencode(query_params)
    full_url = f"{base_url}?{query_string}"
    return full_url


def get_api_result(data_id=None, **kwargs) -> pd.DataFrame:
    """
    Call the API built by `get_api_url` and return the JSON result as a DataFrame.
    """
    if data_id is None:
        raise ValueError("'data_id' must be provided.")

    call_url = get_api_url(data_id=data_id, **kwargs)

    response = requests.get(call_url)
    response.raise_for_status()            # raise if HTTP error

    # Convert JSON payload to a pandas DataFrame
    result_json = response.json()
    df_result = pd.json_normalize(result_json)
    
    # If the result is not a DataFrame or is empty, just print it
    if not isinstance(df_result, pd.DataFrame) or df_result.empty:
        print(df_result)

    return df_result


def get_api_data(data_id=None, **kwargs):
    """
    Retrieve API data and harmonise it with meta‑information.
    The function returns a DataFrame containing the result together with
    any additional parameter values supplied via **kwargs.
    """
    if data_id is None:
        raise ValueError("'data_id' must be provided.")

    # ------------------------------------------------------------------
    # Retrieve meta information
    # ------------------------------------------------------------------
    data_info = from_meta_datalist(data_id=data_id)
    if data_info.empty:
        raise ValueError(f"Data ID {data_id} not found in data list meta database.")

    result_info = from_meta_result(api_url_id=data_info["api_url_id"].iloc[0])

    # ------------------------------------------------------------------
    # Initialise an empty DataFrame whose columns are the result IDs
    # ------------------------------------------------------------------
    df_data = pd.DataFrame(
        {str(rid): [pd.NA] for rid in result_info["result_id"].astype(str).tolist()}
    )

    # ------------------------------------------------------------------
    # Retrieve the actual API result
    # ------------------------------------------------------------------
    df_result = get_api_result(data_id=data_id, **kwargs)

    # If the API call did not return a usable DataFrame, return it as‑is
    if not isinstance(df_result, pd.DataFrame) or df_result.empty:
        return df_result

    # Combine existing (mostly empty) df_data with the new result,
    # then drop rows that are entirely NA
    df_data = (
        pd.concat([df_data, df_result], ignore_index=True)
        .dropna(how="all")
        .reset_index(drop=True)
    )

    # ------------------------------------------------------------------
    # Determine which columns correspond to parameters that should be
    # overwritten by the additional arguments.
    # ------------------------------------------------------------------
    param_ids = (
        result_info.dropna(subset=["param_id"])
        .loc[result_info["param_id"] != ""]
        [["result_id", "param_id"]]
    )

    # Update df_data with supplied parameter values
    for _, row in param_ids.iterrows():
        variable_id = str(row["result_id"])
        param_id = str(row["param_id"])
        if variable_id in df_data.columns and param_id in kwargs:
            df_data[variable_id] = kwargs[param_id]

    return df_data


def import_api_data(
    data_id: Optional[str] = None,
    schema: str = "ods",
    sleep_seconds: float = 0,
    verbose: bool = True,
    dbms: Optional[str] = None,
    **kwargs: Any,
) -> Optional[bool]:
    """
    Import data identified by `data_id` from an API into the appropriate
    database schema and write a log entry to the metadata schema.

    Parameters
    ----------
    data_id : str
        Identifier of the data set to import (mandatory).
    schema : {'ods', 'meta', 'data'}
        Target schema for the operation. Defaults to ``'ods'``.
    sleep_seconds : float
        Optional pause (in seconds) before starting the import.
    verbose : bool
        If True, status messages are emitted via the ``logging`` module.
    dbms : str, optional
        Database management system type (e.g. ``'mysql'`` or ``'postgresql'``).
        If omitted, the value is taken from the environment variable
        ``ecoDI_DBMS``.
    **kwargs
        Additional parameters forwarded to the API request and used for
        logging.

    Returns
    -------
    bool or None
        ``True`` if the data was appended successfully; ``False`` if no
        data was retrieved; ``None`` if an unexpected error occurred.
    """

    logger = logging.getLogger(__name__)
    if verbose:
        logging.basicConfig(level=logging.INFO, format="%(message)s")

    if data_id is None:
        raise ValueError("'data_id' must be provided.")

    # Validate schema argument
    allowed_schemas = {"ods", "meta", "data"}
    if schema not in allowed_schemas:
        raise ValueError(f"schema must be one of {allowed_schemas}")

    # Resolve DBMS from environment if not supplied
    if dbms is None:
        dbms = get_env("ecoDI_DBMS")

    # Build a query‑string representation of the extra kwargs
    api_params = "&".join(f"{k}={v}" for k, v in kwargs.items())

    # Optional sleep
    if sleep_seconds:
        time.sleep(sleep_seconds)

    if verbose:
        logger.info(
            f"Importing API data for data ID: {data_id} with parameters: {api_params}"
        )

    # Initialise status flags in the custom environment
    set_env("STATUS", "1")
    set_env("EMSG", "")

    start_dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ------------------------------------------------------------------
    # Retrieve meta‑information about the data set
    # ------------------------------------------------------------------
    data_info = from_meta_datalist(data_id=data_id)
    data_id = data_info.at[0,"data_id"]
    table_id = data_info.at[0,"raw_table_id"].lower()
    table_name = data_info.at[0,"raw_table_nm"]
    raw_site_id = data_info.at[0,"raw_site_id"]

    ddl_text = from_meta_ddl(data_id=data_id)

    # ------------------------------------------------------------------
    # Pull the actual data from the API
    # ------------------------------------------------------------------
    df_data = get_api_data(data_id=data_id, **kwargs)

    # ------------------------------------------------------------------
    # Authentication / user info
    # ------------------------------------------------------------------
    user_id = get_env("USERNAME")
    db_info_encoded = get_env(f"{schema.upper()}_INFO")
    db_info = decode_base64(db_info_encoded)
    db_id = db_info.split(":")[0]

    # ------------------------------------------------------------------
    # Branch: no data received
    # ------------------------------------------------------------------
    if not isinstance(df_data, pd.DataFrame) or df_data.empty:
        if verbose:
            logger.info(
                f"No data retrieved for data ID: {data_id}. Import operation aborted."
            )

        end_dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_msg = ""

        if raw_site_id == "RS0001" and isinstance(df_data, pd.DataFrame):
            error_msg = df_data.get("errMsg", "")

        status = "0"
        record_cnt = column_cnt = 0
        is_ok = False

        schema_name = f"ecodi_{schema}"
        isql = (
            f"INSERT INTO ecodi_meta.mt_log_dataimp SET "
            f"user_id = '{user_id}', db_id = '{db_id}', schema_nm = '{schema_name}', "
            f"start_dt = '{start_dt}', end_dt = '{end_dt}', data_id = '{data_id}', "
            f"table_id = '{table_id.upper()}', table_nm = '{table_name}', "
            f"api_params = '{api_params}', record_cnt = {record_cnt}, "
            f"column_cnt = {column_cnt}, status = '{status}', "
            f"error_msg = '{error_msg}', cret_nm = '{user_id}';"
        )
    else:
        # ------------------------------------------------------------------
        # Branch: data present – write to the "data" schema
        # ------------------------------------------------------------------
        schema = "data"

        if not is_connected(schema):
            db_connect(schema)

        # Apply DDL (create/alter table) if necessary
        ddl_from_text(f"{schema.upper()}_CON", txt=ddl_text)

        # Record row count before insertion
        cnt_before = getquery(
            f"SELECT COUNT(*) FROM ecodi_data.{table_id}", schema
        ).iloc[0, 0]

        if table_id == "mt_kosis_stat":
            df_data['TBL_ID'] = df_data['TBL_ID'].fillna("")
            df_data['STAT_ID'] = df_data['STAT_ID'].fillna("")
            df_data['SEND_DE'] = df_data['SEND_DE'].fillna("")
            df_data['REC_TBL_SE'] = df_data['REC_TBL_SE'].fillna("")

        # Insert (append) data
        is_ok = db_settable(
            name=table_id, value=df_data, append=True, schema="data"
        )

        # Record row count after insertion
        cnt_after = getquery(
            f"SELECT COUNT(*) FROM ecodi_data.{table_id}", schema
        ).iloc[0, 0]

        end_dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = get_env("STATUS")
        error_msg = get_env("EMSG")

        record_cnt = cnt_after - cnt_before
        column_cnt = 0 if status == "0" else df_data.shape[1]

        schema_name = f"ecodi_{schema}"

        # Build the appropriate INSERT statement for the log table
        if dbms == "mysql":
            isql = (
                f"INSERT INTO ecodi_meta.mt_log_dataimp SET "
                f"user_id = '{user_id}', db_id = '{db_id}', schema_nm = '{schema_name}', "
                f"start_dt = '{start_dt}', end_dt = '{end_dt}', data_id = '{data_id}', "
                f"table_id = '{table_id.upper()}', table_nm = '{table_name}', "
                f"api_params = '{api_params}', record_cnt = {record_cnt}, "
                f"column_cnt = {column_cnt}, status = '{status}', "
                f"error_msg = '{error_msg}', cret_nm = '{user_id}';"
            )
        elif dbms == "postgresql":
            isql = (
                f"INSERT INTO ecodi_meta.mt_log_dataimp "
                f"(user_id, db_id, schema_nm, start_dt, end_dt, data_id, table_id, "
                f"table_nm, api_params, record_cnt, column_cnt, status, error_msg, cret_nm) "
                f"VALUES ('{user_id}', '{db_id}', '{schema_name}', '{start_dt}', "
                f"'{end_dt}', '{data_id}', '{table_id.upper()}', '{table_name}', "
                f"'{api_params}', {record_cnt}, {column_cnt}, '{status}', "
                f"'{error_msg}', '{user_id}');"
            )
        else:
            raise ValueError(f"Unsupported DBMS type: {dbms}")

        # Close the data‑schema connection
        db_close(schema)

    # ------------------------------------------------------------------
    # Write the log entry to the meta schema
    # ------------------------------------------------------------------
    meta_schema = "meta"
    db_connect(meta_schema)

    meta_engine = get_env(f"{meta_schema.upper()}_CON")
    with meta_engine.begin() as conn:   # ensures transaction handling
        conn.execute(text(isql))
        
    if dbms == "mysql":
        # MySQL autocommit handling – the `begin()` context already commits,
        # but we keep the explicit call for parity with the original R code.
        conn.commit()

    if verbose:
        logger.info(
            f"Imported record count: {record_cnt}, column count: {column_cnt}, status: {status}"
        )

    # Mimic R's `invisible(is_ok)` – we return the flag but callers can ignore it.
    return is_ok if 'is_ok' in locals() else None


# Exported symbols (similar to R's @export)
__all__ = [
    "from_meta_apiurl",
    "from_meta_param",
    "from_meta_apikey",
    "from_meta_datalist",
    "from_meta_pramset",
    "from_meta_result",
    "from_meta_ddl",
    "get_api_url",
    "get_api_result",
    "get_api_data",
    "set_apikey_env",
    "import_api_data"
]

