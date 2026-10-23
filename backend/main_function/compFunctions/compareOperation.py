import io
import requests
import pandas as pd
import polars as pl
import json
import numpy as np
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime, time

from main_function.services.check_sso import SSO_NPDM, NpdmClient
from main_function.functions.conditioning import zerobom_conditioning
from main_function.functions.tool_option_logic import GetModelToolOptionMaster, ToolOptionCross
from main_function.services.main_tooloption import run_tooloption, getToolinfo
from main_function.services.subs_hwpart import run_subshwpart
from main_function.compFunctions.check_parts import GetTargetParts

from main_function.functions.profile import ModelProfile, GetOperationPart
from main_function.functions.substate import GoGetTemplate, GetParseStructure, StructureCheck
from main_function.services.main_hwpart import targetpart_compare, developmentpart_compare, initialpart_compare


def _safe_scalar_value(value, default=None):
    """
    Convert possible Polars/Pandas/Numpy values into one Python scalar.

    This prevents Polars ShapeError such as:
        cannot evaluate two Series of different lengths (3 and 0)

    Do not use external Series directly inside:
        pl.when(...)
    """

    if value is None:
        return default

    if isinstance(value, pl.Series):
        if value.len() == 0:
            return default

        first_value = value.item(0)

        if first_value is None:
            return default

        return first_value

    if isinstance(value, pd.Series):
        if len(value) == 0:
            return default

        first_value = value.iloc[0]

        if pd.isna(first_value):
            return default

        return first_value

    if isinstance(value, np.ndarray):
        if value.size == 0:
            return default

        first_value = value.flat[0]

        if first_value is None:
            return default

        return first_value

    return value


def _safe_bool(value, default=False):
    """
    Convert any value to a Python bool safely.
    """

    value = _safe_scalar_value(value, default=default)

    if value is None:
        return default

    if isinstance(value, str):
        value_clean = value.strip().lower()

        if value_clean in ["", "none", "null", "nan", "false", "0", "no", "n"]:
            return False

        if value_clean in ["true", "1", "yes", "y"]:
            return True

    return bool(value)


def _safe_text(value, default=""):
    """
    Convert possible Series/scalar into clean string.
    """

    value = _safe_scalar_value(value, default=default)

    if value is None:
        return default

    return str(value).strip()


def _ensure_columns(df: pl.DataFrame, required_columns: dict) -> pl.DataFrame:
    """
    Ensure required columns exist before select/filter logic.

    required_columns format:
        {
            "column_name": default_value
        }
    """

    if df is None:
        df = pl.DataFrame()

    for col_name, default_value in required_columns.items():
        if col_name not in df.columns:
            df = df.with_columns(
                pl.lit(default_value).alias(col_name)
            )

    return df


