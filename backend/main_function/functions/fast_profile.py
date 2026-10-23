
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
import traceback
from difflib import SequenceMatcher
import concurrent.futures # Added for threading
import json
import re
import concurrent.futures
from datetime import date, timedelta
import polars as pl

from time import perf_counter
from contextlib import contextmanager

from services.check_sso import SSO_NPDM
from services.main_hwpart import targetpart_compare, developmentpart_compare, initialpart_compare
from services.main_tooloption import run_tooloption, getToolinfo
from services.subs_hwpart import run_subshwpart
from datetime import timedelta, datetime, date

from functions.get_latestver import read_latest_version, read_table
from functions.getdata import (
    HerosURL, userURL, CoworkURL, memberURL,
    OPurl, suffixURL, extraURL, AccMaster
    )
from functions.get_profile_support import get_suffix_data
from functions.get_init_info import predict_development
from functions.datasend import send_to_pymongo_generic

from functions.profiling.get_year import db_search_model_with_fallback_score


class Fast_ModelProfile:
    def __init__(
        self,
        trget: str,
        ssolgenet_cookie: str = "",
        smsession_cookie: str = "",
        **kwargs
    ):
        self.trget = trget
        self.targetModel = trget  # Set self.targetModel to prevent AttributeError
        self.ssolgenet_cookie = ssolgenet_cookie or kwargs.get("ssolgenet", "")
        self.smsession_cookie = smsession_cookie or kwargs.get("smsession", "")
        self.getProfile()

    def _perform_sso_login(self):
        sso = SSO_NPDM()
        # Authenticate using provided cookies or fallback
        if self.ssolgenet_cookie or self.smsession_cookie:
            is_logged_in = sso.check_sso(
                ssolgenet_cookie=self.ssolgenet_cookie,
                smsession_cookie=self.smsession_cookie
            )
        else:
            is_logged_in = sso.auto_login()

        # Safely extract user identity metadata
        name_user = getattr(sso, "user_id", "SYS.AUTO")
        name_ic = getattr(sso, "user_ic", "SYS.AUTO")
        
        # Return tuple to satisfy: sso, name_user, name_ic = future_sso.result()
        return sso, name_user, name_ic

    def _fetch_cowork_data(self, sso, pastday, gettoday):
        """Helper method to fetch cowork data in a thread."""
        cowork_params = {
            "cParamSearchVO": {
                "releaseCreationDate": {"comparison": "BT", "fromDate": "", "toDate": ""},
                "gerpCreationDate": {"fromDate": f"{pastday}", "toDate": f"{gettoday}", "comparison": "BT"},
                "requestBOMOpen": {"comparison": "BT", "fromDate": "", "toDate": ""},
                "divisions": "GLZ",
                "creationPlantUnit": "GLZ.EKHQ",
                "names": f"{self.targetModel}"
            }
        }
        cowork_headers = {
            "Accept": "application/json, text/plain, */*",
            "Authorization": sso.auth_bearer,
            "BusinessUnit": "HE",
            "Content-Type": "application/json",
            "Host": "npdm.lge.com",
            "Referer": "https://npdm.lge.com/"
        }
        try:
            response = requests.put(CoworkURL, headers=cowork_headers, json=cowork_params, timeout=10)
            return response.json()
        except Exception as e:
            return None

    def getProfile(self):
        GetModelName = self.targetModel.split(".")
        self.firstModelName = GetModelName[0]
        
        gettoday = date.today()
        pastday = gettoday - timedelta(days=365)

        # --- START CONCURRENT EXECUTION ---
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # 1. Submit all independent database and network tasks immediately
            future_sso = executor.submit(self._perform_sso_login)
            future_user_list = executor.submit(read_table, memberURL, "user_list")
            future_all_engineer = executor.submit(pl.read_database_uri, uri=userURL, query="SELECT * FROM public.all_engineer")
            future_model_year = executor.submit(db_search_model_with_fallback_score, self.firstModelName)
            future_heros = executor.submit(read_latest_version, db_uri=HerosURL, prefix="HEROmodel2026Y_v3.3_v")
            future_acc = executor.submit(read_latest_version, db_uri=AccMaster, prefix="HEROacc2026Y_v3.1_v")
            future_region = executor.submit(read_table, db_uri=suffixURL, table_name="regionSuffix")
            future_plant = executor.submit(read_table, db_uri=suffixURL, table_name="plantSuffix")
            future_board = executor.submit(read_table, db_uri=suffixURL, table_name="boardSuffix")

            # 2. Wait for SSO to finish, as Cowork API depends on the auth token
            sso, name_user, name_ic = future_sso.result()
            
            # 3. Submit Cowork API task now that we have the SSO token
            future_cowork = executor.submit(self._fetch_cowork_data, sso, pastday, gettoday)

            # 4. Gather all results from the threads
            user_row = future_user_list.result()
            getUser = future_all_engineer.result()
            model_year_crosschecked = future_model_year.result()
            HEROsFrame = future_heros.result()
            getAccpart = future_acc.result()
            RegionFrame = future_region.result()
            PlantFrame = future_plant.result()
            BoardFrame = future_board.result()
            getjson_cowork = future_cowork.result()
        # --- END CONCURRENT EXECUTION ---

        # Check engineer profile
        get_name_row = user_row.filter(pl.col("ID").str.contains(name_user))
        if get_name_row.height > 0:
            self.user_team = get_name_row.item(0, "TEAM")
            self.user_part = get_name_row.item(0, "Part")
            self.user_level = get_name_row.item(0, "Level")
        else:
            self.user_team = "No TEAM"
            self.user_part = "NO PART"
            self.user_level = "NO LEVEL"

        getUser = getUser.select("getName")

        # Process Cowork Data
        try:
            if (
                getjson_cowork is not None
                and "data" in getjson_cowork
                and getjson_cowork["data"] is not None
                and len(getjson_cowork["data"]) > 0
            ):
                all_outdata = []
                coworkdata = getjson_cowork["data"]

                for item in coworkdata:
                    if item.get("outData") is not None:
                        all_outdata.append(item["outData"])

                required_outdata_columns = [
                    "cha_coWorker1", "cha_coWorker2", "cha_coWorker3",
                    "cha_coWorker4", "cha_coWorker5", "cha_coWorker6",
                    "cha_coWorker7", "cha_coWorker8", "cha_coWorker9",
                    "cha_names", "cha_states", "mr_chassis"
                ]

                required_cowork_columns = [
                    "names", "titles", "technicalSpecification", "states"
                ]

                if len(all_outdata) == 0:
                    self.getCircuit = "Not Found"
                else:
                    getcoworkName = pl.DataFrame(all_outdata)

                    for col in required_outdata_columns:
                        if col not in getcoworkName.columns:
                            getcoworkName = getcoworkName.with_columns(pl.lit("").alias(col))

                    getcoworkName = getcoworkName.select(required_outdata_columns)
                    coworkdata = pl.DataFrame(coworkdata, infer_schema_length=1000)

                    for col in required_cowork_columns:
                        if col not in coworkdata.columns:
                            coworkdata = coworkdata.with_columns(pl.lit("").alias(col))

                    coworkdata = coworkdata.select(required_cowork_columns)
                    Result_cowork = pl.concat([getcoworkName, coworkdata], how="horizontal")

                    atsc_members = (
                        getUser
                        .select("getName")
                        .to_series()
                        .drop_nulls()
                        .cast(pl.Utf8)
                        .str.strip_chars()
                        .to_list()
                    )

                    search_columns = [
                        "cha_coWorker1", "cha_coWorker2", "cha_coWorker3",
                        "cha_coWorker4", "cha_coWorker5", "cha_coWorker6",
                        "cha_coWorker7", "cha_coWorker8", "cha_coWorker9",
                        "cha_names", "names"
                    ]

                    # Optimized Polars string matching instead of map_elements
                    pattern = "(?i)(" + "|".join(re.escape(m) for m in atsc_members) + ")"
                    
                    Result_atsc = Result_cowork.with_columns(
                        pl.concat_str(
                            [pl.col(col).cast(pl.Utf8).fill_null("") for col in search_columns],
                            separator=" "
                        ).alias("all_names")
                    ).with_columns(
                        pl.col("all_names").str.extract_all(pattern).list.join(", ").alias("found_atsc_members")
                    ).filter(
                        pl.col("found_atsc_members").is_not_null() & (pl.col("found_atsc_members") != "")
                    )

                    if Result_atsc.height > 0:
                        self.getCircuit = Result_atsc.item(0, "found_atsc_members")
                    else:
                        self.getCircuit = "Not Found"
            else:
                self.getCircuit = "Not Found"
        
        
        except Exception:
            self.getCircuit = "Not Found"
            
        self.model_year = model_year_crosschecked["matched_location"]

        PlantFrame = PlantFrame.with_columns(pl.col("compareString").str.replace_all(r"_", "."))

        if len(GetModelName) != 2:
            raise ValueError(f"Invalid model format: {self.targetModel}")

        GetName, self.GetSuffixName = GetModelName
        self.GetModelName = GetName
        self.GetSuffixName = self.GetSuffixName.lower()

        self.GetRegionSuffix = self.GetSuffixName[1:3]
        self.GetBoardSuffix = self.GetSuffixName[4]
        
        #Get Board Name -- Base on Suffix and NPDM
        BoardFrame = BoardFrame.select(["compareString", "Brand"]).with_columns(
            pl.col("compareString").str.to_lowercase().str.replace_all(r"_", ".")
        )
        BoardFrame = BoardFrame.filter(pl.col("compareString").str.contains(self.GetBoardSuffix))
        self.GetBoardInfo = BoardFrame.item(0, "Brand") if BoardFrame.height > 0 else "Unknown"

        GetPanel = self.GetSuffixName[3]
        SearchRegion = RegionFrame.filter(
            pl.col("compareString")
            .fill_null("")
            .str.to_lowercase()
            .str.contains(self.GetRegionSuffix.lower(), literal=True)
        )

        if SearchRegion.height == 0:
            raise ValueError(f"No region found for {self.GetRegionSuffix}")

        self.ParseRegion = SearchRegion[0, "Region"].upper()
        self.ParseMarket = SearchRegion[0, "Market"]

        #Get Plant Name -- Base on Suffix and NPDM
        GetPlant = PlantFrame.filter(
            pl.lit(self.GetSuffixName.upper()).str.contains("^" + pl.col("compareString") + "$")
        )
        self.GetSubs = GetPlant[0, "Plant"] if GetPlant.height > 0 else "Unknown"
        
        #Get Model Profile base on HEROs -> Change This into NPDM Base / Database base Detection

        GetProfileRow = HEROsFrame.with_columns(pl.col("Region").str.to_uppercase())
        GetProfileRow = HEROsFrame.filter(
            (pl.col("Model Name").fill_null("").str.to_uppercase().str.contains(GetName.upper(), literal=True)) &
            (pl.col("Region") == self.ParseRegion) &
            (pl.col("Suffix").fill_null("").str.to_uppercase().str.contains(GetPanel.upper(), literal=True))
        )

        input_key = GetName.lstrip("0123456789").strip("_")

        if GetProfileRow.height > 0:
            acc_region = GetProfileRow[0, "Region"]
        else:
            acc_region = self.ParseRegion

        acc_model = (
            getAccpart
            .with_columns([
                pl.col("Model Name")
                .str.replace_all(r"^_+|_+$", "")
                .str.replace(r"^\d+", "")
                .alias("model_key")
            ])
            .filter(
                (pl.col("Region") == acc_region) &
                (pl.lit(input_key).str.starts_with(pl.col("model_key")))
            )
        )

        def normalize_remote_magic(remote_magic, suffix_name):
            if remote_magic is None:
                return remote_magic
            remote_magic = str(remote_magic).strip()
            if str(suffix_name)[1:3].lower() == "ff":
                return remote_magic
            return re.sub(r"\bMR26GA\b", "MR26GC", remote_magic, flags=re.IGNORECASE)

        self.SuffixCountry = self.GetSuffixName[1:3]
        RemoteMagic = acc_model[0, "Magic Remote"] if acc_model.height > 0 else None
        RemoteMagic = normalize_remote_magic(RemoteMagic, self.SuffixCountry)

        self.ModelProfile = GetProfileRow
        self.HEROsFrame = HEROsFrame
        
        if GetProfileRow.height > 0:
            self.GetInch = GetProfileRow[0, "Inch"]
            self.GetSeries = GetProfileRow[0, "Series"]
            self.GetCPunit = GetProfileRow[0, "CP Unit"]
            self.GetGrade = GetProfileRow[0, "Grade"]
            self.GetSoC = GetProfileRow[0, "SoC"]
            self.GetChassis = GetProfileRow[0, "Chassis Name"]
            self.GetPanelName = GetProfileRow[0, "Panel Maker"]
            self.GetHerosRegion = GetProfileRow[0, "Region"]
        else:
            self.GetInch = self.GetSeries = self.GetCPunit = self.GetGrade = self.GetSoC = self.GetChassis = self.GetPanelName = self.GetHerosRegion = "Unknown"

        self.GetRemoteMR = RemoteMagic
        self.GetRemoteSR = acc_model[0, "Wifi Name"] if acc_model.height > 0 else "Unknown"

        self.jsonProfile = [{
                "modelYear" : self.model_year,
                "ModelName" : self.targetModel,
                "Inch" : self.GetInch,
                "Series" : self.GetSeries,
                "Region": self.GetHerosRegion,
                "CPunit": self.GetCPunit,
                "SoC": self.GetSoC,
                "Board": self.GetBoardInfo,
                "Chassis": self.GetChassis,
                "Panel": self.GetPanelName,
                "RemoteMR": self.GetRemoteMR,
                "RemoteSR": self.GetRemoteSR,
                "Plant": self.GetSubs,
                "CircuitPIC": self.getCircuit,
                "ParseRegion": self.ParseRegion,
                "Market": self.ParseMarket,
                "ModelSuffix": self.SuffixCountry,
                "Model_Name": GetName,
                "user-info": {
                    "retest-userIc": name_ic,
                    "retest-userId": name_user,
                    "user-team": self.user_team,
                    "user-part": self.user_part,
                    "user-level": self.user_level
                }
            }
        ]



