# PROPRIETARY AND CONFIDENTIAL
#
# This file and its contents are the proprietary property of LGERC HW ATSC 60Hz.
# Unauthorized copying, redistribution, modification, disclosure, or claim of
# ownership is strictly prohibited.
#
# Use of LLMs, AI agents, AI chatbots, or automated code tools to alter,
# redefine, disguise, or claim this source code as another party’s own work is
# prohibited and may result in legal action.
#
# Removal or deletion of this notice, whether intentional or unintentional,
# does not waive any rights and shall be considered a breach of the applicable
# repository license notice.
#
# ALL RIGHTS RESERVED.


from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))



#from streamlit_navigation_bar import st_navbar
import pandas as pd
import time
import requests
import json
import io
import numpy as np
from openpyxl import load_workbook, workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import polars as pl
from pathlib import Path
import os
from dej_sdk import bucket
import tempfile
import re
import polars as pl
import hashlib
from pandas.io.formats.style import Styler
import connectorx

from datetime import datetime
from services.check_sso import SSO_NPDM
from services.main_hwpart import targetpart_compare, developmentpart_compare, initialpart_compare
from services.main_tooloption import run_tooloption, getToolinfo
from services.subs_hwpart import run_subshwpart

from functions.conditioning import zerobom_conditioning
from functions.profile import ModelProfile
from functions.get_latestver import read_table, read_latest_version
from functions.strucFucntions.matchFunctions import (
    contains_keywords_or_any, 
    contains_or_any, 
    partnum_match,
    build_regex_expr
)

#pl.Config.set_tbl_rows(-1)
#pl.Config.set_tbl_cols(-1)
#pl.Config.set_tbl_width_chars(-1)

def get_structure_compare(target_model, bomFrame, ssolgenet_cookie=None, smsession_cookie=None):
    TemplateLinkUrl, GetTemplateFrame, GetTemplate, TemplateID = GoGetTemplate(target_model)
    joined_result_matched, run_info, output_report = match_template_bom(GetTemplateFrame, bomFrame, target_model, TemplateID)
    get_compare_result = check_status(joined_result_matched)
    joined_result_excel, json_data, compare_matching = final_result_compare(get_compare_result, GetTemplateFrame, run_info, output_report)

    result_check = (
        "NG"
        if joined_result_excel.select(pl.col("status").eq("NG").any()).item()
        else "OK"
    )

    return joined_result_excel, json_data, compare_matching, result_check

def normalize_polars_df(df: pl.DataFrame) -> pl.DataFrame:
    """
    Standardizes null-like values across all columns and applies
    Min-Max normalization to numeric columns to scale them into [0, 1].
    """
    # 1. Clean String Nulls: Convert empty strings, whitespace, and literal string "null"/"nan"/"none" to pl.Null
    string_cols = [col for col, dtype in zip(df.columns, df.dtypes) if dtype == pl.Utf8]
    
    if string_cols:
        df = df.with_columns([
            pl.when(
                pl.col(col).str.strip_chars().str.to_lowercase().is_in(["", "null", "nan", "none"])
            )
            .then(None)
            .otherwise(pl.col(col))
            .alias(col)
            for col in string_cols
        ])

    # 2. Clean Float NaN/Inf: Convert floating-point NaN and Inf to native pl.Null
    float_cols = [col for col, dtype in zip(df.columns, df.dtypes) if dtype in (pl.Float32, pl.Float64)]
    
    if float_cols:
        df = df.with_columns([
            pl.when(pl.col(col).is_nan() | pl.col(col).is_infinite())
            .then(None)
            .otherwise(pl.col(col))
            .alias(col)
            for col in float_cols
        ])

    # 3. Min-Max Normalize all numeric columns: (x - min) / (max - min)
    numeric_cols = [col for col, dtype in zip(df.columns, df.dtypes) if dtype.is_numeric()]
    
    normalized_exprs = []
    for col in numeric_cols:
        min_val = pl.col(col).min()
        max_val = pl.col(col).max()
        
        # Guard against division by zero if min == max
        scaled = pl.when(max_val > min_val)\
                   .then((pl.col(col) - min_val) / (max_val - min_val))\
                   .otherwise(0.0)\
                   .alias(col)
        
        normalized_exprs.append(scaled)

    return df.with_columns(normalized_exprs)

