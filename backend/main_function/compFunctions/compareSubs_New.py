import polars as pl
import re
import json
import pandas as pd


import polars as pl

def get_subsititute_part_only(bom_input: pl.DataFrame) -> pl.DataFrame:
    """
    1. Filters input BOM for Substitute parts (dataType == 'S').
    2. Identifies 'HW' parts based on part number (pn) / name / description rules from target_run.
    3. Adds a 'category' column identifying the part category.
    """
    
    def classify_part(row: dict) -> tuple[str, str]:
        # Extract outData nested dictionary if present
        out_data = row.get("outData") or {}
        if not isinstance(out_data, dict):
            out_data = {}

        pn = str(
            row.get("childNameDisplay") or row.get("part_number") or row.get("pn") or ""
        ).strip()
        
        desc = str(
            row.get("childDescription") or row.get("description") or out_data.get("pp_descriptions") or ""
        ).strip()
        
        spec = str(
            row.get("spec") or out_data.get("mr_siteTechnicalSpec") or ""
        ).strip()

        # --- Classification logic ---
        if pn.startswith("AAA") or "Accessory Assembly" in desc:
            return "Accessory Assembly", "HW"
        if pn.startswith("621") or "Ferrite" in desc:
            return "Ferrite Core", "HW"
        if pn.startswith("130") or "Battery" in desc or "LR" in spec:
            return "Battery", "HW"
        if pn.startswith("AKB") or "Remote" in desc or "MR" in spec or "L-Con" in spec:
            return "Remote Control", "HW"
        if pn.startswith(("ABA", "ACQ")) or "Bracket Assembly" in desc:
            return "Bracket Assembly", "HW"
        if pn.startswith("EBT") and ("Chassis Assembly,Sub" in desc or "Sub" in desc):
            return "Sub Chassis Assembly", "HW"
        if pn.startswith("EAT") or "Module,Wifi Bluetooth Module" in desc or "Wifi" in desc:
            return "WiFi/Bluetooth Module", "HW"
        if pn.startswith("EBR") and ("PCB Assembly,IR Key" in desc or "IR Key" in desc):
            return "IR Key PCB Assembly", "HW"
        if pn.startswith("EAB") or "Speaker" in desc:
            return "Speaker", "HW"
        if pn.startswith("EAD"):
            if "Power Cord" in desc:
                return "Power Cord", "HW"
            if "Harness" in desc:
                return "Harness", "HW"
            return "FFC Cable", "HW"
        if pn.startswith(("EAY", "EBR")) and ("Power" in desc or "LGP" in spec):
            return "Power Board", "HW"
        if pn.startswith("EBT") and "Chassis Assembly" in desc:
            return "Main Chassis Assembly", "HW"
        if pn.startswith("MEG") or "Holder" in desc:
            return "Holder", "HW"
        if pn.startswith("EBZ") or "Tuner" in spec:
            return "Tuner Cover / Part", "HW"
        if pn.startswith("961") or "Tape,Glass Fiber" in desc:
            return "Glass Fiber Tape", "HW"
        if pn.startswith("EBS") or "Electric Parts Assembly,Main" in desc:
            return "Main Electric Parts Assembly / Shield", "HW"
        if pn.startswith(("MED", "MGJ")):
            return "Heat Sink / Plate", "HW"
        if pn.startswith("RAA") or "Sheet,Copper" in desc:
            return "Copper Sheet", "HW"
        if pn.startswith("AGF") or "Package Assembly" in desc:
            return "Package Assembly", "HW"
        if pn.startswith("EBU") or "ORP Total Assembly" in desc or "BPR Total Assembly" in desc:
            return "EBU Mainboard Assembly", "HW"
        if pn.startswith("EBR") and ("Insert PCB Assembly" in desc or "PCB Assembly,Main" in desc):
            return "Main PCB Assembly", "HW"
        if pn.startswith("EAX") or "PCB" in desc:
            return "Bare PCB", "HW"
        if pn.startswith("ECC") or "EDID Check Sum Assembly" in desc:
            return "EDID Assembly", "HW"
        if pn.startswith("SAB") or "S/W Package" in desc:
            return "Software / eMMC Package", "HW"
        if pn.startswith("MDS") or "Gasket" in desc:
            return "Gasket", "HW"
        if pn.startswith("RAB") or "Tape" in desc:
            return "Tape", "HW"
        if pn.startswith("MCQ") or "Damper" in desc:
            return "Damper", "HW"

        return "Uncategorized HW", "HW"

    # Filter for substitute data type first
    substitute_bom = bom_input.filter(pl.col("dataType") == "S")

    # If the DataFrame is empty, return early with expected schema
    if substitute_bom.is_empty():
        return substitute_bom.with_columns([
            pl.lit("").alias("category"),
            pl.lit("").alias("part_type")
        ])

    # Classify each row
    rows = substitute_bom.to_dicts()
    classifications = [classify_part(row) for row in rows]

    categories = [cat for cat, ptype in classifications]
    part_types = [ptype for cat, ptype in classifications]

    # Add new category and part_type columns, then filter to 'HW' parts only
    res_df = (
        substitute_bom
        .with_columns([
            pl.Series("category", categories),
            pl.Series("part_type", part_types)
        ])
        .filter(pl.col("part_type") == "HW")
        .drop("part_type")  # Remove temporary column
    )

    res_df = res_df.drop(['uniqueStr', 'uniqueStrParent', 'referenceDesignator'])

    return res_df

