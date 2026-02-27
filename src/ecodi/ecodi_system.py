import pandas as pd
import os

from ecodi.dbms import (
    db_connect,
    is_connected,
    getquery
)

from ecodi.env import (
    get_env
)


def get_log_manage(
    schema: str = "all",
    user: str | None = None,
    desc: bool = True,
    limit: int = 500,
):
    """
    Retrieve rows from ecodi_meta.mt_log_manage with optional filtering.
    """
    allowed_schemas = {"all", "meta", "ods", "data"}
    if schema not in allowed_schemas:
        raise ValueError(f"schema must be one of {allowed_schemas}")

    # Ensure a connection to the meta database
    if not is_connected("meta"):
        db_connect("meta")

    sql = "SELECT * FROM ecodi_meta.mt_log_manage WHERE 1=1 "

    if user is not None:
        sql += f" AND user_id = '{user}' "

    if schema != "all":
        sql += f" AND schema_nm = 'ecodi_{schema}'"

    sql += " ORDER BY start_dt DESC " if desc else " ORDER BY start_dt ASC "
    sql += f" LIMIT {limit} "

    return getquery(sql, schema="meta")


def get_log_import(
    schema: str = "all",
    user: str | None = None,
    desc: bool = True,
    limit: int = 500,
):
    """
    Retrieve rows from ecodi_meta.mt_log_dataimp with optional filtering.
    """
    allowed_schemas = {"all", "meta", "ods", "data"}
    if schema not in allowed_schemas:
        raise ValueError(f"schema must be one of {allowed_schemas}")

    if not is_connected("meta"):
        db_connect("meta")

    sql = "SELECT * FROM ecodi_meta.mt_log_dataimp WHERE 1=1 "

    if user is not None:
        sql += f" AND user_id = '{user}' "

    if schema != "all":
        sql += f" AND schema_nm = 'ecodi_{schema}'"

    sql += " ORDER BY start_dt DESC " if desc else " ORDER BY start_dt ASC "
    sql += f" LIMIT {limit} "

    return getquery(sql, schema="meta")


def get_table_list(
    schema: str = "all",
    dbms: str | None = None
) -> pd.DataFrame:
    """
    Retrieve a list of tables (and some metadata) from the EcoDI database.

    Parameters
    ----------
    schema : str, optional
        One of ``["all", "meta", "ods", "data"]``.  ``"all"`` retrieves every
        matching schema, otherwise a single ``ecodi_<schema>`` schema is used.
    dbms : str, optional
        Database management system – either ``"mysql"`` or ``"postgresql"``.
        If omitted, the value is taken from the ``ecoDI_DBMS`` environment
        variable.

    Returns
    -------
    pandas.DataFrame
        Query result containing ``table_schema``, ``table_name``,
        ``table_comment``, ``table_rows`` and ``table_cols``.
    """
    # ------------------------------------------------------------------
    # Validate arguments
    # ------------------------------------------------------------------
    allowed_schemas = ["all", "meta", "ods", "data"]
    if schema not in allowed_schemas:
        raise ValueError(f"`schema` must be one of {allowed_schemas}")

    if dbms is None:
        dbms = get_env("ecoDI_DBMS")
    if dbms not in {"mysql", "postgresql"}:
        raise ValueError("`dbms` must be either 'mysql' or 'postgresql'")

    # ------------------------------------------------------------------
    # Build the appropriate SQL statement
    # ------------------------------------------------------------------
    if schema == "all":
        if dbms == "mysql":
            sql = """
                SELECT tabs.TABLE_SCHEMA   AS table_schema,
                       tabs.TABLE_NAME    AS table_name,
                       tabs.table_comment AS table_comment,
                       tabs.table_rows    AS table_rows,
                       COUNT(cols.COLUMN_NAME) AS table_cols
                  FROM INFORMATION_SCHEMA.TABLES tabs
                  LEFT JOIN INFORMATION_SCHEMA.COLUMNS cols
                    ON tabs.TABLE_NAME = cols.TABLE_NAME
                 WHERE tabs.TABLE_SCHEMA LIKE 'ecodi%%'
                 GROUP BY tabs.TABLE_SCHEMA,
                          tabs.TABLE_NAME,
                          tabs.table_rows,
                          tabs.table_comment;
            """
        else:   # postgresql
            sql = """
                SELECT it.table_schema               AS table_schema,
                       it.table_name                 AS table_name,
                       obj_description(pc.oid, 'pg_class') AS table_comment,
                       pc.reltuples                  AS table_rows,
                       COUNT(ic.column_name)        AS table_cols
                  FROM information_schema.tables it
                  LEFT JOIN pg_catalog.pg_class pc
                    ON it.table_name = pc.relname
                  LEFT JOIN information_schema.columns ic
                    ON ic.table_schema = it.table_schema
                   AND ic.table_name   = it.table_name
                 WHERE it.table_schema LIKE 'ecodi%%'
                 GROUP BY it.table_schema,
                          it.table_name,
                          table_comment,
                          table_rows;
            """
    else:   # specific schema
        if dbms == "mysql":
            sql = f"""
                SELECT tabs.TABLE_SCHEMA   AS table_schema,
                       tabs.TABLE_NAME    AS table_name,
                       tabs.table_comment AS table_comment,
                       tabs.table_rows    AS table_rows,
                       COUNT(cols.COLUMN_NAME) AS table_cols
                  FROM INFORMATION_SCHEMA.TABLES tabs
                  LEFT JOIN INFORMATION_SCHEMA.COLUMNS cols
                    ON tabs.TABLE_NAME = cols.TABLE_NAME
                 WHERE tabs.TABLE_SCHEMA = 'ecodi_{schema}'
                 GROUP BY tabs.TABLE_NAME,
                          tabs.table_rows,
                          tabs.table_comment;
            """
        else:   # postgresql
            sql = f"""
                SELECT it.table_schema               AS table_schema,
                       it.table_name                 AS table_name,
                       obj_description(pc.oid, 'pg_class') AS table_comment,
                       pc.reltuples                  AS table_rows,
                       COUNT(ic.column_name)        AS table_cols
                  FROM information_schema.tables it
                  LEFT JOIN pg_catalog.pg_class pc
                    ON it.table_name = pc.relname
                  LEFT JOIN information_schema.columns ic
                    ON ic.table_schema = it.table_schema
                   AND ic.table_name   = it.table_name
                 WHERE it.table_schema LIKE 'ecodi_{schema}'
                 GROUP BY it.table_schema,
                          it.table_name,
                          table_comment,
                          table_rows;
            """

    # ------------------------------------------------------------------
    # Ensure a connection to the "meta" schema is available
    # ------------------------------------------------------------------
    if not is_connected("meta"):
        db_connect("meta")

    # ------------------------------------------------------------------
    # Execute the query and return the result
    # ------------------------------------------------------------------
    result = getquery(sql, schema = "meta")
    return result