def compare_operation(targetBOM, target_model, ssolgenet_cookie=None, smsession_cookie=None):
    # Safely resolve cookies.
    ssolgenet = ssolgenet_cookie or globals().get("ssolgenet", "")
    smsession = smsession_cookie or globals().get("smsession", "")

    # Load model profile and operation plan.
    getProfile = ModelProfile(
        target_model,
        ssolgenet_cookie=ssolgenet,
        smsession_cookie=smsession
    )

    # IMPORTANT FIX:
    # Make sure this is always Python bool, not Polars Series.
    heros_region = _safe_text(getattr(getProfile, "GetHerosRegion", ""), default="")
    is_na_region = heros_region.upper() == "NA"

    getOperation = GetOperationPart(
        target_model
    )

    targetParts = GetTargetParts(targetBOM, target_model)

    operation_db_version = getattr(getOperation, "latest_version", "")
    operation_region = getattr(getOperation, "region_operationPlan", "")

    dej_operation = getattr(getOperation, "OperationGet", pl.DataFrame())

    # Defensive schema handling for operation plan.
    required_dej_columns = {
        "Category": "",
        "raw_partNo": "",
        "raw_operationLevel": "",
        "raw_operationQuantity": None,
        "raw_substitute": "",
        "raw_rawSubstituteQuantity": None,
        "raw_releaseNo": "",
        "raw_masterRemark": "",
        "raw_accMagicRemote": "",
        "raw_suffixHq": "",
        "raw_suffixHqException": "",
    }

    dej_operation = _ensure_columns(dej_operation, required_dej_columns)

    dej_operation = dej_operation.select([
        "Category",
        "raw_partNo",
        "raw_operationLevel",
        "raw_operationQuantity",
        "raw_substitute",
        "raw_rawSubstituteQuantity",
        "raw_releaseNo",
        "raw_masterRemark",
        "raw_accMagicRemote",
        "raw_suffixHq",
        "raw_suffixHqException",
    ])

    target_operation = getattr(targetParts, "target_operation", pl.DataFrame())

    required_target_columns = {
        "Category": "",
        "dataType": "",
        "part_number": "",
        "part_quantity": None,
        "JobExpl": "",
    }

    target_operation = _ensure_columns(target_operation, required_target_columns)

    if "JobExpl" in target_operation.columns:
        target_operation = target_operation.drop(["JobExpl"])

    target_operation = target_operation.filter(
        pl.col("dataType") == "B"
    )

    # If either side is empty, return a safe empty result instead of crashing.
    if dej_operation.height == 0 or target_operation.height == 0:
        operationResult = pl.DataFrame({
            "Category": [],
            "partNo": [],
            "operationLevel": [],
            "operationQuantity": [],
            "substitute": [],
            "rawSubstituteQuantity": [],
            "releaseNo": [],
            "masterRemark": [],
            "accMagicRemote": [],
            "part_number": [],
            "part_quantity": [],
            "pnCheck": [],
            "qtyCheck": [],
            "uitCheck": [],
            "Status": [],
            "Remarks": [],
        })

        operationJson = {
            "db_version": operation_db_version,
            "region_operation": operation_region,
            "remote": getattr(getProfile, "GetRemoteMR", ""),
            "operation_data": operationResult.to_dicts(),
        }

        columnsOp = dej_operation.columns
        result_check = "NG"

        return columnsOp, dej_operation, target_operation, operationResult, operationJson, result_check

    operationResult = (
        dej_operation
        .join(
            target_operation,
            on="Category",
            how="inner"
        )
        .unique(subset=["raw_partNo", "part_number"])
    )

    # If join result is empty, return safely.
    if operationResult.height == 0:
        operationResult = pl.DataFrame({
            "Category": [],
            "partNo": [],
            "operationLevel": [],
            "operationQuantity": [],
            "substitute": [],
            "rawSubstituteQuantity": [],
            "releaseNo": [],
            "masterRemark": [],
            "accMagicRemote": [],
            "part_number": [],
            "part_quantity": [],
            "pnCheck": [],
            "qtyCheck": [],
            "uitCheck": [],
            "Status": [],
            "Remarks": [],
        })

        operationJson = {
            "db_version": operation_db_version,
            "region_operation": operation_region,
            "remote": getattr(getProfile, "GetRemoteMR", ""),
            "operation_data": operationResult.to_dicts(),
        }

        columnsOp = dej_operation.columns
        result_check = "NG"

        return columnsOp, dej_operation, target_operation, operationResult, operationJson, result_check

    operationResult = operationResult.with_columns([
        pl.lit(None).alias("pnCheck"),
        pl.lit(None).alias("qtyCheck"),
        pl.lit(None).alias("uitCheck"),
        pl.lit(None).alias("Status"),
        pl.lit(None).alias("Remarks"),
    ])

    operationResult = operationResult.with_columns([
        pl.col("raw_operationQuantity")
        .cast(pl.Float64, strict=False)
        .alias("raw_operationQuantity_num"),

        pl.col("part_quantity")
        .cast(pl.Float64, strict=False)
        .alias("part_quantity_num"),
    ])

    operationResult = operationResult.with_columns([
        pl.when(
            pl.col("raw_substitute")
            .cast(pl.Utf8)
            .fill_null("")
            .str.split("/")
            .list.contains(pl.col("part_number").cast(pl.Utf8))
        )
        .then(pl.lit(0))
        .when(
            pl.col("raw_partNo").cast(pl.Utf8)
            ==
            pl.col("part_number").cast(pl.Utf8)
        )
        .then(pl.lit(0))
        .otherwise(pl.lit(1))
        .alias("pnCheck"),

        pl.when(
            pl.col("raw_operationQuantity_num") == pl.col("part_quantity_num")
        )
        .then(pl.lit(0))
        .otherwise(pl.lit(1))
        .alias("qtyCheck"),
    ])

    # IMPORTANT FIX:
    # Use a scalar literal only.
    # Also use is_in(["Battery", "Remote"]), not is_in([["Battery", "Remote"]]).
    battery_remote_na_expr = (
        pl.col("Category").is_in(["Battery", "Remote"])
        &
        pl.lit(is_na_region)
    )

    operationResult = operationResult.with_columns(
        pl.when(battery_remote_na_expr)
        .then(pl.lit(0))

        .when(
            (pl.col("Category") == "6in1 EBT")
            &
            (pl.col("raw_partNo").cast(pl.Utf8) == pl.col("part_number").cast(pl.Utf8))
        )
        .then(pl.lit(0))

        .when(pl.col("Category") == "6in1 EBT")
        .then(pl.lit(1))

        .when(
            (pl.col("pnCheck") == 0)
            &
            (pl.col("qtyCheck") == 0)
        )
        .then(pl.lit(0))

        .otherwise(pl.lit(1))
        .alias("Status")
    )

    operationResult = operationResult.unique(subset="part_number")

    # NOTE:
    # Your original code wrote remarks into alias("Status") again.
    # This overwrites numeric Status with string OK/NG.
    # I changed this to alias("Remarks").
    operationResult = operationResult.with_columns(
        pl.when(battery_remote_na_expr)
        .then(pl.lit("OK"))

        .when(
            (pl.col("Category") == "6in1 EBT")
            &
            (pl.col("raw_partNo").cast(pl.Utf8) == pl.col("part_number").cast(pl.Utf8))
        )
        .then(pl.lit("OK"))

        .when(pl.col("Category") == "6in1 EBT")
        .then(pl.lit("NG"))

        .when(
            (pl.col("pnCheck") == 0)
            &
            (pl.col("qtyCheck") == 0)
        )
        .then(pl.lit("OK"))

        .when(
            (pl.col("pnCheck") == 1)
            &
            (pl.col("qtyCheck") == 1)
        )
        .then(pl.lit("Part No and Quantity Mismatch"))

        .when(pl.col("pnCheck") == 1)
        .then(pl.lit("Part No Mismatch"))

        .otherwise(pl.lit("Quantity Mismatch"))
        .alias("Remarks")
    )

    operationResult = operationResult.rename({
        "raw_partNo": "partNo",
        "raw_operationLevel": "operationLevel",
        "raw_operationQuantity": "operationQuantity",
        "raw_substitute": "substitute",
        "raw_rawSubstituteQuantity": "rawSubstituteQuantity",
        "raw_releaseNo": "releaseNo",
        "raw_masterRemark": "masterRemark",
        "raw_accMagicRemote": "accMagicRemote",
    })

    operationJson = {
        "db_version": operation_db_version,
        "region_operation": operation_region,
        "remote": getattr(getProfile, "GetRemoteMR", ""),
        "operation_data": operationResult.to_dicts(),
    }

    columnsOp = dej_operation.columns

    # Status is numeric: 0 = OK, 1 = NG.
    result_check = (
        "NG"
        if operationResult.select((pl.col("Status") != 0).any()).item()
        else "OK"
    )

    return columnsOp, dej_operation, target_operation, operationResult, operationJson, result_check


