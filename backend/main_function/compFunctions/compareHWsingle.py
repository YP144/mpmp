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

from services.check_sso import SSO_NPDM, NpdmClient
from functions.conditioning import zerobom_conditioning
from functions.tool_option_logic import GetModelToolOptionMaster, ToolOptionCross
from services.main_tooloption import run_tooloption, getToolinfo
from services.subs_hwpart import run_subshwpart
from compFunctions.check_parts import GetTargetParts

from functions.profile import ModelProfile, GetOperationPart
from functions.substate import GoGetTemplate, GetParseStructure, StructureCheck
from services.main_hwpart import targetpart_compare, developmentpart_compare, initialpart_compare

#comparehw_multiopt()

#New Logic => Should be Faster / Better

def get_multi_option_df(
    data: dict | list | str,
    option_name: str,
) -> tuple[pd.DataFrame, list[dict]]:
    """
    Accept:
      - A list of option records
      - A dictionary containing a 'data' list
      - A JSON string containing either format

    Returns:
      - DataFrame
      - List of dictionaries representing the DataFrame
    """

    # 1. Parse JSON strings if necessary
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"{option_name}: Invalid JSON input"
            ) from exc

    # 2. Support both API response formats
    if isinstance(data, dict):
        option_data = data.get("data", [])
    elif isinstance(data, list):
        option_data = data
    else:
        raise TypeError(
            f"{option_name}: Expected dict, list, or JSON string; "
            f"received {type(data).__name__}"
        )

    # 3. Validate the option records
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

    # 4. Convert records into a DataFrame
    df_multiopt = pd.DataFrame([
        {
            "Multi Option": record.get("designator"),
            option_name: record.get("optionValue"),
        }
        for record in option_data
    ], columns=["Multi Option", option_name])

    # 5. Convert DataFrame to JSON-compatible records
    df_multiopt_json = (
        df_multiopt.astype(object)
        .where(pd.notna(df_multiopt), None)
        .to_dict(orient="records")
    )

    return df_multiopt, df_multiopt_json

def compare_multi_options(
    df_initial: pd.DataFrame,
    df_development: pd.DataFrame,
    df_target: pd.DataFrame,
) -> pd.DataFrame:

    key = "Multi Option"

    # Validate required columns and duplicate keys.
    datasets = {
        "Initial": df_initial,
        "Development": df_development,
        "Target": df_target,
    }

    for name, df in datasets.items():
        if key not in df.columns:
            raise ValueError(f"{name} DataFrame is missing '{key}'")

        duplicates = df.loc[
            df[key].notna() & df[key].duplicated(keep=False), key
        ].unique().tolist()

        if duplicates:
            raise ValueError(
                f"{name} contains duplicate Multi Option values: {duplicates}"
            )

    # Outer merge preserves options that exist in only one version.
    result = df_initial.merge(
        df_development,
        on=key,
        how="outer",
        validate="many_to_many",
        indicator="_initial_development",
    )

    result = result.merge(
        df_target,
        on=key,
        how="outer",
        validate="many_to_many",
    )

    # Report which versions contain each option.
    result["Initial Exists"] = result["_initial_development"].isin(
        ["both", "left_only"]
    )
    result["Development Exists"] = result["_initial_development"].isin(
        ["both", "right_only"]
    )
    result["Target Exists"] = result["Target"].notna()

    result.drop(columns="_initial_development", inplace=True)

    # Compare values only when all three versions have the option.
    all_exist = (
        result["Initial Exists"]
        & result["Development Exists"]
        & result["Target Exists"]
    )

    result["Comparison"] = "MISSING OPTION"

    same_values = (
        result["Initial"].eq(result["Development"])
        & result["Development"].eq(result["Target"])
    )

    result.loc[all_exist & same_values, "Comparison"] = "OK"
    result.loc[all_exist & ~same_values, "Comparison"] = "DIFFERENT"

    # Keep a predictable row order.
    return result.sort_values(key, na_position="last").reset_index(drop=True)


def compare_hw_multi_process(mp_json: dict, dev_json: dict, init_json: dict):

    begin_time = datetime.now()

    df_initial_multiopt, json_initial_multiopt = get_multi_option_df(
        init_json, "Initial"
    )

    df_development_multiopt, json_development_multiopt = get_multi_option_df(
        dev_json, "Development"
    )

    df_target_multiopt, json_target_multiopt = get_multi_option_df(
        mp_json, "Target"
    )
    
    hw_multi_compare_result = compare_multi_options(
        df_initial_multiopt,
        df_development_multiopt,
        df_target_multiopt
    )

    status_df = hw_multi_compare_result["Comparison"]

    result = (
        "CHECK"
        if status_df.eq("Check").any()
        else "OK"
    )

    hw_multi_compare_result["Remarks"] = ""
    
    finish_time = datetime.now()

    # Convert DataFrame rows into Python list of dicts
    comp_data = hw_multi_compare_result.replace({np.nan: None}).to_dict(
        orient="records"
    )

    # Create final JSON structure
    final_json_data = {
        "compPro": "BENcompare",
        "process": "HWmultiOption",
        "timestamp": begin_time.strftime("%Y-%m-%d %H:%M:%S"),
        "startTime": begin_time.strftime("%Y-%m-%d %H:%M:%S"),
        "finishTime": finish_time.strftime("%Y-%m-%d %H:%M:%S"),
        "compData": comp_data,
        "result": result
    }

    #st.dataframe(comp_data)

    final_json = final_json_data

    return hw_multi_compare_result, final_json, result

