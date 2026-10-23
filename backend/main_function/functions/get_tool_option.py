import re
import json
import streamlit as st
from functions.conditioning import zerobom_conditioning
from functions.TOMS.toms_req import get_emulator_json, get_machine_json, TOMS


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


def compare_tool_options(target_data, dev_data, init_data):
    """Compares key-value pairs across target, dev, and init JSON outputs and returns
    a structured comparison dictionary.
    """
    comparison_result = {}

    REGION_KEYS = {
        "Area Code",
        "Country Group",
        "Country",
        "countryType",
        "Japan LNB",
        "ATSC3.0",
        "DVBS",
        "DVBS2",
    }

    # Keys that should undergo the Engineer Confirm logic (Modify this set as needed)
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

    # Normalize all three inputs to ensure uniform {key: value} structures
    target_norm = normalize_full_tool_option(target_data)
    dev_norm = normalize_full_tool_option(dev_data)
    init_norm = normalize_full_tool_option(init_data)

    all_sections = (
        set(target_norm.keys()) | set(dev_norm.keys()) | set(init_norm.keys())
    )

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

            # Convert dicts (like Tool Option sub-dicts) to string for direct comparison
            str_target = (
                json.dumps(v_target, sort_keys=True)
                if isinstance(v_target, dict)
                else v_target
            )
            str_dev = (
                json.dumps(v_dev, sort_keys=True)
                if isinstance(v_dev, dict)
                else v_dev
            )
            str_init = (
                json.dumps(v_init, sort_keys=True)
                if isinstance(v_init, dict)
                else v_init
            )

            # 1. Status Check
            is_same = str_target == str_dev == str_init
            status = "SAME" if is_same else "DIFFERENT"

            # 2. Region Check
            if key in REGION_KEYS:
                if str_target == str_dev and str_target != str_init:
                    region_check = "PASS"
                elif is_same:
                    region_check = "SAME"
                else:
                    region_check = "CHECK"
            else:
                region_check = "N/A"

            # 3. PRM Check
            prm_check = "PASS" if str_target == str_dev else "FAIL"

            # 4. Editor Field
            if is_same:
                editor = "System"
            elif str_target != str_dev and str_target != str_init:
                editor = "Target Admin"
            elif str_dev != str_target and str_dev != str_init:
                editor = "Dev Engineer"
            else:
                editor = "Init Spec"

            # 5. Compare Note
            if is_same:
                compare_note = "All sources match"
            else:
                compare_note = (
                    f"Target: {v_target} | Dev: {v_dev} | Init: {v_init}"
                )

            # 6. Engineer Confirm Logic
            if key in INCLUDED_CONFIRM_KEYS:
                # Check if init_value matches both dev_value and target_value
                engineer_confirm = "OK" if (str_init == str_dev == str_target) else "UNCHECKED"
            else:
                engineer_confirm = "N/A"

            section_comparison.append({
                "key": key,
                "target_value": v_target,
                "dev_value": v_dev,
                "init_value": v_init,
                "status": status,
                "region check": region_check,
                "prm check": prm_check,
                "editor": editor,
                "compare note": compare_note,
                "Engineer Confirm": engineer_confirm,
            })

        comparison_result[section] = section_comparison

    return comparison_result


def get_compare_tool_option_result(target_model, dev_model, init_model):
    target_tool_option = get_tool_option_settings(target_model)
    dev_tool_option = get_tool_option_settings(dev_model)
    init_tool_option = get_tool_option_settings(init_model)

    result_dict = compare_tool_options(
        target_tool_option, dev_tool_option, init_tool_option
    )
    return result_dict



