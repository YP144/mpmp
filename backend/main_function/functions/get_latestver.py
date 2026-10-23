
import dej_sdk

import polars as pl
import json
import requests
import sys
import os
import requests
import html
from urllib.parse import parse_qs
from datetime import datetime
import time
from dateutil.relativedelta import relativedelta
import re
from datetime import datetime
import connectorx
from sqlalchemy import create_engine, text
import json
import numpy as np
import pandas as pd
import polars as pl

import re
import polars as pl
from sqlalchemy import create_engine, text


def read_latest_version(
    db_uri: str,
    prefix: str = "structureTemplate_v",
    schema: str = "public",
) -> pl.DataFrame:
    """
    Find the latest versioned table and read it.

    Example table names:
        structureTemplate_v1_0
        structureTemplate_v2_0
        structureTemplate_v3_0
    """

    tables_df = pl.read_database_uri(
        query=f"""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = '{schema}'
              AND table_name LIKE '{prefix}%'
        """,
        uri=db_uri,
    )

    versions = []

    for table_name in tables_df["table_name"].to_list():
        match = re.match(rf"^{re.escape(prefix)}(\d+)_(\d+)$", table_name)

        if match:
            major = int(match.group(1))
            minor = int(match.group(2))
            versions.append((major, minor, table_name))

    if not versions:
        raise Exception(f"No versioned table found with prefix: {prefix}")

    latest_major, latest_minor, latest_table = max(
        versions,
        key=lambda x: (x[0], x[1])
    )

    print("Latest version:", f"v{latest_major}.{latest_minor}")
    print("Latest table:", latest_table)

    query = f'SELECT * FROM {schema}."{latest_table}"'

    print("Read query:", query)

    df = pl.read_database_uri(
        query=query,
        uri=db_uri,
    )

    return df

def read_table(
    db_uri: str,
    table_name: str,
    schema: str = "public",
) -> pl.DataFrame:
    """
    Read a normal non-versioned table.

    Example:
        SELECT * FROM public.all_engineer
    """

    query = f'SELECT * FROM {schema}."{table_name}"'

    print("Read query:", query)

    df = pl.read_database_uri(
        query=query,
        uri=db_uri,
    )

    return df