def compare_substitute_bom(target: pl.DataFrame, dev: pl.DataFrame, init: pl.DataFrame):
    substitute_target      = get_subsititute_part_only(bom_input=target)
    substitute_development = get_subsititute_part_only(bom_input=dev)
    substitute_initial     = get_subsititute_part_only(bom_input=init)

    # 1. Identify primary part number join key column name
    join_keys = []
    for col in ["part_number", "pn", "childNameDisplay"]:
        if col in substitute_target.columns:
            join_keys.append(col)
            break

    if not join_keys:
        join_keys = [c for c in substitute_target.columns if "part_number" in c or "pn" in c]

    key_col = join_keys[0]

    # 2. Rename columns with mode prefixes (target_, dev_, init_)
    target_renamed = substitute_target.rename({c: f"target_{c}" for c in substitute_target.columns})
    dev_renamed    = substitute_development.rename({c: f"dev_{c}" for c in substitute_development.columns})
    init_renamed   = substitute_initial.rename({c: f"init_{c}" for c in substitute_initial.columns})

    t_key = f"target_{key_col}"
    d_key = f"dev_{key_col}"
    i_key = f"init_{key_col}"

    # 3. Join Target and Dev
    df_td = target_renamed.join(
        dev_renamed,
        left_on=t_key,
        right_on=d_key,
        how="full",
        coalesce=False
    )

    # Create a coalesced join key so Dev-only parts can match Init-only parts
    df_td = df_td.with_columns(
        pl.coalesce([pl.col(t_key), pl.col(d_key)]).alias("_shared_join_key")
    )

    # 4. Join with Init on the coalesced join key
    combined_df = df_td.join(
        init_renamed,
        left_on="_shared_join_key",
        right_on=i_key,
        how="full",
        coalesce=False
    ).drop("_shared_join_key")

    # 5. Filter out rows that are 'Uncategorized HW' / 'Uncategorised HW' in ALL THREE environments
    uncategorized_targets = ["Uncategorized HW", "Uncategorised HW"]
    
    is_all_uncategorized = (
        pl.col("target_category").fill_null("").is_in(uncategorized_targets) &
        pl.col("dev_category").fill_null("").is_in(uncategorized_targets) &
        pl.col("init_category").fill_null("").is_in(uncategorized_targets)
    )

    result_df = "TRIAL"

    # Keep rows where at least one environment has a valid category or missing entry
    combined_df = combined_df.filter(~is_all_uncategorized)

    # 6. Fill remaining null values with empty strings
    combined_df = combined_df.fill_null("")



    combined_dict = combined_df.to_dicts()

    return combined_df, combined_dict, result_df