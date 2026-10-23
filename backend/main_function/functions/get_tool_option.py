import re
import json
import streamlit as st
from sqlalchemy import create_engine, text

from functions.conditioning import zerobom_conditioning
from functions.TOMS.toms_req import get_emulator_json, get_machine_json, TOMS

from functions.JIRA.jira_def import get_jira_tool_option_df 
from functions.JIRA.jira_req import get_jira_power_cons


def get_area_code(suffix_country: str):
    suffix_country = suffix_country.upper()

    db_uri = "postgresql://beforebom27-user:XS1ppHW7JFAaRRuzo7ECYhpz8thxHNcsFelR9YRyqqbvTMjftLDXKQM0OaIvnMJo@beforebom27.postgres.svc:5432/toolOption"
    table_name = "areaCode"
    # 1. Create the database engine
    engine = create_engine(db_uri)

    # 2. Write the query using parameterized inputs to prevent SQL injection.
    # Note: Double quotes are used around the table and column name to handle parentheses safely.
    query = text(f'SELECT * FROM "{table_name}" WHERE "Suffix(2~3)" = :suffix')

    # 3. Execute the query and fetch the result
    with engine.connect() as connection:
        result = connection.execute(query, {"suffix": suffix_country}).fetchone()
        
        if result:
            # Convert the SQLAlchemy Row object into a dictionary for easy reading
            return dict(result._mapping)
        else:
            return None

#tool option _ operation
def get_tool_option_url():

    region_key = r"postgres://beforebom27-user:XS1ppHW7JFAaRRuzo7ECYhpz8thxHNcsFelR9YRyqqbvTMjftLDXKQM0OaIvnMJo@beforebom27.postgres.svc:5432/toolOption"

    return region_key

def get_tool_op(suffix_country: str):
    get_region_op = get_tool_option_url()

    tool_op = read_table(
        db_uri=get_region_op,
        table_name="key_RegionBase"
    )
    tool_op = tool_op.with_columns(
        pl.col("Suffix").str.to_lowercase()
    )
 
    tool_op = tool_op.filter(
        pl.col("Suffix").str.contains(model_profie.SuffixCountry)
    )

    # Convert to a list of dictionaries (JSON query-friendly format)
    get_key_suffix_dict = tool_op.to_dicts()

    # Define parent keys (case-insensitive matching)
    parent_keys_lower = {"suffix", "region/country", "index", "spk"}

    # Transform the data structure
    structured_query_data = []
    for row in get_key_suffix_dict:
        parent_dict = {}
        child_dict = {}
        
        for k, v in row.items():
            if k.lower() in parent_keys_lower:
                parent_dict[k] = v
            else:
                child_dict[k] = v
                
        # Nest the remaining fields into the child query
        parent_dict["tool_region"] = child_dict
        structured_query_data.append(parent_dict)

    return structured_query_data
    


def tool_option_js_query(JobExpl_ToolOption):

    parsed_items = JobExpl_ToolOption.split('/')
    data = {}

    # =============== 1. BOARD OPTION & HEADER EXTRACTION (parsed_items[0]) =============== #
    board_option_text = parsed_items[0].strip() # "[2027 27_K27LP K27LP] Board Option:2011C2000CA"

    # Extract header inside square brackets [...]
    header_match = re.search(r"\[(.*?)\]", board_option_text)
    if header_match:
        data["Header"] = header_match.group(1)

    # FIXED REGEX: Remove [...] using proper escaped brackets \[.*?\]
    clean_board_text = re.sub(r"\[.*?\]", "", board_option_text).strip() # "Board Option:2011C2000CA"

    # Split key and value by ":"
    if ":" in clean_board_text:
        key, value = clean_board_text.split(":", 1)
        data[key.strip()] = value.strip()


    # =============== 2. TOOL OPTION EXTRACTION (parsed_items[1]) =============== #
    tool_option_text = parsed_items[1].strip()

    tool_match = re.search(r"\((.*?)\)", tool_option_text)
    if tool_match:
        raw_tools = tool_match.group(1)
        tool_dict = dict(pair.split(":") for pair in raw_tools.split(","))
        data["Tool Option"] = tool_dict


    # =============== 3. REMAINING ITEMS EXTRACTION (parsed_items[2:]) =============== #
    for item in parsed_items[2:]:
        item = item.strip()
        
        if ":" in item:
            key, value = item.split(":", 1)
            data[key.strip()] = value.strip()
        else:
            match = re.match(r"(.+?)\s*\[(Yes|No)\]", item)
            if match:
                key = match.group(1).strip() 
                value = match.group(2).strip()
                data[key] = value

    # Output complete parsed JSON structure
    #st.json(data)

    return data