def GoGetTemplate(target_model):    #Get By Suffix
 
    profile = ModelProfile(target_model)

    TemplateURL = r"postgres://bom-db-user:zEfETCPR9YaHv46cgke6UjWOQ6uVu1XcTLhfd9iYtD62O3CXUrRCftSyOL7RyTKq@bom-db-0.bom-db.postgres.svc:5432/structure"

    TemplateList = read_table(
        db_uri=TemplateURL,
        table_name="structure"
    )
    TemplateList = TemplateList.with_columns(
        pl.col("Suffix")
        .str.replace_all(r"_",".")
        .str.replace_all(r"/", "|")
    )


    target_suffix = profile.GetSuffixName.upper()

    GetTemplate = TemplateList.with_columns(
        pl.col("Suffix")
        .str.replace_all(r"\(.*?\)", "")
        .str.replace_all(r"\s+", "")
        .str.replace_all(r"_", ".")
        .str.replace_all(r"/", "|")
        .alias("SuffixRegex")
    ).filter(
        pl.struct(["SuffixRegex"]).map_elements(
            lambda x: bool(
                re.fullmatch(
                    x["SuffixRegex"],
                    target_suffix
                )
            ),
            return_dtype=pl.Boolean
        )
    )

    #print("Target Model:", target_model)
    #print("GetSubs:", profile.GetSubs)
    #print("GetSuffixName:", profile.GetSuffixName)

    #print("Rows found:", GetTemplate.height)
    #print(GetTemplate)

    debug_df = TemplateList.with_columns(
        pl.col("Suffix")
        .str.replace_all(r"\(.*?\)", "")
        .str.replace_all(r"\s+", "")
        .str.replace_all(r"_", ".")
        .str.replace_all(r"/", "|")
        .alias("SuffixRegex")
    )

    #print(debug_df.select("Suffix", "SuffixRegex"))

    if GetTemplate.is_empty():
        raise ValueError(
            f"No template found. "
            f"GetSubs={profile.GetSubs}, "
            f"GetSuffixName={profile.GetSuffixName}"
        )

    TemplateLinkUrl = GetTemplate.item(0, "Template")
    TemplateID = {
        "Name": GetTemplate.item(0, "Name"),
        "Header": GetTemplate.item(0, "Header"),
        "Subsidiary": GetTemplate.item(0, "Subsidiary"),
        "Suffix": GetTemplate.item(0, "Suffix"),
        "Version": GetTemplate.item(0, "Version"),
        "Editor": GetTemplate.item(0, "Editor"),
    }

    GetTemplateFrame = read_latest_version(
        db_uri=TemplateLinkUrl
    )

    GetTemplateFrame = GetTemplateFrame.with_columns(
        pl.col("Comp").str.replace_all(" ", "|").str.to_lowercase()
    )
    GetTemplateFrame = GetTemplateFrame.with_columns(
        pl.col("PartNum").str.replace_all(r"^\|+", "")
    )
    GetTemplateFrame = GetTemplateFrame.with_columns(
        pl.col("Uit_Ref").str.replace_all(r"/", "|")
    )

    GetTemplateFrame = GetTemplateFrame.select(pl.exclude(["category", "Description\n(Grouping name)"]))
    GetTemplateFrame = GetTemplateFrame.with_columns(pl.col("Comp").str.replace_all(r"None|Null",""))

    GetTemplateFrame = GetTemplateFrame.with_columns(
        pl.arange(1, pl.len() + 1).alias("id")
    )

    return TemplateLinkUrl, GetTemplateFrame, GetTemplate, TemplateID

