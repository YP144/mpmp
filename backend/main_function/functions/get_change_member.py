import requests
import json
import polars as pl

from services.check_sso import SSO_NPDM


import requests
import sys
import json
import time
import requests
import polars as pl

from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter


pl.Config.set_tbl_rows(-1)
pl.Config.set_tbl_cols(-1)

def implode_all_columns(df: pl.DataFrame | pl.LazyFrame):
    return df.select([
        pl.col(col).implode()
        for col in df.columns
    ])

def get_coworking_info(get_auth, change_no_obid):


    #change_no_obid = "vQOmDt8FfzsgWW4uZspZth"
    change_no_url = f"https://npdm.lge.com/api/foundation/workflow/header/getWorkflowLifeCycle/{change_no_obid}"

    change_no_headers = {
                "Accept": "application/json",
                "Authorization": get_auth,
                "BusinessUnit": "HE",
                "Content-Type": "application/json",
                "Referer": f"https://npdm.lge.com/get-information?obid={change_no_obid}&type=independent",
            }

    # Fetch the data
    change_no_response = requests.get(change_no_url, headers=change_no_headers)
    change_no_json = change_no_response.json()

    # Extract the specific lists from the JSON response
    get_change_no_data = change_no_json["data"]
    get_change_no_approval_list = get_change_no_data["approvalVOList"]
    get_change_no_workgroup_list = get_change_no_data["workGroupList"]

    # Convert the Python list of dictionaries directly to a Polars DataFrame
    # infer_schema_length=10000 tells Polars to check up to 10,000 rows to determine column data types
    change_approval_list_df = pl.DataFrame(
        get_change_no_approval_list, 
        infer_schema_length=10000
    )

    change_workgroup_list_df = pl.DataFrame(
        get_change_no_workgroup_list, 
        infer_schema_length=10000
    )

    

    return implode_all_columns(change_approval_list_df)

