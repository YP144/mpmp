import polars as pl
import re
import os

from db.read import read_table
from functions.getdata import masterDataURL, memberURL

def read_master_mp_data():
    master_mp_master = read_table(
        db_uri=masterDataURL,
        table_name="resultmain"
    )

    master_mp_master = master_mp_master.select([
        "crosscheck_id", "mp model", "dev model", "initial model",
        "result", "model_circuit_pic", "engineer_confirmation", "structure", "benComp", "hwTool", "substitute_check",
        "tool_option", "operation_plan", "compare_note", "year", "version",
        "model_series", "model_subsidiary", "model_soc", "model_region", "additional_remark"
    ])

    return master_mp_master

def read_user_summary():
    master_user_master = read_table(
        db_uri=memberURL,
        table_name="summary_user"
    )

    master_user_master = master_user_master.drop(["No","Emp_No", "Email", "NickName", "Part"])

    return master_user_master

def read_team_summary():
    master_team_master = read_table(
        db_uri=memberURL,
        table_name="summary_team"
    )

    return master_team_master