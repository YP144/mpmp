import json
import re
from typing import Union, Dict, List, Any, Optional, Tuple

import polars as pl


JsonLike = Union[str, Dict[str, Any], List[Any]]


def normalize_json_to_dataframe(
    data: JsonLike,
    flatten: bool = True,
    standardize_names: bool = True,
    fill_nulls: bool = False,
    fill_value: Any = None,
    infer_types: bool = True,
    remove_duplicates: bool = False,
    record_path: Optional[Union[str, List[Union[str, int]]]] = None,
    auto_extract_records: bool = True,
    record_keys: Optional[List[str]] = None,
    parent_keys: Optional[List[str]] = None,
    concat_all_records: bool = True,
    include_parent_context: bool = True,
    include_source_metadata: bool = True,
    explode_lists: bool = False,
    include_dict_records: bool = True,
    include_root_record: bool = False,
    list_as_json: bool = True,
    separator: str = ".",
) -> pl.DataFrame:
    """
    Normalize JSON / dict / list data into one Polars DataFrame.

    This function recursively collects records from all nested JSON structures,
    including MotherData, ParentData, data, childData, relatedRequestList, partVO,
    technicalValueSet.al, and other list/dict containers.
    """

    parsed_data = _parse_input(data)

    if record_keys is None:
        record_keys = [
            "MotherData",
            "motherData",
            "mother_data",
            "ParentData",
            "parentData",
            "parent_data",
            "data",
            "Data",
            "ChildData",
            "childData",
            "child_data",
            "children",
            "Children",
            "child",
            "items",
            "item",
            "rows",
            "row",
            "results",
            "result",
            "records",
            "record",
            "contents",
            "content",
            "list",
            "payload",
            "body",
            "response",
            "relatedRequestList",
            "related_request_list",
            "partVO",
            "partVo",
            "part_vo",
            "technicalValueSet",
            "technical_value_set",
            "al",
        ]

    if parent_keys is None:
        parent_keys = [
            "MotherData",
            "motherData",
            "mother_data",
            "ParentData",
            "parentData",
            "parent_data",
            "data",
            "Data",
            "ChildData",
            "childData",
            "child_data",
            "children",
            "Children",
            "child",
            "payload",
            "body",
            "response",
            "result",
            "results",
        ]

    if record_path is not None:
        selected = _get_by_path(parsed_data, record_path, separator=separator)
        records = _records_from_explicit_path(
            selected=selected,
            path=_path_to_string(record_path),
            include_source_metadata=include_source_metadata,
            separator=separator,
        )
    elif concat_all_records:
        records = _collect_all_records(
            data=parsed_data,
            record_keys=record_keys,
            parent_keys=parent_keys,
            include_parent_context=include_parent_context,
            include_source_metadata=include_source_metadata,
            explode_lists=explode_lists,
            include_dict_records=include_dict_records,
            include_root_record=include_root_record,
            separator=separator,
        )
    else:
        extracted = _extract_first_records(
            data=parsed_data,
            auto_extract_records=auto_extract_records,
            record_keys=record_keys,
        )
        records = _normalize_records(extracted)

        if include_source_metadata:
            for idx, record in enumerate(records):
                record.setdefault("_source_path", "auto")
                record.setdefault("_source_key", "auto")
                record.setdefault("_record_level", "record")
                record.setdefault("_record_index", idx)

    if not records:
        return pl.DataFrame()

    if flatten:
        records = [
            _flatten_dict(
                record,
                separator=separator,
                list_as_json=list_as_json,
            )
            for record in records
        ]

    records = _make_polars_safe_records(records)

    try:
        df = pl.DataFrame(records, infer_schema_length=None)
    except Exception as e:
        raise ValueError(f"Failed to create Polars DataFrame: {e}") from e

    if standardize_names:
        df = _rename_columns_safely(df)

    if infer_types:
        df = _infer_types(df)

    if fill_nulls:
        df = _fill_nulls_smart(df, fill_value)

    if remove_duplicates and df.height > 0:
        df = df.unique(maintain_order=True)

    return df


