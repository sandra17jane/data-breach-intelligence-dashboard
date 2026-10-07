"""
data_preprocessing.py
----------------------
Handles loading, cleaning, validating, and feature-engineering the
publicly reported data breach dataset used by the Data Breach
Intelligence Dashboard.

All functions are designed to be safe against missing values,
malformed dates, and inconsistent boolean representations that are
common in real-world CSV exports.
"""

import ast
import os

import numpy as np
import pandas as pd

# Columns that must be parsed as datetimes
DATE_COLUMNS = ["BreachDate", "AddedDate", "ModifiedDate"]

# Columns that represent boolean risk / status flags
BOOLEAN_COLUMNS = [
    "IsVerified",
    "IsFabricated",
    "IsSensitive",
    "IsRetired",
    "IsSpamList",
    "IsMalware",
    "IsSubscriptionFree",
]

# Values considered "truthy" when a boolean column arrives as text
TRUE_VALUES = {"true", "1", "yes", "t", "y"}
FALSE_VALUES = {"false", "0", "no", "f", "n"}


def load_raw_dataset(csv_path: str) -> pd.DataFrame:
    """Load the raw breach CSV file from disk.

    Raises a clear, user-friendly error if the file cannot be found
    or parsed, rather than letting a raw traceback surface in the
    Streamlit UI.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Could not find the dataset at '{csv_path}'. "
            "Please make sure the CSV file is placed inside the data/ folder."
        )

    try:
        df = pd.read_csv(csv_path)
    except Exception as exc:  # pragma: no cover - defensive
        raise ValueError(f"Failed to read CSV file at '{csv_path}': {exc}")

    return df


def get_dataset_overview(df: pd.DataFrame) -> dict:
    """Return a dictionary of summary information used on the
    'raw data inspection' portion of the dashboard / notebook story.
    """
    overview = {
        "head": df.head(5),
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str),
        "missing_values": df.isna().sum(),
        "duplicate_rows": int(df.duplicated().sum()),
        "statistical_summary": df.describe(include="all"),
    }
    return overview


def _coerce_boolean(value) -> bool:
    """Safely convert a single value (bool, str, int, NaN) into a
    proper Python bool. Defaults to False for unrecognized / missing
    values so downstream aggregations never break.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and not pd.isna(value):
        return bool(value)
    if isinstance(value, str):
        cleaned = value.strip().lower()
        if cleaned in TRUE_VALUES:
            return True
        if cleaned in FALSE_VALUES:
            return False
    return False


def _parse_data_classes(value) -> list:
    """Parse the DataClasses column, which is stored as a
    string-representation of a Python list, e.g.
    "['Email addresses', 'Passwords']", into an actual list of
    strings. Returns an empty list for missing / malformed values.
    """
    if isinstance(value, list):
        return value
    if not isinstance(value, str) or not value.strip():
        return []
    try:
        parsed = ast.literal_eval(value)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    except (ValueError, SyntaxError):
        pass
    # Fallback: comma-split if literal_eval fails for some reason
    return [item.strip(" []'\"") for item in value.split(",") if item.strip(" []'\"")]


def clean_dataset(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Run the full cleaning + feature engineering pipeline and
    return a new, cleaned DataFrame. The original DataFrame passed
    in is never modified in place.
    """
    df = df_raw.copy()

    # 1. Drop unnamed index columns produced by pandas re-exports
    unnamed_cols = [c for c in df.columns if str(c).startswith("Unnamed")]
    if unnamed_cols:
        df = df.drop(columns=unnamed_cols)

    # 2. Remove exact duplicate rows
    df = df.drop_duplicates()

    # 3. Parse date columns safely (invalid dates become NaT, not errors)
    for col in DATE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)
            # Drop timezone info for simpler downstream date arithmetic
            try:
                df[col] = df[col].dt.tz_localize(None)
            except (TypeError, AttributeError):
                pass

    # 4. Ensure PwnCount is numeric; invalid values become 0
    if "PwnCount" in df.columns:
        df["PwnCount"] = pd.to_numeric(df["PwnCount"], errors="coerce").fillna(0).astype(int)

    # 5. Normalize boolean columns
    for col in BOOLEAN_COLUMNS:
        if col in df.columns:
            df[col] = df[col].apply(_coerce_boolean)

    # 6. Clean text columns: fill missing Domain/Description with placeholders
    if "Domain" in df.columns:
        df["Domain"] = df["Domain"].fillna("unknown").astype(str).str.strip()
        df.loc[df["Domain"] == "", "Domain"] = "unknown"

    if "Description" in df.columns:
        df["Description"] = df["Description"].fillna("").astype(str)

    if "Name" in df.columns:
        df["Name"] = df["Name"].fillna("Unknown").astype(str).str.strip()

    if "Title" in df.columns:
        df["Title"] = df["Title"].fillna(df["Name"]).astype(str).str.strip()

    # 7. Parse DataClasses into real Python lists for downstream analysis
    if "DataClasses" in df.columns:
        df["DataClassesList"] = df["DataClasses"].apply(_parse_data_classes)
        df["NumberOfDataClasses"] = df["DataClassesList"].apply(len)
    else:
        df["DataClassesList"] = [[] for _ in range(len(df))]
        df["NumberOfDataClasses"] = 0

    # 8. Feature engineering derived from BreachDate
    if "BreachDate" in df.columns:
        df["BreachYear"] = df["BreachDate"].dt.year
        df["BreachMonth"] = df["BreachDate"].dt.month
        df["BreachYearMonth"] = df["BreachDate"].dt.to_period("M").astype(str)
        # Rows with unparseable BreachDate get a placeholder year of NaN;
        # these are excluded from year-based charts downstream.
    else:
        df["BreachYear"] = np.nan
        df["BreachMonth"] = np.nan
        df["BreachYearMonth"] = np.nan

    # 9. Log-scaled PwnCount for skewed distribution visualizations
    df["LogPwnCount"] = np.log10(df["PwnCount"].replace(0, 1))

    # 10. Reset index for a clean final dataset
    df = df.reset_index(drop=True)

    return df


def explode_data_classes(df_clean: pd.DataFrame) -> pd.DataFrame:
    """Return a 'long format' DataFrame with one row per
    (breach, data category) pair. This is the format needed to
    count frequency of each exposed data category.
    """
    exploded = df_clean[["Name", "Domain", "BreachYear", "DataClassesList"]].explode(
        "DataClassesList"
    )
    exploded = exploded.rename(columns={"DataClassesList": "DataClass"})
    exploded = exploded.dropna(subset=["DataClass"])
    return exploded


def save_cleaned_dataset(df_clean: pd.DataFrame, output_path: str) -> None:
    """Persist the cleaned dataset to disk as CSV. The list-typed
    DataClassesList column is stringified for safe CSV round-tripping.
    """
    df_to_save = df_clean.copy()
    if "DataClassesList" in df_to_save.columns:
        df_to_save["DataClassesList"] = df_to_save["DataClassesList"].apply(str)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_to_save.to_csv(output_path, index=False)


def load_and_prepare(csv_path: str) -> tuple:
    """Convenience wrapper used by the Streamlit app: loads the raw
    dataset and returns both the raw and cleaned versions.
    """
    df_raw = load_raw_dataset(csv_path)
    df_clean = clean_dataset(df_raw)
    return df_raw, df_clean