def match_template_bom(normalize_template_main: pl.DataFrame, bom_frame, target_model: str, TemplateID):
    profile = ModelProfile(target_model)

    match_result = None

    run_info = {
        "run_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "subsName": profile.GetSubs,
        "setName": TemplateID["Subsidiary"],
        "suffixName": profile.GetSuffixName,
        "subsSuffix": TemplateID["Suffix"],
        "templateHeader": TemplateID["Header"],
        "templateName": TemplateID["Name"],
        "editor": "yudhis.ranggawidjaya",
        "creator": "yudhis.ranggawidjaya",
    }
    
    # Keep only valid template rows - No Dupliation BOM Level and Comp
    normalize_template_individual = (
        normalize_template_main
        .filter(
            pl.col("BOM_Level").is_not_null()
            & (pl.col("BOM_Level").str.strip_chars() != "")
        )
        .unique(subset=["BOM_Level", "Comp", "PartNum"],maintain_order=True,keep="none")
    )

    # processing duplicates based on BOM_Level and Comp
    normalize_template_duplication = (
        normalize_template_main
        .filter(
            pl.col("BOM_Level").is_not_null()
            & (pl.col("BOM_Level").str.strip_chars() != "")
        )
        .filter(
            pl.struct(["BOM_Level", "Comp", "PartNum"]).is_duplicated()
        )
    )

    # Prepare input dataframe - lowercase all part_number
    bom_frame = bom_frame.with_columns([
            pl.col("bomLevel")
            .cast(pl.Int64)
            .alias("bomLevel_int"),

            pl.col("part_number")
            .str.to_lowercase()
            .str.strip_chars()
            .alias("part_number_clean"),

            pl.col("part_descriptions")
            .str.to_lowercase()
            .str.strip_chars()
            .alias("part_descriptions_clean")
        ])   


    # Keep only main BOM rows - DROP ALL UN-NECCESSARY PART
    bom_frame = (
        bom_frame
        .filter(pl.col("dataType") == "B")
        .drop(["changeNo", "revisions", "JobExpl"])
    )

    result_individual = (
        normalize_template_individual.with_columns(
            pl.col("BOM_Level").cast(pl.Int64, strict=False)
        ).join(
            bom_frame,
            left_on="BOM_Level",
            right_on="bomLevel",
            how="inner"
        )
        .filter(
            pl.col("part_number").str.contains(
                build_regex_expr("PartNum"), literal=False
            )
        )
        .filter(    #Parse by part_descriptions
            pl.struct(["desc_ref", "part_descriptions"]).map_elements(
                lambda x: contains_keywords_or_any(x["desc_ref"], x["part_descriptions"]),
                return_dtype=pl.Boolean
            )
        )
        .filter(    ##Parse by part_technicalSpec
            pl.struct(["tech_ref", "part_TechnicalSpec"]).map_elements(
                lambda x: contains_keywords_or_any(x["tech_ref"], x["part_TechnicalSpec"]),
                return_dtype=pl.Boolean
            )
        )
    )

    result_duplication = (
        normalize_template_duplication
            .with_columns(
                pl.col("BOM_Level").cast(pl.Int64, strict=False)
            ).join(
                bom_frame,
                left_on="BOM_Level",
                right_on="bomLevel",
                how="inner"
            )
            .filter(
                pl.struct(["PartNum", "part_number"]).map_elements(
                    lambda x: partnum_match(x["PartNum"], x["part_number"]),
                    return_dtype=pl.Boolean
                )
            )
            .filter(
                pl.struct(["desc_ref", "part_descriptions"]).map_elements(
                    lambda x: contains_keywords_or_any(x["desc_ref"], x["part_descriptions"]),
                    return_dtype=pl.Boolean
                )
            )
            .filter(
                pl.struct(["tech_ref", "part_TechnicalSpec"]).map_elements(
                    lambda x: contains_keywords_or_any(x["tech_ref"], x["part_TechnicalSpec"]),
                    return_dtype=pl.Boolean
                )
            )
    )

    # - Condiitoning Output - #
    joined_result = pl.concat([result_individual, result_duplication]).unique(subset="id")
        
    output_report = {
        "matchingResult": match_result,
        "totalParts": bom_frame.height,
        "partMatch": joined_result.height,
        "duplicatedParts": result_duplication.height,
        "individualParts": result_individual.height
    }
    
    #return joined_result_excel#, full_matchmaking
    return joined_result, run_info, output_report

