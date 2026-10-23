
import polars as pl
from functions.profiling.user_bom_data import get_entire_model_result, get_team_list_information

def process_bom_data(get_all_model):
    """
    Processes the BOM data by mapping team and part information, 
    and extracting HW parts, returning the updated dataframe.
    """
    # Get Team data
    get_team = get_team_list_information()

    # Create dictionaries mapping 'Name' to 'TEAM' and 'Name' to 'Part'
    team_mapping = dict(zip(get_team["Name"].to_list(), get_team["TEAM"].to_list()))
    part_mapping = dict(zip(get_team["Name"].to_list(), get_team["Part"].to_list()))

    # Update 'bom_team', create 'Part', and extract 'HW'
    updated_df = get_all_model.with_columns(
        # 1. Generate the bom_team column
        pl.col("model_circuit_pic")
        .str.split(",")
        .list.eval(pl.element().str.strip_chars())
        .list.eval(pl.element().replace(team_mapping, default=pl.element()))
        .list.join(", ")
        .alias("bom_team"),
        
        # 2. Generate the new Part column
        pl.col("model_circuit_pic")
        .str.split(",")
        .list.eval(pl.element().str.strip_chars())
        .list.eval(pl.element().replace(part_mapping, default=pl.element()))
        .list.join(", ")
        .alias("Part")
    ).with_columns(
        # 3. Generate the HW column by filtering the newly created Part column
        pl.col("Part")
        .str.split(",")
        .list.eval(pl.element().str.strip_chars())
        .list.eval(pl.element().filter(pl.element().str.contains("HW")))
        .list.join(", ")
        .alias("HW")
    )

    return updated_df
