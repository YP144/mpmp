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
import hashlib
from pandas.io.formats.style import Styler
import connectorx

from main_function.services.check_sso import SSO_NPDM
from main_function.services.main_hwpart import targetpart_compare, developmentpart_compare, initialpart_compare
from main_function.services.main_tooloption import run_tooloption, getToolinfo
from main_function.services.subs_hwpart import run_subshwpart

from main_function.functions.profile import ModelProfile
from main_function.functions.get_latestver import read_table, read_latest_version

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

    GetTemplate = TemplateList.with_columns(
        pl.col("Suffix")
        .cast(pl.Utf8)
        .str.replace_all(r"\s+", "")
        .alias("SuffixRegex")
    ).filter(
        (pl.col("Header").str.contains(profile.GetSubs)) &
        (
            pl.lit(profile.GetSuffixName.upper())
            .str.contains("^(" + pl.col("SuffixRegex") + ")$")
        )
    )

    TemplateLinkUrl = GetTemplate.item(0, "Template")

    GetTemplateFrame = read_latest_version(
        db_uri=TemplateLinkUrl
    )

    GetTemplateFrame = GetTemplateFrame.drop(["Criteria", "Mother Part"])

    

    return TemplateLinkUrl, GetTemplateFrame, GetTemplate

def GetParseStructure(GetTarget, GetModelName, INCKDframe):

    modelName = GetModelName
    GetTarget = GetTarget.filter(
        pl.col("dataType") == "B"
    )
    GetTarget_lazy = GetTarget.lazy()  # Convert to lazy once

    INCKDframe = INCKDframe.with_row_index(name="row_number", offset=0)
    #Drop None BomLevel Rows

    INCKDframe = INCKDframe.with_columns(pl.col("Comp").fill_null(""))

    checkProfile = ModelProfile(modelName)

    # ============= LAZY FUNCTIONS =============

    def CheckLvl_PN_Desc_Lazy(rownum, TemplateSubsidiary, TargeModelBOM_lazy):
        if TemplateSubsidiary[rownum, "BOM_Level"] in ("", None):
            return TargeModelBOM_lazy.filter(pl.lit(False))
        
        filtered = TargeModelBOM_lazy.filter(
            (pl.col("part_number").str.contains(rf"^{TemplateSubsidiary[rownum, 'PartNum']}")) &
            (pl.col("bomLevel") == int(f"{TemplateSubsidiary[rownum, 'BOM_Level']}")) &
            (pl.col("part_descriptions").str.contains(f"{TemplateSubsidiary[rownum, 'Comp']}")) &
            (pl.col("dataType") == "B")
        )
        
        # ✅ ADD THESE 3 LINES:
        return filtered.with_columns([
            pl.lit(TemplateSubsidiary[rownum, "PartNum"]).alias("PartNum"),
            pl.lit(TemplateSubsidiary[rownum, "Comp"]).alias("Comp"),
            pl.lit(TemplateSubsidiary[rownum, "row_number"]).alias("row_number"),
        ]).limit(1)

    def CheckLvl_PN_DescSpecCase_Lazy(rownum, addDesc: str, TecSpec: str, TemplateSubsidiary, TargeModelBOM_lazy):
        if TemplateSubsidiary[rownum, "BOM_Level"] in ("", None):
            return TargeModelBOM_lazy.filter(pl.lit(False))
        
        filtered = TargeModelBOM_lazy.filter(
            (pl.col("part_number").str.contains(rf"^{TemplateSubsidiary[rownum, 'PartNum']}")) &
            (pl.col("part_descriptions").str.contains(rf"{addDesc}")) &
            (pl.col("bomLevel") == int(f"{TemplateSubsidiary[rownum, 'BOM_Level']}")) &
            (pl.col("part_TechnicalSpec").str.contains(rf"{TecSpec}"))
        )
        
        # ✅ ADD THESE 3 LINES:
        return filtered.with_columns([
            pl.lit(TemplateSubsidiary[rownum, "PartNum"]).alias("PartNum"),
            pl.lit(TemplateSubsidiary[rownum, "Comp"]).alias("Comp"),
            pl.lit(TemplateSubsidiary[rownum, "row_number"]).alias("row_number"),
        ]).limit(1)

    def CheckLvl_PN_Desc_LazyNoLimit(rownum, TemplateSubsidiary, TargeModelBOM_lazy):
        if TemplateSubsidiary[rownum, "BOM_Level"] in ("", None):
            return TargeModelBOM_lazy.filter(pl.lit(False))
        
        filtered = TargeModelBOM_lazy.filter(
            (pl.col("part_number").str.contains(rf"^{TemplateSubsidiary[rownum, 'PartNum']}")) &
            (pl.col("bomLevel") == int(f"{TemplateSubsidiary[rownum, 'BOM_Level']}")) &
            (pl.col("part_descriptions").str.contains(f"{TemplateSubsidiary[rownum, 'Comp']}")) &
            (pl.col("dataType") == "B")
        )
        
        # ✅ ADD THESE 3 LINES:
        return filtered.with_columns([
            pl.lit(TemplateSubsidiary[rownum, "PartNum"]).alias("PartNum"),
            pl.lit(TemplateSubsidiary[rownum, "Comp"]).alias("Comp"),
            pl.lit(TemplateSubsidiary[rownum, "row_number"]).alias("row_number"),
        ])

    def CheckLvl_PN_DescSpecCase_LazyNoLimit(rownum, addDesc: str, TecSpec: str, TemplateSubsidiary, TargeModelBOM_lazy):
        if TemplateSubsidiary[rownum, "BOM_Level"] in ("", None):
            return TargeModelBOM_lazy.filter(pl.lit(False))
        
        filtered = TargeModelBOM_lazy.filter(
            (pl.col("part_number").str.contains(rf"^{TemplateSubsidiary[rownum, 'PartNum']}")) &
            (pl.col("part_descriptions").str.contains(rf"{addDesc}")) &
            (pl.col("bomLevel") == int(f"{TemplateSubsidiary[rownum, 'BOM_Level']}")) &
            (pl.col("part_TechnicalSpec").str.contains(rf"{TecSpec}"))
        )
        
        # ✅ ADD THESE 3 LINES:
        return filtered.with_columns([
            pl.lit(TemplateSubsidiary[rownum, "PartNum"]).alias("PartNum"),
            pl.lit(TemplateSubsidiary[rownum, "Comp"]).alias("Comp"),
            pl.lit(TemplateSubsidiary[rownum, "row_number"]).alias("row_number"),
        ])


    # ============= BUILD ALL LAZY QUERIES (NOT EXECUTED YET) =============

    lazy_queries = {
        "Remote": CheckLvl_PN_Desc_Lazy(2, INCKDframe, GetTarget_lazy),
        "Battery": CheckLvl_PN_Desc_Lazy(1, INCKDframe, GetTarget_lazy),
        "ACC": CheckLvl_PN_DescSpecCase_Lazy(0, "accessory", ".", INCKDframe, GetTarget_lazy),
        "DetachPowerCord_Acc": CheckLvl_PN_Desc_Lazy(3, INCKDframe, GetTarget_lazy),
        "IRblaster": CheckLvl_PN_Desc_Lazy(4, INCKDframe, GetTarget_lazy),
        "LCDAssy": CheckLvl_PN_Desc_Lazy(5, INCKDframe, GetTarget_lazy),
        "IRwifiAssy_LCD": CheckLvl_PN_Desc_Lazy(7, INCKDframe, GetTarget_lazy),
        "IRwifiCable_LCD": CheckLvl_PN_Desc_Lazy(8, INCKDframe, GetTarget_lazy),
        "WiFi_LCD": CheckLvl_PN_Desc_Lazy(9, INCKDframe, GetTarget_lazy),
        "IR_LCD": CheckLvl_PN_Desc_Lazy(10, INCKDframe, GetTarget_lazy),
        "MaintoModuleCable0_LCD": CheckLvl_PN_Desc_Lazy(11, INCKDframe, GetTarget_lazy),
        "MaintoModuleCable1_LCD": CheckLvl_PN_Desc_Lazy(12, INCKDframe, GetTarget_lazy),
        "MaintoPowerCable_LCD": CheckLvl_PN_Desc_Lazy(13, INCKDframe, GetTarget_lazy),
        "Gasket_LCD": CheckLvl_PN_Desc_Lazy(14, INCKDframe, GetTarget_lazy),
        "SubBoard": CheckLvl_PN_DescSpecCase_Lazy(15, ".", checkProfile.GetSeries.lower(), INCKDframe, GetTarget_lazy),
        "IRwifiAssy_SubBoard": CheckLvl_PN_Desc_Lazy(16, INCKDframe, GetTarget_lazy),
        "IRwifiCable_SubBoard": CheckLvl_PN_Desc_Lazy(17, INCKDframe, GetTarget_lazy),
        "WiFi_SubBoard": CheckLvl_PN_DescSpecCase_Lazy(18, "wifi", ".", INCKDframe, GetTarget_lazy),
        "IR_SubBoard": CheckLvl_PN_Desc_Lazy(19, INCKDframe, GetTarget_lazy),
        "AttachedCord_SubBoard": CheckLvl_PN_Desc_Lazy(20, INCKDframe, GetTarget_lazy),
        "OLED": CheckLvl_PN_Desc_Lazy(21, INCKDframe, GetTarget_lazy),
        "SPKCable_MainSPK": CheckLvl_PN_DescSpecCase_Lazy(26, "speaker", ".", INCKDframe, GetTarget_lazy),
        "Cable_MainPower": CheckLvl_PN_Desc_Lazy(27, INCKDframe, GetTarget_lazy),
        "PowerCord_MainDettach": CheckLvl_PN_Desc_Lazy(28, INCKDframe, GetTarget_lazy),
        "PowerCordAssy_MainDettach": CheckLvl_PN_Desc_Lazy(29, INCKDframe, GetTarget_lazy),
        "PowerCord_SecDettach": CheckLvl_PN_Desc_Lazy(30, INCKDframe, GetTarget_lazy),
        "Slabel_MainDettach": CheckLvl_PN_Desc_Lazy(31, INCKDframe, GetTarget_lazy),
        "PowerCordAssy_MainAttach": CheckLvl_PN_Desc_Lazy(32, INCKDframe, GetTarget_lazy),
        "PowerCord_SecAttach": CheckLvl_PN_Desc_Lazy(33, INCKDframe, GetTarget_lazy),
        "Slabel_MainAttach": CheckLvl_PN_Desc_Lazy(34, INCKDframe, GetTarget_lazy),
        "mainEBT_ChassisAssy": CheckLvl_PN_DescSpecCase_Lazy(35, ".", "main", INCKDframe, GetTarget_lazy),
        "TransTp_ChassisAssy": CheckLvl_PN_Desc_Lazy(36, INCKDframe, GetTarget_lazy),
        "Label_ChassisAssy": CheckLvl_PN_Desc_Lazy(37, INCKDframe, GetTarget_lazy),
        "Ribbon_ChassisAssy": CheckLvl_PN_Desc_Lazy(38, INCKDframe, GetTarget_lazy),
        "CableSPK_ChassisAssy": CheckLvl_PN_Desc_Lazy(41, INCKDframe, GetTarget_lazy),
        "CablePower_ChassisAssy": CheckLvl_PN_Desc_Lazy(42, INCKDframe, GetTarget_lazy),
        "CoverPlate_ChassisAssy0": CheckLvl_PN_DescSpecCase_Lazy(43, ".", ".", INCKDframe, GetTarget_lazy),
        "SubEBT_ChassisAssy": CheckLvl_PN_Desc_Lazy(44, INCKDframe, GetTarget_lazy),
        "Tuner_ChassisAssy": CheckLvl_PN_Desc_Lazy(45, INCKDframe, GetTarget_lazy),
        "skdEBR_ChassisAssy": CheckLvl_PN_Desc_Lazy(49, INCKDframe, GetTarget_lazy),
        "skdEBRPackage_ChassisAssy": CheckLvl_PN_Desc_Lazy(50, INCKDframe, GetTarget_lazy),
        "mainEBU_ChassisAssy": CheckLvl_PN_DescSpecCase_Lazy(51, ".", ".", INCKDframe, GetTarget_lazy),
        "Label3ChassisAssy": CheckLvl_PN_Desc_Lazy(52, INCKDframe, GetTarget_lazy),
        "Ribbon3ChassisAssy": CheckLvl_PN_Desc_Lazy(53, INCKDframe, GetTarget_lazy),
        "CableSPKAssy_ChassisAssy": CheckLvl_PN_Desc_Lazy(54, INCKDframe, GetTarget_lazy),
        "CablePowerMain_ChassisAssy": CheckLvl_PN_Desc_Lazy(55, INCKDframe, GetTarget_lazy),
        "MainEBR_ChassisAssy": CheckLvl_PN_DescSpecCase_Lazy(56, "orp", "m.i", INCKDframe, GetTarget_lazy),
        "CoverPlate1_ChassisAssy": CheckLvl_PN_Desc_Lazy(57, INCKDframe, GetTarget_lazy),
        "MainSub0_ChassisAssy": CheckLvl_PN_Desc_Lazy(58, INCKDframe, GetTarget_lazy),
        "MainSub1_ChassisAssy": CheckLvl_PN_Desc_Lazy(59, INCKDframe, GetTarget_lazy),
        "EDID_ChassisAssy": CheckLvl_PN_DescSpecCase_Lazy(60, "edid", ".", INCKDframe, GetTarget_lazy),
        "Gasket_ChassisAssy": CheckLvl_PN_Desc_Lazy(61, INCKDframe, GetTarget_lazy),
        "HeatPad_ChassisAssy": CheckLvl_PN_Desc_Lazy(62, INCKDframe, GetTarget_lazy),
        "PCBScrew_ChassisAssy": CheckLvl_PN_Desc_Lazy(63, INCKDframe, GetTarget_lazy),
        "SVCmain_SVC": CheckLvl_PN_DescSpecCase_Lazy(64, "orp", ".", INCKDframe, GetTarget_lazy),
        "SVCmainRBR_SVC": CheckLvl_PN_DescSpecCase_Lazy(65, "orp", ".", INCKDframe, GetTarget_lazy),
        "Tape_SVC": CheckLvl_PN_Desc_Lazy(66, INCKDframe, GetTarget_lazy),
        "MainFFC": CheckLvl_PN_Desc_LazyNoLimit(24, INCKDframe, GetTarget_lazy),
        "MainSpeaker": CheckLvl_PN_Desc_LazyNoLimit(22, INCKDframe, GetTarget_lazy),
    }

    print(f"Built {len(lazy_queries)} lazy queries...")

    # ============= EXECUTE ALL QUERIES AT ONCE =============
    collected_results = pl.collect_all(list(lazy_queries.values()))

    # Map results back to names
    results = {name: df for name, df in zip(lazy_queries.keys(), collected_results)}

    # ============= POST-PROCESS RESULTS =============

    def safe_get_values(df, *cols):
        """Safely extract values from dataframe, return empty string if not found"""
        if df.height == 0:
            return [""] * len(cols)
        return [df[0, col] if col in df.columns else "" for col in cols]

    RemoteRow = results["Remote"]
    RemotePN, RemoteQty = safe_get_values(RemoteRow, "part_number", "part_quantity")

    BatteryRow = results["Battery"]
    BatteryPN, BatteryQty = safe_get_values(BatteryRow, "part_number", "part_quantity")

    ACCrow = results["ACC"]
    GetACC, GetACCQty = safe_get_values(ACCrow, "part_number", "part_quantity")

    GetDetachPowerCord_Acc = results["DetachPowerCord_Acc"]
    GetDetachPowerCord_AccPN, GetDetachPowerCord_AccQty = safe_get_values(GetDetachPowerCord_Acc, "part_number", "part_quantity")

    GetIRblasterRow = results["IRblaster"]
    GetIRblasterRow_PN, GetIRblasterRowQty = safe_get_values(GetIRblasterRow, "part_number", "part_quantity")

    GetLCDAssyRow = results["LCDAssy"]
    GetLCDAssyRowPN, GetLCDAssyRowQty = safe_get_values(GetLCDAssyRow, "part_number", "part_quantity")

    GetIRwifiAssy_LCD = results["IRwifiAssy_LCD"]
    GetIRwifiAssy_LCDPN, GetIRwifiAssy_LCDQty = safe_get_values(GetIRwifiAssy_LCD, "part_number", "part_quantity")

    GetIRwifiCable_LCD = results["IRwifiCable_LCD"]
    GetIRwifiCable_LCDPN, GetIRwifiCable_LCDQty = safe_get_values(GetIRwifiCable_LCD, "part_number", "part_quantity")

    GetWiFi_LCD = results["WiFi_LCD"]
    GetWiFi_LCDPN, GetWiFi_LCDQty = safe_get_values(GetWiFi_LCD, "part_number", "part_quantity")

    GetIR_LCD = results["IR_LCD"]
    GetIR_LCDPN, GetIR_LCDQty = safe_get_values(GetIR_LCD, "part_number", "part_quantity")

    MaintoModuleCable0_LCD = results["MaintoModuleCable0_LCD"]
    MaintoModuleCable0_LCDPN, MaintoModuleCable0_LCDQty = safe_get_values(MaintoModuleCable0_LCD, "part_number", "part_quantity")

    MaintoModuleCable1_LCD = results["MaintoModuleCable1_LCD"]
    MaintoModuleCable1_LCDPN, MaintoModuleCable1_LCDQty = safe_get_values(MaintoModuleCable1_LCD, "part_number", "part_quantity")

    MaintoPowerCable_LCD = results["MaintoPowerCable_LCD"]
    MaintoPowerCable_LCDPN, MaintoPowerCable_LCDQty = safe_get_values(MaintoPowerCable_LCD, "part_number", "part_quantity")

    Gasket_LCD = results["Gasket_LCD"]
    Gasket_LCDPN, Gasket_LCDQty = safe_get_values(Gasket_LCD, "part_number", "part_quantity")

    SubBoard_SubBoard = results["SubBoard"]
    SubBoard_SubBoardPN, SubBoard_SubBoardQty = safe_get_values(SubBoard_SubBoard, "part_number", "part_quantity")

    GetIRwifiAssy_SubBoard = results["IRwifiAssy_SubBoard"]
    GetIRwifiAssy_SubBoardPN, GetIRwifiAssy_SubBoardQty = safe_get_values(GetIRwifiAssy_SubBoard, "part_number", "part_quantity")

    GetIRwifiCable_SubBoard = results["IRwifiCable_SubBoard"]
    GetIRwifiCable_SubBoardPN, GetIRwifiCable_SubBoardQty = safe_get_values(GetIRwifiCable_SubBoard, "part_number", "part_quantity")

    GetWiFi_SubBoard = results["WiFi_SubBoard"]
    GetWiFi_SubBoardPN, GetWiFi_SubBoardQty = safe_get_values(GetWiFi_SubBoard, "part_number", "part_quantity")

    GetIR_SubBoard = results["IR_SubBoard"]
    GetIR_SubBoardPN, GetIR_SubBoardQty = safe_get_values(GetIR_SubBoard, "part_number", "part_quantity")

    GetAttachedCord_SubBoard = results["AttachedCord_SubBoard"]
    GetAttachedCord_SubBoardPN, GetAttachedCord_SubBoardQty = safe_get_values(GetAttachedCord_SubBoard, "part_number", "part_quantity")

    GetOLED_OLED = results["OLED"]
    GetOLED_OLEDPN, GetOLED_OLEDQty = safe_get_values(GetOLED_OLED, "part_number", "part_quantity")

    GetSPKCable_MainSPK = results["SPKCable_MainSPK"]
    GetSPKCable_MainSPKPN, GetSPKCable_MainSPKQty = safe_get_values(GetSPKCable_MainSPK, "part_number", "part_quantity")

    GetCable_MainPower = results["Cable_MainPower"]
    GetCable_MainPowerPN, GetCable_MainPowerQty = safe_get_values(GetCable_MainPower, "part_number", "part_quantity")

    GetPowerCord_MainDettach = results["PowerCord_MainDettach"]
    GetPowerCord_MainDettachPN, GetPowerCord_MainDettachQty = safe_get_values(GetPowerCord_MainDettach, "part_number", "part_quantity")

    GetPowerCordAssy_MainDettach = results["PowerCordAssy_MainDettach"]
    GetPowerCordAssy_MainDettachPN, GetPowerCordAssy_MainDettachQty = safe_get_values(GetPowerCordAssy_MainDettach, "part_number", "part_quantity")

    GetPowerCord_SecDettach = results["PowerCord_SecDettach"]
    GetPowerCord_SecDettachPN, GetPowerCord_SecDettachQty = safe_get_values(GetPowerCord_SecDettach, "part_number", "part_quantity")

    Slabel_MainDettach = results["Slabel_MainDettach"]
    Slabel_MainDettachPN, Slabel_MainDettachQty = safe_get_values(Slabel_MainDettach, "part_number", "part_quantity")

    GetPowerCordAssy_MainAttach = results["PowerCordAssy_MainAttach"]
    GetPowerCordAssy_MainAttachPN, GetPowerCordAssy_MainAttachQty = safe_get_values(GetPowerCordAssy_MainAttach, "part_number", "part_quantity")

    GetPowerCord_SecAttach = results["PowerCord_SecAttach"]
    GetPowerCord_SecAttachPN, GetPowerCord_SecAttachQty = safe_get_values(GetPowerCord_SecAttach, "part_number", "part_quantity")

    Slabel_MainAttach = results["Slabel_MainAttach"]
    Slabel_MainAttachPN, Slabel_MainAttachQty = safe_get_values(Slabel_MainAttach, "part_number", "part_quantity")

    mainEBT_ChassisAssy = results["mainEBT_ChassisAssy"]
    mainEBT_ChassisAssyPN, mainEBT_ChassisAssyAty = safe_get_values(mainEBT_ChassisAssy, "part_number", "part_quantity")

    TransTp_ChassisAssy = results["TransTp_ChassisAssy"]
    TransTp_ChassisAssyPN, TransTp_ChassisAssyQty = safe_get_values(TransTp_ChassisAssy, "part_number", "part_quantity")

    Label_ChassisAssy = results["Label_ChassisAssy"]
    Label_ChassisAssyPN, Label_ChassisAssyQty = safe_get_values(Label_ChassisAssy, "part_number", "part_quantity")

    Ribbon_ChassisAssy = results["Ribbon_ChassisAssy"]
    Ribbon_ChassisAssyPN, Ribbon_ChassisAssyQty = safe_get_values(Ribbon_ChassisAssy, "part_number", "part_quantity")

    CableSPK_ChassisAssy = results["CableSPK_ChassisAssy"]
    CableSPK_ChassisAssyPN, CableSPK_ChassisAssyQty = safe_get_values(CableSPK_ChassisAssy, "part_number", "part_quantity")

    CablePower_ChassisAssy = results["CablePower_ChassisAssy"]
    CablePower_ChassisAssyPN, CablePower_ChassisAssyQty = safe_get_values(CablePower_ChassisAssy, "part_number", "part_quantity")

    CoverPlate_ChassisAssy0 = results["CoverPlate_ChassisAssy0"]
    CoverPlate_ChassisAssy0PN, CoverPlate_ChassisAssy0Qty = safe_get_values(CoverPlate_ChassisAssy0, "part_number", "part_quantity")

    SubEBT_ChassisAssy = results["SubEBT_ChassisAssy"]
    SubEBT_ChassisAssyPN, SubEBT_ChassisAssyQty = safe_get_values(SubEBT_ChassisAssy, "part_number", "part_quantity")

    Tuner_ChassisAssy = results["Tuner_ChassisAssy"]
    Tuner_ChassisAssyPN, Tuner_ChassisAssyQty = safe_get_values(Tuner_ChassisAssy, "part_number", "part_quantity")

    skdEBR_ChassisAssy = results["skdEBR_ChassisAssy"]
    skdEBR_ChassisAssyPN, skdEBR_ChassisAssyQty = safe_get_values(skdEBR_ChassisAssy, "part_number", "part_quantity")

    skdEBRPackage_ChassisAssy = results["skdEBRPackage_ChassisAssy"]
    skdEBRPackage_ChassisAssyPN, skdEBRPackage_ChassisAssyQty = safe_get_values(skdEBRPackage_ChassisAssy, "part_number", "part_quantity")

    mainEBU_ChassisAssy = results["mainEBU_ChassisAssy"]
    mainEBU_ChassisAssyPN, mainEBU_ChassisAssyQty = safe_get_values(mainEBU_ChassisAssy, "part_number", "part_quantity")

    Label3ChassisAssy = results["Label3ChassisAssy"]
    Label3ChassisAssyPN, Label3ChassisAssyQty = safe_get_values(Label3ChassisAssy, "part_number", "part_quantity")

    Ribbon3ChassisAssy = results["Ribbon3ChassisAssy"]
    Ribbon3ChassisAssyPN, Ribbon3ChassisAssyQty = safe_get_values(Ribbon3ChassisAssy, "part_number", "part_quantity")

    CableSPKAssy_ChassisAssy = results["CableSPKAssy_ChassisAssy"]
    CableSPKAssy_ChassisAssyPN, CableSPKAssy_ChassisAssyQty = safe_get_values(CableSPKAssy_ChassisAssy, "part_number", "part_quantity")

    CablePowerMain_ChassisAssy = results["CablePowerMain_ChassisAssy"]
    CablePowerMain_ChassisAssyPN, CablePowerMain_ChassisAssyQty = safe_get_values(CablePowerMain_ChassisAssy, "part_number", "part_quantity")

    MainEBR_ChassisAssy = results["MainEBR_ChassisAssy"]
    MainEBR_ChassisAssyPN, MainEBR_ChassisAssyQty = safe_get_values(MainEBR_ChassisAssy, "part_number", "part_quantity")

    CoverPlate1_ChassisAssy = results["CoverPlate1_ChassisAssy"]
    CoverPlate1_ChassisAssyPN, CoverPlate1_ChassisAssyQty = safe_get_values(CoverPlate1_ChassisAssy, "part_number", "part_quantity")

    MainSub0_ChassisAssy = results["MainSub0_ChassisAssy"]
    MainSub0_ChassisAssyPN, MainSub0_ChassisAssyQty = safe_get_values(MainSub0_ChassisAssy, "part_number", "part_quantity")

    MainSub1_ChassisAssy = results["MainSub1_ChassisAssy"]
    MainSub1_ChassisAssyPN, MainSub1_ChassisAssyQty = safe_get_values(MainSub1_ChassisAssy, "part_number", "part_quantity")

    EDID_ChassisAssy = results["EDID_ChassisAssy"]
    EDID_ChassisAssyPN, EDID_ChassisAssyQty = safe_get_values(EDID_ChassisAssy, "part_number", "part_quantity")

    Gasket_ChassisAssy = results["Gasket_ChassisAssy"]
    Gasket_ChassisAssyPN, Gasket_ChassisAssyQty = safe_get_values(Gasket_ChassisAssy, "part_number", "part_quantity")

    HeatPad_ChassisAssy = results["HeatPad_ChassisAssy"]
    HeatPad_ChassisAssyPN, HeatPad_ChassisAssyQty = safe_get_values(HeatPad_ChassisAssy, "part_number", "part_quantity")

    PCBScrew_ChassisAssy = results["PCBScrew_ChassisAssy"]
    PCBScrew_ChassisAssyPN, PCBScrew_ChassisAssyQty = safe_get_values(PCBScrew_ChassisAssy, "part_number", "part_quantity")

    SVCmain_SVC = results["SVCmain_SVC"]
    SVCmain_SVCPN, SVCmain_SVCQty = safe_get_values(SVCmain_SVC, "part_number", "part_quantity")

    SVCmainRBR_SVC = results["SVCmainRBR_SVC"]
    SVCmainRBR_SVCPN, SVCmainRBR_SVCQty = safe_get_values(SVCmainRBR_SVC, "part_number", "part_quantity")

    Tape_SVC = results["Tape_SVC"]
    Tape_SVCPN, Tape_SVCQty = safe_get_values(Tape_SVC, "part_number", "part_quantity")

    MainFFC = results["MainFFC"]
    MainFFC_PN, MainFFC_Qty = safe_get_values(MainFFC, "part_number", "part_quantity")

    MainSpeaker = results["MainSpeaker"]
    MainSpeaker_PN, MainSpeaker_Qty = safe_get_values(MainSpeaker, "part_number", "part_quantity")

    # ============= HANDLE FFC & SPEAKER SPLITS =============

    if MainFFC.height < 2:
        MainFFC0 = MainFFC
        MainFFC1 = None
    else:
        print("Model Have 2 FFC")
        MainFFC0 = MainFFC.slice(0, 1).with_columns([
            pl.lit(INCKDframe[24, "row_number"]).alias("row_number"),
            pl.lit(INCKDframe[24, "PartNum"]).alias("PartNum"),
            pl.lit(INCKDframe[24, "BOM_Level"]).alias("BOM_Level"),
        ])
        MainFFC1 = MainFFC.slice(1, 1).with_columns([
            pl.lit(INCKDframe[25, "row_number"]).alias("row_number"),
            pl.lit(INCKDframe[25, "PartNum"]).alias("PartNum"),
            pl.lit(INCKDframe[25, "BOM_Level"]).alias("BOM_Level"),
            pl.lit(INCKDframe[25, "Comp"]).alias("Comp"),
        ])

    
    if MainSpeaker.height < 2:
        MainSpeaker0 = MainSpeaker
        MainSpeaker1 = None
    else:
        print("Model Have 2 Speaker")
        MainSpeaker0 = MainSpeaker.slice(0, 1).with_columns([
            pl.lit(INCKDframe[22, "row_number"]).alias("row_number"),
            pl.lit(INCKDframe[22, "PartNum"]).alias("PartNum"),
            pl.lit(INCKDframe[22, "BOM_Level"]).alias("BOM_Level"),
            pl.lit(INCKDframe[22, "Comp"]).alias("Comp"),
        ])
        MainSpeaker1 = MainSpeaker.slice(1, 1).with_columns([
            pl.lit(INCKDframe[23, "row_number"]).alias("row_number"),
            pl.lit(INCKDframe[23, "PartNum"]).alias("PartNum"),
            pl.lit(INCKDframe[23, "BOM_Level"]).alias("BOM_Level"),
            pl.lit(INCKDframe[23, "Comp"]).alias("Comp"),
        ])

    # ============= CONCAT ALL FRAMES =============

    frames = [
        RemoteRow, BatteryRow, ACCrow, GetDetachPowerCord_Acc, GetWiFi_LCD, GetIR_LCD, MaintoModuleCable1_LCD, MaintoModuleCable0_LCD, 
        MaintoPowerCable_LCD, Gasket_LCD, GetIRblasterRow, GetLCDAssyRow,
        GetIRwifiAssy_LCD, GetIRwifiCable_LCD, 
        SubBoard_SubBoard, GetIRwifiAssy_SubBoard, GetIRwifiCable_SubBoard, 
        GetWiFi_SubBoard, GetIR_SubBoard, GetAttachedCord_SubBoard, 
        GetOLED_OLED,
        GetSPKCable_MainSPK, 
        GetCable_MainPower, 
        GetPowerCord_MainDettach, 
        GetPowerCordAssy_MainDettach, GetPowerCord_SecDettach, Slabel_MainDettach, 
        GetPowerCordAssy_MainAttach, GetPowerCord_SecAttach, Slabel_MainAttach,
        TransTp_ChassisAssy,
        CableSPK_ChassisAssy, 
        CablePower_ChassisAssy, SubEBT_ChassisAssy, 
        Tuner_ChassisAssy, skdEBR_ChassisAssy, skdEBRPackage_ChassisAssy, 
        Label3ChassisAssy, Ribbon3ChassisAssy, 
        CableSPKAssy_ChassisAssy, CablePowerMain_ChassisAssy, MainEBR_ChassisAssy, 
        CoverPlate1_ChassisAssy, MainSub0_ChassisAssy, MainSub1_ChassisAssy, 
        EDID_ChassisAssy, HeatPad_ChassisAssy, 
        PCBScrew_ChassisAssy,
        mainEBU_ChassisAssy, mainEBT_ChassisAssy,
        SVCmain_SVC, SVCmainRBR_SVC, Tape_SVC, MainFFC1, MainFFC0, CoverPlate_ChassisAssy0, MainSpeaker0, MainSpeaker1
    ]

    frames = [df for df in frames if df is not None]
    getResultRow = pl.concat(frames, how="diagonal_relaxed")

    FullStructure = INCKDframe.join(getResultRow, on=["row_number", "PartNum", "Comp"], how="left")
    FinalReport = ""

    if INCKDframe.height < FullStructure.height:
        FinalReport = "NG"
    elif INCKDframe.height == FullStructure.height:
        FinalReport = "OK"
        
    GetBOMLevelonly = INCKDframe.filter(
        pl.col("BOM_Level").str.strip_chars().is_not_null() &
        (pl.col("BOM_Level").str.strip_chars() != "")
    ).drop([
        "Qty_Ref", "Uit_Ref", "Supply Type"
    ])

    GetBOMLevelwithPart = FullStructure.filter(
        pl.col("part_number").str.strip_chars().is_not_null() &
        (pl.col("part_number").str.strip_chars() != "")
    )
    StructureReport = {
        "ModelName": GetModelName,
        "ModelSeries": checkProfile.GetSeries.lower(),
        "StructureCheck" : {
            "Total Row": INCKDframe.height,
            "Comparasion Result Row": FullStructure.height,
            "Compare Report": FinalReport,
            "Part with Structure" : GetBOMLevelonly.height,
            "Part without Structure": INCKDframe.height - GetBOMLevelonly.height,
            "BOM Level with Parts" : GetBOMLevelwithPart.height,
            "BOM Level without Parts": FullStructure.height - GetBOMLevelwithPart.height
        },
        "ModelProperties": {
            "FFC": MainFFC.height,
            "Speaker": MainSpeaker.height
        }
    }

    GetReport = json.dumps(StructureReport, indent=4)
    
    return FullStructure, GetReport

