import re
import polars as pl

def contains_keywords_or_any(ref_value, target_value):
    if ref_value is None:
        return True

    ref_value = str(ref_value).strip()

    if ref_value == "":
        return True

    if target_value is None:
        return False

    target_value = str(target_value).lower()

    keywords = [
        keyword.strip().lower()
        for keyword in ref_value.replace("|", ",").split(",")
        if keyword.strip() != ""
    ]

    if not keywords:
        return True

    for keyword in keywords:
        pattern = r"\b" + re.escape(keyword) + r"\b"

        if re.search(pattern, target_value):
            return True

    return False

def contains_or_any(ref_value, target_value):
    if ref_value is None:
        return True

    ref_value = str(ref_value).strip()

    if ref_value == "":
        return True

    if target_value is None:
        return False

    return ref_value.lower() in str(target_value).lower()

def partnum_match(template_part, bom_part):
    if template_part is None or bom_part is None:
        return False

    template_part = str(template_part).strip()
    bom_part = str(bom_part).strip()

    if template_part == "":
        return False

    # If PartNum contains "|", treat it as OR condition
    part_options = [
        part.strip()
        for part in template_part.split("|")
        if part.strip() != ""
    ]

    return any(part in bom_part for part in part_options)

def build_regex_expr(col_name: str) -> pl.Expr:
    """Transforms wildcard references like 'EBT*' or 'EAX*/GUI*'

    into valid Regex patterns like '^(EBT.*)$' or '^(EAX.*|GUI.*)$'.
    """
    return (
        pl.col(col_name)
        # 1. Standardize slashes and pipes to a common delimiter (|)
        .str.replace_all(r"\/", "|")
        # 2. Escape literal regex characters, preserving wildcards for now
        .str.replace_all(r"\.", r"\.")
        # 3. Convert wildcard '*' into Regex '.*'
        .str.replace_all(r"\*", ".*")
        # 4. Wrap with start/end anchors for explicit pattern matching
        .map_elements(lambda p: f"^({p})$" if p else None, return_dtype=pl.Utf8)
    )



