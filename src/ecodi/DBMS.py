# -*- coding: utf-8 -*-
"""
Translated from the original R source code.

Provides helper functions to create, manage and close database connections
for three schemas (meta, ods, data) supporting PostgreSQL and MySQL.
"""

import os
import base64
from typing import Optional, Union, List
import sqlalchemy
from sqlalchemy import create_engine, text, inspect, insert
from sqlalchemy import MetaData
from sqlalchemy import Table, Column, DateTime, Integer, String
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.exc import SQLAlchemyError
import random
from datetime import datetime
import pandas as pd
import numpy as np

# ----------------------------------------------------------------------
# Simple environment‑like storage (mirrors the R get_env / set_env helpers)
# ----------------------------------------------------------------------
_env: dict = {}

# ----------------------------------------------------------------------
# Helper utilities
# ----------------------------------------------------------------------
def _match_arg(value: Union[str, List[str]], valid: List[str]) -> str:
    """Emulate R's ``match.arg`` – keep the first matching element or raise."""
    if isinstance(value, list):
        value = value[0]
    if value not in valid:
        raise ValueError(f"Argument '{value}' not in allowed set {valid}")
    return value


def _build_connection_string(
    dbms: str,
    user: str,
    password: str,
    host: str,
    port: int,
    dbname: str,
    schema: str,
) -> str:
    """
    Build a SQLAlchemy connection URL.
    """
    if dbms == "postgresql":
        # PostgreSQL uses the search_path option to set the schema
        return (
            f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
            f"?options=-c%20search_path=ecodi_{schema}"
        )
    elif dbms == "mysql":
        # MySQL does not need the search_path option
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}"
    else:
        raise ValueError(f"Unsupported DBMS: {dbms}")


# ----------------------------------------------------------------------
# Core functions
# ----------------------------------------------------------------------
def db_connect(
    schema: Union[str, List[str]] = ["meta", "ods", "data"],
    host: str = "localhost",
    port: Optional[int] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    dbms: str = get_env("ecoDI_DBMS") or "postgresql",
) -> None:
    """
    Create (or replace) a database connection for the chosen *schema*.

    The function stores the engine object in ``_env`` under the key
    ``"{SCHEMA}_CON"`` and a Boolean flag under ``"{SCHEMA}_ISCONNCT"``.
    """
    # Validate arguments
    dbms = _match_arg(dbms, ["postgresql", "mysql"])
    schema = _match_arg(schema, ["meta", "ods", "data"])

    # Default database name and port per DBMS
    dbname = "ecodi"
    if dbms == "mysql":
        dbname = f"ecodi_{schema}"
        port = port or 3306
    else:  # postgresql
        port = port or 5432

    # Close an existing connection for the same schema, if any
    if is_connected(schema):
        db_close(schema)

    # Resolve missing credentials from the *_INFO* environment variable
    if user is None or password is None:
        # The INFO variable is base‑64 encoded "user:password"
        info_key = f"{schema.upper()}_INFO"
        encoded = get_env(info_key)
        if encoded is None:
            raise RuntimeError(f"Missing environment variable: {info_key}")

        decoded_bytes = base64.b64decode(encoded)
        decoded = decoded_bytes.decode()
        cred_user, cred_pass = decoded.split(":", 1)

        if user is None:
            user = cred_user
        if password is None:
            password = cred_pass

    # Build the SQLAlchemy engine
    conn_str = _build_connection_string(
        dbms=dbms,
        user=user,
        password=password,
        host=host,
        port=port,
        dbname=dbname,
        schema=schema,
    )
    engine: Engine = sqlalchemy.create_engine(conn_str)

    # Store the connection and flag
    set_env(f"{schema.upper()}_CON", engine)
    set_env(f"{schema.upper()}_ISCONNCT", True)