#Belongs To ATSC (Especially 60Hz)
def StructureCheck(InputConcateFrame, ModelName):
    
    ListModelName = list(ModelName)
    GetRegionCheck = "".join(ListModelName[14]+ ListModelName[15]) 
    GetBrand = "".join(ListModelName[16])
    GetSubs = "".join(ListModelName[18])

    GetProfile = ModelProfile(ModelName)
    RegionUpper = GetProfile.GetRegionSuffix.upper()

    PandasFrameConcar = InputConcateFrame
    PandasFrameConcar = PandasFrameConcar.reset_index(drop=True)

    Report28 = "" 
    RemoteReport = ""
    BatteryReport= ""

    def Supply_Check(rownum):
        partnum = PandasFrameConcar.at[rownum, "PartNum"]
        part_number = PandasFrameConcar.at[rownum, "part_number"]
        supply_type = str(PandasFrameConcar.at[rownum, "Supply Type"]).strip().lower()
        part_supply = str(PandasFrameConcar.at[rownum, "part_supplyType"]).strip().lower()
        qty_ref = str(PandasFrameConcar.at[rownum, "Qty_Ref"]).strip().lower()
        part_qty = str(PandasFrameConcar.at[rownum, "part_quantity"]).strip().lower()
        uit_ref = str(PandasFrameConcar.at[rownum, "Uit_Ref"]).strip().lower()
        part_uit = str(PandasFrameConcar.at[rownum, "part_UIT"]).strip().lower()

        if pd.isna(partnum) or pd.isna(part_number):
            PandasFrameConcar.loc[rownum, "Structrue Check"] = ""
            return
    
        if pd.notna(partnum) and pd.notna(part_number):
            if partnum and part_number is not None: 
                if supply_type == part_supply:
                    Results = "OK"
                    PandasFrameConcar.loc[rownum, "Structrue Check"] = "OK"
                else:
                    Results = "NG"
                    PandasFrameConcar.loc[rownum, "Structrue Check"] = "NG"
        else:
            PandasFrameConcar.loc[rownum, "Structrue Check"] = ""

    def UIT_Supply_Qty(rownum):
        partnum = str(PandasFrameConcar.at[rownum, "PartNum"]).strip().lower()
        part_number = str(PandasFrameConcar.at[rownum, "part_number"]).strip().lower()
        supply_type = str(PandasFrameConcar.at[rownum, "Supply Type"]).strip().lower()
        part_supply = str(PandasFrameConcar.at[rownum, "part_supplyType"]).strip().lower()
        qty_ref = PandasFrameConcar.at[rownum, "Qty_Ref"]
        part_qty = PandasFrameConcar.at[rownum, "part_quantity"]
        uit_ref = str(PandasFrameConcar.at[rownum, "Uit_Ref"]).strip().lower()
        part_uit = str(PandasFrameConcar.at[rownum, "part_UIT"]).strip().lower()

        if pd.isna(partnum) or pd.isna(part_number):
            Results = ""
            PandasFrameConcar.loc[rownum, "Structrue Check"] = ""
            return

        if pd.notna(partnum) and pd.notna(part_number) and pd.notna(qty_ref) and pd.notna(part_qty):

            if partnum and part_number is not None:  
                if (supply_type == part_supply and uit_ref == part_uit and float(qty_ref) == float(part_qty)):
                    Results = "OK"
                    PandasFrameConcar.loc[rownum, "Structrue Check"] = "OK"
                else:
                    Results= "NG"
                    PandasFrameConcar.loc[rownum, "Structrue Check"] = "NG"
        else:
            Results = ""
            PandasFrameConcar.loc[rownum, "Structrue Check"] = ""

    def UIT_Supply_QtyCHECK(rownum):
        partnum = str(PandasFrameConcar.at[rownum, "PartNum"]).strip().lower()
        part_number = str(PandasFrameConcar.at[rownum, "part_number"]).strip().lower()
        supply_type = str(PandasFrameConcar.at[rownum, "Supply Type"]).strip().lower()
        part_supply = str(PandasFrameConcar.at[rownum, "part_supplyType"]).strip().lower()
        qty_ref = PandasFrameConcar.at[rownum, "Qty_Ref"]
        part_qty = PandasFrameConcar.at[rownum, "part_quantity"]
        uit_ref = str(PandasFrameConcar.at[rownum, "Uit_Ref"]).strip().lower()
        part_uit = str(PandasFrameConcar.at[rownum, "part_UIT"]).strip().lower()

        if pd.isna(partnum) or pd.isna(part_number):
            Results = ""
            PandasFrameConcar.loc[rownum, "Structrue Check"] = ""
            return

        if pd.notna(partnum) and pd.notna(part_number) and pd.notna(qty_ref) and pd.notna(part_qty):

            if partnum and part_number is not None:  
                if (supply_type == part_supply and uit_ref == part_uit and float(qty_ref) == float(part_qty)):
                    Results = "OK"
                    PandasFrameConcar.loc[rownum, "Structrue Check"] = "OK"
                else:
                    Results= "NG"
                    PandasFrameConcar.loc[rownum, "Structrue Check"] = "CHECK"
        else:
            Results = ""
            PandasFrameConcar.loc[rownum, "Structrue Check"] = ""

    def UIT_Qty(rownum):
        partnum = PandasFrameConcar.at[rownum, "PartNum"]
        part_number = PandasFrameConcar.at[rownum, "part_number"]
        supply_type = str(PandasFrameConcar.at[rownum, "Supply Type"]).strip().lower()
        part_supply = str(PandasFrameConcar.at[rownum, "part_supplyType"]).strip().lower()
        qty_ref = PandasFrameConcar.at[rownum, "Qty_Ref"]
        part_qty = PandasFrameConcar.at[rownum, "part_quantity"]
        uit_ref = str(PandasFrameConcar.at[rownum, "Uit_Ref"]).strip().lower()
        part_uit = str(PandasFrameConcar.at[rownum, "part_UIT"]).strip().lower()

        if pd.isna(partnum) or pd.isna(part_number) or pd.isna(qty_ref) or pd.isna(part_qty):
            PandasFrameConcar.loc[rownum, "Structrue Check"] = ""
            return
        if pd.notna(partnum) and pd.notna(part_number):
            if partnum and part_number is not None: 
                if qty_ref == part_qty and float(uit_ref) == float(part_uit):
                    Results = "OK"
                    PandasFrameConcar.loc[rownum, "Structrue Check"] = "OK"
                else:
                    Results = "NG"
                    PandasFrameConcar.loc[rownum, "Structrue Check"] = "NG"
        else:
            PandasFrameConcar.loc[2, "Structrue Check"] = ""

    def UIT_Supply(rownum):
        partnum = PandasFrameConcar.at[rownum, "PartNum"]
        part_number = PandasFrameConcar.at[rownum, "part_number"]
        supply_type = str(PandasFrameConcar.at[rownum, "Supply Type"]).strip().lower()
        part_supply = str(PandasFrameConcar.at[rownum, "part_supplyType"]).strip().lower()
        qty_ref = str(PandasFrameConcar.at[rownum, "Qty_Ref"]).strip().lower()
        part_qty = str(PandasFrameConcar.at[rownum, "part_quantity"]).strip().lower()
        uit_ref = str(PandasFrameConcar.at[rownum, "Uit_Ref"]).strip().lower()
        part_uit = str(PandasFrameConcar.at[rownum, "part_UIT"]).strip().lower()

        if pd.isna(part_number):
            PandasFrameConcar.loc[rownum, "Structrue Check"] = ""
            return
    
        elif pd.notna(part_number):
            if pd.notna(partnum) and pd.notna(part_number):
                if partnum and part_number: 
                    if supply_type == part_supply or uit_ref == part_uit:
                        Results = "OK"
                        PandasFrameConcar.loc[rownum, "Structrue Check"] = "OK"
                    elif supply_type != part_supply or uit_ref != part_uit:
                        Results = "NG"
                        PandasFrameConcar.loc[rownum, "Structrue Check"] = "NG"
                    else:
                        Results = "CHECK"
                        PandasFrameConcar.loc[rownum, "Structrue Check"] = "CHECK"
        else:
            PandasFrameConcar.loc[rownum, "Structrue Check"] = ""

    def UIT_Supply_ReSearch(rownum):
        partnum = PandasFrameConcar.at[rownum, "PartNum"]
        part_number = PandasFrameConcar.at[rownum, "part_number"]
        supply_type = str(PandasFrameConcar.at[rownum, "Supply Type"]).strip().lower()
        part_supply = str(PandasFrameConcar.at[rownum, "part_supplyType"]).strip().lower()
        qty_ref = str(PandasFrameConcar.at[rownum, "Qty_Ref"]).strip().lower()
        part_qty = str(PandasFrameConcar.at[rownum, "part_quantity"]).strip().lower()
        uit_ref = str(PandasFrameConcar.at[rownum, "Uit_Ref"]).strip().lower()
        part_uit = str(PandasFrameConcar.at[rownum, "part_UIT"]).strip().lower()

        if pd.isna(part_number):
            PandasFrameConcar.loc[rownum, "Structrue Check"] = ""
            return
    
        elif pd.notna(part_number):
            if pd.notna(partnum) and pd.notna(part_number):
                if partnum and part_number: 
                    if supply_type == part_supply or re.search(re.escape(part_uit), uit_ref):
                        Results = "OK"
                        PandasFrameConcar.loc[rownum, "Structrue Check"] = "OK"
                    elif supply_type != part_supply or uit_ref != part_uit:
                        Results = "NG"
                        PandasFrameConcar.loc[rownum, "Structrue Check"] = "NG"
                    else:
                        Results = "CHECK"
                        PandasFrameConcar.loc[rownum, "Structrue Check"] = "CHECK"
        else:
            PandasFrameConcar.loc[rownum, "Structrue Check"] = ""

    def Supply_Qty(rownum):
        partnum = str(PandasFrameConcar.at[rownum, "PartNum"]).strip().lower()
        part_number = str(PandasFrameConcar.at[rownum, "part_number"]).strip().lower()
        supply_type = str(PandasFrameConcar.at[rownum, "Supply Type"]).strip().lower()
        part_supply = str(PandasFrameConcar.at[rownum, "part_supplyType"]).strip().lower()
        qty_ref = PandasFrameConcar.at[rownum, "Qty_Ref"]
        part_qty = PandasFrameConcar.at[rownum, "part_quantity"]
        uit_ref = str(PandasFrameConcar.at[rownum, "Uit_Ref"]).strip().lower()
        part_uit = str(PandasFrameConcar.at[rownum, "part_UIT"]).strip().lower()

        if pd.isna(partnum) or pd.isna(part_number) or pd.isna(qty_ref) or pd.isna(part_qty):
            PandasFrameConcar.loc[rownum, "Structrue Check"] = ""
            return

        if pd.notna(partnum) and pd.notna(part_number):
            if partnum and part_number is not None: 
                if supply_type == part_supply and str(qty_ref) == str(part_qty):
                    Results = "OK"
                    PandasFrameConcar.loc[rownum, "Structrue Check"] = "OK"
                else:
                    Results = "NG"
                    PandasFrameConcar.loc[rownum, "Structrue Check"] = "NG"
        else:
            PandasFrameConcar.loc[rownum, "Structrue Check"] = " "

    def Supply_QtyOR(rownum):
        partnum = str(PandasFrameConcar.at[rownum, "PartNum"]).strip().lower()
        part_number = str(PandasFrameConcar.at[rownum, "part_number"]).strip().lower()
        supply_type = str(PandasFrameConcar.at[rownum, "Supply Type"]).strip().lower()
        part_supply = str(PandasFrameConcar.at[rownum, "part_supplyType"]).strip().lower()
        qty_ref = PandasFrameConcar.at[rownum, "Qty_Ref"]
        part_qty = PandasFrameConcar.at[rownum, "part_quantity"]
        uit_ref = str(PandasFrameConcar.at[rownum, "Uit_Ref"]).strip().lower()
        part_uit = str(PandasFrameConcar.at[rownum, "part_UIT"]).strip().lower()

        if pd.isna(partnum) or pd.isna(part_number):
            PandasFrameConcar.loc[rownum, "Structrue Check"] = ""
        else:
            if supply_type == part_supply or str(qty_ref) == str(part_qty):
                Results = "OK"
                PandasFrameConcar.loc[rownum, "Structrue Check"] = "OK"
            else:
                Results = "NG"
                PandasFrameConcar.loc[rownum, "Structrue Check"] = "NG"
    
    def BlankResult(rownum):
        Results = ""
        PandasFrameConcar.loc[rownum, "Structrue Check"] = ""
    
    def CheckResults(rownum):
        Results = "CHECK"
        PandasFrameConcar.loc[rownum, "Structrue Check"] = "CHECK"

    def CheckPartNum(rownum):
        partnum = PandasFrameConcar.at[rownum, "PartNum"]
        part_number = PandasFrameConcar.at[rownum, "part_number"]
        supply_type = str(PandasFrameConcar.at[rownum, "Supply Type"]).strip().lower()
        part_supply = str(PandasFrameConcar.at[rownum, "part_supplyType"]).strip().lower()
        qty_ref = str(PandasFrameConcar.at[rownum, "Qty_Ref"]).strip().lower()
        part_qty = str(PandasFrameConcar.at[rownum, "part_quantity"]).strip().lower()
        uit_ref = str(PandasFrameConcar.at[rownum, "Uit_Ref"]).strip().lower()
        part_uit = str(PandasFrameConcar.at[rownum, "part_UIT"]).strip().lower()

        if pd.isna(part_number):
            Results = "NG"
            PandasFrameConcar.loc[rownum, "Structrue Check"] = "NG"
            return
    
        else:
            Results = "OK"
            PandasFrameConcar.loc[rownum, "Structrue Check"] = "OK"
    
    UIT_Supply_Qty(0)

    partnumRemote = PandasFrameConcar.at[1, "PartNum"]
    part_numberRemote = PandasFrameConcar.at[1, "part_number"]
    supply_typeRemote = str(PandasFrameConcar.at[1, "Supply Type"]).strip().lower()
    part_supplyRemote = str(PandasFrameConcar.at[1, "part_supplyType"]).strip().lower()
    qty_refRemote = str(PandasFrameConcar.at[1, "Qty_Ref"]).strip().lower()
    part_qtyRemote = str(PandasFrameConcar.at[1, "part_quantity"]).strip().lower()
    uit_refRemote = str(PandasFrameConcar.at[1, "Uit_Ref"]).strip().lower()
    part_uitRemote = str(PandasFrameConcar.at[1, "part_UIT"]).strip().lower()

    if RegionUpper == "US" or RegionUpper == "CC":
        RemoteReport = "Remote NA Region"
        Results = "OK"
        PandasFrameConcar.loc[1, "Structrue Check"] = "OK"
    else:
        
        RemoteReport = "Remote MR"
        if pd.isna(partnumRemote):
            
            Results = "NG"
            PandasFrameConcar.loc[1, "Structrue Check"] = "NG"
            return
        else:
            if GetSubs == "S" and GetBrand == "L": 
                Results = "OK"
                PandasFrameConcar.loc[2, "Structrue Check"] = "OK"
                return
            elif str(qty_refRemote) == str(part_qtyRemote)  or part_supplyRemote == "supplier" or part_supplyRemote == "assembly pull":
                Results = "OK"
                PandasFrameConcar.loc[2, "Structrue Check"] = "OK"
            else:
                Results = "NG"
                PandasFrameConcar.loc[2, "Structrue Check"] = "NG"
   
    if RegionUpper == "US" or RegionUpper == "CC" or RegionUpper == "WC":
        BatteryReport = f"Battery {RegionUpper} Region"
        Results = "OK"
        PandasFrameConcar.loc[1, "Structrue Check"] = "OK"
    else:
        BatteryReport = f"Battery OK"
        Supply_QtyOR(1)

    UIT_Supply_Qty(5)
    Supply_Qty(7)

    CheckPartNum(15) #SubBoard
    UIT_Supply_Qty(16)
    Supply_Qty(17)
    UIT_Supply(18)
    UIT_Supply(19)
    UIT_Supply(20)

    UIT_Supply(22)

    UIT_Supply(23)
    UIT_Supply(24)
    UIT_Supply(25)

    if re.search(r"LB", GetProfile.GetSeries):
        Report28 ="Model LB"
        CheckResults(28)
    else:
        if pd.notna(PandasFrameConcar.at[28, "part_number"]):
            Report28 = "Part in 28"
            Supply_QtyOR(28)
        else:
            if pd.notna(PandasFrameConcar.at[3, "part_number"]) or pd.notna(PandasFrameConcar.at[20, "part_number"]) or pd.notna(PandasFrameConcar.at[33, "part_number"]) or pd.notna(PandasFrameConcar.at[42, "part_number"]):
                Report28 = "No Part in 3 - 20 - 33 - 42"
                BlankResult(28)
            else:
                if pd.notna(PandasFrameConcar.at[3, "part_number"]) and pd.notna(PandasFrameConcar.at[32, "part_number"]):
                    Report28 = "No Part in 3 and 32, Checking 28"
                    Supply_QtyOR(28)
                else:
                    Results = "NG"
                    PandasFrameConcar.loc[28, "Structrue Check"] = "NG"
                
    Supply_Qty(29)
    Supply_Qty(30)
    UIT_Supply(31)
    UIT_Supply_Qty(32)
    Supply_Qty(33)
    UIT_Supply(34)
    UIT_Supply_Qty(35)  #EBT Special Case

    if GetProfile.GetSeries == "UA75" or GetProfile.GetSeries == "QNED82":
        UIT_Qty(36)
    else:
        BlankResult(36)

    Supply_Qty(37)
    Supply_Qty(38)
    Supply_Qty(39)
    Supply_Qty(40)
    Supply_Qty(41)
    Supply_Qty(42)
    UIT_Supply_Qty(43)
    Supply_Qty(44)
    Supply_Qty(45)
    Supply_Qty(46)
    Supply_Qty(47)
    Supply_Qty(48)
    UIT_Supply_Qty(49)
    UIT_Supply(50)
    UIT_Supply_ReSearch(51)
    Supply_QtyOR(52) #Label Special Case
    Supply_QtyOR(53) #Ribbon Special Case

    UIT_Supply_Qty(56)
    UIT_Supply_Qty(57)
    UIT_Supply_Qty(58)
    UIT_Supply_Qty(59)
    UIT_Supply_Qty(60)

    Supply_Check(63)
    UIT_Supply_Qty(64)
    UIT_Supply_Qty(65)

    jsonReport = {
        "Special-Case_28": Report28,
        "Remote_Status": RemoteReport,
        "BatteryReport": BatteryReport
    }
    
    return PandasFrameConcar, jsonReport

