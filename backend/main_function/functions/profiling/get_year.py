from difflib import SequenceMatcher
import polars as pl
import re
import os
import json

from db.read import read_latest_version
from main_function.functions.getdata import HerosURL

#
# == if the model name exist in both dataframe
#
def use_row_as_header(df: pl.DataFrame, header_row: int = 0) -> pl.DataFrame:
    """
    Use the selected row as headers, remove rows up to that header row,
    and make sure column names are not blank or duplicated.
    """

    raw_headers = df.row(header_row)

    new_headers = []
    seen = {}

    for i, value in enumerate(raw_headers):
        if value is None or str(value).strip() == "":
            header = f"column_{i}"
        else:
            header = str(value).strip()

        if header in seen:
            seen[header] += 1
            header = f"{header}_{seen[header]}"
        else:
            seen[header] = 0

        new_headers.append(header)

    return (
        df
        .slice(header_row + 1)
        .rename(dict(zip(df.columns, new_headers)))
    )


def search_model_in_dataframes(
    model_input: str,
    df_26y: pl.DataFrame,
    df_27y: pl.DataFrame,
    column_name: str = "Model Name"
) -> dict:
    """
    Search model_input in 26Y and 27Y DataFrames.

    Returns a dictionary showing:
    - whether the model matched in 26Y
    - whether the model matched in 27Y
    - exact match rows
    - partial match rows
    - final matched location
    """

    model_input_clean = model_input.strip().upper()

    def search_one_dataframe(df: pl.DataFrame, year_name: str) -> dict:
        if column_name not in df.columns:
            return {
                "year": year_name,
                "exact_match": False,
                "partial_match": False,
                "exact_rows": pl.DataFrame(),
                "partial_rows": pl.DataFrame(),
                "match_count": 0
            }

        # Clean null values and compare as uppercase string
        exact_rows = df.filter(
            pl.col(column_name)
            .cast(pl.Utf8)
            .str.strip_chars()
            .str.to_uppercase()
            == model_input_clean
        )

        partial_rows = df.filter(
            pl.col(column_name)
            .cast(pl.Utf8)
            .str.strip_chars()
            .str.to_uppercase()
            .str.contains(model_input_clean, literal=True)
        )

        return {
            "year": year_name,
            "exact_match": exact_rows.height > 0,
            "partial_match": partial_rows.height > 0,
            "exact_rows": exact_rows,
            "partial_rows": partial_rows,
            "match_count": exact_rows.height
        }

    result_26y = search_one_dataframe(df_26y, "26Y")
    result_27y = search_one_dataframe(df_27y, "27Y")

    matched_26y = result_26y["exact_match"] or result_26y["partial_match"]
    matched_27y = result_27y["exact_match"] or result_27y["partial_match"]

    if matched_26y and matched_27y:
        matched_location = "Both 26Y and 27Y"
    elif matched_26y:
        matched_location = "26Y"
    elif matched_27y:
        matched_location = "27Y"
    else:
        matched_location = "No match found"

    return {
        "input": model_input,
        "matched_location": matched_location,
        "matched_26y": matched_26y,
        "matched_27y": matched_27y,
        "result_26y": result_26y,
        "result_27y": result_27y
    }
    
    
#
# ==> Detemine Name ifeven not 100% match beween DataFrame <== 

def normalize_model_name(value) -> str:
    """
    Clean model name before comparing:
    - Convert to string
    - Remove spaces
    - Convert to uppercase
    - Remove non-alphanumeric characters
    """

    if value is None:
        return ""

    value = str(value).strip().upper()
    value = re.sub(r"[^A-Z0-9]", "", value)

    return value


def calculate_match_percentage(input_name: str, candidate_name: str) -> float:
    """
    Calculate similarity percentage between input_name and candidate_name.
    Returns a value from 0 to 100.
    """

    input_clean = normalize_model_name(input_name)
    candidate_clean = normalize_model_name(candidate_name)

    if input_clean == "" or candidate_clean == "":
        return 0.0

    score = SequenceMatcher(None, input_clean, candidate_clean).ratio() * 100

    return round(score, 2)


