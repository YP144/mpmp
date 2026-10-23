import streamlit as st
import requests
import polars as pl

from services.check_sso import SSO_NPDM, NpdmClient
from functions.conditioning import zerobom_conditioning

from compFunctions.compareHWsingle import compare_hw_multi_process
from compFunctions.compareHWmulti import compare_hw_single_process

#sso = SSO_NPDM()
#sso.auto_login()

#Get EBR and EAX Info
def get_eax_and_ebr_obid(complete_bom: pl.DataFrame):

    # Get PCB Part Only
    get_eax = complete_bom.filter(
        pl.col("part_number").str.contains(r"(?i)^EAX")
        & pl.col("part_descriptions").str.contains(r"(?i)PCB")
    )

    # Get Main EBR Part
    get_ebr = complete_bom.filter(
        pl.col("part_number").str.contains(r"(?i)^EBR")
        & pl.col("part_TechnicalSpec").str.contains(r"(?i)m\.i")
    )

    # Check unique part numbers
    unique_eax_pn = (
        get_eax.get_column("part_number").unique().to_list()
        if not get_eax.is_empty()
        else []
    ) 

    unique_ebr_pn = (
        get_ebr.get_column("part_number").unique().to_list()
        if not get_ebr.is_empty()
        else []
    )

    # Validate that candidates exist
    if not unique_eax_pn:
        st.error("No EAX PCB part found in the BOM.")
        st.stop()

    if not unique_ebr_pn:
        st.error("No matching EBR part found in the BOM.")
        st.stop()

    # Select the first unique part number
    selected_eax_pn = unique_eax_pn[0]
    selected_ebr_pn = unique_ebr_pn[0]

    # Get the first matching row for each selected part number
    eax_row = get_eax.filter(
        pl.col("part_number") == selected_eax_pn
    ).row(0, named=True)

    ebr_row = get_ebr.filter(
        pl.col("part_number") == selected_ebr_pn
    ).row(0, named=True)

    # Build selected result
    get_eax_ebr = {
        "ebr_pn": ebr_row["part_number"],
        "ebr_techSpec": ebr_row["part_TechnicalSpec"],
        "ebr_obid": ebr_row["pp_obid"],
        "eax_pn": eax_row["part_number"],
        "eax_techSpec": eax_row["part_TechnicalSpec"],
        "eax_obid": eax_row["pp_obid"],
    }

    # Add notifications when multiple unique part numbers exist
    notifications = []

    if len(unique_eax_pn) > 1:
        notifications.append(
            f"Multiple EAX PCB part numbers found ({len(unique_eax_pn)}): "
            f"{unique_eax_pn}. Selected: {selected_eax_pn}"
        )

    if len(unique_ebr_pn) > 1:
        notifications.append(
            f"Multiple EBR part numbers found ({len(unique_ebr_pn)}): "
            f"{unique_ebr_pn}. Selected: {selected_ebr_pn}"
        )

    get_eax_ebr["notifications"] = notifications

    return get_eax_ebr, get_ebr

#Get single option
def get_single_option_ebr(eax_obid: str, zuken_obid: str, option_obid: str, bearerAuth: str):
  single_option_params = {
    "zukenDocumentObid": zuken_obid,
    "currentOptionGroupObid": option_obid
  }

  single_option_headers = {
      "Accept": "application/json, text/plain, */*",
      "Authorization": bearerAuth,
      "Referer": f"https://npdm.lge.com/get-information?obid={eax_obid}&type=independent"
  }

  single_option_url = "https://npdm.lge.com/api/engineering/cad/ecad/drawing/zukenpartlist/updatecircuitbom/getmultioptioncompareresultofsingle"

  response = requests.put(
              single_option_url,
              headers=single_option_headers,
              json=single_option_params,
              timeout=60
          )

  #st.text(f"Request Status: {response.status_code}")

  get_response_data = response.json()
  get_response_data = get_response_data['data']

  return get_response_data

#Get multi option
def get_multi_option_ebr(eax_obid: str, zuken_obid: str, option_obid: str, bearerAuth: str):
  single_option_params = {
    "zukenDocumentObid": zuken_obid,
    "currentOptionGroupObid": option_obid
  }

  single_option_headers = {
      "Accept": "application/json, text/plain, */*",
      "Authorization": bearerAuth,
      "Referer": f"https://npdm.lge.com/get-information?obid={eax_obid}&type=independent"
  }

  single_option_url = "https://npdm.lge.com/api/engineering/cad/ecad/drawing/zukenpartlist/updatecircuitbom/getmultioptioncompareresultofmulti"

  response = requests.put(
              single_option_url,
              headers=single_option_headers,
              json=single_option_params,
              timeout=60
          )

  #st.text(f"Request Status: {response.status_code}")

  get_response_data = response.json()
  get_response_data = get_response_data['data']

  return get_response_data

