# main_function/compFunctions/compare_library.py
import json
import traceback
from datetime import datetime
import psycopg2
from psycopg2 import Error, sql

from main_function.functions.getdata import masterDataURL
from main_function.compFunctions.run_crosschecking_manual import run_compare_json_manual
from main_function.compFunctions.run_crosschecking_mybom_fx import run_compare_json_mybom


def comapre_db_update(
    trget: str,
    dev: str = "",
    init: str = "",
    ssolgenet_cookie: str = "",
    smsession_cookie: str = "",
    **kwargs,
):
    """Executes the core BOM comparison pipeline and persists results into PostgreSQL.

    Guarantees exception handling and connection cleanups so bad targets do not cause HTTP 500.
    """
    ssolgenet = ssolgenet_cookie or kwargs.get("ssolgenet", "")
    smsession = smsession_cookie or kwargs.get("smsession", "")

    crosscheckResult = {}
    GetTargetBOM = {}
    db_report = {
        "status": "pending",
        "message": "",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mp_model": trget,
        "target_table": "resultmain",
    }

    # 1. Safely execute JSON comparison pipeline
    try:
        try:
            crosscheckResult, GetTargetBOM = (
                run_compare_json_mybom(
                    trget,
                    dev,
                    init,
                    ssolgenet_cookie=ssolgenet,
                    smsession_cookie=smsession,
                )
            )
        except TypeError:
            crosscheckResult, GetTargetBOM = (
                run_compare_json_mybom(trget, dev, init)
            )
    except Exception as pipe_err:
        err_msg = f"Comparison pipeline execution failed for {trget}: {str(pipe_err)}"
        print(f"--- ERROR in run_compare_json ({trget}) ---\n{traceback.format_exc()}", flush=True)
        db_report["status"] = "error"
        db_report["message"] = err_msg
        
        fallback_result = {
            "targetName": trget,
            "version": 1.0,
            "SummaryResult": {"overallResult": "NG", "compareNote": err_msg},
            "ExecutionLog": [{
                "stage": "BOM Comparison Pipeline",
                "status": "FAILURE",
                "error": str(pipe_err)
            }]
        }
        return fallback_result, {}, db_report

    # Extract parsed properties safely with structural defaults
    mpModel_val = crosscheckResult.get("targetName", trget) or trget
    devModel_val = crosscheckResult.get("devName", dev) or dev
    initModel_val = crosscheckResult.get("initName", init) or init

    get_version = crosscheckResult.get("version", 1.0)
    get_overall_result = crosscheckResult.get("SummaryResult") or {}

    structure_val = get_overall_result.get("Structure", "")
    benCompare_val = get_overall_result.get("HWcompare", "")
    subsCheck_val = get_overall_result.get("subsCompare", "")
    multiOption_val = get_overall_result.get("multiOption", "")
    toolOptCompare_val = get_overall_result.get("tooloptionMaster", "")
    operationPlan_val = get_overall_result.get("operationPlan", "")
    overallResult_val = get_overall_result.get("overallResult", "NG")
    compareNote_val = get_overall_result.get("compareNote", "")

    # Safely extract engineer metadata without nested KeyErrors
    model_profile = crosscheckResult.get("ModelProfile") or {}
    profile_list = model_profile.get("profileData") or [{}]
    profile_data = profile_list[0] if isinstance(profile_list, list) and len(profile_list) > 0 else {}
    
    user_info = profile_data.get("user-info") or {}
    engineer_checkouter = user_info.get("retest-userId", "SYS.AUTO")

    curr_date = datetime.now()
    table_name = "resultmain"
    db_report["mp_model"] = mpModel_val

    # 2. Database Upsert with isolated transaction management
    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(masterDataURL)
        cursor = connection.cursor()

        check_query = sql.SQL(
            'SELECT 1 FROM {table} WHERE "mp model" = %s'
        ).format(table=sql.Identifier(table_name))
        cursor.execute(check_query, (mpModel_val,))
        record_exists = cursor.fetchone()

        if record_exists:
            update_query = sql.SQL(
                """
                UPDATE {table} SET 
                    "dev model" = %s, "initial model" = %s, "version" = %s, 
                    "structure" = %s, "benComp" = %s, "substitute_check" = %s, 
                    "hwTool" = %s, "tool_option" = %s, "operation_plan" = %s, 
                    "result" = %s, "compare_note" = %s, "engineer_checkouter" = %s, 
                    "bom_checking_time" = %s, "bom_last_checker" = %s
                WHERE "mp model" = %s
            """
            ).format(table=sql.Identifier(table_name))

            update_values = (
                devModel_val,
                initModel_val,
                get_version,
                structure_val,
                benCompare_val,
                subsCheck_val,
                multiOption_val,
                toolOptCompare_val,
                operationPlan_val,
                overallResult_val,
                compareNote_val,
                engineer_checkouter,
                curr_date,
                curr_date,
                mpModel_val,
            )
            cursor.execute(update_query, update_values)
            db_report["message"] = f"Successfully updated record for MP Model: {mpModel_val}"
        else:
            insert_query = sql.SQL(
                """
                INSERT INTO {table} (
                    "mp model", "dev model", "initial model", "version", 
                    "structure", "benComp", "substitute_check", "hwTool", 
                    "tool_option", "operation_plan", "result", "compare_note", 
                    "engineer_checkouter", "bom_checking_time", "bom_last_checker"
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            ).format(table=sql.Identifier(table_name))

            insert_values = (
                mpModel_val,
                devModel_val,
                initModel_val,
                get_version,
                structure_val,
                benCompare_val,
                subsCheck_val,
                multiOption_val,
                toolOptCompare_val,
                operationPlan_val,
                overallResult_val,
                compareNote_val,
                engineer_checkouter,
                curr_date,
                curr_date,
            )
            cursor.execute(insert_query, insert_values)
            db_report["message"] = f"Successfully inserted new record for MP Model: {mpModel_val}"

        connection.commit()
        db_report["status"] = "success"

    except (Exception, Error) as error:
        if connection:
            connection.rollback()
        db_report["status"] = "error"
        db_report["message"] = f"Database error for {mpModel_val}: {str(error)}"
        print(f"--- DB ERROR ({mpModel_val}) --- {error}", flush=True)

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return crosscheckResult, GetTargetBOM, db_report


def comapre_db_update_manual(
    trget: str,
    dev: str = "",
    init: str = "",
    ssolgenet_cookie: str = "",
    smsession_cookie: str = "",
    **kwargs,
):
    """Executes manual core BOM comparison pipeline safely and persists into PostgreSQL.

    Guarantees exception handling and connection cleanups so bad targets do not cause HTTP 500.
    """
    ssolgenet = ssolgenet_cookie or kwargs.get("ssolgenet", "")
    smsession = smsession_cookie or kwargs.get("smsession", "")

    crosscheckResult = {}
    GetTargetBOM = {}
    db_report = {
        "status": "pending",
        "message": "",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mp_model": trget,
        "target_table": "resultmain",
    }

    try:
        try:
            crosscheckResult, GetTargetBOM, ebt_tool_option, master_tool_option = (
                run_compare_json_manual(
                    trget,
                    dev,
                    init,
                    ssolgenet_cookie=ssolgenet,
                    smsession_cookie=smsession,
                )
            )
        except TypeError:
            crosscheckResult, GetTargetBOM, ebt_tool_option, master_tool_option = (
                run_compare_json_manual(trget, dev, init)
            )
    except Exception as pipe_err:
        err_msg = f"Manual comparison pipeline execution failed for {trget}: {str(pipe_err)}"
        print(f"--- ERROR in run_compare_json_manual ({trget}) ---\n{traceback.format_exc()}", flush=True)
        db_report["status"] = "error"
        db_report["message"] = err_msg
        
        fallback_result = {
            "targetName": trget,
            "version": 1.0,
            "SummaryResult": {"overallResult": "NG", "compareNote": err_msg},
            "ExecutionLog": [{
                "stage": "BOM Manual Comparison Pipeline",
                "status": "FAILURE",
                "error": str(pipe_err)
            }]
        }
        return fallback_result, {}, db_report

    # Extract parsed properties safely with structural defaults
    mpModel_val = crosscheckResult.get("targetName", trget) or trget
    devModel_val = crosscheckResult.get("devName", dev) or dev
    initModel_val = crosscheckResult.get("initName", init) or init

    get_version = crosscheckResult.get("version", 1.0)
    get_overall_result = crosscheckResult.get("SummaryResult") or {}

    structure_val = get_overall_result.get("Structure", "")
    benCompare_val = get_overall_result.get("HWcompare", "")
    subsCheck_val = get_overall_result.get("subsCompare", "")
    multiOption_val = get_overall_result.get("multiOption", "")
    toolOptCompare_val = get_overall_result.get("tooloptionMaster", "")
    operationPlan_val = get_overall_result.get("operationPlan", "")
    overallResult_val = get_overall_result.get("overallResult", "NG")
    compareNote_val = get_overall_result.get("compareNote", "")

    model_profile = crosscheckResult.get("ModelProfile") or {}
    profile_list = model_profile.get("profileData") or [{}]
    profile_data = profile_list[0] if isinstance(profile_list, list) and len(profile_list) > 0 else {}
    
    user_info = profile_data.get("user-info") or {}
    engineer_checkouter = user_info.get("retest-userId", "SYS.MANUAL")

    curr_date = datetime.now()
    table_name = "resultmain"
    db_report["mp_model"] = mpModel_val

    # Database Upsert with isolated transaction management
    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(masterDataURL)
        cursor = connection.cursor()

        check_query = sql.SQL(
            'SELECT 1 FROM {table} WHERE "mp model" = %s'
        ).format(table=sql.Identifier(table_name))
        cursor.execute(check_query, (mpModel_val,))
        record_exists = cursor.fetchone()

        if record_exists:
            update_query = sql.SQL(
                """
                UPDATE {table} SET 
                    "dev model" = %s, "initial model" = %s, "version" = %s, 
                    "structure" = %s, "benComp" = %s, "substitute_check" = %s, 
                    "hwTool" = %s, "tool_option" = %s, "operation_plan" = %s, 
                    "result" = %s, "compare_note" = %s, "engineer_checkouter" = %s, 
                    "bom_checking_time" = %s, "bom_last_checker" = %s
                WHERE "mp model" = %s
            """
            ).format(table=sql.Identifier(table_name))

            update_values = (
                devModel_val,
                initModel_val,
                get_version,
                structure_val,
                benCompare_val,
                subsCheck_val,
                multiOption_val,
                toolOptCompare_val,
                operationPlan_val,
                overallResult_val,
                compareNote_val,
                engineer_checkouter,
                curr_date,
                curr_date,
                mpModel_val,
            )
            cursor.execute(update_query, update_values)
            db_report["message"] = f"Successfully updated manual record for MP Model: {mpModel_val}"
        else:
            insert_query = sql.SQL(
                """
                INSERT INTO {table} (
                    "mp model", "dev model", "initial model", "version", 
                    "structure", "benComp", "substitute_check", "hwTool", 
                    "tool_option", "operation_plan", "result", "compare_note", 
                    "engineer_checkouter", "bom_checking_time", "bom_last_checker"
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            ).format(table=sql.Identifier(table_name))

            insert_values = (
                mpModel_val,
                devModel_val,
                initModel_val,
                get_version,
                structure_val,
                benCompare_val,
                subsCheck_val,
                multiOption_val,
                toolOptCompare_val,
                operationPlan_val,
                overallResult_val,
                compareNote_val,
                engineer_checkouter,
                curr_date,
                curr_date,
            )
            cursor.execute(insert_query, insert_values)
            db_report["message"] = f"Successfully inserted new manual record for MP Model: {mpModel_val}"

        connection.commit()
        db_report["status"] = "success"

    except (Exception, Error) as error:
        if connection:
            connection.rollback()
        db_report["status"] = "error"
        db_report["message"] = f"Database error for {mpModel_val}: {str(error)}"
        print(f"--- DB ERROR MANUAL ({mpModel_val}) --- {error}", flush=True)

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return crosscheckResult, GetTargetBOM, db_report