def get_column_list(
    table_nm: str | None = None,
    schema: str = "meta",
    dbms: str | None = None,
) -> list[dict]:
    """
    Retrieve column metadata for a given table from either MySQL or PostgreSQL
    ``information_schema`` and return the result as a list of dictionaries.

    Parameters
    ----------
    table_nm : str
        Name of the table whose columns are to be inspected. Required.
    schema : str, default "meta"
        One of ``"meta"``, ``"ods"``, ``"data"`` indicating the logical schema.
    dbms : str, optional
        Database management system identifier. If omitted, it is taken from the
        environment variable ``ecoDI_DBMS``.

    Returns
    -------
    list[dict]
        Query result rows where each dict represents a column description.
    """
    # ----------------------------------------------------------------------
    # Validate arguments
    # ----------------------------------------------------------------------
    allowed_schemas = ("meta", "ods", "data")
    if schema not in allowed_schemas:
        raise ValueError(f"schema must be one of {allowed_schemas}, got '{schema}'")

    if table_nm is None:
        raise ValueError("table_nm parameter is required.")

    if dbms is None:
        dbms = get_env("ecoDI_DBMS")
        if dbms is None:
            raise EnvironmentError("ecoDI_DBMS environment variable is not set.")

    # ----------------------------------------------------------------------
    # Build the appropriate SQL statement
    # ----------------------------------------------------------------------
    if dbms == "mysql":
        sql = f"""
            SELECT TABLE_NAME,
                   ORDINAL_POSITION,
                   COLUMN_NAME,
                   COLUMN_COMMENT,
                   COLUMN_TYPE,
                   IS_NULLABLE,
                   COLUMN_KEY
              FROM INFORMATION_SCHEMA.COLUMNS
             WHERE TABLE_NAME = '{table_nm}'
               AND TABLE_SCHEMA = 'ecodi_{schema}'
             ORDER BY ORDINAL_POSITION;
        """
    elif dbms == "postgresql":
        sql = f"""
            SELECT ic.table_name AS table_name,
                   ic.ordinal_position AS ordinal_position,
                   ic.column_name AS column_name,
                   cmt.column_comment AS column_comment,
                   CASE WHEN ic.character_maximum_length IS NOT NULL
                        THEN CONCAT(ic.udt_name, '(', ic.character_maximum_length, ')')
                        ELSE ic.udt_name
                   END AS column_type,
                   ic.is_nullable AS is_nullable,
                   ic.character_maximum_length,
                   MAX(CASE WHEN ik.column_name IS NOT NULL THEN 'PRI'
                            ELSE NULL
                       END) AS column_key
              FROM information_schema.columns AS ic
              LEFT JOIN information_schema.table_constraints AS it
                     ON ic.table_schema = it.table_schema
              LEFT JOIN information_schema.key_column_usage AS ik
                     ON it.table_schema = ik.table_schema
                    AND it.constraint_name = ik.constraint_name
                    AND ic.column_name = ik.column_name
              INNER JOIN (
                  SELECT ps.relname AS table_name,
                         pa.attname AS column_name,
                         pd.description AS column_comment
                    FROM pg_stat_all_tables ps,
                         pg_description pd,
                         pg_attribute pa
                   WHERE pd.objsubid <> 0
                     AND ps.relid = pd.objoid
                     AND pd.objoid = pa.attrelid
                     AND pd.objsubid = pa.attnum
                     AND ps.schemaname = 'ecodi_{schema}'
                     AND ps.relname = '{table_nm}'
              ) AS cmt
                     ON ic.table_name = cmt.table_name
                    AND ic.column_name = cmt.column_name
             WHERE ic.table_schema = 'ecodi_{schema}'
               AND ic.table_name = '{table_nm}'
               AND it.constraint_type = 'PRIMARY KEY'
             GROUP BY ic.table_name,
                      ic.ordinal_position,
                      ic.column_name,
                      cmt.column_comment,
                      ic.udt_name,
                      ic.is_nullable,
                      ic.character_maximum_length;
        """
    else:
        raise ValueError(f"Unsupported dbms '{dbms}'. Expected 'mysql' or 'postgresql'.")

    # ----------------------------------------------------------------------
    # Ensure a connection to the meta database exists
    # ----------------------------------------------------------------------
    if not is_connected("meta"):
        db_connect("meta")

    # ----------------------------------------------------------------------
    # Execute the query and return the result
    # ----------------------------------------------------------------------
    result = getquery(sql, schema="meta")
    return result
  

# Exported symbols (similar to R's @export)
__all__ = [
    "get_log_manage",
    "get_log_import",
    "get_table_list",
    "get_column_list",
]

