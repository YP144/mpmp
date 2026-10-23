import io
import requests
import pandas as pd
import polars as pl
import json 
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
import time
import logging
import traceback
import threading
from pymongo import MongoClient

from main_function.services.check_sso import SSO_NPDM, NpdmClient
from main_function.services.main_tooloption import run_tooloption, getToolinfo
from main_function.services.subs_hwpart import run_subshwpart

from main_function.compFunctions.check_parts import GetTargetParts
from main_function.compFunctions.compareOperation import compare_operation
from main_function.compFunctions.checx_eax_substitute import compare_under_eax
from main_function.compFunctions.compare_prm import compare_chassis

from main_function.functions.get_subsidiary_bom import getPlantBOM
from main_function.functions.conditioning import zerobom_conditioning
from main_function.functions.tool_option_logic import GetModelToolOptionMaster, ToolOptionCross, compare_tool_option_summary
from main_function.functions.strucFucntions.quickCompare import get_structure_compare
from main_function.functions.profiling.get_partInfo import (
    get_eax_profile, get_ebt_profile
)

from main_function.functions.fast_profile import Fast_ModelProfile
from main_function.functions.searchPart import get_part_profile
from main_function.functions.fast_operationplan import GetOperationPart
from main_function.functions.substate import GoGetTemplate, GetParseStructure, StructureCheck
from main_function.functions.get_init_info import (
    is_valid_model_input,
    normalize_model_input,
    predict_development,
    predict_initial,
    predict_models_callback,
    get_development_model,
    get_initial,
)

from functions.get_hw_main_part import compare_hw_status_process

from main_function.functions.datasend import send_to_pymongo, get_next_version_by_target
from main_function.functions.getdata import mongoURL
from main_function.services.main_hwpart import targetpart_compare, developmentpart_compare, initialpart_compare
from concurrent.futures import ThreadPoolExecutor, as_completed

from compFunctions.compareHWsingle import compare_hw_multi_process
from compFunctions.compareHWmulti import compare_hw_single_process
from compFunctions.compareSubs_New import compare_substitute_bom
from functions.get_data_for_hwoption import hw_multi_option_info, hw_single_option_info



BASE_DIR = Path(__file__).resolve().parent
JSON_DIR = BASE_DIR / "json"

JSON_DIR = Path("json")
logging.basicConfig(
    filename="crosscheck.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(threadName)s | %(message)s"
)


def download_model_ebom(client, model_name: str, plant_unit: str, output_file: str, model_type: str = "unknown"):
    if not model_name:
        logging.warning(f"[{model_type.upper()}] No model name provided. Skipping BOM download.")
        return None

    try:
        ebom = client.get_model_ebom(model_name, plant_unit)
        
        # Check for empty response or invalid payload structure
        if not ebom:
            raise ValueError(
                f"[{model_type.upper()}] API returned an empty or None response for "
                f"Model: '{model_name}' at Plant/Unit: '{plant_unit}'."
            )
        
        if isinstance(ebom, dict) and len(ebom) == 0:
            raise ValueError(
                f"[{model_type.upper()}] API returned empty dictionary {{}} for "
                f"Model: '{model_name}' at Plant/Unit: '{plant_unit}'."
            )

        # Optional: verify 'data' key presence if your API standard mandates it
        if isinstance(ebom, dict) and "data" not in ebom and "bom" not in ebom:
            available_keys = list(ebom.keys())
            raise ValueError(
                f"[{model_type.upper()}] Invalid BOM API response for Model: '{model_name}' (Plant: '{plant_unit}'). "
                f"Missing expected data key. Available keys: {available_keys}. Response: {str(ebom)[:200]}"
            )

        save_json(ebom, output_file)
        return ebom

    except Exception as e:
        logging.error(f"Failed downloading BOM for {model_type} ({model_name} @ {plant_unit}): {str(e)}")
        raise