def get_best_model_matches(
    model_input: str,
    df_26y: pl.DataFrame,
    df_27y: pl.DataFrame,
    column_name: str = "Model Name",
    top_n: int = 10
) -> dict:
    """
    Find the best matching model names from both 26Y and 27Y DataFrames.

    Returns:
    - best match in 26Y
    - best match in 27Y
    - best overall match
    - top matching rows from both DataFrames
    """

    def score_dataframe(df: pl.DataFrame, year_name: str) -> pl.DataFrame:
        if column_name not in df.columns:
            return pl.DataFrame({
                "Year": [],
                "Input": [],
                "Matched Model Name": [],
                "Match Percentage": []
            })

        model_names = (
            df
            .select(column_name)
            .drop_nulls()
            .unique()
            .to_series()
            .to_list()
        )

        scored_rows = []

        for model_name in model_names:
            score = calculate_match_percentage(model_input, model_name)

            scored_rows.append({
                "Year": year_name,
                "Input": model_input,
                "Matched Model Name": model_name,
                "Match Percentage": score
            })

        if not scored_rows:
            return pl.DataFrame({
                "Year": [],
                "Input": [],
                "Matched Model Name": [],
                "Match Percentage": []
            })

        return (
            pl.DataFrame(scored_rows)
            .sort("Match Percentage", descending=True)
            .head(top_n)
        )

    result_26y = score_dataframe(df_26y, "26Y")
    result_27y = score_dataframe(df_27y, "27Y")

    all_results = pl.concat([result_26y, result_27y], how="vertical")

    if all_results.height == 0:
        return {
            "input": model_input,
            "best_location": "No data found",
            "best_match": None,
            "best_score": 0.0,
            "result_26y": result_26y,
            "result_27y": result_27y,
            "all_results": all_results
        }

    all_results = all_results.sort("Match Percentage", descending=True)

    best_row = all_results.row(0, named=True)

    best_location = best_row["Year"]
    best_match = best_row["Matched Model Name"]
    best_score = best_row["Match Percentage"]

    return {
        "input": model_input,
        "best_location": best_location,
        "best_match": best_match,
        "best_score": best_score,
        "result_26y": result_26y,
        "result_27y": result_27y,
        "all_results": all_results
    }


#
# ==> Classify Model with Disguisable Rule <==
#    
def analyze_dataframe_distinction_rules(
    df_26y: pl.DataFrame,
    df_27y: pl.DataFrame,
    column_name: str = "Model Name",
    min_confidence: float = 80.0
) -> dict:
    """
    Analyze both 26Y and 27Y DataFrames and find character-position rules
    that can distinguish 26Y from 27Y.

    Example:
    If many 26Y models have 'B' at position 8
    and many 27Y models have 'C' at position 8,
    the function will create a rule like:

    position 8:
        B -> 26Y
        C -> 27Y

    Returns:
    - rules DataFrame
    - raw position analysis
    - model counts
    """

    def get_unique_model_names(df: pl.DataFrame) -> list[str]:
        if column_name not in df.columns:
            return []

        model_names = (
            df
            .select(column_name)
            .drop_nulls()
            .unique()
            .to_series()
            .to_list()
        )

        cleaned_model_names = []

        for model_name in model_names:
            cleaned_name = normalize_model_name(model_name)

            if cleaned_name != "":
                cleaned_model_names.append(cleaned_name)

        return cleaned_model_names

    models_26y = get_unique_model_names(df_26y)
    models_27y = get_unique_model_names(df_27y)

    all_models = models_26y + models_27y

    if not all_models:
        return {
            "rules": pl.DataFrame(),
            "position_analysis": pl.DataFrame(),
            "model_count_26y": 0,
            "model_count_27y": 0
        }

    max_len = max(len(model) for model in all_models)

    analysis_rows = []

    for position in range(max_len):
        chars_26y = {}
        chars_27y = {}

        for model in models_26y:
            char = model[position] if position < len(model) else "<END>"
            chars_26y[char] = chars_26y.get(char, 0) + 1

        for model in models_27y:
            char = model[position] if position < len(model) else "<END>"
            chars_27y[char] = chars_27y.get(char, 0) + 1

        all_chars = set(chars_26y.keys()) | set(chars_27y.keys())

        for char in all_chars:
            count_26y = chars_26y.get(char, 0)
            count_27y = chars_27y.get(char, 0)
            total = count_26y + count_27y

            if total == 0:
                continue

            confidence_26y = round((count_26y / total) * 100, 2)
            confidence_27y = round((count_27y / total) * 100, 2)

            if count_26y > count_27y:
                predicted_year = "26Y"
                confidence = confidence_26y
            elif count_27y > count_26y:
                predicted_year = "27Y"
                confidence = confidence_27y
            else:
                predicted_year = "Ambiguous"
                confidence = 50.0

            analysis_rows.append({
                "Position": position,
                "Character": char,
                "Count 26Y": count_26y,
                "Count 27Y": count_27y,
                "Predicted Year": predicted_year,
                "Confidence": confidence
            })

    position_analysis = pl.DataFrame(analysis_rows)

    if position_analysis.height == 0:
        rules = pl.DataFrame()
    else:
        rules = (
            position_analysis
            .filter(
                (pl.col("Predicted Year") != "Ambiguous") &
                (pl.col("Confidence") >= min_confidence)
            )
            .sort(["Position", "Confidence"], descending=[False, True])
        )

    return {
        "rules": rules,
        "position_analysis": position_analysis,
        "model_count_26y": len(models_26y),
        "model_count_27y": len(models_27y)
    }
    

