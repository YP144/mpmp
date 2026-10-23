import polars as pl
import polars.selectors as cs
import json
import os

#from pyspark.sql.functions import regexp_extract, col


def remove_nulls(data):
    # If the data is a dictionary, recursively check its keys and values
    if isinstance(data, dict):
        return {key: remove_nulls(value) for key, value in data.items() if value is not None}
    # If the data is a list, recursively check each item in the list
    elif isinstance(data, list):
        return [remove_nulls(item) for item in data if item is not None]
    # Return the data as-is if it is neither a dictionary nor a list (and not None)
    else:
        return data

def load_and_validate_json(file_path):
    # Check if the file exists at the specified path
    if not os.path.exists(file_path):
        print(f"Error: The file path '{file_path}' does not exist.")
        return None
    
    # Attempt to open and parse the JSON file
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error: The file is not a valid JSON format. Details: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def safe_json_dumps(val):
    # Return None immediately if the value is empty
    if val is None:
        return None
    # Convert Polars Series to a standard Python list so json.dumps can read it
    if isinstance(val, pl.Series):
        val = val.to_list()
    # Safely convert the native Python object to a JSON string
    return json.dumps(val, ensure_ascii=False)



def select_df_column(df):
    # Select the summary column
    selected_column_summary = df.select(['summary'])
    
    # CORRECTED: Using hex codes \x5B for '[' and \x5D for ']' 
    # This prevents the chat UI from converting them into dollar signs ($$)
    pattern = r'^\x5B(.*?)\x5D\x5B(.*?)\x5D\x5B(.*?)\x5D\x5B(.*?)\x5D\x5B(.*?)\x5D\s*(.*)$'

    # Extract the values into new distinct columns
    result_df = selected_column_summary.with_columns([
        pl.col('summary').str.extract(pattern, 1).alias('os'),
        pl.col('summary').str.extract(pattern, 2).alias('chassis'),
        pl.col('summary').str.extract(pattern, 3).alias('category'),
        pl.col('summary').str.extract(pattern, 4).alias('region'),
        pl.col('summary').str.extract(pattern, 5).alias('pcode'),
        pl.col('summary').str.extract(pattern, 6).alias('pm_model_name')
    ])
        
    return result_df

