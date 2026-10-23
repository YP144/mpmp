import polars as pl
from functions.conditionig import zerobom_conditioning, get_parent_partlist

def comapre_under_eax(result, eax_substitute):

    #Get Substitue from GetProfile (SoC only)

    eax_substitute = eax_substitute.rename({
        "DESIGNATOR": "referenceDesignator"
    })
  
    combineDesignator = result.join(eax_substitute, on=["referenceDesignator"], how="left")
    combineDesignator = combineDesignator.select([
        "bomLevel", "part_number", "part_descriptions",
        "part_quantity", "SERIES", "ACTUAL PART NO",
        "1ST", "2ND", "3rd", "4th", "Remark"]).filter((pl.col("SERIES").is_not_null()))

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
    
    return result_compare_eax
