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


def compareBENtool():
    JSON_DIR = Path(__file__).resolve().parent.parent / "json"
    begin_time = datetime.now()

    with open(JSON_DIR / "3_initial_tooloption.json", "r", encoding="utf-8") as f:
        df_initial_tooloption = pd.DataFrame(json.load(f))
    
    with open(JSON_DIR / "3_development_tooloption.json", "r", encoding="utf-8") as f:
        df_development_tooloption = pd.DataFrame(json.load(f))
    
    with open(JSON_DIR / "3_target_tooloption.json", "r", encoding="utf-8") as f:
        df_target_tooloption = pd.DataFrame(json.load(f))

    initial_dict = df_initial_tooloption.iloc[0].to_dict()
    dev_dict = df_development_tooloption.iloc[0].to_dict()
    target_dict = df_target_tooloption.iloc[0].to_dict()

    tooloption_compare_df = pd.DataFrame({
        "Category": initial_dict.keys(),
        "Initial": initial_dict.values(),
        "Development": [dev_dict.get(k) for k in initial_dict.keys()],
        "Target": [target_dict.get(k) for k in initial_dict.keys()],
        "Remarks":["" for k in initial_dict.keys()]
    })

    # Replace empty strings with NaN for consistent comparison
    tooloption_compare_df = tooloption_compare_df.replace("", np.nan)

    # Add Status column
    # 1 = different, 0 = same
    tooloption_compare_df["Status"] = tooloption_compare_df[
        ["Initial", "Development", "Target"]
    ].nunique(
        axis=1,
        dropna=False
    ).gt(1).astype(int)

    # Overall result
    # 1 = at least one difference exists
    # 0 = no difference
    result = int(tooloption_compare_df["Status"].eq(1).any())

    finish_time = datetime.now()

    # Convert DataFrame rows into Python list of dicts
    comp_data = tooloption_compare_df.replace({np.nan: None}).to_dict(
        orient="records"
    )

    # Create final JSON structure
    final_json_data = {
        "compPro": "BENcompare",
        "process": "Tooloption",
        "timestamp": begin_time.strftime("%Y-%m-%d %H:%M:%S"),
        "startTime": begin_time.strftime("%Y-%m-%d %H:%M:%S"),
        "finishTime": finish_time.strftime("%Y-%m-%d %H:%M:%S"),
        "compData": comp_data,
        "result": result
    }

    # Convert to JSON string
    """tooloption_json = json.dumps(
        final_json_data,
        ensure_ascii=False,
        indent=4
    )"""

    tooloption_json = final_json_data

    return tooloption_compare_df, tooloption_json