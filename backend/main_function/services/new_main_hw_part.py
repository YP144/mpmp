import json
import re
import pandas as pd
from openpyxl import load_workbook

class PartComparison:
    def __init__(self, json_input: str | dict = "json/0_target_ebom.json", excel_path: str = "excel/template_part.xlsx"):
        self.excel_path = excel_path
        
        # Handle input whether it's a file path (str) or already a dictionary (dict)
        if isinstance(json_input, dict):
            self.response_data = json_input
        elif isinstance(json_input, str):
            # Optional: check if string is a direct JSON payload or a file path
            if json_input.strip().startswith("{"):
                self.response_data = json.loads(json_input)
            else:
                with open(json_input, "r", encoding="utf-8") as f:
                    self.response_data = json.load(f)
        else:
            raise TypeError("json_input must be a valid file path (str) or a dictionary (dict).")

        self.data_items = self.response_data.get("data", [])
        
        # Initialize output attributes
        self.targethw = pd.DataFrame()
        self.targethw_dict = []

    def _search_ebom(self, parent_ids, name_prefix="", description_keyword="", spec_keyword="", limit=1):
        """Generic helper to search and extract component records matching criteria."""
        if isinstance(parent_ids, str):
            parent_ids = [parent_ids]

        # Normalize name_prefix and spec_keyword to tuples so they handle strings or tuples seamlessly
        name_prefixes = tuple(name_prefix) if isinstance(name_prefix, (tuple, list)) else ((name_prefix,) if name_prefix else ())
        spec_keywords = tuple(spec_keyword) if isinstance(spec_keyword, (tuple, list)) else ((spec_keyword,) if spec_keyword else ())

        matched_items = []
        for item in self.data_items:
            # Check parent ID match
            if parent_ids and item.get("uniqueStrParent") not in parent_ids:
                continue
            
            child_name = str(item.get("childNameDisplay", ""))
            out_data = item.get("outData", {})
            pp_desc = str(out_data.get("pp_descriptions", ""))
            site_spec = str(out_data.get("mr_siteTechnicalSpec", ""))

            # Apply filters safely supporting tuples/lists
            if name_prefixes and not any(p in child_name for p in name_prefixes):
                continue
            if description_keyword and description_keyword not in pp_desc:
                continue
            if spec_keywords and not any(s in site_spec for s in spec_keywords):
                continue

            matched_items.append({
                "pn": item.get("childNameDisplay", ""),
                "qty": item.get("bomQuantity", ""),
                "level": item.get("bomLevel", ""),
                "uit": out_data.get("mr_userItemType", ""),
                "supplytype": item.get("supplyType", ""),
                "state": out_data.get("pp_states", ""),
                "parttype": item.get("dataType", ""),
                "spec": site_spec,
                "uniqueid": item.get("uniqueStr", "")
            })

            if len(matched_items) >= limit:
                break

        return matched_items

    def _get_single_part(self, parent_ids, name_prefix="", description_keyword="", spec_keyword=""):
        res = self._search_ebom(parent_ids, name_prefix, description_keyword, spec_keyword, limit=1)
        if res:
            return res[0]
        # Return default empty dict structure
        return {
            "pn": "", "qty": "", "level": "", "uit": "", 
            "supplytype": "", "state": "", "parttype": "", "spec": "", "uniqueid": ""
        }

    def target_run(self):
        # 1. Accessory Assembly (Root level parent "00001")
        accessory = self._get_single_part("00001", name_prefix="AAA", description_keyword="Accessory Assembly")
        accessory_uid = accessory["uniqueid"]

        # 2. Ferrite Core
        ferrite_core = self._get_single_part(accessory_uid, name_prefix="621", description_keyword="Ferrite")

        # 3. Batteries & Remotes
        battery = self._get_single_part(
            accessory_uid, 
            description_keyword="Battery", 
            spec_keyword="LR" # covers LR06 / LR03 variations handled via filtering or name
        )
        lcon_battery = self._get_single_part(None, name_prefix="130", description_keyword="Battery")
        remote = self._get_single_part(accessory_uid, name_prefix="AKB", description_keyword="Remote", spec_keyword="MR")
        lcon_remote = self._get_single_part(None, name_prefix="AKB", description_keyword="Remote", spec_keyword="L-Con")

        # 4. Bracket & Sub-assemblies
        bracket_assy = self._get_single_part("00001", name_prefix=("ABA", "ACQ"), description_keyword="Bracket Assembly") # custom handling or simplified
        # For simplicity and backward compatibility following exact filters:
        bracket_assy = self._get_single_part("00001", description_keyword="Bracket Assembly")
        bracket_uid = bracket_assy["uniqueid"]

        ebt_subassy = self._get_single_part(bracket_uid, name_prefix="EBT", description_keyword="Chassis Assembly,Sub")
        ebt_sub_uid = ebt_subassy["uniqueid"]

        wifi_assy = self._get_single_part(ebt_sub_uid, name_prefix="EAT", description_keyword="Module,Wifi Bluetooth Module")
        ir_assy = self._get_single_part(ebt_sub_uid, name_prefix="EBR", description_keyword="PCB Assembly,IR Key")
        ffc_assy = self._get_single_part(ebt_sub_uid, name_prefix="EAD", description_keyword="Cable,FFC")

        # 5. Speakers
        speaker_right = self._get_single_part("00001", name_prefix="EAB", description_keyword="Speaker", spec_keyword="RIGHT")
        speaker_left = self._get_single_part("00001", name_prefix="EAB", description_keyword="Speaker", spec_keyword="LEFT")
        speaker_general = self._get_single_part("00001", name_prefix="EAB", description_keyword="Speaker")

        # 6. FFC Main (Multiple items)
        ffc_main_items = self._search_ebom(None, name_prefix="EAD", description_keyword="Cable,FFC", limit=2)
        while len(ffc_main_items) < 2:
            ffc_main_items.append({k: "" for k in ["pn", "qty", "level", "uit", "supplytype", "state", "parttype", "spec", "uniqueid"]})

        # 7. Power & Main Chassis
        ebt_powercord = self._get_single_part("00001", name_prefix="EBT", description_keyword="Chassis Assembly,Sub")
        powercord_uid = ebt_powercord["uniqueid"]
        powercord_attach = self._get_single_part(powercord_uid, name_prefix="EAD", description_keyword="Power Cord,Attach")
        powercord_detach = self._get_single_part(None, name_prefix="EAD", description_keyword="Power Cord,Detach")
        power_board = self._get_single_part("00001", name_prefix=("EAY", "EBR"), description_keyword="Power", spec_keyword="LGP")
        
        ebt_main = self._get_single_part("00001", name_prefix="EBT", description_keyword="Chassis Assembly", spec_keyword="MAIN")
        ebt_main_uid = ebt_main["uniqueid"]

        holder_main = self._get_single_part(ebt_main_uid, name_prefix="MEG", description_keyword="Holder")
        tuner_cover = self._get_single_part(ebt_main_uid, name_prefix="EBZ", description_keyword="Part", spec_keyword="Tuner")
        transparent_tape = self._get_single_part(ebt_main_uid, name_prefix="961", description_keyword="Tape,Glass Fiber")
        harness_single = self._get_single_part(ebt_main_uid, name_prefix="EAD", description_keyword="Harness,Single")
        harness_multi = self._get_single_part(ebt_main_uid, name_prefix="EAD", description_keyword="Harness,Multi")
        
        plate_shield = self._get_single_part(ebt_main_uid, name_prefix="EBS", description_keyword="Electric Parts Assembly,Main")
        plate_shield_uid = plate_shield["uniqueid"]

        plate_sink = self._get_single_part(plate_shield_uid, name_prefix=("MED", "MGJ"))
        plate_holder = self._get_single_part(plate_shield_uid, name_prefix="MEG", description_keyword="Holder")
        sheet_cooper = self._get_single_part(plate_shield_uid, name_prefix="RAA", description_keyword="Sheet,Copper")
        
        ebr_package = self._get_single_part(ebt_main_uid, name_prefix="EBR", description_keyword="PCB Assembly,Main", spec_keyword="PAKING")
        ebr_package_uid = ebr_package["uniqueid"]
        main_package = self._get_single_part(ebr_package_uid, name_prefix="AGF", description_keyword="Package Assembly")

        # Model check for EBU Main
        is_mrgb9m = any("MRGB9M" in item.get("childNameDisplay", "") for item in self.data_items)
        if is_mrgb9m:
            ebu_main = self._get_single_part(None, name_prefix="EBU", description_keyword="BPR Total Assembly", spec_keyword="MAIN")
        else:
            ebu_main = self._get_single_part([ebt_main_uid, ebr_package_uid], name_prefix="EBU", description_keyword="ORP Total Assembly", spec_keyword="MAIN")
        
        ebu_main_uid = ebu_main["uniqueid"]
        ebr_main = self._get_single_part(ebu_main_uid, name_prefix="EBR", description_keyword="Insert PCB Assembly", spec_keyword="MAIN")
        pcb_main = self._get_single_part(None, name_prefix="EAX", description_keyword="PCB", spec_keyword="Main")
        wifi_assymain = self._get_single_part(ebr_package_uid, name_prefix="EAT", description_keyword="Module,Wifi Bluetooth Module")
        edid = self._get_single_part(None, name_prefix="ECC", description_keyword="EDID Check Sum Assembly")
        sw_assy = self._get_single_part(None, name_prefix="SAB", description_keyword="S/W Package", spec_keyword="eMMC")

        # SVC Parts
        ebu_svc = self._get_single_part("00001", name_prefix="EBU", description_keyword="Mainboard,ORP Total Assembly,SVC")
        ebu_svc_uid = ebu_svc["uniqueid"]
        tuner_coversvc = self._get_single_part(ebu_svc_uid, name_prefix="EBZ", description_keyword="Part", spec_keyword="Tuner")
        holder_svc = self._get_single_part(ebu_svc_uid, name_prefix="MEG", description_keyword="Holder")
        ebr_svc = self._get_single_part(ebu_svc_uid, name_prefix="EBR", description_keyword="ORP Insert PCB Assembly")
        plate_shieldsvc = self._get_single_part(ebu_svc_uid, name_prefix="EBS", description_keyword="Electric Parts Assembly,Main")
        wifi_assysvc = self._get_single_part(ebr_svc.get("uniqueid"), name_prefix="EAT", description_keyword="Module,Wifi Bluetooth Module")

        # List/Bulk Items (Gaskets & Tapes up to 5 items)
        gaskets = self._search_ebom(["00001", ebt_main_uid], name_prefix="MDS", description_keyword="Gasket", limit=5)
        tapes = self._search_ebom(["00001", ebt_main_uid], name_prefix="RAB", description_keyword="Tape", limit=5)
        dampers = self._search_ebom(["00001", ebt_main_uid], name_prefix="MCQ", description_keyword="Damper", limit=5)

        # Ensure lists are padded to length 5 for safe unpack/usage
        def pad_list(lst, count=5):
            empty_item = {k: "" for k in ["pn", "qty", "level", "uit", "supplytype", "state", "parttype", "spec", "uniqueid"]}
            while len(lst) < count:
                lst.append(empty_item)
            return lst

        gaskets = pad_list(gaskets)
        tapes = pad_list(tapes)
        dampers = pad_list(dampers)

        # Collect all parts for export JSON
        all_parts_refs = [
            accessory, ferrite_core, battery, remote, lcon_battery, lcon_remote,
            bracket_assy, ebt_subassy, wifi_assy, ir_assy, ffc_assy, speaker_right,
            speaker_left, speaker_general, ffc_main_items[0], ffc_main_items[1],
            ebt_powercord, powercord_attach, powercord_detach, power_board, ebt_main,
            holder_main, tuner_cover, transparent_tape, harness_single, harness_multi,
            plate_shield, plate_sink, plate_holder, sheet_cooper, ebr_package, main_package,
            ebu_main, ebr_main, pcb_main, wifi_assymain, edid, sw_assy, ebu_svc,
            tuner_coversvc, holder_svc, ebr_svc, plate_shieldsvc, wifi_assysvc
        ] + gaskets + tapes + dampers

        # Base category names
        raw_category_names = [
            "accessory", "ferrite_core", "battery", "remote", "lcon_battery", "lcon_remote",
            "bracket_assy", "ebt_subassy", "wifi_assy", "ir_assy", "ffc_assy", "speaker_right",
            "speaker_left", "speaker_general", "ffc_main_1", "ffc_main_2",
            "ebt_powercord", "powercord_attach", "powercord_detach", "power_board", "ebt_main",
            "holder_main", "tuner_cover", "transparent_tape", "harness_single", "harness_multi",
            "plate_shield", "plate_sink", "plate_holder", "sheet_cooper", "ebr_package", "main_package",
            "ebu_main", "ebr_main", "pcb_main", "wifi_assymain", "edid", "sw_assy", "ebu_svc",
            "tuner_coversvc", "holder_svc", "ebr_svc", "plate_shieldsvc", "wifi_assysvc"
        ] + [f"gasket_{i+1}" for i in range(len(gaskets))] \
          + [f"tape_{i+1}" for i in range(len(tapes))] \
          + [f"damper_{i+1}" for i in range(len(dampers))]

        # Format categories: remove `_{number}` suffix and replace `_` with space
        category_names = [re.sub(r'_\d+$', '', name).replace('_', ' ') for name in raw_category_names]

        # --- Assign to instance attributes ---
        all_hwpart_df = pd.DataFrame(all_parts_refs)
        all_hwpart_df['Category'] = category_names

        self.targethw = all_hwpart_df
        self.targethw_dict = all_hwpart_df.to_dict(orient="records")

        # Save files
        # Export to Json
        #all_hwpart_df.to_excel("json/1_target_hwpart.xlsx", index=False)
        #all_hwpart_df.to_json("json/1_target_hwpart.json", orient="records", indent=4)
        #print("Target Part List saved successfully.")

        # Excel template update
        #target_model_name = ""
        #target_model_df = pd.json_normalize([i for i in self.data_items if i.get("uniqueStr") == "00001"])
        #if not target_model_df.empty:
        #    target_model_name = target_model_df.iloc[0].get('childNameDisplay', '')

        #wb = load_workbook(self.excel_path)
        #ws = wb["BEN Compare"]
        #s["N4"] = str(target_model_name.split('@')[0]) if target_model_name else ""
        #wb.save(self.excel_path)
        #print("Target part compare completed.")

        