def meta_connect(
    host: str = "localhost",
    port: Optional[int] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    dbms: str = get_env("ecoDI_DBMS") or "postgresql",
) -> None:
    """Convenience wrapper for ``db_connect`` with the *meta* schema."""
    db_connect(
        schema="meta",
        host=host,
        port=port,
        user=user,
        password=password,
        dbms=dbms,
    )


def data_connect(
    host: str = "localhost",
    port: Optional[int] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    dbms: str = get_env("ecoDI_DBMS") or "postgresql",
) -> None:
    """Convenience wrapper for ``db_connect`` with the *data* schema."""
    db_connect(
        schema="data",
        host=host,
        port=port,
        user=user,
        password=password,
        dbms=dbms,
    )


def ods_connect(
    host: str = "localhost",
    port: Optional[int] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    dbms: str = get_env("ecoDI_DBMS") or "postgresql",
) -> None:
    """Convenience wrapper for ``db_connect`` with the *ods* schema."""
    db_connect(
        schema="ods",
        host=host,
        port=port,
        user=user,
        password=password,
        dbms=dbms,
    )


def is_connected(schema: Union[str, List[str]] = ["meta", "ods", "data"]) -> bool:
    """
    Return ``True`` if a live connection for *schema* exists, otherwise ``False``.
    """
    schema = _match_arg(schema, ["meta", "ods", "data"])
    flag = get_env(f"{schema.upper()}_ISCONNCT")
    return bool(flag)


def db_close(schema: Union[str, List[str]] = ["meta", "ods", "data"]) -> bool:
    """
    Disconnect the stored engine for *schema*.
    Returns ``True`` if a connection was closed, ``False`` otherwise.
    """
    schema = _match_arg(schema, ["meta", "ods", "data"])

    if not is_connected(schema):
        return False

    engine: Engine = get_env(f"{schema.upper()}_CON")
    if engine is not None:
        engine.dispose()

    set_env(f"{schema.upper()}_ISCONNCT", False)
    return True


def query_from_file(con, sql_file: str = None, is_ddl: bool = False):
    """
    Execute SQL statements stored in a file.

    Parameters
    ----------
    con : sqlalchemy.engine.Connection
        Live DB connection.
    sql_file : str, optional
        Path to the file that contains the SQL code.
    is_ddl : bool, default False
        If True, the file may contain multiple DDL statements that will be
        executed one‑by‑one. If False only a single statement is permitted.
    """
    if sql_file is None or not os.path.isfile(sql_file):
        raise FileNotFoundError("SQL file does not exist.")

    # read the whole file
    with open(sql_file, encoding="utf-8") as f:
        sql_query_string = f.read()

    # split on ';', strip whitespace and drop empty fragments
    sql_statements = [
        stmt.strip()
        for stmt in sql_query_string.split(";")
        if stmt.strip()
    ]

    if not sql_statements:
        raise ValueError("No valid SQL statements found in the file.")
    if len(sql_statements) > 1 and not is_ddl:
        raise ValueError(
            "Multiple SQL statements found in the file, but 'is_ddl' is FALSE. "
            "Set 'is_ddl' to TRUE to execute multiple statements."
        )

    set_env("STATUS", "1")
    set_env("EMSG", "")

    if is_ddl:
        for sql in sql_statements:
            try:
                with con.begin() as conn:
                    result = conn.execute(text(sql))
            except SQLAlchemyError as e:
                set_env("STATUS", "0")
                set_env("EMSG", str(e))
    else:
        # When not DDL we use the original whole text (allows multi‑line SELECTs)
        try:
            result = pd.read_sql_query(text(sql_query_string), con)
            return result
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error executing query: {e}")
      

def get_connection(schema: str):
    """Convenient wrapper that returns the stored connection object."""
    return get_env(f"{schema.upper()}_CON")


# ----------------------------------------------------------------------
# Core functions (direct translation from the R source)
# ----------------------------------------------------------------------
# def _match_arg(arg, choices):
#     """Emulate R's match.arg – return the first matching choice."""
#     if arg not in choices:
#         raise ValueError(f"Argument must be one of {choices}, got {arg}")
#     return arg


