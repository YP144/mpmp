import html
from urllib.parse import parse_qs, unquote
import requests


class SSO_MARS:
    def __init__(self, username: str = "", password: str = ""):
        self.baseUrl = "https://mp-schedule-monitoring-be-fe.apps.hedej.lge.com/"
        self.session = requests.Session()

        self.userId = ""
        self.userIc = ""
        self.auth_bearer = ""

    def auto_login(self, ssolgenet_cookie: str = "", smsession_cookie: str = "") -> bool:
        try:
            if not ssolgenet_cookie or not smsession_cookie:
                raise ValueError("SSO cookies not found. Please pass valid ssolgenet_cookie and smsession_cookie.")

            # 1. Parse user info from ssolgenet_cookie
            decoded = html.unescape(ssolgenet_cookie)
            parsed = parse_qs(decoded)

            self.userId = parsed.get("empno", [None])[0]
            self.userIc = parsed.get("ssoid", [None])[0]

            # 2. Inject cookies to requests session
            self.session.cookies["ssolgenet"] = ssolgenet_cookie
            self.session.cookies["SMSESSION"] = smsession_cookie

            # 3. Get authentication bearer token
            if not self.ssoLogin_getAuthBear():
                raise ValueError("Session expired or authentication failed.")

            return True

        except Exception as e:
            print("Auto login failed:", e)
            return False

    def check_sso(self, ssolgenet_cookie: str = "", smsession_cookie: str = "") -> bool:
        """
        Alias wrapper around auto_login for SSO verification.
        """
        return self.auto_login(ssolgenet_cookie=ssolgenet_cookie, smsession_cookie=smsession_cookie)

    def ssoLogin_getAuthBear(self) -> bool:
        getAuthHeader = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Host": "npdm.lge.com",
            "Origin": "https://npdm.lge.com",
            "Referer": "https://npdm.lge.com/ssoLogin"
        }
        getAuthPayload = {"omfAuthenticationVO": {"expiredHoursAfter": 18}}

        getAuthBear = self.session.post(
            "https://npdm.lge.com/api/foundation/user/login/sso?ssoRedirect=none",
            headers=getAuthHeader,
            json=getAuthPayload,
            timeout=15
        )

        content_type = getAuthBear.headers.get("Content-Type", "")
        if getAuthBear.status_code == 200 or "application/json" in content_type:
            json_data = getAuthBear.json()
            self.auth_bearer = json_data.get("data", {}).get("token", "")
            return bool(self.auth_bearer)
        else:
            print(f"MARS/NPDM Server not reached. Status Code: {getAuthBear.status_code}")
            return False


def center_login(ssolgenet_cookie: str = "", smsession_cookie: str = ""):
    sso = SSO_MARS()
    get_login = sso.check_sso(ssolgenet_cookie=ssolgenet_cookie, smsession_cookie=smsession_cookie)
    get_bearer = sso.auth_bearer

    return get_login, get_bearer


if __name__ == "__main__":
    test_ssolgenet = "empno=12345&ssoid=testuser"
    test_smsession = "dummy_smsession_value"

    sso = SSO_MARS()
    is_logged_in = sso.check_sso(ssolgenet_cookie=test_ssolgenet, smsession_cookie=test_smsession)

    if is_logged_in:
        print("Login Success!")
        print("User ID:", sso.userId)
        print("User IC:", sso.userIc)
        print("Auth Bearer Token:", sso.auth_bearer[:30] + "...")
    else:
        print("Login Failed.")



class SSO_NPDM:
    def __init__(self, username: str = "", password: str = ""):
        self.baseUrl = "https://sso.lge.com"
        self.session = requests.Session()

        self.userId = ""
        self.userIc = ""
        self.auth_bearer = ""

    def auto_login(self, ssolgenet_cookie: str = "", smsession_cookie: str = "") -> bool:
        try:
            if not ssolgenet_cookie or not smsession_cookie:
                raise ValueError("SSO cookies not found. Please pass valid ssolgenet_cookie and smsession_cookie.")

            # 1. Parse user info from ssolgenet_cookie
            decoded = html.unescape(ssolgenet_cookie)
            parsed = parse_qs(decoded)

            self.userId = parsed.get("empno", [None])[0]
            self.userIc = parsed.get("ssoid", [None])[0]

            # 2. Inject cookies to requests session
            self.session.cookies["ssolgenet"] = ssolgenet_cookie
            self.session.cookies["SMSESSION"] = smsession_cookie

            # 3. Get NPDM bearer token
            if not self.ssoLogin_getAuthBear():
                raise ValueError("Session expired or NPDM authentication failed.")
            
            return True

        except Exception as e:
            print("Auto login failed:", e)
            return False

    def check_sso(self, ssolgenet_cookie: str = "", smsession_cookie: str = "") -> bool:
        """
        Alias wrapper around auto_login for SSO verification.
        """
        return self.auto_login(ssolgenet_cookie=ssolgenet_cookie, smsession_cookie=smsession_cookie)

    def ssoLogin_getAuthBear(self) -> bool:
        getAuthHeader = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Host": "npdm.lge.com",
            "Origin": "https://npdm.lge.com",
            "Referer": "https://npdm.lge.com/ssoLogin"
        }
        getAuthPayload = {"omfAuthenticationVO": {"expiredHoursAfter": 18}}
        
        getAuthBear = self.session.post(
            "https://npdm.lge.com/api/foundation/user/login/sso?ssoRedirect=none",
            headers=getAuthHeader,
            json=getAuthPayload,
            timeout=15
        )

        content_type = getAuthBear.headers.get("Content-Type", "")
        if getAuthBear.status_code == 200 or "application/json" in content_type:
            json_data = getAuthBear.json()
            self.auth_bearer = json_data.get("data", {}).get("token", "")
            return bool(self.auth_bearer)
        else:
            print(f"NPDM Server not reached. Status Code: {getAuthBear.status_code}")
            return False


