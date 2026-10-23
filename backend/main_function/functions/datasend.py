from minio import Minio
from dej_sdk import bucket

from main_function.functions.getdata import mongoURL
from pymongo import MongoClient
from pprint import pprint
import copy
from datetime import datetime

import json
import io
import sys
import re
import os

atscBucket = "atsclgerc"
oledBucket = "oledlgerc"
dvbBucket = "dvblgerc"
historyBucket = "historylgerc"
mpBucket = "mpcrossheck"

conn_en, err_en = bucket.connect(atscBucket)

def get_next_versioned_filename(file_name: str):
    """
    Creates the next versioned file name.

    Example:
    input:  report.pdf
    output: report_version_1.pdf, report_version_2.pdf, etc.
    """

    name, ext = os.path.splitext(file_name)

    try:
        objects = conn_en.list_objects(atscBucket, prefix=name)

        version_numbers = []

        for obj in objects:
            object_name = obj.object_name

            pattern = rf"^{re.escape(name)}_v(\d+){re.escape(ext)}$"
            match = re.match(pattern, object_name)

            if match:
                version_numbers.append(int(match.group(1)))

        next_version = max(version_numbers, default=0) + 1

        return f"{name}_v{next_version}{ext}"

    except Exception as e:
        st.error(f"Error checking file versions: {e}")
        return None

def upload_bytes_tos3(file_bytes: bytes, file_name: str):
    if file_bytes is None:
        st.error("No file data to upload.")
        return False

    try:
        versioned_file_name = get_next_versioned_filename(file_name)

        if versioned_file_name is None:
            return False

        file_stream = io.BytesIO(file_bytes)

        conn_en.put_object(
            atscBucket,
            versioned_file_name,
            file_stream,
            length=len(file_bytes)
        )

        st.success(f"{versioned_file_name} Successfully Uploaded.")
        return True

    except Exception as e:
        st.error(f"Error when uploading file: {e}")
        return False


def get_next_version_by_target(
    mongoURL: str,
    target_name: str,
    db_name: str = "resultreport",
    collection_name: str = "result27Y"
) -> float:
    client = MongoClient(mongoURL)

    try:
        db = client[db_name]
        collection = db[collection_name]

        latest_doc = collection.find_one(
            {"targetName": target_name},
            sort=[("version", -1)]
        )

        if not latest_doc:
            return 1.0

        latest_version = latest_doc.get("version", 0)

        try:
            latest_version = float(latest_version)
        except (TypeError, ValueError):
            latest_version = 0.0

        return round(latest_version + 1.0, 1)

    finally:
        client.close()

def send_to_pymongo(crosscheckResult):
    try:
        client = MongoClient(mongoURL)

        db = client["resultreport"]
        collection = db["result27Y"]

        result = collection.insert_one(crosscheckResult)

        print("Inserted ID:", result.inserted_id)

        print(
            "Total Documents:",
            collection.count_documents({})
        )

        latest = collection.find_one(
            {"_id": result.inserted_id}
        )

        #print("Retrieved Document:")
        #print(latest)

    except Exception as e:
        print(f"MongoDB Error: {e}")

    finally:
        client.close()

def send_to_pymongo_errorCode(crosscheckResult):
    try:
        client = MongoClient(mongoURL)

        db = client["resultreport"]
        collection = db["xreport"]

        result = collection.insert_one(crosscheckResult)

        print("Inserted ID:", result.inserted_id)

        print(
            "Total Documents:",
            collection.count_documents({})
        )

        latest = collection.find_one(
            {"_id": result.inserted_id}
        )

        #print("Retrieved Document:")
        #print(latest)

    except Exception as e:
        print(f"MongoDB Error: {e}")

    finally:
        client.close()

def send_to_pymongo_errorCode_percompare(crosscheckResult):
    try:
        client = MongoClient(mongoURL)

        db = client["resultreport"]
        collection = db["overReport"]

        result = collection.insert_one(crosscheckResult)

        print("Inserted ID:", result.inserted_id)

        print(
            "Total Documents:",
            collection.count_documents({})
        )

        latest = collection.find_one(
            {"_id": result.inserted_id}
        )

        #print("Retrieved Document:")
        #print(latest)

    except Exception as e:
        print(f"MongoDB Error: {e}")

    finally:
        client.close()

def read_from_pymongo(crosscheckResult):
    client = None

    try:
        client = MongoClient(mongoURL)

        db = client["resultreport"]
        collection = db["result27Y"]

        # Insert document
        result = collection.insert_one(crosscheckResult)

        print(f"Inserted ID: {result.inserted_id}")

        # Count documents in current collection
        count = collection.count_documents({})
        #print(f"result_result document count: {count}")

        # Show all collections and their document counts
        print("\n=== Database Summary ===")

        collections = db.list_collection_names()

        for coll_name in collections:
            coll_count = db[coll_name].count_documents({})
            print(f"{coll_name}: {coll_count} documents")

        # Show latest inserted document
        latest = collection.find_one(
            {"_id": result.inserted_id}
        )

        print("\n=== Latest Document ===")
        print(latest)

    except Exception as e:
        print(f"MongoDB Error: {e}")

    finally:
        if client is not None:
            client.close()

def read_from_pymongo():
    client = MongoClient(mongoURL)

    db = client["resultreport"]
    collection = db["result27Y"]

    latest_doc = collection.find_one(
        sort=[("_id", -1)]
    )

    print("=== Latest Document ===")
    pprint(latest_doc)

    client.close()


def send_to_pymongo_generic(crosscheckResult, collection_name: str):

    client = None

    try:
        client = MongoClient(mongoURL)

        db = client["resultreport"]
        collection = db[collection_name]

        # Create new document
        new_doc = copy.deepcopy(crosscheckResult)

        # Keep original document id for traceability
        new_doc["source_doc_id"] = str(
            crosscheckResult.get("_id", "")
        )

        # Submission timestamp
        new_doc["submitted_at"] = datetime.utcnow()

        # Remove original MongoDB _id
        new_doc.pop("_id", None)

        print(
            "Version being inserted:",
            new_doc.get("version")
        )

        result = collection.insert_one(new_doc)

        print(
            f"Inserted ID: {result.inserted_id}"
        )

        inserted_doc = collection.find_one(
            {"_id": result.inserted_id}
        )

        print("Retrieved Document:")
        print(inserted_doc)

        return str(result.inserted_id)

    except Exception as e:
        print(f"MongoDB Error: {e}")
        return None

    finally:
        if client:
            client.close()


def send_useract(event_data: dict, collection_name: str = "user_events"):
    client = None

    try:
        client = MongoClient(mongoURL)

        db = client["resultreport"]
        collection = db[collection_name]

        new_doc = copy.deepcopy(event_data)

        # Server-side timestamp
        new_doc["created_at"] = datetime.datetime.now(datetime.UTC)

        result = collection.insert_one(new_doc)

        return str(result.inserted_id)

    except Exception as e:
        print(f"MongoDB Error: {e}")
        return None

    finally:
        if client:
            client.close()