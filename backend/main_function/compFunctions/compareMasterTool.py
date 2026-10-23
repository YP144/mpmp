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

from services.check_sso import SSO_NPDM, NpdmClient
from functions.conditioning import zerobom_conditioning
from functions.tool_option_logic import GetModelToolOptionMaster, ToolOptionCross
from services.main_tooloption import run_tooloption, getToolinfo
from services.subs_hwpart import run_subshwpart
from compFunctions.check_parts import GetTargetParts

from functions.profile import ModelProfile, GetOperationPart
from functions.substate import GoGetTemplate, GetParseStructure, StructureCheck
from services.main_hwpart import targetpart_compare, developmentpart_compare, initialpart_compare
from functions.tool_option_logic import getToolinfo

def compare_tool_option_summary(BOMframe, target_model):

    #BOMtarget, BOMname = zerobom_conditioning(BOMframe)

    ebt_tool_option = ToolOptionCross(BOMframe).rename({"settings": "mp_settings"})
    master_tool_option  = GetModelToolOptionMaster(target_model)

    ebt_tool_option = pl.DataFrame(ebt_tool_option)
    master_tool_option = pl.DataFrame(master_tool_option)

    #compared_tool_option = ebt_tool_option.join(master_tool_option, on)

    """ebt_tool_json = json.dumps(
        ebt_tool_option.to_dicts(),
        ensure_ascii=False,
        indent=4
    )"""

    ebt_tool_json = ebt_tool_option


    return ebt_tool_option, master_tool_option, ebt_tool_json


#input must be a dataframe
def compare_tool_option_list(tool_option: pl.DataFrame):
    
    """tool1 = 
    tool2
    tool3
    tool4
    tool6
    boardoption    

    tool_option_result = getToolinfo()"""

    return