def normalize_json_to_dataframes(
    data: JsonLike,
    flatten: bool = True,
    standardize_names: bool = True,
    infer_types: bool = True,
    include_parent_context: bool = True,
    include_source_metadata: bool = True,
    separator: str = ".",
) -> Dict[str, pl.DataFrame]:
    """
    Return one DataFrame per source path.

    This is useful when you do not want heterogeneous row types in one DataFrame.
    """

    df = normalize_json_to_dataframe(
        data=data,
        flatten=flatten,
        standardize_names=False,
        fill_nulls=False,
        infer_types=False,
        concat_all_records=True,
        include_parent_context=include_parent_context,
        include_source_metadata=include_source_metadata,
        separator=separator,
    )

    if df.is_empty() or "_source_path" not in df.columns:
        return {"root": df}

    output: Dict[str, pl.DataFrame] = {}

    source_paths = (
        df.select(pl.col("_source_path"))
        .unique(maintain_order=True)
        .to_series()
        .to_list()
    )

    for source_path in source_paths:
        sub_df = df.filter(pl.col("_source_path") == source_path)

        if standardize_names:
            sub_df = _rename_columns_safely(sub_df)

        if infer_types:
            sub_df = _infer_types(sub_df)

        output[str(source_path)] = sub_df

    return output


def _parse_input(data: JsonLike) -> Union[Dict[str, Any], List[Any]]:
    """
    Parse JSON string, dict, or list.
    """

    if isinstance(data, dict):
        return data

    if isinstance(data, list):
        return data

    if isinstance(data, str):
        text = data.strip()

        if not text:
            raise ValueError("Input string is empty.")

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError("String input must be valid JSON.") from e

        if not isinstance(parsed, (dict, list)):
            raise ValueError(
                f"JSON string must decode to dict or list, got {type(parsed).__name__}."
            )

        return parsed

    raise ValueError(
        f"Unsupported input type: {type(data).__name__}. Expected JSON string, dict, or list."
    )


def _records_from_explicit_path(
    selected: Any,
    path: str,
    include_source_metadata: bool = True,
    separator: str = ".",
) -> List[Dict[str, Any]]:
    """
    Convert selected path data to list of records.
    """

    records = _normalize_records(selected)

    if include_source_metadata:
        source_key = _last_path_key(path)

        for idx, record in enumerate(records):
            record.setdefault("_source_path", path)
            record.setdefault("_source_key", source_key)
            record.setdefault("_record_level", _level_from_path(path))
            record.setdefault("_record_index", idx)

    return records


