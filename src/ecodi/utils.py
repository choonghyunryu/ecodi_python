import os
import platform
import base64
import pathlib
import tempfile
import datetime
import pandas as pd
from typing import List, Optional, Union

def regist_apikey(key_name: str | None = None,
                  key_value: str | None = None,
                  overwrite: bool = False) -> None:
    """
    Register an API key as an environment variable.

    Parameters
    ----------
    key_name : str, optional
        Name of the environment variable.
    key_value : str, optional
        Value to assign to the environment variable.
    overwrite : bool, default False
        If ``True`` replace an existing variable with the same name.

    Raises
    ------
    ValueError
        If ``key_name`` or ``key_value`` is not supplied, or if the
        variable already exists and ``overwrite`` is ``False``.
    """
    if key_name is None or key_value is None:
        raise ValueError("Both 'key_name' and 'key_value' must be provided.")

    if key_name in os.environ and not overwrite:
        raise ValueError(
            f"An API key with the name {key_name} already exists. "
            "Use 'overwrite=True' to replace it."
        )

    # Register the environment variable
    os.environ[key_name] = key_value
    print(f"API key {key_name} registered successfully.")


def unregist_apikey(key_name: str | None = None) -> None:
    """
    Unregister (remove) an API key from the environment variables.

    Parameters
    ----------
    key_name : str, optional
        Name of the environment variable to remove.

    Raises
    ------
    ValueError
        If ``key_name`` is not supplied.
    """
    if key_name is None:
        raise ValueError("'key_name' must be provided.")

    # Remove the environment variable if it exists; ignore otherwise
    os.environ.pop(key_name, None)
    print(f"API key {key_name} unregistered successfully.")


def write_apikey(
    key_name: Optional[str] = None,
    key_value: Optional[str] = None,
    overwrite: bool = False,
    file_path: str = "~/.ecoDI_apikeys"
) -> None:
    """
    Store an API key in a simple ``key=base64(value)`` text file.

    Parameters
    ----------
    key_name : str, optional
        Identifier for the key (required).
    key_value : str, optional
        The plain‑text API key to store (required).
    overwrite : bool, default False
        If ``True`` and the key already exists, replace its value.
    file_path : str, default ``~/.ecoDI_apikeys``
        Location of the key file.

    Raises
    ------
    ValueError
        If ``key_name`` or ``key_value`` is missing, or if the key already exists
        and ``overwrite`` is ``False``.
    """
    if key_name is None or key_value is None:
        raise ValueError("Both 'key_name' and 'key_value' must be provided.")

    # Expand ``~`` to the user home directory
    path = pathlib.Path(os.path.expanduser(file_path))

    # Gather existing keys if the file is present
    existing_keys = []
    if path.is_file():
        with path.open("r", encoding="utf-8") as fh:
            lines = [ln.rstrip("\n") for ln in fh.readlines()]
        existing_keys = [ln.split("=", 1)[0] for ln in lines if "=" in ln]

    # -----------------------------------------------------------------
    # Case 1 – file exists, key already present, no overwrite requested
    # -----------------------------------------------------------------
    if path.is_file() and not overwrite:
        if key_name in existing_keys:
            raise ValueError(
                f"Key already exists in the file {file_path}. "
                "Use 'overwrite=True' to replace it."
            )
        # Append the new key
        with path.open("a", encoding="utf-8") as fh:
            fh.write(f"{key_name}={encode_base64(key_value)}\n")
        print(f"API key appended to {file_path} successfully.")
        return

    # -----------------------------------------------------------------
    # Case 2 – file exists and overwrite is requested
    # -----------------------------------------------------------------
    if path.is_file() and overwrite:
        if key_name in existing_keys:
            # Rewrite the file, replacing the matching line
            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, encoding="utf-8"
            ) as tmp:
                for line in lines:
                    current_name = line.split("=", 1)[0]
                    if current_name == key_name:
                        tmp.write(f"{key_name}={encode_base64(key_value)}\n")
                    else:
                        tmp.write(f"{line}\n")
            os.replace(tmp.name, path)
            print(f"API key overwritten in {file_path} successfully.")
            return
        # If the key does not exist, fall through to append logic
        with path.open("a", encoding="utf-8") as fh:
            fh.write(f"{key_name}={encode_base64(key_value)}\n")
        print(f"API key appended to {file_path} successfully.")
        return

    # -----------------------------------------------------------------
    # Case 3 – file does not exist; create it with the new key
    # -----------------------------------------------------------------
    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        fh.write(f"{key_name}={encode_base64(key_value)}\n")
    print(f"API key written to {file_path} successfully.")
    return


def read_apikey(
    key_name: Optional[str] = None,
    file_path: str = "~/.ecoDI_apikeys"
) -> str:
    """
    Retrieve a stored API key from the key file.

    Parameters
    ----------
    key_name : str, optional
        Identifier of the key to read (required).
    file_path : str, default ``~/.ecoDI_apikeys``
        Location of the key file.

    Returns
    -------
    str
        The decoded API key value.

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.
    ValueError
        If ``key_name`` is missing or the key cannot be found.
    """
    if key_name is None:
        raise ValueError("'key_name' must be provided to identify which key to read from the file.")

    path = pathlib.Path(os.path.expanduser(file_path))

    if not path.is_file():
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    with path.open("r", encoding="utf-8") as fh:
        lines = [ln.rstrip("\n") for ln in fh.readlines()]

    key_map = {}
    for line in lines:
        if "=" not in line:
            continue
        name, encoded = line.split("=", 1)
        key_map[name] = encoded

    if key_name not in key_map:
        raise ValueError(f"Key {key_name} not found in the file {file_path}.")

    return decode_base64(key_map[key_name])