def build_match_expr(ref_col, part_col, numeric=False):

    if numeric:
        return (
            pl.col(ref_col).cast(pl.Float64, strict=False)
            ==
            pl.col(part_col).cast(pl.Float64, strict=False)
        )

    ref = (
        pl.col(ref_col)
        .cast(pl.String)
        .fill_null("")
        .str.to_uppercase()
        .str.replace_all(r"\s*[|/]\s*", "|")
    )

    part = (
        pl.col(part_col)
        .cast(pl.String)
        .fill_null("")
        .str.to_uppercase()
        .str.strip_chars()
    )

    return (
        ref.str.split("|")
        .list.eval(pl.element().str.strip_chars())
        .list.contains(part)
    )

def check_status(df: pl.DataFrame) -> pl.DataFrame:

    comparisons = [
        ("qty_check", "Qty_Ref", "part_quantity", "Qty", True),
        ("uit_check", "Uit_Ref", "part_UIT", "UIT", False),
        ("supply_check", "Supply Type", "part_supplyType", "Supply", False),
    ]

    yes_checks = []
    or_checks = []
    reason_exprs = []

    for check_col, ref_col, part_col, label, numeric in comparisons:

       
        match_expr = build_match_expr(
            ref_col,
            part_col,
            numeric=numeric
        )


        check_value = (
            pl.col(check_col)
            .fill_null("")
            .str.to_lowercase()
        )

        # YES logic
        yes_checks.append(
            pl.when(check_value == "yes")
            .then(match_expr)
            .otherwise(True)
        )

        # OR logic
        or_checks.append(
            pl.when(check_value == "or")
            .then(match_expr)
            .otherwise(False)
        )

        # Failure reason
        reason_exprs.append(
            pl.when(
                ((check_value == "yes") | (check_value == "or"))
                & (~match_expr)
            )
            .then(pl.lit(label))
            .otherwise(pl.lit(""))
        )

    yes_result = pl.all_horizontal(yes_checks)

    has_or = pl.any_horizontal([
        pl.col(c).fill_null("").str.to_lowercase() == "or"
        for c in ["qty_check", "uit_check", "supply_check"]
    ])

    or_result = pl.any_horizontal(or_checks)

    final_result = (
        pl.when(has_or)
        .then(yes_result & or_result)
        .otherwise(yes_result)
    )

    return (
        df.with_columns([
            pl.when(final_result)
            .then(pl.lit("OK"))
            .otherwise(pl.lit("NG"))
            .alias("status"),

            pl.concat_str(reason_exprs, separator=", ")
            .str.replace_all(r"(,\s*)+", ", ")
            .str.strip_chars(", ")
            .alias("reason")
        ])
    )
    
def final_result_compare(get_compare_result, normalize_template_main, run_info, output_report):
    joined_result_excel = normalize_template_main.join(get_compare_result, on=["id", "PartNum"], how="left")

    joined_result_excel = joined_result_excel.with_columns(
        pl.lit("").alias("remarks")
    )

    #print(joined_result_excel.columns)
    joined_result_excel = joined_result_excel.drop(['BOM_Level_right', 'Comp_right', 'Qty_Ref_right', 'Uit_Ref_right', 'Supply Type_right', 'desc_ref_right', 'tech_ref_right', 'partno_check_right', 'qty_check_right', 'uit_check_right', 'supply_check_right', 'special-case_right', 'check_num_right', 'series_only_right', 'series_exception_right', 'suffix_only_right', 'suffix_exception_right', 'exception_result_right'
    ])
    
    json_matchmaking = joined_result_excel.to_dicts()
    #json_data = json.dumps(json_matchmaking, indent=4, ensure_ascii=False)
    
    compare_matching = {
        "run_info": run_info,
        "compareData": json_matchmaking,
        "compareReport": output_report
    }
    
    
    return joined_result_excel, json_matchmaking, compare_matching
    




