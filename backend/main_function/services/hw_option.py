import json
import requests
import os
from pathlib import Path

class HW_Option:
    def __init__(self):
        self.PCB_development = ""
        self.PCB_initial = ""
        self.PCB_target = ""

    def HW_Optioncheck(self):
        JSON_DIR = Path(__file__).resolve().parent.parent / "json"

        # --- Anywhere in your functions ---

        with open(JSON_DIR / "2_development_part.json", "r", encoding="utf-8") as f:
            hw_development = json.load(f)

        with open(JSON_DIR / "2_initial_part.json", "r", encoding="utf-8") as f:
            hw_initial = json.load(f)

        with open(JSON_DIR / "2_target_part.json", "r", encoding="utf-8") as f:
            hw_target = json.load(f)
        
        filtered_PCB_dev = [
            {
                "Category": item.get("Category", ""),
                "Part No": item.get("Part No", ""),
            }
            for item in hw_development
            if item.get("Category") in ("PCB", "EBR Main")
        ]

        filtered_PCB_init = [
            {
                "Category": item.get("Category", ""),
                "Part No": item.get("Part No", ""),
            }
            for item in hw_development
            if item.get("Category") in ("PCB", "EBR Main")
        ]

        filtered_PCB_target = [
            {
                "Category": item.get("Category", ""),
                "Part No": item.get("Part No", ""),
            }
            for item in hw_development
            if item.get("Category") in ("PCB", "EBR Main")
        ]

        self.PCB_development = filtered_PCB_dev[0]["Part No"]
        self.PCB_initial = filtered_PCB_init[0]["Part No"]
        self.PCB_target = filtered_PCB_target[0]["Part No"]

        EBR_development = filtered_PCB_dev[1]["Part No"]
        EBR_initial = filtered_PCB_init[1]["Part No"]
        EBR_target = filtered_PCB_target[1]["Part No"]

    # ##Get OBID
    #         headers = {
    #         "Accept": "application/json",
    #         "Authorization": "eyJyZWdEYXRlIjoxNzc1MDQ0ODU0MDczLCJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0ZWFtY2VudGVyVXNlcklkIjoiIiwicm9sZSI6W3siYXV0aG9yaXR5IjoiUk9MRV9HZW5lcmFsIFVzZXIgUm9sZSJ9LHsiYXV0aG9yaXR5IjoiUk9MRV9IYXJkd2FyZShQQ0IpIEVuZ2luZWVyIFJvbGUifSx7ImF1dGhvcml0eSI6IlJPTEVfVVNFUiJ9XSwiaWQiOiJJQzAwMDk2OCIsImV4cCI6MTc3NTEwOTY1NH0.Y-WNswljt--qV0aNQvX9qZMF-d3kXe-bSNLwruAzepY",
    #         "BusinessUnit": "HE",
    #         "Content-Type": "application/json",
    #         "Referer": "https://npdm.lge.com/search/bom"
    #         }
    #         # getObIdPayload = {
    #         # "searchVO":{
    #         #     "revisionPattern":"",
    #         #     "latestOnly":True,
    #         #     "hasEBom":False,
    #         #     "callingProgram":"Regular",
    #         #     "includeTempPart":False,
    #         #     "lifeCycleSet":["EC Part Policy","Development Part Policy"],
    #         #     "created":{"toDate":"","comparison":"GT"},
    #         #     "uncleansedPartOpt":"Include",
    #         #     "statesSet":[],
    #         #     "divisionUnitSet":["GLZ"],
    #         #     "plantUnitSet":["GLZ.EKHQ"],
    #         #     "partStatusSetIn":[],
    #         #     "namesPattern":f"{PCB_development}",
    #         #     "descriptions":"",
    #         #     "advanceSelectOptionSet":["Maker"]},
    #         # "pagingEntity":{
    #         #     "totalCount":0,
    #         #     "targetRow":1,
    #         #     "rowSize":300,
    #         #     "currentPage":1
    #         #     }
    #         # }
    #         getObIdPayload = {
    #             "searchVO": {
    #                 "partSearchKind": 3,
    #                 "lifeCycleSetNotIn": ["MDMS Interfaced Model Policy"],
    #                 "latestOnly": True,
    #                 "plantUnitSet": ["GLZ.EKHQ"],
    #                 "namesPattern": f"{PCB_development}*"
    #                 },
    #             "pagingEntity": {
    #                 "totalCount": 0,
    #                 "targetRow": 1,
    #                 "rowSize": 50,
    #                 "currentPage": 1
    #                 }
    #             }
    #         getObIdResponse = requests.put(
    #         "https://npdm.lge.com/api/engineering/parts/search-part",
    #         headers=headers,
    #         json=getObIdPayload,
    #         timeout=10
    #         )
    #         getObIdResponse.raise_for_status()
    #         ob_list = getObIdResponse.json().get("data", {}).get("list", [])
    #         if not ob_list:
    #             raise ValueError("OBID not found for target model")
    #         ObId = ob_list[0]["obid"]

    #         print("OBID:", ObId)
if __name__ == "__main__":
    HW_Option().HW_Optioncheck()
