"""
analysis.py
------------
Pure analytical functions that compute metrics and summary tables
from the cleaned breach DataFrame. Kept separate from visualization
so the same numbers can power KPI cards, charts, and the narrative
insights page without duplication.

No function here hardcodes a result — every number is derived from
whatever DataFrame is passed in, so filtering upstream automatically
changes every answer downstream.
"""

import numpy as np
import pandas as pd


def total_breaches(df: pd.DataFrame) -> int:
    return int(len(df))


def total_records_exposed(df: pd.DataFrame) -> int:
    return int(df["PwnCount"].sum()) if len(df) else 0


def average_records_per_breach(df: pd.DataFrame) -> float:
    return float(df["PwnCount"].mean()) if len(df) else 0.0


def largest_breach(df: pd.DataFrame) -> pd.Series:
    """Return the full row (as a Series) for the breach with the
    highest PwnCount. Returns an empty Series if df is empty.
    """
    if df.empty:
        return pd.Series(dtype=object)
    return df.loc[df["PwnCount"].idxmax()]


def top_n_breaches_by_pwncount(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return df.sort_values("PwnCount", ascending=False).head(n)[
        ["Name", "Domain", "BreachDate", "PwnCount", "NumberOfDataClasses"]
    ]


def breaches_per_year(df: pd.DataFrame) -> pd.DataFrame:
    counts = (
        df.dropna(subset=["BreachYear"])
        .groupby("BreachYear")
        .size()
        .reset_index(name="BreachCount")
    )
    counts["BreachYear"] = counts["BreachYear"].astype(int)
    return counts.sort_values("BreachYear")


def records_exposed_per_year(df: pd.DataFrame) -> pd.DataFrame:
    totals = (
        df.dropna(subset=["BreachYear"])
        .groupby("BreachYear")["PwnCount"]
        .sum()
        .reset_index(name="TotalRecordsExposed")
    )
    totals["BreachYear"] = totals["BreachYear"].astype(int)
    return totals.sort_values("BreachYear")


def most_common_data_classes(exploded_df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    counts = (
        exploded_df.groupby("DataClass").size().reset_index(name="Frequency")
    )
    return counts.sort_values("Frequency", ascending=False).head(n)


def verified_percentage(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0
    return float(df["IsVerified"].mean() * 100)


def flag_counts(df: pd.DataFrame) -> dict:
    """Return counts for every boolean risk flag in one place."""
    flags = [
        "IsVerified",
        "IsSensitive",
        "IsMalware",
        "IsSpamList",
        "IsFabricated",
        "IsRetired",
        "IsSubscriptionFree",
    ]
    result = {}
    for flag in flags:
        if flag in df.columns:
            result[flag] = int(df[flag].sum())
        else:
            result[flag] = 0
    return result


def pwncount_vs_dataclasses_correlation(df: pd.DataFrame) -> float:
    """Pearson correlation between PwnCount and NumberOfDataClasses."""
    if len(df) < 2:
        return 0.0
    return float(df["PwnCount"].corr(df["NumberOfDataClasses"]))


def top_breaches_by_data_class_count(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return df.sort_values("NumberOfDataClasses", ascending=False).head(n)[
        ["Name", "Domain", "NumberOfDataClasses", "PwnCount"]
    ]


def top_domains(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    counts = df.groupby("Domain").size().reset_index(name="BreachCount")
    return counts.sort_values("BreachCount", ascending=False).head(n)


def identify_extreme_breaches(df: pd.DataFrame, z_threshold: float = 3.0) -> pd.DataFrame:
    """Flag breaches whose PwnCount is an extreme outlier using a
    z-score computed on the log-transformed distribution (since raw
    PwnCount is heavily right-skewed).
    """
    if df.empty or df["LogPwnCount"].std(ddof=0) == 0:
        return df.iloc[0:0][["Name", "Domain", "PwnCount"]]

    mean_log = df["LogPwnCount"].mean()
    std_log = df["LogPwnCount"].std(ddof=0)
    z_scores = (df["LogPwnCount"] - mean_log) / std_log

    extreme = df.loc[z_scores.abs() >= z_threshold, ["Name", "Domain", "PwnCount", "LogPwnCount"]]
    return extreme.sort_values("PwnCount", ascending=False)


def year_with_most_breaches(df: pd.DataFrame):
    counts = breaches_per_year(df)
    if counts.empty:
        return None
    row = counts.loc[counts["BreachCount"].idxmax()]
    return int(row["BreachYear"]), int(row["BreachCount"])


def year_with_most_records_exposed(df: pd.DataFrame):
    totals = records_exposed_per_year(df)
    if totals.empty:
        return None
    row = totals.loc[totals["TotalRecordsExposed"].idxmax()]
    return int(row["BreachYear"]), int(row["TotalRecordsExposed"])


def most_common_single_data_class(exploded_df: pd.DataFrame):
    counts = most_common_data_classes(exploded_df, n=1)
    if counts.empty:
        return None
    row = counts.iloc[0]
    return row["DataClass"], int(row["Frequency"])


def generate_dynamic_insights(df: pd.DataFrame, exploded_df: pd.DataFrame) -> list:
    """Generate a list of plain-English insight strings computed
    directly from the current (possibly filtered) dataset. Used on
    the Executive Overview and Insights & Conclusion pages so the
    narrative never drifts from the actual numbers.
    """
    insights = []

    if df.empty:
        return ["No breaches match the current filter selection."]

    largest = largest_breach(df)
    insights.append(
        f"The largest breach on record is **{largest['Name']}**, exposing "
        f"**{int(largest['PwnCount']):,}** records."
    )

    year_count = year_with_most_breaches(df)
    if year_count:
        insights.append(
            f"**{year_count[0]}** recorded the highest number of breaches "
            f"({year_count[1]} breaches)."
        )

    year_records = year_with_most_records_exposed(df)
    if year_records:
        insights.append(
            f"**{year_records[0]}** had the highest total records exposed "
            f"({year_records[1]:,} records)."
        )

    common_class = most_common_single_data_class(exploded_df)
    if common_class:
        insights.append(
            f"**{common_class[0]}** is the most frequently exposed data "
            f"category, appearing in {common_class[1]} breaches."
        )

    verified_pct = verified_percentage(df)
    insights.append(f"**{verified_pct:.1f}%** of breaches in the dataset are verified.")

    flags = flag_counts(df)
    insights.append(
        f"**{flags['IsSensitive']}** breaches are marked sensitive and "
        f"**{flags['IsMalware']}** are associated with malware."
    )

    corr = pwncount_vs_dataclasses_correlation(df)
    direction = "positive" if corr > 0 else "negative"
    insights.append(
        f"There is a weak-to-moderate {direction} correlation "
        f"(r = {corr:.2f}) between the number of records exposed and the "
        f"number of data categories compromised in a breach."
    )

    return insights
