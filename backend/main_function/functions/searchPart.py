import polars as pl
import requests
import json

from services.check_sso import SSO_NPDM

sso = SSO_NPDM()
is_logged_in = sso.auto_login()
getBearer = sso.auth_bearer


def getCreatePart(getNameSSO, getEmail, getId, partKey):

    getName = f"{getNameSSO}({getEmail})"

    searchPartParams = {
        "searchVO":{
            "revisionPattern":"",
            "latestOnly":"true",
            "hasEBom":"false",
            "creator":getId,
            "callingProgram":"Regular",
            "includeTempPart":"false",
            "lifeCycleSet":[
                "EC Part Policy",
                "Development Part Policy"
            ],
            "created":{
                "toDate":"",
                "comparison":"GT"
            },
            "uncleansedPartOpt":"Include",
            "statesSet":[
                
            ],
            "divisionUnitSet":[
                "GLZ"
            ],
            "plantUnitSet":[
                "GLZ.EKHQ"
            ],
            "partStatusSetIn":[
                
            ],
            "outData":{
                "creatorName":getName
            },
            "namesPattern":f"{partKey}**",
            "descriptions":"",
            "advanceSelectOptionSet":[
                "Maker"
            ]
        },
        "pagingEntity":{
            "totalCount":0,
            "targetRow":1,
            "rowSize":100000,
            "currentPage":1
        }
    }

    searchPart_headers = {
            "Accept": "application/json, text/plain, */*",
            "Authorization": sso.auth_bearer,
            "BusinessUnit": "HE",
            "Content-Type": "application/json",
            "Host": "npdm.lge.com",
            "Referer": "https://npdm.lge.com/search/part"
        }

    searhParturl = "https://npdm.lge.com/api/engineering/parts/search-part"

    searchPart_response = requests.put(searhParturl, headers=searchPart_headers, json=searchPartParams)
    searchPart_status = searchPart_response.status_code
    getsearchPart = searchPart_response.json()

    get_list = getsearchPart.get("data", {}).get("list", [])

    getDatalist = []
    getRevlist = []

    for item in get_list:
        out_data = item.get("outData", [])
        #data_data = item.get("list", [])
        getDatalist.append(out_data)
        #getRevlist.append(data_data)

    getpartFrame = pl.DataFrame(getDatalist)
    getrevFrame = pl.DataFrame(get_list)

    getSearchFrame = pl.concat([getpartFrame, getrevFrame], how="horizontal")

    columns = ["titles", "states", "revision", "mr_creationStatusName"]

    if getSearchFrame.is_empty():
        getpartFrame = pl.DataFrame({col: [] for col in columns})
    else:
        getpartFrame = getSearchFrame.select(columns)

    getHeight = getpartFrame.height
    
    return searchPart_status, getsearchPart, getpartFrame, getHeight


def get_part_profile(get_part_list, part_ref: str):

    if isinstance(get_part_list, dict):
        get_part_list = get_part_list.get("data", [])

    if not isinstance(get_part_list, list):
        return []

    result = []

    for item in get_part_list:
        if not isinstance(item, dict):
            continue

        if str(item.get("childNameDisplay", "")).startswith(part_ref):
            result.append({
                "childNameDisplay": item.get("childNameDisplay"),
                "bomQuantity": item.get("bomQuantity"),
                "supplyType": item.get("supplyType"),
                "dataType": item.get("dataType"),
                "bomExpandPath": item.get("bomExpandPath"),
                "className": item.get("className"),
                "jobExplanation": item.get("jobExplanation")
            })

    return result