def _collect_all_records(
    data: Any,
    record_keys: List[str],
    parent_keys: List[str],
    include_parent_context: bool = True,
    include_source_metadata: bool = True,
    explode_lists: bool = False,
    include_dict_records: bool = True,
    include_root_record: bool = False,
    separator: str = ".",
) -> List[Dict[str, Any]]:
    """
    Recursively collect all records from nested JSON.

    This handles:
    - Root scalar metadata such as httpStatus, message, timestamp.
    - data scalar metadata such as displayType, currentUserId, Result.
    - Lists of dicts such as data.relatedRequestList.
    - Dict records such as data.partVO.
    - Deep child lists such as data.partVO.technicalValueSet.al.
    - MotherData / ParentData / ChildData style structures.
    """

    collected: List[Dict[str, Any]] = []

    def walk(
        value: Any,
        path: str = "root",
        context: Optional[Dict[str, Any]] = None,
        level: str = "root",
        source_index: Optional[int] = None,
    ) -> None:
        if context is None:
            context = {}

        if isinstance(value, dict):
            current_context = dict(context)

            if include_parent_context:
                scalar_context = _extract_scalar_context(value)
                for key, scalar_value in scalar_context.items():
                    context_key = f"_context{separator}{key}"
                    current_context.setdefault(context_key, scalar_value)

            should_add_dict = False

            if path == "root" and include_root_record:
                should_add_dict = _looks_like_record(value)
            elif include_dict_records and path != "root":
                should_add_dict = _looks_like_record(value) and (
                    _path_or_key_matches(path, record_keys)
                    or _has_nested_record_container(value, record_keys)
                    or _is_leaf_record_dict(value)
                )

            if should_add_dict:
                row = dict(context)

                for key, child in value.items():
                    row[key] = child

                if include_source_metadata:
                    row["_source_path"] = path
                    row["_source_key"] = _last_path_key(path)
                    row["_record_level"] = _level_from_path(path)
                    row["_record_index"] = 0 if source_index is None else source_index

                collected.append(row)

            for key, child in value.items():
                child_path = f"{path}{separator}{key}" if path else str(key)
                child_level = _level_from_key(key, parent_keys)

                if _is_list_of_dicts(child):
                    rows = _rows_from_list_of_dicts(
                        items=child,
                        path=child_path,
                        key=key,
                        level=child_level,
                        context=current_context,
                        include_source_metadata=include_source_metadata,
                        explode_lists=explode_lists,
                    )
                    collected.extend(rows)

                    for idx, item in enumerate(child):
                        walk(
                            value=item,
                            path=f"{child_path}[{idx}]",
                            context=current_context,
                            level=child_level,
                            source_index=idx,
                        )

                elif isinstance(child, list):
                    if _path_or_key_matches(child_path, record_keys) or key in record_keys:
                        rows = _rows_from_any_list(
                            items=child,
                            path=child_path,
                            key=key,
                            level=child_level,
                            context=current_context,
                            include_source_metadata=include_source_metadata,
                        )
                        collected.extend(rows)

                    for idx, item in enumerate(child):
                        walk(
                            value=item,
                            path=f"{child_path}[{idx}]",
                            context=current_context,
                            level=child_level,
                            source_index=idx,
                        )

                elif isinstance(child, dict):
                    walk(
                        value=child,
                        path=child_path,
                        context=current_context,
                        level=child_level,
                        source_index=0,
                    )

        elif isinstance(value, list):
            if _is_list_of_dicts(value):
                key = _last_path_key(path)
                rows = _rows_from_list_of_dicts(
                    items=value,
                    path=path,
                    key=key,
                    level=level,
                    context=context,
                    include_source_metadata=include_source_metadata,
                    explode_lists=explode_lists,
                )
                collected.extend(rows)

                for idx, item in enumerate(value):
                    walk(
                        value=item,
                        path=f"{path}[{idx}]",
                        context=context,
                        level=level,
                        source_index=idx,
                    )

            else:
                for idx, item in enumerate(value):
                    walk(
                        value=item,
                        path=f"{path}[{idx}]",
                        context=context,
                        level=level,
                        source_index=idx,
                    )

    walk(data)

    return _dedupe_records_by_identity(collected)


def _rows_from_list_of_dicts(
    items: List[Dict[str, Any]],
    path: str,
    key: str,
    level: str,
    context: Dict[str, Any],
    include_source_metadata: bool = True,
    explode_lists: bool = False,
) -> List[Dict[str, Any]]:
    """
    Convert a list of dictionaries into records.
    """

    rows: List[Dict[str, Any]] = []

    for idx, item in enumerate(items):
        row = dict(context)
        row.update(item)

        if include_source_metadata:
            row["_source_path"] = path
            row["_source_key"] = key
            row["_record_level"] = level
            row["_record_index"] = idx

        if explode_lists:
            rows.extend(_explode_record_lists(row))
        else:
            rows.append(row)

    return rows


def _rows_from_any_list(
    items: List[Any],
    path: str,
    key: str,
    level: str,
    context: Dict[str, Any],
    include_source_metadata: bool = True,
) -> List[Dict[str, Any]]:
    """
    Convert any list into records.

    For scalar lists:
        ["a", "b"] -> rows with value column.
    """

    rows: List[Dict[str, Any]] = []

    for idx, item in enumerate(items):
        row = dict(context)

        if isinstance(item, dict):
            row.update(item)
        else:
            row["value"] = item

        if include_source_metadata:
            row["_source_path"] = path
            row["_source_key"] = key
            row["_record_level"] = level
            row["_record_index"] = idx

        rows.append(row)

    return rows


