import os
import subprocess
import base64
import importlib.resources
from pathlib import Path
from typing import Any, Dict, Optional

# Global environment dictionary that mimics the R .ecoDIEnv
_ecodi_env: Dict[str, Any] = {}


def get_sysenv(var_name: str) -> Optional[str]:
    """
    Retrieve a system environment variable.
    Returns ``None`` if the variable is missing, empty, or ``NA``‑like.
    """
    raw_value = os.getenv(var_name)
    if raw_value is not None and raw_value != "":
        return str(raw_value)
    return None


def set_env(name: str, value: Any, env: Dict[str, Any] = _ecodi_env) -> None:
    """
    Store *value* under *name* in the given environment dictionary.
    """
    env[name] = value


def unset_env(name: str, env: Dict[str, Any] = _ecodi_env) -> None:
    """
    Remove *name* from the given environment dictionary if it exists.
    """
    if name in env:
        del env[name]


def get_env(name: Optional[str] = None, env: Dict[str, Any] = _ecodi_env) -> Any:
    """
    Retrieve a value from the environment.
    - If *name* is omitted, the whole environment dictionary is returned.
    - Otherwise the value associated with *name* (or ``None`` if absent) is returned.
    """
    if name is None:
        # Return a shallow copy to avoid accidental external mutation
        return env.copy()
      
    if name not in env:
        return False  
      
    return env[name]


def ecoDI_env() -> None:
    """
    Display basic information about the current ecoDI environment.
    Uses simple ``print`` statements; replace with a logging library if desired.
    """
    user_name = get_env("USERNAME")
    if user_name:
        print(f"user name: {user_name}")
        dbms = get_env("ecoDI_DBMS")
        if dbms:
            print(f"DBMS: {dbms}")


def init_env() -> None:
    """
    Initialise the ecoDI environment with default values.
    - USERNAME is taken from the result of ``whoami``.
    - META_INFO, ODS_INFO, and DATA_INFO are read from ``~/.ecoDI_dbinfo``.
    - ecoDI_DBMS is set to ``postgresql``.
    - ``show.error.messages`` behaviour is mimicked by raising exceptions normally.
    """
    # Set the user name
    try:
        username = subprocess.check_output(["whoami"], text=True).strip()
    except subprocess.CalledProcessError:
        username = None
    set_env("USERNAME", username)

    # Load the three lines from the dbinfo file
    dbinfo_path = Path.home() / ".ecoDI_dbinfo"
    if dbinfo_path.is_file():
        lines = dbinfo_path.read_text().splitlines()
        if len(lines) >= 3:
            set_env("META_INFO", lines[0].strip())
            set_env("ODS_INFO", lines[1].strip())
            set_env("DATA_INFO", lines[2].strip())

    # Set the DBMS
    set_env("ecoDI_DBMS", "postgresql")

    # In R the option `show.error.messages = TRUE` makes errors visible.
    # Python already shows traceback for uncaught exceptions, so no extra step is needed.


def encode_base64(text: str) -> str:
    """
    Encode a string to base‑64.
    """
    raw_bytes = text.encode("utf-8")
    encoded_bytes = base64.b64encode(raw_bytes)
    return encoded_bytes.decode("utf-8")


def decode_base64(b64_string: str) -> str:
    """
    Decode a base‑64 string back to plain text.
    """
    raw_bytes = base64.b64decode(b64_string)
    return raw_bytes.decode("utf-8")


# Assume the following helpers are defined in the ecoDI package
# get_env, is_connected, db_connect, query_from_file, db_load_csv, cli_alert_info, system_file

def initial_meta(dbms: str = None) -> None:
    """
    Create tables and load meta data for the specified DBMS.

    Parameters
    ----------
    dbms : str, optional
        Identifier of the DBMS to use. If not provided, the value is taken from the
        environment variable ``ecoDI_DBMS`` via ``get_env``.
    """
    # Resolve default DBMS value
    if dbms is None:
        dbms = get_env("ecoDI_DBMS")

    # Ensure a connection to the meta schema exists
    if not is_connected("meta"):
        db_connect("meta")

    # Paths inside the installed ecoDI package
    ddl_path = importlib.resources.files(f'ecodi.dbms.ddl.{dbms}')
    meta_path = importlib.resources.files('ecodi.dbms.meta')

    # --------------------------------------------------
    # 1) Create tables from DDL files
    # --------------------------------------------------
    for ddl_file in Path(str(ddl_path._paths[0])).glob("*.sql"):
        print(f"Creating table from {ddl_file}")
        query_from_file(
            get_env("META_CON"),
            sql_file=str(ddl_file),
            is_ddl=True
        )

    # --------------------------------------------------
    # 2) Load CSV meta‑data files
    # --------------------------------------------------
    for csv_file in Path(str(meta_path._paths[0])).glob("*.csv"):
        print(f"Loading meta data from {csv_file}")

        # Derive table name from the CSV file name (remove extension)
        table_name = csv_file.stem

        db_load_csv(
            name=table_name,
            file_name=str(csv_file),
            row_names=False,
            overwrite=False,
            append=True,
            schema="meta",
            is_postfix=True
        )
        
        
# Exported symbols (similar to R's @export)
__all__ = [
    "get_sysenv",
    "set_env",
    "unset_env",
    "get_env",
    "ecoDI_env",
    "init_env",
    "encode_base64",
    "decode_base64",
    "initial_meta",
]
