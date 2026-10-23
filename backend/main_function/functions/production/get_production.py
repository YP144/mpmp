import html
import json
import logging
import random
import re
import time
from bs4 import BeautifulSoup
import pandas as pd
import requests

from main_function.services.check_sso import SSO_MARS

# Configure logger
logger = logging.getLogger("production_scraper")
logging.basicConfig(level=logging.INFO)


# get_production.py

def get_current_production_date(ssolgenet_cookie: str, smsession_cookie: str):
    final_df = pd.DataFrame()
    diagnostics = {
        "sso_status": False,
        "page_logs": [],
        "total_parsed_rows": 0,
        "final_rows_after_dedup": 0,
        "errors": []
    }

    try:
        sso = SSO_MARS()
        is_logged_in = sso.auto_login(
            ssolgenet_cookie=ssolgenet_cookie,
            smsession_cookie=smsession_cookie
        )
        diagnostics["sso_status"] = is_logged_in

        if not is_logged_in:
            error_msg = "SSO Login failed. Authentication token could not be issued."
            logger.error(error_msg)
            diagnostics["errors"].append(error_msg)
            return {
                "success": False,
                "data": [],
                "diagnostics": diagnostics
            }

    except Exception as e:
        error_msg = f"An error occurred during SSO initialization: {e}"
        logger.error(error_msg)
        diagnostics["errors"].append(error_msg)
        return {
            "success": False,
            "data": [],
            "diagnostics": diagnostics
        }

    mars_url = r"https://mp-schedule-monitoring-be-fe.apps.hedej.lge.com/pre-mp-pv-models/"
    mars_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://mp-schedule-monitoring-be-fe.apps.hedej.lge.com/pre-mp-pv-models/",
        "Authorization": f"Bearer {sso.auth_bearer}",
    }

    all_dfs = []

    for page_num in range(1, 6):
        page_log = {
            "page": page_num,
            "http_status": None,
            "table_found": False,
            "rows_extracted": 0,
            "error": None
        }

        mars_params = {"page": str(page_num), "filter": "all"}

        try:
            logger.info(f"[Page {page_num}] Fetching MARS data stream...")
            mars_response = sso.session.get(
                mars_url,
                headers=mars_headers,
                params=mars_params,
                timeout=15,
            )
            page_log["http_status"] = mars_response.status_code
            mars_response.raise_for_status()

        except requests.exceptions.HTTPError as http_err:
            error_str = f"HTTP Error on page {page_num}: Status {mars_response.status_code} - {http_err}"
            logger.error(error_str)
            page_log["error"] = error_str
            diagnostics["page_logs"].append(page_log)
            continue
        except requests.exceptions.RequestException as req_err:
            error_str = f"Network failure on page {page_num}: {req_err}"
            logger.error(error_str)
            page_log["error"] = error_str
            diagnostics["page_logs"].append(page_log)
            continue

        soup = BeautifulSoup(mars_response.text, "html.parser")
        table_tag = soup.find("table", id="mpTable")

        if table_tag:
            page_log["table_found"] = True
            try:
                clean_headers = []
                thead = table_tag.find("thead")
                if thead:
                    for th in thead.find_all("th"):
                        label_span = th.find("span", class_="th-label")
                        if label_span:
                            clean_headers.append(label_span.text.strip())
                        else:
                            clean_headers.append("Unknown")

                df = pd.read_html(str(table_tag))[0]

                if clean_headers and len(clean_headers) == len(df.columns):
                    df.columns = clean_headers

                df = df.dropna(how="all")
                rows_count = len(df)
                page_log["rows_extracted"] = rows_count
                logger.info(f"[Page {page_num}] Successfully parsed {rows_count} rows.")

                all_dfs.append(df)

            except Exception as e:
                error_str = f"Parsing error on page {page_num}: {e}"
                logger.error(error_str)
                page_log["error"] = error_str
        else:
            error_str = f"Table with id='mpTable' not found on page {page_num} (Response length: {len(mars_response.text)})"
            logger.warning(error_str)
            page_log["error"] = error_str

        diagnostics["page_logs"].append(page_log)

        if page_num < 5:
            time.sleep(random.uniform(1, 2))

    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True)
        diagnostics["total_parsed_rows"] = len(final_df)

        if "Work Order" in final_df.columns:
            final_df = final_df.drop_duplicates(subset=["Work Order"], ignore_index=True)
        else:
            final_df = final_df.drop_duplicates(ignore_index=True)

        diagnostics["final_rows_after_dedup"] = len(final_df)
        records = json.loads(final_df.to_json(orient="records"))

        return {
            "success": True,
            "data": records,
            "diagnostics": diagnostics
        }
    else:
        return {
            "success": False,
            "data": [],
            "diagnostics": diagnostics
        }