# Optional: Helper for timing blocks of code to find bottlenecks
@contextmanager
def timer(name):
    start = perf_counter()
    yield
    print(f"{name}: {perf_counter() - start:.3f}s")

# --- 1. Cache Master Data & Pre-normalize at SQL/Load Level ---
# --- 1. Cache Master Data & Pre-normalize at SQL/Load Level ---
# --- 1. Cache Master Data & Pre-normalize at SQL/Load Level ---

def load_suffix_tables():
    # Wrap both column names and table names in double quotes to preserve exact casing
    region = pl.read_database_uri(
        uri=suffixURL,
        query='SELECT "compareString", "Region", "Market" FROM "regionSuffix"'
    )

    plant = pl.read_database_uri(
        uri=suffixURL,
        query='SELECT "compareString", "Plant" FROM "plantSuffix"'
    ).with_columns(
        pl.col("compareString").str.replace_all(r"_", ".").alias("compareString")
    )

    board = pl.read_database_uri(
        uri=suffixURL,
        query='SELECT "compareString", "Brand" FROM "boardSuffix"'
    ).with_columns(
        pl.col("compareString").str.to_lowercase().str.replace_all(r"_", ".").alias("compareString")
    )

    return region, plant, board

class Auto_Fast_ModelProfile():
    def __init__(self, targetModel: str):
        self.targetModel = targetModel
        # Initialize the report dictionary to track faults, errors, and filtering results
        self.report = {
            "errors": [],
            "faults": [],
            "filtering_warnings": [],
            "parsing_details": {}
        }
        self.getProfile()

    def getProfile(self):
        GetModelName = self.targetModel.split(".")
        
        # Moved validation to the top to prevent index errors and unnecessary DB calls
        if len(GetModelName) != 2:
            error_msg = f"Invalid model format: {self.targetModel}"
            self.report["errors"].append(error_msg)
            self.report_json = json.dumps(self.report, indent=4)
            raise ValueError(error_msg)

        self.firstModelName = GetModelName[0]
        GetName, self.GetSuffixName = GetModelName
        self.GetModelName = GetName
        self.GetSuffixName = self.GetSuffixName.lower()
        
        self.GetRegionSuffix = self.GetSuffixName[1:3]
        self.GetBoardSuffix = self.GetSuffixName[4]
        GetPanel = self.GetSuffixName[3]

        self.report["parsing_details"] = {
            "targetModel": self.targetModel,
            "ModelName": self.GetModelName,
            "SuffixName": self.GetSuffixName,
            "RegionSuffix": self.GetRegionSuffix,
            "BoardSuffix": self.GetBoardSuffix,
            "PanelSuffix": GetPanel
        }
        
        gettoday = date.today()
        pastday = gettoday - timedelta(days=365)

        # --- 2. Safe Concurrent Execution (Max Workers = 4) ---
        with timer("Concurrent DB load"):
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = {
                    "model_year": executor.submit(db_search_model_with_fallback_score, self.firstModelName),
                    "heros": executor.submit(read_latest_version, db_uri=HerosURL, prefix="HEROmodel2026Y_v3.3_v"),
                    "acc": executor.submit(read_latest_version, db_uri=AccMaster, prefix="HEROacc2026Y_v3.1_v")
                }
                
                results = {}
                for name, future in futures.items():
                    try:
                        results[name] = future.result()
                    except Exception as e:
                        self.report["faults"].append(f"{name} failed: {e}")
                        raise

        # Extract results into local variables (avoiding st.session_state bloat)
        model_year_crosschecked = results.get("model_year", {})
        HEROsFrame = results.get("heros", pl.DataFrame())
        getAccpart = results.get("acc", pl.DataFrame())
        
        # Load cached suffix tables
        RegionFrame, PlantFrame, BoardFrame = load_suffix_tables()

        self.model_year = model_year_crosschecked.get("matched_location", "Unknown")
        if self.model_year == "Unknown":
            self.report["filtering_warnings"].append("Model year crosscheck returned no matched location.")

        # --- 3. Optimized Filtering (Using Equality & Precomputed Keys) ---
        
        # Board Filter (Already pre-normalized in cache)
        BoardFrame_filtered = BoardFrame.filter(pl.col("compareString").str.contains(self.GetBoardSuffix))
        if BoardFrame_filtered.height > 0:
            self.GetBoardInfo = BoardFrame_filtered.item(0, "Brand")
        else:
            self.GetBoardInfo = "Unknown"
            self.report["filtering_warnings"].append(f"No board info found for suffix: {self.GetBoardSuffix}")

        # Region Filter
        SearchRegion = RegionFrame.filter(
            pl.col("compareString")
            .fill_null("")
            .str.to_lowercase()
            .str.contains(self.GetRegionSuffix.lower(), literal=True)
        )

        if SearchRegion.height == 0:
            error_msg = f"No region found for {self.GetRegionSuffix}"
            self.report["errors"].append(error_msg)
            self.report_json = json.dumps(self.report, indent=4)
            raise ValueError(error_msg)

        self.ParseRegion = SearchRegion[0, "Region"].upper()
        self.ParseMarket = SearchRegion[0, "Market"]

        # Plant Filter (Already pre-normalized in cache, using equality)
        GetPlant = PlantFrame.filter(
            pl.lit(self.GetSuffixName.upper()).str.contains("^" + pl.col("compareString") + "$")
        )
        
        if GetPlant.height > 0:
            self.GetSubs = GetPlant[0, "Plant"]
        else:
            self.GetSubs = "Unknown"
            self.report["filtering_warnings"].append(f"No plant found for suffix: {self.GetSuffixName.upper()}")
        
        # HEROs Filter (Precomputing normalized keys for best performance)
        HEROsFrame_normalized = HEROsFrame.with_columns(
            pl.col("Region").str.to_uppercase().alias("Region_upper"),
            pl.col("Model Name").fill_null("").str.to_uppercase().alias("Model_upper"),
            pl.col("Panel").fill_null("").str.to_uppercase().alias("Panel_upper")
        )

        GetProfileRow = HEROsFrame_normalized.filter(
            (pl.col("Model_upper") == GetName.upper()) &
            (pl.col("Region_upper") == self.ParseRegion) &
            (pl.col("Panel_upper").str.contains(GetPanel.upper(), literal=True))
        )

        # Accessory Filter
        input_key = GetName.lstrip("0123456789").strip("_")
        acc_model = (
            getAccpart
            .with_columns([
                pl.col("Model Name").str.replace_all(r"^_+|_+$", "").str.replace(r"^\d+", "").alias("model_key")
            ])
            .filter(
                (pl.col("Region") == self.ParseRegion) &
                (pl.lit(input_key).str.starts_with(pl.col("model_key")))
            )
        )

        def normalize_remote_magic(remote_magic, suffix_name):
            if remote_magic is None:
                return remote_magic
            remote_magic = str(remote_magic).strip()
            if str(suffix_name)[1:3].lower() == "ff":
                return remote_magic
            return re.sub(r"\bMR26GA\b", "MR26GC", remote_magic, flags=re.IGNORECASE)

        self.SuffixCountry = self.GetSuffixName[1:3]
        
        if acc_model.height > 0:
            RemoteMagic = acc_model[0, "Magic Remote"]
            self.GetRemoteSR = acc_model[0, "Wifi Name"]
        else:
            RemoteMagic = None
            self.GetRemoteSR = "Unknown"
            self.report["filtering_warnings"].append(f"No accessory model found for input_key: {input_key}, region: {self.ParseRegion}")

        RemoteMagic = normalize_remote_magic(RemoteMagic, self.SuffixCountry)

        # Store final outputs
        self.ModelProfile = GetProfileRow
        self.HEROsFrame = HEROsFrame
        
        if GetProfileRow.height > 0:
            self.GetInch = GetProfileRow[0, "Inch"]
            self.GetSeries = GetProfileRow[0, "Series"]
            self.GetCPunit = GetProfileRow[0, "CP Unit"]
            self.GetGrade = GetProfileRow[0, "Grade"]
            self.GetSoC = GetProfileRow[0, "SoC"]
            self.GetChassis = GetProfileRow[0, "Chassis Name"]
            self.GetPanelName = GetProfileRow[0, "CM00029"]
            self.GetHerosRegion = GetProfileRow[0, "Region"]
        else:
            self.GetInch = self.GetSeries = self.GetCPunit = self.GetGrade = self.GetSoC = self.GetChassis = self.GetPanelName = self.GetHerosRegion = "Unknown"
            self.report["filtering_warnings"].append(f"No HEROs profile found for model: {GetName}, region: {self.ParseRegion}, panel: {GetPanel}")

        self.GetRemoteMR = RemoteMagic

        self.jsonProfile = [{
                "modelYear" : self.model_year,
                "ModelName" : self.targetModel,
                "Inch" : self.GetInch,
                "Series" : self.GetSeries,
                "Region": self.GetHerosRegion,
                "CPunit": self.GetCPunit,
                "SoC": self.GetSoC,
                "Board": self.GetBoardInfo,
                "BoardSuffix": self.GetBoardSuffix,
                "Chassis": self.GetChassis,
                "Panel": self.GetPanelName,
                "RemoteMR": self.GetRemoteMR,
                "RemoteSR": self.GetRemoteSR,
                "Plant": self.GetSubs,
                "ParseRegion": self.ParseRegion,
                "Market": self.ParseMarket,
                "ModelSuffix": self.SuffixCountry,
                "Model_Name": GetName
            }
        ]
        
        # Finalize the report into a JSON string
        self.report_json = json.dumps(self.report, indent=4)


#model_name = "43QNED7EB3C.PEUFLWE"
#profile = Auto_Fast_ModelProfile(model_name)

#st.json(profile.jsonProfile)

