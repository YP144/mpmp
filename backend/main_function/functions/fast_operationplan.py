import re
import threading
from datetime import datetime
from functools import lru_cache
import polars as pl
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# 1. Cache the ModelProfile initialization
@lru_cache(maxsize=32)
def get_cached_profile(target_model: str):
    return ModelProfile(target_model)

class GetOperationPart():
    def __init__(self, targetModel: str):
        self.targetModel = targetModel
        self.getOPpart()

    def getOPpart(self):
        # Use the cached profile to avoid redundant API/DB calls
        profile = get_cached_profile(self.targetModel)
        model_name = profile.targetModel
        model_plant = profile.GetSubs
        model_region = profile.GetRegionSuffix
        model_suffix = profile.GetSuffixName
        model_series = profile.GetSeries
        model_inch = profile.GetInch

        def safe_item(df: pl.DataFrame, column: str, default: str = "Not Found"):
            if df is not None and df.height > 0 and column in df.columns:
                value = df.item(0, column)
                if value is None:
                    return default
                return value
            return default

        # 2. Push filtering to the SQL query by adding a where_clause parameter
        def read_latest_version(
            db_uri: str,
            prefix: str = "2026YHWplan_v",
            schema: str = "public",
            where_clause: str = None
        ) -> pl.DataFrame:
            tables_df = pl.read_database_uri(
                query=f"""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = '{schema}'
                    AND table_name LIKE '{prefix}%'
                """,
                uri=db_uri,
            )

            versions = []
            for table_name in tables_df["table_name"].to_list():
                match = re.match(rf"^{re.escape(prefix)}(\d+)_(\d+)$", table_name)
                if match:
                    major = int(match.group(1))
                    minor = int(match.group(2))
                    versions.append((major, minor, table_name))

            if not versions:
                raise Exception(f"No versioned table found with prefix: {prefix}")

            latest_major, latest_minor, latest_table = max(
                versions,
                key=lambda x: (x[0], x[1])
            )

            query = f'SELECT * FROM {schema}."{latest_table}"'
            
            # Apply the SQL filter before downloading the data
            if where_clause:
                query += f" WHERE {where_clause}"

            df = pl.read_database_uri(
                query=query,
                uri=db_uri,
            )
            return df, latest_table

        # ==========================================
        # Fetch Databases Concurrently with SQL Filtering
        # ==========================================
        with ThreadPoolExecutor(max_workers=2) as db_executor:
            future_op = db_executor.submit(read_latest_version, OPurl)
            
            # Push the Region filter directly to the SQL query to reduce network load
            region_filter = f"\"Region\" = '{profile.GetHerosRegion}'"
            future_acc = db_executor.submit(read_latest_version, AccMaster, "HEROacc2026Y_v4.3_v", "public", region_filter)

            GetOPlist, latest_table = future_op.result()
            GetAccMaster, LatestAccMaster = future_acc.result()

        # Process OPlist
        GetOPlist = GetOPlist.with_columns(
            pl.col("suffixHq").str.to_lowercase()
        )
        
        self.latest_version = latest_table
        self.region_operationPlan = profile.GetRegionSuffix

        # 3. Optimize fuzzy matching (Pre-filtering is now done in SQL above)
        # Note: Ensure your external `find_nearest_model_name_match` uses `rapidfuzz` internally for best performance.
        firstModelName = profile.firstModelName
        all_match_result, show_top_3_matches, nearest_match = find_nearest_model_name_match(
            df=GetAccMaster,
            input_model=firstModelName,
            model_col="Model Name",
            top_n=3,
            min_score=40
        )

        model_remote = nearest_match.item(0, "Magic Remote")

        def replace_mr26ga_to_mr26gc(text):
            if text is None:
                return text
            return str(text).replace("MR26GA", "MR26GC")
                
        model_remote = replace_mr26ga_to_mr26gc(model_remote)

        # ==========================================
        # 4. Parse Parts Concurrently using ProcessPoolExecutor
        # ==========================================
        battery_part_no = "EAC" if profile.GetRegionSuffix in ["tt", "ts"] else "6910VA"

        # Using ProcessPoolExecutor for CPU-bound tasks to bypass the GIL
        # We submit the external function directly to avoid pickling issues with nested functions
        with ProcessPoolExecutor(max_workers=7) as part_executor:
            future_remote = part_executor.submit(parse_part_number_polars, GetOPlist, "AKB", profile.targetModel, model_plant, model_region.upper(), model_suffix.upper(), model_series, model_inch, "partNo", False)
            future_speaker = part_executor.submit(parse_part_number_polars, GetOPlist, "EAB", profile.targetModel, model_plant, model_region.upper(), model_suffix.upper(), model_series, model_inch, "partNo", False)
            future_powercord = part_executor.submit(parse_part_number_polars, GetOPlist, "EAD", profile.targetModel, model_plant, model_region.upper(), model_suffix.upper(), model_series, model_inch, "partNo", False)
            future_edid = part_executor.submit(parse_part_number_polars, GetOPlist, "ECC", profile.targetModel, model_plant, model_region.upper(), model_suffix.upper(), model_series, model_inch, "partNo", False)
            future_heatplate = part_executor.submit(parse_part_number_polars, GetOPlist, "EBS", profile.targetModel, model_plant, model_region.upper(), model_suffix.upper(), model_series, model_inch, "partNo", False)
            future_wifi = part_executor.submit(parse_part_number_polars, GetOPlist, "EAT", profile.targetModel, model_plant, model_region.upper(), model_suffix.upper(), model_series, model_inch, "partNo", False)
            future_battery = part_executor.submit(parse_part_number_polars, GetOPlist, battery_part_no, profile.targetModel, model_plant, model_region.upper(), model_suffix.upper(), model_series, model_inch, "partNo", False)

            OpRemote_judge_result, OpRemote = future_remote.result()
            speaker_judge_result, OpSpeaker = future_speaker.result()
            powercord_judge_result, OpPowerCord = future_powercord.result()
            edid_judge_result, OpEdid = future_edid.result()
            heatplate_judge_result, OpHeatPlate = future_heatplate.result()
            wifi_judge_result, OpWifi = future_wifi.result()
            battery_judge_result, OpBattery = future_battery.result()

        # ==========================================
        # Apply Specific Logic & Add Categories
        # ==========================================
        
        # Remote Logic
        remote_code = model_remote.replace("Metallic", "").strip()
        is_metallic = "Metallic" in model_remote

        base_filter = (
            pl.col("raw_masterRemark")
            .cast(pl.Utf8)
            .str.strip_chars()
            .str.contains(rf"^{re.escape(remote_code)}(\s|$)")
        )

        if is_metallic:
            OpRemote = OpRemote.filter(
                base_filter & pl.col("raw_masterRemark").cast(pl.Utf8).str.contains(r"(?i)\bMetallic\b")
            )
        else:
            OpRemote = OpRemote.filter(
                base_filter & ~pl.col("raw_masterRemark").cast(pl.Utf8).str.contains(r"(?i)\bMetallic\b")
            )

        # Add Categories
        OpRemote = OpRemote.with_columns(pl.lit("Remote").alias("Category"))
        OpSpeaker = OpSpeaker.with_columns(pl.lit("Speaker").alias("Category"))
        OpPowerCord = OpPowerCord.with_columns(pl.lit("Power Cord").alias("Category"))
        OpEdid = OpEdid.with_columns(pl.lit("EDID").alias("Category"))
        OpHeatPlate = OpHeatPlate.with_columns(pl.lit("Heat Plate").alias("Category"))
        OpWifi = OpWifi.with_columns(pl.lit("WiFi").alias("Category"))
        OpBattery = OpBattery.with_columns(pl.lit("Battery").alias("Category"))

        # ==========================================
        # Finalize and Send Report
        # ==========================================
        self.OperationGet = pl.concat([
            OpRemote, OpBattery, OpEdid, OpHeatPlate, OpPowerCord, OpSpeaker, OpWifi
        ])

        opertionPlanMacthReport = {
            "timestamp": datetime.now(),
            "miseEnPlace": {
                "operationPlan": latest_table,
                "accMaster": LatestAccMaster,
                "modelName": profile.targetModel,
                "model_name": firstModelName,
                "suffixName": model_suffix,
                "regionName": model_region,
                "model_remote": model_remote,
                "profile": profile.jsonProfile,
                "accChosen": (
                    nearest_match.to_dicts()
                    if isinstance(nearest_match, pl.DataFrame)
                    else [{"nearest_match": str(nearest_match)}]
                )
            },
            "Remote": {
                "partNo": "AKB",
                "AllmatchReport": OpRemote_judge_result.to_dicts(),
                "matchReport": OpRemote.to_dicts()
            },
            "Speaker": {
                "partNo": "EAB",
                "AllmatchReport": speaker_judge_result.to_dicts(),
                "matchReport": OpSpeaker.to_dicts()
            },
            "PowerCord": {
                "partNo": "EAD",
                "AllmatchReport": powercord_judge_result.to_dicts(),
                "matchReport": OpPowerCord.to_dicts()
            },
            "Edid": {
                "partNo": "ECC",
                "AllmatchReport": edid_judge_result.to_dicts(),
                "matchReport": OpEdid.to_dicts()
            },
            "HeatPlate": {
                "partNo": "EBS",
                "AllmatchReport": heatplate_judge_result.to_dicts(),
                "matchReport": OpHeatPlate.to_dicts()
            },
            "WiFi": {
                "partNo": "EAT",
                "AllmatchReport": wifi_judge_result.to_dicts(),
                "matchReport": OpWifi.to_dicts()
            },
            "Battery": {
                "partNo": "69VA10/EAC",
                "AllmatchReport": battery_judge_result.to_dicts(),
                "matchReport": OpBattery.to_dicts()
            }
        }

        # 5. Run MongoDB saving in the background (fire-and-forget)
        threading.Thread(
            target=send_to_pymongo_generic, 
            args=(opertionPlanMacthReport, "operationMatch"), 
            daemon=True
        ).start()

        self.OperationGet = self.OperationGet.with_row_index(name="row_number")