def getquery(sql: str,
             schema: str = "meta",
             dbms: str = None):
    """
    Execute a SELECT query and log the execution.

    Parameters
    ----------
    sql : str
        The SQL statement to run.
    schema : str, optional
        One of "meta", "ods", "data". Default is "meta".
    dbms : str, optional
        Database engine name (e.g., "mysql" or "postgresql").
        If omitted, it is read from the environment variable
        ``ecoDI_DBMS``.
    Returns
    -------
    pandas.DataFrame
        The query result (empty DataFrame on error).
    """
    # ------------------------------------------------------------------
    # Argument handling
    # ------------------------------------------------------------------
    schema = _match_arg(schema, ["meta", "ods", "data"])

    if dbms is None:
        dbms = get_env("ecoDI_DBMS")

    # ------------------------------------------------------------------
    # Ensure a live connection
    # ------------------------------------------------------------------
    if not is_connected(schema):
        db_connect(schema)

    # ------------------------------------------------------------------
    # Initialise status tracking
    # ------------------------------------------------------------------
    set_env("STATUS", "1")
    set_env("EMSG", "")

    sdt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # start datetime

    result = pd.DataFrame()  # default empty result
    try:
        conn = get_connection(schema)
        # Assuming ``conn`` follows the DBAPI2 interface (e.g., SQLAlchemy engine)
        result = pd.read_sql_query(sql, conn)
    except Exception as e:
        set_env("STATUS", "0")
        set_env("EMSG", str(e))

    edt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # end datetime

    # ------------------------------------------------------------------
    # Retrieve status / error message
    # ------------------------------------------------------------------
    status = get_env("STATUS")
    emsg = str(get_env("EMSG"))
    emsg = emsg.replace("'", r"\'")                # escape single quotes for logging

    # ------------------------------------------------------------------
    # User / DB identification
    # ------------------------------------------------------------------
    uid = get_env("USERNAME") or "unknown_user"

    # Decode the base64‑encoded DB info string
    encoded_info = get_env(f"{schema.upper()}_INFO")
    dbinfo_bytes = base64.b64decode(encoded_info) if encoded_info else b""
    dbinfo = dbinfo_bytes.decode("utf-8", errors="ignore")
    dbid = dbinfo.split(":")[0] if ":" in dbinfo else ""

    # ------------------------------------------------------------------
    # Row / column counts (0 if the query failed)
    # ------------------------------------------------------------------
    if status == "0":
        rcnt = 0
        ccnt = 0
    else:
        rcnt = result.shape[0]
        ccnt = result.shape[1]

    # ------------------------------------------------------------------
    # Prepare the logged SQL (escape single quotes, truncate)
    # ------------------------------------------------------------------
    sql_for_log = sql.replace("'", "''")[:3500]

    # ------------------------------------------------------------------
    # Random key generation (mirrors the R logic)
    # ------------------------------------------------------------------
    rnd = round(random.random() * 100_000_000)
    rnd = rnd * 10 if rnd < 100_000_000 else rnd

    schema_nm = f"ecodi_{schema}"

    # ------------------------------------------------------------------
    # Build the INSERT statement for the logging table
    # ------------------------------------------------------------------
    if dbms == "mysql":
        isql = f"""
        INSERT INTO ecodi_meta.mt_log_manage 
        SET user_id = '{uid}', db_id = '{dbid}', 
            schema_nm = '{schema_nm}', start_dt = '{sdt}', 
            rand_key = {rnd}, end_dt = '{edt}', 
            record_cnt = {rcnt}, column_cnt = {ccnt}, 
            sql_stmt = '{sql_for_log}', status = '{status}', 
            error_msg = '{emsg}', cret_nm = '{uid}';
        """
    elif dbms == "postgresql":
        isql = f"""
        INSERT INTO ecodi_meta.mt_log_manage 
        (user_id, db_id, schema_nm, start_dt, rand_key, end_dt, 
         record_cnt, column_cnt, sql_stmt, status, 
         error_msg, cret_nm)
        VALUES ('{uid}', '{dbid}', '{schema_nm}', '{sdt}', {rnd},
                '{edt}', {rcnt}, {ccnt}, '{sql_for_log}', '{status}', 
                '{emsg}', '{uid}');
        """
    else:
        raise ValueError(f"Unsupported DBMS: {dbms}")

    # ------------------------------------------------------------------
    # Log the execution in the *meta* schema
    # ------------------------------------------------------------------
    db_close(schema)                      # close the original schema connection
    meta_schema = "meta"
    db_connect(meta_schema)               # open a connection to the meta schema

    meta_conn = get_connection(meta_schema)

    # 메타데이터 객체 선언
    metadata_obj = MetaData()

    # 테이블 객체 선언
    log_manage_table = Table(
        "mt_log_manage",
        metadata_obj,
        Column("user_id", String(20), primary_key=True),
        Column("db_id", String(20), primary_key=True),
        Column("schema_nm", String(20), primary_key=True),
        Column("start_dt", DateTime, primary_key=True),
        Column("rand_key", Integer, primary_key=True),
        Column("end_dt", DateTime),
        Column("record_cnt", Integer),
        Column("column_cnt", Integer),
        Column("sql_stmt", String(4000)),
        Column("status", String(20)),
        Column("error_msg", String(1000)),
        Column("cret_nm", String(20))
    )

    # INSERT문 생성
    stmt = insert(log_manage_table).values(user_id=uid, db_id=dbid, 
                  schema_nm=schema_nm, start_dt=sdt, rand_key=rnd, end_dt=edt, 
                  record_cnt=rcnt, column_cnt=ccnt, sql_stmt=sql_for_log,
                  status=status, error_msg=emsg, cret_nm=uid)

    with meta_conn.connect() as conn:
        conn.execute(stmt)
        conn.commit()
        
    return result