def tool_option_js_query_bom_input(target_bom):

   

    get_query_list = target_bom['data']

    # Filter items where childNameDisplay starts with 'EBT' AND jobExplanation is not null/empty
    new_query_list = [
        {
            "childNameDisplay": item["childNameDisplay"],
            "jobExplanation": item["jobExplanation"]
        }
        for item in get_query_list
        if item.get("childNameDisplay", "").startswith("EBT") 
        and item.get("jobExplanation") is not None  # Excludes None / null
        and item.get("jobExplanation") != ""        # Excludes empty strings
    ]

    get_job_exp = new_query_list[0]['jobExplanation']

    parsed_items = get_job_exp.split('/')
    data = {}

    # =============== 1. BOARD OPTION & HEADER EXTRACTION (parsed_items[0]) =============== #
    board_option_text = parsed_items[0].strip() # "[2027 27_K27LP K27LP] Board Option:2011C2000CA"

    # Extract header inside square brackets [...]
    header_match = re.search(r"\[(.*?)\]", board_option_text)
    if header_match:
        data["Header"] = header_match.group(1)

    # FIXED REGEX: Remove [...] using proper escaped brackets \[.*?\]
    clean_board_text = re.sub(r"\[.*?\]", "", board_option_text).strip() # "Board Option:2011C2000CA"

    # Split key and value by ":"
    if ":" in clean_board_text:
        key, value = clean_board_text.split(":", 1)
        data[key.strip()] = value.strip()


    # =============== 2. TOOL OPTION EXTRACTION (parsed_items[1]) =============== #
    tool_option_text = parsed_items[1].strip()

    tool_match = re.search(r"\((.*?)\)", tool_option_text)
    if tool_match:
        raw_tools = tool_match.group(1)
        tool_dict = dict(pair.split(":") for pair in raw_tools.split(","))
        data["Tool Option"] = tool_dict


    # =============== 3. REMAINING ITEMS EXTRACTION (parsed_items[2:]) =============== #
    for item in parsed_items[2:]:
        item = item.strip()
        
        if ":" in item:
            key, value = item.split(":", 1)
            data[key.strip()] = value.strip()
        else:
            match = re.match(r"(.+?)\s*\[(Yes|No)\]", item)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                data[key] = value

    # Output complete parsed JSON structure
    #st.json(data)

    return data