def select_df_column_description(df):
    # Select the summary column
    selected_column_summary = df.select(['description'])

    # 1. Extract the vertical key-value pairs from the first table
    # Note: Using \x28 for '(' and \x29 for ')' to prevent chat UI math-formatting bugs
    result_df = df.with_columns([
        pl.col('description').str.extract(r'\x7C\x7CModel Name\x7C(.*?)\x7C', 1).alias('model_name'),
        pl.col('description').str.extract(r'\x7C\x7CDivision\x7C(.*?)\x7C', 1).alias('division'),
        pl.col('description').str.extract(r'\x7C\x7CwebOS Version\x7C(.*?)\x7C', 1).alias('webos_version'),
        pl.col('description').str.extract(r'\x7C\x7CSoC\x28Main Chip\x29\x7C(.*?)\x7C', 1).alias('soc_main_chip'),
        pl.col('description').str.extract(r'\x7C\x7CSW Version\x7C(.*?)\x7C', 1).alias('sw_version'),
        pl.col('description').str.extract(r'\x7C\x7CEvent\x7C(.*?)\x7C', 1).alias('event'),
        pl.col('description').str.extract(r'\x7C\x7CGrade\x7C(.*?)\x7C', 1).alias('grade'),
        pl.col('description').str.extract(r'\x7C\x7CModule Name\x7C(.*?)\x7C', 1).alias('module_name'),
        pl.col('description').str.extract(r'\x7C\x7CLocal Dimming\x7C(.*?)\x7C', 1).alias('local_dimming'),
        pl.col('description').str.extract(r'\x7C\x7CBase Region\x7C(.*?)\x7C', 1).alias('base_region'),
        pl.col('description').str.extract(r'\x7C\x7CInch\x28Size\x29\x7C(.*?)\x7C', 1).alias('inch_size'),
        pl.col('description').str.extract(r'\x7C\x7CTool\x7C(.*?)\x7C', 1).alias('tool'),
        pl.col('description').str.extract(r'\x7C\x7CPanel Code\x7C(.*?)\x7C', 1).alias('panel_code'),
        pl.col('description').str.extract(r'\x7C\x7CAudio EQ/EYE \x28TV Color\x29\x7C(.*?)\x7C', 1).alias('audio_eq')
    ])
    
    # 2. Extract the horizontal data from the "Tool Options" table
    # This pattern finds the header, skips to the next line, and captures the 11 values between the pipes
    tool_options_pattern = (
        r'\x7C\x7CRegions\x7C\x7CMax PWM[^\n]*\n\s*'  # Matches the header row and the newline character
        r'\x7C([^\x7C]*)\x7C([^\x7C]*)\x7C([^\x7C]*)\x7C([^\x7C]*)\x7C([^\x7C]*)\x7C' # Captures groups 1-5
        r'([^\x7C]*)\x7C([^\x7C]*)\x7C([^\x7C]*)\x7C([^\x7C]*)\x7C([^\x7C]*)\x7C([^\x7C]*)\x7C' # Captures groups 6-11
    )
    
    result_df = result_df.with_columns([
        pl.col('description').str.extract(tool_options_pattern, 1).alias('to_regions'),
        pl.col('description').str.extract(tool_options_pattern, 2).alias('to_max_pwm'),
        pl.col('description').str.extract(tool_options_pattern, 3).alias('to_def_backlight'),
        pl.col('description').str.extract(tool_options_pattern, 4).alias('to_adaptdim_def'),
        pl.col('description').str.extract(tool_options_pattern, 5).alias('to_adapt_dimming'),
        pl.col('description').str.extract(tool_options_pattern, 6).alias('to_oled_cpc'),
        pl.col('description').str.extract(tool_options_pattern, 7).alias('to_new_erp'),
        pl.col('description').str.extract(tool_options_pattern, 8).alias('to_standard_backlight'),
        pl.col('description').str.extract(tool_options_pattern, 9).alias('to_luminance_up'),
        pl.col('description').str.extract(tool_options_pattern, 10).alias('to_energy_star'),
        pl.col('description').str.extract(tool_options_pattern, 11).alias('to_sensor_gain')
    ])
    
    # 3. Clean up any accidental whitespace from all the new columns
    new_columns = [
        'model_name', 'division', 'webos_version', 'soc_main_chip', 'sw_version', 'event', 
        'grade', 'module_name', 'local_dimming', 'base_region', 'inch_size', 'tool', 
        'panel_code', 'audio_eq', 'to_regions', 'to_max_pwm', 'to_def_backlight', 
        'to_adaptdim_def', 'to_adapt_dimming', 'to_oled_cpc', 'to_new_erp', 
        'to_standard_backlight', 'to_luminance_up', 'to_energy_star', 'to_sensor_gain'
    ]
    
    for col_name in new_columns:
        result_df = result_df.with_columns(pl.col(col_name).str.strip_chars())
        
    return result_df


def conditioning_name(df):

    pass



# Define your input and output file paths
file_path = r"C:\Users\user\Desktop\xlred\new_npdm\JIRA_TEST\my_custom_output.json"
csv_output_path = r"C:\Users\user\Desktop\xlred\new_npdm\JIRA_TEST\filtered_issues_selected_columns.csv"

# Load and validate the JSON data using the new function
json_data = load_and_validate_json(file_path)

# Proceed with processing only if the data was successfully loaded
if json_data is not None:
    # Extract the "issues" data
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
        #print(df)
        get_select_data = select_df_column_description(df)
        get_select_data = get_select_data.rename({
            "to_adapt_dimming" : "to_mec"
        })

        get_select_name = select_df_column(df)
        get_select_name = get_select_name.drop('summary')

        get_total_model = pl.concat([get_select_name, get_select_data], how="horizontal")

        print(get_total_model)
        print(get_total_model.height)

        #print(get_select_data.item(0, "description"))
        
        # Safely convert any remaining complex nested Structs and Lists to JSON strings
        df_for_csv = df.with_columns(
            cs.by_dtype(pl.Struct, pl.List).map_elements(
                safe_json_dumps, 
                return_dtype=pl.String
            )
        )
        
        # Write the flattened DataFrame to a CSV file
        df_for_csv.write_csv(csv_output_path)
        print(f"Data successfully exported to CSV at: {csv_output_path}")
        
    else:
        print("No data found.")