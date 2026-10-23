
import streamlit as st
import polars as pl
import polars.selectors as cs
import json
import os

from functions.JIRA.jira_req import get_jira_power_cons
from functions.profile import ModelProfile
from functions.JIRA.jira_process import (
    remove_nulls, load_and_validate_json, safe_json_dumps,
    select_df_column, select_df_column_description
)

#jira_key = "ODA3Mzc0ODAwMTY1OlHLm3Hs4YgvWCnHbHahhbNr5O2D"
#mpx_isseu_key = "MTgxOTI0Mzg4NjcyOs7DbmSZKdBTxMOohTqdGzZ9PbkQ"

#model_name = "43QNED75CKA.AKRFLCX"
#get_model_profile = ModelProfile(model_name)

#get_jira_json = get_jira_power_cons(API_KEY=jira_key, model_name=model_name)

# Load and validate the JSON data using the new function
#json_data = load_and_validate_json(get_jira_json)

def get_jira_tool_option_df(get_jira_json: dict):
  json_data = get_jira_json

  # Initialize default fallbacks to prevent UnboundLocalError
  get_total_model = None
  jira_model = []
  filtered_list = []

  # Proceed with processing only if the data was successfully loaded
  if json_data is not None:
    get_data = json_data.get("issues", [])

    # Apply the function to remove all null values from the issues data
    filtered_data = remove_nulls(get_data)

    # Convert the cleaned list of dictionaries into a Polars DataFrame
    if filtered_data:
      # Create the DataFrame
      df = pl.DataFrame(filtered_data)

      # Expand the 'fields' column into individual columns
      if "fields" in df.columns:
        df = df.unnest("fields")

      # Drop any columns that have 'customfield_' in their header name
      df = df.drop(cs.starts_with("customfield_"))

      # Print the DataFrame to verify the output
      print("Data successfully converted to a Polars DataFrame:")
      get_select_data = select_df_column_description(df)
      get_select_data = get_select_data.rename({"to_adapt_dimming": "to_mec"})

      get_select_name = select_df_column(df)
      get_select_name = get_select_name.drop("summary")

      get_total_model = pl.concat(
          [get_select_name, get_select_data], how="horizontal"
      )

      jira_model = get_total_model.to_dicts()
    else:
      print("No data found.")

    # Define the fields you want to keep
    desired_keys = [
        "summary",
        "model_name",
        "division",
        "webos_version",
        "soc_main_chip",
        "sw_version",
        "event",
        "grade",
        "module_name",
        "local_dimming",
        "base_region",
        "inch_size",
        "tool",
        "panel_code",
        "audio_eq",
        "to_regions",
        "to_max_pwm",
        "to_def_backlight",
        "to_adaptdim_def",
        "to_mec",
        "to_oled_cpc",
        "to_new_erp",
        "to_standard_backlight",
        "to_luminance_up",
        "to_energy_star",
        "to_sensor_gain",
    ]

    # Only parse/filter if get_total_model actually exists
    if get_total_model is not None:
      filtered_list = [
          {key: item[key] for key in desired_keys if key in item}
          for item in jira_model
      ]
      # Print or export the filtered result
      print(json.dumps(filtered_list, indent=4))

  return jira_model, get_total_model, filtered_list


#get_total_model, model_df = get_jira_tool_option_df()

#print(get_total_model)
#print(model_df)


#with open("jiracheck/jira_export.json", "w", encoding="utf-8") as f:
  # Serialize the list to a JSON string with indentation
  #f.write(json.dumps(get_total_model, indent=4))


