import polars as pl
import pandas as pd

from functions.structureCompare import GoGetTemplate, GetParseStructure, StructureCheck
from functions.conditioning import zerobom_conditioning

TargetBOM = "./backend/main_function/json/0_target_ebom.json"

def get_structure_result(target_model):
    BOMframe, model_name = zerobom_conditioning(TargetBOM)
    
    TemplateLinkUrl, GetTemplateFrame, GetTemplate = GoGetTemplate(target_model)
    
    FullStructure, GetReport, getResultRow = GetParseStructure(BOMframe, model_name, GetTemplateFrame)

    return BOMframe, FullStructure






