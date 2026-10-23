
import polars as pl
import json
import requests
import sys
import os
import requests
import html
from urllib.parse import parse_qs
import time
from dateutil.relativedelta import relativedelta
from services.check_sso import SSO_NPDM
from datetime import date, datetime, timezone, timedelta
import uuid
import requests
from functions.datasend import upload_bytes_tos3, send_to_pymongo, read_from_pymongo, read_from_pymongo


def GetModelCoWork():
    current_time = date.today()
    # current_time = datetime.strptime("2026-06-13", "%Y-%m-%d").date()
    PastDate = current_time - timedelta(days=7)

    sso = SSO_NPDM()
    is_logged_in = sso.auto_login(ssolgenet_cookie, smsession_cookie)

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": sso.auth_bearer,
        "BusinessUnit": "HE",
        "Content-Type": "application/json",
        "Host": "npdm.lge.com",
        "Referer": "https://npdm.lge.com/"
    }

    ParamCoWork = {
        "cParamSearchVO": {
            "releaseCreationDate": {
                "comparison": "BT",
                "fromDate": "",
                "toDate": ""
            },
            "gerpCreationDate": {
                "fromDate": PastDate.isoformat(),
                "toDate": current_time.isoformat(),
                "comparison": "BT"
            },
            "requestBOMOpen": {
                "comparison": "BT",
                "fromDate": "",
                "toDate": ""
            },
            "divisions": "GLZ",
            "creationPlantUnit": "GLZ.EKHQ"
        }
    }

    response = requests.put(
        "https://npdmbatch-he.lge.com/api/scheduler/report/he/model/bom/status",
        headers=headers,
        json=ParamCoWork
    )

    try:
        CoWorkModel = response.json()
    except Exception:
        return pl.DataFrame(), response.status_code, {
            "error": "Response is not valid JSON",
            "text": response.text
        }

    coworkdata = CoWorkModel.get("data")

    if coworkdata is None:
        return pl.DataFrame(), response.status_code, {
            "error": "API returned data=None",
            "response": CoWorkModel
        }

    if not isinstance(coworkdata, list):
        return pl.DataFrame(), response.status_code, {
            "error": "API returned data but it is not a list",
            "data_type": str(type(coworkdata)),
            "response": CoWorkModel
        }

    if len(coworkdata) == 0:
        return pl.DataFrame(), response.status_code, {
            "message": "API returned empty data list",
            "response": CoWorkModel
        }

    all_outdata = []

    for item in coworkdata:
        if item is not None and isinstance(item, dict):
            out_data = item.get("outData")

            if out_data is not None and isinstance(out_data, dict):
                all_outdata.append(out_data)

    if len(all_outdata) == 0:
        return pl.DataFrame(), response.status_code, {
            "error": "No outData found in API data",
            "response": CoWorkModel
        }

    getcoworkName = pl.DataFrame(all_outdata, infer_schema_length=1000)

    getcoworkName = pl.DataFrame(all_outdata, infer_schema_length=1000)

    required_outdata_cols = [
        "cha_coWorker1", "cha_coWorker2", "cha_coWorker3",
        "cha_coWorker4", "cha_coWorker5", "cha_coWorker6",
        "cha_coWorker7", "cha_coWorker8", "cha_coWorker9",
        "cha_coWorker10", "cha_coWorker11", "cha_coWorker12",
        "cha_names", "cha_states", "mr_chassis"
    ]

    existing_outdata_cols = [
        col for col in required_outdata_cols
        if col in getcoworkName.columns
    ]

    getcoworkName = getcoworkName.select(existing_outdata_cols)

    coworkdata_df = pl.DataFrame(coworkdata, infer_schema_length=1000)

    required_main_cols = [
        "names",
        "titles",
        "technicalSpecification",
        "states",
        "releasedDate"
    ]

    existing_main_cols = [
        col for col in required_main_cols
        if col in coworkdata_df.columns
    ]

    coworkdata_df = coworkdata_df.select(existing_main_cols)

    coworkFrame = pl.concat(
        [getcoworkName, coworkdata_df],
        how="horizontal"
    )

    # ------------------------------------------------------------
    # Add extraction identity metadata
    # ------------------------------------------------------------
    extraction_run_id = str(uuid.uuid4())
    extraction_datetime_utc = datetime.now(timezone.utc).isoformat()
    extraction_date_utc = datetime.now(timezone.utc).date().isoformat()

    coworkFrame = coworkFrame.with_columns([
        pl.lit(extraction_run_id).alias("extractionRunId"),
        pl.lit(extraction_datetime_utc).alias("extractionDate"),
        pl.lit(extraction_date_utc).alias("extractionDateOnly"),
        pl.lit("NPDM_GetModelCoWork").alias("data_origin"),
        pl.lit(True).alias("is_current_extraction")
    ])

    getCoworkStatus = response.status_code

    return coworkFrame, getCoworkStatus, CoWorkModel



search_columns = [
    "cha_coWorker1", "cha_coWorker2", "cha_coWorker3",
    "cha_coWorker4", "cha_coWorker5", "cha_coWorker6",
    "cha_coWorker7", "cha_coWorker8", "cha_coWorker9",
    "cha_coWorker10", "cha_coWorker11", "cha_coWorker12",
    "cha_names",
    "names"
]

def _convert_member_df_to_list(member_df: pl.DataFrame, name_col: str = "getName") -> list[str]:
    """
    Convert member DataFrame column into Python list.
    Null and empty names are removed.
    """
    return (
        member_df
        .select(pl.col(name_col).cast(pl.Utf8).fill_null(""))
        .filter(pl.col(name_col) != "")
        .get_column(name_col)
        .to_list()
    )


def _find_members_in_text(text: str, member_list: list[str]) -> str:
    """
    Find members whose names are included in the given text.
    """
    if text is None:
        return ""

    found = []

    for member in member_list:
        if member in text:
            found.append(member)

    return ", ".join(found)

def _generate_model_by_members(
    cowork_df: pl.DataFrame,
    member_df: pl.DataFrame,
    result_column: str,
    name_col: str = "getName"
) -> pl.DataFrame:
    """
    Common function to generate model list by matching member names
    from cowork columns.
    """
    member_list = _convert_member_df_to_list(member_df, name_col=name_col)

    existing_search_columns = [
        col for col in search_columns
        if col in cowork_df.columns
    ]

    if not existing_search_columns:
        raise ValueError(
            f"No matching search columns found. "
            f"search_columns={search_columns}, "
            f"cowork_df.columns={cowork_df.columns}"
        )

    result_df = (
        cowork_df
        .with_columns(
            pl.concat_str(
                [
                    pl.col(col).cast(pl.Utf8).fill_null("")
                    for col in existing_search_columns
                ],
                separator=" "
            ).alias("all_names")
        )
        .with_columns(
            pl.col("all_names")
            .map_elements(
                lambda text: _find_members_in_text(text, member_list),
                return_dtype=pl.Utf8
            )
            .alias(result_column)
        )
        .filter(pl.col(result_column) != "")
    )

    return result_df