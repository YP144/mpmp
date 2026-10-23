import polars as pl
import requests
import connectorx

from services.check_sso import SSO_NPDM
from functions.getdata import userURL, getCoworkDB, getMasterData, memberURL
from functions.get_latestver import read_latest_version, read_table

def checkProfile(Username):
    userState = ""
    userRow = []
    queryALL = 'SELECT * FROM "public"."user_list"'

    readuser = pl.read_database_uri(
        query=queryALL,
        uri=memberURL,
        engine="connectorx")

    readuser = readuser.filter(
        pl.col("ID") == Username
    )

    if readuser is None or readuser.height == 0:
        userState = ""
        userRow = []
    else:
        userState = "User Exist"
        userRow = readuser

    return userState, userRow
        
def GetWorkingInfo():

        sso = SSO_NPDM()
        is_logged_in = sso.auto_login(ssolgenet_cookie, smsession_cookie)

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Authorization": sso.auth_bearer,
            "BusinessUnit": "HE",
            "Content-Type": "application/json",
            "Host": "npdm.lge.com",
            "Referer": "https://npdm.lge.com/my-desk/my-working-boms"
        }

        WorkingParams = {
            "searchVO":{
                "type":"MODEL",
                "states":"WORKING",
                "site":"GLZ.EAIC",
                "changeType":"Release"
            }
            }

        response = requests.put(
                "https://npdm.lge.com/api/workflow/common/my-working-boms",
                headers=headers,
                json=WorkingParams
            )

        all_outdata = []
        getState = []
        GetWorkingBOM = response.json()
        GetWorkingBOM = GetWorkingBOM["data"]

        for item in GetWorkingBOM:
            all_outdata.append(item["outData"])

        StateFrame = pl.DataFrame(GetWorkingBOM, infer_schema_length=None)
        WorkingFrame = pl.DataFrame(all_outdata, infer_schema_length=None)
        WorkingFrame = WorkingFrame.select([
            "pm_originName", "change_plantUnitDesc", "chassis", "wfit_states", "mr_checkouter", "change_states", "dueDate", "change_names"
        ])
        GetStateFrame = StateFrame.select([
            "states", "revision"
            ])

        FullWorkingInfo = pl.concat([WorkingFrame, StateFrame], how="horizontal")

        return WorkingFrame, GetWorkingBOM, FullWorkingInfo

def _find_members_in_text(text, member_list):
    if text is None:
        return ""

    if isinstance(member_list, str):
        member_list = [member_list]

    text_lower = str(text).lower()

    found_members = [
        member
        for member in member_list
        if member and str(member).lower() in text_lower
    ]

    return ", ".join(found_members)

def create_new_bom_table(uri, table_name):
    query = f'SELECT * FROM public."{table_name}"'
    df = pl.read_database_uri(query, uri)

    new_columns = [
        "structure check",
        "ben compare",
        "substitute chekck",
        "hw option",
        "tool option",
        "operation plan",
    ]

    df = df.with_columns([
        pl.lit("OK").alias(col)
        for col in new_columns
    ])

    return df

#Get BOM list for user from main Master Database
def getBOMlist(
    userName,
    result_column="found_members",
    name_col: str = "getName",
) -> pl.DataFrame:
    """
    Common function to generate model list by matching member names
    from cowork columns.
    """

    """search_columns = [
        "cha_coWorker1", "cha_coWorker2", "cha_coWorker3",
        "cha_coWorker4", "cha_coWorker5", "cha_coWorker6",
        "cha_coWorker7", "cha_coWorker8", "cha_coWorker9",
        "cha_coWorker10", "cha_coWorker11", "cha_coWorker12",
        "cha_names",
        "names"
    ]"""

    search_columns = ["Circuit PIC"]

    if isinstance(userName, str):
        member_list = [userName]
    elif isinstance(userName, list):
        member_list = userName
    else:
        member_list = list(userName)


    cowork_df = create_new_bom_table(getMasterData, "bom_management_rpa")

    cowork_df = cowork_df.rename({
        "Confirmation": "Result",
        "Part": "Substitute",
        "PCB Check": "HW option"
    })


    new_columns = [
        "ben compare",
        "operation plan",
    ]

    cowork_df = cowork_df.with_columns([
        pl.lit("OK").alias(col)
        for col in new_columns
    ])

    desired_order = [
        "Target Model",
        "Development Model",
        "Initial Model",
        "Result",
        "Subsidiary",
        "Circuit PIC",
        "Structure",
        "ben compare",
        "Substitute",
        "operation plan",
        "Tool Option",
        "HW Option",
        "Additional Remark",
        "BOM Release Date",
        "Final",
        "Year"
    ]

    cowork_df = cowork_df.select(desired_order)


    valid_search_columns = [
        col for col in search_columns
        if col in cowork_df.columns
    ]

    result_df = (
        cowork_df
        .with_columns(
            pl.concat_str(
                [
                    pl.col(col).cast(pl.Utf8).fill_null("")
                    for col in valid_search_columns
                ],
                separator=" "
            ).alias("all_names")
        )
        .with_columns(
            pl.col("all_names")
            .map_elements(
                lambda text: _find_members_in_text(text, member_list),
                return_dtype=pl.Utf8
            )
            .alias(result_column)
        )
        .filter(pl.col(result_column) != "")
    )

    return cowork_df, result_df

def user_model_list(main_model_list, user_email):
    
    filtered_model_list = main_model_list.filter(
        pl.col("model_circuit_pic").str.contains(rf"\b{user_email}")
    )


    return filtered_model_list