## ===> Tool Option Get Informtion <===
def get_tool_option_settings(target_model):

    def convert_options_to_dict(option_list):
        """Converts a list of dicts [{'name': '...', 'selected_value': '...'},

        ...] into a dictionary {'name': 'selected_value', ...}.
        """
        if isinstance(option_list, list):
            return {item["name"]: item["selected_value"] for item in option_list}
        return option_list

    #Get Tool Option
    js_query_tool = tool_option_js_query_bom_input(target_model)
    #st.json(js_query_tool)

    tool_option_all = js_query_tool['Tool Option']

    get_tool_option1 = int(js_query_tool['Tool Option']["1"])
    get_tool_option2 = int(js_query_tool['Tool Option']["2"])
    get_tool_option3 = int(js_query_tool['Tool Option']["3"])
    get_tool_option4 = int(js_query_tool['Tool Option']["4"])
    get_tool_option5 = int(js_query_tool['Tool Option']["5"])
    get_tool_option6 = int(js_query_tool['Tool Option']["6"])
    get_board_option = str(js_query_tool['Board Option'])
    get_board_option = int(get_board_option, 16)

    ##Get Detailed Settings for each Tool Option
    emulator_json = get_emulator_json("27")
    machine_json = get_machine_json("27")

    # 1. Initialize the emulator using the loaded local JSON data
    emu = TOMS(
        model_name="WEBOS27", 
        mock_emulator=emulator_json, 
        mock_machine=machine_json
    )

    get_tool_option1 = emu.decode_tool_option("ToolOption1", get_tool_option1)
    get_tool_option2 = emu.decode_tool_option("ToolOption2", get_tool_option2)
    get_tool_option3 = emu.decode_tool_option("ToolOption3", get_tool_option3)
    get_tool_option4 = emu.decode_tool_option("ToolOption4", get_tool_option4)
    get_tool_option5 = emu.decode_tool_option("ToolOption5", get_tool_option5)
    get_tool_option6 = emu.decode_tool_option("ToolOption6", get_tool_option6)
    get_board_option = emu.decode_tool_option("BoardOption", get_board_option)

    # Convert tool_option6 to dictionary and translate defaultStdBacklight
    tool_option6_dict = convert_options_to_dict(get_tool_option6)
    if "defaultStdBacklight" in tool_option6_dict:
        backlight_mapping = [
            "25~29", "30~34", "35~39", "40~44", "45~49", "50~54",
            "55~59", "60~64", "65~69", "70~75", "76~79", "80~84",
            "85~89", "90~94", "95~99", "100"
        ]
        try:
            val = int(tool_option6_dict["defaultStdBacklight"])
            if 0 <= val <= 15:
                tool_option6_dict["defaultStdBacklight"] = backlight_mapping[val]
        except (ValueError, TypeError):
            pass

    model_tool_option = {
        "model_tool_option": js_query_tool,
        "board_option": convert_options_to_dict(get_board_option),
        "tool_option1": convert_options_to_dict(get_tool_option1),
        "tool_option2": convert_options_to_dict(get_tool_option2),
        "tool_option3": convert_options_to_dict(get_tool_option3),
        "tool_option4": convert_options_to_dict(get_tool_option4),
        "tool_option5": convert_options_to_dict(get_tool_option5),
        "tool_option6": convert_options_to_dict(get_tool_option6),
    }

    return model_tool_option

def normalize_option_section(section_data):
    """Converts list-based option data like [{'name': 'panelType',

    'selected_value': 'LCD'}] into a flat dictionary {'panelType': 'LCD'}. If it
    is already a dictionary, returns it as is.
    """
    if isinstance(section_data, list):
        return {
            item["name"]: item.get("selected_value")
            for item in section_data
            if isinstance(item, dict) and "name" in item
        }
    elif isinstance(section_data, dict):
        # Handles nested dictionaries like "Tool Option": {"1": "218240", ...}
        return section_data
    return {}

def normalize_full_tool_option(tool_option_json):
    """Normalizes all sections in a tool option JSON object."""
    if not isinstance(tool_option_json, dict):
        return {}

    normalized = {}
    for section_name, section_content in tool_option_json.items():
        normalized[section_name] = normalize_option_section(section_content)
    return normalized


