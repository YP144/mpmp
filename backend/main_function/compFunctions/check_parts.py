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


import io
import json
import re
import zipfile
from copy import copy as copy_style
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd
import polars as pl
import requests

from openpyxl import Workbook, load_workbook
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
#use @st.cache_data

from main_function.services.check_sso import SSO_NPDM, NpdmClient
from main_function.services.main_hwpart import targetpart_compare, developmentpart_compare, initialpart_compare
from main_function.services.main_tooloption import run_tooloption, getToolinfo
from main_function.services.subs_hwpart import run_subshwpart

from main_function.functions.profile import ModelProfile, GetOperationPart
from main_function.functions.substate import GoGetTemplate, GetParseStructure, StructureCheck
from main_function.functions.allcompare import create_download_all_excel
from main_function.functions.datasend import upload_bytes_tos3
from main_function.functions.conditioning import zerobom_conditioning
from main_function.functions.tool_option_logic import GetModelToolOptionMaster, ToolOptionCross

class GetTargetParts:
    def __init__(self, TargeModelBOM: pl.DataFrame, target_model: str):
        self.TargeModelBOM = TargeModelBOM
        self.target_model = target_model
        self.profile = ModelProfile(target_model)

        self.get_target_parts()
        self.get_prm_parts()

    def safe_item(self, df: pl.DataFrame, column: str, default: str = "Not Found"):
        if df is not None and df.height > 0 and column in df.columns:
            value = df.item(0, column)

            if value is None:
                return default

            return value

        return default

    def get_target_parts(self):
        #Operation Plan and others
        # Get WiFi

        """self.TargeModelBOM = self.TargeModelBOM.filter(
            pl.col("dataType") == "B"
        )"""

        self.WiFirow = self.TargeModelBOM.filter(
            pl.col("part_number").str.contains("EAT")
        ).unique(subset="part_number")
        self.WiFirow = self.WiFirow.with_columns(
            pl.lit("WiFi").alias("Category")
        )

        self.GetWiFi = self.safe_item(self.WiFirow, "part_number")
        self.GetWiFiQty = self.safe_item(self.WiFirow, "part_quantity")

        # Get Speaker
        self.SPKrow = self.TargeModelBOM.filter(
            pl.col("part_descriptions").str.contains("speaker|spk l|spk r")
        ).unique(subset="part_number")

        self.SPKrow = self.SPKrow.with_columns(
            pl.lit("Speaker").alias("Category")
        )

        self.GetSpeaker = self.safe_item(self.SPKrow, "part_number")
        self.GetSpeakerQty = self.safe_item(self.SPKrow, "part_quantity")

        # Get Battery
        self.BatteryRow = self.TargeModelBOM.filter(
            pl.col("part_descriptions").str.contains("battery")
        ).unique(subset="part_number")
        self.BatteryRow = self.BatteryRow.with_columns(
            pl.lit("Battery").alias("Category")
        )

        self.GetBattery = self.safe_item(self.BatteryRow, "part_number")
        self.GetBatteryQty = self.safe_item(self.BatteryRow, "part_quantity")

        # Get Remote
        self.GetRemoteRow = self.TargeModelBOM.filter(
            (pl.col("part_number").str.contains("AKB")) &
            (pl.col("part_descriptions").str.contains("remote"))
        ).unique(subset="part_number")

        self.GetRemoteRow = self.GetRemoteRow.with_columns(
            pl.lit("Remote").alias("Category")
        )

        self.GetRemote = self.safe_item(self.GetRemoteRow, "part_number")
        self.GetRemoteQty = self.safe_item(self.GetRemoteRow, "part_quantity")

       
        # Get HeatPlate
        self.Heatrow = self.TargeModelBOM.filter(
            (pl.col("part_number").str.contains("EBS")) &
            (pl.col("part_TechnicalSpec").str.contains("plate"))
        ).unique(subset="part_number")

        self.Heatrow = self.Heatrow.with_columns(
            pl.lit("Heat Plate").alias("Category")
        )

        self.GetHeat = self.safe_item(self.Heatrow, "part_number")
        self.GetHeatQty = self.safe_item(self.Heatrow, "part_quantity")

        # Get EDID
        self.EDIDrow = self.TargeModelBOM.filter(
            (pl.col("part_number").str.contains("ECC")) &
            (pl.col("part_descriptions").str.contains("edid"))
        ).unique(subset="part_number")

        self.EDIDrow = self.EDIDrow.with_columns(
            pl.lit("EDID").alias("Category")
        )

        self.GetEDID = self.safe_item(self.EDIDrow, "part_number")
        self.GetEDIDQty = self.safe_item(self.EDIDrow, "part_quantity")

        # Get Power Cord
        self.Cordrow = self.TargeModelBOM.filter(
            (pl.col("part_number").str.contains("EAD")) &
            (pl.col("part_descriptions").str.contains("cord"))
        ).unique(subset="part_number")

        self.Cordrow = self.Cordrow.with_columns(
            pl.lit("Power Cord").alias("Category")
        )

        self.GetCord = self.safe_item(self.Cordrow, "part_number")
        self.GetCordQty = self.safe_item(self.Cordrow, "part_quantity")

        if re.search(r"6 in 1", self.profile.GetBoardInfo, re.IGNORECASE):

            self.GetEBTunderEBT = self.TargeModelBOM.filter(
                (pl.col("part_number").str.contains(r"^EBT")) &
                (pl.col("part_TechnicalSpec").str.contains(r"\b6 in 1\b")) &
                (pl.col("bomLevel") == 2)
            ).unique(subset="part_number")

            self.GetEBTunderEBT = self.GetEBTunderEBT.with_columns(
                pl.lit("6in1 EBT").alias("Category")
            )

            self.target_operation = pl.concat([
                self.GetRemoteRow,
                self.BatteryRow,
                self.SPKrow,
                self.Cordrow,
                self.EDIDrow,
                self.Heatrow,
                self.WiFirow,
                self.GetEBTunderEBT
            ], how="diagonal")

        else:
            self.target_operation = pl.concat([
                self.GetRemoteRow,
                self.BatteryRow,
                self.SPKrow,
                self.Cordrow,
                self.EDIDrow,
                self.Heatrow,
                self.WiFirow
            ], how="diagonal")
        #PRM JackSpec Master
        


    def get_prm_parts(self):
        # Get EBT
        self.EBTrow = self.TargeModelBOM.filter(
            pl.col("part_number").str.contains("EBT")
        )

        self.GetEBT = self.safe_item(self.EBTrow, "part_number")
        self.GetEBTQty = self.safe_item(self.EBTrow, "part_quantity")
        # Get EBR
        self.EBRrow = self.TargeModelBOM.filter(
            pl.col("part_number").str.contains("EBR")
        )

        self.GetEBR = self.safe_item(self.EBRrow, "part_number")
        self.GetEBRQty = self.safe_item(self.EBRrow, "part_quantity")

        # Get HDMI
        self.HDMIrow = self.TargeModelBOM.filter(
            pl.col("part_descriptions").str.contains("hdmi")
        )

        self.GetHDMI = self.safe_item(self.HDMIrow, "part_number")
        self.GetHDMIQty = self.safe_item(self.HDMIrow, "part_quantity")

        # Get Chassis
        self.EBUrow = self.TargeModelBOM.filter(
            (pl.col("part_number").str.contains("EBU")) &
            (pl.col("part_descriptions").str.contains("orp"))
        )


        self.result = {
            "GetCord": self.GetCord,
            "GetCordQty": self.GetCordQty,
            "GetEDID": self.GetEDID,
            "GetEDIDQty": self.GetEDIDQty,
            "GetHeat": self.GetHeat,
            "GetHeatQty": self.GetHeatQty,
            "GetSpeaker": self.GetSpeaker,
            "GetSpeakerQty": self.GetSpeakerQty,
            "GetRemoteRow": self.GetRemoteRow,
            "HDMIrow": self.HDMIrow,
            "GetEBT": self.GetEBT,
            "EBTrow": self.EBTrow,
            "GetEBTQty": self.GetEBTQty,
            "GetEBR": self.GetEBR,
            "GetEBRQty": self.GetEBRQty,
            "GetRemote": self.GetRemote,
            "GetRemoteQty": self.GetRemoteQty,
            "GetBattery": self.GetBattery,
            "GetBatteryQty": self.GetBatteryQty,
            "GetHDMI": self.GetHDMI,
            "GetHDMIQty": self.GetHDMIQty,
            "GetWiFi": self.GetWiFi,
            "GetWiFiQty": self.GetWiFiQty,
        }

        

        return self.result