#1st Get Material => Input 
def get_currentoptiongroup_obid(ebr_obid: str, eax_obid: str, bearerAuth: str):

  currentoptionGroup_headers = {
      "Accept": "application/json, text/plain, */*",
      "Authorization": bearerAuth,
      "Referer": f"https://npdm.lge.com/get-information?obid={eax_obid}&type=independent" #EAX input
  }
 
  curentoptiongroup_url = f"https://npdm.lge.com/api/engineering/cad/ecad/drawing/zukenpartlist/updatecircuitbom/getgenericpartvo/{ebr_obid}" #EBR obid here

  response = requests.get(
              curentoptiongroup_url,
              headers=currentoptionGroup_headers,
              timeout=60
          )
  get_json = response.json()

  get_currentOptionObid = get_json['data']['outData']['currentOptionGroupObid']
  
  return get_currentOptionObid

def get_zukenDocumentObid(ebr_obid: str, eax_obid: str, bearerAuth: str):
  zukenDocumentObid_headers = {
      "Accept": "application/json, text/plain, */*",
      "Authorization": bearerAuth,
      "Referer": f"https://npdm.lge.com/get-information?obid={eax_obid}&type=independent"
  }

  zukenDocumentObid_url = f"https://npdm.lge.com/api/engineering/cad/ecad/drawing/zukenpartlist/updatecircuitbom/getzukendocumentvoofpreviousoptions/{ebr_obid}"

  response = requests.get(
              zukenDocumentObid_url,
              headers=zukenDocumentObid_headers,
              timeout=60
          )
  print(f"get zuken status: {response.status_code}")
  get_json = response.json()

  get_zukenDocumentObid = get_json['data']['obid']
  #get_zukenDocumentObid = None

  return get_zukenDocumentObid, get_json

def request_model_hw_multioption_info(complete_bom: pl.DataFrame, bearerAuth):

  get_eax_ebr, get_ebr_df = get_eax_and_ebr_obid(complete_bom=complete_bom)
  get_ebr_obid = get_eax_ebr['ebr_obid']
  get_eax_obid = get_eax_ebr['eax_obid']

  #Create a notification if the Current Option Group is not Found
  currentoptionGroup_obid = get_currentoptiongroup_obid(ebr_obid=get_ebr_obid, eax_obid=get_eax_obid, bearerAuth=bearerAuth)
  #Create a notification if the Zuken Document is not Found
  zukenDocumentObid, zuken_json = get_zukenDocumentObid(ebr_obid=get_ebr_obid, eax_obid=get_eax_obid, bearerAuth=bearerAuth)

  get_response_multi = get_multi_option_ebr(
    eax_obid=get_eax_obid,
    zuken_obid=zukenDocumentObid,
    option_obid=currentoptionGroup_obid,
    bearerAuth=bearerAuth
  )

  return get_response_multi

def request_model_hw_singleoption_info(complete_bom: pl.DataFrame, bearerAuth):

  get_eax_ebr, get_ebr_df = get_eax_and_ebr_obid(complete_bom=complete_bom)
  get_ebr_obid = get_eax_ebr['ebr_obid']
  get_eax_obid = get_eax_ebr['eax_obid']

  #Create a notification if the Current Option Group is not Found
  currentoptionGroup_obid = get_currentoptiongroup_obid(ebr_obid=get_ebr_obid, eax_obid=get_eax_obid, bearerAuth=bearerAuth)
  #Create a notification if the Zuken Document is not Found
  zukenDocumentObid, zuken_json = get_zukenDocumentObid(ebr_obid=get_ebr_obid, eax_obid=get_eax_obid, bearerAuth=bearerAuth)

  get_response_single = get_single_option_ebr(
    eax_obid=get_eax_obid,
    zuken_obid=zukenDocumentObid,
    option_obid=currentoptionGroup_obid,
    bearerAuth=bearerAuth
  )

  return get_response_single

def hw_multi_option_info(target, dev, init, bearerAuth):
    
    #Get Multi Option for HW Option
    get_multi_target = request_model_hw_multioption_info(complete_bom=target, bearerAuth=bearerAuth)
    get_multi_development = request_model_hw_multioption_info(complete_bom=dev, bearerAuth=bearerAuth)
    get_multi_init = request_model_hw_multioption_info(complete_bom=init, bearerAuth=bearerAuth)

    return get_multi_target, get_multi_development, get_multi_init

def hw_single_option_info(target, dev, init, bearerAuth):
    
    #Get Single Option for HW Option
    get_single_target = request_model_hw_singleoption_info(complete_bom=target, bearerAuth=bearerAuth)
    get_single_development = request_model_hw_singleoption_info(complete_bom=dev, bearerAuth=bearerAuth)
    get_single_init = request_model_hw_singleoption_info(complete_bom=init, bearerAuth=bearerAuth)


    return get_single_target, get_single_development, get_single_init