## ==> compare and judgement <=== ##
def compare_tool_options(target_data, dev_data, init_data, get_tool_op_query: dict, jira_input, get_json_area_code=None):
    """Compares key-value pairs across target, dev, and init JSON outputs and returns
    a structured comparison dictionary.
    """
    comparison_result = {}

    # Helper function to normalize equivalent state strings
    def normalize_value_state(val):
        if val is None:
            return None
        if isinstance(val, str):
            val_lower = val.strip().lower()
            if val_lower in {"off", "no"}:
                return "OFF"
            if val_lower in {"on", "yes"}:
                return "ON"
        return val

    # Extract single dict if jira_input is passed as a list of dicts
    if isinstance(jira_input, list) and len(jira_input) > 0:
        jira_dict = jira_input[0]
    elif isinstance(jira_input, dict):
        jira_dict = jira_input
    else:
        jira_dict = {}


    # Extract single dict if get_json_area_code is passed as a list of dicts
    if isinstance(get_json_area_code, list) and len(get_json_area_code) > 0:
        area_code_dict = get_json_area_code[0]
    elif isinstance(get_json_area_code, dict):
        area_code_dict = get_json_area_code
    else:
        area_code_dict = {}

    # Check compare Area Code
    AREA_CODE_KEYS = {
        "Area Option",
        "Country Group",
        "Country"
    }

    AREA_CODE_MAPPING = {
        "Area Option": "Area Option",
        "Country Group": "Country Group",
        "Country": "Country"
    }

    #Check Compare with Jira Option
    # Jira Reference Mapping: target_key -> jira_key
    JIRA_MAPPING = {
        "eyeCurveDerivation": "audio_eq",
        "maxPwmType": "to_max_pwm",
        "defaultStdBacklight": "to_def_backlight",
        "adaptDimDefault": "to_adaptdim_def",
        "motionEyeCareIndex": "to_mec",
        "oledCPC": "to_oled_cpc",
        "supportNewErP": "to_new_erp",
        "standardBacklight": "to_standard_backlight",
        "supportLuminanceUp": "to_luminance_up",
        "supportEpa": "to_energy_star"
        # Note: 'supportEpa' duplicate reference mapped cleanly
    }

    JIRA_KEYS = set(JIRA_MAPPING.keys())


    # Check compare with Region Rule
    REGION_KEYS = {
        "supportDvrReady",
        "supportCiAp",
        "supportDtcpKey",
        "supportUhdcpKey",
        "supportHeadPhone",
        "supportNewErP",
        "supportCiEcpAp",
        "ATSC3.0",
        "CI+",
        "CI+ECP",
        "DTCP Rx"
    }

    # Keys that should undergo the Engineer Confirm logic (Check compare with Initial Model)
    INCLUDED_CONFIRM_KEYS = {
        "moduleInchType",
        "toolType",
        "moduleMakerType",
        "tconPmicType",
        "moduleBackLightType",
        "panelLedBarType",
        "adjustVCOM",
        "audioPwVolt",
        "pwm2Duty",
        "scanningBl",
        "modeSelect",
        "panelGamutType",
        "motionProMode",
        "ampChipType",
        "audioSpkWatt", 
        "aiSoundType",
        "pwmFreqDouble",
        "motionBooster",
        "DPCType",
        "logoLight",
        "supportFanControl",
        "cameraType",
        "supportWol",
        "hdmiSwitchType",
        "supportMovingSpeaker",
        "supportIRBlaster",
        "supportScreenRollerMotor",
        "supportMotionDetectSensor",
        "supportLCDScreenCooling",
        "supportLAN",
        "supportOpticalJack",
        "supportFarFieldVoice",
        "supportTypecCtric",
        "AiArtExtension",
        "boardDesign",
        "emmcDensityAutoExtension",
        "supportMacAp",
        "supportEsnAp",
        "supportWidevineAp",
        "PDCharge",
        "digitalEye",
        "supportIsf",
        "supportTvLink",
        "supportCalmanSW",
        "supportAudioLineOut",
        "wifiType",
        "wifiMacType",
        "motionRemoconType",
        "eyeCurveDerivation",
        "edidType",
        "panelType",
        "panelInterface",
        "panelResolution",
        "panelMaxFrameRate",
        "panelMaxBitRate",
        "panelDivisionType",
        "externalFrcType",
        "ddrSize",
        "micomLocalKeyType",
        "arRlOnControl",
        "irLedControl",
        "modelType",
        "weeTurnkeyVersion",
        "pmicType"
    }

    # New Keys designated to have the result 'Unchecked'
    ENGINEER_CHECKED_KEYS = {
        "bplCurrentType",
        "vividSportsBacklight",
        "hdrDefaultBacklight",
        "supportDolbyVisionHDR",
        "supportVRR",
        "supportFreesyncPro",
        "supportHDRPlus",
        "supportMirrorMode",
        "specialEditionType",
        "videoIndex",
        "audioIndex",
        "maxInputNumberUsb",
        "usb1",
        "usb2",
        "usb3",
        "soundModeType"
        # Add your setup keys here that should default to 'Unchecked'
        # e.g., "setupKey1", "setupKey2"
    }

    target_norm = normalize_full_tool_option(target_data) if 'normalize_full_tool_option' in globals() else target_data
    dev_norm = normalize_full_tool_option(dev_data) if 'normalize_full_tool_option' in globals() else dev_data
    init_norm = normalize_full_tool_option(init_data) if 'normalize_full_tool_option' in globals() else init_data

    all_sections = (
        set(target_norm.keys()) | set(dev_norm.keys()) | set(init_norm.keys())
    )

    is_first_row_global = True

    for section in sorted(all_sections):
        target_sec = target_norm.get(section, {})
        dev_sec = dev_norm.get(section, {})
        init_sec = init_norm.get(section, {})

        all_item_keys = (
            set(target_sec.keys())
            | set(dev_sec.keys())
            | set(init_sec.keys())
        )

        section_comparison = []

        for key in sorted(all_item_keys):
            v_target = target_sec.get(key)
            v_dev = dev_sec.get(key)
            v_init = init_sec.get(key)

            norm_target_val = normalize_value_state(v_target)
            norm_dev_val = normalize_value_state(v_dev)
            norm_init_val = normalize_value_state(v_init)

            str_target = json.dumps(norm_target_val, sort_keys=True) if isinstance(norm_target_val, dict) else norm_target_val
            str_dev = json.dumps(norm_dev_val, sort_keys=True) if isinstance(norm_dev_val, dict) else norm_dev_val
            str_init = json.dumps(norm_init_val, sort_keys=True) if isinstance(norm_init_val, dict) else norm_init_val

            # 1. Status Check
            is_same = str_target == str_dev == str_init
            status = "SAME" if is_same else "DIFFERENT"

            # 2. Region Check
            if key in REGION_KEYS:
                v_op = get_tool_op_query.get(key)
                norm_op_val = normalize_value_state(v_op)
                str_op = json.dumps(norm_op_val, sort_keys=True) if isinstance(norm_op_val, dict) else norm_op_val
                
                region_check = "PASS" if str_target == str_op else "CHECK"
            else:
                region_check = "N/A"

            # 3. Editor Field
            if key in JIRA_KEYS:
                editor = "Jira"
            elif key in AREA_CODE_KEYS:
                editor = "Area Code"
            elif key in REGION_KEYS:
                editor = "Region / OP"
            elif key in INCLUDED_CONFIRM_KEYS:
                editor = "Initial"
            elif key in ENGINEER_CHECKED_KEYS:
                editor = "Engineer Checked"
            else:
                editor = "No Rule"

            # 4. Engineer Confirm Logic
            if key in JIRA_KEYS:
                jira_field = JIRA_MAPPING.get(key)
                v_jira = jira_dict.get(jira_field)
                norm_jira_val = normalize_value_state(v_jira)

                comp_target_val = norm_target_val
                if key == "defaultStdBacklight" and isinstance(comp_target_val, str) and "~" in comp_target_val:
                    comp_target_val = comp_target_val.split("~")[0].strip()

                if comp_target_val is None or norm_jira_val is None:
                    engineer_confirm = "CHECK"
                elif str(comp_target_val) == str(norm_jira_val):
                    engineer_confirm = "OK"
                else:
                    engineer_confirm = "CHECK"
            elif key in AREA_CODE_KEYS:
                area_field = AREA_CODE_MAPPING.get(key)
                v_area = area_code_dict.get(area_field)
                norm_area_val = normalize_value_state(v_area)

                if norm_target_val is None and norm_area_val is None:
                    engineer_confirm = "OK"
                elif str(norm_target_val) == str(norm_area_val):
                    engineer_confirm = "OK"
                else:
                    engineer_confirm = "UNCHECK"
            elif key in INCLUDED_CONFIRM_KEYS:
                engineer_confirm = "OK" if (str_init == str_dev == str_target) else "NG"
            elif key in ENGINEER_CHECKED_KEYS:
                engineer_confirm = "Unchecked"
            elif key in REGION_KEYS:
                v_op = get_tool_op_query.get(key)
                norm_op_val = normalize_value_state(v_op)
                str_op = json.dumps(norm_op_val, sort_keys=True) if isinstance(norm_op_val, dict) else norm_op_val
                engineer_confirm = "OK" if (str_target == str_op) else "NG"
            else:
                engineer_confirm = "UNCHECKED"

            # 5. Compare Note formatting
            prm_note_prefix = (
                "[Note: PRM Check evaluated whether Target and Dev values matched (PASS if equal, FAIL otherwise)] | "
                if is_first_row_global else ""
            )
            is_first_row_global = False

            if key in JIRA_KEYS:
                jira_field = JIRA_MAPPING.get(key)
                v_jira = jira_dict.get(jira_field)
                norm_jira_val = normalize_value_state(v_jira)

                comp_target_val = norm_target_val
                if key == "defaultStdBacklight" and isinstance(comp_target_val, str) and "~" in comp_target_val:
                    comp_target_val = comp_target_val.split("~")[0].strip()

                if comp_target_val is not None and norm_jira_val is not None and str(comp_target_val) == str(norm_jira_val):
                    conclusion = "same as Jira"
                else:
                    conclusion = "different from Jira"
            elif key in AREA_CODE_KEYS:
                area_field = AREA_CODE_MAPPING.get(key)
                v_area = area_code_dict.get(area_field)
                norm_area_val = normalize_value_state(v_area)

                if (norm_target_val is None and norm_area_val is None) or (str(norm_target_val) == str(norm_area_val)):
                    conclusion = "Same as Area Code Rule"
                else:
                    conclusion = "different from Area Code Rule"
            elif key in INCLUDED_CONFIRM_KEYS:
                conclusion = "same as initial" if (str_init == str_dev == str_target) else "different than initial"
            elif key in ENGINEER_CHECKED_KEYS:
                conclusion = "UNCHECKED by ENGINEER"
            elif key in REGION_KEYS:
                v_op = get_tool_op_query.get(key)
                norm_op_val = normalize_value_state(v_op)
                str_op = json.dumps(norm_op_val, sort_keys=True) if isinstance(norm_op_val, dict) else norm_op_val
                conclusion = "Same as OP" if str_target == str_op else "Different than OP"
            else:
                conclusion = "All sources match" if is_same else f"Target: {v_target} | Dev: {v_dev} | Init: {v_init}"

            compare_note = prm_note_prefix + conclusion

            section_comparison.append({
                "key": key,
                "target_value": v_target,
                "dev_value": v_dev,
                "init_value": v_init,
                "status": status,
                "region check": region_check,
                "editor": editor,
                "compare note": compare_note,
                "Engineer Confirm": engineer_confirm,
            })

        comparison_result[section] = section_comparison

    return comparison_resul

