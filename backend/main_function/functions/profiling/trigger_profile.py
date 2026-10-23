import polars as pl
from datetime import date
from functions.profiling.user_bom_data import get_entire_model_result

from functions.profiling.get_timestamp import calculate_bom_delay
from functions.profiling.get_pic_team_info import process_bom_data
from functions.fast_profile import Fast_ModelProfile

import concurrent.futures


def get_mapped_profile(bom_name):
    """
    Fetches the ModelProfile for a given bom_name and maps the required fields.
    Uses distinct names to avoid DuplicateError with existing columns.
    """
    try:
        # Initialize the profile and extract the first dictionary from the JSON list
        profile_data = Fast_ModelProfile(bom_name).jsonProfile[0]
        
        # Map the JSON keys to new, distinct dataframe column names
        return {
            "profile_model_subsidiary": profile_data.get("Plant"),
            "profile_model_region": profile_data.get("Region"),
            "profile_model_soc": profile_data.get("SoC")
        }
    except Exception:
        # Return null values if the profile is missing, empty, or causes an error
        return {
            "profile_model_subsidiary": None,
            "profile_model_region": None,
            "profile_model_soc": None
        }

def apply_to_all_row_profiling(df):
    # 1. Extract only the unique "mp model" values to avoid redundant processing
    unique_models = df.select("mp model").unique()
    
    # 2. Convert the unique models to a Python list for processing
    model_list = unique_models.to_series().to_list()
    
    # 3. Run the mapping function concurrently on ONLY the unique models
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Map the function to the unique models in parallel
        future_to_model = {executor.submit(get_mapped_profile, model): model for model in model_list}
        
        for future in concurrent.futures.as_completed(future_to_model):
            model = future_to_model[future]
            try:
                profile_data = future.result()
                # Combine the original model name with its profile data
                results.append({
                    "mp model": model,
                    "profile_model_subsidiary": profile_data.get("profile_model_subsidiary"),
                    "profile_model_region": profile_data.get("profile_model_region"),
                    "profile_model_soc": profile_data.get("profile_model_soc")
                })
            except Exception as e:
                # Handle exceptions or assign default values if the lookup fails
                results.append({
                    "mp model": model,
                    "profile_model_subsidiary": None,
                    "profile_model_region": None,
                    "profile_model_soc": None
                })
                
    # 4. Convert the results back into a fast Polars DataFrame
    mapping_df = pl.DataFrame(results)
    
    # 5. Perform a native, lightning-fast Rust join back to the original DataFrame
    profiled_df = df.join(mapping_df, on="mp model", how="left")
    
    return profiled_df