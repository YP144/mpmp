import pymongo
import polars as pl
import pandas as pd
from pymongo import MongoClient
from fastapi import HTTPException
from utils.link import mongoURL

# Initialize the client
client = MongoClient(mongoURL)
db = client["resultreport"]
collection = db["result27Y"]

def fetch_latest_mongo_result_profile(target_model: str) -> dict: 
    try:
        # 1. Print the exact target model string received from main.py
        print(f"--- DEBUG: Received target_model: '{target_model}' ---")
        
        # 2. Define and print the exact query dictionary being sent to MongoDB
        query = {"targetName": target_model}
        print(f"--- DEBUG: Querying MongoDB for: {query} ---")

        # Search for targetName using the string passed from main.py
        latest_doc = collection.find_one(
            query, 
            sort=[("version", -1), ("_id", -1)]
        )

        # 3. Print the raw document retrieved from the database
        print(f"--- DEBUG: Retrieved latest_doc: {latest_doc} ---")
        print(f"--- DEBUG: Type of latest_doc: {type(latest_doc)} ---")

        if not latest_doc:
            raise HTTPException(status_code=404, detail="Model profile not found.")

        # Get the list
        profile_data_list = latest_doc.get('ModelProfile', {}).get('profileData')
        
        if not profile_data_list:
            raise HTTPException(status_code=404, detail="Profile data is missing in the document.")

        # Return the first item in the list (the actual dictionary)
        return profile_data_list[0]

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching data from MongoDB: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")

def fetch_latest_mongo_result(
    target_model: str,
    dev_model: str = "",
    init_model: str = "",
) -> dict: 
    try:
        print(f"--- DEBUG: Received target_model: '{target_model}' ---")
        print(f"--- DEBUG: Received dev_model: '{dev_model}' ---")
        print(f"--- DEBUG: Received init_model: '{init_model}' ---")

        query = {"targetName": target_model}

        if dev_model:
            query["devName"] = dev_model

        if init_model:
            query["initName"] = init_model

        print(f"--- DEBUG: Querying MongoDB for: {query} ---")

        latest_doc = collection.find_one(
            query, 
            sort=[("version", -1), ("_id", -1)]
        )

        print(f"--- DEBUG: Retrieved latest_doc: {latest_doc} ---")
        print(f"--- DEBUG: Type of latest_doc: {type(latest_doc)} ---")

        # Cleaned up duplicated check
        if not latest_doc:
            raise HTTPException(status_code=404, detail="Result document not found.")

        return latest_doc

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching data from MongoDB: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