def summarize_engineer_confirms(result_dict):
    """
    Summarizes the 'Engineer Confirm' status for each 'editor' category 
    and adds an 'overall_result' key based on the priority: NG > CHECK > UNCHECKED > OK.
    """
    editor_statuses = {}
    all_statuses = set()
    
    # Priority mapping to determine the worst-case status
    priority = {"NG": 3, "CHECK": 2, "UNCHECKED": 1, "OK": 0}

    def normalize_status(val):
        if not val:
            return "OK"
        v_upper = str(val).strip().upper()
        if "NG" in v_upper:
            return "NG"
        if "CHECK" in v_upper:
            return "CHECK"
        if "UNCHECK" in v_upper:
            return "UNCHECKED"
        if "OK" in v_upper:
            return "OK"
        return "OK" # Default fallback

    # 1. Collect all statuses per editor category and globally
    for section, items in result_dict.items():
        for item in items:
            editor = item.get("editor", "Unknown")
            confirm_val = item.get("Engineer Confirm")
            
            status = normalize_status(confirm_val)
            
            if editor not in editor_statuses:
                editor_statuses[editor] = set()
            editor_statuses[editor].add(status)
            all_statuses.add(status)

    # 2. Determine the summary status per category
    summary_result = {}
    for editor, statuses in editor_statuses.items():
        highest_status = "OK"
        max_priority = -1
        
        for status in statuses:
            prio = priority.get(status, 0)
            if prio > max_priority:
                max_priority = prio
                highest_status = status
                
        summary_result[editor] = highest_status

    # 3. Determine the overall result using the same priority logic
    overall_highest = "OK"
    overall_max_priority = -1
    for status in all_statuses:
        prio = priority.get(status, 0)
        if prio > overall_max_priority:
            overall_max_priority = prio
            overall_highest = status
            
    summary_result["overall_result"] = overall_highest

    return summary_result


def compare_tool_option_hw():
    
    get_jira_json = get_jira_power_cons(API_KEY=jira_key, model_name=model_name)
    get_jira_json_model, jira_df, only_jira_json = get_jira_tool_option_df(get_jira_json=get_jira_json)

    get_tool_option_region = get_tool_op(suffix_country=suffix_profile)

    result_dict = get_compare_tool_option_result(
    target_model=target_model, 
    dev_model=dev_model, 
    init_model=init_model, 
    suffix_country=suffix_profile,
    jira_input=only_jira_json,
    get_json_area=get_area_code_now
    )

    result_toolOption = {
        "result" : result_dict,
        "jiraInput": only_jira_json,
        "areaCode" : get_area_code_now
    }


    return result_toolOption