import os
import base64
from typing import Optional, Any, List, Dict
import pandas as pd
import requests
from urllib.parse import urlencode


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


def from_meta_datalist(data_id: Optional[str] = None) -> List[Dict[str, Any]]:
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

    # The R code always loads a specific data list row; replicate the same logic
    data_list = from_meta_datalist(data_id="DA0001")
    if data_list:
        table_id = data_list[0].get("table_id")
        # `table_id` is retrieved but not used further in the original R code.
        # Keep it here in case future logic needs it.
        _ = table_id

    if api_url_id is None:
        sql = "SELECT * FROM mt_api_result"
    else:
        sql = f"SELECT * FROM mt_api_result WHERE api_url_id = '{api_url_id}'"

    return getquery(sql)
  

def from_meta_ddl(
    data_id=None,
    is_postfix=True,
    schema="data",
    dbms=get_env("ecoDI_DBMS")
):
    if data_id is None:
        raise ValueError("'data_id' must be provided.")

    if not is_connected("meta"):
        db_connect("meta")

    if schema not in ("data", "ods", "meta"):
        raise ValueError("schema must be one of ('data', 'ods', 'meta')")

    # 메타 정보 조회
    data_info = from_meta_datalist(data_id=data_id)
    table_id = data_info["raw_table_id"].lower()
    table_nm = data_info["data_nm"]
    api_url_id = data_info["api_url_id"]

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


def get_api_result(data_id=None, **kwargs):
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