def center_login(ssolgenet_cookie: str = "", smsession_cookie: str = ""):
    sso = SSO_NPDM()
    get_login = sso.check_sso(ssolgenet_cookie=ssolgenet_cookie, smsession_cookie=smsession_cookie)
    get_bearer = sso.auth_bearer

    return get_login, get_bearer


NPDM_BASE_URL = "https://npdm.lge.com"
NPDM_SEARCH_PART_URL = f"{NPDM_BASE_URL}/api/engineering/parts/search-part"


class NpdmClient:
    def __init__(self, auth_bearer: str, session: requests.Session = None):
        self.session = session or requests.Session()
        self.headers = {
            "Accept": "application/json",
            "Authorization": auth_bearer,
            "BusinessUnit": "HE",
            "Content-Type": "application/json",
            "Referer": "https://npdm.lge.com/search/bom",
        }

    def _build_search_payload(self, model_name: str, plant_unit: str) -> dict:
        return {
            "searchVO": {
                "partSearchKind": 3,
                "lifeCycleSetNotIn": ["MDMS Interfaced Model Policy"],
                "latestOnly": True,
                "plantUnitSet": [plant_unit],
                "namesPattern": f"{model_name}*",
            },
            "pagingEntity": {
                "totalCount": 0,
                "targetRow": 1,
                "rowSize": 50,
                "currentPage": 1,
            },
        }

    def _build_ebom_payload(self, obid: str, plant_unit: str) -> dict:
        return {
            "bomViewInputVO": {
                "inputParentPartObid": obid,
                "plantUnitCode": plant_unit,
                "wantedExplosionLevel": 20,
                "withDrawingOrChange": "Only BOM",
                "includeEBomMR": True,
                "includeSubstitute": True,
                "splitDesignator": False,
                "uniqueStr": "00001",
                "backWard": False,
                "changeName": "",
                "workingApply": False,
            }
        }

    def search_part_obid(self, model_name: str, plant_unit: str) -> str:
        payload = self._build_search_payload(model_name, plant_unit)
        response = self.session.put(
            NPDM_SEARCH_PART_URL,
            headers=self.headers,
            json=payload,
            timeout=10,
        )
        response.raise_for_status()

        ob_list = response.json().get("data", {}).get("list", [])

        if not ob_list:
            raise ValueError(f"OBID not found for model: {model_name}")

        return ob_list[0]["obid"]

    def get_ebom(self, obid: str, plant_unit: str) -> dict:
        payload = self._build_ebom_payload(obid, plant_unit)

        response = self.session.put(
            f"{NPDM_BASE_URL}/api/engineering/part/{obid}/ebom",
            headers=self.headers,
            json=payload,
            timeout=10,
        )
        response.raise_for_status()

        return response.json()

    def get_model_ebom(self, model_name: str, plant_unit: str) -> dict:
        obid = self.search_part_obid(model_name, plant_unit)
        return self.get_ebom(obid, plant_unit)


if __name__ == "__main__":
    test_ssolgenet = "empno=12345&ssoid=testuser"
    test_smsession = "dummy_smsession_value"

    sso = SSO_NPDM()
    is_logged_in = sso.check_sso(ssolgenet_cookie=test_ssolgenet, smsession_cookie=test_smsession)
    
    if is_logged_in:
        print("Login Success!")
        print("User ID:", sso.userId)
        print("User IC:", sso.userIc)
        print("Auth Bearer Token:", sso.auth_bearer[:30] + "...")

        client = NpdmClient(auth_bearer=sso.auth_bearer, session=sso.session)
    else:
        print("Login Failed.")