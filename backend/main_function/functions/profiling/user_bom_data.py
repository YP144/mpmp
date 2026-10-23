import polars as pl
import re
import os

from db.read import read_table
from functions.getdata import (
    masterDataURL,
    memberURL
)

#
# ==> Parse Main Database for Engineer Model Only <==
#
def get_user_model_information(engineer_name: str):
    get_home_table = read_table(
        db_uri=masterDataURL,
        table_name="resultmain"
    )

    engineer_total_bom = get_home_table.filter(
        # Ubah string database ke UPPER dan kata kunci ke UPPER
        pl.col("model_circuit_pic").str.to_uppercase().str.contains(engineer_name.upper())
    )

    # engineer_total_bom = engineer_total_bom.select([
    #     "crosscheck_id", "mp model", "dev model", "initial model",
    #     "result", "model_circuit_pic", "engineer_confirmation", "structure", "benComp", "hwTool", "substitute_check",
    #     "tool_option", "operation_plan", "compare_note", "time", "urgent", "overdue", "year", "version",
    #     "model_series", "model_subsidiary", "model_soc", "model_region", "additional_remark","bom_release_date",
    #     "bom_last_checker", "bom_delay_count", "bom_team", 
    # ])

    total_engineer_bom = engineer_total_bom.height

    return engineer_total_bom


def get_team_information():
    get_summary_team_table = read_table(
        db_uri=memberURL,
        table_name="summary_team"
    )

    return get_summary_team_table


def get_team_list_information():
    get_summary_team_table = read_table(
        db_uri=memberURL,
        table_name="summary_user"
    )

    return get_summary_team_table


def get_user_information():
    get_summary_user_table = read_table(
        db_uri=memberURL,
        table_name="summary_user"
    )

    get_summary_user_table = get_summary_user_table.with_columns(
        pl.when(pl.col("TEAM") == "TV HW DVB TEAM")
        .then(pl.lit("DVB"))
        .when(pl.col("TEAM") == "TV HW OLED TEAM")
        .then(pl.lit("OLED"))
        .when(pl.col("TEAM") == "TV HW ATSC TEAM")
        .then(pl.lit("ATSC"))
        .otherwise(pl.col("TEAM"))
        .alias("TEAM")
    )

    return get_summary_user_table


def get_user_information_onlyHW():
    get_summary_user_table = read_table(
        db_uri=memberURL,
        table_name="summary_user"
    )

    get_summary_user_table = get_summary_user_table.with_columns(
        pl.when(pl.col("TEAM") == "TV HW DVB TEAM")
        .then(pl.lit("DVB"))
        .when(pl.col("TEAM") == "TV HW OLED TEAM")
        .then(pl.lit("OLED"))
        .when(pl.col("TEAM") == "TV HW ATSC TEAM")
        .then(pl.lit("ATSC"))
        .otherwise(pl.col("TEAM"))
        .alias("TEAM")
    )

    get_summary_user_table = get_summary_user_table.filter(
        pl.col("Part").str.contains("HW") | pl.col("Part").str.contains("Asia")
    )

    return get_summary_user_table


def get_entire_model_result():
    get_entire_model = read_table(
        db_uri=masterDataURL,
        table_name="resultmain"
    )

    #get_entire_model = get_entire_model.select(["mp model", "dev model", "initial model", "result", "engineer_confirmation", "version", "structure", "benComp", "hwTool", "substitute_check", "tool_option", "operation_plan", "model_subsidiary", "model_circuit_pic", "model_region", "model_soc", "bom_release_date", "bom_team", "bom_delay_count", "additional_remark", "year"])

    return get_entire_model


def get_entire_working_model_result():
    get_entire_model = read_table(
        db_uri=memberURL,
        table_name="all_working_model"
    )

    #get_entire_model = get_entire_model.select(["mp model", "dev model", "initial model", "result", "engineer_confirmation", "version", "structure", "benComp", "hwTool", "substitute_check", "tool_option", "operation_plan", "model_subsidiary", "model_circuit_pic", "model_region", "model_soc", "bom_release_date", "bom_team", "bom_delay_count", "additional_remark", "year"])

    return get_entire_model