def _explode_record_lists(record: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Explode one level of list-of-dicts inside a row.
    """

    rows = [dict(record)]

    for key, value in list(record.items()):
        if not _is_list_of_dicts(value):
            continue

        new_rows: List[Dict[str, Any]] = []

        for row in rows:
            child_items = row.pop(key, [])

            if not child_items:
                new_rows.append(row)
                continue

            for child in child_items:
                expanded = dict(row)

                for child_key, child_value in child.items():
                    expanded[f"{key}.{child_key}"] = child_value

                new_rows.append(expanded)

        rows = new_rows

    return rows


def _normalize_records(value: Any) -> List[Dict[str, Any]]:
    """
    Normalize any value into list[dict].
    """

    if isinstance(value, dict):
        return [value]

    if isinstance(value, list):
        records: List[Dict[str, Any]] = []

        for item in value:
            if isinstance(item, dict):
                records.append(item)
            else:
                records.append({"value": item})

        return records

    return [{"value": value}]


def _extract_first_records(
    data: Any,
    auto_extract_records: bool = True,
    record_keys: Optional[List[str]] = None,
) -> Any:
    """
    Backward-compatible first-record extraction.

    If concat_all_records=False, this selects the first/best list-of-dicts.
    """

    if isinstance(data, list):
        return data

    if not isinstance(data, dict):
        return data

    if not auto_extract_records:
        return data

    keys = record_keys or []

    direct_candidate = _find_direct_record_list(data, keys)
    if direct_candidate is not None:
        return direct_candidate

    nested_candidate = _find_nested_record_list(data, keys)
    if nested_candidate is not None:
        return nested_candidate

    largest_candidate = _find_largest_list_of_dicts(data)
    if largest_candidate is not None:
        return largest_candidate

    return data


def _find_direct_record_list(data: Dict[str, Any], record_keys: List[str]) -> Optional[List[Dict[str, Any]]]:
    """
    Find a direct child list-of-dicts under preferred record keys.
    """

    for key in record_keys:
        if key not in data:
            continue

        value = data[key]

        if _is_list_of_dicts(value):
            return value

        if isinstance(value, dict):
            nested = _find_direct_record_list(value, record_keys)
            if nested is not None:
                return nested

    return None


def _find_nested_record_list(data: Any, record_keys: List[str]) -> Optional[List[Dict[str, Any]]]:
    """
    Recursively search for first list-of-dicts under preferred keys.
    """

    if isinstance(data, dict):
        for key, value in data.items():
            if key in record_keys and _is_list_of_dicts(value):
                return value

        for value in data.values():
            found = _find_nested_record_list(value, record_keys)
            if found is not None:
                return found

    elif isinstance(data, list):
        if _is_list_of_dicts(data):
            return data

        for item in data:
            found = _find_nested_record_list(item, record_keys)
            if found is not None:
                return found

    return None


def _find_largest_list_of_dicts(data: Any) -> Optional[List[Dict[str, Any]]]:
    """
    Find the largest list-of-dicts anywhere in the JSON tree.

    This is used only when concat_all_records=False and the function needs to
    choose one best table automatically.
    """

    largest: Optional[List[Dict[str, Any]]] = None
    largest_len = 0

    def walk(value: Any) -> None:
        nonlocal largest, largest_len

        if _is_list_of_dicts(value):
            if len(value) > largest_len:
                    largest = value
                    largest_len = len(value)

                for item in value:
                    walk(item)

            elif isinstance(value, dict):
                for child in value.values():
                    walk(child)

            elif isinstance(value, list):
                for item in value:
                    walk(item)

        walk(data)
        return largest


def _is_list_of_dicts(value: Any) -> bool:
    """
    True when value is a non-empty list and every non-null item is a dict.

    Empty lists are not treated as record tables because they do not provide
    fields for schema creation.
    """

    if not isinstance(value, list) or not value:
        return False

    dict_items = [item for item in value if item is not None]
    return bool(dict_items) and all(isinstance(item, dict) for item in dict_items)


def _looks_like_record(value: Any) -> bool:
    """
    Decide whether a dict can be represented as a DataFrame row.

    A record usually has at least one scalar value. Dicts containing only nested
    containers are treated as containers, not records.
    """

    if not isinstance(value, dict) or not value:
        return False

    return any(not isinstance(v, (dict, list)) for v in value.values())


def _is_leaf_record_dict(value: Any) -> bool:
    """
    True when a dict has no nested dict/list values.

    This is useful for child objects like:
        {"an": "...", "av": "..."}
    """

    if not isinstance(value, dict) or not value:
        return False

    return all(not isinstance(v, (dict, list)) for v in value.values())


def _has_nested_record_container(
    value: Any,
    record_keys: Optional[List[str]] = None,
) -> bool:
    """
    True if a dict contains nested data that looks like records.
    """

    keys = record_keys or []

    if not isinstance(value, dict):
        return False

    for key, child in value.items():
        if key in keys and (_is_list_of_dicts(child) or isinstance(child, dict)):
            return True

        if _is_list_of_dicts(child):
            return True

    return False


def _extract_scalar_context(value: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract only scalar fields from a dict.

    These scalar fields are propagated to child rows as context columns.
    """

    context: Dict[str, Any] = {}

    for key, child in value.items():
        if isinstance(child, (dict, list)):
            continue

        context[key] = child

    return context


def _path_or_key_matches(path: str, keys: List[str]) -> bool:
    """
    Check whether the current path or its last key matches preferred record keys.
    """

    if not keys:
        return False

    last_key = _last_path_key(path)

    if last_key in keys:
        return True

    normalized_path = path.replace("[", ".[")

    for key in keys:
        if path == key:
            return True

        if path.endswith(f".{key}"):
            return True

        if f".{key}." in normalized_path:
            return True

        if f".{key}[" in normalized_path:
            return True

    return False


def _last_path_key(path: str) -> str:
    """
    Return the last logical key from a path.

    Example:
        root.data.relatedRequestList[0] -> relatedRequestList
    """

    if not path:
        return "root"

    clean = re.sub(r"$$\d+$$$", "", str(path))
    clean = clean.rstrip(".")

    if "." in clean:
        return clean.split(".")[-1]

    return clean or "root"


def _level_from_key(key: str, parent_keys: List[str]) -> str:
    """
    Return a friendly record level based on common parent/child names.
    """

    key_lower = str(key).lower()

    if key_lower in {"motherdata", "mother_data"}:
        return "mother"

    if key_lower in {"parentdata", "parent_data", "parent"}:
        return "parent"

    if key_lower in {"childdata", "child_data", "children", "child"}:
        return "child"

    if key_lower in {"data", "payload", "body", "response"}:
        return "data"

    if key_lower in {"relatedrequestlist", "related_request_list"}:
        return "related_request"

    if key_lower in {"partvo", "part_vo"}:
        return "part"

    if key_lower in {"technicalvalueset", "technical_value_set"}:
        return "technical_value_set"

    if key_lower == "al":
        return "technical_value"

    if key in parent_keys:
        return key

    return "record"


def _level_from_path(path: str) -> str:
    """
    Infer a record level from a source path.
    """

    path_lower = str(path).lower()

    if "motherdata" in path_lower or "mother_data" in path_lower:
        return "mother"

    if "parentdata" in path_lower or "parent_data" in path_lower:
        return "parent"

    if (
        "childdata" in path_lower
        or "child_data" in path_lower
        or ".children" in path_lower
        or ".child" in path_lower
    ):
        return "child"

    if "relatedrequestlist" in path_lower or "related_request_list" in path_lower:
        return "related_request"

    if "partvo" in path_lower or "part_vo" in path_lower:
        return "part"

    if "technicalvalueset" in path_lower or "technical_value_set" in path_lower:
        return "technical_value_set"

    if path_lower.endswith(".al") or ".al[" in path_lower:
        return "technical_value"

    if path_lower.endswith(".data") or ".data." in path_lower:
        return "data"

    return "record"


def _path_to_string(
    path: Union[str, List[Union[str, int]]],
    separator: str = ".",
) -> str:
    """
    Convert a path list/string into a readable path string.
    """

    if isinstance(path, str):
        return path

    parts: List[str] = []

    for part in path:
        if isinstance(part, int):
            if parts:
                parts[-1] = f"{parts[-1]}[{part}]"
            else:
                parts.append(f"[{part}]")
        else:
            parts.append(str(part))

    return separator.join(parts)


def _get_by_path(
    data: Any,
    path: Union[str, List[Union[str, int]]],
    separator: str = ".",
) -> Any:
    """
    Get data by dotted path or list path.

    Examples:
        "data.relatedRequestList"
        ["data", "partVO", "technicalValueSet", "al"]
    """

    if isinstance(path, str):
        parts: List[Union[str, int]] = _split_path(path, separator=separator)
    else:
        parts = path

    current = data

    for part in parts:
        if isinstance(part, int):
            if not isinstance(current, list):
                raise KeyError(f"Expected list before index {part}, got {type(current).__name__}.")

            current = current[part]
            continue

        if not isinstance(current, dict):
            raise KeyError(f"Expected dict before key '{part}', got {type(current).__name__}.")

        current = current[part]

    return current


def _split_path(path: str, separator: str = ".") -> List[Union[str, int]]:
    """
    Split dotted paths that may contain list indexes.

    Example:
        data.items[0].children -> ["data", "items", 0, "children"]
    """

    if not path:
        return []

    raw_parts = path.split(separator)
    parts: List[Union[str, int]] = []

    for raw_part in raw_parts:
        if raw_part == "":
            continue

        matches = re.finditer(r"([^$$$$]+)|$$(\d+)$$", raw_part)

        for match in matches:
            key_part = match.group(1)
            index_part = match.group(2)

            if key_part is not None:
                parts.append(key_part)

            if index_part is not None:
                parts.append(int(index_part))

    return parts


def _flatten_dict(
    record: Dict[str, Any],
    parent_key: str = "",
    separator: str = ".",
    list_as_json: bool = True,
) -> Dict[str, Any]:
    """
    Flatten nested dictionaries.

    Lists are kept as JSON strings by default unless they contain simple scalar
    values and list_as_json=False.
    """

    flattened: Dict[str, Any] = {}

    for key, value in record.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else str(key)

        if isinstance(value, dict):
            nested = _flatten_dict(
                value,
                parent_key=new_key,
                separator=separator,
                list_as_json=list_as_json,
            )
            flattened.update(nested)

        elif isinstance(value, list):
            if list_as_json:
                flattened[new_key] = json.dumps(value, ensure_ascii=False, default=str)
            else:
                flattened[new_key] = value

        else:
            flattened[new_key] = value

    return flattened


def _make_polars_safe_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Make rows safe for Polars DataFrame creation.

    Polars expects each column to have reasonably consistent data types. This
    function converts remaining dict/list values to JSON strings.
    """

    safe_records: List[Dict[str, Any]] = []

    for record in records:
        safe_record: Dict[str, Any] = {}

        for key, value in record.items():
            safe_key = str(key)

            if isinstance(value, (dict, list)):
                safe_record[safe_key] = json.dumps(value, ensure_ascii=False, default=str)
            else:
                safe_record[safe_key] = value

        safe_records.append(safe_record)

    return safe_records


def _rename_columns_safely(df: pl.DataFrame) -> pl.DataFrame:
    """
    Standardize column names and guarantee uniqueness.
    """

    rename_map: Dict[str, str] = {}
    used: Dict[str, int] = {}

    for column in df.columns:
        new_name = _standardize_column_name(column)

        if new_name in used:
            used[new_name] += 1
            new_name = f"{new_name}_{used[new_name]}"
        else:
            used[new_name] = 0

        rename_map[column] = new_name

    return df.rename(rename_map)


def _standardize_column_name(name: str) -> str:
    """
    Convert column names to snake_case-like safe names.

    Examples:
        outData.part_names -> outdata_part_names
        _source_path       -> source_path
    """

    text = str(name).strip()

    text = text.replace(".", "_")
    text = text.replace("-", "_")
    text = text.replace(" ", "_")
    text = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", text)
    text = re.sub(r"[^0-9a-zA-Z_가-힣]+", "_", text)
    text = re.sub(r"_+", "_", text)
    text = text.strip("_").lower()

    if not text:
        text = "column"

    if text[0].isdigit():
        text = f"col_{text}"

    return text


def _infer_types(df: pl.DataFrame) -> pl.DataFrame:
    """
    Infer practical column types.

    It attempts safe casts for string columns to bool, int, float, date, or
    datetime. If casting would lose many values, it keeps the original string.
    """

    if df.is_empty():
        return df

    output = df

    for column in output.columns:
        dtype = output.schema[column]

        if dtype != pl.String:
            continue

        series = output[column]
        non_null_count = series.drop_nulls().len()

        if non_null_count == 0:
            continue

        stripped = series.str.strip_chars()

        bool_candidate = stripped.str.to_lowercase()
        bool_values = {"true", "false", "yes", "no", "y", "n"}

        bool_matches = (
            bool_candidate
            .filter(bool_candidate.is_not_null() & bool_candidate.is_in(list(bool_values)))
            .len()
        )

        if bool_matches == non_null_count:
            output = output.with_columns(
                pl.when(pl.col(column).str.to_lowercase().is_in(["true", "yes", "y"]))
                .then(True)
                .when(pl.col(column).str.to_lowercase().is_in(["false", "no", "n"]))
                .then(False)
                .otherwise(None)
                .alias(column)
            )
            continue

        int_cast = stripped.cast(pl.Int64, strict=False)
        int_count = int_cast.drop_nulls().len()

        if int_count == non_null_count:
            output = output.with_columns(int_cast.alias(column))
            continue

        float_cast = stripped.cast(pl.Float64, strict=False)
        float_count = float_cast.drop_nulls().len()

        if float_count == non_null_count:
            output = output.with_columns(float_cast.alias(column))
            continue

        datetime_cast = stripped.str.strptime(
            pl.Datetime,
            format="%Y-%m-%d %H:%M:%S",
            strict=False,
        )
        datetime_count = datetime_cast.drop_nulls().len()

        if datetime_count == non_null_count:
            output = output.with_columns(datetime_cast.alias(column))
            continue

        date_cast = stripped.str.strptime(
            pl.Date,
            format="%Y-%m-%d",
            strict=False,
        )
        date_count = date_cast.drop_nulls().len()

        if date_count == non_null_count:
            output = output.with_columns(date_cast.alias(column))
            continue

    return output


def _fill_nulls_smart(df: pl.DataFrame, fill_value: Any = None) -> pl.DataFrame:
    """
    Fill null values.

    If fill_value is None, use sensible defaults by dtype.
    """

    if df.is_empty():
        return df

    if fill_value is not None:
        return df.fill_null(fill_value)

    expressions = []

    for column, dtype in df.schema.items():
        if dtype == pl.String:
            expressions.append(pl.col(column).fill_null("").alias(column))
        elif dtype in {
            pl.Int8,
            pl.Int16,
            pl.Int32,
            pl.Int64,
            pl.UInt8,
            pl.UInt16,
            pl.UInt32,
            pl.UInt64,
            pl.Float32,
            pl.Float64,
        }:
            expressions.append(pl.col(column).fill_null(0).alias(column))
        elif dtype == pl.Boolean:
            expressions.append(pl.col(column).fill_null(False).alias(column))
        else:
            expressions.append(pl.col(column).alias(column))

    return df.with_columns(expressions)


def _dedupe_records_by_identity(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove exact duplicate records while preserving order.

    This prevents duplicate rows caused by collecting a list item and then
    visiting the same dict again during recursive walking.
    """

    seen = set()
    output: List[Dict[str, Any]] = []

    for record in records:
        identity = _record_identity(record)

        if identity in seen:
            continue

        seen.add(identity)
        output.append(record)

    return output


def _record_identity(record: Dict[str, Any]) -> str:
    """
    Create stable JSON identity for duplicate detection.
    """

    try:
        return json.dumps(record, sort_keys=True, ensure_ascii=False, default=str)
    except TypeError:
        return str(sorted((str(k), str(v)) for k, v in record.items()))


if __name__ == "__main__":
    # Example usage:
    #
    # with open("input.json", "r", encoding="utf-8") as f:
    #     raw_json = f.read()
    #
    # df = normalize_json_to_dataframe(raw_json)
    # print(df)
    #
    # To inspect each record source separately:
    # dfs = normalize_json_to_dataframes(raw_json)
    # for source_path, source_df in dfs.items():
    #     print(source_path, source_df.shape)
    pass