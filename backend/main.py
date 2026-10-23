# backend/main.py
import asyncio
import json
import traceback
from datetime import date, datetime
from typing import Optional, Union, List
import logging
from uuid import uuid4
from typing import Optional, Dict, Any

from bson import ObjectId
from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from pymongo.errors import PyMongoError
import traceback

from db.database import get_dej_db_connection 
from db.mongoRepo import (
    fetch_latest_mongo_result,
    fetch_latest_mongo_result_profile,
    send_to_pymongo_generic
)
from main_function.compFunctions.compare_library import comapre_db_update, comapre_db_update_manual
from main_function.functions.production.get_production import get_current_production_date

from utils.auth import check_user
from test import get_bom_api

def log_api_error(
    *,
    endpoint: str,
    stage: str,
    error: Exception,
    model_name: str | None = None,
    request_id: str | None = None,
):
    # Always write to the server log first.
    logger.exception(
        "API failure: endpoint=%s stage=%s model=%s request_id=%s",
        endpoint,
        stage,
        model_name,
        request_id,
        exc_info=(
            type(error),
            error,
            error.__traceback__,
        ),
    )

    error_document = {
        "timestamp": datetime.now(timezone.utc),
        "endpoint": endpoint,
        "stage": stage,
        "model_name": model_name,
        "request_id": request_id,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": "".join(
            traceback.format_exception(
                type(error),
                error,
                error.__traceback__,
            )
        ),
    }

    try:
        send_to_pymongo_generic(error_document, "overReport")
    except Exception:
        # Do not let a MongoDB logging failure hide the original error.
        logger.exception("Failed to save API error to MongoDB")


app = FastAPI(
    title="MPX API",
    description="Backend API for the MPX System",
    version="0.1.0",
)

# --------------------------------------------------
# CORS
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://mpxo--3000--yudhis-ranggawidjaya.apps.axstudio.lge.com",
        "https://mpxo-dev.apps.axstudio.lge.com/",
        "https://mpxo.apps.axstudio.lge.com/",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Helpers
# --------------------------------------------------
def mongo_json_safe(value):
    if isinstance(value, ObjectId):
        return str(value)

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, list):
        return [mongo_json_safe(item) for item in value]

    if isinstance(value, dict):
        return {str(key): mongo_json_safe(val) for key, val in value.items()}

    return value

NOTIFICATION_DB_INDEX = 0
NOTIFICATION_DATABASE = "MasterMP_Data"
NOTIFICATION_QUERIES = {
    "summaryTeam": 'SELECT * FROM "public"."summary_team"',
    "summaryUser": 'SELECT * FROM "public"."summary_user"',
}


def _fetch_rows(cursor, query):
    cursor.execute(query)
    rows = cursor.fetchall()
    if rows and not isinstance(rows[0], dict):
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in rows]
    return [dict(row) for row in rows]


class AuthUser(BaseModel):
    userId: Optional[str] = ""
    userIc: Optional[str] = ""
    authBearer: Optional[str] = ""
    smsession: Optional[str] = ""
    ssolgenet: Optional[str] = ""

class ModelRequests(BaseModel):
    targetModel: str

class CrosscheckRequests(BaseModel):
    ssolgenet_cookie: Optional[str] = ""
    smsession_cookie: Optional[str] = ""
    targetModel: Union[str, List[str]]
    devModel: Optional[str] = ""
    initModel: Optional[str] = ""

class ProductionList(BaseModel):
    ssolgenet_cookie: str
    smsession_cookie: str

class RemarkCrosschecking(BaseModel):
    crosschecking_result: Optional[Dict[str, Any]] = None


@app.post("/api/sendremark")
async def post_remark_result(request: RemarkCrosschecking):
    if not request.crosschecking_result:
        raise HTTPException(status_code=400, detail="crosschecking_result payload cannot be empty.")
    
    print(">>> RECEIVED REMARK CROSSCHECKING DATA:")
    #print(request.crosschecking_result)
    
    with open("./test_check/remark_json_12.json", "w", encoding="utf-8") as f:
        json.dump(request.crosschecking_result, f, indent=4, ensure_ascii=False)

    #send_to_pymongo_generic(request.crosschecking_result, "result27Y")
    

    # Process or persist updated crosschecking results here
    
    return {
        "status": "success",
        "message": "Remark and crosschecking state saved successfully.",
        #"received_data": request.crosschecking_result
    }

