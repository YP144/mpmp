import io
import requests
import pandas as pd
import polars as pl
import json
import streamlit as st
import numpy as np
from pathlib import Path
from dataclasses import dataclass, field 
from typing import Dict, Any, List, Optional
from datetime import datetime, time

def compare_single_options(
    df_initial: pd.DataFrame,
    df_development: pd.DataFrame,
    df_target: pd.DataFrame,
) -> pd.DataFrame:

    key = "Singel Option"

    datasets = {
        "Initial": df_initial,
        "Development": df_development,
        "Target": df_target,
    }

    # Validate key columns and duplicate option names.
    for name, df in datasets.items():
        if key not in df.columns:
            raise ValueError(
                f"{name} DataFrame is missing '{key}'. "
                f"Available columns: {df.columns.tolist()}"
            )

        value_column = name
        if value_column not in df.columns:
            raise ValueError(
                f"{name} DataFrame is missing '{value_column}'"
            )

        duplicates = df.loc[
            df[key].notna() & df[key].duplicated(keep=False),
            key,
        ].unique().tolist()

        if duplicates:
            raise ValueError(
                f"{name} contains duplicate single-option values: "
                f"{duplicates}"
            )

    # Merge Initial and Development first.
    result = df_initial.merge(
        df_development,
        on=key,
        how="outer",
        validate="many_to_many",
        indicator="_initial_development",
    )

    # Add Target.
    result = result.merge(
        df_target,
        on=key,
        how="outer",
        validate="many_to_many",
        indicator="_target_merge",
    )

    # Track which versions contain each option.
    result["Initial Exists"] = result[
        "_initial_development"
    ].isin(["both", "left_only"])

    result["Development Exists"] = result[
        "_initial_development"
    ].isin(["both", "right_only"])

    result["Target Exists"] = result[
        "_target_merge"
    ].isin(["both", "right_only"])

    result.drop(
        columns=["_initial_development", "_target_merge"],
        inplace=True,
    )

    all_exist = (
        result["Initial Exists"]
        & result["Development Exists"]
        & result["Target Exists"]
    )

    # Compare the selected states across all three versions.
    same_values = (
        result["Initial"].eq(result["Development"])
        & result["Development"].eq(result["Target"])
    )

    result["Status"] = "Check"

    result.loc[
        all_exist & same_values,
        "Status",
    ] = "OK"

    result["Remarks"] = ""

    return result.sort_values(
        key,
        na_position="last",
    ).reset_index(drop=True)


def get_single_option_df(
    data: dict | list | str,
    option_name: str,
) -> tuple[pd.DataFrame, list[dict]]:
    """
    Convert single-option API/JSON data into a DataFrame.

    Expected records:
        {
            "optionValue": "Some Option",
            "isChecked": True
        }

    Returns:
        DataFrame and JSON-compatible list of dictionaries.
    """
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"{option_name}: Invalid JSON input"
            ) from exc

    if isinstance(data, dict):
        option_data = data.get("data", [])
    elif isinstance(data, list):
        option_data = data
    else:
        raise TypeError(
            f"{option_name}: Expected dict, list, or JSON string; "
            f"received {type(data).__name__}"
        )

    if not isinstance(option_data, list):
        raise ValueError(
            f"{option_name}: Expected a list of option records"
        )

    invalid_records = [
        i for i, record in enumerate(option_data)
        if not isinstance(record, dict)
    ]

    if invalid_records:
        raise ValueError(
            f"{option_name}: Invalid records at indexes "
            f"{invalid_records[:10]}"
        )

    df_singleopt = pd.DataFrame(
        [
            {
                "Singel Option": record.get("optionValue"),
                option_name: record.get("isChecked"),
            }
            for record in option_data
        ],
        columns=["Singel Option", option_name],
    )

    # Ensure missing values become Python None in JSON output.
    df_singleopt_json = (
        df_singleopt.astype(object)
        .where(pd.notna(df_singleopt), None)
        .to_dict(orient="records")
    )

    return df_singleopt, df_singleopt_json


def compare_hw_single_process(
    mp_json: dict | list | str,
    dev_json: dict | list | str,
    init_json: dict | list | str,
):
    begin_time = datetime.now()

    # Convert each source using isChecked, keyed by optionValue.
    df_initial, _ = get_single_option_df(
        init_json, "Initial"
    )

    df_development, _ = get_single_option_df(
        dev_json, "Development"
    )

    df_target, _ = get_single_option_df(
        mp_json, "Target"
    )

    # Compare Initial, Development, and Target.
    result_df = compare_single_options(
        df_initial,
        df_development,
        df_target,
    )

    # Overall process result.
    overall_result = (
        "CHECK"
        if result_df["Status"].eq("Check").any()
        else "OK"
    )

    result_df["Remarks"] = ""

    compare_columns = [
        "Initial",
        "Development",
        "Target"
    ]

    mapping = {
        True: "●",
        False: ""
    }

    for col in compare_columns:
        result_df[col] = result_df[col].map(mapping)



    finish_time = datetime.now()

    

    # Convert NumPy/pandas values to JSON-compatible values.
    comp_data = (
        result_df.astype(object)
        .where(pd.notna(result_df), None)
        .to_dict(orient="records")
    )

    final_json = {
        "compPro": "BENcompare",
        "process": "HWSingleOption",
        "timestamp": begin_time.strftime("%Y-%m-%d %H:%M:%S"),
        "startTime": begin_time.strftime("%Y-%m-%d %H:%M:%S"),
        "finishTime": finish_time.strftime("%Y-%m-%d %H:%M:%S"),
        "compData": comp_data,
        "result": overall_result,
    }

    return result_df, final_json, overall_result
