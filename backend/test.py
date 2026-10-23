import requests
from services.check_sso import SSO_NPDM, center_login


def get_bom_api(ssolgenet, smsession):

    sso = SSO_NPDM()
    sso.check_sso(ssolgenet_cookie=ssolgenet, smsession_cookie=smsession)

    npdm_url = "https://npdm.lge.com/api/workflow/common/my-working-boms"

    npdm_header = {
        "Accept" : "application/json, text/plain, */*",
        "Authorization" : sso.auth_bearer,
        "Referer" : "https://npdm.lge.com/my-desk/my-working-boms"
    }

    npdm_params = {
    "searchVO": {
        "type": "MODEL",
        "states": "WORKING",
        "site": "GLZ.EAIC",
        "changeType": "Release"
    }
    }

    response = requests.put(
        npdm_url,
        headers=npdm_header,
        json=npdm_params
    )

    print(response.status_code)
    print(response.json())

