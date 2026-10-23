import requests
import polars as pl
import pandas as pd
import os
import re
import sys

from services.check_sso import SSO_NPDM, center_login
from functions.conditioning import zerobom_conditioning, get_parent_partlist

# ==> EAX Checklist <==
#1. Search How many Release's
#2. Check Latest Releases
#3. Check Who made new releases 

#
# ==> HELPER FUNCTION <==
#

def parse_related_request_list(response_data) -> pl.DataFrame:
    """
    Parse relatedRequestList from response_data and flatten each item's outData
    into the same row, creating a single Polars DataFrame.

    Supports response_data as either:
    - dict: {"data": {"relatedRequestList": [...]}}
    - dict: {"relatedRequestList": [...]}
    - list of dicts
    """

    related_request_list = []

    if isinstance(response_data, dict):
        if isinstance(response_data.get("data"), dict):
            related_request_list = response_data.get("data", {}).get("relatedRequestList", [])
        else:
            related_request_list = response_data.get("relatedRequestList", [])

    elif isinstance(response_data, list):
        for element in response_data:
            if not isinstance(element, dict):
                continue

            if isinstance(element.get("data"), dict):
                related_request_list.extend(
                    element.get("data", {}).get("relatedRequestList", [])
                )
            elif isinstance(element.get("relatedRequestList"), list):
                related_request_list.extend(
                    element.get("relatedRequestList", [])
                )
            else:
                # If the list itself is already the relatedRequestList
                if "outData" in element or "requestStartDate" in element:
                    related_request_list.append(element)

    rows = []

    for item in related_request_list:
        if not isinstance(item, dict):
            continue

        row = {
            key: value
            for key, value in item.items()
            if key != "outData"
        }

        out_data = item.get("outData") or {}

        if isinstance(out_data, dict):
            for out_key, out_value in out_data.items():
                row[f"outData_{out_key}"] = out_value

        rows.append(row)

    if not rows:
        return pl.DataFrame()

    return pl.DataFrame(rows, infer_schema_length=None)

#
# ==> Get EAX Profile 
#

def get_eax_profile(target_bom):
    GetTargetBOM, TargetName = zerobom_conditioning(target_bom)

    result, get_eax_num, _, get_eax_obid = get_parent_partlist(GetTargetBOM)


    get_login, get_bearer = center_login()
    # Get Number of Release
    eax_release_url = f"https://npdm.lge.com/api/engineering/item/part/find-part-related-request/{get_eax_obid}"

    headers = {
                "Accept": "application/json",
                "Authorization": get_bearer,
                "BusinessUnit": "HE",
                "Content-Type": "application/json",
                "Referer": f"https://npdm.lge.com/get-information?obid={get_eax_obid}&type=independent",
            }

    response = requests.get(
        eax_release_url,
        headers=headers,
        timeout=19
    )
    responseData = response.json()

    main_eax_release = parse_related_request_list(responseData)
    get_eax_release_frame = main_eax_release.select([
        "outData_this_ownerName", "outData_this_creatorName",
        "outData_this_relatedModelName", "outData_part_technicalSpecification", "outData_part_names",
        "names", "outData_part_revision", "outData_this_requestSiteDesc","states", "titles"
    ])

    get_pcb_detail_frame = main_eax_release.select([
        "pcbSize", "pcbLayer", "aspectRatio", "throughHole", "minHoleSize", "created", "modified", "obid"
    ])
    
    return get_eax_release_frame, get_pcb_detail_frame, responseData



#
# ==> Get EBT Profile <==
#
def get_ebt_profile():
    pass



