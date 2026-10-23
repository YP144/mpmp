import polars as pl
import re

def compare_chassis(CompleteBOM: pl.DataFrame, heros_chassis: str) -> str:
    get_ebt = CompleteBOM.filter(
        (pl.col("part_number").str.contains(r"^EBT")) &
        (pl.col("bomLevel") == 1)
    )

    if get_ebt.height == 0:
        return "No EBT found"

    ebt_technical = get_ebt.item(0, "part_TechnicalSpec")

    if ebt_technical is None:
        return "No technical spec found"

    heros_chassis = str(heros_chassis).strip()
    ebt_technical = str(ebt_technical).strip()

    # print("heros_chassis:", repr(heros_chassis))
    # print("ebt_technical:", repr(ebt_technical))

    regex_chassis = re.escape(heros_chassis)

    if re.search(regex_chassis, ebt_technical, flags=re.IGNORECASE):
        return f"'{heros_chassis}' Correct"
    else:
        return "Chassis Not Correct"