def deletequery(table_nm: str,
                schema: str = "meta",
                **params):
    """
    Delete rows from *table_nm* with optional WHERE clauses.

    Parameters
    ----------
    table_nm : str
        Name of the table to delete from.
    schema : str, optional
        One of "meta", "ods", "data". Default is "meta".
    **params
        Column‑value pairs that are added as ``AND col = 'value'`` filters.
    Returns
    -------
    int
        Number of rows affected (as reported by the DB driver).
    """
    schema = _match_arg(schema, ["meta", "ods", "data"])

    if not is_connected(schema):
        db_connect(schema)

    set_env("STATUS", "1")
    set_env("EMSG", "")

    # Base DELETE statement
    sql = f"DELETE FROM {table_nm} WHERE 1=1 "

    # Append additional filters
    for param_name, param_value in params.items():
        sql += f" AND {param_name} = '{param_value}' "
    
    conn_schema = get_connection(schema)
    
    try:
        conn_schema = get_connection(schema)
        with conn_schema.begin() as conn:   # ensures transaction handling
            result = conn.execute(text(sql))
        rows_affected = result.rowcount    
    except Exception as e:
        set_env("STATUS", "0")
        set_env("EMSG", str(e))
        rows_affected = 0

    return rows_affected


def is_tabled(name: str,
              schema: str = "meta"):
    """
    Check whether a table with *name* exists in the given *schema*.

    Parameters
    ----------
    name : str
        Table name to look for.
    schema : str, optional
        One of "meta", "ods", "data". Default is "meta".
    Returns
    -------
    bool
        ``True`` if the table exists, otherwise ``False``.
    """
    schema = _match_arg(schema, ["meta", "ods", "data"])

    if not is_connected(schema):
        db_connect(schema)

    conn = get_connection(schema)
    tables = inspect(conn).get_table_names()    # adapt to your DB‑API / SQLAlchemy version
    return name in tables