def save_json(data: dict, file_name: str) -> None:
    JSON_DIR.mkdir(parents=True, exist_ok=True)

    with open(JSON_DIR / file_name, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def run_stage(
    stage_name,
    execution_log,
    exception_log,
    func
):
    start_time = time.perf_counter()

    execution_log.append({
        "stage": stage_name,
        "status": "START",
        "time": datetime.now().isoformat(),
        "thread": threading.current_thread().name
    })

    try:

        result = func()

        elapsed = round(
            time.perf_counter() - start_time,
            2
        )

        execution_log.append({
            "stage": stage_name,
            "status": "SUCCESS",
            "elapsed": elapsed,
            "thread": threading.current_thread().name
        })

        logging.info(
            f"{stage_name} completed in {elapsed}s"
        )

        return result

    except Exception as e:

        elapsed = round(
            time.perf_counter() - start_time,
            2
        )

        execution_log.append({
            "stage": stage_name,
            "status": "FAILED",
            "elapsed": elapsed,
            "thread": threading.current_thread().name,
            "message": str(e)
        })

        exception_log.append({
            "stage": stage_name,
            "exception": type(e).__name__,
            "message": str(e),
            "traceback": traceback.format_exc(),
            "time": datetime.now().isoformat()
        })

        logging.error(
            f"{stage_name} FAILED",
            exc_info=True
        )

        return None

def safe_future(
    future,
    stage_name,
    execution_log,
    exception_log,
    timeout=120
):
    try:

        result = future.result(timeout=timeout)

        execution_log.append({
            "stage": stage_name,
            "status": "SUCCESS",
            "time": datetime.now().isoformat()
        })

        return result

    except Exception as e:

        execution_log.append({
            "stage": stage_name,
            "status": "FAILED",
            "message": str(e),
            "time": datetime.now().isoformat()
        })

        exception_log.append({
            "stage": stage_name,
            "exception": type(e).__name__,
            "message": str(e),
            "traceback": traceback.format_exc(),
            "time": datetime.now().isoformat()
        })

        logging.error(
            f"{stage_name} FAILED",
            exc_info=True
        )

        return None


    except requests.exceptions.RequestException as e:
        print("API Request Failed")
        print(e)

    except Exception as e:
        print("Unexpected error occurred")
        print(e)


def run_compare_json_manual(
    trget,
    dev,
    init,
    modifier_name="System",
    ssolgenet_cookie: str = "",
    smsession_cookie: str = "",
    **kwargs
):
    # Start Logging
    execution_log = []
    exception_log = []
    
    # Time Tracking Dictionary and Helper
    time_processing = {}
    time_lock = threading.Lock()

    def record_time(process_name, start_time):
        elapsed = time.perf_counter() - start_time
        with time_lock:
            time_processing[process_name] = {
                "ms": round(elapsed * 1000, 2),
                "s": round(elapsed, 2),
                "minutes": round(elapsed / 60, 2)
            }

    run_start_time = datetime.now()
    overall_start = time.perf_counter()
    current_time = datetime.now()

    # Extract cookies if passed inside kwargs or directly
    ssolgenet = ssolgenet_cookie or kwargs.get("ssolgenet", "")
    smsession = smsession_cookie or kwargs.get("smsession", "")

    # --- SSO AUTHENTICATION HANDLING ---
    sso = SSO_NPDM()
    sso.check_sso(ssolgenet_cookie=ssolgenet, smsession_cookie=smsession)

    #if ssolgenet or smsession:
        # Pass explicit cookies to your SSO check/login method
    #    is_logged_in = sso.check_sso(ssolgenet_cookie=ssolgenet, smsession_cookie=smsession)
    #else:
        # Fallback to auto_login if no explicit cookies provided
    #    is_logged_in = sso.auto_login()

    #if not is_logged_in or not sso.auth_bearer:
    #    raise PermissionError(
    #        "SSO Authentication failed. Could not retrieve NPDM Bearer Token. Please check your cookies."
    #    )
    
    bearerAuth = sso.auth_bearer

    target_model = trget
    development_model = dev
    initial_model = init

    client = NpdmClient(bearerAuth)

    site_target = "GLZ.EKHQ"
    site_development = get_site_by_model(development_model)
    site_initial = get_site_by_model(initial_model)

    try:
        # ------------------------------------------------------------
        # SLOW PART 1:
        # ------------------------------------------------------------
        def process_target_model():
            start_time = time.perf_counter()
            if not target_model:
                return None

            target_bom = download_model_ebom(
                client=client,
                model_name=target_model,
                plant_unit=site_target,
                output_file="0_target_ebom.json",
                model_type="target",  # <--- Added model_type
            )

            record_time("Process Target Model", start_time)

            return {
                "model_type": "target",
                "bom": target_bom,
            }

        def process_development_model():
            start_time = time.perf_counter()
            if not development_model:
                return None

            development_bom = download_model_ebom(
                client=client,
                model_name=development_model,
                plant_unit=site_development,
                output_file="0_development_ebom.json",
                model_type="development",  # <--- Added model_type
            )

            record_time("Process Development Model", start_time)

            return {
                "model_type": "development",
                "bom": development_bom,
            }

        def process_initial_model():
            start_time = time.perf_counter()
            if not initial_model:
                return None

            initial_bom = download_model_ebom(
                client=client,
                model_name=initial_model,
                plant_unit=site_initial,
                output_file="0_initial_ebom.json",
                model_type="initial",  # <--- Added model_type
            )

            record_time("Process Initial Model", start_time)

            return {
                "model_type": "initial",
                "bom": initial_bom,
            }

        model_tasks = [
            process_target_model,
            process_development_model,
            process_initial_model,
        ]

        model_results = {}

        with ThreadPoolExecutor(max_workers=3) as executor:
            future_map = {
                executor.submit(task): task.__name__
                for task in model_tasks
            }

            for future in as_completed(future_map):
                task_name = future_map[future]

                try:
                    result = future.result()
                    if result:
                        model_results[result["model_type"]] = result
                except Exception as e:

                    exception_log.append({
                        "stage": task_name,
                        "exception": type(e).__name__,
                        "message": str(e),
                        "traceback": traceback.format_exc(),
                        "time": datetime.now().isoformat()
                    })

                    logging.error(
                        f"{task_name} FAILED",
                        exc_info=True
                    )

                    continue
        # ------------------------------------------------------------
        # SLOW PART 2:
        # ------------------------------------------------------------


        def run_subshwpart_task():
            start_time = time.perf_counter()
            res = run_subshwpart().run()
            record_time("Run Subs HW Part", start_time)
            return res

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_subshwpart = executor.submit(run_subshwpart_task)

            subs_hwpart = future_subshwpart.result()

        
 
 
    except requests.exceptions.RequestException as e:
        print("API Request Failed")
        print(e)

    except Exception as e:

        print("Unexpected error occurred")
        print(e)

    # Safe key extraction with default fallbacks
    target_data = model_results.get("target") or {}
    TargetBOM = target_data.get("bom") if isinstance(target_data, dict) else None

    dev_data = model_results.get("development") or {}
    DevBOM = dev_data.get("bom") if isinstance(dev_data, dict) else None

    init_data = model_results.get("initial") or {}
    InitBOM = init_data.get("bom") if isinstance(init_data, dict) else None

    # Guarantee fallback to empty dictionary/list if download returned None
    TargetBOM = TargetBOM if TargetBOM is not None else {}
    DevBOM = DevBOM if DevBOM is not None else {}
    InitBOM = InitBOM if InitBOM is not None else {}

    with open("test_check/output_test.json", "w", encoding="utf-8") as f:
        json.dump(model_results, f, indent=4, ensure_ascii=False, default=str)

    #with open("test_check/output_target.json", "w", encoding="utf-8") as f:
    #   json.dump(TargetBOM, f, indent=4, ensure_ascii=False, default=str)


    start_zerobom = time.perf_counter()
    GetTargetBOM, TargetName = zerobom_conditioning(TargetBOM)
    GetDevBOM, DevName = zerobom_conditioning(DevBOM)
    GetInitBOM, InitName = zerobom_conditioning(InitBOM)
    record_time("ZeroBOM Conditioning", start_zerobom)

    if TargetName == trget:
    
        start_model_state = time.perf_counter()

        # ------------------------------------------------------------
        # SLOW PART 7:
        # ------------------------------------------------------------
        start_profile = time.perf_counter()
        # main_function/compFunctions/main_compare_jsonPure.py

        # Line ~711: Pass cookies into Fast_ModelProfile
        GetProfile = Fast_ModelProfile( 
            trget,
            ssolgenet_cookie=ssolgenet,
            smsession_cookie=smsession
        )
        record_time("Model Profile", start_profile)

        tool_option_output = get_compare_tool_option_result(TargetBOM, DevBOM, InitBOM)
        compare_hw_df, compare_hw_dict = compare_hw_status_process(TargetBOM, DevBOM, InitBOM)

        single_target, single_dev, single_init = hw_single_option_info(GetTargetBOM, GetDevBOM, GetInitBOM, bearerAuth)
        multi_target, multi_dev, multi_init = hw_multi_option_info(GetTargetBOM, GetDevBOM, GetInitBOM, bearerAuth)

        substitute_df, substitute_dict = compare_substitute_bom(
            target=GetTargetBOM,
            dev=GetDevBOM,
            init=GetInitBOM
            
        )
        

        hw_multi_df, hw_multi_dict, hw_mult_result = compare_hw_multi_process(
            mp_json=multi_target,
            dev_json=multi_dev,
            init_json=multi_init
            )
        hw_single_df, hw_single_dict, hw_single_result = compare_hw_single_process(
            mp_json=single_target,
            dev_json=single_dev,
            init_json=single_init
            )
                
        start_plant_bom = time.perf_counter()
        subsidiaryBOM, subsidiaryDicts, model_name = getPlantBOM(trget)
        record_time("Subsidiary BOM", start_plant_bom)

        def task_structure_checkin():
            start_time = time.perf_counter()
            # Pass ssolgenet & smsession into get_structure_compare
            res = get_structure_compare(trget, GetTargetBOM, ssolgenet_cookie=ssolgenet, smsession_cookie=smsession)
            record_time("Structure Compare", start_time)
            return res

        def task_compare_ben():
            start_time = time.perf_counter()
            res = compareBEN_compare()
            record_time("BEN Compare", start_time)
            return res

        def task_compare_ben_tool():
            start_time = time.perf_counter()
            res = compareBENtool()
            record_time("BEN Tool Compare", start_time)
            return res

        def task_compare_hwtool():
            start_time = time.perf_counter()
            res = compare_hwtool()
            record_time("HW Tool Compare", start_time)
            return res

        def task_compare_substitute():
            start_time = time.perf_counter()
            res = compare_substitute()
            record_time("Substitute Compare", start_time)
            return res

        def task_compare_hwmulti():
            start_time = time.perf_counter()
            res = compare_hwmulti()
            record_time("HW Single Option", start_time)
            return res

        def task_compare_hw_multiopt():
            start_time = time.perf_counter()
            res = comparehw_multiopt()
            record_time("HW Multi Option", start_time)
            return res

        def task_compare_operation():
            start_time = time.perf_counter()
            res = compare_operation(
                GetTargetBOM, 
                trget, 
                ssolgenet_cookie=ssolgenet, 
                smsession_cookie=smsession
            )
            record_time("Operation Compare", start_time)
            return res

        def task_compare_tool_option():
            start_time = time.perf_counter()
            res = compare_tool_option_summary(GetTargetBOM, target_model, bearerAuth)
            record_time("Tool Master Compare", start_time)
            return res

        def task_compare_eax_substitute():
            start_time = time.perf_counter()
            res = compare_under_eax(GetTargetBOM, GetProfile.GetSoC)
            record_time("EAX Substitute Compare", start_time)
            return res

        def task_compare_chassis():
            start_time = time.perf_counter()
            res = compare_chassis(GetTargetBOM, GetProfile.GetChassis)
            record_time("Chassis Compare", start_time)
            return res


        with ThreadPoolExecutor(max_workers=11) as executor:
            future_get_structure_compare = executor.submit(task_structure_checkin)
            future_ben = executor.submit(task_compare_ben)
            future_ben_tool = executor.submit(task_compare_ben_tool)
            future_hwtool = executor.submit(task_compare_hwtool)
            future_substitute = executor.submit(task_compare_substitute)
            future_hwmulti = executor.submit(task_compare_hwmulti)
            future_hw_multiopt = executor.submit(task_compare_hw_multiopt)
            future_compare_operation = executor.submit(task_compare_operation)
            future_tool_option_summary = executor.submit(task_compare_tool_option)
            future_compare_eax_substitute = executor.submit(task_compare_eax_substitute)
            future_compare_chassis = executor.submit(task_compare_chassis)
            
            structure_data = safe_future(
                future_get_structure_compare,
                "Structure Compare",
                execution_log,
                exception_log
            )

            if structure_data:
                (
                    joined_result_excel,
                    json_data,
                    compare_matching,
                    result_check
                ) = structure_data
            else:
                joined_result_excel = None
                json_data = {}
                compare_matching = []
                result_check = "NG"


            ben_data = safe_future(
                future_ben,
                "BEN Compare",
                execution_log,
                exception_log
            )

            if ben_data:
                final_df, final_json, ben_result = ben_data
            else:
                final_df = None
                final_json = {}
                ben_result = "CHECK"


            tool_data = safe_future(
                future_ben_tool,
                "BEN Tool Compare",
                execution_log,
                exception_log
            )

            if tool_data:
                tooloption_compare_df, tooloption_json = tool_data
            else:
                tooloption_compare_df = None
                tooloption_json = {}


            hwtool_data = safe_future(
                future_hwtool,
                "HW Tool Compare",
                execution_log,
                exception_log
            )

            if hwtool_data:
                (
                    df_final_partstatus,
                    df_partStatus_json,
                    subs_hwtool_check
                ) = hwtool_data
            else:
                df_final_partstatus = None
                df_partStatus_json = {}
                subs_hwtool_check = "CHECK"


            subs_data = safe_future(
                future_substitute,
                "Substitute Compare",
                execution_log,
                exception_log
            )

            if subs_data:
                (
                    df_final_subs,
                    df_subs_json,
                    subsitute_check_result
                ) = subs_data
            else:
                df_final_subs = None
                df_subs_json = {}
                subsitute_check_result = "CHECK"


            single_data = safe_future(
                future_hwmulti,
                "HW Single Option",
                execution_log,
                exception_log
            )

            if single_data:
                (
                    df_final_singelopt,
                    json_final_singelopt,
                    hwmulti_result
                ) = single_data
            else:
                hwmulti_result = "CHECK"
                json_final_singelopt = {}

            #multi option data compare
            multi_data = safe_future(
                future_hw_multiopt,
                "HW Multi Option",
                execution_log,
                exception_log
            )

            if multi_data:
                (
                    df_final_multiopt,
                    json_final_multiopt,
                    hwsingle_result
                ) = multi_data
            else:
                hwsingle_result = "CHECK"
                json_final_multiopt = {}

            #operation master data compare
            operation_data = safe_future(
                future_compare_operation,
                "Operation Compare",
                execution_log,
                exception_log
            )

            if operation_data:
                (
                    columnsOp,
                    dej_operation,
                    target_operation,
                    operationResult,
                    operationJson,
                    op_result
                ) = operation_data
            else:
                operationJson = {}
                op_result = "NG"

            #tool option master data compare
            toolmaster_data = safe_future(
                future_tool_option_summary,
                "Tool Master Compare",
                execution_log,
                exception_log
            )

            if toolmaster_data:
                (
                    ebt_tool_option,
                    master_tool_option,
                    ebt_tool_json,
                    result_toolMaster
                ) = toolmaster_data
            else:
                ebt_tool_option = None
                master_tool_option = None
                ebt_tool_json = {}
                result_toolMaster = "NG"


            #eax_subsititute compare
            eax_substitute_data = safe_future(
                future_compare_eax_substitute,
                "EAX Substitute Compare",
                execution_log,
                exception_log
            )

            if eax_substitute_data:
                eax_substitute_json = eax_substitute_data
            else:
                eax_substitute_json = {}
                result_eax_substitute = "NG"

            #chassis compare
            compare_chassis_data = safe_future(
                future_compare_chassis,
                "Chassi Compare",
                execution_log,
                exception_log
            )

            if compare_chassis_data:
                compare_chassis_json = compare_chassis_data
            else:
                compare_chassis_json = {}
                result_eax_substitute = "NG"


        targetProfile = GetProfile.jsonProfile

        subs_table_result = (
            "CHECK"
            if subs_hwtool_check == "CHECK" or subsitute_check_result == "CHECK"
            else "OK"
        )

        hwoption_table_result = (
            "CHECK"
            if hwmulti_result == "CHECK" or hwsingle_result == "CHECK"
            else "OK"
        )
        
        overall_table_result = (
            "NG"
            if result_check == "NG" or result_toolMaster == "NG" or op_result == "NG"
            else "OK"
            )

        #Jusgement with Notes

        ng_reasons = []
        check_reasons = []

        checks = {
            "Structure": result_check,
            "HW Compare": ben_result,
            "Substitution Compare": subs_table_result,
            "Multi Option": hwoption_table_result,
            "Tool Option Master": result_toolMaster,
            "Operation Plan": op_result,
        }

        for name, value in checks.items():
            if value == "NG":
                ng_reasons.append(f"{name} (NG)")
            elif value == "CHECK":
                check_reasons.append(f"{name} (CHECK)")

        failure_reasons = ng_reasons

        overall_remark = (
            "; ".join(failure_reasons)
            if failure_reasons
            else "OK"
        )

        run_finish_time = datetime.now()

        duration_seconds = round(
            time.perf_counter() - overall_start,
            2
        )

        successful_stages = len(
            [x for x in execution_log
            if x.get("status") == "SUCCESS"]
        )

        failed_stages = len(
            [x for x in execution_log
            if x.get("status") == "FAILED"]
        )

        #Get Previous Version
        next_version = get_next_version_by_target(
            mongoURL=mongoURL,
            target_name=trget
        )


        

        crosscheckResult = {
            "timestamp": current_time,
            "version": next_version,
            "modifier": modifier_name,   # <--- TAMBAHKAN BARIS INI DI SINI
            "targetName": trget,
            "devName": dev,
            "initName": init,
            "prm_check": {
                "chassis": compare_chassis_json,
            },
            "ModelProfile": {
                "profileData": targetProfile,
            },
            "structureCompare": {
                "result": compare_matching
            },

            "benComapre": {
                "compareHW": final_json,
                "compareTool": tooloption_json,
            },
            "subsCheck": {
                "partStatus": df_partStatus_json,
                "subsJson": df_subs_json,
            },
            "multiOption": {
                "singleOpt": json_final_singelopt,
                "multiOpt": json_final_multiopt,
            },
            "toolOptCompare": {
                "summaryTool": ebt_tool_json,
                "toolSummary": None,
            },
            "eaxSubstitute": eax_substitute_json,
            "OperationPlan": {
                "OperationCheck": operationJson,
            },
            "HWpartCheck" : {
                "chassisName" : compare_chassis_json,
                "ebt_profile": get_part_profile(get_part_list=TargetBOM, part_ref="EBT"),
                "ebr_profile": get_part_profile(get_part_list=TargetBOM, part_ref="EBR"),
                "eax_profile": get_part_profile(get_part_list=TargetBOM, part_ref="EAX"),
                "ebu_profile": get_part_profile(get_part_list=TargetBOM, part_ref="EBU"),
                "ead_profile": get_part_profile(get_part_list=TargetBOM, part_ref="EAD")
            },
            "SummaryResult": {
                "Structure": result_check,
                "HWcompare": ben_result,
                "subsCompare": subs_table_result,
                "multiOption": hwoption_table_result,
                "tooloptionMaster": result_toolMaster,
                "operationPlan": op_result,
                "overallResult": overall_table_result,
                "compareNote": overall_remark
            },
            "SubsidiaryBOM": {
                "modelName": model_name,
                "PlantBOM": subsidiaryDicts
            },
            "ExecutionSummary": {
                "startTime": run_start_time.isoformat(),
                "finishTime": run_finish_time.isoformat(),
                "durationSeconds": duration_seconds,
                "successfulStages": successful_stages,
                "failedStages": failed_stages,
                "warningStages": len(exception_log)
            },
            
            # --- NEW: Added timeProcessing right below ExecutionSummary ---
            "timeProcessing": time_processing,

            "ExecutionLog": execution_log,

            "ExceptionLog": exception_log,
        }

        

        run_stage(
            "MongoDB Save",
            execution_log,
            exception_log,
            lambda: send_to_pymongo(crosscheckResult)
        )

        return crosscheckResult,GetTargetBOM, ebt_tool_option, master_tool_option

    else:
        print(f"Error: Target Model {trget}, but API return {TargetName}")

def get_site_by_model(model_name: str) -> str:
    if model_name.endswith("LCX"):
        return "GLZ.EAIC"
    return "GLZ.EKHQ"