@app.on_event("startup")
async def startup_db_client():
    # Force pool initialization / test ping on application start
    try:
        async with get_dej_db_connection(NOTIFICATION_DB_INDEX, database=NOTIFICATION_DATABASE) as (conn, cursor):
            if cursor:
                cursor.execute("SELECT 1;")
        print("--- Database pool pre-warmed successfully ---", flush=True)
    except Exception as e:
        print(f"--- Startup DB Warmup Warning: {e} ---", flush=True)

@app.get("/")
async def root():
    return {"status": "online", "message": "FastAPI Authentication Service is running"}

@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/authentication")
async def check_authentication(request: AuthUser):
    try:
        print(f"--- DEBUG /api/authentication received: userId={request.userId}, userIc={request.userIc} ---", flush=True)
        auth_state = check_user(userId=request.userIc, userIc=request.userId)


        auth_state["userEmpNo"] = "IC130073"

        return auth_state
    except Exception as e:
        print(f"--- ERROR in check_authentication: {str(e)} ---", flush=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/notification")
async def get_notification():
    try:
        async with get_dej_db_connection(
            NOTIFICATION_DB_INDEX, database=NOTIFICATION_DATABASE
        ) as (conn, cursor):
            if cursor is None:
                raise HTTPException(
                    status_code=500,
                    detail=f"DB index {NOTIFICATION_DB_INDEX} is not a SQL database",
                )
            result = {}
            for key, query in NOTIFICATION_QUERIES.items():
                result[key] = await asyncio.to_thread(_fetch_rows, cursor, query)
    except HTTPException:
        raise
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch notification data: {e}")

    return jsonable_encoder(mongo_json_safe(result))


@app.post("/api/bom/model_profile")
def get_latest_result(request: ModelRequests):
    doc = fetch_latest_mongo_result_profile(request.targetModel)
    if not doc:
        raise HTTPException(
            status_code=404,
            detail=f"No model profile result found for targetModel='{request.targetModel}'",
        )
    return jsonable_encoder(mongo_json_safe(doc))


@app.post("/api/bom/retest")
async def retest_model(request: CrosscheckRequests, http_request: Request):
    request_id = str(uuid4())
    stage = "initialization"

    try:
        ssolgenet = request.ssolgenet_cookie or http_request.cookies.get("ssolgenet") or ""
        smsession = request.smsession_cookie or http_request.cookies.get("SMSESSION") or ""

        if isinstance(request.targetModel, str):
            target_list = [m.strip() for m in request.targetModel.split(",") if m.strip()]
        else:
            target_list = request.targetModel or []

        if not target_list:
            return {
                "status": "error",
                "total_processed": 0,
                "results": [{
                    "status": "error",
                    "message": "At least one targetModel must be provided.",
                    "get_result": "NG",
                    "all_result": {"overallResult": "NG"}
                }]
            }

        retest_results = []
        
        for current_target in target_list:
            try:
                crosscheckResult, GetTargetBOM, db_report = await asyncio.to_thread(
                    comapre_db_update,
                    current_target,
                    request.devModel,
                    request.initModel,
                    ssolgenet_cookie=ssolgenet,
                    smsession_cookie=smsession
                )

                get_version = crosscheckResult.get("version", 1.0)
                get_summary_result = crosscheckResult.get("SummaryResult", {})
                get_result = get_summary_result.get("overallResult", "NG")
                getExecutionLog = crosscheckResult.get("ExecutionLog", [])

                mp_model_val = (
                    db_report.get("mp_model") 
                    if isinstance(db_report, dict) and "mp_model" in db_report 
                    else current_target
                )

                retest_results.append({
                    "status": "success",
                    "message": f"Retest completed for MP Model: {current_target}",
                    "report": db_report,
                    "version": get_version,
                    "mp_mode": mp_model_val,
                    "get_result": get_result.capitalize() if isinstance(get_result, str) else get_result,
                    "all_result": get_summary_result,
                    "exceptionLog": getExecutionLog
                })
            except Exception as e:
                error_traceback = traceback.format_exc()
                #print(f"--- DIAGNOSTIC ERROR for {current_target} --- \n{error_traceback}", flush=True)
                
                retest_results.append({
                    "status": "error",
                    "message": f"Error processing target model {current_target}: {str(e)}",
                    "mp_mode": current_target,
                    "version": 1.0,
                    "get_result": "NG",
                    "all_result": {"overallResult": "NG"},
                    "exceptionLog": [
                        {
                            "stage": "Execution Pipeline",
                            "status": "FAILURE",
                            "error": str(e),
                            "traceback": error_traceback
                        }
                    ]
                })

      
        #get_bom_api(ssolgenet, smsession)

        return {
            "status": "success",
            "total_processed": len(retest_results),
            "results": retest_results
        }


    except Exception as exc:
        log_api_error(
            endpoint="/api/bom/retest",
            stage=stage,
            error=exc,
            model_name=request.model_name,
            request_id=request_id,
        )

        raise HTTPException(
            status_code=500,
            detail={
                "message": "BOM retest failed.",
                "request_id": request_id,
            },
        )


@app.post("/api/bom/retest_manual")
async def retest_model_manual(request: CrosscheckRequests, http_request: Request):
    ssolgenet = request.ssolgenet_cookie or http_request.cookies.get("ssolgenet") or ""
    smsession = request.smsession_cookie or http_request.cookies.get("SMSESSION") or ""

    if isinstance(request.targetModel, str):
        target_list = [m.strip() for m in request.targetModel.split(",") if m.strip()]
    else:
        target_list = request.targetModel or []

    if not target_list:
        return {
            "status": "error",
            "total_processed": 0,
            "results": [{
                "status": "error",
                "message": "At least one targetModel must be provided.",
                "get_result": "NG",
                "all_result": {"overallResult": "NG"}
            }]
        }

    retest_results = []

    for current_target in target_list:
        attempts = 0
        max_attempts = 2  # Retry once on cold-start/stale connection failure
        
        while attempts < max_attempts:
            attempts += 1
            try:
                crosscheckResult, GetTargetBOM, db_report = await asyncio.to_thread(
                    comapre_db_update_manual,
                    current_target,
                    request.devModel,
                    request.initModel,
                    ssolgenet_cookie=ssolgenet,
                    smsession_cookie=smsession
                )
                
                get_version = crosscheckResult.get("version", 1.0) if isinstance(crosscheckResult, dict) else 1.0
                get_summary_result = crosscheckResult.get("SummaryResult") if isinstance(crosscheckResult, dict) else {}
                if not get_summary_result:
                    get_summary_result = {"overallResult": "NG"}

                get_result = get_summary_result.get("overallResult", "NG")
                getExecutionLog = crosscheckResult.get("ExecutionLog") if isinstance(crosscheckResult, dict) else []

                mp_model_val = (
                    db_report.get("mp_model") 
                    if isinstance(db_report, dict) and "mp_model" in db_report 
                    else current_target
                )

                is_success = isinstance(db_report, dict) and db_report.get("status") != "error"

                retest_results.append({
                    "status": "success" if is_success else "error",
                    "message": db_report.get("message") if isinstance(db_report, dict) else f"Retest finished for {current_target}",
                    "report": db_report,
                    "version": get_version,
                    "mp_mode": mp_model_val,
                    "get_result": get_result.capitalize() if isinstance(get_result, str) else get_result,
                    "all_result": get_summary_result,
                    "exceptionLog": getExecutionLog or []
                })
                break  # Success, exit retry loop
                
            except Exception as e:
                error_traceback = traceback.format_exc()
                print(f"--- DIAGNOSTIC CATCH (Attempt {attempts}/{max_attempts}) for {current_target} --- \n{error_traceback}", flush=True)
                
                if attempts < max_attempts:
                    await asyncio.sleep(0.5)  # Brief pause before retrying cold-start DB connection
                    continue

                retest_results.append({
                    "status": "error",
                    "message": f"Error processing target model {current_target}: {str(e)}",
                    "mp_mode": current_target,
                    "version": 1.0,
                    "get_result": "NG",
                    "all_result": {"overallResult": "NG"},
                    "exceptionLog": [
                        {
                            "stage": "Execution Pipeline",
                            "status": "FAILURE",
                            "error": str(e),
                            "traceback": error_traceback
                        }
                    ]
                })

    return {
        "status": "success",
        "total_processed": len(retest_results),
        "results": retest_results
    }

@app.post("/api/bom/view_result")
def view_result_model(request: CrosscheckRequests):
    if not request.targetModel:
        raise HTTPException(status_code=400, detail="targetModel is required")

    target_str = request.targetModel[0] if isinstance(request.targetModel, list) else request.targetModel
    doc = fetch_latest_mongo_result(target_str)
    if not doc:
        raise HTTPException(
            status_code=404,
            detail=f"No view_result found for targetModel='{target_str}'",
        )

    safe_doc = mongo_json_safe(doc)
    return jsonable_encoder(safe_doc)


@app.post("/api/bom/get_production")
def get_production_list(request: ProductionList):
    result = get_current_production_date(
        ssolgenet_cookie=request.ssolgenet_cookie,
        smsession_cookie=request.smsession_cookie
    )

    if isinstance(result, list):
        return {
            "success": True,
            "data": result,
            "diagnostics": {"total_parsed_rows": len(result)}
        }

    diag = result.get("diagnostics", {})
    logging.info(
        f"Scrape completed | Success: {result.get('success')} | "
        f"Parsed Rows: {diag.get('total_parsed_rows')} | "
        f"Final Rows: {diag.get('final_rows_after_dedup')}"
    )

    return result

# --------------------------------------------------
# Add Pydantic model for update_model_info
# --------------------------------------------------
class UpdateModelInfoRequest(BaseModel):
    mpModel: str
    field: str      # 'devModel' or 'initialModel'
    value: str
    db_uri: Optional[str] = None
    table_name: Optional[str] = None


@app.post("/api/bom/update_model_info")
async def update_model_info(request: UpdateModelInfoRequest):
    # Exact mapping matching your PostgreSQL table columns
    column_mapping = {
        "devModel": '"dev model"',
        "initialModel": '"initial model"',
        "dev_model": '"dev model"',
        "initial_model": '"initial model"',
        "initial_updater": '"initial updater"',
        "initial_update_time": '"initial update datetime"',
    }

    column_name = column_mapping.get(request.field)

    if not column_name:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid field '{request.field}'. Allowed values are 'devModel' or 'initialModel'."
        )

    try:
        async with get_dej_db_connection(NOTIFICATION_DB_INDEX, database="MasterMP_Auto") as (conn, cursor):
            if cursor is None:
                raise HTTPException(status_code=500, detail="Failed to acquire database connection.")

            # Define the static updater and capture the current date and time
            current_time = datetime.now()
            static_updater = "engineer"

            # Target exact column names wrapped in double quotes, adding the new columns to the SET clause
            query = f"""
                UPDATE public.resultmain
                SET {column_name} = %s,
                    "initial updater" = %s,
                    "initial update datetime" = %s
                WHERE "mp model" = %s;
            """

            def _execute_update():
                # Pass the new variables into the execute tuple in the exact order of the query placeholders
                cursor.execute(query, (request.value, static_updater, current_time, request.mpModel))
                conn.commit()
                return cursor.rowcount

            rows_updated = await asyncio.to_thread(_execute_update)

            if rows_updated == 0:
                raise HTTPException(
                    status_code=404,
                    detail=f"No record found matching 'mp model' = '{request.mpModel}'"
                )

            return {
                "status": "success",
                "message": f"Successfully updated {request.field}, initial updater, and update time for {request.mpModel}",
                "updated_rows": rows_updated
            }

    except HTTPException:
        raise
    except Exception as e:
        print(f"--- ERROR in update_model_info: {str(e)} ---", flush=True)
        raise HTTPException(status_code=500, detail=f"Database update failed: {str(e)}")