# ----------------------------------------------------------------------
# Main function translated from R
# ----------------------------------------------------------------------
def db_settable(
    name: str,
    value: pd.DataFrame,
    row_names: bool = False,
    overwrite: bool = False,
    append: bool = False,
    schema: str = "meta",
    is_postfix: bool = True,
    dbms: str = get_env("ecoDI_DBMS")
) -> pd.DataFrame | None:
    """
    Write a pandas DataFrame to a database table, log the operation and
    return the result of the write (or None on failure).
    """
    # ------------------------------------------------------------------
    # Validate schema argument (matches R's match.arg)
    # ------------------------------------------------------------------
    allowed_schemas = {"meta", "ods", "data"}
    if schema not in allowed_schemas:
        raise ValueError(f"schema must be one of {allowed_schemas}")

    # ------------------------------------------------------------------
    # Ensure DB connection is live
    # ------------------------------------------------------------------
    if not is_connected(schema):
        db_connect(schema)

    # ------------------------------------------------------------------
    # Initialise status flags in the environment
    # ------------------------------------------------------------------
    set_env("STATUS", "1")
    set_env("EMSG", "")

    # Record start timestamp (format: YYYY-MM-DD HH:MM:SS)
    start_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ------------------------------------------------------------------
    # Post‑fix handling (adds creation/modification metadata columns)
    # ------------------------------------------------------------------
    if is_postfix:
        # Drop possible existing metadata columns
        cols_to_drop = {"cret_dt", "cret_nm"}
        value = value.drop(columns=[c for c in value.columns if c in cols_to_drop], errors="ignore")
        # Append new metadata columns
        value = value.assign(
            cret_dt=datetime.now(),
            cret_nm="ecoDI",
            mdfy_dt=pd.NA,
            mdfy_nm=pd.NA,
        )

    # ------------------------------------------------------------------
    # Normalise identifiers for PostgreSQL (lower‑case)
    # ------------------------------------------------------------------
    if dbms == "postgresql":
        name = name.lower()
        value.columns = [col.lower() for col in value.columns]

    # ------------------------------------------------------------------
    # Write the DataFrame to the database table
    # ------------------------------------------------------------------
    try:
        engine = get_env(f"{schema.upper()}_CON")
        if_append = "append" if append else "replace" if overwrite else "fail"
        # pandas uses `if_exists` values: 'fail', 'replace', 'append'
        value.to_sql(
            name=name,
            con=engine,
            if_exists=if_append,
            index=row_names,
            method="multi"   # improve performance for bulk inserts
        )
        result = None  # pandas `to_sql` does not return a useful value
    except Exception as e:
        # Capture error information in the environment
        set_env("STATUS", "0")
        set_env("EMSG", str(e))
        result = None

    # ------------------------------------------------------------------
    # Record end timestamp
    # ------------------------------------------------------------------
    end_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ------------------------------------------------------------------
    # Build logging information
    # ------------------------------------------------------------------
    status = get_env("STATUS")
    emsg = str(get_env("EMSG")).replace("'", r"\'")

    uid = get_env("USERNAME") or "unknown_user"

    # Decode DB info (expects base64 string like "dbid:otherinfo")
    encoded_info = get_env(f"{schema.upper()}_INFO")
    dbinfo = ""
    if encoded_info:
        decoded_bytes = base64.b64decode(encoded_info)
        dbinfo = decoded_bytes.decode()
    dbid = dbinfo.split(":")[0] if dbinfo else "unknown_db"

    rcnt = 0 if status == "0" else len(value)
    ccnt = 0 if status == "0" else value.shape[1]

    sql_stmt = f"insert into {name}" if append else f"create table {name}"

    # Generate a random key (mimics R's runif logic)
    rnd = int(random.random() * 100_000_000)
    rnd = rnd * 10 if rnd < 100_000_000 else rnd

    schema_nm = f"ecodi_{schema}"

    # ------------------------------------------------------------------
    # Compose the INSERT statement for the logging table (ecodi_meta.mt_log_manage)
    # ------------------------------------------------------------------
    if dbms == "mysql":
        isql = f"""
        INSERT INTO ecodi_meta.mt_log_manage 
        SET user_id = '{uid}', db_id = '{dbid}', 
            schema_nm = '{schema_nm}', start_dt = '{start_dt}', 
            rand_key = {rnd}, end_dt = '{end_dt}', 
            record_cnt = {rcnt},
            column_cnt = {ccnt}, sql_stmt = '{sql_stmt}', 
            status = '{status}', 
            error_msg = '{emsg}', cret_nm = '{uid}';
        """
    elif dbms == "postgresql":
        isql = f"""
        INSERT INTO ecodi_meta.mt_log_manage 
        (user_id, db_id, schema_nm, start_dt, rand_key, end_dt, 
         record_cnt, column_cnt, sql_stmt, status, 
         error_msg, cret_nm)
        VALUES ('{uid}', '{dbid}', '{schema_nm}', '{start_dt}', {rnd},
                '{end_dt}', {rcnt}, {ccnt}, '{sql_stmt}', '{status}', 
                '{emsg}', '{uid}');
        """
    else:
        raise ValueError(f"Unsupported DBMS '{dbms}'")

    # ------------------------------------------------------------------
    # Log the operation
    # ------------------------------------------------------------------
    db_close(schema)               # close the original schema connection

    # Re‑connect to the META schema to write the log entry
    meta_schema = "meta"
    if not is_connected(meta_schema):
        db_connect(meta_schema)

    meta_engine = get_env(f"{meta_schema.upper()}_CON")
    with meta_engine.begin() as conn:   # ensures transaction handling
        conn.execute(text(isql))

    if dbms == "mysql":
        # MySQL autocommit handling – the `begin()` context already commits,
        # but we keep the explicit call for parity with the original R code.
        conn.commit()

    return result


