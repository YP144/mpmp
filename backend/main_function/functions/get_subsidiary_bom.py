import json
import requests
import polars as pl

from main_function.services.check_sso import SSO_NPDM


def getPlantBOM(target_name, bearerAuth: str):
    target_name_original = target_name

    target_parts = target_name.split(".")
    model_name = target_parts[0]
    suffix_name = target_parts[1] if len(target_parts) > 1 else ""

    suffix_middle = suffix_name[1:-2] if len(suffix_name) > 3 else suffix_name
    display_suffix_name = "*" + suffix_middle + "**"

    empty_df = pl.DataFrame()

    empty_plant_dict = {
        "modelName": model_name,
        "targetName": target_name_original,
        "suffixName": display_suffix_name,
        "totalPlant": 0,
        "plantList": [],
        "plants": []
    }

    try:
        #sso = SSO_NPDM()
        #is_logged_in = sso.auto_login(ssolgenet_cookie, smsession_cookie)

        reqURL = "https://npdm.lge.com/api/engineering/item/model/find-model-list-paging"

        headers = {
            "Accept": "application/json",
            "Authorization": bearerAuth,
            "BusinessUnit": "HE",
            "Content-Type": "application/json",
            "Referer": "https://npdm.lge.com/search/model",
        }

        json_get_bom = {
            "searchInfo": {
                "creator": "",
                "revision": "",
                "states": "",
                "names": f"{model_name}*",
                "modelSuffix": "",
                "createDate": "",
                "creationDateOption": "",
                "creationFromDate": "",
                "creationPlantUnit": "",
                "productType": "",
                "creationToDate": "",
                "setPartNoExist": "",
                "setPartNo": "",
                "grossCbm": "",
                "grossDepth": "",
                "grossHeight": "",
                "grossWeight": "",
                "grossWidth": "",
                "boxPerQty": "",
                "brandName": "",
                "brandType": "",
                "chassis": "",
                "communicationModel": "",
                "container20SQty": "",
                "container40HQty": "",
                "container40SQty": "",
                "developmentGrade": "",
                "enabledFlag": "Y",
                "ospGrantedBy": "",
                "legacyProductModel": "",
                "legacyProductSuffix": "",
                "marketCode": "",
                "mmSeqId": "",
                "netWeight": "",
                "noNeedPvFlag": "",
                "packingType": "",
                "previousModelCode": "",
                "previousSuffixCode": "",
                "productGoodsTypeCode": "",
                "productLevel1Code": "",
                "productLevel2Code": "",
                "productLevel3Code": "",
                "productLevel4Code": "",
                "productTypeCode": "",
                "projectLeader": "",
                "salesModel": "",
                "salesModelFlag": "",
                "salesSuffix": "",
                "tentativeModelFlag": "",
                "toolName": "",
                "userItemType": "",
                "disabledType": "",
                "pr": "",
                "prStatus": "",
                "latestRev": "true",
                "hasBom": "false",
                "creatorSsoid": "",
                "divisions": "",
                "buyerName": "",
                "customerModel": "",
                "isMassExport": "false",
                "setModelRev": "",
                "setModelStates": "",
                "rfqModelFlag": "N",
                "isRelatedModel": "false",
                "model": "",
                "suffix": "",
                "creationDate": {
                    "comparison": "",
                    "fromDate": "",
                    "toDate": ""
                },
                "modifiedDate": {
                    "comparison": "",
                    "fromDate": "",
                    "toDate": ""
                },
                "releasedDate": {
                    "comparison": "",
                    "fromDate": "",
                    "toDate": ""
                },
                "erpBomIfDate": {
                    "comparison": "",
                    "fromDate": "",
                    "toDate": ""
                },
                "descriptions": "",
                "outData": {
                    "setPartNoFullName": "",
                    "creatorFullName": "",
                    "chkLatestOnly": "true",
                    "chkHasBom": "false"
                },
                "divisionSet": [
                    "GLZ"
                ],
                "creationPlantUnitSet": []
            },
            "pagingEntity": {
                "omfOrderByBuilder": {
                    "isEnd": "false",
                    "isOQL": "true",
                    "list": [],
                    "listType": []
                },
                "totalCount": 2,
                "targetRow": 1,
                "rowSize": 300,
                "currentPage": 1,
                "executeCount": "true"
            }
        }

        response = requests.put(
            reqURL,
            headers=headers,
            json=json_get_bom,
            timeout=60
        )

        if response is None:
            return empty_df, empty_plant_dict, model_name

        if response.status_code < 200 or response.status_code >= 300:
            return empty_df, empty_plant_dict, model_name

        try:
            response_json = response.json()
        except Exception:
            return empty_df, empty_plant_dict, model_name

        if not response_json:
            return empty_df, empty_plant_dict, model_name

        bom_list = response_json.get("data", {}).get("list", [])

        if not bom_list:
            return empty_df, empty_plant_dict, model_name

        if not isinstance(bom_list, list):
            return empty_df, empty_plant_dict, model_name

        listFrame = pl.DataFrame(bom_list, infer_schema_length=None)

        if listFrame.is_empty():
            return empty_df, empty_plant_dict, model_name

        if "outData" in listFrame.columns:
            resultFrame = listFrame.unnest("outData")
        else:
            resultFrame = listFrame

        required_columns = [
            "obid",
            "created",
            "modified",
            "pm_creationPlantUnit",
            "this_creatorName",
            "mr_titles",
            "creationPlantUnitDesc",
            "states",
            "revision",
            "revCreator",
            "changeName"
        ]

        existing_columns = [
            col for col in required_columns
            if col in resultFrame.columns
        ]

        if not existing_columns:
            return empty_df, empty_plant_dict, model_name

        resultFrame = resultFrame.select(existing_columns)

        if "mr_titles" not in resultFrame.columns:
            return empty_df, empty_plant_dict, model_name

        resultFrame = resultFrame.filter(
            pl.col("mr_titles")
            .str.contains(
                rf"{model_name}.*{suffix_middle}.*"
            )
            .fill_null(False)
        )

        if resultFrame.is_empty():
            return empty_df, empty_plant_dict, model_name

        getPlant_list = (
            resultFrame
            .select(["creationPlantUnitDesc"])
            .unique(subset="creationPlantUnitDesc")
        )

        totalPlant = getPlant_list.height

        dictsResult = resultFrame.to_dicts()
        dictsPlants = getPlant_list.to_dicts()

        plantDicts = {
            "modelName": model_name,
            "targetName": target_name_original,
            "suffixName": display_suffix_name,
            "totalPlant": totalPlant,
            "plantList": dictsPlants,
            "plants": dictsResult
        }

        return resultFrame, plantDicts, model_name

    except Exception as e:
        print("getPlantBOM error:", e)
        return empty_df, empty_plant_dict, model_name