import pandas as pd
import json
from datetime import datetime, time
from services.new_main_hw_part import PartComparison

def compare_hw_status(combined_df: pd.DataFrame) -> pd.DataFrame:
    df = combined_df.copy()
    
    # Identify empty part rows (where all PN / UniqueID values across target, dev, and initial are blank)
    part_cols = [col for col in df.columns if col.endswith('_pn') or col.endswith('_uniqueid')]
    is_blank_row = df[part_cols].apply(
        lambda row: row.astype(str).str.strip().eq('').all(), axis=1
    )
    
    # Filter out blank rows from the DataFrame
    df = df[~is_blank_row].reset_index(drop=True)
    
    check_cols = ["pn", "qty", "uit", "supplytype", "state"]
    
    mpx_results = []
    mpx_reasons = []
    eng_confirms = []
    eng_reasons = []

    # Rule categories requiring 'release' status
    rule_categories = {
        "ebt main", "ir assy", "ebt subassy", "sw assy", "ebu main", "ebu svc"
    }

    for idx, row in df.iterrows():
        # --- 1. MPX Result & MPX Reason ---
        mismatches = []
        for col in check_cols:
            t_val = str(row.get(f"target_{col}", "") or "").strip()
            d_val = str(row.get(f"dev_{col}", "") or "").strip()
            i_val = str(row.get(f"initial_{col}", "") or "").strip()

            col_diffs = []
            if t_val != d_val:
                col_diffs.append(f"Target({t_val if t_val else 'BLANK'}) vs Dev({d_val if d_val else 'BLANK'})")
            if t_val != i_val:
                col_diffs.append(f"Target({t_val if t_val else 'BLANK'}) vs Initial({i_val if i_val else 'BLANK'})")
            if d_val != i_val and t_val == d_val:
                col_diffs.append(f"Dev({d_val if d_val else 'BLANK'}) vs Initial({i_val if i_val else 'BLANK'})")

            if col_diffs:
                mismatches.append(f"{col.upper()} mismatch: [{', '.join(col_diffs)}]")

        if not mismatches:
            mpx_results.append("SAME")
            mpx_reasons.append("All attributes (PN, Qty, UIT, Supply Type, State) match across environments.")
        else:
            mpx_results.append("DIFFERENT")
            mpx_reasons.append("; ".join(mismatches))

        # --- 2. Engineering Confirm & Confirmed Reason ---
        category = str(row.get("target_Category", "")).strip().lower()
        requires_release = (category in rule_categories) or ("ebr" in category)

        t_state = str(row.get("target_state", "") or "").strip().lower()
        d_state = str(row.get("dev_state", "") or "").strip().lower()
        i_state = str(row.get("initial_state", "") or "").strip().lower()

        if requires_release:
            non_release = []
            if t_state != "release":
                non_release.append(f"Target state is '{t_state if t_state else 'BLANK'}'")
            if d_state != "release":
                non_release.append(f"Dev state is '{d_state if d_state else 'BLANK'}'")
            if i_state != "release":
                non_release.append(f"Initial state is '{i_state if i_state else 'BLANK'}'")

            if not non_release:
                eng_confirms.append("OK")
                eng_reasons.append(f"Category '{category}' rule met: all environments are in 'release' state.")
            else:
                eng_confirms.append("Unchecked")
                eng_reasons.append(f"Category '{category}' requires 'release' state, but {', '.join(non_release)}.")
        else:
            eng_confirms.append("OK")
            eng_reasons.append(f"Category '{category}' has no specific release requirement.")

    # Assign new columns to DataFrame
    df["MPX Result"] = mpx_results
    df["MPX Reason"] = mpx_reasons
    df["Engineering Confirm"] = eng_confirms
    df["Confirmed Reason"] = eng_reasons
    df["Remarks"] = ""  # Blank as requested

    return df

def compare_hw_status_process(target_bom, dev_bom, initial_bom):

    begin_time = datetime.now()

    # 1. Create instances for each environment
    target_comp = PartComparison(json_input=target_bom)
    dev_comp = PartComparison(json_input=dev_bom)
    initial_comp = PartComparison(json_input=initial_bom)

    # 2. Run the processing for each
    target_comp.target_run()
    dev_comp.target_run()
    initial_comp.target_run()

    # 3. Access the DataFrame output from each
    target_df = target_comp.targethw
    dev_df = dev_comp.targethw
    initial_df = initial_comp.targethw

    # 4. Add prefixes to differentiate column names for each source
    target_df_renamed = target_df.add_prefix("target_")
    dev_df_renamed = dev_df.add_prefix("dev_")
    initial_df_renamed = initial_df.add_prefix("initial_")

    # 5. Concatenate side-by-side (axis=1) with unique column names
    combined_df = pd.concat([target_df_renamed, dev_df_renamed, initial_df_renamed], axis=1)
    compare_combined_df = compare_hw_status(combined_df=combined_df)
    result_dict = compare_combined_df.to_dict(orient="records")

    finish_time = datetime.now()


    # Create final JSON structure
    final_json_data = {
        "compPro": "HWPartCheck",
        "process": "HWpartStatus",
        "timestamp": begin_time.strftime("%Y-%m-%d %H:%M:%S"),
        "startTime": begin_time.strftime("%Y-%m-%d %H:%M:%S"),
        "finishTime": finish_time.strftime("%Y-%m-%d %H:%M:%S"),
        "result": result_dict
    }


    return compare_combined_df, final_json_data