def classify_model_with_distinction_rules(
    model_input: str,
    df_26y: pl.DataFrame,
    df_27y: pl.DataFrame,
    column_name: str = "Model Name",
    top_n: int = 10,
    min_rule_confidence: float = 80.0
) -> dict:
    """
    Classify model_input as 26Y or 27Y using:
    1. Best similarity match
    2. Distinction rules learned from both DataFrames

    This helps cases like:
    - 85QNED76CAA should be detected as 27Y if 'C' at a certain position
      is strongly associated with 27Y.
    - 85QNED76BAA should be detected as 26Y if 'B' at that position
      is strongly associated with 26Y.
    """

    model_clean = normalize_model_name(model_input)

    distinction_result = analyze_dataframe_distinction_rules(
        df_26y=df_26y,
        df_27y=df_27y,
        column_name=column_name,
        min_confidence=min_rule_confidence
    )

    rules = distinction_result["rules"]

    match_score_result = get_best_model_matches(
        model_input=model_input,
        df_26y=df_26y,
        df_27y=df_27y,
        column_name=column_name,
        top_n=top_n
    )

    rule_votes_26y = 0
    rule_votes_27y = 0
    matched_rule_rows = []

    if rules.height > 0 and model_clean != "":
        for row in rules.iter_rows(named=True):
            position = row["Position"]
            character = row["Character"]

            if position < len(model_clean):
                input_character = model_clean[position]
            else:
                input_character = "<END>"

            if input_character == character:
                predicted_year = row["Predicted Year"]
                confidence = row["Confidence"]

                if predicted_year == "26Y":
                    rule_votes_26y += confidence
                elif predicted_year == "27Y":
                    rule_votes_27y += confidence

                matched_rule_rows.append({
                    "Position": position,
                    "Input Character": input_character,
                    "Rule Character": character,
                    "Predicted Year": predicted_year,
                    "Rule Confidence": confidence,
                    "Count 26Y": row["Count 26Y"],
                    "Count 27Y": row["Count 27Y"]
                })

    matched_rules = (
        pl.DataFrame(matched_rule_rows)
        if matched_rule_rows
        else pl.DataFrame({
            "Position": [],
            "Input Character": [],
            "Rule Character": [],
            "Predicted Year": [],
            "Rule Confidence": [],
            "Count 26Y": [],
            "Count 27Y": []
        })
    )

    best_similarity_location = match_score_result["best_location"]
    best_similarity_score = match_score_result["best_score"]
    best_similarity_match = match_score_result["best_match"]

    similarity_vote_26y = 0
    similarity_vote_27y = 0

    if best_similarity_location == "26Y":
        similarity_vote_26y = best_similarity_score
    elif best_similarity_location == "27Y":
        similarity_vote_27y = best_similarity_score

    final_score_26y = similarity_vote_26y + rule_votes_26y
    final_score_27y = similarity_vote_27y + rule_votes_27y

    if final_score_26y > final_score_27y:
        final_classification = "26Y"
    elif final_score_27y > final_score_26y:
        final_classification = "27Y"
    else:
        final_classification = "Ambiguous"

    return {
        "input": model_input,
        "normalized_input": model_clean,
        "final_classification": final_classification,
        "final_score_26y": round(final_score_26y, 2),
        "final_score_27y": round(final_score_27y, 2),
        "best_similarity_location": best_similarity_location,
        "best_similarity_match": best_similarity_match,
        "best_similarity_score": best_similarity_score,
        "rule_votes_26y": round(rule_votes_26y, 2),
        "rule_votes_27y": round(rule_votes_27y, 2),
        "matched_rules": matched_rules,
        "distinction_rules": rules,
        "match_score_result": match_score_result
    }

    
# 
# ==> Summarize Result for Indentification <==
#    

def dataframe_to_dicts(value):
    """
    Convert Polars DataFrame to list of dictionaries.
    """

    if isinstance(value, pl.DataFrame):
        return value.to_dicts()

    return value


