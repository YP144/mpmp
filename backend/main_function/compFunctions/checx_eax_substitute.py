import polars as pl
import json

from db.read import read_table
from main_function.functions.getdata import get_eax_url
from main_function.functions.conditioning import get_parent_partlist


#
# ==> eax Substitute needs to read the database from input <==
#


def compare_under_eax(completeBOM, SoC):
    """
    K25Lp -> K25Lpn / K25Lpnm

    Always returns JSON format:
    {
        "soc": SoC,
        "eaxPartNumber": get_eax_num,
        "tableName": table_name,
        "dbExist": "Exist" / "notExist",
        "compareData": []
    }
    """

    # Default JSON output
    json_eax_result = {
        "soc": None,
        "eaxPartNumber": None,
        "tableName": None,
        "dbExist": None,
        "eaxobid": None,
        "compareData": []
    }

    # Validate input first
    if completeBOM is None or SoC is None or str(SoC).strip() == "":
        json_eax_result["dbExist"] = "notExist"
        return json_eax_result

    # Normalize SoC safely
    SoC = str(SoC).strip().lower()

    if SoC == "lm24f":
        SoC = "lm24f"
    else:
        SoC = "k25lp"

    json_eax_result["soc"] = SoC

    # Get EAX / EBR parent-child part list
    try:
        result, get_eax_num, _, get_eax_obid = get_parent_partlist(completeBOM)
    except Exception as e:
        json_eax_result["dbExist"] = "notExist"
        json_eax_result["error"] = str(e)
        return json_eax_result

    # If EAX is not detected
    if get_eax_num is None or str(get_eax_num).strip() == "":
        json_eax_result["dbExist"] = "notExist"

        if result is not None and not result.is_empty():
            json_eax_result["compareData"] = result.to_dicts()

        return json_eax_result

    # Set EAX part number
    get_eax_num = str(get_eax_num).strip()

    # Use same table name format as your previous working code
    table_name = f"{SoC.lower()}_{get_eax_num.upper()}"

    json_eax_result["eaxPartNumber"] = get_eax_num
    json_eax_result["tableName"] = table_name
    json_eax_result["eaxobid"] = get_eax_obid

    # Check result DataFrame
    if result is None or result.is_empty():
        json_eax_result["dbExist"] = "notExist"
        return json_eax_result

    # Determine DB URL from EAX and SoC
    try:
        get_eax_db = get_eax_url(SoC.lower())
    except Exception as e:
        json_eax_result["dbExist"] = "notExist"
        json_eax_result["error"] = str(e)
        return json_eax_result

    # Read EAX substitute table
    try:
        eax_db = read_table(
            db_uri=get_eax_db,
            table_name=table_name
        )

        if eax_db is not None and not eax_db.is_empty():
            json_eax_result["dbExist"] = "Exist"
        else:
            json_eax_result["dbExist"] = "notExist"

    except Exception as e:
        json_eax_result["dbExist"] = "notExist"
        json_eax_result["error"] = str(e)
        return json_eax_result

    # Return JSON even if EAX DB has no data
    if eax_db is None or eax_db.is_empty():
        return json_eax_result

    # Check required DB column before rename
    if "DESIGNATOR" not in eax_db.columns:
        json_eax_result["dbExist"] = "notExist"
        json_eax_result["error"] = "DESIGNATOR column not found in EAX DB"
        return json_eax_result

    # Rename DESIGNATOR to referenceDesignator
    eax_substitute = eax_db.rename({
        "DESIGNATOR": "referenceDesignator"
    })

    # Check join key
    if "referenceDesignator" not in result.columns:
        json_eax_result["dbExist"] = "notExist"
        json_eax_result["error"] = "referenceDesignator column not found in BOM result"
        return json_eax_result

    # Join BOM result with EAX substitute DB
    try:
        combineDesignator = result.join(
            eax_substitute,
            on=["referenceDesignator"],
            how="left"
        )
    except Exception as e:
        json_eax_result["dbExist"] = "notExist"
        json_eax_result["error"] = str(e)
        return json_eax_result

    required_columns = [
        "bomLevel",
        "part_number",
        "part_descriptions",
        "part_quantity",
        "SERIES",
        "ACTUAL PART NO",
        "1ST",
        "2ND",
        "3rd",
        "4th",
        "Remark"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in combineDesignator.columns
    ]

    if missing_columns:
        json_eax_result["dbExist"] = "notExist"
        json_eax_result["error"] = f"Missing columns: {missing_columns}"
        return json_eax_result

    combineDesignator = combineDesignator.select(required_columns).filter(
        pl.col("SERIES").is_not_null()
    )

    # Return JSON even if no rows remain after filtering
    if combineDesignator.is_empty():
        return json_eax_result

    result_compare_eax = combineDesignator.with_columns(
        pl.when(
            pl.concat_list(["1ST", "2ND", "3rd", "4th"])
            .list.drop_nulls()
            .list.contains(pl.col("part_number"))
        )
        .then(pl.lit("OK"))
        .otherwise(pl.lit("NEED HW OPTION"))
        .alias("status")
    )

    # Return JSON even if final result is empty
    if result_compare_eax.is_empty():
        return json_eax_result

    json_eax_result["compareData"] = result_compare_eax.to_dicts()

    return json_eax_result