def compare_operation_new(CompleteBOM, target_model):
    get_operation_part = GetOperationPart(target_model)

    required_cols = [
        'input_part_number', 'row_part_number', 'raw_operationRole', 
        'raw_operationYear', 'raw_partNo', 'raw_operationLevel', 'raw_boxHeight',
        'raw_substitute', 'raw_substituteQuantity',
        'raw_modelException', 'raw_model', 'raw_suffixHq', 'raw_suffixHqException', 
        'raw_plant', 'raw_plantException', 'raw_parentPartNo', 'raw_operationQuantity', 
        'raw_masterRemark', 'raw_releaseNo', 'raw_accMagicRemote',
        'Category', 'reason', 'matched_criteria'
    ]
    
    existing_cols = [c for c in required_cols if c in get_operation_part.OperationGet.columns]
    selected_df = get_operation_part.OperationGet.select(existing_cols).unique()

    # Determine if Remote and Battery are optional based on model_remote state
    model_remote = get_operation_part.opertionPlanMacthReport.get("miseEnPlace", {}).get("model_remote", "")
    normalized_remote_val = str(model_remote).strip().lower() if model_remote else ""
    is_remote_battery_optional = normalized_remote_val in ["ready", "blank", "none", ""]

    # Base required prefixes definition
    required_base_prefixes = {"EAD": "PowerCord", "EAB": "Speaker", "ECC": "Edid"}
    if not is_remote_battery_optional:
        required_base_prefixes["AKB"] = "Remote"
    
    if "input_part_number" in selected_df.columns and selected_df.height > 0:
        present_prefixes = set(
            selected_df.select(pl.col("input_part_number").str.slice(0, 3).alias("prefix"))
            .drop_nulls()["prefix"]
            .unique()
            .to_list()
        )
    else:
        present_prefixes = set()

    unmatched_inputs = getattr(get_operation_part, "unmatched_input_parts", [])
    unmatched_prefix_map = {item["prefix"]: item for item in unmatched_inputs}

    missing_details = []

    # Validate required base prefixes (AKB dynamically included only if not optional)
    for req_pref, category in required_base_prefixes.items():
        if req_pref not in present_prefixes:
            if req_pref in unmatched_prefix_map:
                why_reason = f"Present in operation plan list for prefix '{req_pref}', but failed model/region/suffix/plant filtering criteria."
            else:
                why_reason = f"Prefix '{req_pref}' ({category}) was not found in the operation plan list for model '{target_model}'."
            
            missing_details.append({
                "prefix": req_pref,
                "category": category,
                "why": why_reason
            })

    # Validate Battery prefix only if Remote & Battery are NOT optional
    if not is_remote_battery_optional:
        if ("691" not in present_prefixes) and ("EAC" not in present_prefixes):
            if "EAC" in unmatched_prefix_map:
                why_reason = "Battery prefix '6910VA' / 'EAC' was evaluated but failed model/region/suffix/plant filtering criteria."
            else:
                why_reason = "Neither '691' nor 'EAC' battery prefixes were found in the operation plan list."
            
            missing_details.append({
                "prefix": "691 / EAC",
                "category": "Battery",
                "why": why_reason
            })

    has_missing_required_prefixes = len(missing_details) > 0

    if has_missing_required_prefixes:
        summary_lines = ["MISSING REQUIRED PARTS DETECTED (Result: NG):"]
        for idx, item in enumerate(missing_details, 1):
            summary_lines.append(f"  {idx}. Part/Prefix: [{item['prefix']}] ({item['category']})")
            summary_lines.append(f"     Reason: {item['why']}")
        missing_parts_summary = "\n".join(summary_lines)
    else:
        missing_parts_summary = "All required part categories are present."

    # Finalize report and push to Mongo
    get_operation_part.finalize_and_push_report(missing_parts_summary, missing_details)

    bom_part_numbers = CompleteBOM["part_number"].drop_nulls().unique()

    compared_df = selected_df.with_columns(
        pl.when(pl.col("raw_partNo").is_in(bom_part_numbers))
        .then(pl.lit("Matched with raw_partNo"))
        .when(
            pl.col("raw_substitute").is_not_null() & 
            (pl.col("raw_substitute") != "") & 
            pl.col("raw_substitute").is_in(bom_part_numbers)
        )
        .then(pl.lit("bom use substitute"))
        .otherwise(pl.lit("not match/ no matching found"))
        .alias("compare_states"),
        
        pl.when(
            pl.col("raw_partNo").is_in(bom_part_numbers) | 
            (
                pl.col("raw_substitute").is_not_null() & 
                (pl.col("raw_substitute") != "") & 
                pl.col("raw_substitute").is_in(bom_part_numbers)
            )
        )
        .then(pl.lit("OK"))
        .otherwise(pl.lit("NG"))
        .alias("part_number_status"),
        
        pl.when(pl.col("raw_partNo").is_in(bom_part_numbers))
        .then(pl.col("raw_partNo"))
        .when(
            pl.col("raw_substitute").is_not_null() & 
            (pl.col("raw_substitute") != "") & 
            pl.col("raw_substitute").is_in(bom_part_numbers)
        )
        .then(pl.col("raw_substitute"))
        .otherwise(pl.lit(None))
        .alias("_join_key")
    )

    final_output_df = compared_df.join(
        CompleteBOM,
        left_on="_join_key",
        right_on="part_number",
        how="left"
    ).rename({"_join_key": "CompleteBOM_part_number"}).unique()

    final_output_df = final_output_df.with_columns(
        pl.when(pl.col("part_number_status") == "NG")
        .then(pl.lit("NG"))
        .otherwise(pl.lit("OK"))
        .alias("status")
    )

    final_output_df = final_output_df.with_columns(
        pl.concat_str([
            pl.when(pl.col("part_number_status") == "NG")
            .then(pl.lit("part_number_status NG; "))
            .otherwise(pl.lit(""))
        ])
        .str.strip_chars()
        .alias("status_remark")
    )

    if "raw_partNo" in final_output_df.columns:
        final_output_df = final_output_df.unique(subset=["input_part_number", "raw_partNo"])

    operationJson = final_output_df.to_dicts()

    has_row_ng = final_output_df.height == 0 or final_output_df.select((pl.col("status") != "OK").any()).item()
    
    result_check = "NG" if (has_row_ng or has_missing_required_prefixes) else "OK"

    return operationJson, final_output_df, result_check, get_operation_part