def search_model_with_fallback_score(
    model_input: str,
    df_26y: pl.DataFrame,
    df_27y: pl.DataFrame,
    column_name: str = "Model Name",
    top_n: int = 10
) -> dict:
    """
    Search exact/partial first.
    If no result exists, use match score fallback.
    Output is JSON-ready dictionary.
    """

    search_result = search_model_in_dataframes(
        model_input=model_input,
        df_26y=df_26y,
        df_27y=df_27y,
        column_name=column_name
    )

    has_exact_or_partial_match = (
        search_result["matched_26y"] or
        search_result["matched_27y"]
    )

    if has_exact_or_partial_match:
        json_ready_result = {
            "input": str(search_result["input"]),
            "matched_location": str(search_result["matched_location"]),
            "matched_26y": int(search_result["matched_26y"]),
            "matched_27y": int(search_result["matched_27y"]),

            "result_26y": {
                "year": str(search_result["result_26y"]["year"]),
                "exact_match": int(search_result["result_26y"]["exact_match"]),
                "partial_match": int(search_result["result_26y"]["partial_match"]),
                "exact_rows": dataframe_to_dicts(search_result["result_26y"]["exact_rows"]),
                "partial_rows": dataframe_to_dicts(search_result["result_26y"]["partial_rows"]),
                "match_count": int(search_result["result_26y"]["match_count"])
            },

            "result_27y": {
                "year": str(search_result["result_27y"]["year"]),
                "exact_match": int(search_result["result_27y"]["exact_match"]),
                "partial_match": int(search_result["result_27y"]["partial_match"]),
                "exact_rows": dataframe_to_dicts(search_result["result_27y"]["exact_rows"]),
                "partial_rows": dataframe_to_dicts(search_result["result_27y"]["partial_rows"]),
                "match_count": int(search_result["result_27y"]["match_count"])
            },

            "search_method": "exact_or_partial_search",
            "used_fallback_score": 0,
            "best_match": "",
            "best_score": 0,
            "match_score_result": {}
        }

        return json_ready_result

    match_score_result = get_best_model_matches(
        model_input=model_input,
        df_26y=df_26y,
        df_27y=df_27y,
        column_name=column_name,
        top_n=top_n
    )

    best_location = match_score_result["best_location"]

    matched_26y = best_location == "26Y"
    matched_27y = best_location == "27Y"

    if matched_26y:
        matched_location = "26Y"
    elif matched_27y:
        matched_location = "27Y"
    else:
        matched_location = "No match found"

    fallback_result = {
        "input": str(model_input),
        "matched_location": str(matched_location),
        "matched_26y": int(matched_26y),
        "matched_27y": int(matched_27y),

        "result_26y": {
            "year": "26Y",
            "exact_match": 0,
            "partial_match": 0,
            "exact_rows": [],
            "partial_rows": dataframe_to_dicts(match_score_result["result_26y"]),
            "match_count": int(match_score_result["result_26y"].height)
        },

        "result_27y": {
            "year": "27Y",
            "exact_match": 0,
            "partial_match": 0,
            "exact_rows": [],
            "partial_rows": dataframe_to_dicts(match_score_result["result_27y"]),
            "match_count": int(match_score_result["result_27y"].height)
        },

        "search_method": "fallback_match_score",
        "used_fallback_score": 1,
        "best_match": str(match_score_result["best_match"]) if match_score_result["best_match"] is not None else "",
        "best_score": int(round(match_score_result["best_score"])) if match_score_result["best_score"] is not None else 0,

        "match_score_result": {
            "input": str(match_score_result["input"]),
            "best_location": str(match_score_result["best_location"]),
            "best_match": str(match_score_result["best_match"]) if match_score_result["best_match"] is not None else "",
            "best_score": int(round(match_score_result["best_score"])) if match_score_result["best_score"] is not None else 0,
            "result_26y": dataframe_to_dicts(match_score_result["result_26y"]),
            "result_27y": dataframe_to_dicts(match_score_result["result_27y"]),
            "all_results": dataframe_to_dicts(match_score_result["all_results"])
        }
    }

    return fallback_result


"""final_result = search_model_with_fallback_score(
    model_input=modelName,
    df_26y=modelName26Y,
    df_27y=modelName27Y,
    column_name="Model Name",
    top_n=5
)"""

def db_search_model_with_fallback_score(modelName):
    get_modelFrame26Y = read_latest_version(
        db_uri=HerosURL,
        prefix="HEROmodel2026Y_v3.3_v"
    )

    get_modelFrame27Y = read_latest_version(
        db_uri=HerosURL,
        prefix="HEROmodel2027Y_v1.0_v"
    )


    modelName26Y = get_modelFrame26Y.select([
        "Model Name"
    ])


    modelName27Y = get_modelFrame27Y.select([
        "Model Name"
    ])

    final_result = search_model_with_fallback_score(
        model_input=modelName,
        df_26y=modelName26Y,
        df_27y=modelName27Y,
        column_name="Model Name",
        top_n=5
    )


    return final_result



#json_output = json.dumps(final_result, indent=4, ensure_ascii=False)

#print(json_output)