def get_prd_seq(
    period_se: str = "일",
    prd_sde: Optional[Union[str, int]] = None,
    prd_ede: Optional[Union[str, int]] = None,
) -> List[str]:
    """
    Generate a sequence of period identifiers.

    Parameters
    ----------
    period_se : str
        One of the Korean period keywords:
        "일", "월", "분기", "반기", "년",
        "2년", "3년", "4년", "5년", "10년", "부정기".
    prd_sde : str | int | None
        Start period (interpretation depends on ``period_se``).
    prd_ede : str | int | None
        End period (interpretation depends on ``period_se``).

    Returns
    -------
    List[str]
        List of period strings in the same format as the R version.
    """
    # ------------------------------------------------------------------
    # Validate period_se (behaviour similar to R's match.arg)
    # ------------------------------------------------------------------
    valid_options = [
        "일",
        "월",
        "분기",
        "반기",
        "년",
        "2년",
        "3년",
        "4년",
        "5년",
        "10년",
        "부정기",
    ]
    if period_se not in valid_options:
        raise ValueError(
            f"period_se must be one of {valid_options}, got '{period_se}'."
        )

    # ------------------------------------------------------------------
    # Helper: convert YYYYMMDD string to date
    # ------------------------------------------------------------------
    def _to_date_ymd(s: str) -> datetime.date:
        return datetime.datetime.strptime(s, "%Y%m%d").date()

    # ------------------------------------------------------------------
    # Daily ("일")
    # ------------------------------------------------------------------
    if period_se == "일":
        start_date = _to_date_ymd(str(prd_sde))
        end_date = _to_date_ymd(str(prd_ede))

        dates = pd.date_range(start=start_date, end=end_date, freq="D")
        return [d.strftime("%Y%m%d") for d in dates]

    # ------------------------------------------------------------------
    # Monthly ("월") – input like "2023.01"
    # ------------------------------------------------------------------
    if period_se == "월":
        # Append day 01 to create a full date string, then parse.
        start_date = datetime.datetime.strptime(f"{prd_sde}.01", "%Y.%m.%d")
        end_date = datetime.datetime.strptime(f"{prd_ede}.01", "%Y.%m.%d")

        dates = pd.date_range(start=start_date, end=end_date, freq="MS")
        return [d.strftime("%Y.%m") for d in dates]

    # ------------------------------------------------------------------
    # Quarterly ("분기") – input like "2023 1/4"
    # ------------------------------------------------------------------
    if period_se == "분기":
        # Convert "YYYY q/4" → "YYYYQq"
        def _to_period_q(s: str) -> pd.Period:
            year, quarter_part = s.strip().split()
            quarter = quarter_part.split("/")[0]  # e.g. "1" from "1/4"
            return pd.Period(f"{year}Q{quarter}", freq="Q")

        start_per = _to_period_q(prd_sde)
        end_per = _to_period_q(prd_ede)

        periods = pd.period_range(start=start_per, end=end_per, freq="Q")
        return [f"{p.start_time.year} {p.quarter}/4" for p in periods]

    # ------------------------------------------------------------------
    # Half‑year ("반기") – input like "2023 1/2" or "2023 2/2"
    # ------------------------------------------------------------------
    if period_se == "반기":
        # Replace " 1/2" → "0131" (Jan 31) and " 2/2" → "1231" (Dec 31)
        def _replace_half(s: str) -> str:
            s = s.replace(" 1/2", "0131")
            s = s.replace(" 2/2", "1231")
            return s

        start_str = _replace_half(str(prd_sde))
        end_str = _replace_half(str(prd_ede))

        start_date = _to_date_ymd(start_str)
        end_date = _to_date_ymd(end_str)

        dates = pd.date_range(start=start_date, end=end_date, freq="6M")
        result = []
        for d in dates:
            month = d.month
            half = 1 if month <= 6 else 2
            result.append(f"{d.year} {half}/2")
        return result

    # ------------------------------------------------------------------
    # Yearly ("년")
    # ------------------------------------------------------------------
    if period_se == "년":
        start_year = int(prd_sde)
        end_year = int(prd_ede)
        return [str(y) for y in range(start_year, end_year + 1)]

    # ------------------------------------------------------------------
    # Multi‑year steps ("2년", "3년", ...) – numeric step size
    # ------------------------------------------------------------------
    if period_se in {"2년", "3년", "4년", "5년", "10년"}:
        step = int(period_se.replace("년", ""))
        start_year = int(prd_sde)
        end_year = int(prd_ede)
        return [str(y) for y in range(start_year, end_year + 1, step)]

    # ------------------------------------------------------------------
    # Irregular ("부정기")
    # ------------------------------------------------------------------
    if period_se == "부정기":
        return [str(prd_sde), str(prd_ede)]

    # Fallback (should never reach here)
    return []


def get_os() -> str:
    """
    Detect the operating system name, mimicking the behaviour of the R function.

    Returns
    -------
    str
        Lower‑case OS identifier: "osx", "linux", "windows", etc.
    """
    os_name = platform.system()
    if os_name == "Darwin":
        return "osx"
    return os_name.lower()
  

# Exported symbols (similar to R's @export)
__all__ = [
    "regist_apikey",
    "unregist_apikey",
    "write_apikey",
    "read_apikey",
    "get_prd_seq",
    "get_os",
]