def ddl_from_text(con, txt: str = None, verbose: bool = False):
    """
    Execute DDL statements supplied as a plain text string.

    Parameters
    ----------
    con : sqlalchemy.engine.Connection
        Live DB connection.
    txt : str, optional
        DDL statements separated by ';'.
    verbose : bool, default False
        If True, print error messages for each failing statement.
    """
    if txt is None:
        raise ValueError("DDL text does not exist.")

    sql_statements = [
        stmt.strip()
        for stmt in txt.split(";")
        if stmt.strip()
    ]

    for sql in sql_statements:
        try:
            con.execute(text(sql))
        except SQLAlchemyError as e:
            if verbose:
                print(f"Error executing SQL: {sql}")
            set_env("STATUS", "0")
            set_env("EMSG", str(e))


def db_load_csv(name: str,
                file_name: str = None,
                row_names: bool = False,
                overwrite: bool = False,
                append: bool = False,
                schema: str = "meta",
                is_postfix: bool = True,
                dbms: str = None):
    """
    Load a CSV file into a database table.

    Parameters
    ----------
    name : str
        Target table name.
    file_name : str, optional
        Path to the CSV file.
    row_names : bool, default False
        If True, include the CSV index as a column.
    overwrite : bool, default False
        Drop the existing table before writing (if True).
    append : bool, default False
        Append to an existing table (if True).
    schema : {'meta', 'ods', 'data'}, default 'meta'
        Database schema to use.
    is_postfix : bool, default True
        Whether to add audit columns (creation / modification info).
    dbms : str, optional
        Database management system identifier (e.g., 'mysql').
    """
    schema = schema.lower()
    if schema not in ("meta", "ods", "data"):
        raise ValueError("Invalid schema; must be one of 'meta', 'ods', or 'data'.")

    if file_name is None or not os.path.isfile(file_name):
        raise FileNotFoundError("CSV file does not exist.")

    # ------------------------------------------------------------------
    # Load CSV
    # ------------------------------------------------------------------
    df = pd.read_csv(file_name, dtype=str)          # force strings like R's read.csv
    if not row_names:
        df.reset_index(drop=True, inplace=True)

    # ------------------------------------------------------------------
    # Optional audit columns
    # ------------------------------------------------------------------
    if is_postfix:
        now = datetime.now()
        df["cret_dt"] = now
        df["cret_nm"] = "ecoDI"
        df["mdfy_dt"] = pd.NA
        df["mdfy_nm"] = pd.NA

    # ------------------------------------------------------------------
    # Validate DB connection
    # ------------------------------------------------------------------
    if not is_connected(schema):
        raise RuntimeError("DB not connected !!!")

    # environment flags used by the original script
    set_env("STATUS", "1")
    set_env("EMSG", "")

    start_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ------------------------------------------------------------------
    # Write to DB
    # ------------------------------------------------------------------
    conn = get_env(f"{schema.upper()}_CON")   # expects a SQLAlchemy engine/connection
    if conn is None:
        raise RuntimeError(f"Connection for schema {schema} not found in env.")

    result = None
    dbms = get_env("ecoDI_DBMS")
    
    try:
        db_settable(
            name = table_name,
            value = df,
            row_names = row_names,
            overwrite = overwrite,
            append = append,
            schema = schema,
            is_postfix = is_postfix, 
            dbms = dbms)
    except Exception as e:   
        set_env("STATUS", "0")
        set_env("EMSG", str(e))
        result = False
        
    end_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ------------------------------------------------------------------
    # Build log entry (mirrors the R implementation)
    # ------------------------------------------------------------------
    status = get_env("STATUS")
    emsg = get_env("EMSG")
    emsg = emsg.replace("'", r"\'")   # escape single quotes for SQL

    uid = get_env("USERNAME")
    dbinfo_b64 = get_env(f"{schema.upper()}_INFO")
    dbinfo = base64.b64decode(dbinfo_b64).decode() if dbinfo_b64 else ""
    dbid = dbinfo.split(":")[0] if ":" in dbinfo else ""

    rcnt = 0 if status == "0" else len(df)
    ccnt = 0 if status == "0" else len(df.columns)

    sql_placeholder = f"Insert table {name}" if append else f"Create table {name}"
    rnd = np.random.randint(0, 100_000_000)
    rnd = rnd * 10 if rnd < 100_000_000 else rnd

    schema_nm = f"ecodi_{schema}"

    log_sql = f"""
        INSERT INTO ecodi_meta.mt_log_manage
        (user_id, db_id, schema_nm, start_dt, rand_key, end_dt,
         record_cnt, column_cnt, sql_stmt, status, error_msg, cret_nm)
        VALUES ('{uid}', '{dbid}', '{schema_nm}', '{start_dt}', {rnd},
                '{end_dt}', {rcnt}, {ccnt}, '{sql_placeholder}',
                '{status}', '{emsg}', '{uid}');
    """

    # ------------------------------------------------------------------
    # Commit the log
    # ------------------------------------------------------------------
    db_close(schema)

    # ensure we are connected to the meta schema for logging
    db_connect("meta")
    meta_conn = get_env("META_CON")
    if meta_conn is None:
        raise RuntimeError("Meta connection not found in environment.")
        
    try:
        with meta_conn.begin() as conn:   # ensures transaction handling
            conn.execute(text(log_sql))
        if dbms == "mysql":
            meta_conn.commit()
    except SQLAlchemyError as e:
        # Even if logging fails, we don't want to raise – original code ignores it.
        pass

    return result

  
  
# Exported symbols (similar to R's @export)
__all__ = [
    "_match_arg",
    "_build_connection_string",
    "db_connect",
    "meta_connect",
    "ods_connect",
    "data_connect",
    "is_connected",
    "db_close",
    "query_from_file",
    "get_connection",
    "getquery",
    "deletequery",
    "is_tabled",
    "db_settable",
    "db_load_csv",
]

  