def create_download_all_excel(
    target_model,
    dev_model,
    init_model,
    ProfileFrame,
    SummaryFrame=None,
    tool_frame=None,
    structure_frame=None,
    remark_frame=None,
    ben_df=None,
    toolopt_df=None,
    status_df=None,
    subs_df=None,
    single_df=None,
    multi_df=None,
    tool_multi_frame=None,
    op_frame=None
):
    """
    Create one Excel file containing combined results from:
    sheet1 Summary/Profile,
    sheet2 Structure,
    sheet3 BEN Compare,
    sheet4 Substitute,
    sheet5 HW Tool Option,
    sheet6 Tool Option Check,
    sheet7 Operation Plan.
    """

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        workbook = writer.book

        # =========================
        # Common Excel Formats
        # =========================
        title_format = workbook.add_format({
            "bold": True,
            "font_size": 20,
            "align": "left",
            "valign": "vcenter"
        })

        section_title_format = workbook.add_format({
            "bold": True,
            "font_size": 12,
            "bg_color": "#B4C6E7",
            "font_color": "#000000",
            "align": "left",
            "valign": "vcenter",
            "border": 1
        })

        header_format = workbook.add_format({
            "bold": True,
            "bg_color": "#D9E1F2",
            "font_color": "#000000",
            "align": "center",
            "valign": "vcenter",
            "border": 1
        })

        normal_format = workbook.add_format({
            "align": "left",
            "valign": "vcenter",
            "border": 1
        })

        remarks_format = workbook.add_format({
            "align": "left",
            "valign": "top",
            "text_wrap": True,
            "border": 1
        })

        ok_format = workbook.add_format({
            "bg_color": "#00B050",
            "font_color": "#FFFFFF",
            "bold": True,
            "align": "center",
            "valign": "vcenter",
            "border": 1
        })

        ng_format = workbook.add_format({
            "bg_color": "#FF1300",
            "font_color": "#FFFFFF",
            "bold": True,
            "align": "center",
            "valign": "vcenter",
            "border": 1
        })

        check_format = workbook.add_format({
            "bg_color": "#F5C527",
            "font_color": "#000000",
            "bold": True,
            "align": "center",
            "valign": "vcenter",
            "border": 1
        })

        red_diff_format = workbook.add_format({
            "bg_color": "#FF1300",
            "font_color": "#FFFFFF",
            "bold": True,
            "align": "left",
            "valign": "vcenter",
            "border": 1
        })

        def safe_excel_value(value):
            if value is None:
                return ""

            try:
                if pd.isna(value):
                    return ""
            except Exception:
                pass

            return value

        def normalize_compare_value(value):
            if value is None:
                return ""

            try:
                if pd.isna(value):
                    return ""
            except Exception:
                pass

            value = str(value).strip()

            if value.lower() == "nan":
                return ""

            return value

        def to_pandas_safe(df):
            if df is None:
                return pd.DataFrame()

            if isinstance(df, pd.io.formats.style.Styler):
                df = df.data

            if isinstance(df, pl.DataFrame):
                df = df.to_pandas()

            if isinstance(df, pd.DataFrame):
                return df.copy()

            try:
                return pd.DataFrame(df)
            except Exception:
                return pd.DataFrame()

        def write_basic_table(
            worksheet,
            df,
            startrow,
            startcol,
            result_col_name=None,
            remarks_col_names=None
        ):
            df = to_pandas_safe(df)

            if df.empty:
                return startrow

            df.columns = [str(col).strip() for col in df.columns]
            columns = list(df.columns)

            if remarks_col_names is None:
                remarks_col_names = ["Remarks", "Al. Remarks", "Eng. Remarks"]

            for col_idx, col_name in enumerate(columns):
                worksheet.write(startrow, startcol + col_idx, col_name, header_format)

            for row_idx in range(len(df)):
                excel_row = startrow + 1 + row_idx

                for col_idx, col_name in enumerate(columns):
                    value = safe_excel_value(df.iloc[row_idx, col_idx])
                    cell_format = normal_format

                    if col_name in remarks_col_names:
                        cell_format = remarks_format

                    if result_col_name is not None and col_name == result_col_name:
                        result_value = str(value).strip().upper()

                        if result_value == "OK":
                            cell_format = ok_format
                        elif result_value == "NG":
                            cell_format = ng_format
                        elif result_value == "CHECK":
                            cell_format = check_format

                    worksheet.write(excel_row, startcol + col_idx, value, cell_format)

            for col_idx, col_name in enumerate(columns):
                max_len = len(str(col_name))

                if len(df) > 0:
                    max_len = max(max_len, df[col_name].astype(str).map(len).max())

                worksheet.set_column(
                    startcol + col_idx,
                    startcol + col_idx,
                    min(max_len + 3, 45)
                )

            return startrow + len(df) + 1

        def write_compare_table(
            worksheet,
            df,
            startrow,
            startcol,
            initial_col_name,
            compare_col_names,
            remarks_col_names=None
        ):
            df = to_pandas_safe(df)

            if df.empty:
                return startrow

            df.columns = [str(col).strip() for col in df.columns]
            columns = list(df.columns)

            if remarks_col_names is None:
                remarks_col_names = ["Remarks", "Al. Remarks", "Eng. Remarks"]

            for col_idx, col_name in enumerate(columns):
                worksheet.write(startrow, startcol + col_idx, col_name, header_format)

            initial_idx = columns.index(initial_col_name) if initial_col_name in columns else None

            for row_idx in range(len(df)):
                excel_row = startrow + 1 + row_idx

                initial_value = ""
                if initial_idx is not None:
                    initial_value = normalize_compare_value(df.iloc[row_idx, initial_idx])

                for col_idx, col_name in enumerate(columns):
                    raw_value = df.iloc[row_idx, col_idx]
                    cell_value = safe_excel_value(raw_value)
                    cell_format = normal_format

                    if col_name in remarks_col_names:
                        cell_format = remarks_format

                    if col_name in compare_col_names:
                        current_value = normalize_compare_value(raw_value)

                        if initial_value == "" or current_value == "" or current_value != initial_value:
                            cell_format = red_diff_format

                    worksheet.write(excel_row, startcol + col_idx, cell_value, cell_format)

            for col_idx, col_name in enumerate(columns):
                max_len = len(str(col_name))

                if len(df) > 0:
                    max_len = max(max_len, df[col_name].astype(str).map(len).max())

                worksheet.set_column(
                    startcol + col_idx,
                    startcol + col_idx,
                    min(max_len + 3, 45)
                )

            return startrow + len(df) + 1

        # =========================================================
        # Sheet 1: Summary / Model Profile
        # =========================================================
        worksheet = workbook.add_worksheet("Summary")
        writer.sheets["Summary"] = worksheet

        worksheet.merge_range(
            0,
            0,
            0,
            8,
            "Model Profile Summary - " + str(target_model),
            title_format
        )

        worksheet.write(2, 1, "Target Model", section_title_format)
        worksheet.write(2, 2, str(target_model), normal_format)

        worksheet.write(3, 1, "Development Model", section_title_format)
        worksheet.write(3, 2, str(dev_model), normal_format)

        worksheet.write(4, 1, "Initial Model", section_title_format)
        worksheet.write(4, 2, str(init_model), normal_format)

        worksheet.write(6, 1, "Model Profile", section_title_format)
        write_basic_table(
            worksheet=worksheet,
            df=ProfileFrame,
            startrow=7,
            startcol=1
        )

        if SummaryFrame is not None:
            worksheet.write(21, 1, "Summary Result", section_title_format)
            write_basic_table(
                worksheet=worksheet,
                df=SummaryFrame,
                startrow=22,
                startcol=1,
                result_col_name="Result"
            )

        if tool_frame is not None:
            worksheet.write(32, 1, "Tool Option Summary", section_title_format)
            write_basic_table(
                worksheet=worksheet,
                df=tool_frame,
                startrow=33,
                startcol=1,
                result_col_name="Result"
            )

        worksheet.freeze_panes(7, 1)
        worksheet.set_zoom(90)

        # =========================================================
        # Sheet 2: Structure
        # =========================================================
        worksheet = workbook.add_worksheet("Structure")
        writer.sheets["Structure"] = worksheet

        worksheet.merge_range(
            0,
            0,
            0,
            8,
            "Structure Checklist - " + str(target_model),
            title_format
        )

        if structure_frame is not None:
            write_basic_table(
                worksheet=worksheet,
                df=structure_frame,
                startrow=3,
                startcol=1
            )

        if remark_frame is not None:
            remark_startrow = 3
            structure_df = to_pandas_safe(structure_frame)
            if not structure_df.empty:
                remark_startrow = len(structure_df) + 7

            worksheet.write(remark_startrow - 1, 1, "Structure Remarks", section_title_format)
            write_basic_table(
                worksheet=worksheet,
                df=remark_frame,
                startrow=remark_startrow,
                startcol=1
            )

        worksheet.set_zoom(90)

        # =========================================================
        # Sheet 3: BEN Compare
        # =========================================================
        worksheet = workbook.add_worksheet("BEN Compare")
        writer.sheets["BEN Compare"] = worksheet

        worksheet.merge_range(
            0,
            0,
            0,
            10,
            "BEN Compare - " + str(target_model),
            title_format
        )

        worksheet.write(1, 1, "Target Model", section_title_format)
        worksheet.write(1, 2, str(target_model), normal_format)
        worksheet.write(1, 3, "Development Model", section_title_format)
        worksheet.write(1, 4, str(dev_model), normal_format)
        worksheet.write(1, 5, "Initial Model", section_title_format)
        worksheet.write(1, 6, str(init_model), normal_format)

        if ben_df is not None:
            worksheet.write(3, 1, "BOM Part Compare", section_title_format)
            write_compare_table(
                worksheet=worksheet,
                df=ben_df,
                startrow=4,
                startcol=1,
                initial_col_name="Part No_Initial",
                compare_col_names=["Part No_Development", "Part No_Target"]
            )

        if toolopt_df is not None:
            ben_df_len = len(to_pandas_safe(ben_df))
            tool_startrow = max(31, ben_df_len + 8)

            worksheet.write(tool_startrow - 1, 1, "Tool Option Compare", section_title_format)
            write_compare_table(
                worksheet=worksheet,
                df=toolopt_df,
                startrow=tool_startrow,
                startcol=1,
                initial_col_name="Initial",
                compare_col_names=["Development", "Target"]
            )

        worksheet.freeze_panes(4, 1)
        worksheet.set_zoom(90)

        # =========================================================
        # Sheet 4: Substitute & Part Status
        # =========================================================
        worksheet = workbook.add_worksheet("Substitute")
        writer.sheets["Substitute"] = worksheet

        worksheet.merge_range(
            0,
            0,
            0,
            10,
            "Substitute & Part Status - " + str(target_model),
            title_format
        )

        if status_df is not None:
            status_df = to_pandas_safe(status_df)

            if "Al. Remarks" not in status_df.columns:
                status_df["Al. Remarks"] = ""

            if "Eng. Remarks" not in status_df.columns:
                status_df["Eng. Remarks"] = ""

            worksheet.write(3, 1, "Part Status Compare", section_title_format)
            write_compare_table(
                worksheet=worksheet,
                df=status_df,
                startrow=4,
                startcol=1,
                initial_col_name="Status_Init",
                compare_col_names=["Status_Dev", "Status_Target"]
            )

        if subs_df is not None:
            subs_df = to_pandas_safe(subs_df)

            if "Al. Remarks" not in subs_df.columns:
                subs_df["Al. Remarks"] = ""

            if "Eng. Remarks" not in subs_df.columns:
                subs_df["Eng. Remarks"] = ""

            status_len = len(to_pandas_safe(status_df))
            subs_startrow = status_len + 9

            worksheet.write(subs_startrow - 1, 1, "Substitute Logic Compare", section_title_format)
            write_compare_table(
                worksheet=worksheet,
                df=subs_df,
                startrow=subs_startrow,
                startcol=1,
                initial_col_name="Subs_Init",
                compare_col_names=["Subs_Dev", "Subs_Target"]
            )

        worksheet.set_zoom(90)

        # =========================================================
        # Sheet 5: HW Tool Option Compare
        # =========================================================
        worksheet = workbook.add_worksheet("HW Tool Option")
        writer.sheets["HW Tool Option"] = worksheet

        worksheet.merge_range(
            0,
            0,
            0,
            10,
            "HW Tool Option Compare - " + str(target_model),
            title_format
        )

        if single_df is not None:
            worksheet.write(3, 1, "Single Option Compare", section_title_format)
            write_compare_table(
                worksheet=worksheet,
                df=single_df,
                startrow=4,
                startcol=1,
                initial_col_name="Initial",
                compare_col_names=["Development", "Target"],
                remarks_col_names=["Eng. Remarks"]
            )

        if multi_df is not None:
            single_len = len(to_pandas_safe(single_df))
            multi_startrow = max(61, single_len + 9)

            worksheet.write(multi_startrow - 1, 1, "Multi Option Compare", section_title_format)
            write_compare_table(
                worksheet=worksheet,
                df=multi_df,
                startrow=multi_startrow,
                startcol=1,
                initial_col_name="Initial",
                compare_col_names=["Development", "Target"],
                remarks_col_names=["Eng. Remarks"]
            )

        worksheet.set_zoom(90)

        # =========================================================
        # Sheet 6: Tool Option Check
        # =========================================================
        worksheet = workbook.add_worksheet("Tool Option Check")
        writer.sheets["Tool Option Check"] = worksheet

        worksheet.merge_range(
            0,
            0,
            0,
            10,
            "Tool Option Check - " + str(target_model),
            title_format
        )

        if tool_frame is not None:
            worksheet.write(3, 1, "Tool Option Summary", section_title_format)
            write_basic_table(
                worksheet=worksheet,
                df=tool_frame,
                startrow=4,
                startcol=1,
                result_col_name="Result"
            )

        if tool_multi_frame is not None:
            tool_frame_len = len(to_pandas_safe(tool_frame))
            multi_tool_startrow = tool_frame_len + 9

            worksheet.write(multi_tool_startrow - 1, 1, "Tool Option Master Checklist", section_title_format)
            write_basic_table(
                worksheet=worksheet,
                df=tool_multi_frame,
                startrow=multi_tool_startrow,
                startcol=1,
                result_col_name="Result"
            )

        worksheet.set_zoom(90)

        # =========================================================
        # Sheet 7: Operation Plan
        # =========================================================
        worksheet = workbook.add_worksheet("Operation Plan")
        writer.sheets["Operation Plan"] = worksheet

        worksheet.merge_range(
            0,
            0,
            0,
            10,
            "Operation Plan Check - " + str(target_model),
            title_format
        )

        if op_frame is not None:
            write_basic_table(
                worksheet=worksheet,
                df=op_frame,
                startrow=3,
                startcol=1,
                result_col_name="Result"
            )

        worksheet.set_zoom(90)

    output.seek(0)
    return output