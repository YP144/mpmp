import pandas as pd
import json
from openpyxl import load_workbook
from pathlib import Path

JSON_DIR = Path(__file__).resolve().parent.parent / "json"

class targetpart_compare():
    def __init__(self):
        pass
    def target_run(self):
        self.targetpartscrapper()
        # self.targetpart_compare()
        # developmentpartscrapper()
        # initialpartscrapper()
    def targetpartscrapper(self):

        with open(JSON_DIR / "0_target_ebom.json", "r", encoding="utf-8") as f:
            response_data = json.load(f)
        
        #<Search for specific components in EBOM data (Accessory Assembly)>
        Accesory = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == "00001" and
                "AAA" in "{}".format(item.get("childNameDisplay", "")) and 
                "Accessory Assembly" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))
            ))
            ])
        if not Accesory.empty:
            for idx, row in Accesory.iterrows():
                targetaccessory_pn = row['childNameDisplay']
                targetaccessory_qty = row['bomQuantity']
                targetaccessory_level = row['bomLevel']
                targetaccessory_uit = row['outData.mr_userItemType']
                targetaccessory_supplytype = row['supplyType']
                targetaccessory_state = row['outData.pp_states']
                targetaccessory_parttype = row['dataType']
                targetaccessory_spec = row['outData.mr_siteTechnicalSpec']
                targetaccessory_uniquieid = row['uniqueStr']
        else:
            targetaccessory_pn = ""
            targetaccessory_qty = ""
            targetaccessory_level = ""
            targetaccessory_uit = ""
            targetaccessory_supplytype = ""
            targetaccessory_state = ""
            targetaccessory_parttype = ""
            targetaccessory_spec = ""
            targetaccessory_uniquieid = ""
        #<Search for specific components in EBOM data (Ferrite Core)>
        Ferrit_core = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetaccessory_uniquieid and
                "621" in "{}".format(item.get("childNameDisplay", "")) and
                "Ferrite" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))
                ))
            ])
        if not Ferrit_core.empty:
            for idx, row in Ferrit_core.iterrows():
                targetferritcore_pn = row['childNameDisplay']
                targetferritcore_qty = row['bomQuantity']
                targetferritcore_level = row['bomLevel']
                targetferritcore_uit = row['outData.mr_userItemType']
                targetferritcore_supplytype = row['supplyType']
                targetferritcore_state = row['outData.pp_states']
                targetferritcore_parttype = row['dataType']
                targetferritcore_spec = row['outData.mr_siteTechnicalSpec']
                targetferritcore_uniquieid = row['uniqueStr']
        else:
            targetferritcore_pn = ""
            targetferritcore_qty = ""
            targetferritcore_level = ""
            targetferritcore_uit = ""
            targetferritcore_supplytype = ""
            targetferritcore_state = ""
            targetferritcore_parttype = ""
            targetferritcore_spec = ""
            targetferritcore_uniquieid = ""
        #<Search for specific components in EBOM data (MR battery)
        MR_battery = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetaccessory_uniquieid and
                "EAC" in "{}".format(item.get("childNameDisplay", "")) and
                "Battery" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "LR06" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", ""))) or 
                (item.get("uniqueStrParent") == targetaccessory_uniquieid and
                "691" in "{}".format(item.get("childNameDisplay", "")) and
                "Battery" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "LR06" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", ""))) or
                (item.get("uniqueStrParent") == targetaccessory_uniquieid and
                "EAC" in "{}".format(item.get("childNameDisplay", "")) and
                "Battery" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "LR03" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", ""))) or 
                (item.get("uniqueStrParent") == targetaccessory_uniquieid and 
                "691" in "{}".format(item.get("childNameDisplay", "")) and 
                "Battery" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "LR03" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", ""))
                ))
            ])
        if not MR_battery.empty:
            for idx, row in MR_battery.iterrows():
                targetbattery_pn = row['childNameDisplay']
                targetbattery_qty = row['bomQuantity']
                targetbattery_level = row['bomLevel']
                targetbattery_uit = row['outData.mr_userItemType']
                targetbattery_supplytype = row['supplyType']
                targetbattery_state = row['outData.pp_states']
                targetbattery_parttype = row['dataType']
                targetbattery_spec = row['outData.mr_siteTechnicalSpec']
                targetbattery_uniquieid = row['uniqueStr']
            targetbattery_pn = MR_battery['childNameDisplay'].iloc[0]
            targetbattery_qty = MR_battery['bomQuantity'].iloc[0]
            targetbattery_level = MR_battery['bomLevel'].iloc[0]
            targetbattery_uit = MR_battery['outData.mr_userItemType'].iloc[0]
            targetbattery_supplytype = MR_battery['supplyType'].iloc[0]
            targetbattery_state = MR_battery['outData.pp_states'].iloc[0]
            targetbattery_parttype = MR_battery['dataType'].iloc[0]
            targetbattery_spec = MR_battery['outData.mr_siteTechnicalSpec'].iloc[0]
            targetbattery_uniquieid = MR_battery['uniqueStr'].iloc[0]
        else:
            targetbattery_pn = ""
            targetbattery_qty = ""
            targetbattery_level = ""
            targetbattery_uit = ""
            targetbattery_supplytype = ""
            targetbattery_state = ""
            targetbattery_parttype = ""
            targetbattery_spec = ""
            targetbattery_uniquieid = ""
        #<Search for specific components in EBOM data (L-Con battery)
        Lcon_battery = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                "130" in "{}".format(item.get("childNameDisplay", "")) and
                "Battery" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))
                ))
            ])
        if not Lcon_battery.empty:
            for idx, row in Lcon_battery.iterrows():
                targetlconbattery_pn = row['childNameDisplay']
                targetlconbattery_qty = row['bomQuantity']
                targetlconbattery_level = row['bomLevel']
                targetlconbattery_uit = row['outData.mr_userItemType']
                targetlconbattery_supplytype = row['supplyType']
                targetlconbattery_state = row['outData.pp_states']
                targetlconbattery_parttype = row['dataType']
                targetlconbattery_spec = row['outData.mr_siteTechnicalSpec']
                targetlconbattery_uniquieid = row['uniqueStr']
            targetlconbattery_pn = Lcon_battery['childNameDisplay'].iloc[0]
            targetlconbattery_qty = Lcon_battery['bomQuantity'].iloc[0]
            targetlconbattery_level = Lcon_battery['bomLevel'].iloc[0]
            targetlconbattery_uit = Lcon_battery['outData.mr_userItemType'].iloc[0]
            targetlconbattery_supplytype = Lcon_battery['supplyType'].iloc[0]
            targetlconbattery_state = Lcon_battery['outData.pp_states'].iloc[0]
            targetlconbattery_parttype = Lcon_battery['dataType'].iloc[0]
            targetlconbattery_spec = Lcon_battery['outData.mr_siteTechnicalSpec'].iloc[0]
            targetlconbattery_uniquieid = Lcon_battery['uniqueStr'].iloc[0]
        else:
            targetlconbattery_pn = ""
            targetlconbattery_qty = ""
            targetlconbattery_level = ""
            targetlconbattery_uit = ""
            targetlconbattery_supplytype = ""
            targetlconbattery_state = ""
            targetlconbattery_parttype = ""
            targetlconbattery_spec = ""
            targetlconbattery_uniquieid = ""    
        #<Search for specific components in EBOM data (MR remote)
        MR_remote = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetaccessory_uniquieid and
                "AKB" in "{}".format(item.get("childNameDisplay", "")) and
                "Remote" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "MR" in "{}".format(item.get("outData", {}).get('mr_siteTechnicalSpec', ""))
                ))
            ])
        if not MR_remote.empty:
            for idx, row in MR_remote.iterrows():
                targetremote_pn = row['childNameDisplay']
                targetremote_qty = row['bomQuantity']
                targetremote_level = row['bomLevel']
                targetremote_uit = row['outData.mr_userItemType']
                targetremote_supplytype = row['supplyType']
                targetremote_state = row['outData.pp_states']
                targetremote_parttype = row['dataType']
                targetremote_spec = row['outData.mr_siteTechnicalSpec']
                targetremote_uniquieid = row['uniqueStr']
            targetremote_pn = MR_remote['childNameDisplay'].iloc[0]
            targetremote_qty = MR_remote['bomQuantity'].iloc[0]
            targetremote_level = MR_remote['bomLevel'].iloc[0]
            targetremote_uit = MR_remote['outData.mr_userItemType'].iloc[0]
            targetremote_supplytype = MR_remote['supplyType'].iloc[0]
            targetremote_state = MR_remote['outData.pp_states'].iloc[0]
            targetremote_parttype = MR_remote['dataType'].iloc[0]
            targetremote_spec = MR_remote['outData.mr_siteTechnicalSpec'].iloc[0]
            targetremote_uniquieid = MR_remote['uniqueStr'].iloc[0]
        else:
            targetremote_pn = ""
            targetremote_qty = ""
            targetremote_level = ""
            targetremote_uit = ""
            targetremote_supplytype = ""
            targetremote_state = ""
            targetremote_parttype = ""
            targetremote_spec = ""
            targetremote_uniquieid = ""
        #<Search for specific components in EBOM data (L-Con remote)
        Lcon_remote = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                "AKB" in "{}".format(item.get("childNameDisplay", "")) and
                "Remote" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "L-Con" in "{}".format(item.get("outData", {}).get('mr_siteTechnicalSpec', ""))
                ))
            ])
        if not Lcon_remote.empty:
            for idx, row in Lcon_remote.iterrows():
                targetlconremote_pn = row['childNameDisplay']
                targetlconremote_qty = row['bomQuantity']
                targetlconremote_level = row['bomLevel']
                targetlconremote_uit = row['outData.mr_userItemType']
                targetlconremote_supplytype = row['supplyType']
                targetlconremote_state = row['outData.pp_states']
                targetlconremote_parttype = row['dataType']
                targetlconremote_spec = row['outData.mr_siteTechnicalSpec']
                targetlconremote_uniquieid = row['uniqueStr']
            targetlconremote_pn = Lcon_remote['childNameDisplay'].iloc[0]
            targetlconremote_qty = Lcon_remote['bomQuantity'].iloc[0]
            targetlconremote_level = Lcon_remote['bomLevel'].iloc[0]
            targetlconremote_uit = Lcon_remote['outData.mr_userItemType'].iloc[0]
            targetlconremote_supplytype = Lcon_remote['supplyType'].iloc[0]
            targetlconremote_state = Lcon_remote['outData.pp_states'].iloc[0]
            targetlconremote_parttype = Lcon_remote['dataType'].iloc[0]
            targetlconremote_spec = Lcon_remote['outData.mr_siteTechnicalSpec'].iloc[0]
            targetlconremote_uniquieid = Lcon_remote['uniqueStr'].iloc[0]
        else:
            targetlconremote_pn = ""
            targetlconremote_qty = ""
            targetlconremote_level = ""
            targetlconremote_uit = ""
            targetlconremote_supplytype = ""
            targetlconremote_state = ""
            targetlconremote_parttype = ""
            targetlconremote_spec = ""
            targetlconremote_uniquieid = ""
        #<Search for specific components in EBOM data (Bracket Assy)
        Bracket_Assy = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == "00001" and
                ("ABA" in "{}".format(item.get("childNameDisplay", "")) and 
                "Bracket Assembly,Sub" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))) or
                ("ACQ" in "{}".format(item.get("childNameDisplay", "")) and
                "Bracket Assembly" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))) and
                ("Wifi" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or 
                "IR" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "SUB" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
            ))
            ])
        if not Bracket_Assy.empty:
            for idx, row in Bracket_Assy.iterrows():
                targetbracketassy_pn = row['childNameDisplay']
                targetbracketassy_qty = row['bomQuantity']
                targetbracketassy_level = row['bomLevel']
                targetbracketassy_uit = row['outData.mr_userItemType']
                targetbracketassy_supplytype = row['supplyType']
                targetbracketassy_state = row['outData.pp_states']
                targetbracketassy_parttype = row['dataType']
                targetbracketassy_spec = row['outData.mr_siteTechnicalSpec']
                targetbracketassy_uniquieid = row['uniqueStr']
        else:
            targetbracketassy_pn = ""
            targetbracketassy_qty = ""
            targetbracketassy_level = ""
            targetbracketassy_uit = ""
            targetbracketassy_supplytype = ""
            targetbracketassy_state = ""
            targetbracketassy_parttype = ""
            targetbracketassy_spec = ""
            targetbracketassy_uniquieid = ""
        #<Search for specific components in EBOM data (Wifi Assy)
        EBT_Subassy = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetbracketassy_uniquieid and
                "EBT" in "{}".format(item.get("childNameDisplay", "")) and 
                "Chassis Assembly,Sub" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Wifi" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or 
                "IR" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "SUB" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not EBT_Subassy.empty:
            for idx, row in EBT_Subassy.iterrows():
                targetebtassy_pn = row['childNameDisplay']
                targetebtassy_qty = row['bomQuantity']
                targetebtassy_level = row['bomLevel']
                targetebtassy_uit = row['outData.mr_userItemType']
                targetebtassy_supplytype = row['supplyType']
                targetebtassy_state = row['outData.pp_states']
                targetebtassy_parttype = row['dataType']
                targetebtassy_spec = row['outData.mr_siteTechnicalSpec']
                targetebtassy_uniquieid = row['uniqueStr']
            targetebtassy_pn =EBT_Subassy['childNameDisplay'].iloc[0]
            targetebtassy_qty =EBT_Subassy['bomQuantity'].iloc[0]
            targetebtassy_level =EBT_Subassy['bomLevel'].iloc[0]
            targetebtassy_uit =EBT_Subassy['outData.mr_userItemType'].iloc[0]
            targetebtassy_supplytype =EBT_Subassy['supplyType'].iloc[0]
            targetebtassy_state =EBT_Subassy['outData.pp_states'].iloc[0]
            targetebtassy_parttype =EBT_Subassy['dataType'].iloc[0]
            targetebtassy_spec =EBT_Subassy['outData.mr_siteTechnicalSpec'].iloc[0]
            targetebtassy_uniquieid =EBT_Subassy['uniqueStr'].iloc[0]
        else:
            targetebtassy_pn = ""
            targetebtassy_qty = ""
            targetebtassy_level = ""
            targetebtassy_uit = ""
            targetebtassy_supplytype = ""
            targetebtassy_state = ""
            targetebtassy_parttype = ""
            targetebtassy_spec = ""
            targetebtassy_uniquieid = ""
        #<Search for specific components in EBOM data (Wifi Assy)
        Wifi_assy = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                (item.get("uniqueStrParent") == targetebtassy_uniquieid and
                "EAT" in "{}".format(item.get("childNameDisplay", "")) and 
                "Module,Wifi Bluetooth Module" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "LGSW" in "{}".format(item.get("outData", {}).get('mr_siteTechnicalSpec', ""))) or
                (item.get("uniqueStrParent") == targetebtassy_uniquieid and
                "EBR" in "{}".format(item.get("childNameDisplay", "")) and 
                "PCB Assembly,Sub" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "CKD" in "{}".format(item.get("outData", {}).get('mr_siteTechnicalSpec', "")))
                ))
            ])
        if not Wifi_assy.empty:
            for idx, row in Wifi_assy.iterrows():
                targetwifiassy_pn = row['childNameDisplay']
                targetwifiassy_qty = row['bomQuantity']
                targetwifiassy_level = row['bomLevel']
                targetwifiassy_uit = row['outData.mr_userItemType']
                targetwifiassy_supplytype = row['supplyType']
                targetwifiassy_state = row['outData.pp_states']
                targetwifiassy_parttype = row['dataType']
                targetwifiassy_spec = row['outData.mr_siteTechnicalSpec']
                targetwifiassy_uniquieid = row['uniqueStr']
            targetwifiassy_pn =Wifi_assy['childNameDisplay'].iloc[0]
            targetwifiassy_qty =Wifi_assy['bomQuantity'].iloc[0]
            targetwifiassy_level =Wifi_assy['bomLevel'].iloc[0]
            targetwifiassy_uit =Wifi_assy['outData.mr_userItemType'].iloc[0]
            targetwifiassy_supplytype =Wifi_assy['supplyType'].iloc[0]
            targetwifiassy_state =Wifi_assy['outData.pp_states'].iloc[0]
            targetwifiassy_parttype =Wifi_assy['dataType'].iloc[0]
            targetwifiassy_spec =Wifi_assy['outData.mr_siteTechnicalSpec'].iloc[0]
            targetwifiassy_uniquieid =Wifi_assy['uniqueStr'].iloc[0]
        else:
            targetwifiassy_pn = ""
            targetwifiassy_qty = ""
            targetwifiassy_level = ""
            targetwifiassy_uit = ""
            targetwifiassy_supplytype = ""
            targetwifiassy_state = ""
            targetwifiassy_parttype = ""
            targetwifiassy_spec = ""
            targetwifiassy_uniquieid = ""
        #<Search for specific components in EBOM data (IR Assy)
        IR_assy = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtassy_uniquieid and
                "EBR" in "{}".format(item.get("childNameDisplay", "")) and 
                "PCB Assembly,IR Key" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "IR" in "{}".format(item.get("outData", {}).get('mr_siteTechnicalSpec', ""))
                ))
            ])
        if not IR_assy.empty:
            for idx, row in IR_assy.iterrows():
                targetirassy_pn = row['childNameDisplay']
                targetirassy_qty = row['bomQuantity']
                targetirassy_level = row['bomLevel']
                targetirassy_uit = row['outData.mr_userItemType']
                targetirassy_supplytype = row['supplyType']
                targetirassy_state = row['outData.pp_states']        
                targetirassy_parttype = row['dataType']
                targetirassy_spec = row['outData.mr_siteTechnicalSpec']
                targetirassy_uniquieid = row['uniqueStr']
            targetirassy_pn = IR_assy['childNameDisplay'].iloc[0]
            targetirassy_qty = IR_assy['bomQuantity'].iloc[0]
            targetirassy_level = IR_assy['bomLevel'].iloc[0]
            targetirassy_uit = IR_assy['outData.mr_userItemType'].iloc[0]
            targetirassy_supplytype = IR_assy['supplyType'].iloc[0]
            targetirassy_state = IR_assy['outData.pp_states'].iloc[0]
            targetirassy_parttype = IR_assy['dataType'].iloc[0]
            targetirassy_spec = IR_assy['outData.mr_siteTechnicalSpec'].iloc[0]
            targetirassy_uniquieid = IR_assy['uniqueStr'].iloc[0]
        else:
            targetirassy_pn = ""
            targetirassy_qty = ""
            targetirassy_level = ""
            targetirassy_uit = ""
            targetirassy_supplytype = ""
            targetirassy_state = ""
            targetirassy_parttype = ""
            targetirassy_spec = ""
            targetirassy_uniquieid = ""
        #<Search for specific components in EBOM data (FFC Assy)
        FFC_assy = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtassy_uniquieid and
                "EAD" in "{}".format(item.get("childNameDisplay", "")) and 
                "Cable,FFC" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Wifi" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or 
                "IR" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not FFC_assy.empty:
            for idx, row in FFC_assy.iterrows():
                targetffcassy_pn = row['childNameDisplay']
                targetffcassy_qty = row['bomQuantity']
                targetffcassy_level = row['bomLevel']
                targetffcassy_uit = row['outData.mr_userItemType']
                targetffcassy_supplytype = row['supplyType']
                targetffcassy_state = row['outData.pp_states']
                targetffcassy_parttype = row['dataType']
                targetffcassy_spec = row['outData.mr_siteTechnicalSpec']
                targetffcassy_uniquieid = row['uniqueStr']
            targetffcassy_pn = FFC_assy['childNameDisplay'].iloc[0]
            targetffcassy_qty = FFC_assy['bomQuantity'].iloc[0]
            targetffcassy_level = FFC_assy['bomLevel'].iloc[0]
            targetffcassy_uit = FFC_assy['outData.mr_userItemType'].iloc[0]
            targetffcassy_supplytype = FFC_assy['supplyType'].iloc[0]
            targetffcassy_state = FFC_assy['outData.pp_states'].iloc[0]
            targetffcassy_parttype = FFC_assy['dataType'].iloc[0]
            targetffcassy_spec = FFC_assy['outData.mr_siteTechnicalSpec'].iloc[0]
            targetffcassy_uniquieid = FFC_assy['uniqueStr'].iloc[0]
        else:
            targetffcassy_pn = ""
            targetffcassy_qty = ""
            targetffcassy_level = ""
            targetffcassy_uit = ""
            targetffcassy_supplytype = ""
            targetffcassy_state = ""
            targetffcassy_parttype = ""
            targetffcassy_spec = ""
            targetffcassy_uniquieid = ""
        #<Search for specific components in EBOM data (Speaker Right)
        Speaker_Right = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == "00001" and
                "EAB" in "{}".format(item.get("childNameDisplay", "")) and 
                "Speaker" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "RIGHT" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", ""))
                ))
            ])
        if not Speaker_Right.empty:
            for idx, row in Speaker_Right.iterrows():
                targetspeakerright_pn = row['childNameDisplay']
                targetspeakerright_qty = row['bomQuantity']
                targetspeakerright_level = row['bomLevel']
                targetspeakerright_uit = row['outData.mr_userItemType']
                targetspeakerright_supplytype = row['supplyType']
                targetspeakerright_state = row['outData.pp_states']
                targetspeakerright_parttype = row['dataType']
                targetspeakerright_spec = row['outData.mr_siteTechnicalSpec']
                targetspeakerright_uniquieid = row['uniqueStr']
            targetspeakerright_pn = Speaker_Right['childNameDisplay'].iloc[0]
            targetspeakerright_qty = Speaker_Right['bomQuantity'].iloc[0]
            targetspeakerright_level = Speaker_Right['bomLevel'].iloc[0]
            targetspeakerright_uit = Speaker_Right['outData.mr_userItemType'].iloc[0]
            targetspeakerright_supplytype = Speaker_Right['supplyType'].iloc[0]
            targetspeakerright_state = Speaker_Right['outData.pp_states'].iloc[0]
            targetspeakerright_parttype = Speaker_Right['dataType'].iloc[0]
            targetspeakerright_spec = Speaker_Right['outData.mr_siteTechnicalSpec'].iloc[0]
            targetspeakerright_uniquieid = Speaker_Right['uniqueStr'].iloc[0]
        else:
            targetspeakerright_pn = ""
            targetspeakerright_qty = ""
            targetspeakerright_level = ""
            targetspeakerright_uit = ""
            targetspeakerright_supplytype = ""
            targetspeakerright_state = ""
            targetspeakerright_parttype = ""
            targetspeakerright_spec = ""
            targetspeakerright_uniquieid = ""
        #<Search for specific components in EBOM data (Speaker Left)
        Speaker_Left = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == "00001" and
                "EAB" in "{}".format(item.get("childNameDisplay", "")) and 
                "Speaker" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "LEFT" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", ""))
                ))
            ])
        if not Speaker_Left.empty:
            for idx, row in Speaker_Left.iterrows():
                targetspeakerleft_pn = row['childNameDisplay']
                targetspeakerleft_qty = row['bomQuantity']
                targetspeakerleft_level = row['bomLevel']
                targetspeakerleft_uit = row['outData.mr_userItemType']
                targetspeakerleft_supplytype = row['supplyType']
                targetspeakerleft_state = row['outData.pp_states']
                targetspeakerleft_parttype = row['dataType']
                targetspeakerleft_spec = row['outData.mr_siteTechnicalSpec']
                targetspeakerleft_uniquieid = row['uniqueStr']
            targetspeakerleft_pn = Speaker_Left['childNameDisplay'].iloc[0]
            targetspeakerleft_qty = Speaker_Left['bomQuantity'].iloc[0]
            targetspeakerleft_level = Speaker_Left['bomLevel'].iloc[0]        
            targetspeakerleft_uit = Speaker_Left['outData.mr_userItemType'].iloc[0]
            targetspeakerleft_supplytype = Speaker_Left['supplyType'].iloc[0]
            targetspeakerleft_state = Speaker_Left['outData.pp_states'].iloc[0]
            targetspeakerleft_parttype = Speaker_Left['dataType'].iloc[0]
            targetspeakerleft_spec = Speaker_Left['outData.mr_siteTechnicalSpec'].iloc[0]
            targetspeakerleft_uniquieid = Speaker_Left['uniqueStr'].iloc[0]
        else:
            targetspeakerleft_pn = ""
            targetspeakerleft_qty = ""
            targetspeakerleft_level = ""
            targetspeakerleft_uit = ""
            targetspeakerleft_supplytype = ""
            targetspeakerleft_state = ""
            targetspeakerleft_parttype = ""
            targetspeakerleft_spec = ""
            targetspeakerleft_uniquieid = ""    
        #<Search for specific components in EBOM data (Speaker Assy)
        Speaker_assy = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == "00001" and
                "EAB" in "{}".format(item.get("childNameDisplay", "")) and 
                "Speaker" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))
                ))
            ])
        if not Speaker_assy.empty:
            for idx, row in Speaker_assy.iterrows():
                targetspeaker_pn = row['childNameDisplay']
                targetspeaker_qty = row['bomQuantity']
                targetspeaker_level = row['bomLevel']
                targetspeaker_uit = row['outData.mr_userItemType']
                targetspeaker_supplytype = row['supplyType']
                targetspeaker_state = row['outData.pp_states']
                targetspeaker_parttype = row['dataType']
                targetspeaker_spec = row['outData.mr_siteTechnicalSpec']
                targetspeaker_uniquieid = row['uniqueStr']
            targetspeaker_pn = Speaker_assy['childNameDisplay'].iloc[0]
            targetspeaker_qty = Speaker_assy['bomQuantity'].iloc[0]
            targetspeaker_level = Speaker_assy['bomLevel'].iloc[0]        
            targetspeaker_uit = Speaker_assy['outData.mr_userItemType'].iloc[0]
            targetspeaker_supplytype = Speaker_assy['supplyType'].iloc[0]
            targetspeaker_state = Speaker_assy['outData.pp_states'].iloc[0]
            targetspeaker_parttype = Speaker_assy['dataType'].iloc[0]
            targetspeaker_spec = Speaker_assy['outData.mr_siteTechnicalSpec'].iloc[0]
            targetspeaker_uniquieid = Speaker_assy['uniqueStr'].iloc[0]
        else:
            targetspeaker_pn = ""
            targetspeaker_qty = ""
            targetspeaker_level = ""
            targetspeaker_uit = ""
            targetspeaker_supplytype = ""
            targetspeaker_state = ""
            targetspeaker_parttype = ""
            targetspeaker_spec = ""
            targetspeaker_uniquieid
        #<Search for specific components in EBOM data (FFC Main)
        FFC_Main = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                "EAD" in "{}".format(item.get("childNameDisplay", "")) and 
                "Cable,FFC" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("68P" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or 
                "CEDS" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "VBY1" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "VX1" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "EPI" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        targets_ffc = []  # tampung semua baris
        if not FFC_Main.empty:
            for _, row in FFC_Main.head(5).iterrows():
                targets_ffc.append({
                    "pn":           row.get("childNameDisplay"),
                    "qty":          row.get("bomQuantity"),
                    "level":        row.get("bomLevel"),
                    "uit":          row.get("outData.mr_userItemType"),
                    "supplytype":   row.get("supplyType"),
                    "state":        row.get("outData.pp_states"),
                    "parttype":     row.get("dataType"),
                    "spec":         row.get("outData.mr_siteTechnicalSpec"),
                    "uniqueid":     row.get("uniqueStr"),
                })
        # contoh akses aman:
        if len(targets_ffc) >= 1:
            targetffcmain1_pn = targets_ffc[0]["pn"]
            targetffcmain1_qty = targets_ffc[0]["qty"]
            targetffcmain1_level = targets_ffc[0]["level"]
            targetffcmain1_uit = targets_ffc[0]["uit"]
            targetffcmain1_supplytype = targets_ffc[0]["supplytype"]
            targetffcmain1_state = targets_ffc[0]["state"]
            targetffcmain1_parttype = targets_ffc[0]["parttype"]
            targetffcmain1_spec = targets_ffc[0]["spec"]
            targetffcmain1_uniquieid = targets_ffc[0]["uniqueid"]
        else:
            targetffcmain1_pn = ""
            targetffcmain1_qty = ""
            targetffcmain1_level = ""
            targetffcmain1_uit = ""
            targetffcmain1_supplytype = ""
            targetffcmain1_state = ""
            targetffcmain1_parttype = ""
            targetffcmain1_spec = ""
            targetffcmain1_uniquieid = ""
        if len(targets_ffc) >= 2:
            targetffcmain2_pn = targets_ffc[1]["pn"]
            targetffcmain2_qty = targets_ffc[1]["qty"]
            targetffcmain2_level = targets_ffc[1]["level"]
            targetffcmain2_uit = targets_ffc[1]["uit"]
            targetffcmain2_supplytype = targets_ffc[1]["supplytype"]
            targetffcmain2_state = targets_ffc[1]["state"]
            targetffcmain2_parttype = targets_ffc[1]["parttype"]
            targetffcmain2_spec = targets_ffc[1]["spec"]
            targetffcmain2_uniquieid = targets_ffc[1]["uniqueid"]
        else:
            targetffcmain2_pn = ""
            targetffcmain2_qty = ""
            targetffcmain2_level = ""
            targetffcmain2_uit = ""
            targetffcmain2_supplytype = ""
            targetffcmain2_state = ""
            targetffcmain2_parttype = ""
            targetffcmain2_spec = ""
            targetffcmain2_uniquieid = ""
        #<Search for specific components in EBOM data (EBT Power Cord)
        EBT_Powercord = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == "00001" and
                "EBT" in "{}".format(item.get("childNameDisplay", "")) and 
                "Chassis Assembly,Sub" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("P_Cord Assy" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or 
                "Power Cord" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "Powercord" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "P_Cord" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not EBT_Powercord.empty:
            for idx, row in EBT_Powercord.iterrows():
                targetebtpowercord_pn = row['childNameDisplay']
                targetebtpowercord_qty = row['bomQuantity']
                targetebtpowercord_level = row['bomLevel']
                targetebtpowercord_uit = row['outData.mr_userItemType']
                targetebtpowercord_supplytype = row['supplyType']
                targetebtpowercord_state = row['outData.pp_states']
                targetebtpowercord_parttype = row['dataType']
                targetebtpowercord_spec = row['outData.mr_siteTechnicalSpec']
                targetebtpowercord_uniquieid = row['uniqueStr']
            targetebtpowercord_pn = EBT_Powercord['childNameDisplay'].iloc[0]
            targetebtpowercord_qty = EBT_Powercord['bomQuantity'].iloc[0]
            targetebtpowercord_level = EBT_Powercord['bomLevel'].iloc[0]        
            targetebtpowercord_uit = EBT_Powercord['outData.mr_userItemType'].iloc[0]
            targetebtpowercord_supplytype = EBT_Powercord['supplyType'].iloc[0]
            targetebtpowercord_state = EBT_Powercord['outData.pp_states'].iloc[0]
            targetebtpowercord_parttype = EBT_Powercord['dataType'].iloc[0]
            targetebtpowercord_spec = EBT_Powercord['outData.mr_siteTechnicalSpec'].iloc[0]
            targetebtpowercord_uniquieid = EBT_Powercord['uniqueStr'].iloc[0]
        else:
            targetebtpowercord_pn = ""
            targetebtpowercord_qty = ""
            targetebtpowercord_level = ""
            targetebtpowercord_uit = ""
            targetebtpowercord_supplytype = ""
            targetebtpowercord_state = ""
            targetebtpowercord_parttype = ""
            targetebtpowercord_spec = ""
            targetebtpowercord_uniquieid = ""
        #<Search for specific components in EBOM data (Power Cord Attach)
        Powercord_attach = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtpowercord_uniquieid and
                "EAD" in "{}".format(item.get("childNameDisplay", "")) and 
                "Power Cord,Attach" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("AT" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Powercord_attach.empty:
            for idx, row in Powercord_attach.iterrows():
                targetpowercordattach_pn = row['childNameDisplay']
                targetpowercordattach_qty = row['bomQuantity']
                targetpowercordattach_level = row['bomLevel']
                targetpowercordattach_uit = row['outData.mr_userItemType']
                targetpowercordattach_supplytype = row['supplyType']
                targetpowercordattach_state = row['outData.pp_states']
                targetpowercordattach_parttype = row['dataType']
                targetpowercordattach_spec = row['outData.mr_siteTechnicalSpec']
                targetpowercordattach_uniquieid = row['uniqueStr']
            targetpowercordattach_pn = Powercord_attach['childNameDisplay'].iloc[0]
            targetpowercordattach_qty = Powercord_attach['bomQuantity'].iloc[0]
            targetpowercordattach_level = Powercord_attach['bomLevel'].iloc[0]        
            targetpowercordattach_uit = Powercord_attach['outData.mr_userItemType'].iloc[0]
            targetpowercordattach_supplytype = Powercord_attach['supplyType'].iloc[0]
            targetpowercordattach_state = Powercord_attach['outData.pp_states'].iloc[0]
            targetpowercordattach_parttype = Powercord_attach['dataType'].iloc[0]
            targetpowercordattach_spec = Powercord_attach['outData.mr_siteTechnicalSpec'].iloc[0]
            targetpowercordattach_uniquieid = Powercord_attach['uniqueStr'].iloc[0]
        else:
            targetpowercordattach_pn = ""
            targetpowercordattach_qty = ""
            targetpowercordattach_level = ""
            targetpowercordattach_uit = ""
            targetpowercordattach_supplytype = ""
            targetpowercordattach_state = ""
            targetpowercordattach_parttype = ""
            targetpowercordattach_spec = ""
            targetpowercordattach_uniquieid = ""
        #<Search for specific components in EBOM data (Power Cord Detach)
        Powercord_detach = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                "EAD" in "{}".format(item.get("childNameDisplay", "")) and 
                "Power Cord,Detach" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("DE" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Powercord_detach.empty:
            for idx, row in Powercord_detach.iterrows():
                targetpowercorddetach_pn = row['childNameDisplay']
                targetpowercorddetach_qty = row['bomQuantity']
                targetpowercorddetach_level = row['bomLevel']
                targetpowercorddetach_uit = row['outData.mr_userItemType']
                targetpowercorddetach_supplytype = row['supplyType']
                targetpowercorddetach_state = row['outData.pp_states']
                targetpowercorddetach_parttype = row['dataType']
                targetpowercorddetach_spec = row['outData.mr_siteTechnicalSpec']
                targetpowercorddetach_uniquieid = row['uniqueStr']
            targetpowercorddetach_pn = Powercord_detach['childNameDisplay'].iloc[0]
            targetpowercorddetach_qty = Powercord_detach['bomQuantity'].iloc[0]
            targetpowercorddetach_level = Powercord_detach['bomLevel'].iloc[0]        
            targetpowercorddetach_uit = Powercord_detach['outData.mr_userItemType'].iloc[0]
            targetpowercorddetach_supplytype = Powercord_detach['supplyType'].iloc[0]
            targetpowercorddetach_state = Powercord_detach['outData.pp_states'].iloc[0]
            targetpowercorddetach_parttype = Powercord_detach['dataType'].iloc[0]
            targetpowercorddetach_spec = Powercord_detach['outData.mr_siteTechnicalSpec'].iloc[0]
            targetpowercorddetach_uniquieid = Powercord_detach['uniqueStr'].iloc[0]
        else:
            targetpowercorddetach_pn = ""
            targetpowercorddetach_qty = ""
            targetpowercorddetach_level = ""
            targetpowercorddetach_uit = ""
            targetpowercorddetach_supplytype = ""
            targetpowercorddetach_state = ""
            targetpowercorddetach_parttype = ""
            targetpowercorddetach_spec = ""
            targetpowercorddetach_uniquieid = ""
        #<Search for specific components in EBOM data (Power Board)
        Power_Board = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == "00001" and
                ("EAY" in "{}".format(item.get("childNameDisplay", "")) or
                "EBR" in "{}".format(item.get("childNameDisplay", ""))) and
                "Power" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("LGP" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Power_Board.empty:
            for idx, row in Power_Board.iterrows():
                targetpowerboard_pn = row['childNameDisplay']
                targetpowerboard_qty = row['bomQuantity']
                targetpowerboard_level = row['bomLevel']
                targetpowerboard_uit = row['outData.mr_userItemType']
                targetpowerboard_supplytype = row['supplyType']
                targetpowerboard_state = row['outData.pp_states']
                targetpowerboard_parttype = row['dataType']
                targetpowerboard_spec = row['outData.mr_siteTechnicalSpec']
                targetpowerboard_uniquieid = row['uniqueStr']
            targetpowerboard_pn = Power_Board['childNameDisplay'].iloc[0]
            targetpowerboard_qty = Power_Board['bomQuantity'].iloc[0]
            targetpowerboard_level = Power_Board['bomLevel'].iloc[0]
            targetpowerboard_uit = Power_Board['outData.mr_userItemType'].iloc[0]
            targetpowerboard_supplytype = Power_Board['supplyType'].iloc[0]
            targetpowerboard_state = Power_Board['outData.pp_states'].iloc[0]
            targetpowerboard_parttype = Power_Board['dataType'].iloc[0]
            targetpowerboard_spec = Power_Board['outData.mr_siteTechnicalSpec'].iloc[0]
            targetpowerboard_uniquieid = Power_Board['uniqueStr'].iloc[0]
        else:
            targetpowerboard_pn = ""
            targetpowerboard_qty = ""
            targetpowerboard_level = ""
            targetpowerboard_uit = ""
            targetpowerboard_supplytype = ""
            targetpowerboard_state = ""
            targetpowerboard_parttype = ""
            targetpowerboard_spec = ""
            targetpowerboard_uniquieid = ""
        #<Search for specific components in EBOM data (EBT Main)
        EBT_Main = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == "00001" and
                "EBT" in "{}".format(item.get("childNameDisplay", "")) and 
                "Chassis Assembly" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("MAIN" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not EBT_Main.empty:
            for idx, row in EBT_Main.iterrows():
                targetebtmain_pn = row['childNameDisplay']
                targetebtmain_qty = row['bomQuantity']
                targetebtmain_level = row['bomLevel']
                targetebtmain_uit = row['outData.mr_userItemType']
                targetebtmain_supplytype = row['supplyType']
                targetebtmain_state = row['outData.pp_states']
                targetebtmain_parttype = row['dataType']
                targetebtmain_spec = row['outData.mr_siteTechnicalSpec']
                targetebtmain_uniquieid = row['uniqueStr']
            targetebtmain_pn = EBT_Main['childNameDisplay'].iloc[0]
            targetebtmain_qty = EBT_Main['bomQuantity'].iloc[0]
            targetebtmain_level = EBT_Main['bomLevel'].iloc[0]
            targetebtmain_uit = EBT_Main['outData.mr_userItemType'].iloc[0]
            targetebtmain_supplytype = EBT_Main['supplyType'].iloc[0]
            targetebtmain_state = EBT_Main['outData.pp_states'].iloc[0]
            targetebtmain_parttype = EBT_Main['dataType'].iloc[0]
            targetebtmain_spec = EBT_Main['outData.mr_siteTechnicalSpec'].iloc[0]
            targetebtmain_uniquieid = EBT_Main['uniqueStr'].iloc[0]
        else:
            targetebtmain_pn = ""
            targetebtmain_qty = ""
            targetebtmain_level = ""
            targetebtmain_uit = ""
            targetebtmain_supplytype = ""
            targetebtmain_state = ""
            targetebtmain_parttype = ""
            targetebtmain_spec = ""
            targetebtmain_uniquieid = ""
        #<Search for specific components in EBOM data (Tuner Case Cover)
        Holder_main = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtmain_uniquieid and
                "MEG" in "{}".format(item.get("childNameDisplay", "")) and 
                "Holder" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Holder" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Holder_main.empty:
            for idx, row in Holder_main.iterrows():
                targetholdermain_pn = row['childNameDisplay']
                targetholdermain_qty = row['bomQuantity']
                targetholdermain_level = row['bomLevel']
                targetholdermain_uit = row['outData.mr_userItemType']
                targetholdermain_supplytype = row['supplyType']
                targetholdermain_state = row['outData.pp_states']
                targetholdermain_parttype = row['dataType']
                targetholdermain_spec = row['outData.mr_siteTechnicalSpec']
                targetholdermain_uniquieid = row['uniqueStr']
            targetholdermain_pn = Holder_main['childNameDisplay'].iloc[0]
            targetholdermain_qty = Holder_main['bomQuantity'].iloc[0]
            targetholdermain_level = Holder_main['bomLevel'].iloc[0]
            targetholdermain_uit = Holder_main['outData.mr_userItemType'].iloc[0]
            targetholdermain_supplytype = Holder_main['supplyType'].iloc[0]
            targetholdermain_state = Holder_main['outData.pp_states'].iloc[0]
            targetholdermain_parttype = Holder_main['dataType'].iloc[0]
            targetholdermain_spec = Holder_main['outData.mr_siteTechnicalSpec'].iloc[0]
            targetholdermain_uniquieid = Holder_main['uniqueStr'].iloc[0]
        else:
            targetholdermain_pn = ""
            targetholdermain_qty = ""
            targetholdermain_level = ""
            targetholdermain_uit = ""
            targetholdermain_supplytype = ""
            targetholdermain_state = ""
            targetholdermain_parttype = ""
            targetholdermain_spec = ""
            targetholdermain_uniquieid = ""
        #<Search for specific components in EBOM data (Tuner Case Cover)
        Tuner_cover = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtmain_uniquieid and
                "EBZ" in "{}".format(item.get("childNameDisplay", "")) and 
                "Part" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Tuner" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Tuner_cover.empty:
            for idx, row in Tuner_cover.iterrows():
                targettunercover_pn = row['childNameDisplay']
                targettunercover_qty = row['bomQuantity']
                targettunercover_level = row['bomLevel']
                targettunercover_uit = row['outData.mr_userItemType']
                targettunercover_supplytype = row['supplyType']
                targettunercover_state = row['outData.pp_states']
                targettunercover_parttype = row['dataType']
                targettunercover_spec = row['outData.mr_siteTechnicalSpec']
                targettunercover_uniquieid = row['uniqueStr']
            targettunercover_pn = Tuner_cover['childNameDisplay'].iloc[0]
            targettunercover_qty = Tuner_cover['bomQuantity'].iloc[0]
            targettunercover_level = Tuner_cover['bomLevel'].iloc[0]
            targettunercover_uit = Tuner_cover['outData.mr_userItemType'].iloc[0]
            targettunercover_supplytype = Tuner_cover['supplyType'].iloc[0]
            targettunercover_state = Tuner_cover['outData.pp_states'].iloc[0]
            targettunercover_parttype = Tuner_cover['dataType'].iloc[0]
            targettunercover_spec = Tuner_cover['outData.mr_siteTechnicalSpec'].iloc[0]
            targettunercover_uniquieid = Tuner_cover['uniqueStr'].iloc[0]
        else:
            targettunercover_pn = ""
            targettunercover_qty = ""
            targettunercover_level = ""
            targettunercover_uit = ""
            targettunercover_supplytype = ""
            targettunercover_state = ""
            targettunercover_parttype = ""
            targettunercover_spec = ""
            targettunercover_uniquieid = ""
        #<Search for specific components in EBOM data (Transparent Tape)
        Transparent_Tape = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtmain_uniquieid and
                "961" in "{}".format(item.get("childNameDisplay", "")) and 
                "Tape,Glass Fiber" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("961" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Transparent_Tape.empty:
            for idx, row in Transparent_Tape.iterrows():
                targettransparenttape_pn = row['childNameDisplay']
                targettransparenttape_qty = row['bomQuantity']
                targettransparenttape_level = row['bomLevel']
                targettransparenttape_uit = row['outData.mr_userItemType']
                targettransparenttape_supplytype = row['supplyType']
                targettransparenttape_state = row['outData.pp_states']
                targettransparenttape_parttype = row['dataType']
                targettransparenttape_spec = row['outData.mr_siteTechnicalSpec']
                targettransparenttape_uniquieid = row['uniqueStr']
        else:
            targettransparenttape_pn = ""
            targettransparenttape_qty = ""
            targettransparenttape_level = ""
            targettransparenttape_uit = ""
            targettransparenttape_supplytype = ""
            targettransparenttape_state = ""
            targettransparenttape_parttype = ""
            targettransparenttape_spec = ""
            targettransparenttape_uniquieid = ""
        #<Search for specific components in EBOM data (Harness Single)
        Harness_Single = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtmain_uniquieid and
                "EAD" in "{}".format(item.get("childNameDisplay", "")) and 
                "Harness,Single" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("SMH" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Harness_Single.empty:
            for idx, row in Harness_Single.iterrows():
                targetharnesssingle_pn = row['childNameDisplay']
                targetharnesssingle_qty = row['bomQuantity']
                targetharnesssingle_level = row['bomLevel']
                targetharnesssingle_uit = row['outData.mr_userItemType']
                targetharnesssingle_supplytype = row['supplyType']
                targetharnesssingle_state = row['outData.pp_states']
                targetharnesssingle_parttype = row['dataType']
                targetharnesssingle_spec = row['outData.mr_siteTechnicalSpec']
                targetharnesssingle_uniquieid = row['uniqueStr']
            targetharnesssingle_pn = Harness_Single['childNameDisplay'].iloc[0]
            targetharnesssingle_qty = Harness_Single['bomQuantity'].iloc[0]
            targetharnesssingle_level = Harness_Single['bomLevel'].iloc[0]
            targetharnesssingle_uit = Harness_Single['outData.mr_userItemType'].iloc[0]
            targetharnesssingle_supplytype = Harness_Single['supplyType'].iloc[0]
            targetharnesssingle_state = Harness_Single['outData.pp_states'].iloc[0]
            targetharnesssingle_parttype = Harness_Single['dataType'].iloc[0]
            targetharnesssingle_spec = Harness_Single['outData.mr_siteTechnicalSpec'].iloc[0]
            targetharnesssingle_uniquieid = Harness_Single['uniqueStr'].iloc[0]
        else:
            targetharnesssingle_pn = ""
            targetharnesssingle_qty = ""
            targetharnesssingle_level = ""
            targetharnesssingle_uit = ""
            targetharnesssingle_supplytype = ""
            targetharnesssingle_state = ""
            targetharnesssingle_parttype = ""
            targetharnesssingle_spec = ""
            targetharnesssingle_uniquieid = ""
        #<Search for specific components in EBOM data (Harness Multi)
        Harness_Multi = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtmain_uniquieid and
                "EAD" in "{}".format(item.get("childNameDisplay", "")) and 
                "Harness,Multi" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("250A1" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Harness_Multi.empty:
            for idx, row in Harness_Multi.iterrows():
                targetharnessmulti_pn = row['childNameDisplay']
                targetharnessmulti_qty = row['bomQuantity']
                targetharnessmulti_level = row['bomLevel']
                targetharnessmulti_uit = row['outData.mr_userItemType']
                targetharnessmulti_supplytype = row['supplyType']
                targetharnessmulti_state = row['outData.pp_states']
                targetharnessmulti_parttype = row['dataType']
                targetharnessmulti_spec = row['outData.mr_siteTechnicalSpec']
                targetharnessmulti_uniquieid = row['uniqueStr']
            targetharnessmulti_pn = Harness_Multi['childNameDisplay'].iloc[0]
            targetharnessmulti_qty = Harness_Multi['bomQuantity'].iloc[0]
            targetharnessmulti_level = Harness_Multi['bomLevel'].iloc[0]
            targetharnessmulti_uit = Harness_Multi['outData.mr_userItemType'].iloc[0]
            targetharnessmulti_supplytype = Harness_Multi['supplyType'].iloc[0]
            targetharnessmulti_state = Harness_Multi['outData.pp_states'].iloc[0]
            targetharnessmulti_parttype = Harness_Multi['dataType'].iloc[0]
            targetharnessmulti_spec = Harness_Multi['outData.mr_siteTechnicalSpec'].iloc[0]
            targetharnessmulti_uniquieid = Harness_Multi['uniqueStr'].iloc[0]
        else:
            targetharnessmulti_pn = ""
            targetharnessmulti_qty = ""
            targetharnessmulti_level = ""
            targetharnessmulti_uit = ""
            targetharnessmulti_supplytype = ""
            targetharnessmulti_state = ""
            targetharnessmulti_parttype = ""
            targetharnessmulti_spec = ""
            targetharnessmulti_uniquieid = ""
        #<Search for specific components in EBOM data (Plate Shield Assy)
        Plate_Shield = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtmain_uniquieid and
                "EBS" in "{}".format(item.get("childNameDisplay", "")) and 
                "Electric Parts Assembly,Main" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Shield" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "Plate" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Plate_Shield.empty:
            for idx, row in Plate_Shield.iterrows():
                targetplateshield_pn = row['childNameDisplay']
                targetplateshield_qty = row['bomQuantity']
                targetplateshield_level = row['bomLevel']
                targetplateshield_uit = row['outData.mr_userItemType']
                targetplateshield_supplytype = row['supplyType']
                targetplateshield_state = row['outData.pp_states']
                targetplateshield_parttype = row['dataType']
                targetplateshield_spec = row['outData.mr_siteTechnicalSpec']
                targetplateshield_uniquieid = row['uniqueStr']
            targetplateshield_pn = Plate_Shield['childNameDisplay'].iloc[0]
            targetplateshield_qty = Plate_Shield['bomQuantity'].iloc[0]
            targetplateshield_level = Plate_Shield['bomLevel'].iloc[0]
            targetplateshield_uit = Plate_Shield['outData.mr_userItemType'].iloc[0]
            targetplateshield_supplytype = Plate_Shield['supplyType'].iloc[0]
            targetplateshield_state = Plate_Shield['outData.pp_states'].iloc[0]
            targetplateshield_parttype = Plate_Shield['dataType'].iloc[0]
            targetplateshield_spec = Plate_Shield['outData.mr_siteTechnicalSpec'].iloc[0]
            targetplateshield_uniquieid = Plate_Shield['uniqueStr'].iloc[0]
        else:
            targetplateshield_pn = ""
            targetplateshield_qty = ""
            targetplateshield_level = ""
            targetplateshield_uit = ""
            targetplateshield_supplytype = ""
            targetplateshield_state = ""
            targetplateshield_parttype = ""
            targetplateshield_spec = ""
            targetplateshield_uniquieid = ""
        #<Search for specific components in EBOM data (Plate Shield)
        Plate_Sink = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetplateshield_uniquieid and
                "MED" in "{}".format(item.get("childNameDisplay", "")) or 
                "MGJ" in "{}".format(item.get("childNameDisplay", ""))
                ))
            ])
        if not Plate_Sink.empty:
            for idx, row in Plate_Sink.iterrows():
                targetplatesink_pn = row['childNameDisplay']
                targetplatesink_qty = row['bomQuantity']
                targetplatesink_level = row['bomLevel']
                targetplatesink_uit = row['outData.mr_userItemType']
                targetplatesink_supplytype = row['supplyType']
                targetplatesink_state = row['outData.pp_states']
                targetplatesink_parttype = row['dataType']
                targetplatesink_spec = row['outData.mr_siteTechnicalSpec']
                targetplatesink_uniquieid = row['uniqueStr']
            targetplatesink_pn = Plate_Sink['childNameDisplay'].iloc[0]
            targetplatesink_qty = Plate_Sink['bomQuantity'].iloc[0]
            targetplatesink_level = Plate_Sink['bomLevel'].iloc[0]
            targetplatesink_uit = Plate_Sink['outData.mr_userItemType'].iloc[0]
            targetplatesink_supplytype = Plate_Sink['supplyType'].iloc[0]
            targetplatesink_state = Plate_Sink['outData.pp_states'].iloc[0]
            targetplatesink_parttype = Plate_Sink['dataType'].iloc[0]
            targetplatesink_spec = Plate_Sink['outData.mr_siteTechnicalSpec'].iloc[0]
            targetplatesink_uniquieid = Plate_Sink['uniqueStr'].iloc[0]
        else:
            targetplatesink_pn = ""
            targetplatesink_qty = ""
            targetplatesink_level = ""
            targetplatesink_uit = ""
            targetplatesink_supplytype = ""
            targetplatesink_state = ""
            targetplatesink_parttype = ""
            targetplatesink_spec = ""
            targetplatesink_uniquieid = ""
        #<Search for specific components in EBOM data (Plate Holder)
        Plate_Holder = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetplateshield_uniquieid and
                "MEG" in "{}".format(item.get("childNameDisplay", "")) and
                "Holder" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))
                ))
            ])
        if not Plate_Holder.empty:
            for idx, row in Plate_Holder.iterrows():
                targetplateholder_pn = row['childNameDisplay']
                targetplateholder_qty = row['bomQuantity']
                targetplateholder_level = row['bomLevel']
                targetplateholder_uit = row['outData.mr_userItemType']
                targetplateholder_supplytype = row['supplyType']
                targetplateholder_state = row['outData.pp_states']
                targetplateholder_parttype = row['dataType']
                targetplateholder_spec = row['outData.mr_siteTechnicalSpec']
                targetplateholder_uniquieid = row['uniqueStr']
            targetplateholder_pn = Plate_Holder['childNameDisplay'].iloc[0]
            targetplateholder_qty = Plate_Holder['bomQuantity'].iloc[0]
            targetplateholder_level = Plate_Holder['bomLevel'].iloc[0]
            targetplateholder_uit = Plate_Holder['outData.mr_userItemType'].iloc[0]
            targetplateholder_supplytype = Plate_Holder['supplyType'].iloc[0]
            targetplateholder_state = Plate_Holder['outData.pp_states'].iloc[0]
            targetplateholder_parttype = Plate_Holder['dataType'].iloc[0]
            targetplateholder_spec = Plate_Holder['outData.mr_siteTechnicalSpec'].iloc[0]
            targetplateholder_uniquieid = Plate_Holder['uniqueStr'].iloc[0]
        else:
            targetplateholder_pn = ""
            targetplateholder_qty = ""
            targetplateholder_level = ""
            targetplateholder_uit = ""
            targetplateholder_supplytype = ""
            targetplateholder_state = ""
            targetplateholder_parttype = ""
            targetplateholder_spec = ""
            targetplateholder_uniquieid = ""
        #<Search for specific components in EBOM data (Sheet Cooper)
        Sheet_Cooper = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetplateshield_uniquieid and
                "RAA" in "{}".format(item.get("childNameDisplay", "")) and
                "Sheet,Copper" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))
                ))
            ])
        if not Sheet_Cooper.empty:
            for idx, row in Sheet_Cooper.iterrows():
                targetsheetcooper_pn = row['childNameDisplay']
                targetsheetcooper_qty = row['bomQuantity']
                targetsheetcooper_level = row['bomLevel']
                targetsheetcooper_uit = row['outData.mr_userItemType']
                targetsheetcooper_supplytype = row['supplyType']
                targetsheetcooper_state = row['outData.pp_states']
                targetsheetcooper_parttype = row['dataType']
                targetsheetcooper_spec = row['outData.mr_siteTechnicalSpec']
                targetsheetcooper_uniquieid = row['uniqueStr']
            targetsheetcooper_pn = Sheet_Cooper['childNameDisplay'].iloc[0]
            targetsheetcooper_qty = Sheet_Cooper['bomQuantity'].iloc[0]
            targetsheetcooper_level = Sheet_Cooper['bomLevel'].iloc[0]
            targetsheetcooper_uit = Sheet_Cooper['outData.mr_userItemType'].iloc[0]
            targetsheetcooper_supplytype = Sheet_Cooper['supplyType'].iloc[0]
            targetsheetcooper_state = Sheet_Cooper['outData.pp_states'].iloc[0]
            targetsheetcooper_parttype = Sheet_Cooper['dataType'].iloc[0]
            targetsheetcooper_spec = Sheet_Cooper['outData.mr_siteTechnicalSpec'].iloc[0]
            targetsheetcooper_uniquieid = Sheet_Cooper['uniqueStr'].iloc[0]
        else:
            targetsheetcooper_pn = ""
            targetsheetcooper_qty = ""
            targetsheetcooper_level = ""
            targetsheetcooper_uit = ""
            targetsheetcooper_supplytype = ""
            targetsheetcooper_state = ""
            targetsheetcooper_parttype = ""
            targetsheetcooper_spec = ""
            targetsheetcooper_uniquieid = ""
        #<Search for specific components in EBOM data (EBR Package)
        EBR_Package = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtmain_uniquieid and
                "EBR" in "{}".format(item.get("childNameDisplay", "")) and 
                "PCB Assembly,Main" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("PAKING" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not EBR_Package.empty:
            for idx, row in EBR_Package.iterrows():
                targetebrpackage_pn = row['childNameDisplay']
                targetebrpackage_qty = row['bomQuantity']
                targetebrpackage_level = row['bomLevel']
                targetebrpackage_uit = row['outData.mr_userItemType']
                targetebrpackage_supplytype = row['supplyType']
                targetebrpackage_state = row['outData.pp_states']
                targetebrpackage_parttype = row['dataType']
                targetebrpackage_spec = row['outData.mr_siteTechnicalSpec']
                targetebrpackage_uniquieid = row['uniqueStr']
            targetebrpackage_pn = EBR_Package['childNameDisplay'].iloc[0]
            targetebrpackage_qty = EBR_Package['bomQuantity'].iloc[0]
            targetebrpackage_level = EBR_Package['bomLevel'].iloc[0]
            targetebrpackage_uit = EBR_Package['outData.mr_userItemType'].iloc[0]
            targetebrpackage_supplytype = EBR_Package['supplyType'].iloc[0]
            targetebrpackage_state = EBR_Package['outData.pp_states'].iloc[0]
            targetebrpackage_parttype = EBR_Package['dataType'].iloc[0]
            targetebrpackage_spec = EBR_Package['outData.mr_siteTechnicalSpec'].iloc[0]
            targetebrpackage_uniquieid = EBR_Package['uniqueStr'].iloc[0]
        else:
            targetebrpackage_pn = ""
            targetebrpackage_qty = ""
            targetebrpackage_level = ""
            targetebrpackage_uit = ""
            targetebrpackage_supplytype = ""
            targetebrpackage_state = ""
            targetebrpackage_parttype = ""
            targetebrpackage_spec = ""
            targetebrpackage_uniquieid = ""
        #<Search for specific components in EBOM data (EBR Package)
        Main_Package = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebrpackage_uniquieid and
                "AGF" in "{}".format(item.get("childNameDisplay", "")) and 
                "Package Assembly" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Package" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Main_Package.empty:
            for idx, row in Main_Package.iterrows():
                targetmainpackage_pn = row['childNameDisplay']
                targetmainpackage_qty = row['bomQuantity']
                targetmainpackage_level = row['bomLevel']
                targetmainpackage_uit = row['outData.mr_userItemType']
                targetmainpackage_supplytype = row['supplyType']
                targetmainpackage_state = row['outData.pp_states']
                targetmainpackage_parttype = row['dataType']
                targetmainpackage_spec = row['outData.mr_siteTechnicalSpec']
                targetmainpackage_uniquieid = row['uniqueStr']
            targetmainpackage_pn = Main_Package['childNameDisplay'].iloc[0]
            targetmainpackage_qty = Main_Package['bomQuantity'].iloc[0]
            targetmainpackage_level = Main_Package['bomLevel'].iloc[0]
            targetmainpackage_uit = Main_Package['outData.mr_userItemType'].iloc[0]
            targetmainpackage_supplytype = Main_Package['supplyType'].iloc[0]
            targetmainpackage_state = Main_Package['outData.pp_states'].iloc[0]
            targetmainpackage_parttype = Main_Package['dataType'].iloc[0]
            targetmainpackage_spec = Main_Package['outData.mr_siteTechnicalSpec'].iloc[0]
            targetmainpackage_uniquieid = Main_Package['uniqueStr'].iloc[0]
        else:
            targetmainpackage_pn = ""
            targetmainpackage_qty = ""
            targetmainpackage_level = ""
            targetmainpackage_uit = ""
            targetmainpackage_supplytype = ""
            targetmainpackage_state = ""
            targetmainpackage_parttype = ""
            targetmainpackage_spec = ""
            targetmainpackage_uniquieid = ""        
        
        is_MRGB9M_model = any(
            "MRGB9M" in item.get("childNameDisplay", "")
            for item in response_data.get("data", [])
        )
        if is_MRGB9M_model:
            #<Search for specific components in EBOM data (EBU Main MRGB9M)
            EBU_Main = pd.json_normalize([
                    item for item in response_data.get("data", [])
                    if (
                        "EBU" in item.get("childNameDisplay", "")
                        and "BPR Total Assembly" in item.get("outData", {}).get("pp_descriptions", "")
                        and "MAIN" in item.get("outData", {}).get("mr_siteTechnicalSpec", "")
                    )
                ])
            if not EBU_Main.empty:
                for idx, row in EBU_Main.iterrows():
                    targetebumain_pn = row['childNameDisplay']
                    targetebumain_qty = row['bomQuantity']
                    targetebumain_level = row['bomLevel']
                    targetebumain_uit = row['outData.mr_userItemType']
                    targetebumain_supplytype = row['supplyType']
                    targetebumain_state = row['outData.pp_states']
                    targetebumain_parttype = row['dataType']
                targetebumain_pn = EBU_Main['childNameDisplay'].iloc[0]
                targetebumain_qty = EBU_Main['bomQuantity'].iloc[0]
                targetebumain_level = EBU_Main['bomLevel'].iloc[0]
                targetebumain_uit = EBU_Main['outData.mr_userItemType'].iloc[0]
                targetebumain_supplytype = EBU_Main['supplyType'].iloc[0]
                targetebumain_state = EBU_Main['outData.pp_states'].iloc[0]
                targetebumain_parttype = EBU_Main['dataType'].iloc[0]
                targetebumain_spec = EBU_Main['outData.mr_siteTechnicalSpec'].iloc[0]
                targetebumain_uniquieid = EBU_Main['uniqueStr'].iloc[0]
            else:
                targetebumain_pn = ""
                targetebumain_qty = ""
                targetebumain_level = ""
                targetebumain_uit = ""
                targetebumain_supplytype = ""
                targetebumain_state = ""
                targetebumain_parttype = ""
                targetebumain_spec = ""
                targetebumain_uniquieid = ""
        else:
            #<Search for specific components in EBOM data (EBU Main)     
            EBU_Main = pd.json_normalize([
                    item for item in response_data.get("data", [])
                    if (
                        item.get("uniqueStrParent") in [
                            targetebtmain_uniquieid,
                            targetebrpackage_uniquieid,
                        ]
                        and "EBU" in item.get("childNameDisplay", "")
                        and "ORP Total Assembly" in item.get("outData", {}).get("pp_descriptions", "")
                        and "MAIN" in item.get("outData", {}).get("mr_siteTechnicalSpec", "")
                    )
                ])
            if not EBU_Main.empty:
                for idx, row in EBU_Main.iterrows():
                    targetebumain_pn = row['childNameDisplay']
                    targetebumain_qty = row['bomQuantity']
                    targetebumain_level = row['bomLevel']
                    targetebumain_uit = row['outData.mr_userItemType']
                    targetebumain_supplytype = row['supplyType']
                    targetebumain_state = row['outData.pp_states']
                    targetebumain_parttype = row['dataType']
                    targetebumain_spec = row['outData.mr_siteTechnicalSpec']
                    targetebumain_uniquieid = row['uniqueStr']
                targetebumain_pn = EBU_Main['childNameDisplay'].iloc[0]
                targetebumain_qty = EBU_Main['bomQuantity'].iloc[0]
                targetebumain_level = EBU_Main['bomLevel'].iloc[0]
                targetebumain_uit = EBU_Main['outData.mr_userItemType'].iloc[0]
                targetebumain_supplytype = EBU_Main['supplyType'].iloc[0]
                targetebumain_state = EBU_Main['outData.pp_states'].iloc[0]
                targetebumain_parttype = EBU_Main['dataType'].iloc[0]
                targetebumain_spec = EBU_Main['outData.mr_siteTechnicalSpec'].iloc[0]
                targetebumain_uniquieid = EBU_Main['uniqueStr'].iloc[0]
            else:
                targetebumain_pn = ""
                targetebumain_qty = ""
                targetebumain_level = ""
                targetebumain_uit = ""
                targetebumain_supplytype = ""
                targetebumain_state = ""
                targetebumain_parttype = ""
                targetebumain_spec = ""
                targetebumain_uniquieid = ""
        #<Search for specific components in EBOM data (EBR Main)
        EBR_Main = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebumain_uniquieid and
                "EBR" in "{}".format(item.get("childNameDisplay", "")) and 
                ("ORP Insert PCB Assembly" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) or
                "BPR Insert PCB Assembly" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))) and
                ("MAIN" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not EBR_Main.empty:
            for idx, row in EBR_Main.iterrows():
                targetebrmain_pn = row['childNameDisplay']
                targetebrmain_qty = row['bomQuantity']
                targetebrmain_level = row['bomLevel']
                targetebrmain_uit = row['outData.mr_userItemType']
                targetebrmain_supplytype = row['supplyType']
                targetebrmain_state = row['outData.pp_states']
                targetebrmain_parttype = row['dataType']
                targetebrmain_spec = row['outData.mr_siteTechnicalSpec']
                targetebrmain_uniquieid = row['uniqueStr']
            targetebrmain_pn = EBR_Main['childNameDisplay'].iloc[0]
            targetebrmain_qty = EBR_Main['bomQuantity'].iloc[0]
            targetebrmain_level = EBR_Main['bomLevel'].iloc[0]
            targetebrmain_uit = EBR_Main['outData.mr_userItemType'].iloc[0]
            targetebrmain_supplytype = EBR_Main['supplyType'].iloc[0]
            targetebrmain_state = EBR_Main['outData.pp_states'].iloc[0]
            targetebrmain_parttype = EBR_Main['dataType'].iloc[0]
            targetebrmain_spec = EBR_Main['outData.mr_siteTechnicalSpec'].iloc[0]
            targetebrmain_uniquieid = EBR_Main['uniqueStr'].iloc[0]
        else:
            targetebrmain_pn = ""
            targetebrmain_qty = ""
            targetebrmain_level = ""
            targetebrmain_uit = ""
            targetebrmain_supplytype = ""
            targetebrmain_state = ""
            targetebrmain_parttype = ""
            targetebrmain_spec = ""
            targetebrmain_uniquieid = ""
        #<Search for specific components in EBOM data (PCB Main)
        PCB_Main = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                # targetebrmain_uniquieid in "{}".format(item.get("uniqueStrParent", "")) and
                "EAX" in "{}".format(item.get("childNameDisplay", "")) and 
                "PCB" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Main" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not PCB_Main.empty:
            for idx, row in PCB_Main.iterrows():
                targetpcbmain_pn = row['childNameDisplay']
                targetpcbmain_qty = row['bomQuantity']
                targetpcbmain_level = row['bomLevel']
                targetpcbmain_uit = row['outData.mr_userItemType']
                targetpcbmain_supplytype = row['supplyType']
                targetpcbmain_state = row['outData.pp_states']
                targetpcbmain_parttype = row['dataType']
                targetpcbmain_spec = row['outData.mr_siteTechnicalSpec']
                targetpcbmain_uniquieid = row['uniqueStr']
            targetpcbmain_pn = PCB_Main['childNameDisplay'].iloc[0]
            targetpcbmain_qty = PCB_Main['bomQuantity'].iloc[0]
            targetpcbmain_level = PCB_Main['bomLevel'].iloc[0]
            targetpcbmain_uit = PCB_Main['outData.mr_userItemType'].iloc[0]
            targetpcbmain_supplytype = PCB_Main['supplyType'].iloc[0]
            targetpcbmain_state = PCB_Main['outData.pp_states'].iloc[0]
            targetpcbmain_parttype = PCB_Main['dataType'].iloc[0]
            targetpcbmain_spec = PCB_Main['outData.mr_siteTechnicalSpec'].iloc[0]
            targetpcbmain_uniquieid = PCB_Main['uniqueStr'].iloc[0]
        else:
            targetpcbmain_pn = ""
            targetpcbmain_qty = ""
            targetpcbmain_level = ""
            targetpcbmain_uit = ""
            targetpcbmain_supplytype = ""
            targetpcbmain_state = ""
            targetpcbmain_parttype = ""
            targetpcbmain_spec = ""
            targetpcbmain_uniquieid = ""
        #<Search for specific components in EBOM data (Wifi Main)
        Wifi_assymain = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                (item.get("uniqueStrParent") == targetebrmain_uniquieid and
                "EAT" in "{}".format(item.get("childNameDisplay", "")) and 
                "Module,Wifi Bluetooth Module" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "LGSW" in "{}".format(item.get("outData", {}).get('mr_siteTechnicalSpec', ""))) or
                (item.get("uniqueStrParent") == targetebrmain_uniquieid and
                "EBR" in "{}".format(item.get("childNameDisplay", "")) and 
                "PCB Assembly,Sub" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "CKD" in "{}".format(item.get("outData", {}).get('mr_siteTechnicalSpec', "")))
                ))
            ])
        if not Wifi_assymain.empty:
            for idx, row in Wifi_assymain.iterrows():
                targetwifiassymain_pn = row['childNameDisplay']
                targetwifiassymain_qty = row['bomQuantity']
                targetwifiassymain_level = row['bomLevel']
                targetwifiassymain_uit = row['outData.mr_userItemType']
                targetwifiassymain_supplytype = row['supplyType']
                targetwifiassymain_state = row['outData.pp_states']
                targetwifiassymain_parttype = row['dataType']
                targetwifiassymain_spec = row['outData.mr_siteTechnicalSpec']
                targetwifiassymain_uniquieid = row['uniqueStr']
            targetwifiassymain_pn = Wifi_assymain['childNameDisplay'].iloc[0]
            targetwifiassymain_qty = Wifi_assymain['bomQuantity'].iloc[0]
            targetwifiassymain_level = Wifi_assymain['bomLevel'].iloc[0]
            targetwifiassymain_uit = Wifi_assymain['outData.mr_userItemType'].iloc[0]
            targetwifiassymain_supplytype = Wifi_assymain['supplyType'].iloc[0]
            targetwifiassymain_state = Wifi_assymain['outData.pp_states'].iloc[0]
            targetwifiassymain_parttype = Wifi_assymain['dataType'].iloc[0]
            targetwifiassymain_spec = Wifi_assymain['outData.mr_siteTechnicalSpec'].iloc[0]
            targetwifiassymain_uniquieid = Wifi_assymain['uniqueStr'].iloc[0]
        else:
            targetwifiassymain_pn = ""
            targetwifiassymain_qty = ""
            targetwifiassymain_level = ""
            targetwifiassymain_uit = ""
            targetwifiassymain_supplytype = ""
            targetwifiassymain_state = ""
            targetwifiassymain_parttype = ""
            targetwifiassymain_spec = ""
            targetwifiassymain_uniquieid = ""    
        #<Search for specific components in EBOM data (EDID)
        EDID = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                "ECC" in "{}".format(item.get("childNameDisplay", "")) and 
                "EDID Check Sum Assembly" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("EDID" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not EDID.empty:
            for idx, row in EDID.iterrows():
                targetedid_pn = row['childNameDisplay']
                targetedid_qty = row['bomQuantity']
                targetedid_level = row['bomLevel']
                targetedid_uit = row['outData.mr_userItemType']
                targetedid_supplytype = row['supplyType']
                targetedid_state = row['outData.pp_states']
                targetedid_parttype = row['dataType']
                targetedid_spec = row['outData.mr_siteTechnicalSpec']
                targetedid_uniquieid = row['uniqueStr']
            targetedid_pn = EDID['childNameDisplay'].iloc[0]
            targetedid_qty = EDID['bomQuantity'].iloc[0]
            targetedid_level = EDID['bomLevel'].iloc[0]
            targetedid_uit = EDID['outData.mr_userItemType'].iloc[0]
            targetedid_supplytype = EDID['supplyType'].iloc[0]
            targetedid_state = EDID['outData.pp_states'].iloc[0]
            targetedid_parttype = EDID['dataType'].iloc[0]
            targetedid_spec = EDID['outData.mr_siteTechnicalSpec'].iloc[0]
            targetedid_uniquieid = EDID['uniqueStr'].iloc[0]
        else:
            targetedid_pn = ""
            targetedid_qty = ""
            targetedid_level = ""
            targetedid_uit = ""
            targetedid_supplytype = ""
            targetedid_state = ""
            targetedid_parttype = ""
            targetedid_spec = ""
            targetedid_uniquieid = ""
        #<Search for specific components in EBOM data (SW Assy)
        SW_Assy = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                "SAB" in "{}".format(item.get("childNameDisplay", "")) and 
                "S/W Package" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("eMMC" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not SW_Assy.empty:
            for idx, row in SW_Assy.iterrows():
                targetswassy_pn = row['childNameDisplay']
                targetswassy_qty = row['bomQuantity']
                targetswassy_level = row['bomLevel']
                targetswassy_uit = row['outData.mr_userItemType']
                targetswassy_supplytype = row['supplyType']
                targetswassy_state = row['outData.pp_states']
                targetswassy_parttype = row['dataType']
                targetswassy_spec = row['outData.mr_siteTechnicalSpec']
                targetswassy_uniquieid = row['uniqueStr']
            targetswassy_pn = SW_Assy['childNameDisplay'].iloc[0]
            targetswassy_qty = SW_Assy['bomQuantity'].iloc[0]
            targetswassy_level = SW_Assy['bomLevel'].iloc[0]
            targetswassy_uit = SW_Assy['outData.mr_userItemType'].iloc[0]
            targetswassy_supplytype = SW_Assy['supplyType'].iloc[0]
            targetswassy_state = SW_Assy['outData.pp_states'].iloc[0]
            targetswassy_parttype = SW_Assy['dataType'].iloc[0]
            targetswassy_spec = SW_Assy['outData.mr_siteTechnicalSpec'].iloc[0]
            targetswassy_uniquieid = SW_Assy['uniqueStr'].iloc[0]
        else:
            targetswassy_pn = ""
            targetswassy_qty = ""
            targetswassy_level = ""
            targetswassy_uit = ""
            targetswassy_supplytype = ""
            targetswassy_state = ""
            targetswassy_parttype = ""
            targetswassy_spec = ""
            targetswassy_uniquieid = ""
        #<Search for specific components in EBOM data (EBU SVC)
        EBU_SVC = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == "00001" and
                "EBU" in "{}".format(item.get("childNameDisplay", "")) and 
                "Mainboard,ORP Total Assembly,SVC" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Main" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not EBU_SVC.empty:
            for idx, row in EBU_SVC.iterrows():
                targetebusvc_pn = row['childNameDisplay']
                targetebusvc_qty = row['bomQuantity']
                targetebusvc_level = row['bomLevel']
                targetebusvc_uit = row['outData.mr_userItemType']
                targetebusvc_supplytype = row['supplyType']
                targetebusvc_state = row['outData.pp_states']
                targetebusvc_parttype = row['dataType']
                targetebusvc_spec = row['outData.mr_siteTechnicalSpec']
                targetebusvc_uniquieid = row['uniqueStr']
            targetebusvc_pn = EBU_SVC['childNameDisplay'].iloc[0]
            targetebusvc_qty = EBU_SVC['bomQuantity'].iloc[0]
            targetebusvc_level = EBU_SVC['bomLevel'].iloc[0]
            targetebusvc_uit = EBU_SVC['outData.mr_userItemType'].iloc[0]
            targetebusvc_supplytype = EBU_SVC['supplyType'].iloc[0]
            targetebusvc_state = EBU_SVC['outData.pp_states'].iloc[0]
            targetebusvc_parttype = EBU_SVC['dataType'].iloc[0]
            targetebusvc_spec = EBU_SVC['outData.mr_siteTechnicalSpec'].iloc[0]
            targetebusvc_uniquieid = EBU_SVC['uniqueStr'].iloc[0]
        else:
            targetebusvc_pn = ""
            targetebusvc_qty = ""
            targetebusvc_level = ""
            targetebusvc_uit = ""
            targetebusvc_supplytype = ""
            targetebusvc_state = ""
            targetebusvc_parttype = ""
            targetebusvc_spec = ""
            targetebusvc_uniquieid = ""
        #<Search for specific components in EBOM data (Tuner Case Cover)
        Tuner_coversvc = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebusvc_uniquieid and
                "EBZ" in "{}".format(item.get("childNameDisplay", "")) and 
                "Part" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Tuner" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Tuner_coversvc.empty:
            for idx, row in Tuner_coversvc.iterrows():
                targettunercoversvc_pn = row['childNameDisplay']
                targettunercoversvc_qty = row['bomQuantity']
                targettunercoversvc_level = row['bomLevel']
                targettunercoversvc_uit = row['outData.mr_userItemType']
                targettunercoversvc_supplytype = row['supplyType']
                targettunercoversvc_state = row['outData.pp_states']
                targettunercoversvc_parttype = row['dataType']
                targettunercoversvc_spec = row['outData.mr_siteTechnicalSpec']
                targettunercoversvc_uniquieid = row['uniqueStr']
            targettunercoversvc_pn = Tuner_coversvc['childNameDisplay'].iloc[0]
            targettunercoversvc_qty = Tuner_coversvc['bomQuantity'].iloc[0]
            targettunercoversvc_level = Tuner_coversvc['bomLevel'].iloc[0]
            targettunercoversvc_uit = Tuner_coversvc['outData.mr_userItemType'].iloc[0]
            targettunercoversvc_supplytype = Tuner_coversvc['supplyType'].iloc[0]
            targettunercoversvc_state = Tuner_coversvc['outData.pp_states'].iloc[0]
            targettunercoversvc_parttype = Tuner_coversvc['dataType'].iloc[0]
            targettunercoversvc_spec = Tuner_coversvc['outData.mr_siteTechnicalSpec'].iloc[0]
            targettunercoversvc_uniquieid = Tuner_coversvc['uniqueStr'].iloc[0]
        else:
            targettunercoversvc_pn = ""
            targettunercoversvc_qty = ""
            targettunercoversvc_level = ""
            targettunercoversvc_uit = ""
            targettunercoversvc_supplytype = ""
            targettunercoversvc_state = ""
            targettunercoversvc_parttype = ""
            targettunercoversvc_spec = ""
            targettunercoversvc_uniquieid = ""
        #<Search for specific components in EBOM data (Tuner Case Cover)
        Holder_svc = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebusvc_uniquieid and
                "MEG" in "{}".format(item.get("childNameDisplay", "")) and 
                "Holder" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Holder" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Holder_svc.empty:
            for idx, row in Holder_svc.iterrows():
                targetholdersvc_pn = row['childNameDisplay']
                targetholdersvc_qty = row['bomQuantity']
                targetholdersvc_level = row['bomLevel']
                targetholdersvc_uit = row['outData.mr_userItemType']
                targetholdersvc_supplytype = row['supplyType']
                targetholdersvc_state = row['outData.pp_states']
                targetholdersvc_parttype = row['dataType']
                targetholdersvc_spec = row['outData.mr_siteTechnicalSpec']
                targetholdersvc_uniquieid = row['uniqueStr']
            targetholdersvc_pn = Holder_svc['childNameDisplay'].iloc[0]
            targetholdersvc_qty = Holder_svc['bomQuantity'].iloc[0]
            targetholdersvc_level = Holder_svc['bomLevel'].iloc[0]
            targetholdersvc_uit = Holder_svc['outData.mr_userItemType'].iloc[0]
            targetholdersvc_supplytype = Holder_svc['supplyType'].iloc[0]
            targetholdersvc_state = Holder_svc['outData.pp_states'].iloc[0]
            targetholdersvc_parttype = Holder_svc['dataType'].iloc[0]
            targetholdersvc_spec = Holder_svc['outData.mr_siteTechnicalSpec'].iloc[0]
            targetholdersvc_uniquieid = Holder_svc['uniqueStr'].iloc[0]
        else:
            targetholdersvc_pn = ""
            targetholdersvc_qty = ""
            targetholdersvc_level = ""
            targetholdersvc_uit = ""
            targetholdersvc_supplytype = ""
            targetholdersvc_state = ""
            targetholdersvc_parttype = ""
            targetholdersvc_spec = ""
            targetholdersvc_uniquieid = ""
        #<Search for specific components in EBOM data (EBR SVC)
        EBR_SVC = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebusvc_uniquieid and
                "EBR" in "{}".format(item.get("childNameDisplay", "")) and 
                "ORP Insert PCB Assembly" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("MAIN" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not EBR_SVC.empty:
            for idx, row in EBR_SVC.iterrows():
                targetebrsvc_pn = row['childNameDisplay']
                targetebrsvc_qty = row['bomQuantity']
                targetebrsvc_level = row['bomLevel']
                targetebrsvc_uit = row['outData.mr_userItemType']
                targetebrsvc_supplytype = row['supplyType'] 
                targetebrsvc_state = row['outData.pp_states']
                targetebrsvc_parttype = row['dataType']
                targetebrsvc_spec = row['outData.mr_siteTechnicalSpec']
                targetebrsvc_uniquieid = row['uniqueStr']
            targetebrsvc_pn = EBR_SVC['childNameDisplay'].iloc[0]
            targetebrsvc_qty = EBR_SVC['bomQuantity'].iloc[0]
            targetebrsvc_level = EBR_SVC['bomLevel'].iloc[0]
            targetebrsvc_uit = EBR_SVC['outData.mr_userItemType'].iloc[0]
            targetebrsvc_supplytype = EBR_SVC['supplyType'].iloc[0]
            targetebrsvc_state = EBR_SVC['outData.pp_states'].iloc[0]
            targetebrsvc_parttype = EBR_SVC['dataType'].iloc[0]
            targetebrsvc_spec = EBR_SVC['outData.mr_siteTechnicalSpec'].iloc[0]
            targetebrsvc_uniquieid = EBR_SVC['uniqueStr'].iloc[0]
        else:
            targetebrsvc_pn = ""
            targetebrsvc_qty = ""
            targetebrsvc_level = ""
            targetebrsvc_uit = ""
            targetebrsvc_supplytype = ""
            targetebrsvc_state = ""
            targetebrsvc_parttype = ""
            targetebrsvc_spec = ""
            targetebrsvc_uniquieid = ""   
        #<Search for specific components in EBOM data (Plate Shield Assy SVC)
        Plate_Shieldsvc = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebusvc_uniquieid and
                "EBS" in "{}".format(item.get("childNameDisplay", "")) and 
                "Electric Parts Assembly,Main" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Shield" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "Plate" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Plate_Shieldsvc.empty:
            for idx, row in Plate_Shieldsvc.iterrows():
                targetplateshieldsvc_pn = row['childNameDisplay']
                targetplateshieldsvc_qty = row['bomQuantity']
                targetplateshieldsvc_level = row['bomLevel']
                targetplateshieldsvc_uit = row['outData.mr_userItemType']
                targetplateshieldsvc_supplytype = row['supplyType']
                targetplateshieldsvc_state = row['outData.pp_states']
                targetplateshieldsvc_parttype = row['dataType']
                targetplateshieldsvc_spec = row['outData.mr_siteTechnicalSpec']
                targetplateshieldsvc_uniquieid = row['uniqueStr']
            targetplateshieldsvc_pn = Plate_Shieldsvc['childNameDisplay'].iloc[0]
            targetplateshieldsvc_qty = Plate_Shieldsvc['bomQuantity'].iloc[0]
            targetplateshieldsvc_level = Plate_Shieldsvc['bomLevel'].iloc[0]
            targetplateshieldsvc_uit = Plate_Shieldsvc['outData.mr_userItemType'].iloc[0]
            targetplateshieldsvc_supplytype = Plate_Shieldsvc['supplyType'].iloc[0]
            targetplateshieldsvc_state = Plate_Shieldsvc['outData.pp_states'].iloc[0]
            targetplateshieldsvc_parttype = Plate_Shieldsvc['dataType'].iloc[0]
            targetplateshieldsvc_spec = Plate_Shieldsvc['outData.mr_siteTechnicalSpec'].iloc[0]
            targetplateshieldsvc_uniquieid = Plate_Shieldsvc['uniqueStr'].iloc[0]
        else:
            targetplateshieldsvc_pn = ""
            targetplateshieldsvc_qty = ""
            targetplateshieldsvc_level = ""
            targetplateshieldsvc_uit = ""
            targetplateshieldsvc_supplytype = ""
            targetplateshieldsvc_state = ""
            targetplateshieldsvc_parttype = ""
            targetplateshieldsvc_spec = ""
            targetplateshieldsvc_uniquieid = ""    
        #<Search for specific components in EBOM data (Wifi SVC)
        Wifi_assysvc = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                targetebrsvc_uniquieid in "{}".format(item.get("uniqueStrParent", "")) and
                "EAT" in "{}".format(item.get("childNameDisplay", "")) and 
                "Module,Wifi Bluetooth Module" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) or
                "LGSW" in "{}".format(item.get("outData", {}).get('mr_siteTechnicalSpec', ""))
                ))
            ])
        if not Wifi_assysvc.empty:
            for idx, row in Wifi_assysvc.iterrows():
                targetwifiassysvc_pn = row['childNameDisplay']
                targetwifiassysvc_qty = row['bomQuantity']
                targetwifiassysvc_level = row['bomLevel']
                targetwifiassysvc_uit = row['outData.mr_userItemType']
                targetwifiassysvc_supplytype = row['supplyType']
                targetwifiassysvc_state = row['outData.pp_states']
                targetwifiassysvc_parttype = row['dataType']
                targetwifiassysvc_spec = row['outData.mr_siteTechnicalSpec']
                targetwifiassysvc_uniquieid = row['uniqueStr']
            targetwifiassysvc_pn = Wifi_assysvc['childNameDisplay'].iloc[0]
            targetwifiassysvc_qty = Wifi_assysvc['bomQuantity'].iloc[0]
            targetwifiassysvc_level = Wifi_assysvc['bomLevel'].iloc[0]
            targetwifiassysvc_uit = Wifi_assysvc['outData.mr_userItemType'].iloc[0]
            targetwifiassysvc_supplytype = Wifi_assysvc['supplyType'].iloc[0]
            targetwifiassysvc_state = Wifi_assysvc['outData.pp_states'].iloc[0]
            targetwifiassysvc_parttype = Wifi_assysvc['dataType'].iloc[0]
            targetwifiassysvc_spec = Wifi_assysvc['outData.mr_siteTechnicalSpec'].iloc[0]
            targetwifiassysvc_uniquieid = Wifi_assysvc['uniqueStr'].iloc[0]
        else:
            targetwifiassysvc_pn = ""
            targetwifiassysvc_qty = ""
            targetwifiassysvc_level = ""
            targetwifiassysvc_uit = ""
            targetwifiassysvc_supplytype = ""
            targetwifiassysvc_state = ""
            targetwifiassysvc_parttype = ""
            targetwifiassysvc_spec = ""
            targetwifiassysvc_uniquieid = ""
        #<Search for specific components in EBOM data (Label)
        Label = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                (item.get("uniqueStrParent") == targetebtmain_uniquieid or
                item.get("uniqueStrParent") == targetebumain_uniquieid or
                item.get("uniqueStrParent") == targetebusvc_uniquieid) and
                "385" in "{}".format(item.get("childNameDisplay", "")) and 
                "Label" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("PRINTING BAR" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Label.empty:
            for idx, row in Label.iterrows():
                targetlabel_pn = row['childNameDisplay']
                targetlabel_qty = row['bomQuantity']
                targetlabel_level = row['bomLevel']
                targetlabel_uit = row['outData.mr_userItemType']
                targetlabel_supplytype = row['supplyType']
                targetlabel_state = row['outData.pp_states']
                targetlabel_parttype = row['dataType']
                targetlabel_spec = row['outData.mr_siteTechnicalSpec']
                targetlabel_uniquieid = row['uniqueStr']
        else:
            targetlabel_pn = ""
            targetlabel_qty = ""
            targetlabel_level = ""
            targetlabel_uit = ""
            targetlabel_supplytype = ""
            targetlabel_state = ""
            targetlabel_parttype = ""
            targetlabel_spec = ""
            targetlabel_uniquieid = ""
        #<Search for specific components in EBOM data (Ribbon)
        Ribbon = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                (item.get("uniqueStrParent") == targetebtmain_uniquieid or
                item.get("uniqueStrParent") == targetebumain_uniquieid or
                item.get("uniqueStrParent") == targetebusvc_uniquieid) and
                "481" in "{}".format(item.get("childNameDisplay", "")) and 
                "Ribbon" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("CUTTING PAPER" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
            ))
            ])
        if not Ribbon.empty:
            for idx, row in Ribbon.iterrows():
                targetribbon_pn = row['childNameDisplay']
                targetribbon_qty = row['bomQuantity']
                targetribbon_level = row['bomLevel']
                targetribbon_uit = row['outData.mr_userItemType']
                targetribbon_supplytype = row['supplyType']
                targetribbon_state = row['outData.pp_states']
                targetribbon_parttype = row['dataType']
                targetribbon_spec = row['outData.mr_siteTechnicalSpec']
                targetribbon_uniquieid = row['uniqueStr']
            targetribbon_pn = Ribbon['childNameDisplay'].iloc[0]
        else:
            targetribbon_pn = ""
            targetribbon_qty = ""
            targetribbon_level = ""
            targetribbon_uit = ""
            targetribbon_supplytype = ""
            targetribbon_state = ""
            targetribbon_parttype = ""
            targetribbon_spec = ""
            targetribbon_uniquieid = ""
        #<Search for specific components in EBOM data (Gasket)
        Gasket = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                (item.get("uniqueStrParent") == "00001" or
                item.get("uniqueStrParent") == targetebtmain_uniquieid) and
                "MDS" in "{}".format(item.get("childNameDisplay", "")) and 
                "Gasket" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))
                ))
            ])
        targets_gasket = [] # tampung semua baris
        if not Gasket.empty:
            for _, row in Gasket.head(5).iterrows():
                targets_gasket.append({
                    "pn":           row.get("childNameDisplay"),
                    "qty":          row.get("bomQuantity"),
                    "level":        row.get("bomLevel"),
                    "uit":          row.get("outData.mr_userItemType"),
                    "supplytype":   row.get("supplyType"),
                    "state":        row.get("outData.pp_states"),
                    "parttype":     row.get("dataType"),
                    "spec":         row.get("outData.mr_siteTechnicalSpec"),
                    "uniqueid":     row.get("uniqueStr"),
                })
        # contoh akses aman:
        if len(targets_gasket) >= 1:
            targetgasket1_pn = targets[0]["pn"]
            targetgasket1_qty = targets[0]["qty"]
            targetgasket1_level = targets[0]["level"]
            targetgasket1_uit = targets[0]["uit"]
            targetgasket1_supplytype = targets[0]["supplytype"]
            targetgasket1_state = targets[0]["state"]
            targetgasket1_parttype = targets[0]["parttype"]
            targetgasket1_spec = targets[0]["spec"]
            targetgasket1_uniquieid = targets[0]["uniqueid"]
        else:
            targetgasket1_pn = ""
            targetgasket1_qty = ""
            targetgasket1_level = ""
            targetgasket1_uit = ""
            targetgasket1_supplytype = ""
            targetgasket1_state = ""
            targetgasket1_parttype = ""
            targetgasket1_spec = ""
            targetgasket1_uniquieid = ""
        if len(targets_gasket) >= 2:
            targetgasket2_pn = targets[1]["pn"]
            targetgasket2_qty = targets[1]["qty"]
            targetgasket2_level = targets[1]["level"]
            targetgasket2_uit = targets[1]["uit"]
            targetgasket2_supplytype = targets[1]["supplytype"]
            targetgasket2_state = targets[1]["state"]
            targetgasket2_parttype = targets[1]["parttype"]
            targetgasket2_spec = targets[1]["spec"]
            targetgasket2_uniquieid = targets[1]["uniqueid"]
        else:   
            targetgasket2_pn = ""
            targetgasket2_qty = ""
            targetgasket2_level = ""
            targetgasket2_uit = ""
            targetgasket2_supplytype = ""
            targetgasket2_state = ""
            targetgasket2_parttype = ""
            targetgasket2_spec = ""
            targetgasket2_uniquieid = ""
        if len(targets_gasket) >= 3:
            targetgasket3_pn = targets[2]["pn"]
            targetgasket3_qty = targets[2]["qty"]
            targetgasket3_level = targets[2]["level"]
            targetgasket3_uit = targets[2]["uit"]
            targetgasket3_supplytype = targets[2]["supplytype"]
            targetgasket3_state = targets[2]["state"]
            targetgasket3_parttype = targets[2]["parttype"]
            targetgasket3_spec = targets[2]["spec"]
            targetgasket3_uniquieid = targets[2]["uniqueid"]
        else:
            targetgasket3_pn = ""
            targetgasket3_qty = ""
            targetgasket3_level = ""
            targetgasket3_uit = ""
            targetgasket3_supplytype = ""
            targetgasket3_state = ""
            targetgasket3_parttype = ""
            targetgasket3_spec = ""
            targetgasket3_uniquieid = ""
        if len(targets_gasket) >= 4:
            targetgasket4_pn = targets[3]["pn"]
            targetgasket4_qty = targets[3]["qty"]
            targetgasket4_level = targets[3]["level"]
            targetgasket4_uit = targets[3]["uit"]
            targetgasket4_supplytype = targets[3]["supplytype"]
            targetgasket4_state = targets[3]["state"]
            targetgasket4_parttype = targets[3]["parttype"]
            targetgasket4_spec = targets[3]["spec"]
            targetgasket4_uniquieid = targets[3]["uniqueid"]
        else:
            targetgasket4_pn = ""
            targetgasket4_qty = ""
            targetgasket4_level = ""
            targetgasket4_uit = ""
            targetgasket4_supplytype = ""
            targetgasket4_state = ""
            targetgasket4_parttype = ""
            targetgasket4_spec = ""
            targetgasket4_uniquieid = ""
        if len(targets_gasket) >= 5:
            targetgasket5_pn = targets[4]["pn"]
            targetgasket5_qty = targets[4]["qty"]
            targetgasket5_level = targets[4]["level"]
            targetgasket5_uit = targets[4]["uit"]
            targetgasket5_supplytype = targets[4]["supplytype"]
            targetgasket5_state = targets[4]["state"]
            targetgasket5_parttype = targets[4]["parttype"]
            targetgasket5_spec = targets[4]["spec"]
            targetgasket5_uniquieid = targets[4]["uniqueid"]
        else:
            targetgasket5_pn = ""
            targetgasket5_qty = ""
            targetgasket5_level = ""
            targetgasket5_uit = ""    
            targetgasket5_supplytype = ""
            targetgasket5_state = ""
            targetgasket5_parttype = ""
            targetgasket5_spec = ""
            targetgasket5_uniquieid = ""
        #<Search for specific components in EBOM data (Tape)
        Tape = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                (item.get("uniqueStrParent") == "00001" or
                item.get("uniqueStrParent") ==targetebtmain_uniquieid) and
                "RAB" in "{}".format(item.get("childNameDisplay", "")) and 
                "Tape" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))
                ))
            ])
        targets_tape = []  # tampung semua baris
        if not Tape.empty:
            for _, row in Gasket.head(5).iterrows():
                targets_tape.append({
                    "pn":           row.get("childNameDisplay"),
                    "qty":          row.get("bomQuantity"),
                    "level":        row.get("bomLevel"),
                    "uit":          row.get("outData.mr_userItemType"),
                    "supplytype":   row.get("supplyType"),
                    "state":        row.get("outData.pp_states"),
                    "parttype":     row.get("dataType"),
                    "spec":         row.get("outData.mr_siteTechnicalSpec"),
                    "uniqueid":     row.get("uniqueStr"),
                })
        # contoh akses aman:
        if len(targets_tape) >= 1:
            targettape1_pn = targets[0]["pn"]
            targettape1_qty = targets[0]["qty"]
            targettape1_level = targets[0]["level"]
            targettape1_uit = targets[0]["uit"]
            targettape1_supplytype = targets[0]["supplytype"]
            targettape1_state = targets[0]["state"]
            targettape1_parttype = targets[0]["parttype"]
            targettape1_spec = targets[0]["spec"]
            targettape1_uniquieid = targets[0]["uniqueid"]
        else:
            targettape1_pn = ""
            targettape1_qty = ""
            targettape1_level = ""
            targettape1_uit = ""
            targettape1_supplytype = ""
            targettape1_state = ""
            targettape1_parttype = ""
            targettape1_spec = ""
            targettape1_uniquieid = ""
        if len(targets_tape) >= 2:
            targettape2_pn = targets[1]["pn"]
            targettape2_qty = targets[1]["qty"]
            targettape2_level = targets[1]["level"]
            targettape2_uit = targets[1]["uit"]
            targettape2_supplytype = targets[1]["supplytype"]
            targettape2_state = targets[1]["state"]
            targettape2_parttype = targets[1]["parttype"]
            targettape2_spec = targets[1]["spec"]
            targettape2_uniquieid = targets[1]["uniqueid"]
        else:
            targettape2_pn = ""
            targettape2_qty = ""
            targettape2_level = ""
            targettape2_uit = ""
            targettape2_supplytype = ""
            targettape2_state = ""
            targettape2_parttype = ""
            targettape2_spec = ""
            targettape2_uniquieid = ""
        if len(targets_tape) >= 3:
            targettape3_pn = targets[2]["pn"]
            targettape3_qty = targets[2]["qty"]
            targettape3_level = targets[2]["level"]
            targettape3_uit = targets[2]["uit"]
            targettape3_supplytype = targets[2]["supplytype"]
            targettape3_state = targets[2]["state"]
            targettape3_parttype = targets[2]["parttype"]
            targettape3_spec = targets[2]["spec"]
            targettape3_uniquieid = targets[2]["uniqueid"]
        else:
            targettape3_pn = ""
            targettape3_qty = ""
            targettape3_level = ""
            targettape3_uit = ""
            targettape3_supplytype = ""
            targettape3_state = ""
            targettape3_parttype = ""
            targettape3_spec = ""
            targettape3_uniquieid = ""
        if len(targets_tape) >= 4:
            targettape4_pn = targets[3]["pn"]
            targettape4_qty = targets[3]["qty"]
            targettape4_level = targets[3]["level"]
            targettape4_uit = targets[3]["uit"]
            targettape4_supplytype = targets[3]["supplytype"]
            targettape4_state = targets[3]["state"]
            targettape4_parttype = targets[3]["parttype"]
            targettape4_spec = targets[3]["spec"]
            targettape4_uniquieid = targets[3]["uniqueid"]
        else:
            targettape4_pn = ""
            targettape4_qty = ""
            targettape4_level = ""
            targettape4_uit = ""
            targettape4_supplytype = ""
            targettape4_state = ""
            targettape4_parttype = ""
            targettape4_spec = ""
            targettape4_uniquieid = ""
        if len(targets_tape) >= 5:
            targettape5_pn = targets[4]["pn"]
            targettape5_qty = targets[4]["qty"]
            targettape5_level = targets[4]["level"]
            targettape5_uit = targets[4]["uit"]
            targettape5_supplytype = targets[4]["supplytype"]
            targettape5_state = targets[4]["state"]
            targettape5_parttype = targets[4]["parttype"]
            targettape5_spec = targets[4]["spec"]
            targettape5_uniquieid = targets[4]["uniqueid"]
        else:
            targettape5_pn = ""
            targettape5_qty = ""
            targettape5_level = ""
            targettape5_uit = ""
            targettape5_supplytype = ""
            targettape5_state = ""
            targettape5_parttype = ""
            targettape5_spec = ""
            targettape5_uniquieid = ""
        #<Search for specific components in EBOM data (Damper)
        Damper = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                (item.get("uniqueStrParent") == "00001" or
                item.get("uniqueStrParent") ==targetebtmain_uniquieid) and
                "MCQ" in "{}".format(item.get("childNameDisplay", "")) and 
                "Damper" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))
                ))
            ])
        targets_damper = []  # tampung semua baris
        if not Damper.empty:
            for _, row in Gasket.head(5).iterrows():
                targets.append({
                    "pn":           row.get("childNameDisplay"),
                    "qty":          row.get("bomQuantity"),
                    "level":        row.get("bomLevel"),
                    "uit":          row.get("outData.mr_userItemType"),
                    "supplytype":   row.get("supplyType"),
                    "state":        row.get("outData.pp_states"),
                    "parttype":     row.get("dataType"),
                    "spec":         row.get("outData.mr_siteTechnicalSpec"),
                    "uniqueid":     row.get("uniqueStr"),
                })
        # contoh akses aman:
        if len(targets_damper) >= 1:
            targetdamper1_pn = targets[0]["pn"]
            targetdamper1_qty = targets[0]["qty"]
            targetdamper1_level = targets[0]["level"]
            targetdamper1_uit = targets[0]["uit"]
            targetdamper1_supplytype = targets[0]["supplytype"]
            targetdamper1_state = targets[0]["state"]
            targetdamper1_parttype = targets[0]["parttype"]
            targetdamper1_spec = targets[0]["spec"]
            targetdamper1_uniquieid = targets[0]["uniqueid"]
        else:
            targetdamper1_pn = ""
            targetdamper1_qty = ""
            targetdamper1_level = ""
            targetdamper1_uit = ""
            targetdamper1_supplytype = ""
            targetdamper1_state = ""
            targetdamper1_parttype = ""
            targetdamper1_spec = ""
            targetdamper1_uniquieid = ""
        if len(targets_damper) >= 2:
            targetdamper2_pn = targets[1]["pn"]
            targetdamper2_qty = targets[1]["qty"]
            targetdamper2_level = targets[1]["level"]
            targetdamper2_uit = targets[1]["uit"]
            targetdamper2_supplytype = targets[1]["supplytype"]
            targetdamper2_state = targets[1]["state"]
            targetdamper2_parttype = targets[1]["parttype"]
            targetdamper2_spec = targets[1]["spec"]
            targetdamper2_uniquieid = targets[1]["uniqueid"]
        else:
            targetdamper2_pn = ""
            targetdamper2_qty = ""
            targetdamper2_level = ""
            targetdamper2_uit = ""
            targetdamper2_supplytype = ""
            targetdamper2_state = ""
            targetdamper2_parttype = ""
            targetdamper2_spec = ""
            targetdamper2_uniquieid = ""
        if len(targets_damper) >= 3:
            targetdamper3_pn = targets[2]["pn"]
            targetdamper3_qty = targets[2]["qty"]
            targetdamper3_level = targets[2]["level"]
            targetdamper3_uit = targets[2]["uit"]
            targetdamper3_supplytype = targets[2]["supplytype"]
            targetdamper3_state = targets[2]["state"]
            targetdamper3_parttype = targets[2]["parttype"]
            targetdamper3_spec = targets[2]["spec"]
            targetdamper3_uniquieid = targets[2]["uniqueid"]
        else:
            targetdamper3_pn = ""
            targetdamper3_qty = ""
            targetdamper3_level = ""
            targetdamper3_uit = ""
            targetdamper3_supplytype = ""
            targetdamper3_state = ""
            targetdamper3_parttype = ""
            targetdamper3_spec = ""
            targetdamper3_uniquieid = ""
        if len(targets_damper) >= 4:
            targetdamper4_pn = targets[3]["pn"]
            targetdamper4_qty = targets[3]["qty"]
            targetdamper4_level = targets[3]["level"]
            targetdamper4_uit = targets[3]["uit"]
            targetdamper4_supplytype = targets[3]["supplytype"]
            targetdamper4_state = targets[3]["state"]
            targetdamper4_parttype = targets[3]["parttype"]
            targetdamper4_spec = targets[3]["spec"]
            targetdamper4_uniquieid = targets[3]["uniqueid"]
        else:
            targetdamper4_pn = ""
            targetdamper4_qty = ""
            targetdamper4_level = ""
            targetdamper4_uit = ""
            targetdamper4_supplytype = ""
            targetdamper4_state = ""
            targetdamper4_parttype = ""
            targetdamper4_spec = ""
            targetdamper4_uniquieid = ""
        if len(targets_damper) >= 5:
            targetdamper5_pn = targets[4]["pn"]
            targetdamper5_qty = targets[4]["qty"]
            targetdamper5_level = targets[4]["level"]
            targetdamper5_uit = targets[4]["uit"]
            targetdamper5_supplytype = targets[4]["supplytype"]
            targetdamper5_state = targets[4]["state"]
            targetdamper5_parttype = targets[4]["parttype"]
            targetdamper5_spec = targets[4]["spec"]
            targetdamper5_uniquieid = targets[4]["uniqueid"]
        else:
            targetdamper5_pn = ""
            targetdamper5_qty = ""
            targetdamper5_level = ""
            targetdamper5_uit = ""
            targetdamper5_supplytype = ""
            targetdamper5_state = ""
            targetdamper5_parttype = ""
            targetdamper5_spec = ""
            targetdamper5_uniquieid = ""
                
        all_hwpart = pd.concat([
            Accesory, Ferrit_core, MR_battery, MR_remote, Lcon_battery, Lcon_remote, 
            Bracket_Assy, EBT_Subassy, Wifi_assy, IR_assy, FFC_assy, Speaker_Right, 
            Speaker_Left, Speaker_assy, FFC_Main, EBT_Powercord, Powercord_attach, 
            Powercord_detach, Power_Board, EBT_Main, Holder_main, Tuner_cover, Transparent_Tape, 
            Harness_Single, Harness_Multi, Plate_Shield, Plate_Sink, Plate_Holder, Sheet_Cooper,
            EBR_Package, Main_Package, EBU_Main, EBR_Main, PCB_Main, Wifi_assymain, EDID, SW_Assy, 
            EBU_SVC, Tuner_coversvc, Holder_svc, EBR_SVC, Plate_Shieldsvc, Wifi_assysvc, 
            Label, Ribbon, Gasket, Tape, Damper
            ], ignore_index=True)
        all_hwpart.to_json("json/1_target_hwpart.json", orient="records", indent=4)
        print("Target Part List saved to 1_target_hwpart.json")
        data = [
            {
                "Category": "EBT Main",
                "Part No": targetebtmain_pn, 
                "Qty": targetebtmain_qty, 
                "Supply Type": targetebtmain_supplytype, 
                "UIT": targetebtmain_uit, 
                "Spec": targetebtmain_spec,
            },
            {
                "Category": "EBT Sub",
                "Part No": targetebtassy_pn, 
                "Qty": targetebtassy_qty, 
                "Supply Type": targetebtassy_supplytype, 
                "UIT": targetebtassy_uit, 
                "Spec": targetebtassy_spec,
            },
            {
                "Category": "EBU Main",
                "Part No": targetebumain_pn, 
                "Qty": targetebumain_qty, 
                "Supply Type": targetebumain_supplytype, 
                "UIT": targetebumain_uit, 
                "Spec": targetebumain_spec,
            },
            {
                "Category": "EBR Main",
                "Part No": targetebrmain_pn, 
                "Qty": targetebrmain_qty, 
                "Supply Type": targetebrmain_supplytype, 
                "UIT": targetebrmain_uit, 
                "Spec": targetebrmain_spec,
            },
            {
                "Category": "SW Assy",
                "Part No": targetswassy_pn, 
                "Qty": targetswassy_qty, 
                "Supply Type": targetswassy_supplytype, 
                "UIT": targetswassy_uit, 
                "Spec": targetswassy_spec,
            },
            {
                "Category": "EDID Check Sum Assembly",
                "Part No": targetedid_pn, 
                "Qty": targetedid_qty, 
                "Supply Type": targetedid_supplytype, 
                "UIT": targetedid_uit, 
                "Spec": targetedid_spec,
            },
            {
                "Category": "Plate Shield Assy",
                "Part No": targetplateshield_pn, 
                "Qty": targetplateshield_qty, 
                "Supply Type": targetplateshield_supplytype, 
                "UIT": targetplateshield_uit, 
                "Spec": targetplateshield_spec,
            },
            {
                "Category": "Shield Plate",
                "Part No": targetplatesink_pn, 
                "Qty": targetplatesink_qty, 
                "Supply Type": targetplatesink_supplytype, 
                "UIT": targetplatesink_uit, 
                "Spec": targetplatesink_spec,
            },
            {
                "Category": "Plate Holder",
                "Part No": targetplateholder_pn, 
                "Qty": targetplateholder_qty, 
                "Supply Type": targetplateholder_supplytype, 
                "UIT": targetplateholder_uit, 
                "Spec": targetplateholder_spec,
            },
            {
                "Category": "Sheet Cooper",
                "Part No": targetsheetcooper_pn, 
                "Qty": targetsheetcooper_qty, 
                "Supply Type": targetsheetcooper_supplytype, 
                "UIT": targetsheetcooper_uit, 
                "Spec": targetsheetcooper_spec,
            },
            {
                "Category": "SKD Main Package",
                "Part No": targetmainpackage_pn, 
                "Qty": targetmainpackage_qty, 
                "Supply Type": targetmainpackage_supplytype, 
                "UIT": targetmainpackage_uit, 
                "Spec": targetmainpackage_spec,
            },
            {
                "Category": "PCB",
                "Part No": targetpcbmain_pn, 
                "Qty": targetpcbmain_qty, 
                "Supply Type": targetpcbmain_supplytype, 
                "UIT": targetpcbmain_uit, 
                "Spec": targetpcbmain_spec,
            },
            {
                "Category": "EBU SVC",
                "Part No": targetebusvc_pn, 
                "Qty": targetebusvc_qty, 
                "Supply Type": targetebusvc_supplytype, 
                "UIT": targetebusvc_uit, 
                "Spec": targetebusvc_spec,
            },
            {
                "Category": "EBR SVC",
                "Part No": targetebrsvc_pn, 
                "Qty": targetebrsvc_qty, 
                "Supply Type": targetebrsvc_supplytype, 
                "UIT": targetebrsvc_uit, 
                "Spec": targetebrsvc_spec,
            },
            {
                "Category": "Plate Shield SVC",
                "Part No": targetplateshieldsvc_pn, 
                "Qty": targetplateshieldsvc_qty, 
                "Supply Type": targetplateshieldsvc_supplytype, 
                "UIT": targetplateshieldsvc_uit, 
                "Spec": targetplateshieldsvc_spec,
            },
            {
                "Category": "Wifi Assy SVC",
                "Part No": targetwifiassysvc_pn, 
                "Qty": targetwifiassysvc_qty, 
                "Supply Type": targetwifiassysvc_supplytype, 
                "UIT": targetwifiassysvc_uit, 
                "Spec": targetwifiassysvc_spec,
            },
            {
                "Category": "Speaker Right",
                "Part No": targetspeakerright_pn, 
                "Qty": targetspeakerright_qty, 
                "Supply Type": targetspeakerright_supplytype, 
                "UIT": targetspeakerright_uit, 
                "Spec": targetspeakerright_spec,
            },
            {
                "Category": "Speaker Left",
                "Part No": targetspeakerleft_pn, 
                "Qty": targetspeakerleft_qty, 
                "Supply Type": targetspeakerleft_supplytype, 
                "UIT": targetspeakerleft_uit, 
                "Spec": targetspeakerleft_spec,
            },
            {
                "Category": "SPK Assy",
                "Part No": targetspeaker_pn, 
                "Qty": targetspeaker_qty, 
                "Supply Type": targetspeaker_supplytype, 
                "UIT": targetspeaker_uit, 
                "Spec": targetspeaker_spec,
            },
            {
                "Category": "Power Board",
                "Part No": targetpowerboard_pn, 
                "Qty": targetpowerboard_qty, 
                "Supply Type": targetpowerboard_supplytype, 
                "UIT": targetpowerboard_uit, 
                "Spec": targetpowerboard_spec,
            },
            {
                "Category": "EBT Power Cord",
                "Part No": targetebtpowercord_pn, 
                "Qty": targetebtpowercord_qty, 
                "Supply Type": targetebtpowercord_supplytype, 
                "UIT": targetebtpowercord_uit, 
                "Spec": targetebtpowercord_spec,
            },
            {
                "Category": "Power Cord Attach",
                "Part No": targetpowercordattach_pn, 
                "Qty": targetpowercordattach_qty, 
                "Supply Type": targetpowercordattach_supplytype, 
                "UIT": targetpowercordattach_uit, 
                "Spec": targetpowercordattach_spec,
            },
            {
                "Category": "Power Cord Detach",
                "Part No": targetpowercorddetach_pn, 
                "Qty": targetpowercorddetach_qty, 
                "Supply Type": targetpowercorddetach_supplytype, 
                "UIT": targetpowercorddetach_uit, 
                "Spec": targetpowercorddetach_spec,
            },
            {
                "Category": "Cable FFC Main 1",
                "Part No": targetffcmain1_pn, 
                "Qty": targetffcmain1_qty, 
                "Supply Type": targetffcmain1_supplytype, 
                "UIT": targetffcmain1_uit, 
                "Spec": targetffcmain1_spec,
            },
            {
                "Category": "Cable FFC Main 2",
                "Part No": targetffcmain2_pn, 
                "Qty": targetffcmain2_qty, 
                "Supply Type": targetffcmain2_supplytype, 
                "UIT": targetffcmain2_uit, 
                "Spec": targetffcmain2_spec,
            },
            {
                "Category": "Cable FFC Sub Assy",
                "Part No": targetffcassy_pn, 
                "Qty": targetffcassy_qty, 
                "Supply Type": targetffcassy_supplytype, 
                "UIT": targetffcassy_uit, 
                "Spec": targetffcassy_spec,
            },
            {
                "Category": "Harness Single",
                "Part No": targetharnesssingle_pn, 
                "Qty": targetharnesssingle_qty, 
                "Supply Type": targetharnesssingle_supplytype, 
                "UIT": targetharnesssingle_uit, 
                "Spec": targetharnesssingle_spec,
            },
            {
                "Category": "Harness Multi",
                "Part No": targetharnessmulti_pn, 
                "Qty": targetharnessmulti_qty, 
                "Supply Type": targetharnessmulti_supplytype, 
                "UIT": targetharnessmulti_uit, 
                "Spec": targetharnessmulti_spec,
            },
            {
                "Category": "IR Assy",
                "Part No": targetirassy_pn, 
                "Qty": targetirassy_qty, 
                "Supply Type": targetirassy_supplytype, 
                "UIT": targetirassy_uit, 
                "Spec": targetirassy_spec,
            },
            {
                "Category": "Wifi Assy",
                "Part No": targetwifiassy_pn, 
                "Qty": targetwifiassy_qty, 
                "Supply Type": targetwifiassy_supplytype, 
                "UIT": targetwifiassy_uit, 
                "Spec": targetwifiassy_spec,
            },
            {
                "Category": "Wifi Assy Main",
                "Part No": targetwifiassymain_pn, 
                "Qty": targetwifiassymain_qty, 
                "Supply Type": targetwifiassymain_supplytype, 
                "UIT": targetwifiassymain_uit, 
                "Spec": targetwifiassymain_spec,
            },
            {
                "Category": "MR Remote",
                "Part No": targetremote_pn, 
                "Qty": targetremote_qty, 
                "Supply Type": targetremote_supplytype, 
                "UIT": targetremote_uit, 
                "Spec": targetremote_spec,
            },
            {
                "Category": "L-Con Remote",
                "Part No": targetlconremote_pn, 
                "Qty": targetlconremote_qty, 
                "Supply Type": targetlconremote_supplytype, 
                "UIT": targetlconremote_uit, 
                "Spec": targetlconremote_spec,
            },
            {
                "Category": "MR Battery",
                "Part No": targetbattery_pn, 
                "Qty": targetbattery_qty, 
                "Supply Type": targetbattery_supplytype, 
                "UIT": targetbattery_uit, 
                "Spec": targetbattery_spec,
            },
            {
                "Category": "L-Con Battery",
                "Part No": targetlconbattery_pn, 
                "Qty": targetlconbattery_qty, 
                "Supply Type": targetlconbattery_supplytype, 
                "UIT": targetlconbattery_uit, 
                "Spec": targetlconbattery_spec,
            },
            {
                "Category": "Ferrit Core",
                "Part No": targetferritcore_pn, 
                "Qty": targetferritcore_qty, 
                "Supply Type": targetferritcore_supplytype, 
                "UIT": targetferritcore_uit, 
                "Spec": targetferritcore_spec,
            },
            {
                "Category": "Tuner Cover",
                "Part No": targettunercover_pn, 
                "Qty": targettunercover_qty, 
                "Supply Type": targettunercover_supplytype, 
                "UIT": targettunercover_uit, 
                "Spec": targettunercover_spec,
            },
            {
                "Category": "Tuner Cover SVC",
                "Part No": targettunercoversvc_pn, 
                "Qty": targettunercoversvc_qty, 
                "Supply Type": targettunercoversvc_supplytype, 
                "UIT": targettunercoversvc_uit, 
                "Spec": targettunercoversvc_spec,
            },
            {
                "Category": "Holder",
                "Part No": targetholdermain_pn, 
                "Qty": targetholdermain_qty, 
                "Supply Type": targetholdermain_supplytype, 
                "UIT": targetholdermain_uit, 
                "Spec": targetholdermain_spec,
            },
            {
                "Category": "Holder SVC",
                "Part No": targetholdersvc_pn, 
                "Qty": targetholdersvc_qty, 
                "Supply Type": targetholdersvc_supplytype, 
                "UIT": targetholdersvc_uit, 
                "Spec": targetholdersvc_spec,
            },
            {
                "Category": "Tape",
                "Part No": targettape1_pn, 
                "Qty": targettape1_qty, 
                "Supply Type": targettape1_supplytype, 
                "UIT": targettape1_uit, 
                "Spec": targettape1_spec,
            },
            {
                "Category": "Tape",
                "Part No": targettape2_pn, 
                "Qty": targettape2_qty, 
                "Supply Type": targettape2_supplytype, 
                "UIT": targettape2_uit, 
                "Spec": targettape2_spec,
            },
            {
                "Category": "Tape",
                "Part No": targettape3_pn, 
                "Qty": targettape3_qty, 
                "Supply Type": targettape3_supplytype, 
                "UIT": targettape3_uit, 
                "Spec": targettape3_spec,
            },
            {
                "Category": "Tape",
                "Part No": targettape4_pn, 
                "Qty": targettape4_qty, 
                "Supply Type": targettape4_supplytype, 
                "UIT": targettape4_uit, 
                "Spec": targettape4_spec,
            },
            {
                "Category": "Tape",
                "Part No": targettape5_pn, 
                "Qty": targettape5_qty, 
                "Supply Type": targettape5_supplytype, 
                "UIT": targettape5_uit, 
                "Spec": targettape5_spec,
            },
            {
                "Category": "Gasket",
                "Part No": targetgasket1_pn, 
                "Qty": targetgasket1_qty, 
                "Supply Type": targetgasket1_supplytype, 
                "UIT": targetgasket1_uit, 
                "Spec": targetgasket1_spec,
            },
            {
                "Category": "Gasket",
                "Part No": targetgasket2_pn, 
                "Qty": targetgasket2_qty, 
                "Supply Type": targetgasket2_supplytype, 
                "UIT": targetgasket2_uit, 
                "Spec": targetgasket2_spec,
            },
            {
                "Category": "Gasket",
                "Part No": targetgasket3_pn, 
                "Qty": targetgasket3_qty, 
                "Supply Type": targetgasket3_supplytype, 
                "UIT": targetgasket3_uit, 
                "Spec": targetgasket3_spec,
            },
            {
                "Category": "Gasket",
                "Part No": targetgasket4_pn, 
                "Qty": targetgasket4_qty, 
                "Supply Type": targetgasket4_supplytype, 
                "UIT": targetgasket4_uit, 
                "Spec": targetgasket4_spec,
            },
            {
                "Category": "Gasket",
                "Part No": targetgasket5_pn, 
                "Qty": targetgasket5_qty, 
                "Supply Type": targetgasket5_supplytype, 
                "UIT": targetgasket5_uit, 
                "Spec": targetgasket5_spec,
            },
            {
                "Category": "Damper",
                "Part No": targetdamper1_pn, 
                "Qty": targetdamper1_qty, 
                "Supply Type": targetdamper1_supplytype, 
                "UIT": targetdamper1_uit, 
                "Spec": targetdamper1_spec,
            },
            {
                "Category": "Damper",
                "Part No": targetdamper2_pn, 
                "Qty": targetdamper2_qty, 
                "Supply Type": targetdamper2_supplytype, 
                "UIT": targetdamper2_uit, 
                "Spec": targetdamper2_spec,
            },
            {
                "Category": "Damper",
                "Part No": targetdamper3_pn, 
                "Qty": targetdamper3_qty, 
                "Supply Type": targetdamper3_supplytype, 
                "UIT": targetdamper3_uit, 
                "Spec": targetdamper3_spec,
            },
            {
                "Category": "Damper",
                "Part No": targetdamper4_pn, 
                "Qty": targetdamper4_qty, 
                "Supply Type": targetdamper4_supplytype, 
                "UIT": targetdamper4_uit, 
                "Spec": targetdamper4_spec,
            },
            {
                "Category": "Damper",
                "Part No": targetdamper5_pn, 
                "Qty": targetdamper5_qty, 
                "Supply Type": targetdamper5_supplytype, 
                "UIT": targetdamper5_uit, 
                "Spec": targetdamper5_spec,
            },
        ]
        with open( JSON_DIR / "2_target_part.json", "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )
        
        part_status = [
            {
                "Category": "EBT Main",
                "Part No": targetebtmain_pn,
                "Qty": targetebtmain_qty,
                "Status": targetebtmain_state,
            },
            {
                "Category": "EBT Sub",
                "Part No": targetebtassy_pn,
                "Qty": targetebtassy_qty,
                "Status": targetebtassy_state,
            },
            {
                "Category": "EBU Main",
                "Part No": targetebumain_pn,
                "Qty": targetebumain_qty,
                "Status": targetebumain_state,
            },
            {
                "Category": "EBR Main",
                "Part No": targetebrmain_pn,
                "Qty": targetebrmain_qty,
                "Status": targetebrmain_state,
            },
            {
                "Category": "SW Assy",
                "Part No": targetswassy_pn,
                "Qty": targetswassy_qty,
                "Status": targetswassy_state,
            },
            {
                "Category": "EDID",
                "Part No": targetedid_pn,
                "Qty": targetedid_qty,
                "Status": targetedid_state,
            },
            {
                "Category": "Plateshield Assy",
                "Part No": targetplateshield_pn,
                "Qty": targetplateshield_qty,
                "Status": targetplateshield_state,
            },
            {
                "Category": "Shield Plate Assy",
                "Part No": targetplatesink_pn,
                "Qty": targetplatesink_qty,
                "Status": targetplatesink_state,
            },
            {
                "Category": "Plate Holder",
                "Part No": targetplateholder_pn,
                "Qty": targetplateholder_qty,
                "Status": targetplateholder_state,
            },
            {
                "Category": "Sheet Cooper",
                "Part No": targetsheetcooper_pn,
                "Qty": targetsheetcooper_qty,
                "Status": targetsheetcooper_state,
            },
            {
                "Category": "SKD Main Package",
                "Part No": targetmainpackage_pn,
                "Qty": targetmainpackage_qty,
                "Status": targetmainpackage_state,
            },
            {
                "Category": "PCB Main",
                "Part No": targetpcbmain_pn,
                "Qty": targetpcbmain_qty,
                "Status": targetpcbmain_state,
            },
            {
                "Category": "EBU SVC",
                "Part No": targetebusvc_pn,
                "Qty": targetebusvc_qty,
                "Status": targetebusvc_state,
            },
            {
                "Category": "EBR SVC",
                "Part No": targetebrsvc_pn,
                "Qty": targetebrsvc_qty,
                "Status": targetebrsvc_state,
            },
            {
                "Category": "Plateshield SVC",
                "Part No": targetplateshieldsvc_pn,
                "Qty": targetplateshieldsvc_qty,
                "Status": targetplateshieldsvc_state,
            },
            {
                "Category": "Wifi Assy SVC",
                "Part No": targetwifiassysvc_pn,
                "Qty": targetwifiassysvc_qty,
                "Status": targetwifiassysvc_state,
            },
            {
                "Category": "Speaker Right",
                "Part No": targetspeakerright_pn,
                "Qty": targetspeakerright_qty,
                "Status": targetspeakerright_state,
            },
            {
                "Category": "Speaker Left",
                "Part No": targetspeakerleft_pn,
                "Qty": targetspeakerleft_qty,
                "Status": targetspeakerleft_state,
            },
            {
                "Category": "Speaker Assy",
                "Part No": targetspeaker_pn,
                "Qty": targetspeaker_qty,
                "Status": targetspeaker_state,
            },
            {
                "Category": "Power Board",
                "Part No": targetpowerboard_pn,
                "Qty": targetpowerboard_qty,
                "Status": targetpowerboard_state,
            },
            {
                "Category": "EBT Power Cord",
                "Part No": targetebtpowercord_pn,
                "Qty": targetebtpowercord_qty,
                "Status": targetebtpowercord_state,
            },
            {
                "Category": "Power Cord Attach",
                "Part No": targetpowercordattach_pn,
                "Qty": targetpowercordattach_qty,
                "Status": targetpowercordattach_state,
            },
            {
                "Category": "Power Cord Detach",
                "Part No": targetpowercorddetach_pn,
                "Qty": targetpowercorddetach_qty,
                "Status": targetpowercorddetach_state,
            },
            {
                "Category": "Cable FFC Main 1",
                "Part No": targetffcmain1_pn,
                "Qty": targetffcmain1_qty,
                "Status": targetffcmain1_state,
            },
            {
                "Category": "Cable FFC Main 2",
                "Part No": targetffcmain2_pn,
                "Qty": targetffcmain2_qty,
                "Status": targetffcmain2_state,
            },
            {
                "Category": "Cable FFC Sub Assy",
                "Part No": targetffcassy_pn,
                "Qty": targetffcassy_qty,
                "Status": targetffcassy_state,
            },
            {
                "Category": "Harness Single",
                "Part No": targetharnesssingle_pn,
                "Qty": targetharnesssingle_qty,
                "Status": targetharnesssingle_state,
            },
            {
                "Category": "Harness Multi",
                "Part No": targetharnessmulti_pn,
                "Qty": targetharnessmulti_qty,
                "Status": targetharnessmulti_state,
            },
            {
                "Category": "IR Assy",
                "Part No": targetirassy_pn,
                "Qty": targetirassy_qty,
                "Status": targetirassy_state,
            },
            {
                "Category": "Wifi Assy",
                "Part No": targetwifiassy_pn,
                "Qty": targetwifiassy_qty,
                "Status": targetwifiassy_state,
            },
            {
                "Category": "Wifi Assy Main",
                "Part No": targetwifiassymain_pn,
                "Qty": targetwifiassymain_qty,
                "Status": targetwifiassymain_state,
            },
            {
                "Category": "MR Remote",
                "Part No": targetremote_pn,
                "Qty": targetremote_qty,
                "Status": targetremote_state,
            },
            {
                "Category": "LCON Remote",
                "Part No": targetlconremote_pn,
                "Qty": targetlconremote_qty,
                "Status": targetlconremote_state,
            },
            {
                "Category": "MR Battery",
                "Part No": targetbattery_pn,
                "Qty": targetbattery_qty,
                "Status": targetbattery_state,
            },
            {
                "Category": "LCON Battery",
                "Part No": targetlconbattery_pn,
                "Qty": targetlconbattery_qty,
                "Status": targetlconbattery_state,
            },
            {
                "Category": "Ferrit Core",
                "Part No": targetferritcore_pn,
                "Qty": targetferritcore_qty,
                "Status": targetferritcore_state,
            },
            {
                "Category": "Tuner Case Cover",
                "Part No": targettunercover_pn,
                "Qty": targettunercover_qty,
                "Status": targettunercover_state,
            },
            {
                "Category": "Tuner Case Cover SVC",
                "Part No": targettunercoversvc_pn,
                "Qty": targettunercoversvc_qty,
                "Status": targettunercoversvc_state,
            },
            {
                "Category": "Holder",
                "Part No": targetholdermain_pn,
                "Qty": targetholdermain_qty,
                "Status": targetholdermain_state,
            },
            {
                "Category": "Holder SVC",
                "Part No": targetholdersvc_pn,
                "Qty": targetholdersvc_qty,
                "Status": targetholdersvc_state,
            },
            {
                "Category": "Tape 1",
                "Part No": targettape1_pn,
                "Qty": targettape1_qty,
                "Status": targettape1_state,
            },
            {
                "Category": "Tape 2",
                "Part No": targettape2_pn,
                "Qty": targettape2_qty,
                "Status": targettape2_state,
            },
            {
                "Category": "Tape 3",
                "Part No": targettape3_pn,
                "Qty": targettape3_qty,
                "Status": targettape3_state,
            },
            {
                "Category": "Tape 4",
                "Part No": targettape4_pn,
                "Qty": targettape4_qty,
                "Status": targettape4_state,
            },
            {
                "Category": "Tape 5",
                "Part No": targettape5_pn,
                "Qty": targettape5_qty,
                "Status": targettape5_state,
            },
            {
                "Category": "Gasket 1",
                "Part No": targetgasket1_pn,
                "Qty": targetgasket1_qty,
                "Status": targetgasket1_state,
            },
            {
                "Category": "Gasket 2",
                "Part No": targetgasket2_pn,
                "Qty": targetgasket2_qty,
                "Status": targetgasket2_state,
            },
            {
                "Category": "Gasket 3",
                "Part No": targetgasket3_pn,
                "Qty": targetgasket3_qty,
                "Status": targetgasket3_state,
            },
            {
                "Category": "Gasket 4",
                "Part No": targetgasket4_pn,
                "Qty": targetgasket4_qty,
                "Status": targetgasket4_state,
            },
            {
                "Category": "Gasket 5",
                "Part No": targetgasket5_pn,
                "Qty": targetgasket5_qty,
                "Status": targetgasket5_state,
            },
            {
                "Category": "Damper 1",
                "Part No": targetdamper1_pn,
                "Qty": targetdamper1_qty,
                "Status": targetdamper1_state,
            },
            {
                "Category": "Damper 2",
                "Part No": targetdamper2_pn,
                "Qty": targetdamper2_qty,
                "Status": targetdamper2_state,
            },
            {
                "Category": "Damper 3",
                "Part No": targetdamper3_pn,
                "Qty": targetdamper3_qty,
                "Status": targetdamper3_state,
            },
            {
                "Category": "Damper 4",
                "Part No": targetdamper4_pn,
                "Qty": targetdamper4_qty,
                "Status": targetdamper4_state,
            },
            {
                "Category": "Damper 5",
                "Part No": targetdamper5_pn,
                "Qty": targetdamper5_qty,
                "Status": targetdamper5_state,
            }
        ]
        with open(JSON_DIR / "4_target_statuspart.json", "w", encoding="utf-8") as f:
            json.dump(
                part_status,
                f,
                indent=4,
                ensure_ascii=False
            )
        
        return [
            targetebtmain_pn, targetebtmain_qty, targetebtmain_supplytype, targetebtmain_uit, targetebtmain_spec,
            targetebtassy_pn, targetebtassy_qty, targetebtassy_supplytype, targetebtassy_uit, targetebtassy_spec,
            targetebumain_pn, targetebumain_qty, targetebumain_supplytype, targetebumain_uit, targetebumain_spec,
            targetebrmain_pn, targetebrmain_qty, targetebrmain_supplytype, targetebrmain_uit, targetebrmain_spec,
            targetswassy_pn, targetswassy_qty, targetswassy_supplytype, targetswassy_uit, targetswassy_spec,
            targetedid_pn, targetedid_qty, targetedid_supplytype, targetedid_uit, targetedid_spec,
            targetplateshield_pn, targetplateshield_qty, targetplateshield_supplytype, targetplateshield_uit, targetplateshield_spec,
            targetplatesink_pn, targetplatesink_qty, targetplatesink_supplytype, targetplatesink_uit, targetplatesink_spec,
            targetplateholder_pn, targetplateholder_qty, targetplateholder_supplytype, targetplateholder_uit, targetplateholder_spec,
            targetsheetcooper_pn, targetsheetcooper_qty, targetsheetcooper_supplytype, targetsheetcooper_uit, targetsheetcooper_spec,
            targetmainpackage_pn, targetmainpackage_qty, targetmainpackage_supplytype, targetmainpackage_uit, targetmainpackage_spec,
            targetpcbmain_pn, targetpcbmain_qty, targetpcbmain_supplytype, targetpcbmain_uit, targetpcbmain_spec,
            targetebusvc_pn, targetebusvc_qty, targetebusvc_supplytype, targetebusvc_uit, targetebusvc_spec,
            targetebrsvc_pn, targetebrsvc_qty, targetebrsvc_supplytype, targetebrsvc_uit, targetebrsvc_spec,
            targetplateshieldsvc_pn, targetplateshieldsvc_qty, targetplateshieldsvc_supplytype, targetplateshieldsvc_uit, targetplateshieldsvc_spec,
            targetwifiassysvc_pn, targetwifiassysvc_qty, targetwifiassysvc_supplytype, targetwifiassysvc_uit, targetwifiassysvc_spec,
            targetspeakerright_pn, targetspeakerright_qty, targetspeakerright_supplytype, targetspeakerright_uit, targetspeakerright_spec,
            targetspeakerleft_pn, targetspeakerleft_qty, targetspeakerleft_supplytype, targetspeakerleft_uit, targetspeakerleft_spec,
            targetspeaker_pn, targetspeaker_qty, targetspeaker_supplytype, targetspeaker_uit, targetspeaker_spec,
            targetpowerboard_pn, targetpowerboard_qty, targetpowerboard_supplytype, targetpowerboard_uit, targetpowerboard_spec,
            targetebtpowercord_pn, targetebtpowercord_qty, targetebtpowercord_supplytype, targetebtpowercord_uit, targetebtpowercord_spec,
            targetpowercordattach_pn, targetpowercordattach_qty, targetpowercordattach_supplytype, targetpowercordattach_uit, targetpowercordattach_spec,
            targetpowercorddetach_pn, targetpowercorddetach_qty, targetpowercorddetach_supplytype, targetpowercorddetach_uit, targetpowercorddetach_spec,
            targetffcmain1_pn, targetffcmain1_qty, targetffcmain1_supplytype, targetffcmain1_uit, targetffcmain1_spec,
            targetffcmain2_pn, targetffcmain2_qty, targetffcmain2_supplytype, targetffcmain2_uit, targetffcmain2_spec,
            targetffcassy_pn, targetffcassy_qty, targetffcassy_supplytype, targetffcassy_uit, targetffcassy_spec,
            targetharnesssingle_pn, targetharnesssingle_qty, targetharnesssingle_supplytype, targetharnesssingle_uit, targetharnesssingle_spec,
            targetharnessmulti_pn, targetharnessmulti_qty, targetharnessmulti_supplytype, targetharnessmulti_uit, targetharnessmulti_spec,
            targetirassy_pn, targetirassy_qty, targetirassy_supplytype, targetirassy_uit, targetirassy_spec,
            targetwifiassy_pn, targetwifiassy_qty, targetwifiassy_supplytype, targetwifiassy_uit, targetwifiassy_spec,
            targetwifiassymain_pn, targetwifiassymain_qty, targetwifiassymain_supplytype, targetwifiassymain_uit, targetwifiassymain_spec,
            targetremote_pn, targetremote_qty, targetremote_supplytype, targetremote_uit, targetremote_spec,
            targetlconremote_pn, targetlconremote_qty, targetlconremote_supplytype, targetlconremote_uit, targetlconremote_spec,
            targetbattery_pn, targetbattery_qty, targetbattery_supplytype, targetbattery_uit, targetbattery_spec,
            targetlconbattery_pn, targetlconbattery_qty, targetlconbattery_supplytype, targetlconbattery_uit, targetlconbattery_spec,
            targetferritcore_pn, targetferritcore_qty, targetferritcore_supplytype, targetferritcore_uit, targetferritcore_spec,
            targettunercover_pn, targettunercover_qty, targettunercover_supplytype, targettunercover_uit, targettunercover_spec,
            targettunercoversvc_pn, targettunercoversvc_qty, targettunercoversvc_supplytype, targettunercoversvc_uit, targettunercoversvc_spec,
            targetholdermain_pn, targetholdermain_qty, targetholdermain_supplytype, targetholdermain_uit, targetholdermain_spec,
            targetholdersvc_pn, targetholdersvc_qty, targetholdersvc_supplytype, targetholdersvc_uit, targetholdersvc_spec,
            targettape1_pn, targettape1_qty, targettape1_supplytype, targettape1_uit, targettape1_spec,
            targettape2_pn, targettape2_qty, targettape2_supplytype, targettape2_uit, targettape2_spec,
            targettape3_pn, targettape3_qty, targettape3_supplytype, targettape3_uit, targettape3_spec,
            targettape4_pn, targettape4_qty, targettape4_supplytype, targettape4_uit, targettape4_spec,
            targettape5_pn, targettape5_qty, targettape5_supplytype, targettape5_uit, targettape5_spec,
            targetgasket1_pn, targetgasket1_qty, targetgasket1_supplytype, targetgasket1_uit, targetgasket1_spec,
            targetgasket2_pn, targetgasket2_qty, targetgasket2_supplytype, targetgasket2_uit, targetgasket2_spec,
            targetgasket3_pn, targetgasket3_qty, targetgasket3_supplytype, targetgasket3_uit, targetgasket3_spec,
            targetgasket4_pn, targetgasket4_qty, targetgasket4_supplytype, targetgasket4_uit, targetgasket4_spec,
            targetgasket5_pn, targetgasket5_qty, targetgasket5_supplytype, targetgasket5_uit, targetgasket5_spec,
            targetdamper1_pn, targetdamper1_qty, targetdamper1_supplytype, targetdamper1_uit, targetdamper1_spec,
            targetdamper2_pn, targetdamper2_qty, targetdamper2_supplytype, targetdamper2_uit, targetdamper2_spec,
            targetdamper3_pn, targetdamper3_qty, targetdamper3_supplytype, targetdamper3_uit, targetdamper3_spec,
            targetdamper4_pn, targetdamper4_qty, targetdamper4_supplytype, targetdamper4_uit, targetdamper4_spec,
            targetdamper5_pn, targetdamper5_qty, targetdamper5_supplytype, targetdamper5_uit, targetdamper5_spec
        ]
        # Save the extracted data to a JSON file
    def targetpart_compare(self):
        with open(JSON_DIR / "0_target_ebom.json", "r", encoding="utf-8") as f:
            response_data = json.load(f)
        target_model = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStr") == "00001" 
            ))
            ])
        if not target_model.empty:
                for idx, row in target_model.iterrows():
                    target_model = row['childNameDisplay']
        wb = load_workbook("excel/template_part.xlsx")
        ws = wb["BEN Compare"]

        data = self.targetpartscrapper()
        ebtmain_pn, ebtmain_qty, ebtmain_supplytype, ebtmain_uit, ebtmain_spec = data[0:5]
        ebtassy_pn, ebtassy_qty, ebtassy_supplytype, ebtassy_uit, ebtassy_spec = data[5:10]
        ebumain_pn, ebumain_qty, ebumain_supplytype, ebumain_uit, ebumain_spec = data[10:15]
        ebrmain_pn, ebrmain_qty, ebrmain_supplytype, ebrmain_uit, ebrmain_spec = data[15:20]
        swassy_pn, swassy_qty, swassy_supplytype, swassy_uit, swassy_spec = data[20:25]
        edid_pn, edid_qty, edid_supplytype, edid_uit, edid_spec = data[25:30]
        plateshield_pn, plateshield_qty, plateshield_supplytype, plateshield_uit, plateshield_spec = data[30:35]
        platesink_pn, platesink_qty, platesink_supplytype, platesink_uit, platesink_spec = data[35:40]
        plateholder_pn, plateholder_qty, plateholder_supplytype, plateholder_uit, plateholder_spec = data[40:45]
        sheetcooper_pn, sheetcooper_qty, sheetcooper_supplytype, sheetcooper_uit, sheetcooper_spec = data[45:50]
        ebrpackage_pn, ebrpackage_qty, ebrpackage_supplytype, ebrpackage_uit, ebrpackage_spec = data[50:55]
        pcbmain_pn, pcbmain_qty, pcbmain_supplytype, pcbmain_uit, pcbmain_spec = data[55:60]
        ebusvc_pn, ebusvc_qty, ebusvc_supplytype, ebusvc_uit, ebusvc_spec = data[60:65]
        ebrsvc_pn, ebrsvc_qty, ebrsvc_supplytype, ebrsvc_uit, ebrsvc_spec = data[65:70]
        plateshieldsvc_pn, plateshieldsvc_qty, plateshieldsvc_supplytype, plateshieldsvc_uit, plateshieldsvc_spec = data[70:75]
        wifiassysvc_pn, wifiassysvc_qty, wifiassysvc_supplytype, wifiassysvc_uit, wifiassysvc_spec = data[75:80]
        speakerright_pn, speakerright_qty, speakerright_supplytype, speakerright_uit, speakerright_spec = data[80:85]
        speakerleft_pn, speakerleft_qty, speakerleft_supplytype, speakerleft_uit, speakerleft_spec = data[85:90]
        speaker_pn, speaker_qty, speaker_supplytype, speaker_uit, speaker_spec = data[90:95]
        powerboard_pn, powerboard_qty, powerboard_supplytype, powerboard_uit, powerboard_spec = data[95:100]
        ebtpowercord_pn, ebtpowercord_qty, ebtpowercord_supplytype, ebtpowercord_uit, ebtpowercord_spec = data[100:105]
        powercordattach_pn, powercordattach_qty, powercordattach_supplytype, powercordattach_uit, powercordattach_spec = data[105:110]
        powercorddetach_pn, powercorddetach_qty, powercorddetach_supplytype, powercorddetach_uit, powercorddetach_spec = data[110:115]
        ffcmain1_pn, ffcmain1_qty, ffcmain1_supplytype, ffcmain1_uit, ffcmain1_spec = data[115:120]
        ffcmain2_pn, ffcmain2_qty, ffcmain2_supplytype, ffcmain2_uit, ffcmain2_spec = data[120:125]
        ffcassy_pn, ffcassy_qty, ffcassy_supplytype, ffcassy_uit, ffcassy_spec = data[125:130]
        harnesssingle_pn, harnesssingle_qty, harnesssingle_supplytype, harnesssingle_uit, harnesssingle_spec = data[130:135]
        harnessmulti_pn, harnessmulti_qty, harnessmulti_supplytype, harnessmulti_uit, harnessmulti_spec = data[135:140]
        irassy_pn, irassy_qty, irassy_supplytype, irassy_uit, irassy_spec = data[140:145]
        wifiassy_pn, wifiassy_qty, wifiassy_supplytype, wifiassy_uit, wifiassy_spec = data[145:150]
        wifimain_pn, wifimain_qty, wifimain_supplytype, wifimain_uit, wifimain_spec = data[150:155]
        remote_pn, remote_qty, remote_supplytype, remote_uit, remote_spec = data[155:160]
        lcon_pn, lcon_qty, lcon_supplytype, lcon_uit, lcon_spec = data[160:165]
        battery_pn, battery_qty, battery_supplytype, battery_uit, battery_spec = data[165:170]
        lconbattery_pn, lconbattery_qty, lconbattery_supplytype, lconbattery_uit, lconbattery_spec = data[170:175]
        ferritcore_pn, ferritcore_qty, ferritcore_supplytype, ferritcore_uit, ferritcore_spec = data[175:180]
        tunercover_pn, tunercover_qty, tunercover_supplytype, tunercover_uit, tunercover_spec = data[180:185]
        tunercoversvc_pn, tunercoversvc_qty, tunercoversvc_supplytype, tunercoversvc_uit, tunercoversvc_spec = data[185:190]
        holdermain_pn, holdermain_qty, holdermain_supplytype, holdermain_uit, holdermain_spec = data[190:195]
        holdersvc_pn, holdersvc_qty, holdersvc_supplytype, holdersvc_uit, holdersvc_spec = data[195:200]
        tape1_pn, tape1_qty, tape1_supplytype, tape1_uit, tape1_spec = data[200:205]
        tape2_pn, tape2_qty, tape2_supplytype, tape2_uit, tape2_spec = data[205:210]
        tape3_pn, tape3_qty, tape3_supplytype, tape3_uit, tape3_spec = data[210:215]
        tape4_pn, tape4_qty, tape4_supplytype, tape4_uit, tape4_spec = data[215:220]
        tape5_pn, tape5_qty, tape5_supplytype, tape5_uit, tape5_spec = data[220:225]
        gasket1_pn, gasket1_qty, gasket1_supplytype, gasket1_uit, gasket1_spec = data[225:230]
        gasket2_pn, gasket2_qty, gasket2_supplytype, gasket2_uit, gasket2_spec = data[230:235]
        gasket3_pn, gasket3_qty, gasket3_supplytype, gasket3_uit, gasket3_spec = data[235:240]
        gasket4_pn, gasket4_qty, gasket4_supplytype, gasket4_uit, gasket4_spec = data[240:245]
        gasket5_pn, gasket5_qty, gasket5_supplytype, gasket5_uit, gasket5_spec = data[245:250]
        damper1_pn, damper1_qty, damper1_supplytype, damper1_uit, damper1_spec = data[250:255]
        damper2_pn, damper2_qty, damper2_supplytype, damper2_uit, damper2_spec = data[255:260]
        damper3_pn, damper3_qty, damper3_supplytype, damper3_uit, damper3_spec = data[260:265]
        damper4_pn, damper4_qty, damper4_supplytype, damper4_uit, damper4_spec = data[265:270]
        damper5_pn, damper5_qty, damper5_supplytype, damper5_uit, damper5_spec = data[270:275]

        rows = list(range(6, 61))
        columns = list(range(14, 19))
        data_list = [
            ebtmain_pn, ebtmain_qty, ebtmain_supplytype, ebtmain_uit, ebtmain_spec,
            ebtassy_pn, ebtassy_qty, ebtassy_supplytype, ebtassy_uit, ebtassy_spec,
            ebumain_pn, ebumain_qty, ebumain_supplytype, ebumain_uit, ebumain_spec,
            ebrmain_pn, ebrmain_qty, ebrmain_supplytype, ebrmain_uit, ebrmain_spec,
            swassy_pn, swassy_qty, swassy_supplytype, swassy_uit, swassy_spec,
            edid_pn, edid_qty, edid_supplytype, edid_uit, edid_spec,
            plateshield_pn, plateshield_qty, plateshield_supplytype, plateshield_uit, plateshield_spec,
            platesink_pn, platesink_qty, platesink_supplytype, platesink_uit, platesink_spec,
            plateholder_pn, plateholder_qty, plateholder_supplytype, plateholder_uit, plateholder_spec,
            sheetcooper_pn, sheetcooper_qty, sheetcooper_supplytype, sheetcooper_uit, sheetcooper_spec,
            ebrpackage_pn, ebrpackage_qty, ebrpackage_supplytype, ebrpackage_uit, ebrpackage_spec,
            pcbmain_pn, pcbmain_qty, pcbmain_supplytype, pcbmain_uit, pcbmain_spec,
            ebusvc_pn, ebusvc_qty, ebusvc_supplytype, ebusvc_uit, ebusvc_spec,
            ebrsvc_pn, ebrsvc_qty, ebrsvc_supplytype, ebrsvc_uit, ebrsvc_spec,
            plateshieldsvc_pn, plateshieldsvc_qty, plateshieldsvc_supplytype, plateshieldsvc_uit, plateshieldsvc_spec,
            wifiassysvc_pn, wifiassysvc_qty, wifiassysvc_supplytype, wifiassysvc_uit, wifiassysvc_spec,
            speakerright_pn, speakerright_qty, speakerright_supplytype, speakerright_uit, speakerright_spec,
            speakerleft_pn, speakerleft_qty, speakerleft_supplytype, speakerleft_uit, speakerleft_spec,
            speaker_pn, speaker_qty, speaker_supplytype, speaker_uit, speaker_spec,
            powerboard_pn, powerboard_qty, powerboard_supplytype, powerboard_uit, powerboard_spec,
            ebtpowercord_pn, ebtpowercord_qty, ebtpowercord_supplytype, ebtpowercord_uit, ebtpowercord_spec,
            powercordattach_pn, powercordattach_qty, powercordattach_supplytype, powercordattach_uit, powercordattach_spec,
            powercorddetach_pn, powercorddetach_qty, powercorddetach_supplytype, powercorddetach_uit, powercorddetach_spec,
            ffcmain1_pn, ffcmain1_qty, ffcmain1_supplytype, ffcmain1_uit, ffcmain1_spec,
            ffcmain2_pn, ffcmain2_qty, ffcmain2_supplytype, ffcmain2_uit, ffcmain2_spec,
            ffcassy_pn, ffcassy_qty, ffcassy_supplytype, ffcassy_uit, ffcassy_spec,
            harnesssingle_pn, harnesssingle_qty, harnesssingle_supplytype, harnesssingle_uit, harnesssingle_spec,
            harnessmulti_pn, harnessmulti_qty, harnessmulti_supplytype, harnessmulti_uit, harnessmulti_spec,
            irassy_pn, irassy_qty, irassy_supplytype, irassy_uit, irassy_spec,
            wifiassy_pn, wifiassy_qty, wifiassy_supplytype, wifiassy_uit, wifiassy_spec,
            wifimain_pn, wifimain_qty, wifimain_supplytype, wifimain_uit, wifimain_spec,
            remote_pn, remote_qty, remote_supplytype, remote_uit, remote_spec,
            lcon_pn, lcon_qty, lcon_supplytype, lcon_uit, lcon_spec,
            battery_pn, battery_qty, battery_supplytype, battery_uit, battery_spec,
            lconbattery_pn, lconbattery_qty, lconbattery_supplytype, lconbattery_uit, lconbattery_spec,
            ferritcore_pn, ferritcore_qty, ferritcore_supplytype, ferritcore_uit, ferritcore_spec,
            tunercover_pn, tunercover_qty, tunercover_supplytype, tunercover_uit, tunercover_spec,
            tunercoversvc_pn, tunercoversvc_qty, tunercoversvc_supplytype, tunercoversvc_uit, tunercoversvc_spec,
            holdermain_pn, holdermain_qty, holdermain_supplytype, holdermain_uit, holdermain_spec,
            holdersvc_pn, holdersvc_qty, holdersvc_supplytype, holdersvc_uit, holdersvc_spec,
            tape1_pn, tape1_qty, tape1_supplytype, tape1_uit, tape1_spec,
            tape2_pn, tape2_qty, tape2_supplytype, tape2_uit, tape2_spec,
            tape3_pn, tape3_qty, tape3_supplytype, tape3_uit, tape3_spec,
            tape4_pn, tape4_qty, tape4_supplytype, tape4_uit, tape4_spec,
            tape5_pn, tape5_qty, tape5_supplytype, tape5_uit, tape5_spec,
            gasket1_pn, gasket1_qty, gasket1_supplytype, gasket1_uit, gasket1_spec,
            gasket2_pn, gasket2_qty, gasket2_supplytype, gasket2_uit, gasket2_spec,
            gasket3_pn, gasket3_qty, gasket3_supplytype, gasket3_uit, gasket3_spec,
            gasket4_pn, gasket4_qty, gasket4_supplytype, gasket4_uit, gasket4_spec,
            gasket5_pn, gasket5_qty, gasket5_supplytype, gasket5_uit, gasket5_spec,
            damper1_pn, damper1_qty, damper1_supplytype, damper1_uit, damper1_spec,
            damper2_pn, damper2_qty, damper2_supplytype, damper2_uit, damper2_spec,
            damper3_pn, damper3_qty, damper3_supplytype, damper3_uit, damper3_spec,
            damper4_pn, damper4_qty, damper4_supplytype, damper4_uit, damper4_spec,
            damper5_pn, damper5_qty, damper5_supplytype, damper5_uit, damper5_spec
        ]
        
        
        for row in ws.iter_rows(min_row=6, max_row=61, min_col=14, max_col=18):
            for cell in row:
                cell.value = None

        ws["N4"] = str(target_model.split('@')[0])

        for i, row in enumerate(rows):
            for j, column in enumerate(columns):
                ws.cell(row=row, column=column).value = data_list[i * len(columns) + j]

        wb.save("excel/template_part.xlsx")
        print("Target part compare completed")

class developmentpart_compare():
    def __init__(self):
        pass
    def target_run(self):
        self.targetpartscrapper()
        # self.targetpart_compare()
        # developmentpartscrapper()
        # initialpartscrapper()
    def targetpartscrapper(self):
        with open(JSON_DIR / "0_development_ebom.json", "r", encoding="utf-8") as f:
            response_data = json.load(f)
        
        #<Search for specific components in EBOM data (Accessory Assembly)>
        Accesory = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == "00001" and
                "AAA" in "{}".format(item.get("childNameDisplay", "")) and 
                "Accessory Assembly" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))
            ))
            ])
        if not Accesory.empty:
            for idx, row in Accesory.iterrows():
                targetaccessory_pn = row['childNameDisplay']
                targetaccessory_qty = row['bomQuantity']
                targetaccessory_level = row['bomLevel']
                targetaccessory_uit = row['outData.mr_userItemType']
                targetaccessory_supplytype = row['supplyType']
                targetaccessory_state = row['outData.pp_states']
                targetaccessory_parttype = row['dataType']
                targetaccessory_spec = row['outData.mr_siteTechnicalSpec']
                targetaccessory_uniquieid = row['uniqueStr']
        else:
            targetaccessory_pn = ""
            targetaccessory_qty = ""
            targetaccessory_level = ""
            targetaccessory_uit = ""
            targetaccessory_supplytype = ""
            targetaccessory_state = ""
            targetaccessory_parttype = ""
            targetaccessory_spec = ""
            targetaccessory_uniquieid = ""
        #<Search for specific components in EBOM data (Ferrite Core)>
        Ferrit_core = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetaccessory_uniquieid and
                "621" in "{}".format(item.get("childNameDisplay", "")) and
                "Ferrite" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))
                ))
            ])
        if not Ferrit_core.empty:
            for idx, row in Ferrit_core.iterrows():
                targetferritcore_pn = row['childNameDisplay']
                targetferritcore_qty = row['bomQuantity']
                targetferritcore_level = row['bomLevel']
                targetferritcore_uit = row['outData.mr_userItemType']
                targetferritcore_supplytype = row['supplyType']
                targetferritcore_state = row['outData.pp_states']
                targetferritcore_parttype = row['dataType']
                targetferritcore_spec = row['outData.mr_siteTechnicalSpec']
                targetferritcore_uniquieid = row['uniqueStr']
        else:
            targetferritcore_pn = ""
            targetferritcore_qty = ""
            targetferritcore_level = ""
            targetferritcore_uit = ""
            targetferritcore_supplytype = ""
            targetferritcore_state = ""
            targetferritcore_parttype = ""
            targetferritcore_spec = ""
            targetferritcore_uniquieid = ""
        #<Search for specific components in EBOM data (MR battery)
        MR_battery = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetaccessory_uniquieid and
                "EAC" in "{}".format(item.get("childNameDisplay", "")) and
                "Battery" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "LR06" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", ""))) or 
                (item.get("uniqueStrParent") == targetaccessory_uniquieid and
                "691" in "{}".format(item.get("childNameDisplay", "")) and
                "Battery" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "LR06" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", ""))) or
                (item.get("uniqueStrParent") == targetaccessory_uniquieid and
                "EAC" in "{}".format(item.get("childNameDisplay", "")) and
                "Battery" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "LR03" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", ""))) or 
                (item.get("uniqueStrParent") == targetaccessory_uniquieid and 
                "691" in "{}".format(item.get("childNameDisplay", "")) and 
                "Battery" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "LR03" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", ""))
                ))
            ])
        if not MR_battery.empty:
            for idx, row in MR_battery.iterrows():
                targetbattery_pn = row['childNameDisplay']
                targetbattery_qty = row['bomQuantity']
                targetbattery_level = row['bomLevel']
                targetbattery_uit = row['outData.mr_userItemType']
                targetbattery_supplytype = row['supplyType']
                targetbattery_state = row['outData.pp_states']
                targetbattery_parttype = row['dataType']
                targetbattery_spec = row['outData.mr_siteTechnicalSpec']
                targetbattery_uniquieid = row['uniqueStr']
            targetbattery_pn = MR_battery['childNameDisplay'].iloc[0]
            targetbattery_qty = MR_battery['bomQuantity'].iloc[0]
            targetbattery_level = MR_battery['bomLevel'].iloc[0]
            targetbattery_uit = MR_battery['outData.mr_userItemType'].iloc[0]
            targetbattery_supplytype = MR_battery['supplyType'].iloc[0]
            targetbattery_state = MR_battery['outData.pp_states'].iloc[0]
            targetbattery_parttype = MR_battery['dataType'].iloc[0]
            targetbattery_spec = MR_battery['outData.mr_siteTechnicalSpec'].iloc[0]
            targetbattery_uniquieid = MR_battery['uniqueStr'].iloc[0]
        else:
            targetbattery_pn = ""
            targetbattery_qty = ""
            targetbattery_level = ""
            targetbattery_uit = ""
            targetbattery_supplytype = ""
            targetbattery_state = ""
            targetbattery_parttype = ""
            targetbattery_spec = ""
            targetbattery_uniquieid = ""
        #<Search for specific components in EBOM data (L-Con battery)
        Lcon_battery = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                "130" in "{}".format(item.get("childNameDisplay", "")) and
                "Battery" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))
                ))
            ])
        if not Lcon_battery.empty:
            for idx, row in Lcon_battery.iterrows():
                targetlconbattery_pn = row['childNameDisplay']
                targetlconbattery_qty = row['bomQuantity']
                targetlconbattery_level = row['bomLevel']
                targetlconbattery_uit = row['outData.mr_userItemType']
                targetlconbattery_supplytype = row['supplyType']
                targetlconbattery_state = row['outData.pp_states']
                targetlconbattery_parttype = row['dataType']
                targetlconbattery_spec = row['outData.mr_siteTechnicalSpec']
                targetlconbattery_uniquieid = row['uniqueStr']
            targetlconbattery_pn = Lcon_battery['childNameDisplay'].iloc[0]
            targetlconbattery_qty = Lcon_battery['bomQuantity'].iloc[0]
            targetlconbattery_level = Lcon_battery['bomLevel'].iloc[0]
            targetlconbattery_uit = Lcon_battery['outData.mr_userItemType'].iloc[0]
            targetlconbattery_supplytype = Lcon_battery['supplyType'].iloc[0]
            targetlconbattery_state = Lcon_battery['outData.pp_states'].iloc[0]
            targetlconbattery_parttype = Lcon_battery['dataType'].iloc[0]
            targetlconbattery_spec = Lcon_battery['outData.mr_siteTechnicalSpec'].iloc[0]
            targetlconbattery_uniquieid = Lcon_battery['uniqueStr'].iloc[0]
        else:
            targetlconbattery_pn = ""
            targetlconbattery_qty = ""
            targetlconbattery_level = ""
            targetlconbattery_uit = ""
            targetlconbattery_supplytype = ""
            targetlconbattery_state = ""
            targetlconbattery_parttype = ""
            targetlconbattery_spec = ""
            targetlconbattery_uniquieid = ""    
        #<Search for specific components in EBOM data (MR remote)
        MR_remote = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetaccessory_uniquieid and
                "AKB" in "{}".format(item.get("childNameDisplay", "")) and
                "Remote" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "MR" in "{}".format(item.get("outData", {}).get('mr_siteTechnicalSpec', ""))
                ))
            ])
        if not MR_remote.empty:
            for idx, row in MR_remote.iterrows():
                targetremote_pn = row['childNameDisplay']
                targetremote_qty = row['bomQuantity']
                targetremote_level = row['bomLevel']
                targetremote_uit = row['outData.mr_userItemType']
                targetremote_supplytype = row['supplyType']
                targetremote_state = row['outData.pp_states']
                targetremote_parttype = row['dataType']
                targetremote_spec = row['outData.mr_siteTechnicalSpec']
                targetremote_uniquieid = row['uniqueStr']
            targetremote_pn = MR_remote['childNameDisplay'].iloc[0]
            targetremote_qty = MR_remote['bomQuantity'].iloc[0]
            targetremote_level = MR_remote['bomLevel'].iloc[0]
            targetremote_uit = MR_remote['outData.mr_userItemType'].iloc[0]
            targetremote_supplytype = MR_remote['supplyType'].iloc[0]
            targetremote_state = MR_remote['outData.pp_states'].iloc[0]
            targetremote_parttype = MR_remote['dataType'].iloc[0]
            targetremote_spec = MR_remote['outData.mr_siteTechnicalSpec'].iloc[0]
            targetremote_uniquieid = MR_remote['uniqueStr'].iloc[0]
        else:
            targetremote_pn = ""
            targetremote_qty = ""
            targetremote_level = ""
            targetremote_uit = ""
            targetremote_supplytype = ""
            targetremote_state = ""
            targetremote_parttype = ""
            targetremote_spec = ""
            targetremote_uniquieid = ""
        #<Search for specific components in EBOM data (L-Con remote)
        Lcon_remote = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                "AKB" in "{}".format(item.get("childNameDisplay", "")) and
                "Remote" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "L-Con" in "{}".format(item.get("outData", {}).get('mr_siteTechnicalSpec', ""))
                ))
            ])
        if not Lcon_remote.empty:
            for idx, row in Lcon_remote.iterrows():
                targetlconremote_pn = row['childNameDisplay']
                targetlconremote_qty = row['bomQuantity']
                targetlconremote_level = row['bomLevel']
                targetlconremote_uit = row['outData.mr_userItemType']
                targetlconremote_supplytype = row['supplyType']
                targetlconremote_state = row['outData.pp_states']
                targetlconremote_parttype = row['dataType']
                targetlconremote_spec = row['outData.mr_siteTechnicalSpec']
                targetlconremote_uniquieid = row['uniqueStr']
            targetlconremote_pn = Lcon_remote['childNameDisplay'].iloc[0]
            targetlconremote_qty = Lcon_remote['bomQuantity'].iloc[0]
            targetlconremote_level = Lcon_remote['bomLevel'].iloc[0]
            targetlconremote_uit = Lcon_remote['outData.mr_userItemType'].iloc[0]
            targetlconremote_supplytype = Lcon_remote['supplyType'].iloc[0]
            targetlconremote_state = Lcon_remote['outData.pp_states'].iloc[0]
            targetlconremote_parttype = Lcon_remote['dataType'].iloc[0]
            targetlconremote_spec = Lcon_remote['outData.mr_siteTechnicalSpec'].iloc[0]
            targetlconremote_uniquieid = Lcon_remote['uniqueStr'].iloc[0]
        else:
            targetlconremote_pn = ""
            targetlconremote_qty = ""
            targetlconremote_level = ""
            targetlconremote_uit = ""
            targetlconremote_supplytype = ""
            targetlconremote_state = ""
            targetlconremote_parttype = ""
            targetlconremote_spec = ""
            targetlconremote_uniquieid = ""
        #<Search for specific components in EBOM data (Bracket Assy)
        Bracket_Assy = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == "00001" and
                ("ABA" in "{}".format(item.get("childNameDisplay", "")) and 
                "Bracket Assembly,Sub" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))) or
                ("ACQ" in "{}".format(item.get("childNameDisplay", "")) and
                "Bracket Assembly" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))) and
                ("Wifi" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or 
                "IR" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "SUB" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
            ))
            ])
        if not Bracket_Assy.empty:
            for idx, row in Bracket_Assy.iterrows():
                targetbracketassy_pn = row['childNameDisplay']
                targetbracketassy_qty = row['bomQuantity']
                targetbracketassy_level = row['bomLevel']
                targetbracketassy_uit = row['outData.mr_userItemType']
                targetbracketassy_supplytype = row['supplyType']
                targetbracketassy_state = row['outData.pp_states']
                targetbracketassy_parttype = row['dataType']
                targetbracketassy_spec = row['outData.mr_siteTechnicalSpec']
                targetbracketassy_uniquieid = row['uniqueStr']
        else:
            targetbracketassy_pn = ""
            targetbracketassy_qty = ""
            targetbracketassy_level = ""
            targetbracketassy_uit = ""
            targetbracketassy_supplytype = ""
            targetbracketassy_state = ""
            targetbracketassy_parttype = ""
            targetbracketassy_spec = ""
            targetbracketassy_uniquieid = ""
        #<Search for specific components in EBOM data (Wifi Assy)
        EBT_Subassy = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetbracketassy_uniquieid and
                "EBT" in "{}".format(item.get("childNameDisplay", "")) and 
                "Chassis Assembly,Sub" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Wifi" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or 
                "IR" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "SUB" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not EBT_Subassy.empty:
            for idx, row in EBT_Subassy.iterrows():
                targetebtassy_pn = row['childNameDisplay']
                targetebtassy_qty = row['bomQuantity']
                targetebtassy_level = row['bomLevel']
                targetebtassy_uit = row['outData.mr_userItemType']
                targetebtassy_supplytype = row['supplyType']
                targetebtassy_state = row['outData.pp_states']
                targetebtassy_parttype = row['dataType']
                targetebtassy_spec = row['outData.mr_siteTechnicalSpec']
                targetebtassy_uniquieid = row['uniqueStr']
            targetebtassy_pn =EBT_Subassy['childNameDisplay'].iloc[0]
            targetebtassy_qty =EBT_Subassy['bomQuantity'].iloc[0]
            targetebtassy_level =EBT_Subassy['bomLevel'].iloc[0]
            targetebtassy_uit =EBT_Subassy['outData.mr_userItemType'].iloc[0]
            targetebtassy_supplytype =EBT_Subassy['supplyType'].iloc[0]
            targetebtassy_state =EBT_Subassy['outData.pp_states'].iloc[0]
            targetebtassy_parttype =EBT_Subassy['dataType'].iloc[0]
            targetebtassy_spec =EBT_Subassy['outData.mr_siteTechnicalSpec'].iloc[0]
            targetebtassy_uniquieid =EBT_Subassy['uniqueStr'].iloc[0]
        else:
            targetebtassy_pn = ""
            targetebtassy_qty = ""
            targetebtassy_level = ""
            targetebtassy_uit = ""
            targetebtassy_supplytype = ""
            targetebtassy_state = ""
            targetebtassy_parttype = ""
            targetebtassy_spec = ""
            targetebtassy_uniquieid = ""
        #<Search for specific components in EBOM data (Wifi Assy)
        Wifi_assy = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                (item.get("uniqueStrParent") == targetebtassy_uniquieid and
                "EAT" in "{}".format(item.get("childNameDisplay", "")) and 
                "Module,Wifi Bluetooth Module" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "LGSW" in "{}".format(item.get("outData", {}).get('mr_siteTechnicalSpec', ""))) or
                (item.get("uniqueStrParent") == targetebtassy_uniquieid and
                "EBR" in "{}".format(item.get("childNameDisplay", "")) and 
                "PCB Assembly,Sub" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "CKD" in "{}".format(item.get("outData", {}).get('mr_siteTechnicalSpec', "")))
                ))
            ])
        if not Wifi_assy.empty:
            for idx, row in Wifi_assy.iterrows():
                targetwifiassy_pn = row['childNameDisplay']
                targetwifiassy_qty = row['bomQuantity']
                targetwifiassy_level = row['bomLevel']
                targetwifiassy_uit = row['outData.mr_userItemType']
                targetwifiassy_supplytype = row['supplyType']
                targetwifiassy_state = row['outData.pp_states']
                targetwifiassy_parttype = row['dataType']
                targetwifiassy_spec = row['outData.mr_siteTechnicalSpec']
                targetwifiassy_uniquieid = row['uniqueStr']
            targetwifiassy_pn =Wifi_assy['childNameDisplay'].iloc[0]
            targetwifiassy_qty =Wifi_assy['bomQuantity'].iloc[0]
            targetwifiassy_level =Wifi_assy['bomLevel'].iloc[0]
            targetwifiassy_uit =Wifi_assy['outData.mr_userItemType'].iloc[0]
            targetwifiassy_supplytype =Wifi_assy['supplyType'].iloc[0]
            targetwifiassy_state =Wifi_assy['outData.pp_states'].iloc[0]
            targetwifiassy_parttype =Wifi_assy['dataType'].iloc[0]
            targetwifiassy_spec =Wifi_assy['outData.mr_siteTechnicalSpec'].iloc[0]
            targetwifiassy_uniquieid =Wifi_assy['uniqueStr'].iloc[0]
        else:
            targetwifiassy_pn = ""
            targetwifiassy_qty = ""
            targetwifiassy_level = ""
            targetwifiassy_uit = ""
            targetwifiassy_supplytype = ""
            targetwifiassy_state = ""
            targetwifiassy_parttype = ""
            targetwifiassy_spec = ""
            targetwifiassy_uniquieid = ""
        #<Search for specific components in EBOM data (IR Assy)
        IR_assy = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtassy_uniquieid and
                "EBR" in "{}".format(item.get("childNameDisplay", "")) and 
                "PCB Assembly,IR Key" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "IR" in "{}".format(item.get("outData", {}).get('mr_siteTechnicalSpec', ""))
                ))
            ])
        if not IR_assy.empty:
            for idx, row in IR_assy.iterrows():
                targetirassy_pn = row['childNameDisplay']
                targetirassy_qty = row['bomQuantity']
                targetirassy_level = row['bomLevel']
                targetirassy_uit = row['outData.mr_userItemType']
                targetirassy_supplytype = row['supplyType']
                targetirassy_state = row['outData.pp_states']        
                targetirassy_parttype = row['dataType']
                targetirassy_spec = row['outData.mr_siteTechnicalSpec']
                targetirassy_uniquieid = row['uniqueStr']
            targetirassy_pn = IR_assy['childNameDisplay'].iloc[0]
            targetirassy_qty = IR_assy['bomQuantity'].iloc[0]
            targetirassy_level = IR_assy['bomLevel'].iloc[0]
            targetirassy_uit = IR_assy['outData.mr_userItemType'].iloc[0]
            targetirassy_supplytype = IR_assy['supplyType'].iloc[0]
            targetirassy_state = IR_assy['outData.pp_states'].iloc[0]
            targetirassy_parttype = IR_assy['dataType'].iloc[0]
            targetirassy_spec = IR_assy['outData.mr_siteTechnicalSpec'].iloc[0]
            targetirassy_uniquieid = IR_assy['uniqueStr'].iloc[0]
        else:
            targetirassy_pn = ""
            targetirassy_qty = ""
            targetirassy_level = ""
            targetirassy_uit = ""
            targetirassy_supplytype = ""
            targetirassy_state = ""
            targetirassy_parttype = ""
            targetirassy_spec = ""
            targetirassy_uniquieid = ""
        #<Search for specific components in EBOM data (FFC Assy)
        FFC_assy = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtassy_uniquieid and
                "EAD" in "{}".format(item.get("childNameDisplay", "")) and 
                "Cable,FFC" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Wifi" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or 
                "IR" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not FFC_assy.empty:
            for idx, row in FFC_assy.iterrows():
                targetffcassy_pn = row['childNameDisplay']
                targetffcassy_qty = row['bomQuantity']
                targetffcassy_level = row['bomLevel']
                targetffcassy_uit = row['outData.mr_userItemType']
                targetffcassy_supplytype = row['supplyType']
                targetffcassy_state = row['outData.pp_states']
                targetffcassy_parttype = row['dataType']
                targetffcassy_spec = row['outData.mr_siteTechnicalSpec']
                targetffcassy_uniquieid = row['uniqueStr']
            targetffcassy_pn = FFC_assy['childNameDisplay'].iloc[0]
            targetffcassy_qty = FFC_assy['bomQuantity'].iloc[0]
            targetffcassy_level = FFC_assy['bomLevel'].iloc[0]
            targetffcassy_uit = FFC_assy['outData.mr_userItemType'].iloc[0]
            targetffcassy_supplytype = FFC_assy['supplyType'].iloc[0]
            targetffcassy_state = FFC_assy['outData.pp_states'].iloc[0]
            targetffcassy_parttype = FFC_assy['dataType'].iloc[0]
            targetffcassy_spec = FFC_assy['outData.mr_siteTechnicalSpec'].iloc[0]
            targetffcassy_uniquieid = FFC_assy['uniqueStr'].iloc[0]
        else:
            targetffcassy_pn = ""
            targetffcassy_qty = ""
            targetffcassy_level = ""
            targetffcassy_uit = ""
            targetffcassy_supplytype = ""
            targetffcassy_state = ""
            targetffcassy_parttype = ""
            targetffcassy_spec = ""
            targetffcassy_uniquieid = ""
        #<Search for specific components in EBOM data (Speaker Right)
        Speaker_Right = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == "00001" and
                "EAB" in "{}".format(item.get("childNameDisplay", "")) and 
                "Speaker" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "RIGHT" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", ""))
                ))
            ])
        if not Speaker_Right.empty:
            for idx, row in Speaker_Right.iterrows():
                targetspeakerright_pn = row['childNameDisplay']
                targetspeakerright_qty = row['bomQuantity']
                targetspeakerright_level = row['bomLevel']
                targetspeakerright_uit = row['outData.mr_userItemType']
                targetspeakerright_supplytype = row['supplyType']
                targetspeakerright_state = row['outData.pp_states']
                targetspeakerright_parttype = row['dataType']
                targetspeakerright_spec = row['outData.mr_siteTechnicalSpec']
                targetspeakerright_uniquieid = row['uniqueStr']
            targetspeakerright_pn = Speaker_Right['childNameDisplay'].iloc[0]
            targetspeakerright_qty = Speaker_Right['bomQuantity'].iloc[0]
            targetspeakerright_level = Speaker_Right['bomLevel'].iloc[0]
            targetspeakerright_uit = Speaker_Right['outData.mr_userItemType'].iloc[0]
            targetspeakerright_supplytype = Speaker_Right['supplyType'].iloc[0]
            targetspeakerright_state = Speaker_Right['outData.pp_states'].iloc[0]
            targetspeakerright_parttype = Speaker_Right['dataType'].iloc[0]
            targetspeakerright_spec = Speaker_Right['outData.mr_siteTechnicalSpec'].iloc[0]
            targetspeakerright_uniquieid = Speaker_Right['uniqueStr'].iloc[0]
        else:
            targetspeakerright_pn = ""
            targetspeakerright_qty = ""
            targetspeakerright_level = ""
            targetspeakerright_uit = ""
            targetspeakerright_supplytype = ""
            targetspeakerright_state = ""
            targetspeakerright_parttype = ""
            targetspeakerright_spec = ""
            targetspeakerright_uniquieid = ""
        #<Search for specific components in EBOM data (Speaker Left)
        Speaker_Left = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == "00001" and
                "EAB" in "{}".format(item.get("childNameDisplay", "")) and 
                "Speaker" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "LEFT" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", ""))
                ))
            ])
        if not Speaker_Left.empty:
            for idx, row in Speaker_Left.iterrows():
                targetspeakerleft_pn = row['childNameDisplay']
                targetspeakerleft_qty = row['bomQuantity']
                targetspeakerleft_level = row['bomLevel']
                targetspeakerleft_uit = row['outData.mr_userItemType']
                targetspeakerleft_supplytype = row['supplyType']
                targetspeakerleft_state = row['outData.pp_states']
                targetspeakerleft_parttype = row['dataType']
                targetspeakerleft_spec = row['outData.mr_siteTechnicalSpec']
                targetspeakerleft_uniquieid = row['uniqueStr']
            targetspeakerleft_pn = Speaker_Left['childNameDisplay'].iloc[0]
            targetspeakerleft_qty = Speaker_Left['bomQuantity'].iloc[0]
            targetspeakerleft_level = Speaker_Left['bomLevel'].iloc[0]        
            targetspeakerleft_uit = Speaker_Left['outData.mr_userItemType'].iloc[0]
            targetspeakerleft_supplytype = Speaker_Left['supplyType'].iloc[0]
            targetspeakerleft_state = Speaker_Left['outData.pp_states'].iloc[0]
            targetspeakerleft_parttype = Speaker_Left['dataType'].iloc[0]
            targetspeakerleft_spec = Speaker_Left['outData.mr_siteTechnicalSpec'].iloc[0]
            targetspeakerleft_uniquieid = Speaker_Left['uniqueStr'].iloc[0]
        else:
            targetspeakerleft_pn = ""
            targetspeakerleft_qty = ""
            targetspeakerleft_level = ""
            targetspeakerleft_uit = ""
            targetspeakerleft_supplytype = ""
            targetspeakerleft_state = ""
            targetspeakerleft_parttype = ""
            targetspeakerleft_spec = ""
            targetspeakerleft_uniquieid = ""    
        #<Search for specific components in EBOM data (Speaker Assy)
        Speaker_assy = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == "00001" and
                "EAB" in "{}".format(item.get("childNameDisplay", "")) and 
                "Speaker" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))
                ))
            ])
        if not Speaker_assy.empty:
            for idx, row in Speaker_assy.iterrows():
                targetspeaker_pn = row['childNameDisplay']
                targetspeaker_qty = row['bomQuantity']
                targetspeaker_level = row['bomLevel']
                targetspeaker_uit = row['outData.mr_userItemType']
                targetspeaker_supplytype = row['supplyType']
                targetspeaker_state = row['outData.pp_states']
                targetspeaker_parttype = row['dataType']
                targetspeaker_spec = row['outData.mr_siteTechnicalSpec']
                targetspeaker_uniquieid = row['uniqueStr']
            targetspeaker_pn = Speaker_assy['childNameDisplay'].iloc[0]
            targetspeaker_qty = Speaker_assy['bomQuantity'].iloc[0]
            targetspeaker_level = Speaker_assy['bomLevel'].iloc[0]        
            targetspeaker_uit = Speaker_assy['outData.mr_userItemType'].iloc[0]
            targetspeaker_supplytype = Speaker_assy['supplyType'].iloc[0]
            targetspeaker_state = Speaker_assy['outData.pp_states'].iloc[0]
            targetspeaker_parttype = Speaker_assy['dataType'].iloc[0]
            targetspeaker_spec = Speaker_assy['outData.mr_siteTechnicalSpec'].iloc[0]
            targetspeaker_uniquieid = Speaker_assy['uniqueStr'].iloc[0]
        else:
            targetspeaker_pn = ""
            targetspeaker_qty = ""
            targetspeaker_level = ""
            targetspeaker_uit = ""
            targetspeaker_supplytype = ""
            targetspeaker_state = ""
            targetspeaker_parttype = ""
            targetspeaker_spec = ""
            targetspeaker_uniquieid
        #<Search for specific components in EBOM data (FFC Main)
        FFC_Main = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                "EAD" in "{}".format(item.get("childNameDisplay", "")) and 
                "Cable,FFC" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("68P" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or 
                "CEDS" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "VBY1" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "VX1" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "EPI" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        targets_ffc = []  # tampung semua baris
        if not FFC_Main.empty:
            for _, row in FFC_Main.head(5).iterrows():
                targets_ffc.append({
                    "pn":           row.get("childNameDisplay"),
                    "qty":          row.get("bomQuantity"),
                    "level":        row.get("bomLevel"),
                    "uit":          row.get("outData.mr_userItemType"),
                    "supplytype":   row.get("supplyType"),
                    "state":        row.get("outData.pp_states"),
                    "parttype":     row.get("dataType"),
                    "spec":         row.get("outData.mr_siteTechnicalSpec"),
                    "uniqueid":     row.get("uniqueStr"),
                })
        # contoh akses aman:
        if len(targets_ffc) >= 1:
            targetffcmain1_pn = targets_ffc[0]["pn"]
            targetffcmain1_qty = targets_ffc[0]["qty"]
            targetffcmain1_level = targets_ffc[0]["level"]
            targetffcmain1_uit = targets_ffc[0]["uit"]
            targetffcmain1_supplytype = targets_ffc[0]["supplytype"]
            targetffcmain1_state = targets_ffc[0]["state"]
            targetffcmain1_parttype = targets_ffc[0]["parttype"]
            targetffcmain1_spec = targets_ffc[0]["spec"]
            targetffcmain1_uniquieid = targets_ffc[0]["uniqueid"]
        else:
            targetffcmain1_pn = ""
            targetffcmain1_qty = ""
            targetffcmain1_level = ""
            targetffcmain1_uit = ""
            targetffcmain1_supplytype = ""
            targetffcmain1_state = ""
            targetffcmain1_parttype = ""
            targetffcmain1_spec = ""
            targetffcmain1_uniquieid = ""
        if len(targets_ffc) >= 2:
            targetffcmain2_pn = targets_ffc[1]["pn"]
            targetffcmain2_qty = targets_ffc[1]["qty"]
            targetffcmain2_level = targets_ffc[1]["level"]
            targetffcmain2_uit = targets_ffc[1]["uit"]
            targetffcmain2_supplytype = targets_ffc[1]["supplytype"]
            targetffcmain2_state = targets_ffc[1]["state"]
            targetffcmain2_parttype = targets_ffc[1]["parttype"]
            targetffcmain2_spec = targets_ffc[1]["spec"]
            targetffcmain2_uniquieid = targets_ffc[1]["uniqueid"]
        else:
            targetffcmain2_pn = ""
            targetffcmain2_qty = ""
            targetffcmain2_level = ""
            targetffcmain2_uit = ""
            targetffcmain2_supplytype = ""
            targetffcmain2_state = ""
            targetffcmain2_parttype = ""
            targetffcmain2_spec = ""
            targetffcmain2_uniquieid = ""
        #<Search for specific components in EBOM data (EBT Power Cord)
        EBT_Powercord = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == "00001" and
                "EBT" in "{}".format(item.get("childNameDisplay", "")) and 
                "Chassis Assembly,Sub" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("P_Cord Assy" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or 
                "Power Cord" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "Powercord" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "P_Cord" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not EBT_Powercord.empty:
            for idx, row in EBT_Powercord.iterrows():
                targetebtpowercord_pn = row['childNameDisplay']
                targetebtpowercord_qty = row['bomQuantity']
                targetebtpowercord_level = row['bomLevel']
                targetebtpowercord_uit = row['outData.mr_userItemType']
                targetebtpowercord_supplytype = row['supplyType']
                targetebtpowercord_state = row['outData.pp_states']
                targetebtpowercord_parttype = row['dataType']
                targetebtpowercord_spec = row['outData.mr_siteTechnicalSpec']
                targetebtpowercord_uniquieid = row['uniqueStr']
            targetebtpowercord_pn = EBT_Powercord['childNameDisplay'].iloc[0]
            targetebtpowercord_qty = EBT_Powercord['bomQuantity'].iloc[0]
            targetebtpowercord_level = EBT_Powercord['bomLevel'].iloc[0]        
            targetebtpowercord_uit = EBT_Powercord['outData.mr_userItemType'].iloc[0]
            targetebtpowercord_supplytype = EBT_Powercord['supplyType'].iloc[0]
            targetebtpowercord_state = EBT_Powercord['outData.pp_states'].iloc[0]
            targetebtpowercord_parttype = EBT_Powercord['dataType'].iloc[0]
            targetebtpowercord_spec = EBT_Powercord['outData.mr_siteTechnicalSpec'].iloc[0]
            targetebtpowercord_uniquieid = EBT_Powercord['uniqueStr'].iloc[0]
        else:
            targetebtpowercord_pn = ""
            targetebtpowercord_qty = ""
            targetebtpowercord_level = ""
            targetebtpowercord_uit = ""
            targetebtpowercord_supplytype = ""
            targetebtpowercord_state = ""
            targetebtpowercord_parttype = ""
            targetebtpowercord_spec = ""
            targetebtpowercord_uniquieid = ""
        #<Search for specific components in EBOM data (Power Cord Attach)
        Powercord_attach = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtpowercord_uniquieid and
                "EAD" in "{}".format(item.get("childNameDisplay", "")) and 
                "Power Cord,Attach" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("AT" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Powercord_attach.empty:
            for idx, row in Powercord_attach.iterrows():
                targetpowercordattach_pn = row['childNameDisplay']
                targetpowercordattach_qty = row['bomQuantity']
                targetpowercordattach_level = row['bomLevel']
                targetpowercordattach_uit = row['outData.mr_userItemType']
                targetpowercordattach_supplytype = row['supplyType']
                targetpowercordattach_state = row['outData.pp_states']
                targetpowercordattach_parttype = row['dataType']
                targetpowercordattach_spec = row['outData.mr_siteTechnicalSpec']
                targetpowercordattach_uniquieid = row['uniqueStr']
            targetpowercordattach_pn = Powercord_attach['childNameDisplay'].iloc[0]
            targetpowercordattach_qty = Powercord_attach['bomQuantity'].iloc[0]
            targetpowercordattach_level = Powercord_attach['bomLevel'].iloc[0]        
            targetpowercordattach_uit = Powercord_attach['outData.mr_userItemType'].iloc[0]
            targetpowercordattach_supplytype = Powercord_attach['supplyType'].iloc[0]
            targetpowercordattach_state = Powercord_attach['outData.pp_states'].iloc[0]
            targetpowercordattach_parttype = Powercord_attach['dataType'].iloc[0]
            targetpowercordattach_spec = Powercord_attach['outData.mr_siteTechnicalSpec'].iloc[0]
            targetpowercordattach_uniquieid = Powercord_attach['uniqueStr'].iloc[0]
        else:
            targetpowercordattach_pn = ""
            targetpowercordattach_qty = ""
            targetpowercordattach_level = ""
            targetpowercordattach_uit = ""
            targetpowercordattach_supplytype = ""
            targetpowercordattach_state = ""
            targetpowercordattach_parttype = ""
            targetpowercordattach_spec = ""
            targetpowercordattach_uniquieid = ""
        #<Search for specific components in EBOM data (Power Cord Detach)
        Powercord_detach = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                "EAD" in "{}".format(item.get("childNameDisplay", "")) and 
                "Power Cord,Detach" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("DE" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Powercord_detach.empty:
            for idx, row in Powercord_detach.iterrows():
                targetpowercorddetach_pn = row['childNameDisplay']
                targetpowercorddetach_qty = row['bomQuantity']
                targetpowercorddetach_level = row['bomLevel']
                targetpowercorddetach_uit = row['outData.mr_userItemType']
                targetpowercorddetach_supplytype = row['supplyType']
                targetpowercorddetach_state = row['outData.pp_states']
                targetpowercorddetach_parttype = row['dataType']
                targetpowercorddetach_spec = row['outData.mr_siteTechnicalSpec']
                targetpowercorddetach_uniquieid = row['uniqueStr']
            targetpowercorddetach_pn = Powercord_detach['childNameDisplay'].iloc[0]
            targetpowercorddetach_qty = Powercord_detach['bomQuantity'].iloc[0]
            targetpowercorddetach_level = Powercord_detach['bomLevel'].iloc[0]        
            targetpowercorddetach_uit = Powercord_detach['outData.mr_userItemType'].iloc[0]
            targetpowercorddetach_supplytype = Powercord_detach['supplyType'].iloc[0]
            targetpowercorddetach_state = Powercord_detach['outData.pp_states'].iloc[0]
            targetpowercorddetach_parttype = Powercord_detach['dataType'].iloc[0]
            targetpowercorddetach_spec = Powercord_detach['outData.mr_siteTechnicalSpec'].iloc[0]
            targetpowercorddetach_uniquieid = Powercord_detach['uniqueStr'].iloc[0]
        else:
            targetpowercorddetach_pn = ""
            targetpowercorddetach_qty = ""
            targetpowercorddetach_level = ""
            targetpowercorddetach_uit = ""
            targetpowercorddetach_supplytype = ""
            targetpowercorddetach_state = ""
            targetpowercorddetach_parttype = ""
            targetpowercorddetach_spec = ""
            targetpowercorddetach_uniquieid = ""
        #<Search for specific components in EBOM data (Power Board)
        Power_Board = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == "00001" and
                ("EAY" in "{}".format(item.get("childNameDisplay", "")) or
                "EBR" in "{}".format(item.get("childNameDisplay", ""))) and
                "Power" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("LGP" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Power_Board.empty:
            for idx, row in Power_Board.iterrows():
                targetpowerboard_pn = row['childNameDisplay']
                targetpowerboard_qty = row['bomQuantity']
                targetpowerboard_level = row['bomLevel']
                targetpowerboard_uit = row['outData.mr_userItemType']
                targetpowerboard_supplytype = row['supplyType']
                targetpowerboard_state = row['outData.pp_states']
                targetpowerboard_parttype = row['dataType']
                targetpowerboard_spec = row['outData.mr_siteTechnicalSpec']
                targetpowerboard_uniquieid = row['uniqueStr']
            targetpowerboard_pn = Power_Board['childNameDisplay'].iloc[0]
            targetpowerboard_qty = Power_Board['bomQuantity'].iloc[0]
            targetpowerboard_level = Power_Board['bomLevel'].iloc[0]
            targetpowerboard_uit = Power_Board['outData.mr_userItemType'].iloc[0]
            targetpowerboard_supplytype = Power_Board['supplyType'].iloc[0]
            targetpowerboard_state = Power_Board['outData.pp_states'].iloc[0]
            targetpowerboard_parttype = Power_Board['dataType'].iloc[0]
            targetpowerboard_spec = Power_Board['outData.mr_siteTechnicalSpec'].iloc[0]
            targetpowerboard_uniquieid = Power_Board['uniqueStr'].iloc[0]
        else:
            targetpowerboard_pn = ""
            targetpowerboard_qty = ""
            targetpowerboard_level = ""
            targetpowerboard_uit = ""
            targetpowerboard_supplytype = ""
            targetpowerboard_state = ""
            targetpowerboard_parttype = ""
            targetpowerboard_spec = ""
            targetpowerboard_uniquieid = ""
        #<Search for specific components in EBOM data (EBT Main)
        EBT_Main = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == "00001" and
                "EBT" in "{}".format(item.get("childNameDisplay", "")) and 
                "Chassis Assembly" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("MAIN" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not EBT_Main.empty:
            for idx, row in EBT_Main.iterrows():
                targetebtmain_pn = row['childNameDisplay']
                targetebtmain_qty = row['bomQuantity']
                targetebtmain_level = row['bomLevel']
                targetebtmain_uit = row['outData.mr_userItemType']
                targetebtmain_supplytype = row['supplyType']
                targetebtmain_state = row['outData.pp_states']
                targetebtmain_parttype = row['dataType']
                targetebtmain_spec = row['outData.mr_siteTechnicalSpec']
                targetebtmain_uniquieid = row['uniqueStr']
            targetebtmain_pn = EBT_Main['childNameDisplay'].iloc[0]
            targetebtmain_qty = EBT_Main['bomQuantity'].iloc[0]
            targetebtmain_level = EBT_Main['bomLevel'].iloc[0]
            targetebtmain_uit = EBT_Main['outData.mr_userItemType'].iloc[0]
            targetebtmain_supplytype = EBT_Main['supplyType'].iloc[0]
            targetebtmain_state = EBT_Main['outData.pp_states'].iloc[0]
            targetebtmain_parttype = EBT_Main['dataType'].iloc[0]
            targetebtmain_spec = EBT_Main['outData.mr_siteTechnicalSpec'].iloc[0]
            targetebtmain_uniquieid = EBT_Main['uniqueStr'].iloc[0]
        else:
            targetebtmain_pn = ""
            targetebtmain_qty = ""
            targetebtmain_level = ""
            targetebtmain_uit = ""
            targetebtmain_supplytype = ""
            targetebtmain_state = ""
            targetebtmain_parttype = ""
            targetebtmain_spec = ""
            targetebtmain_uniquieid = ""
        #<Search for specific components in EBOM data (Tuner Case Cover)
        Holder_main = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtmain_uniquieid and
                "MEG" in "{}".format(item.get("childNameDisplay", "")) and 
                "Holder" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Holder" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Holder_main.empty:
            for idx, row in Holder_main.iterrows():
                targetholdermain_pn = row['childNameDisplay']
                targetholdermain_qty = row['bomQuantity']
                targetholdermain_level = row['bomLevel']
                targetholdermain_uit = row['outData.mr_userItemType']
                targetholdermain_supplytype = row['supplyType']
                targetholdermain_state = row['outData.pp_states']
                targetholdermain_parttype = row['dataType']
                targetholdermain_spec = row['outData.mr_siteTechnicalSpec']
                targetholdermain_uniquieid = row['uniqueStr']
            targetholdermain_pn = Holder_main['childNameDisplay'].iloc[0]
            targetholdermain_qty = Holder_main['bomQuantity'].iloc[0]
            targetholdermain_level = Holder_main['bomLevel'].iloc[0]
            targetholdermain_uit = Holder_main['outData.mr_userItemType'].iloc[0]
            targetholdermain_supplytype = Holder_main['supplyType'].iloc[0]
            targetholdermain_state = Holder_main['outData.pp_states'].iloc[0]
            targetholdermain_parttype = Holder_main['dataType'].iloc[0]
            targetholdermain_spec = Holder_main['outData.mr_siteTechnicalSpec'].iloc[0]
            targetholdermain_uniquieid = Holder_main['uniqueStr'].iloc[0]
        else:
            targetholdermain_pn = ""
            targetholdermain_qty = ""
            targetholdermain_level = ""
            targetholdermain_uit = ""
            targetholdermain_supplytype = ""
            targetholdermain_state = ""
            targetholdermain_parttype = ""
            targetholdermain_spec = ""
            targetholdermain_uniquieid = ""
        #<Search for specific components in EBOM data (Tuner Case Cover)
        Tuner_cover = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtmain_uniquieid and
                "EBZ" in "{}".format(item.get("childNameDisplay", "")) and 
                "Part" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Tuner" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Tuner_cover.empty:
            for idx, row in Tuner_cover.iterrows():
                targettunercover_pn = row['childNameDisplay']
                targettunercover_qty = row['bomQuantity']
                targettunercover_level = row['bomLevel']
                targettunercover_uit = row['outData.mr_userItemType']
                targettunercover_supplytype = row['supplyType']
                targettunercover_state = row['outData.pp_states']
                targettunercover_parttype = row['dataType']
                targettunercover_spec = row['outData.mr_siteTechnicalSpec']
                targettunercover_uniquieid = row['uniqueStr']
            targettunercover_pn = Tuner_cover['childNameDisplay'].iloc[0]
            targettunercover_qty = Tuner_cover['bomQuantity'].iloc[0]
            targettunercover_level = Tuner_cover['bomLevel'].iloc[0]
            targettunercover_uit = Tuner_cover['outData.mr_userItemType'].iloc[0]
            targettunercover_supplytype = Tuner_cover['supplyType'].iloc[0]
            targettunercover_state = Tuner_cover['outData.pp_states'].iloc[0]
            targettunercover_parttype = Tuner_cover['dataType'].iloc[0]
            targettunercover_spec = Tuner_cover['outData.mr_siteTechnicalSpec'].iloc[0]
            targettunercover_uniquieid = Tuner_cover['uniqueStr'].iloc[0]
        else:
            targettunercover_pn = ""
            targettunercover_qty = ""
            targettunercover_level = ""
            targettunercover_uit = ""
            targettunercover_supplytype = ""
            targettunercover_state = ""
            targettunercover_parttype = ""
            targettunercover_spec = ""
            targettunercover_uniquieid = ""
        #<Search for specific components in EBOM data (Transparent Tape)
        Transparent_Tape = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtmain_uniquieid and
                "961" in "{}".format(item.get("childNameDisplay", "")) and 
                "Tape,Glass Fiber" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("961" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Transparent_Tape.empty:
            for idx, row in Transparent_Tape.iterrows():
                targettransparenttape_pn = row['childNameDisplay']
                targettransparenttape_qty = row['bomQuantity']
                targettransparenttape_level = row['bomLevel']
                targettransparenttape_uit = row['outData.mr_userItemType']
                targettransparenttape_supplytype = row['supplyType']
                targettransparenttape_state = row['outData.pp_states']
                targettransparenttape_parttype = row['dataType']
                targettransparenttape_spec = row['outData.mr_siteTechnicalSpec']
                targettransparenttape_uniquieid = row['uniqueStr']
        else:
            targettransparenttape_pn = ""
            targettransparenttape_qty = ""
            targettransparenttape_level = ""
            targettransparenttape_uit = ""
            targettransparenttape_supplytype = ""
            targettransparenttape_state = ""
            targettransparenttape_parttype = ""
            targettransparenttape_spec = ""
            targettransparenttape_uniquieid = ""
        #<Search for specific components in EBOM data (Harness Single)
        Harness_Single = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtmain_uniquieid and
                "EAD" in "{}".format(item.get("childNameDisplay", "")) and 
                "Harness,Single" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("SMH" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Harness_Single.empty:
            for idx, row in Harness_Single.iterrows():
                targetharnesssingle_pn = row['childNameDisplay']
                targetharnesssingle_qty = row['bomQuantity']
                targetharnesssingle_level = row['bomLevel']
                targetharnesssingle_uit = row['outData.mr_userItemType']
                targetharnesssingle_supplytype = row['supplyType']
                targetharnesssingle_state = row['outData.pp_states']
                targetharnesssingle_parttype = row['dataType']
                targetharnesssingle_spec = row['outData.mr_siteTechnicalSpec']
                targetharnesssingle_uniquieid = row['uniqueStr']
            targetharnesssingle_pn = Harness_Single['childNameDisplay'].iloc[0]
            targetharnesssingle_qty = Harness_Single['bomQuantity'].iloc[0]
            targetharnesssingle_level = Harness_Single['bomLevel'].iloc[0]
            targetharnesssingle_uit = Harness_Single['outData.mr_userItemType'].iloc[0]
            targetharnesssingle_supplytype = Harness_Single['supplyType'].iloc[0]
            targetharnesssingle_state = Harness_Single['outData.pp_states'].iloc[0]
            targetharnesssingle_parttype = Harness_Single['dataType'].iloc[0]
            targetharnesssingle_spec = Harness_Single['outData.mr_siteTechnicalSpec'].iloc[0]
            targetharnesssingle_uniquieid = Harness_Single['uniqueStr'].iloc[0]
        else:
            targetharnesssingle_pn = ""
            targetharnesssingle_qty = ""
            targetharnesssingle_level = ""
            targetharnesssingle_uit = ""
            targetharnesssingle_supplytype = ""
            targetharnesssingle_state = ""
            targetharnesssingle_parttype = ""
            targetharnesssingle_spec = ""
            targetharnesssingle_uniquieid = ""
        #<Search for specific components in EBOM data (Harness Multi)
        Harness_Multi = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtmain_uniquieid and
                "EAD" in "{}".format(item.get("childNameDisplay", "")) and 
                "Harness,Multi" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("250A1" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Harness_Multi.empty:
            for idx, row in Harness_Multi.iterrows():
                targetharnessmulti_pn = row['childNameDisplay']
                targetharnessmulti_qty = row['bomQuantity']
                targetharnessmulti_level = row['bomLevel']
                targetharnessmulti_uit = row['outData.mr_userItemType']
                targetharnessmulti_supplytype = row['supplyType']
                targetharnessmulti_state = row['outData.pp_states']
                targetharnessmulti_parttype = row['dataType']
                targetharnessmulti_spec = row['outData.mr_siteTechnicalSpec']
                targetharnessmulti_uniquieid = row['uniqueStr']
            targetharnessmulti_pn = Harness_Multi['childNameDisplay'].iloc[0]
            targetharnessmulti_qty = Harness_Multi['bomQuantity'].iloc[0]
            targetharnessmulti_level = Harness_Multi['bomLevel'].iloc[0]
            targetharnessmulti_uit = Harness_Multi['outData.mr_userItemType'].iloc[0]
            targetharnessmulti_supplytype = Harness_Multi['supplyType'].iloc[0]
            targetharnessmulti_state = Harness_Multi['outData.pp_states'].iloc[0]
            targetharnessmulti_parttype = Harness_Multi['dataType'].iloc[0]
            targetharnessmulti_spec = Harness_Multi['outData.mr_siteTechnicalSpec'].iloc[0]
            targetharnessmulti_uniquieid = Harness_Multi['uniqueStr'].iloc[0]
        else:
            targetharnessmulti_pn = ""
            targetharnessmulti_qty = ""
            targetharnessmulti_level = ""
            targetharnessmulti_uit = ""
            targetharnessmulti_supplytype = ""
            targetharnessmulti_state = ""
            targetharnessmulti_parttype = ""
            targetharnessmulti_spec = ""
            targetharnessmulti_uniquieid = ""
        #<Search for specific components in EBOM data (Plate Shield Assy)
        Plate_Shield = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtmain_uniquieid and
                "EBS" in "{}".format(item.get("childNameDisplay", "")) and 
                "Electric Parts Assembly,Main" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Shield" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "Plate" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Plate_Shield.empty:
            for idx, row in Plate_Shield.iterrows():
                targetplateshield_pn = row['childNameDisplay']
                targetplateshield_qty = row['bomQuantity']
                targetplateshield_level = row['bomLevel']
                targetplateshield_uit = row['outData.mr_userItemType']
                targetplateshield_supplytype = row['supplyType']
                targetplateshield_state = row['outData.pp_states']
                targetplateshield_parttype = row['dataType']
                targetplateshield_spec = row['outData.mr_siteTechnicalSpec']
                targetplateshield_uniquieid = row['uniqueStr']
            targetplateshield_pn = Plate_Shield['childNameDisplay'].iloc[0]
            targetplateshield_qty = Plate_Shield['bomQuantity'].iloc[0]
            targetplateshield_level = Plate_Shield['bomLevel'].iloc[0]
            targetplateshield_uit = Plate_Shield['outData.mr_userItemType'].iloc[0]
            targetplateshield_supplytype = Plate_Shield['supplyType'].iloc[0]
            targetplateshield_state = Plate_Shield['outData.pp_states'].iloc[0]
            targetplateshield_parttype = Plate_Shield['dataType'].iloc[0]
            targetplateshield_spec = Plate_Shield['outData.mr_siteTechnicalSpec'].iloc[0]
            targetplateshield_uniquieid = Plate_Shield['uniqueStr'].iloc[0]
        else:
            targetplateshield_pn = ""
            targetplateshield_qty = ""
            targetplateshield_level = ""
            targetplateshield_uit = ""
            targetplateshield_supplytype = ""
            targetplateshield_state = ""
            targetplateshield_parttype = ""
            targetplateshield_spec = ""
            targetplateshield_uniquieid = ""
        #<Search for specific components in EBOM data (Plate Shield)
        Plate_Sink = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetplateshield_uniquieid and
                "MED" in "{}".format(item.get("childNameDisplay", "")) or 
                "MGJ" in "{}".format(item.get("childNameDisplay", ""))
                ))
            ])
        if not Plate_Sink.empty:
            for idx, row in Plate_Sink.iterrows():
                targetplatesink_pn = row['childNameDisplay']
                targetplatesink_qty = row['bomQuantity']
                targetplatesink_level = row['bomLevel']
                targetplatesink_uit = row['outData.mr_userItemType']
                targetplatesink_supplytype = row['supplyType']
                targetplatesink_state = row['outData.pp_states']
                targetplatesink_parttype = row['dataType']
                targetplatesink_spec = row['outData.mr_siteTechnicalSpec']
                targetplatesink_uniquieid = row['uniqueStr']
            targetplatesink_pn = Plate_Sink['childNameDisplay'].iloc[0]
            targetplatesink_qty = Plate_Sink['bomQuantity'].iloc[0]
            targetplatesink_level = Plate_Sink['bomLevel'].iloc[0]
            targetplatesink_uit = Plate_Sink['outData.mr_userItemType'].iloc[0]
            targetplatesink_supplytype = Plate_Sink['supplyType'].iloc[0]
            targetplatesink_state = Plate_Sink['outData.pp_states'].iloc[0]
            targetplatesink_parttype = Plate_Sink['dataType'].iloc[0]
            targetplatesink_spec = Plate_Sink['outData.mr_siteTechnicalSpec'].iloc[0]
            targetplatesink_uniquieid = Plate_Sink['uniqueStr'].iloc[0]
        else:
            targetplatesink_pn = ""
            targetplatesink_qty = ""
            targetplatesink_level = ""
            targetplatesink_uit = ""
            targetplatesink_supplytype = ""
            targetplatesink_state = ""
            targetplatesink_parttype = ""
            targetplatesink_spec = ""
            targetplatesink_uniquieid = ""
        #<Search for specific components in EBOM data (Plate Holder)
        Plate_Holder = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetplateshield_uniquieid and
                "MEG" in "{}".format(item.get("childNameDisplay", "")) and
                "Holder" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))
                ))
            ])
        if not Plate_Holder.empty:
            for idx, row in Plate_Holder.iterrows():
                targetplateholder_pn = row['childNameDisplay']
                targetplateholder_qty = row['bomQuantity']
                targetplateholder_level = row['bomLevel']
                targetplateholder_uit = row['outData.mr_userItemType']
                targetplateholder_supplytype = row['supplyType']
                targetplateholder_state = row['outData.pp_states']
                targetplateholder_parttype = row['dataType']
                targetplateholder_spec = row['outData.mr_siteTechnicalSpec']
                targetplateholder_uniquieid = row['uniqueStr']
            targetplateholder_pn = Plate_Holder['childNameDisplay'].iloc[0]
            targetplateholder_qty = Plate_Holder['bomQuantity'].iloc[0]
            targetplateholder_level = Plate_Holder['bomLevel'].iloc[0]
            targetplateholder_uit = Plate_Holder['outData.mr_userItemType'].iloc[0]
            targetplateholder_supplytype = Plate_Holder['supplyType'].iloc[0]
            targetplateholder_state = Plate_Holder['outData.pp_states'].iloc[0]
            targetplateholder_parttype = Plate_Holder['dataType'].iloc[0]
            targetplateholder_spec = Plate_Holder['outData.mr_siteTechnicalSpec'].iloc[0]
            targetplateholder_uniquieid = Plate_Holder['uniqueStr'].iloc[0]
        else:
            targetplateholder_pn = ""
            targetplateholder_qty = ""
            targetplateholder_level = ""
            targetplateholder_uit = ""
            targetplateholder_supplytype = ""
            targetplateholder_state = ""
            targetplateholder_parttype = ""
            targetplateholder_spec = ""
            targetplateholder_uniquieid = ""
        #<Search for specific components in EBOM data (Sheet Cooper)
        Sheet_Cooper = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetplateshield_uniquieid and
                "RAA" in "{}".format(item.get("childNameDisplay", "")) and
                "Sheet,Copper" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))
                ))
            ])
        if not Sheet_Cooper.empty:
            for idx, row in Sheet_Cooper.iterrows():
                targetsheetcooper_pn = row['childNameDisplay']
                targetsheetcooper_qty = row['bomQuantity']
                targetsheetcooper_level = row['bomLevel']
                targetsheetcooper_uit = row['outData.mr_userItemType']
                targetsheetcooper_supplytype = row['supplyType']
                targetsheetcooper_state = row['outData.pp_states']
                targetsheetcooper_parttype = row['dataType']
                targetsheetcooper_spec = row['outData.mr_siteTechnicalSpec']
                targetsheetcooper_uniquieid = row['uniqueStr']
            targetsheetcooper_pn = Sheet_Cooper['childNameDisplay'].iloc[0]
            targetsheetcooper_qty = Sheet_Cooper['bomQuantity'].iloc[0]
            targetsheetcooper_level = Sheet_Cooper['bomLevel'].iloc[0]
            targetsheetcooper_uit = Sheet_Cooper['outData.mr_userItemType'].iloc[0]
            targetsheetcooper_supplytype = Sheet_Cooper['supplyType'].iloc[0]
            targetsheetcooper_state = Sheet_Cooper['outData.pp_states'].iloc[0]
            targetsheetcooper_parttype = Sheet_Cooper['dataType'].iloc[0]
            targetsheetcooper_spec = Sheet_Cooper['outData.mr_siteTechnicalSpec'].iloc[0]
            targetsheetcooper_uniquieid = Sheet_Cooper['uniqueStr'].iloc[0]
        else:
            targetsheetcooper_pn = ""
            targetsheetcooper_qty = ""
            targetsheetcooper_level = ""
            targetsheetcooper_uit = ""
            targetsheetcooper_supplytype = ""
            targetsheetcooper_state = ""
            targetsheetcooper_parttype = ""
            targetsheetcooper_spec = ""
            targetsheetcooper_uniquieid = ""
        #<Search for specific components in EBOM data (EBR Package)
        EBR_Package = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtmain_uniquieid and
                "EBR" in "{}".format(item.get("childNameDisplay", "")) and 
                "PCB Assembly,Main" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("PAKING" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not EBR_Package.empty:
            for idx, row in EBR_Package.iterrows():
                targetebrpackage_pn = row['childNameDisplay']
                targetebrpackage_qty = row['bomQuantity']
                targetebrpackage_level = row['bomLevel']
                targetebrpackage_uit = row['outData.mr_userItemType']
                targetebrpackage_supplytype = row['supplyType']
                targetebrpackage_state = row['outData.pp_states']
                targetebrpackage_parttype = row['dataType']
                targetebrpackage_spec = row['outData.mr_siteTechnicalSpec']
                targetebrpackage_uniquieid = row['uniqueStr']
            targetebrpackage_pn = EBR_Package['childNameDisplay'].iloc[0]
            targetebrpackage_qty = EBR_Package['bomQuantity'].iloc[0]
            targetebrpackage_level = EBR_Package['bomLevel'].iloc[0]
            targetebrpackage_uit = EBR_Package['outData.mr_userItemType'].iloc[0]
            targetebrpackage_supplytype = EBR_Package['supplyType'].iloc[0]
            targetebrpackage_state = EBR_Package['outData.pp_states'].iloc[0]
            targetebrpackage_parttype = EBR_Package['dataType'].iloc[0]
            targetebrpackage_spec = EBR_Package['outData.mr_siteTechnicalSpec'].iloc[0]
            targetebrpackage_uniquieid = EBR_Package['uniqueStr'].iloc[0]
        else:
            targetebrpackage_pn = ""
            targetebrpackage_qty = ""
            targetebrpackage_level = ""
            targetebrpackage_uit = ""
            targetebrpackage_supplytype = ""
            targetebrpackage_state = ""
            targetebrpackage_parttype = ""
            targetebrpackage_spec = ""
            targetebrpackage_uniquieid = ""
        #<Search for specific components in EBOM data (EBR Package)
        Main_Package = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebrpackage_uniquieid and
                "AGF" in "{}".format(item.get("childNameDisplay", "")) and 
                "Package Assembly" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Package" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Main_Package.empty:
            for idx, row in Main_Package.iterrows():
                targetmainpackage_pn = row['childNameDisplay']
                targetmainpackage_qty = row['bomQuantity']
                targetmainpackage_level = row['bomLevel']
                targetmainpackage_uit = row['outData.mr_userItemType']
                targetmainpackage_supplytype = row['supplyType']
                targetmainpackage_state = row['outData.pp_states']
                targetmainpackage_parttype = row['dataType']
                targetmainpackage_spec = row['outData.mr_siteTechnicalSpec']
                targetmainpackage_uniquieid = row['uniqueStr']
            targetmainpackage_pn = Main_Package['childNameDisplay'].iloc[0]
            targetmainpackage_qty = Main_Package['bomQuantity'].iloc[0]
            targetmainpackage_level = Main_Package['bomLevel'].iloc[0]
            targetmainpackage_uit = Main_Package['outData.mr_userItemType'].iloc[0]
            targetmainpackage_supplytype = Main_Package['supplyType'].iloc[0]
            targetmainpackage_state = Main_Package['outData.pp_states'].iloc[0]
            targetmainpackage_parttype = Main_Package['dataType'].iloc[0]
            targetmainpackage_spec = Main_Package['outData.mr_siteTechnicalSpec'].iloc[0]
            targetmainpackage_uniquieid = Main_Package['uniqueStr'].iloc[0]
        else:
            targetmainpackage_pn = ""
            targetmainpackage_qty = ""
            targetmainpackage_level = ""
            targetmainpackage_uit = ""
            targetmainpackage_supplytype = ""
            targetmainpackage_state = ""
            targetmainpackage_parttype = ""
            targetmainpackage_spec = ""
            targetmainpackage_uniquieid = ""        
        #<Search for specific components in EBOM data (EBU Main)
        is_MRGB9M_model = any(
            "MRGB9M" in item.get("childNameDisplay", "")
            for item in response_data.get("data", [])
        )
        if is_MRGB9M_model:
            #<Search for specific components in EBOM data (EBU Main MRGB9M)
            EBU_Main = pd.json_normalize([
                    item for item in response_data.get("data", [])
                    if (
                        "EBU" in item.get("childNameDisplay", "")
                        and "BPR Total Assembly" in item.get("outData", {}).get("pp_descriptions", "")
                        and "MAIN" in item.get("outData", {}).get("mr_siteTechnicalSpec", "")
                    )
                ])
            if not EBU_Main.empty:
                for idx, row in EBU_Main.iterrows():
                    targetebumain_pn = row['childNameDisplay']
                    targetebumain_qty = row['bomQuantity']
                    targetebumain_level = row['bomLevel']
                    targetebumain_uit = row['outData.mr_userItemType']
                    targetebumain_supplytype = row['supplyType']
                    targetebumain_state = row['outData.pp_states']
                    targetebumain_parttype = row['dataType']
                targetebumain_pn = EBU_Main['childNameDisplay'].iloc[0]
                targetebumain_qty = EBU_Main['bomQuantity'].iloc[0]
                targetebumain_level = EBU_Main['bomLevel'].iloc[0]
                targetebumain_uit = EBU_Main['outData.mr_userItemType'].iloc[0]
                targetebumain_supplytype = EBU_Main['supplyType'].iloc[0]
                targetebumain_state = EBU_Main['outData.pp_states'].iloc[0]
                targetebumain_parttype = EBU_Main['dataType'].iloc[0]
                targetebumain_spec = EBU_Main['outData.mr_siteTechnicalSpec'].iloc[0]
                targetebumain_uniquieid = EBU_Main['uniqueStr'].iloc[0]
            else:
                targetebumain_pn = ""
                targetebumain_qty = ""
                targetebumain_level = ""
                targetebumain_uit = ""
                targetebumain_supplytype = ""
                targetebumain_state = ""
                targetebumain_parttype = ""
                targetebumain_spec = ""
                targetebumain_uniquieid = ""
        else:
            #<Search for specific components in EBOM data (EBU Main)     
            EBU_Main = pd.json_normalize([
                    item for item in response_data.get("data", [])
                    if (
                        item.get("uniqueStrParent") in [
                            targetebtmain_uniquieid,
                            targetebrpackage_uniquieid,
                        ]
                        and "EBU" in item.get("childNameDisplay", "")
                        and "ORP Total Assembly" in item.get("outData", {}).get("pp_descriptions", "")
                        and "MAIN" in item.get("outData", {}).get("mr_siteTechnicalSpec", "")
                    )
                ])
            if not EBU_Main.empty:
                for idx, row in EBU_Main.iterrows():
                    targetebumain_pn = row['childNameDisplay']
                    targetebumain_qty = row['bomQuantity']
                    targetebumain_level = row['bomLevel']
                    targetebumain_uit = row['outData.mr_userItemType']
                    targetebumain_supplytype = row['supplyType']
                    targetebumain_state = row['outData.pp_states']
                    targetebumain_parttype = row['dataType']
                    targetebumain_spec = row['outData.mr_siteTechnicalSpec']
                    targetebumain_uniquieid = row['uniqueStr']
                targetebumain_pn = EBU_Main['childNameDisplay'].iloc[0]
                targetebumain_qty = EBU_Main['bomQuantity'].iloc[0]
                targetebumain_level = EBU_Main['bomLevel'].iloc[0]
                targetebumain_uit = EBU_Main['outData.mr_userItemType'].iloc[0]
                targetebumain_supplytype = EBU_Main['supplyType'].iloc[0]
                targetebumain_state = EBU_Main['outData.pp_states'].iloc[0]
                targetebumain_parttype = EBU_Main['dataType'].iloc[0]
                targetebumain_spec = EBU_Main['outData.mr_siteTechnicalSpec'].iloc[0]
                targetebumain_uniquieid = EBU_Main['uniqueStr'].iloc[0]
            else:
                targetebumain_pn = ""
                targetebumain_qty = ""
                targetebumain_level = ""
                targetebumain_uit = ""
                targetebumain_supplytype = ""
                targetebumain_state = ""
                targetebumain_parttype = ""
                targetebumain_spec = ""
                targetebumain_uniquieid = ""
        #<Search for specific components in EBOM data (EBR Main)
        EBR_Main = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebumain_uniquieid and
                "EBR" in "{}".format(item.get("childNameDisplay", "")) and 
                ("ORP Insert PCB Assembly" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) or
                "BPR Insert PCB Assembly" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))) and
                ("MAIN" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not EBR_Main.empty:
            for idx, row in EBR_Main.iterrows():
                targetebrmain_pn = row['childNameDisplay']
                targetebrmain_qty = row['bomQuantity']
                targetebrmain_level = row['bomLevel']
                targetebrmain_uit = row['outData.mr_userItemType']
                targetebrmain_supplytype = row['supplyType']
                targetebrmain_state = row['outData.pp_states']
                targetebrmain_parttype = row['dataType']
                targetebrmain_spec = row['outData.mr_siteTechnicalSpec']
                targetebrmain_uniquieid = row['uniqueStr']
            targetebrmain_pn = EBR_Main['childNameDisplay'].iloc[0]
            targetebrmain_qty = EBR_Main['bomQuantity'].iloc[0]
            targetebrmain_level = EBR_Main['bomLevel'].iloc[0]
            targetebrmain_uit = EBR_Main['outData.mr_userItemType'].iloc[0]
            targetebrmain_supplytype = EBR_Main['supplyType'].iloc[0]
            targetebrmain_state = EBR_Main['outData.pp_states'].iloc[0]
            targetebrmain_parttype = EBR_Main['dataType'].iloc[0]
            targetebrmain_spec = EBR_Main['outData.mr_siteTechnicalSpec'].iloc[0]
            targetebrmain_uniquieid = EBR_Main['uniqueStr'].iloc[0]
        else:
            targetebrmain_pn = ""
            targetebrmain_qty = ""
            targetebrmain_level = ""
            targetebrmain_uit = ""
            targetebrmain_supplytype = ""
            targetebrmain_state = ""
            targetebrmain_parttype = ""
            targetebrmain_spec = ""
            targetebrmain_uniquieid = ""
        #<Search for specific components in EBOM data (PCB Main)
        PCB_Main = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                # targetebrmain_uniquieid in "{}".format(item.get("uniqueStrParent", "")) and
                "EAX" in "{}".format(item.get("childNameDisplay", "")) and 
                "PCB" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Main" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not PCB_Main.empty:
            for idx, row in PCB_Main.iterrows():
                targetpcbmain_pn = row['childNameDisplay']
                targetpcbmain_qty = row['bomQuantity']
                targetpcbmain_level = row['bomLevel']
                targetpcbmain_uit = row['outData.mr_userItemType']
                targetpcbmain_supplytype = row['supplyType']
                targetpcbmain_state = row['outData.pp_states']
                targetpcbmain_parttype = row['dataType']
                targetpcbmain_spec = row['outData.mr_siteTechnicalSpec']
                targetpcbmain_uniquieid = row['uniqueStr']
            targetpcbmain_pn = PCB_Main['childNameDisplay'].iloc[0]
            targetpcbmain_qty = PCB_Main['bomQuantity'].iloc[0]
            targetpcbmain_level = PCB_Main['bomLevel'].iloc[0]
            targetpcbmain_uit = PCB_Main['outData.mr_userItemType'].iloc[0]
            targetpcbmain_supplytype = PCB_Main['supplyType'].iloc[0]
            targetpcbmain_state = PCB_Main['outData.pp_states'].iloc[0]
            targetpcbmain_parttype = PCB_Main['dataType'].iloc[0]
            targetpcbmain_spec = PCB_Main['outData.mr_siteTechnicalSpec'].iloc[0]
            targetpcbmain_uniquieid = PCB_Main['uniqueStr'].iloc[0]
        else:
            targetpcbmain_pn = ""
            targetpcbmain_qty = ""
            targetpcbmain_level = ""
            targetpcbmain_uit = ""
            targetpcbmain_supplytype = ""
            targetpcbmain_state = ""
            targetpcbmain_parttype = ""
            targetpcbmain_spec = ""
            targetpcbmain_uniquieid = ""
        #<Search for specific components in EBOM data (Wifi Main)
        Wifi_assymain = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                (item.get("uniqueStrParent") == targetebrmain_uniquieid and
                "EAT" in "{}".format(item.get("childNameDisplay", "")) and 
                "Module,Wifi Bluetooth Module" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "LGSW" in "{}".format(item.get("outData", {}).get('mr_siteTechnicalSpec', ""))) or
                (item.get("uniqueStrParent") == targetebrmain_uniquieid and
                "EBR" in "{}".format(item.get("childNameDisplay", "")) and 
                "PCB Assembly,Sub" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "CKD" in "{}".format(item.get("outData", {}).get('mr_siteTechnicalSpec', "")))
                ))
            ])
        if not Wifi_assymain.empty:
            for idx, row in Wifi_assymain.iterrows():
                targetwifiassymain_pn = row['childNameDisplay']
                targetwifiassymain_qty = row['bomQuantity']
                targetwifiassymain_level = row['bomLevel']
                targetwifiassymain_uit = row['outData.mr_userItemType']
                targetwifiassymain_supplytype = row['supplyType']
                targetwifiassymain_state = row['outData.pp_states']
                targetwifiassymain_parttype = row['dataType']
                targetwifiassymain_spec = row['outData.mr_siteTechnicalSpec']
                targetwifiassymain_uniquieid = row['uniqueStr']
            targetwifiassymain_pn = Wifi_assymain['childNameDisplay'].iloc[0]
            targetwifiassymain_qty = Wifi_assymain['bomQuantity'].iloc[0]
            targetwifiassymain_level = Wifi_assymain['bomLevel'].iloc[0]
            targetwifiassymain_uit = Wifi_assymain['outData.mr_userItemType'].iloc[0]
            targetwifiassymain_supplytype = Wifi_assymain['supplyType'].iloc[0]
            targetwifiassymain_state = Wifi_assymain['outData.pp_states'].iloc[0]
            targetwifiassymain_parttype = Wifi_assymain['dataType'].iloc[0]
            targetwifiassymain_spec = Wifi_assymain['outData.mr_siteTechnicalSpec'].iloc[0]
            targetwifiassymain_uniquieid = Wifi_assymain['uniqueStr'].iloc[0]
        else:
            targetwifiassymain_pn = ""
            targetwifiassymain_qty = ""
            targetwifiassymain_level = ""
            targetwifiassymain_uit = ""
            targetwifiassymain_supplytype = ""
            targetwifiassymain_state = ""
            targetwifiassymain_parttype = ""
            targetwifiassymain_spec = ""
            targetwifiassymain_uniquieid = ""    
        #<Search for specific components in EBOM data (EDID)
        EDID = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                "ECC" in "{}".format(item.get("childNameDisplay", "")) and 
                "EDID Check Sum Assembly" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("EDID" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not EDID.empty:
            for idx, row in EDID.iterrows():
                targetedid_pn = row['childNameDisplay']
                targetedid_qty = row['bomQuantity']
                targetedid_level = row['bomLevel']
                targetedid_uit = row['outData.mr_userItemType']
                targetedid_supplytype = row['supplyType']
                targetedid_state = row['outData.pp_states']
                targetedid_parttype = row['dataType']
                targetedid_spec = row['outData.mr_siteTechnicalSpec']
                targetedid_uniquieid = row['uniqueStr']
            targetedid_pn = EDID['childNameDisplay'].iloc[0]
            targetedid_qty = EDID['bomQuantity'].iloc[0]
            targetedid_level = EDID['bomLevel'].iloc[0]
            targetedid_uit = EDID['outData.mr_userItemType'].iloc[0]
            targetedid_supplytype = EDID['supplyType'].iloc[0]
            targetedid_state = EDID['outData.pp_states'].iloc[0]
            targetedid_parttype = EDID['dataType'].iloc[0]
            targetedid_spec = EDID['outData.mr_siteTechnicalSpec'].iloc[0]
            targetedid_uniquieid = EDID['uniqueStr'].iloc[0]
        else:
            targetedid_pn = ""
            targetedid_qty = ""
            targetedid_level = ""
            targetedid_uit = ""
            targetedid_supplytype = ""
            targetedid_state = ""
            targetedid_parttype = ""
            targetedid_spec = ""
            targetedid_uniquieid = ""
        #<Search for specific components in EBOM data (SW Assy)
        SW_Assy = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                "SAB" in "{}".format(item.get("childNameDisplay", "")) and 
                "S/W Package" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("eMMC" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not SW_Assy.empty:
            for idx, row in SW_Assy.iterrows():
                targetswassy_pn = row['childNameDisplay']
                targetswassy_qty = row['bomQuantity']
                targetswassy_level = row['bomLevel']
                targetswassy_uit = row['outData.mr_userItemType']
                targetswassy_supplytype = row['supplyType']
                targetswassy_state = row['outData.pp_states']
                targetswassy_parttype = row['dataType']
                targetswassy_spec = row['outData.mr_siteTechnicalSpec']
                targetswassy_uniquieid = row['uniqueStr']
            targetswassy_pn = SW_Assy['childNameDisplay'].iloc[0]
            targetswassy_qty = SW_Assy['bomQuantity'].iloc[0]
            targetswassy_level = SW_Assy['bomLevel'].iloc[0]
            targetswassy_uit = SW_Assy['outData.mr_userItemType'].iloc[0]
            targetswassy_supplytype = SW_Assy['supplyType'].iloc[0]
            targetswassy_state = SW_Assy['outData.pp_states'].iloc[0]
            targetswassy_parttype = SW_Assy['dataType'].iloc[0]
            targetswassy_spec = SW_Assy['outData.mr_siteTechnicalSpec'].iloc[0]
            targetswassy_uniquieid = SW_Assy['uniqueStr'].iloc[0]
        else:
            targetswassy_pn = ""
            targetswassy_qty = ""
            targetswassy_level = ""
            targetswassy_uit = ""
            targetswassy_supplytype = ""
            targetswassy_state = ""
            targetswassy_parttype = ""
            targetswassy_spec = ""
            targetswassy_uniquieid = ""
        #<Search for specific components in EBOM data (EBU SVC)
        EBU_SVC = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == "00001" and
                "EBU" in "{}".format(item.get("childNameDisplay", "")) and 
                "Mainboard,ORP Total Assembly,SVC" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Main" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not EBU_SVC.empty:
            for idx, row in EBU_SVC.iterrows():
                targetebusvc_pn = row['childNameDisplay']
                targetebusvc_qty = row['bomQuantity']
                targetebusvc_level = row['bomLevel']
                targetebusvc_uit = row['outData.mr_userItemType']
                targetebusvc_supplytype = row['supplyType']
                targetebusvc_state = row['outData.pp_states']
                targetebusvc_parttype = row['dataType']
                targetebusvc_spec = row['outData.mr_siteTechnicalSpec']
                targetebusvc_uniquieid = row['uniqueStr']
            targetebusvc_pn = EBU_SVC['childNameDisplay'].iloc[0]
            targetebusvc_qty = EBU_SVC['bomQuantity'].iloc[0]
            targetebusvc_level = EBU_SVC['bomLevel'].iloc[0]
            targetebusvc_uit = EBU_SVC['outData.mr_userItemType'].iloc[0]
            targetebusvc_supplytype = EBU_SVC['supplyType'].iloc[0]
            targetebusvc_state = EBU_SVC['outData.pp_states'].iloc[0]
            targetebusvc_parttype = EBU_SVC['dataType'].iloc[0]
            targetebusvc_spec = EBU_SVC['outData.mr_siteTechnicalSpec'].iloc[0]
            targetebusvc_uniquieid = EBU_SVC['uniqueStr'].iloc[0]
        else:
            targetebusvc_pn = ""
            targetebusvc_qty = ""
            targetebusvc_level = ""
            targetebusvc_uit = ""
            targetebusvc_supplytype = ""
            targetebusvc_state = ""
            targetebusvc_parttype = ""
            targetebusvc_spec = ""
            targetebusvc_uniquieid = ""
        #<Search for specific components in EBOM data (Tuner Case Cover)
        Tuner_coversvc = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebusvc_uniquieid and
                "EBZ" in "{}".format(item.get("childNameDisplay", "")) and 
                "Part" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Tuner" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Tuner_coversvc.empty:
            for idx, row in Tuner_coversvc.iterrows():
                targettunercoversvc_pn = row['childNameDisplay']
                targettunercoversvc_qty = row['bomQuantity']
                targettunercoversvc_level = row['bomLevel']
                targettunercoversvc_uit = row['outData.mr_userItemType']
                targettunercoversvc_supplytype = row['supplyType']
                targettunercoversvc_state = row['outData.pp_states']
                targettunercoversvc_parttype = row['dataType']
                targettunercoversvc_spec = row['outData.mr_siteTechnicalSpec']
                targettunercoversvc_uniquieid = row['uniqueStr']
            targettunercoversvc_pn = Tuner_coversvc['childNameDisplay'].iloc[0]
            targettunercoversvc_qty = Tuner_coversvc['bomQuantity'].iloc[0]
            targettunercoversvc_level = Tuner_coversvc['bomLevel'].iloc[0]
            targettunercoversvc_uit = Tuner_coversvc['outData.mr_userItemType'].iloc[0]
            targettunercoversvc_supplytype = Tuner_coversvc['supplyType'].iloc[0]
            targettunercoversvc_state = Tuner_coversvc['outData.pp_states'].iloc[0]
            targettunercoversvc_parttype = Tuner_coversvc['dataType'].iloc[0]
            targettunercoversvc_spec = Tuner_coversvc['outData.mr_siteTechnicalSpec'].iloc[0]
            targettunercoversvc_uniquieid = Tuner_coversvc['uniqueStr'].iloc[0]
        else:
            targettunercoversvc_pn = ""
            targettunercoversvc_qty = ""
            targettunercoversvc_level = ""
            targettunercoversvc_uit = ""
            targettunercoversvc_supplytype = ""
            targettunercoversvc_state = ""
            targettunercoversvc_parttype = ""
            targettunercoversvc_spec = ""
            targettunercoversvc_uniquieid = ""
        #<Search for specific components in EBOM data (Tuner Case Cover)
        Holder_svc = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebusvc_uniquieid and
                "MEG" in "{}".format(item.get("childNameDisplay", "")) and 
                "Holder" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Holder" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Holder_svc.empty:
            for idx, row in Holder_svc.iterrows():
                targetholdersvc_pn = row['childNameDisplay']
                targetholdersvc_qty = row['bomQuantity']
                targetholdersvc_level = row['bomLevel']
                targetholdersvc_uit = row['outData.mr_userItemType']
                targetholdersvc_supplytype = row['supplyType']
                targetholdersvc_state = row['outData.pp_states']
                targetholdersvc_parttype = row['dataType']
                targetholdersvc_spec = row['outData.mr_siteTechnicalSpec']
                targetholdersvc_uniquieid = row['uniqueStr']
            targetholdersvc_pn = Holder_svc['childNameDisplay'].iloc[0]
            targetholdersvc_qty = Holder_svc['bomQuantity'].iloc[0]
            targetholdersvc_level = Holder_svc['bomLevel'].iloc[0]
            targetholdersvc_uit = Holder_svc['outData.mr_userItemType'].iloc[0]
            targetholdersvc_supplytype = Holder_svc['supplyType'].iloc[0]
            targetholdersvc_state = Holder_svc['outData.pp_states'].iloc[0]
            targetholdersvc_parttype = Holder_svc['dataType'].iloc[0]
            targetholdersvc_spec = Holder_svc['outData.mr_siteTechnicalSpec'].iloc[0]
            targetholdersvc_uniquieid = Holder_svc['uniqueStr'].iloc[0]
        else:
            targetholdersvc_pn = ""
            targetholdersvc_qty = ""
            targetholdersvc_level = ""
            targetholdersvc_uit = ""
            targetholdersvc_supplytype = ""
            targetholdersvc_state = ""
            targetholdersvc_parttype = ""
            targetholdersvc_spec = ""
            targetholdersvc_uniquieid = ""
        #<Search for specific components in EBOM data (EBR SVC)
        EBR_SVC = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebusvc_uniquieid and
                "EBR" in "{}".format(item.get("childNameDisplay", "")) and 
                "ORP Insert PCB Assembly" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("MAIN" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not EBR_SVC.empty:
            for idx, row in EBR_SVC.iterrows():
                targetebrsvc_pn = row['childNameDisplay']
                targetebrsvc_qty = row['bomQuantity']
                targetebrsvc_level = row['bomLevel']
                targetebrsvc_uit = row['outData.mr_userItemType']
                targetebrsvc_supplytype = row['supplyType'] 
                targetebrsvc_state = row['outData.pp_states']
                targetebrsvc_parttype = row['dataType']
                targetebrsvc_spec = row['outData.mr_siteTechnicalSpec']
                targetebrsvc_uniquieid = row['uniqueStr']
            targetebrsvc_pn = EBR_SVC['childNameDisplay'].iloc[0]
            targetebrsvc_qty = EBR_SVC['bomQuantity'].iloc[0]
            targetebrsvc_level = EBR_SVC['bomLevel'].iloc[0]
            targetebrsvc_uit = EBR_SVC['outData.mr_userItemType'].iloc[0]
            targetebrsvc_supplytype = EBR_SVC['supplyType'].iloc[0]
            targetebrsvc_state = EBR_SVC['outData.pp_states'].iloc[0]
            targetebrsvc_parttype = EBR_SVC['dataType'].iloc[0]
            targetebrsvc_spec = EBR_SVC['outData.mr_siteTechnicalSpec'].iloc[0]
            targetebrsvc_uniquieid = EBR_SVC['uniqueStr'].iloc[0]
        else:
            targetebrsvc_pn = ""
            targetebrsvc_qty = ""
            targetebrsvc_level = ""
            targetebrsvc_uit = ""
            targetebrsvc_supplytype = ""
            targetebrsvc_state = ""
            targetebrsvc_parttype = ""
            targetebrsvc_spec = ""
            targetebrsvc_uniquieid = ""   
        #<Search for specific components in EBOM data (Plate Shield Assy SVC)
        Plate_Shieldsvc = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebusvc_uniquieid and
                "EBS" in "{}".format(item.get("childNameDisplay", "")) and 
                "Electric Parts Assembly,Main" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Shield" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "Plate" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Plate_Shieldsvc.empty:
            for idx, row in Plate_Shieldsvc.iterrows():
                targetplateshieldsvc_pn = row['childNameDisplay']
                targetplateshieldsvc_qty = row['bomQuantity']
                targetplateshieldsvc_level = row['bomLevel']
                targetplateshieldsvc_uit = row['outData.mr_userItemType']
                targetplateshieldsvc_supplytype = row['supplyType']
                targetplateshieldsvc_state = row['outData.pp_states']
                targetplateshieldsvc_parttype = row['dataType']
                targetplateshieldsvc_spec = row['outData.mr_siteTechnicalSpec']
                targetplateshieldsvc_uniquieid = row['uniqueStr']
            targetplateshieldsvc_pn = Plate_Shieldsvc['childNameDisplay'].iloc[0]
            targetplateshieldsvc_qty = Plate_Shieldsvc['bomQuantity'].iloc[0]
            targetplateshieldsvc_level = Plate_Shieldsvc['bomLevel'].iloc[0]
            targetplateshieldsvc_uit = Plate_Shieldsvc['outData.mr_userItemType'].iloc[0]
            targetplateshieldsvc_supplytype = Plate_Shieldsvc['supplyType'].iloc[0]
            targetplateshieldsvc_state = Plate_Shieldsvc['outData.pp_states'].iloc[0]
            targetplateshieldsvc_parttype = Plate_Shieldsvc['dataType'].iloc[0]
            targetplateshieldsvc_spec = Plate_Shieldsvc['outData.mr_siteTechnicalSpec'].iloc[0]
            targetplateshieldsvc_uniquieid = Plate_Shieldsvc['uniqueStr'].iloc[0]
        else:
            targetplateshieldsvc_pn = ""
            targetplateshieldsvc_qty = ""
            targetplateshieldsvc_level = ""
            targetplateshieldsvc_uit = ""
            targetplateshieldsvc_supplytype = ""
            targetplateshieldsvc_state = ""
            targetplateshieldsvc_parttype = ""
            targetplateshieldsvc_spec = ""
            targetplateshieldsvc_uniquieid = ""    
        #<Search for specific components in EBOM data (Wifi SVC)
        Wifi_assysvc = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                targetebrsvc_uniquieid in "{}".format(item.get("uniqueStrParent", "")) and
                "EAT" in "{}".format(item.get("childNameDisplay", "")) and 
                "Module,Wifi Bluetooth Module" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) or
                "LGSW" in "{}".format(item.get("outData", {}).get('mr_siteTechnicalSpec', ""))
                ))
            ])
        if not Wifi_assysvc.empty:
            for idx, row in Wifi_assysvc.iterrows():
                targetwifiassysvc_pn = row['childNameDisplay']
                targetwifiassysvc_qty = row['bomQuantity']
                targetwifiassysvc_level = row['bomLevel']
                targetwifiassysvc_uit = row['outData.mr_userItemType']
                targetwifiassysvc_supplytype = row['supplyType']
                targetwifiassysvc_state = row['outData.pp_states']
                targetwifiassysvc_parttype = row['dataType']
                targetwifiassysvc_spec = row['outData.mr_siteTechnicalSpec']
                targetwifiassysvc_uniquieid = row['uniqueStr']
            targetwifiassysvc_pn = Wifi_assysvc['childNameDisplay'].iloc[0]
            targetwifiassysvc_qty = Wifi_assysvc['bomQuantity'].iloc[0]
            targetwifiassysvc_level = Wifi_assysvc['bomLevel'].iloc[0]
            targetwifiassysvc_uit = Wifi_assysvc['outData.mr_userItemType'].iloc[0]
            targetwifiassysvc_supplytype = Wifi_assysvc['supplyType'].iloc[0]
            targetwifiassysvc_state = Wifi_assysvc['outData.pp_states'].iloc[0]
            targetwifiassysvc_parttype = Wifi_assysvc['dataType'].iloc[0]
            targetwifiassysvc_spec = Wifi_assysvc['outData.mr_siteTechnicalSpec'].iloc[0]
            targetwifiassysvc_uniquieid = Wifi_assysvc['uniqueStr'].iloc[0]
        else:
            targetwifiassysvc_pn = ""
            targetwifiassysvc_qty = ""
            targetwifiassysvc_level = ""
            targetwifiassysvc_uit = ""
            targetwifiassysvc_supplytype = ""
            targetwifiassysvc_state = ""
            targetwifiassysvc_parttype = ""
            targetwifiassysvc_spec = ""
            targetwifiassysvc_uniquieid = ""
        #<Search for specific components in EBOM data (Label)
        Label = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                (item.get("uniqueStrParent") == targetebtmain_uniquieid or
                item.get("uniqueStrParent") == targetebumain_uniquieid or
                item.get("uniqueStrParent") == targetebusvc_uniquieid) and
                "385" in "{}".format(item.get("childNameDisplay", "")) and 
                "Label" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("PRINTING BAR" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Label.empty:
            for idx, row in Label.iterrows():
                targetlabel_pn = row['childNameDisplay']
                targetlabel_qty = row['bomQuantity']
                targetlabel_level = row['bomLevel']
                targetlabel_uit = row['outData.mr_userItemType']
                targetlabel_supplytype = row['supplyType']
                targetlabel_state = row['outData.pp_states']
                targetlabel_parttype = row['dataType']
                targetlabel_spec = row['outData.mr_siteTechnicalSpec']
                targetlabel_uniquieid = row['uniqueStr']
        else:
            targetlabel_pn = ""
            targetlabel_qty = ""
            targetlabel_level = ""
            targetlabel_uit = ""
            targetlabel_supplytype = ""
            targetlabel_state = ""
            targetlabel_parttype = ""
            targetlabel_spec = ""
            targetlabel_uniquieid = ""
        #<Search for specific components in EBOM data (Ribbon)
        Ribbon = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                (item.get("uniqueStrParent") == targetebtmain_uniquieid or
                item.get("uniqueStrParent") == targetebumain_uniquieid or
                item.get("uniqueStrParent") == targetebusvc_uniquieid) and
                "481" in "{}".format(item.get("childNameDisplay", "")) and 
                "Ribbon" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("CUTTING PAPER" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
            ))
            ])
        if not Ribbon.empty:
            for idx, row in Ribbon.iterrows():
                targetribbon_pn = row['childNameDisplay']
                targetribbon_qty = row['bomQuantity']
                targetribbon_level = row['bomLevel']
                targetribbon_uit = row['outData.mr_userItemType']
                targetribbon_supplytype = row['supplyType']
                targetribbon_state = row['outData.pp_states']
                targetribbon_parttype = row['dataType']
                targetribbon_spec = row['outData.mr_siteTechnicalSpec']
                targetribbon_uniquieid = row['uniqueStr']
            targetribbon_pn = Ribbon['childNameDisplay'].iloc[0]
        else:
            targetribbon_pn = ""
            targetribbon_qty = ""
            targetribbon_level = ""
            targetribbon_uit = ""
            targetribbon_supplytype = ""
            targetribbon_state = ""
            targetribbon_parttype = ""
            targetribbon_spec = ""
            targetribbon_uniquieid = ""
        #<Search for specific components in EBOM data (Gasket)
        Gasket = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                (item.get("uniqueStrParent") == "00001" or
                item.get("uniqueStrParent") == targetebtmain_uniquieid) and
                "MDS" in "{}".format(item.get("childNameDisplay", "")) and 
                "Gasket" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))
                ))
            ])
        targets_gasket = [] # tampung semua baris
        if not Gasket.empty:
            for _, row in Gasket.head(5).iterrows():
                targets_gasket.append({
                    "pn":           row.get("childNameDisplay"),
                    "qty":          row.get("bomQuantity"),
                    "level":        row.get("bomLevel"),
                    "uit":          row.get("outData.mr_userItemType"),
                    "supplytype":   row.get("supplyType"),
                    "state":        row.get("outData.pp_states"),
                    "parttype":     row.get("dataType"),
                    "spec":         row.get("outData.mr_siteTechnicalSpec"),
                    "uniqueid":     row.get("uniqueStr"),
                })
        # contoh akses aman:
        if len(targets_gasket) >= 1:
            targetgasket1_pn = targets[0]["pn"]
            targetgasket1_qty = targets[0]["qty"]
            targetgasket1_level = targets[0]["level"]
            targetgasket1_uit = targets[0]["uit"]
            targetgasket1_supplytype = targets[0]["supplytype"]
            targetgasket1_state = targets[0]["state"]
            targetgasket1_parttype = targets[0]["parttype"]
            targetgasket1_spec = targets[0]["spec"]
            targetgasket1_uniquieid = targets[0]["uniqueid"]
        else:
            targetgasket1_pn = ""
            targetgasket1_qty = ""
            targetgasket1_level = ""
            targetgasket1_uit = ""
            targetgasket1_supplytype = ""
            targetgasket1_state = ""
            targetgasket1_parttype = ""
            targetgasket1_spec = ""
            targetgasket1_uniquieid = ""
        if len(targets_gasket) >= 2:
            targetgasket2_pn = targets[1]["pn"]
            targetgasket2_qty = targets[1]["qty"]
            targetgasket2_level = targets[1]["level"]
            targetgasket2_uit = targets[1]["uit"]
            targetgasket2_supplytype = targets[1]["supplytype"]
            targetgasket2_state = targets[1]["state"]
            targetgasket2_parttype = targets[1]["parttype"]
            targetgasket2_spec = targets[1]["spec"]
            targetgasket2_uniquieid = targets[1]["uniqueid"]
        else:   
            targetgasket2_pn = ""
            targetgasket2_qty = ""
            targetgasket2_level = ""
            targetgasket2_uit = ""
            targetgasket2_supplytype = ""
            targetgasket2_state = ""
            targetgasket2_parttype = ""
            targetgasket2_spec = ""
            targetgasket2_uniquieid = ""
        if len(targets_gasket) >= 3:
            targetgasket3_pn = targets[2]["pn"]
            targetgasket3_qty = targets[2]["qty"]
            targetgasket3_level = targets[2]["level"]
            targetgasket3_uit = targets[2]["uit"]
            targetgasket3_supplytype = targets[2]["supplytype"]
            targetgasket3_state = targets[2]["state"]
            targetgasket3_parttype = targets[2]["parttype"]
            targetgasket3_spec = targets[2]["spec"]
            targetgasket3_uniquieid = targets[2]["uniqueid"]
        else:
            targetgasket3_pn = ""
            targetgasket3_qty = ""
            targetgasket3_level = ""
            targetgasket3_uit = ""
            targetgasket3_supplytype = ""
            targetgasket3_state = ""
            targetgasket3_parttype = ""
            targetgasket3_spec = ""
            targetgasket3_uniquieid = ""
        if len(targets_gasket) >= 4:
            targetgasket4_pn = targets[3]["pn"]
            targetgasket4_qty = targets[3]["qty"]
            targetgasket4_level = targets[3]["level"]
            targetgasket4_uit = targets[3]["uit"]
            targetgasket4_supplytype = targets[3]["supplytype"]
            targetgasket4_state = targets[3]["state"]
            targetgasket4_parttype = targets[3]["parttype"]
            targetgasket4_spec = targets[3]["spec"]
            targetgasket4_uniquieid = targets[3]["uniqueid"]
        else:
            targetgasket4_pn = ""
            targetgasket4_qty = ""
            targetgasket4_level = ""
            targetgasket4_uit = ""
            targetgasket4_supplytype = ""
            targetgasket4_state = ""
            targetgasket4_parttype = ""
            targetgasket4_spec = ""
            targetgasket4_uniquieid = ""
        if len(targets_gasket) >= 5:
            targetgasket5_pn = targets[4]["pn"]
            targetgasket5_qty = targets[4]["qty"]
            targetgasket5_level = targets[4]["level"]
            targetgasket5_uit = targets[4]["uit"]
            targetgasket5_supplytype = targets[4]["supplytype"]
            targetgasket5_state = targets[4]["state"]
            targetgasket5_parttype = targets[4]["parttype"]
            targetgasket5_spec = targets[4]["spec"]
            targetgasket5_uniquieid = targets[4]["uniqueid"]
        else:
            targetgasket5_pn = ""
            targetgasket5_qty = ""
            targetgasket5_level = ""
            targetgasket5_uit = ""    
            targetgasket5_supplytype = ""
            targetgasket5_state = ""
            targetgasket5_parttype = ""
            targetgasket5_spec = ""
            targetgasket5_uniquieid = ""
        #<Search for specific components in EBOM data (Tape)
        Tape = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                (item.get("uniqueStrParent") == "00001" or
                item.get("uniqueStrParent") ==targetebtmain_uniquieid) and
                "RAB" in "{}".format(item.get("childNameDisplay", "")) and 
                "Tape" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))
                ))
            ])
        targets_tape = []  # tampung semua baris
        if not Tape.empty:
            for _, row in Gasket.head(5).iterrows():
                targets_tape.append({
                    "pn":           row.get("childNameDisplay"),
                    "qty":          row.get("bomQuantity"),
                    "level":        row.get("bomLevel"),
                    "uit":          row.get("outData.mr_userItemType"),
                    "supplytype":   row.get("supplyType"),
                    "state":        row.get("outData.pp_states"),
                    "parttype":     row.get("dataType"),
                    "spec":         row.get("outData.mr_siteTechnicalSpec"),
                    "uniqueid":     row.get("uniqueStr"),
                })
        # contoh akses aman:
        if len(targets_tape) >= 1:
            targettape1_pn = targets[0]["pn"]
            targettape1_qty = targets[0]["qty"]
            targettape1_level = targets[0]["level"]
            targettape1_uit = targets[0]["uit"]
            targettape1_supplytype = targets[0]["supplytype"]
            targettape1_state = targets[0]["state"]
            targettape1_parttype = targets[0]["parttype"]
            targettape1_spec = targets[0]["spec"]
            targettape1_uniquieid = targets[0]["uniqueid"]
        else:
            targettape1_pn = ""
            targettape1_qty = ""
            targettape1_level = ""
            targettape1_uit = ""
            targettape1_supplytype = ""
            targettape1_state = ""
            targettape1_parttype = ""
            targettape1_spec = ""
            targettape1_uniquieid = ""
        if len(targets_tape) >= 2:
            targettape2_pn = targets[1]["pn"]
            targettape2_qty = targets[1]["qty"]
            targettape2_level = targets[1]["level"]
            targettape2_uit = targets[1]["uit"]
            targettape2_supplytype = targets[1]["supplytype"]
            targettape2_state = targets[1]["state"]
            targettape2_parttype = targets[1]["parttype"]
            targettape2_spec = targets[1]["spec"]
            targettape2_uniquieid = targets[1]["uniqueid"]
        else:
            targettape2_pn = ""
            targettape2_qty = ""
            targettape2_level = ""
            targettape2_uit = ""
            targettape2_supplytype = ""
            targettape2_state = ""
            targettape2_parttype = ""
            targettape2_spec = ""
            targettape2_uniquieid = ""
        if len(targets_tape) >= 3:
            targettape3_pn = targets[2]["pn"]
            targettape3_qty = targets[2]["qty"]
            targettape3_level = targets[2]["level"]
            targettape3_uit = targets[2]["uit"]
            targettape3_supplytype = targets[2]["supplytype"]
            targettape3_state = targets[2]["state"]
            targettape3_parttype = targets[2]["parttype"]
            targettape3_spec = targets[2]["spec"]
            targettape3_uniquieid = targets[2]["uniqueid"]
        else:
            targettape3_pn = ""
            targettape3_qty = ""
            targettape3_level = ""
            targettape3_uit = ""
            targettape3_supplytype = ""
            targettape3_state = ""
            targettape3_parttype = ""
            targettape3_spec = ""
            targettape3_uniquieid = ""
        if len(targets_tape) >= 4:
            targettape4_pn = targets[3]["pn"]
            targettape4_qty = targets[3]["qty"]
            targettape4_level = targets[3]["level"]
            targettape4_uit = targets[3]["uit"]
            targettape4_supplytype = targets[3]["supplytype"]
            targettape4_state = targets[3]["state"]
            targettape4_parttype = targets[3]["parttype"]
            targettape4_spec = targets[3]["spec"]
            targettape4_uniquieid = targets[3]["uniqueid"]
        else:
            targettape4_pn = ""
            targettape4_qty = ""
            targettape4_level = ""
            targettape4_uit = ""
            targettape4_supplytype = ""
            targettape4_state = ""
            targettape4_parttype = ""
            targettape4_spec = ""
            targettape4_uniquieid = ""
        if len(targets_tape) >= 5:
            targettape5_pn = targets[4]["pn"]
            targettape5_qty = targets[4]["qty"]
            targettape5_level = targets[4]["level"]
            targettape5_uit = targets[4]["uit"]
            targettape5_supplytype = targets[4]["supplytype"]
            targettape5_state = targets[4]["state"]
            targettape5_parttype = targets[4]["parttype"]
            targettape5_spec = targets[4]["spec"]
            targettape5_uniquieid = targets[4]["uniqueid"]
        else:
            targettape5_pn = ""
            targettape5_qty = ""
            targettape5_level = ""
            targettape5_uit = ""
            targettape5_supplytype = ""
            targettape5_state = ""
            targettape5_parttype = ""
            targettape5_spec = ""
            targettape5_uniquieid = ""
        #<Search for specific components in EBOM data (Damper)
        Damper = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                (item.get("uniqueStrParent") == "00001" or
                item.get("uniqueStrParent") ==targetebtmain_uniquieid) and
                "MCQ" in "{}".format(item.get("childNameDisplay", "")) and 
                "Damper" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))
                ))
            ])
        targets_damper = []  # tampung semua baris
        if not Damper.empty:
            for _, row in Gasket.head(5).iterrows():
                targets.append({
                    "pn":           row.get("childNameDisplay"),
                    "qty":          row.get("bomQuantity"),
                    "level":        row.get("bomLevel"),
                    "uit":          row.get("outData.mr_userItemType"),
                    "supplytype":   row.get("supplyType"),
                    "state":        row.get("outData.pp_states"),
                    "parttype":     row.get("dataType"),
                    "spec":         row.get("outData.mr_siteTechnicalSpec"),
                    "uniqueid":     row.get("uniqueStr"),
                })
        # contoh akses aman:
        if len(targets_damper) >= 1:
            targetdamper1_pn = targets[0]["pn"]
            targetdamper1_qty = targets[0]["qty"]
            targetdamper1_level = targets[0]["level"]
            targetdamper1_uit = targets[0]["uit"]
            targetdamper1_supplytype = targets[0]["supplytype"]
            targetdamper1_state = targets[0]["state"]
            targetdamper1_parttype = targets[0]["parttype"]
            targetdamper1_spec = targets[0]["spec"]
            targetdamper1_uniquieid = targets[0]["uniqueid"]
        else:
            targetdamper1_pn = ""
            targetdamper1_qty = ""
            targetdamper1_level = ""
            targetdamper1_uit = ""
            targetdamper1_supplytype = ""
            targetdamper1_state = ""
            targetdamper1_parttype = ""
            targetdamper1_spec = ""
            targetdamper1_uniquieid = ""
        if len(targets_damper) >= 2:
            targetdamper2_pn = targets[1]["pn"]
            targetdamper2_qty = targets[1]["qty"]
            targetdamper2_level = targets[1]["level"]
            targetdamper2_uit = targets[1]["uit"]
            targetdamper2_supplytype = targets[1]["supplytype"]
            targetdamper2_state = targets[1]["state"]
            targetdamper2_parttype = targets[1]["parttype"]
            targetdamper2_spec = targets[1]["spec"]
            targetdamper2_uniquieid = targets[1]["uniqueid"]
        else:
            targetdamper2_pn = ""
            targetdamper2_qty = ""
            targetdamper2_level = ""
            targetdamper2_uit = ""
            targetdamper2_supplytype = ""
            targetdamper2_state = ""
            targetdamper2_parttype = ""
            targetdamper2_spec = ""
            targetdamper2_uniquieid = ""
        if len(targets_damper) >= 3:
            targetdamper3_pn = targets[2]["pn"]
            targetdamper3_qty = targets[2]["qty"]
            targetdamper3_level = targets[2]["level"]
            targetdamper3_uit = targets[2]["uit"]
            targetdamper3_supplytype = targets[2]["supplytype"]
            targetdamper3_state = targets[2]["state"]
            targetdamper3_parttype = targets[2]["parttype"]
            targetdamper3_spec = targets[2]["spec"]
            targetdamper3_uniquieid = targets[2]["uniqueid"]
        else:
            targetdamper3_pn = ""
            targetdamper3_qty = ""
            targetdamper3_level = ""
            targetdamper3_uit = ""
            targetdamper3_supplytype = ""
            targetdamper3_state = ""
            targetdamper3_parttype = ""
            targetdamper3_spec = ""
            targetdamper3_uniquieid = ""
        if len(targets_damper) >= 4:
            targetdamper4_pn = targets[3]["pn"]
            targetdamper4_qty = targets[3]["qty"]
            targetdamper4_level = targets[3]["level"]
            targetdamper4_uit = targets[3]["uit"]
            targetdamper4_supplytype = targets[3]["supplytype"]
            targetdamper4_state = targets[3]["state"]
            targetdamper4_parttype = targets[3]["parttype"]
            targetdamper4_spec = targets[3]["spec"]
            targetdamper4_uniquieid = targets[3]["uniqueid"]
        else:
            targetdamper4_pn = ""
            targetdamper4_qty = ""
            targetdamper4_level = ""
            targetdamper4_uit = ""
            targetdamper4_supplytype = ""
            targetdamper4_state = ""
            targetdamper4_parttype = ""
            targetdamper4_spec = ""
            targetdamper4_uniquieid = ""
        if len(targets_damper) >= 5:
            targetdamper5_pn = targets[4]["pn"]
            targetdamper5_qty = targets[4]["qty"]
            targetdamper5_level = targets[4]["level"]
            targetdamper5_uit = targets[4]["uit"]
            targetdamper5_supplytype = targets[4]["supplytype"]
            targetdamper5_state = targets[4]["state"]
            targetdamper5_parttype = targets[4]["parttype"]
            targetdamper5_spec = targets[4]["spec"]
            targetdamper5_uniquieid = targets[4]["uniqueid"]
        else:
            targetdamper5_pn = ""
            targetdamper5_qty = ""
            targetdamper5_level = ""
            targetdamper5_uit = ""
            targetdamper5_supplytype = ""
            targetdamper5_state = ""
            targetdamper5_parttype = ""
            targetdamper5_spec = ""
            targetdamper5_uniquieid = ""
                
        all_hwpart = pd.concat([
            Accesory, Ferrit_core, MR_battery, MR_remote, Lcon_battery, Lcon_remote, 
            Bracket_Assy, EBT_Subassy, Wifi_assy, IR_assy, FFC_assy, Speaker_Right, 
            Speaker_Left, Speaker_assy, FFC_Main, EBT_Powercord, Powercord_attach, 
            Powercord_detach, Power_Board, EBT_Main, Holder_main, Tuner_cover, Transparent_Tape, 
            Harness_Single, Harness_Multi, Plate_Shield, Plate_Sink, Plate_Holder, Sheet_Cooper,
            EBR_Package, Main_Package, EBU_Main, EBR_Main, PCB_Main, Wifi_assymain, EDID, SW_Assy, 
            EBU_SVC, Tuner_coversvc, Holder_svc, EBR_SVC, Plate_Shieldsvc, Wifi_assysvc, 
            Label, Ribbon, Gasket, Tape, Damper
            ], ignore_index=True)
        all_hwpart.to_json("json/1_development_hwpart.json", orient="records", indent=4)
        print("Development Part List saved to 1_target_hwpart.json")
        data = [
            {
                "Category": "EBT Main",
                "Part No": targetebtmain_pn, 
                "Qty": targetebtmain_qty, 
                "Supply Type": targetebtmain_supplytype, 
                "UIT": targetebtmain_uit, 
                "Spec": targetebtmain_spec,
            },
            {
                "Category": "EBT Sub",
                "Part No": targetebtassy_pn, 
                "Qty": targetebtassy_qty, 
                "Supply Type": targetebtassy_supplytype, 
                "UIT": targetebtassy_uit, 
                "Spec": targetebtassy_spec,
            },
            {
                "Category": "EBU Main",
                "Part No": targetebumain_pn, 
                "Qty": targetebumain_qty, 
                "Supply Type": targetebumain_supplytype, 
                "UIT": targetebumain_uit, 
                "Spec": targetebumain_spec,
            },
            {
                "Category": "EBR Main",
                "Part No": targetebrmain_pn, 
                "Qty": targetebrmain_qty, 
                "Supply Type": targetebrmain_supplytype, 
                "UIT": targetebrmain_uit, 
                "Spec": targetebrmain_spec,
            },
            {
                "Category": "SW Assy",
                "Part No": targetswassy_pn, 
                "Qty": targetswassy_qty, 
                "Supply Type": targetswassy_supplytype, 
                "UIT": targetswassy_uit, 
                "Spec": targetswassy_spec,
            },
            {
                "Category": "EDID Check Sum Assembly",
                "Part No": targetedid_pn, 
                "Qty": targetedid_qty, 
                "Supply Type": targetedid_supplytype, 
                "UIT": targetedid_uit, 
                "Spec": targetedid_spec,
            },
            {
                "Category": "Plate Shield Assy",
                "Part No": targetplateshield_pn, 
                "Qty": targetplateshield_qty, 
                "Supply Type": targetplateshield_supplytype, 
                "UIT": targetplateshield_uit, 
                "Spec": targetplateshield_spec,
            },
            {
                "Category": "Shield Plate",
                "Part No": targetplatesink_pn, 
                "Qty": targetplatesink_qty, 
                "Supply Type": targetplatesink_supplytype, 
                "UIT": targetplatesink_uit, 
                "Spec": targetplatesink_spec,
            },
            {
                "Category": "Plate Holder",
                "Part No": targetplateholder_pn, 
                "Qty": targetplateholder_qty, 
                "Supply Type": targetplateholder_supplytype, 
                "UIT": targetplateholder_uit, 
                "Spec": targetplateholder_spec,
            },
            {
                "Category": "Sheet Cooper",
                "Part No": targetsheetcooper_pn, 
                "Qty": targetsheetcooper_qty, 
                "Supply Type": targetsheetcooper_supplytype, 
                "UIT": targetsheetcooper_uit, 
                "Spec": targetsheetcooper_spec,
            },
            {
                "Category": "SKD Main Package",
                "Part No": targetmainpackage_pn, 
                "Qty": targetmainpackage_qty, 
                "Supply Type": targetmainpackage_supplytype, 
                "UIT": targetmainpackage_uit, 
                "Spec": targetmainpackage_spec,
            },
            {
                "Category": "PCB",
                "Part No": targetpcbmain_pn, 
                "Qty": targetpcbmain_qty, 
                "Supply Type": targetpcbmain_supplytype, 
                "UIT": targetpcbmain_uit, 
                "Spec": targetpcbmain_spec,
            },
            {
                "Category": "EBU SVC",
                "Part No": targetebusvc_pn, 
                "Qty": targetebusvc_qty, 
                "Supply Type": targetebusvc_supplytype, 
                "UIT": targetebusvc_uit, 
                "Spec": targetebusvc_spec,
            },
            {
                "Category": "EBR SVC",
                "Part No": targetebrsvc_pn, 
                "Qty": targetebrsvc_qty, 
                "Supply Type": targetebrsvc_supplytype, 
                "UIT": targetebrsvc_uit, 
                "Spec": targetebrsvc_spec,
            },
            {
                "Category": "Plate Shield SVC",
                "Part No": targetplateshieldsvc_pn, 
                "Qty": targetplateshieldsvc_qty, 
                "Supply Type": targetplateshieldsvc_supplytype, 
                "UIT": targetplateshieldsvc_uit, 
                "Spec": targetplateshieldsvc_spec,
            },
            {
                "Category": "Wifi Assy SVC",
                "Part No": targetwifiassysvc_pn, 
                "Qty": targetwifiassysvc_qty, 
                "Supply Type": targetwifiassysvc_supplytype, 
                "UIT": targetwifiassysvc_uit, 
                "Spec": targetwifiassysvc_spec,
            },
            {
                "Category": "Speaker Right",
                "Part No": targetspeakerright_pn, 
                "Qty": targetspeakerright_qty, 
                "Supply Type": targetspeakerright_supplytype, 
                "UIT": targetspeakerright_uit, 
                "Spec": targetspeakerright_spec,
            },
            {
                "Category": "Speaker Left",
                "Part No": targetspeakerleft_pn, 
                "Qty": targetspeakerleft_qty, 
                "Supply Type": targetspeakerleft_supplytype, 
                "UIT": targetspeakerleft_uit, 
                "Spec": targetspeakerleft_spec,
            },
            {
                "Category": "SPK Assy",
                "Part No": targetspeaker_pn, 
                "Qty": targetspeaker_qty, 
                "Supply Type": targetspeaker_supplytype, 
                "UIT": targetspeaker_uit, 
                "Spec": targetspeaker_spec,
            },
            {
                "Category": "Power Board",
                "Part No": targetpowerboard_pn, 
                "Qty": targetpowerboard_qty, 
                "Supply Type": targetpowerboard_supplytype, 
                "UIT": targetpowerboard_uit, 
                "Spec": targetpowerboard_spec,
            },
            {
                "Category": "EBT Power Cord",
                "Part No": targetebtpowercord_pn, 
                "Qty": targetebtpowercord_qty, 
                "Supply Type": targetebtpowercord_supplytype, 
                "UIT": targetebtpowercord_uit, 
                "Spec": targetebtpowercord_spec,
            },
            {
                "Category": "Power Cord Attach",
                "Part No": targetpowercordattach_pn, 
                "Qty": targetpowercordattach_qty, 
                "Supply Type": targetpowercordattach_supplytype, 
                "UIT": targetpowercordattach_uit, 
                "Spec": targetpowercordattach_spec,
            },
            {
                "Category": "Power Cord Detach",
                "Part No": targetpowercorddetach_pn, 
                "Qty": targetpowercorddetach_qty, 
                "Supply Type": targetpowercorddetach_supplytype, 
                "UIT": targetpowercorddetach_uit, 
                "Spec": targetpowercorddetach_spec,
            },
            {
                "Category": "Cable FFC Main 1",
                "Part No": targetffcmain1_pn, 
                "Qty": targetffcmain1_qty, 
                "Supply Type": targetffcmain1_supplytype, 
                "UIT": targetffcmain1_uit, 
                "Spec": targetffcmain1_spec,
            },
            {
                "Category": "Cable FFC Main 2",
                "Part No": targetffcmain2_pn, 
                "Qty": targetffcmain2_qty, 
                "Supply Type": targetffcmain2_supplytype, 
                "UIT": targetffcmain2_uit, 
                "Spec": targetffcmain2_spec,
            },
            {
                "Category": "Cable FFC Sub Assy",
                "Part No": targetffcassy_pn, 
                "Qty": targetffcassy_qty, 
                "Supply Type": targetffcassy_supplytype, 
                "UIT": targetffcassy_uit, 
                "Spec": targetffcassy_spec,
            },
            {
                "Category": "Harness Single",
                "Part No": targetharnesssingle_pn, 
                "Qty": targetharnesssingle_qty, 
                "Supply Type": targetharnesssingle_supplytype, 
                "UIT": targetharnesssingle_uit, 
                "Spec": targetharnesssingle_spec,
            },
            {
                "Category": "Harness Multi",
                "Part No": targetharnessmulti_pn, 
                "Qty": targetharnessmulti_qty, 
                "Supply Type": targetharnessmulti_supplytype, 
                "UIT": targetharnessmulti_uit, 
                "Spec": targetharnessmulti_spec,
            },
            {
                "Category": "IR Assy",
                "Part No": targetirassy_pn, 
                "Qty": targetirassy_qty, 
                "Supply Type": targetirassy_supplytype, 
                "UIT": targetirassy_uit, 
                "Spec": targetirassy_spec,
            },
            {
                "Category": "Wifi Assy",
                "Part No": targetwifiassy_pn, 
                "Qty": targetwifiassy_qty, 
                "Supply Type": targetwifiassy_supplytype, 
                "UIT": targetwifiassy_uit, 
                "Spec": targetwifiassy_spec,
            },
            {
                "Category": "Wifi Assy Main",
                "Part No": targetwifiassymain_pn, 
                "Qty": targetwifiassymain_qty, 
                "Supply Type": targetwifiassymain_supplytype, 
                "UIT": targetwifiassymain_uit, 
                "Spec": targetwifiassymain_spec,
            },
            {
                "Category": "MR Remote",
                "Part No": targetremote_pn, 
                "Qty": targetremote_qty, 
                "Supply Type": targetremote_supplytype, 
                "UIT": targetremote_uit, 
                "Spec": targetremote_spec,
            },
            {
                "Category": "L-Con Remote",
                "Part No": targetlconremote_pn, 
                "Qty": targetlconremote_qty, 
                "Supply Type": targetlconremote_supplytype, 
                "UIT": targetlconremote_uit, 
                "Spec": targetlconremote_spec,
            },
            {
                "Category": "MR Battery",
                "Part No": targetbattery_pn, 
                "Qty": targetbattery_qty, 
                "Supply Type": targetbattery_supplytype, 
                "UIT": targetbattery_uit, 
                "Spec": targetbattery_spec,
            },
            {
                "Category": "L-Con Battery",
                "Part No": targetlconbattery_pn, 
                "Qty": targetlconbattery_qty, 
                "Supply Type": targetlconbattery_supplytype, 
                "UIT": targetlconbattery_uit, 
                "Spec": targetlconbattery_spec,
            },
            {
                "Category": "Ferrit Core",
                "Part No": targetferritcore_pn, 
                "Qty": targetferritcore_qty, 
                "Supply Type": targetferritcore_supplytype, 
                "UIT": targetferritcore_uit, 
                "Spec": targetferritcore_spec,
            },
            {
                "Category": "Tuner Cover",
                "Part No": targettunercover_pn, 
                "Qty": targettunercover_qty, 
                "Supply Type": targettunercover_supplytype, 
                "UIT": targettunercover_uit, 
                "Spec": targettunercover_spec,
            },
            {
                "Category": "Tuner Cover SVC",
                "Part No": targettunercoversvc_pn, 
                "Qty": targettunercoversvc_qty, 
                "Supply Type": targettunercoversvc_supplytype, 
                "UIT": targettunercoversvc_uit, 
                "Spec": targettunercoversvc_spec,
            },
            {
                "Category": "Holder",
                "Part No": targetholdermain_pn, 
                "Qty": targetholdermain_qty, 
                "Supply Type": targetholdermain_supplytype, 
                "UIT": targetholdermain_uit, 
                "Spec": targetholdermain_spec,
            },
            {
                "Category": "Holder SVC",
                "Part No": targetholdersvc_pn, 
                "Qty": targetholdersvc_qty, 
                "Supply Type": targetholdersvc_supplytype, 
                "UIT": targetholdersvc_uit, 
                "Spec": targetholdersvc_spec,
            },
            {
                "Category": "Tape",
                "Part No": targettape1_pn, 
                "Qty": targettape1_qty, 
                "Supply Type": targettape1_supplytype, 
                "UIT": targettape1_uit, 
                "Spec": targettape1_spec,
            },
            {
                "Category": "Tape",
                "Part No": targettape2_pn, 
                "Qty": targettape2_qty, 
                "Supply Type": targettape2_supplytype, 
                "UIT": targettape2_uit, 
                "Spec": targettape2_spec,
            },
            {
                "Category": "Tape",
                "Part No": targettape3_pn, 
                "Qty": targettape3_qty, 
                "Supply Type": targettape3_supplytype, 
                "UIT": targettape3_uit, 
                "Spec": targettape3_spec,
            },
            {
                "Category": "Tape",
                "Part No": targettape4_pn, 
                "Qty": targettape4_qty, 
                "Supply Type": targettape4_supplytype, 
                "UIT": targettape4_uit, 
                "Spec": targettape4_spec,
            },
            {
                "Category": "Tape",
                "Part No": targettape5_pn, 
                "Qty": targettape5_qty, 
                "Supply Type": targettape5_supplytype, 
                "UIT": targettape5_uit, 
                "Spec": targettape5_spec,
            },
            {
                "Category": "Gasket",
                "Part No": targetgasket1_pn, 
                "Qty": targetgasket1_qty, 
                "Supply Type": targetgasket1_supplytype, 
                "UIT": targetgasket1_uit, 
                "Spec": targetgasket1_spec,
            },
            {
                "Category": "Gasket",
                "Part No": targetgasket2_pn, 
                "Qty": targetgasket2_qty, 
                "Supply Type": targetgasket2_supplytype, 
                "UIT": targetgasket2_uit, 
                "Spec": targetgasket2_spec,
            },
            {
                "Category": "Gasket",
                "Part No": targetgasket3_pn, 
                "Qty": targetgasket3_qty, 
                "Supply Type": targetgasket3_supplytype, 
                "UIT": targetgasket3_uit, 
                "Spec": targetgasket3_spec,
            },
            {
                "Category": "Gasket",
                "Part No": targetgasket4_pn, 
                "Qty": targetgasket4_qty, 
                "Supply Type": targetgasket4_supplytype, 
                "UIT": targetgasket4_uit, 
                "Spec": targetgasket4_spec,
            },
            {
                "Category": "Gasket",
                "Part No": targetgasket5_pn, 
                "Qty": targetgasket5_qty, 
                "Supply Type": targetgasket5_supplytype, 
                "UIT": targetgasket5_uit, 
                "Spec": targetgasket5_spec,
            },
            {
                "Category": "Damper",
                "Part No": targetdamper1_pn, 
                "Qty": targetdamper1_qty, 
                "Supply Type": targetdamper1_supplytype, 
                "UIT": targetdamper1_uit, 
                "Spec": targetdamper1_spec,
            },
            {
                "Category": "Damper",
                "Part No": targetdamper2_pn, 
                "Qty": targetdamper2_qty, 
                "Supply Type": targetdamper2_supplytype, 
                "UIT": targetdamper2_uit, 
                "Spec": targetdamper2_spec,
            },
            {
                "Category": "Damper",
                "Part No": targetdamper3_pn, 
                "Qty": targetdamper3_qty, 
                "Supply Type": targetdamper3_supplytype, 
                "UIT": targetdamper3_uit, 
                "Spec": targetdamper3_spec,
            },
            {
                "Category": "Damper",
                "Part No": targetdamper4_pn, 
                "Qty": targetdamper4_qty, 
                "Supply Type": targetdamper4_supplytype, 
                "UIT": targetdamper4_uit, 
                "Spec": targetdamper4_spec,
            },
            {
                "Category": "Damper",
                "Part No": targetdamper5_pn, 
                "Qty": targetdamper5_qty, 
                "Supply Type": targetdamper5_supplytype, 
                "UIT": targetdamper5_uit, 
                "Spec": targetdamper5_spec,
            },
        ]
        with open(JSON_DIR / "2_development_part.json", "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )
        
        part_status = [
            {
                "Category": "EBT Main",
                "Part No": targetebtmain_pn,
                "Qty": targetebtmain_qty,
                "Status": targetebtmain_state,
            },
            {
                "Category": "EBT Sub",
                "Part No": targetebtassy_pn,
                "Qty": targetebtassy_qty,
                "Status": targetebtassy_state,
            },
            {
                "Category": "EBU Main",
                "Part No": targetebumain_pn,
                "Qty": targetebumain_qty,
                "Status": targetebumain_state,
            },
            {
                "Category": "EBR Main",
                "Part No": targetebrmain_pn,
                "Qty": targetebrmain_qty,
                "Status": targetebrmain_state,
            },
            {
                "Category": "SW Assy",
                "Part No": targetswassy_pn,
                "Qty": targetswassy_qty,
                "Status": targetswassy_state,
            },
            {
                "Category": "EDID",
                "Part No": targetedid_pn,
                "Qty": targetedid_qty,
                "Status": targetedid_state,
            },
            {
                "Category": "Plateshield Assy",
                "Part No": targetplateshield_pn,
                "Qty": targetplateshield_qty,
                "Status": targetplateshield_state,
            },
            {
                "Category": "Shield Plate Assy",
                "Part No": targetplatesink_pn,
                "Qty": targetplatesink_qty,
                "Status": targetplatesink_state,
            },
            {
                "Category": "Plate Holder",
                "Part No": targetplateholder_pn,
                "Qty": targetplateholder_qty,
                "Status": targetplateholder_state,
            },
            {
                "Category": "Sheet Cooper",
                "Part No": targetsheetcooper_pn,
                "Qty": targetsheetcooper_qty,
                "Status": targetsheetcooper_state,
            },
            {
                "Category": "SKD Main Package",
                "Part No": targetmainpackage_pn,
                "Qty": targetmainpackage_qty,
                "Status": targetmainpackage_state,
            },
            {
                "Category": "PCB Main",
                "Part No": targetpcbmain_pn,
                "Qty": targetpcbmain_qty,
                "Status": targetpcbmain_state,
            },
            {
                "Category": "EBU SVC",
                "Part No": targetebusvc_pn,
                "Qty": targetebusvc_qty,
                "Status": targetebusvc_state,
            },
            {
                "Category": "EBR SVC",
                "Part No": targetebrsvc_pn,
                "Qty": targetebrsvc_qty,
                "Status": targetebrsvc_state,
            },
            {
                "Category": "Plateshield SVC",
                "Part No": targetplateshieldsvc_pn,
                "Qty": targetplateshieldsvc_qty,
                "Status": targetplateshieldsvc_state,
            },
            {
                "Category": "Wifi Assy SVC",
                "Part No": targetwifiassysvc_pn,
                "Qty": targetwifiassysvc_qty,
                "Status": targetwifiassysvc_state,
            },
            {
                "Category": "Speaker Right",
                "Part No": targetspeakerright_pn,
                "Qty": targetspeakerright_qty,
                "Status": targetspeakerright_state,
            },
            {
                "Category": "Speaker Left",
                "Part No": targetspeakerleft_pn,
                "Qty": targetspeakerleft_qty,
                "Status": targetspeakerleft_state,
            },
            {
                "Category": "Speaker Assy",
                "Part No": targetspeaker_pn,
                "Qty": targetspeaker_qty,
                "Status": targetspeaker_state,
            },
            {
                "Category": "Power Board",
                "Part No": targetpowerboard_pn,
                "Qty": targetpowerboard_qty,
                "Status": targetpowerboard_state,
            },
            {
                "Category": "EBT Power Cord",
                "Part No": targetebtpowercord_pn,
                "Qty": targetebtpowercord_qty,
                "Status": targetebtpowercord_state,
            },
            {
                "Category": "Power Cord Attach",
                "Part No": targetpowercordattach_pn,
                "Qty": targetpowercordattach_qty,
                "Status": targetpowercordattach_state,
            },
            {
                "Category": "Power Cord Detach",
                "Part No": targetpowercorddetach_pn,
                "Qty": targetpowercorddetach_qty,
                "Status": targetpowercorddetach_state,
            },
            {
                "Category": "Cable FFC Main 1",
                "Part No": targetffcmain1_pn,
                "Qty": targetffcmain1_qty,
                "Status": targetffcmain1_state,
            },
            {
                "Category": "Cable FFC Main 2",
                "Part No": targetffcmain2_pn,
                "Qty": targetffcmain2_qty,
                "Status": targetffcmain2_state,
            },
            {
                "Category": "Cable FFC Sub Assy",
                "Part No": targetffcassy_pn,
                "Qty": targetffcassy_qty,
                "Status": targetffcassy_state,
            },
            {
                "Category": "Harness Single",
                "Part No": targetharnesssingle_pn,
                "Qty": targetharnesssingle_qty,
                "Status": targetharnesssingle_state,
            },
            {
                "Category": "Harness Multi",
                "Part No": targetharnessmulti_pn,
                "Qty": targetharnessmulti_qty,
                "Status": targetharnessmulti_state,
            },
            {
                "Category": "IR Assy",
                "Part No": targetirassy_pn,
                "Qty": targetirassy_qty,
                "Status": targetirassy_state,
            },
            {
                "Category": "Wifi Assy",
                "Part No": targetwifiassy_pn,
                "Qty": targetwifiassy_qty,
                "Status": targetwifiassy_state,
            },
            {
                "Category": "Wifi Assy Main",
                "Part No": targetwifiassymain_pn,
                "Qty": targetwifiassymain_qty,
                "Status": targetwifiassymain_state,
            },
            {
                "Category": "MR Remote",
                "Part No": targetremote_pn,
                "Qty": targetremote_qty,
                "Status": targetremote_state,
            },
            {
                "Category": "LCON Remote",
                "Part No": targetlconremote_pn,
                "Qty": targetlconremote_qty,
                "Status": targetlconremote_state,
            },
            {
                "Category": "MR Battery",
                "Part No": targetbattery_pn,
                "Qty": targetbattery_qty,
                "Status": targetbattery_state,
            },
            {
                "Category": "LCON Battery",
                "Part No": targetlconbattery_pn,
                "Qty": targetlconbattery_qty,
                "Status": targetlconbattery_state,
            },
            {
                "Category": "Ferrit Core",
                "Part No": targetferritcore_pn,
                "Qty": targetferritcore_qty,
                "Status": targetferritcore_state,
            },
            {
                "Category": "Tuner Case Cover",
                "Part No": targettunercover_pn,
                "Qty": targettunercover_qty,
                "Status": targettunercover_state,
            },
            {
                "Category": "Tuner Case Cover SVC",
                "Part No": targettunercoversvc_pn,
                "Qty": targettunercoversvc_qty,
                "Status": targettunercoversvc_state,
            },
            {
                "Category": "Holder",
                "Part No": targetholdermain_pn,
                "Qty": targetholdermain_qty,
                "Status": targetholdermain_state,
            },
            {
                "Category": "Holder SVC",
                "Part No": targetholdersvc_pn,
                "Qty": targetholdersvc_qty,
                "Status": targetholdersvc_state,
            },
            {
                "Category": "Tape 1",
                "Part No": targettape1_pn,
                "Qty": targettape1_qty,
                "Status": targettape1_state,
            },
            {
                "Category": "Tape 2",
                "Part No": targettape2_pn,
                "Qty": targettape2_qty,
                "Status": targettape2_state,
            },
            {
                "Category": "Tape 3",
                "Part No": targettape3_pn,
                "Qty": targettape3_qty,
                "Status": targettape3_state,
            },
            {
                "Category": "Tape 4",
                "Part No": targettape4_pn,
                "Qty": targettape4_qty,
                "Status": targettape4_state,
            },
            {
                "Category": "Tape 5",
                "Part No": targettape5_pn,
                "Qty": targettape5_qty,
                "Status": targettape5_state,
            },
            {
                "Category": "Gasket 1",
                "Part No": targetgasket1_pn,
                "Qty": targetgasket1_qty,
                "Status": targetgasket1_state,
            },
            {
                "Category": "Gasket 2",
                "Part No": targetgasket2_pn,
                "Qty": targetgasket2_qty,
                "Status": targetgasket2_state,
            },
            {
                "Category": "Gasket 3",
                "Part No": targetgasket3_pn,
                "Qty": targetgasket3_qty,
                "Status": targetgasket3_state,
            },
            {
                "Category": "Gasket 4",
                "Part No": targetgasket4_pn,
                "Qty": targetgasket4_qty,
                "Status": targetgasket4_state,
            },
            {
                "Category": "Gasket 5",
                "Part No": targetgasket5_pn,
                "Qty": targetgasket5_qty,
                "Status": targetgasket5_state,
            },
            {
                "Category": "Damper 1",
                "Part No": targetdamper1_pn,
                "Qty": targetdamper1_qty,
                "Status": targetdamper1_state,
            },
            {
                "Category": "Damper 2",
                "Part No": targetdamper2_pn,
                "Qty": targetdamper2_qty,
                "Status": targetdamper2_state,
            },
            {
                "Category": "Damper 3",
                "Part No": targetdamper3_pn,
                "Qty": targetdamper3_qty,
                "Status": targetdamper3_state,
            },
            {
                "Category": "Damper 4",
                "Part No": targetdamper4_pn,
                "Qty": targetdamper4_qty,
                "Status": targetdamper4_state,
            },
            {
                "Category": "Damper 5",
                "Part No": targetdamper5_pn,
                "Qty": targetdamper5_qty,
                "Status": targetdamper5_state,
            }
        ]
        with open(JSON_DIR / "4_development_statuspart.json", "w", encoding="utf-8") as f:
            json.dump(
                part_status,
                f,
                indent=4,
                ensure_ascii=False
            )
        
        return [
            targetebtmain_pn, targetebtmain_qty, targetebtmain_supplytype, targetebtmain_uit, targetebtmain_spec,
            targetebtassy_pn, targetebtassy_qty, targetebtassy_supplytype, targetebtassy_uit, targetebtassy_spec,
            targetebumain_pn, targetebumain_qty, targetebumain_supplytype, targetebumain_uit, targetebumain_spec,
            targetebrmain_pn, targetebrmain_qty, targetebrmain_supplytype, targetebrmain_uit, targetebrmain_spec,
            targetswassy_pn, targetswassy_qty, targetswassy_supplytype, targetswassy_uit, targetswassy_spec,
            targetedid_pn, targetedid_qty, targetedid_supplytype, targetedid_uit, targetedid_spec,
            targetplateshield_pn, targetplateshield_qty, targetplateshield_supplytype, targetplateshield_uit, targetplateshield_spec,
            targetplatesink_pn, targetplatesink_qty, targetplatesink_supplytype, targetplatesink_uit, targetplatesink_spec,
            targetplateholder_pn, targetplateholder_qty, targetplateholder_supplytype, targetplateholder_uit, targetplateholder_spec,
            targetsheetcooper_pn, targetsheetcooper_qty, targetsheetcooper_supplytype, targetsheetcooper_uit, targetsheetcooper_spec,
            targetmainpackage_pn, targetmainpackage_qty, targetmainpackage_supplytype, targetmainpackage_uit, targetmainpackage_spec,
            targetpcbmain_pn, targetpcbmain_qty, targetpcbmain_supplytype, targetpcbmain_uit, targetpcbmain_spec,
            targetebusvc_pn, targetebusvc_qty, targetebusvc_supplytype, targetebusvc_uit, targetebusvc_spec,
            targetebrsvc_pn, targetebrsvc_qty, targetebrsvc_supplytype, targetebrsvc_uit, targetebrsvc_spec,
            targetplateshieldsvc_pn, targetplateshieldsvc_qty, targetplateshieldsvc_supplytype, targetplateshieldsvc_uit, targetplateshieldsvc_spec,
            targetwifiassysvc_pn, targetwifiassysvc_qty, targetwifiassysvc_supplytype, targetwifiassysvc_uit, targetwifiassysvc_spec,
            targetspeakerright_pn, targetspeakerright_qty, targetspeakerright_supplytype, targetspeakerright_uit, targetspeakerright_spec,
            targetspeakerleft_pn, targetspeakerleft_qty, targetspeakerleft_supplytype, targetspeakerleft_uit, targetspeakerleft_spec,
            targetspeaker_pn, targetspeaker_qty, targetspeaker_supplytype, targetspeaker_uit, targetspeaker_spec,
            targetpowerboard_pn, targetpowerboard_qty, targetpowerboard_supplytype, targetpowerboard_uit, targetpowerboard_spec,
            targetebtpowercord_pn, targetebtpowercord_qty, targetebtpowercord_supplytype, targetebtpowercord_uit, targetebtpowercord_spec,
            targetpowercordattach_pn, targetpowercordattach_qty, targetpowercordattach_supplytype, targetpowercordattach_uit, targetpowercordattach_spec,
            targetpowercorddetach_pn, targetpowercorddetach_qty, targetpowercorddetach_supplytype, targetpowercorddetach_uit, targetpowercorddetach_spec,
            targetffcmain1_pn, targetffcmain1_qty, targetffcmain1_supplytype, targetffcmain1_uit, targetffcmain1_spec,
            targetffcmain2_pn, targetffcmain2_qty, targetffcmain2_supplytype, targetffcmain2_uit, targetffcmain2_spec,
            targetffcassy_pn, targetffcassy_qty, targetffcassy_supplytype, targetffcassy_uit, targetffcassy_spec,
            targetharnesssingle_pn, targetharnesssingle_qty, targetharnesssingle_supplytype, targetharnesssingle_uit, targetharnesssingle_spec,
            targetharnessmulti_pn, targetharnessmulti_qty, targetharnessmulti_supplytype, targetharnessmulti_uit, targetharnessmulti_spec,
            targetirassy_pn, targetirassy_qty, targetirassy_supplytype, targetirassy_uit, targetirassy_spec,
            targetwifiassy_pn, targetwifiassy_qty, targetwifiassy_supplytype, targetwifiassy_uit, targetwifiassy_spec,
            targetwifiassymain_pn, targetwifiassymain_qty, targetwifiassymain_supplytype, targetwifiassymain_uit, targetwifiassymain_spec,
            targetremote_pn, targetremote_qty, targetremote_supplytype, targetremote_uit, targetremote_spec,
            targetlconremote_pn, targetlconremote_qty, targetlconremote_supplytype, targetlconremote_uit, targetlconremote_spec,
            targetbattery_pn, targetbattery_qty, targetbattery_supplytype, targetbattery_uit, targetbattery_spec,
            targetlconbattery_pn, targetlconbattery_qty, targetlconbattery_supplytype, targetlconbattery_uit, targetlconbattery_spec,
            targetferritcore_pn, targetferritcore_qty, targetferritcore_supplytype, targetferritcore_uit, targetferritcore_spec,
            targettunercover_pn, targettunercover_qty, targettunercover_supplytype, targettunercover_uit, targettunercover_spec,
            targettunercoversvc_pn, targettunercoversvc_qty, targettunercoversvc_supplytype, targettunercoversvc_uit, targettunercoversvc_spec,
            targetholdermain_pn, targetholdermain_qty, targetholdermain_supplytype, targetholdermain_uit, targetholdermain_spec,
            targetholdersvc_pn, targetholdersvc_qty, targetholdersvc_supplytype, targetholdersvc_uit, targetholdersvc_spec,
            targettape1_pn, targettape1_qty, targettape1_supplytype, targettape1_uit, targettape1_spec,
            targettape2_pn, targettape2_qty, targettape2_supplytype, targettape2_uit, targettape2_spec,
            targettape3_pn, targettape3_qty, targettape3_supplytype, targettape3_uit, targettape3_spec,
            targettape4_pn, targettape4_qty, targettape4_supplytype, targettape4_uit, targettape4_spec,
            targettape5_pn, targettape5_qty, targettape5_supplytype, targettape5_uit, targettape5_spec,
            targetgasket1_pn, targetgasket1_qty, targetgasket1_supplytype, targetgasket1_uit, targetgasket1_spec,
            targetgasket2_pn, targetgasket2_qty, targetgasket2_supplytype, targetgasket2_uit, targetgasket2_spec,
            targetgasket3_pn, targetgasket3_qty, targetgasket3_supplytype, targetgasket3_uit, targetgasket3_spec,
            targetgasket4_pn, targetgasket4_qty, targetgasket4_supplytype, targetgasket4_uit, targetgasket4_spec,
            targetgasket5_pn, targetgasket5_qty, targetgasket5_supplytype, targetgasket5_uit, targetgasket5_spec,
            targetdamper1_pn, targetdamper1_qty, targetdamper1_supplytype, targetdamper1_uit, targetdamper1_spec,
            targetdamper2_pn, targetdamper2_qty, targetdamper2_supplytype, targetdamper2_uit, targetdamper2_spec,
            targetdamper3_pn, targetdamper3_qty, targetdamper3_supplytype, targetdamper3_uit, targetdamper3_spec,
            targetdamper4_pn, targetdamper4_qty, targetdamper4_supplytype, targetdamper4_uit, targetdamper4_spec,
            targetdamper5_pn, targetdamper5_qty, targetdamper5_supplytype, targetdamper5_uit, targetdamper5_spec
        ]
        # Save the extracted data to a JSON file
    def targetpart_compare(self):
        with open(JSON_DIR / "0_development_ebom.json", "r", encoding="utf-8") as f:
            response_data = json.load(f)
        target_model = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStr") == "00001" 
            ))
            ])
        if not target_model.empty:
                for idx, row in target_model.iterrows():
                    target_model = row['childNameDisplay']
        wb = load_workbook("excel/template_part.xlsx")
        ws = wb["BEN Compare"]

        data = self.targetpartscrapper()
        ebtmain_pn, ebtmain_qty, ebtmain_supplytype, ebtmain_uit, ebtmain_spec = data[0:5]
        ebtassy_pn, ebtassy_qty, ebtassy_supplytype, ebtassy_uit, ebtassy_spec = data[5:10]
        ebumain_pn, ebumain_qty, ebumain_supplytype, ebumain_uit, ebumain_spec = data[10:15]
        ebrmain_pn, ebrmain_qty, ebrmain_supplytype, ebrmain_uit, ebrmain_spec = data[15:20]
        swassy_pn, swassy_qty, swassy_supplytype, swassy_uit, swassy_spec = data[20:25]
        edid_pn, edid_qty, edid_supplytype, edid_uit, edid_spec = data[25:30]
        plateshield_pn, plateshield_qty, plateshield_supplytype, plateshield_uit, plateshield_spec = data[30:35]
        platesink_pn, platesink_qty, platesink_supplytype, platesink_uit, platesink_spec = data[35:40]
        plateholder_pn, plateholder_qty, plateholder_supplytype, plateholder_uit, plateholder_spec = data[40:45]
        sheetcooper_pn, sheetcooper_qty, sheetcooper_supplytype, sheetcooper_uit, sheetcooper_spec = data[45:50]
        ebrpackage_pn, ebrpackage_qty, ebrpackage_supplytype, ebrpackage_uit, ebrpackage_spec = data[50:55]
        pcbmain_pn, pcbmain_qty, pcbmain_supplytype, pcbmain_uit, pcbmain_spec = data[55:60]
        ebusvc_pn, ebusvc_qty, ebusvc_supplytype, ebusvc_uit, ebusvc_spec = data[60:65]
        ebrsvc_pn, ebrsvc_qty, ebrsvc_supplytype, ebrsvc_uit, ebrsvc_spec = data[65:70]
        plateshieldsvc_pn, plateshieldsvc_qty, plateshieldsvc_supplytype, plateshieldsvc_uit, plateshieldsvc_spec = data[70:75]
        wifiassysvc_pn, wifiassysvc_qty, wifiassysvc_supplytype, wifiassysvc_uit, wifiassysvc_spec = data[75:80]
        speakerright_pn, speakerright_qty, speakerright_supplytype, speakerright_uit, speakerright_spec = data[80:85]
        speakerleft_pn, speakerleft_qty, speakerleft_supplytype, speakerleft_uit, speakerleft_spec = data[85:90]
        speaker_pn, speaker_qty, speaker_supplytype, speaker_uit, speaker_spec = data[90:95]
        powerboard_pn, powerboard_qty, powerboard_supplytype, powerboard_uit, powerboard_spec = data[95:100]
        ebtpowercord_pn, ebtpowercord_qty, ebtpowercord_supplytype, ebtpowercord_uit, ebtpowercord_spec = data[100:105]
        powercordattach_pn, powercordattach_qty, powercordattach_supplytype, powercordattach_uit, powercordattach_spec = data[105:110]
        powercorddetach_pn, powercorddetach_qty, powercorddetach_supplytype, powercorddetach_uit, powercorddetach_spec = data[110:115]
        ffcmain1_pn, ffcmain1_qty, ffcmain1_supplytype, ffcmain1_uit, ffcmain1_spec = data[115:120]
        ffcmain2_pn, ffcmain2_qty, ffcmain2_supplytype, ffcmain2_uit, ffcmain2_spec = data[120:125]
        ffcassy_pn, ffcassy_qty, ffcassy_supplytype, ffcassy_uit, ffcassy_spec = data[125:130]
        harnesssingle_pn, harnesssingle_qty, harnesssingle_supplytype, harnesssingle_uit, harnesssingle_spec = data[130:135]
        harnessmulti_pn, harnessmulti_qty, harnessmulti_supplytype, harnessmulti_uit, harnessmulti_spec = data[135:140]
        irassy_pn, irassy_qty, irassy_supplytype, irassy_uit, irassy_spec = data[140:145]
        wifiassy_pn, wifiassy_qty, wifiassy_supplytype, wifiassy_uit, wifiassy_spec = data[145:150]
        wifimain_pn, wifimain_qty, wifimain_supplytype, wifimain_uit, wifimain_spec = data[150:155]
        remote_pn, remote_qty, remote_supplytype, remote_uit, remote_spec = data[155:160]
        lcon_pn, lcon_qty, lcon_supplytype, lcon_uit, lcon_spec = data[160:165]
        battery_pn, battery_qty, battery_supplytype, battery_uit, battery_spec = data[165:170]
        lconbattery_pn, lconbattery_qty, lconbattery_supplytype, lconbattery_uit, lconbattery_spec = data[170:175]
        ferritcore_pn, ferritcore_qty, ferritcore_supplytype, ferritcore_uit, ferritcore_spec = data[175:180]
        tunercover_pn, tunercover_qty, tunercover_supplytype, tunercover_uit, tunercover_spec = data[180:185]
        tunercoversvc_pn, tunercoversvc_qty, tunercoversvc_supplytype, tunercoversvc_uit, tunercoversvc_spec = data[185:190]
        holdermain_pn, holdermain_qty, holdermain_supplytype, holdermain_uit, holdermain_spec = data[190:195]
        holdersvc_pn, holdersvc_qty, holdersvc_supplytype, holdersvc_uit, holdersvc_spec = data[195:200]
        tape1_pn, tape1_qty, tape1_supplytype, tape1_uit, tape1_spec = data[200:205]
        tape2_pn, tape2_qty, tape2_supplytype, tape2_uit, tape2_spec = data[205:210]
        tape3_pn, tape3_qty, tape3_supplytype, tape3_uit, tape3_spec = data[210:215]
        tape4_pn, tape4_qty, tape4_supplytype, tape4_uit, tape4_spec = data[215:220]
        tape5_pn, tape5_qty, tape5_supplytype, tape5_uit, tape5_spec = data[220:225]
        gasket1_pn, gasket1_qty, gasket1_supplytype, gasket1_uit, gasket1_spec = data[225:230]
        gasket2_pn, gasket2_qty, gasket2_supplytype, gasket2_uit, gasket2_spec = data[230:235]
        gasket3_pn, gasket3_qty, gasket3_supplytype, gasket3_uit, gasket3_spec = data[235:240]
        gasket4_pn, gasket4_qty, gasket4_supplytype, gasket4_uit, gasket4_spec = data[240:245]
        gasket5_pn, gasket5_qty, gasket5_supplytype, gasket5_uit, gasket5_spec = data[245:250]
        damper1_pn, damper1_qty, damper1_supplytype, damper1_uit, damper1_spec = data[250:255]
        damper2_pn, damper2_qty, damper2_supplytype, damper2_uit, damper2_spec = data[255:260]
        damper3_pn, damper3_qty, damper3_supplytype, damper3_uit, damper3_spec = data[260:265]
        damper4_pn, damper4_qty, damper4_supplytype, damper4_uit, damper4_spec = data[265:270]
        damper5_pn, damper5_qty, damper5_supplytype, damper5_uit, damper5_spec = data[270:275]

        rows = list(range(6, 61))
        columns = list(range(9, 14))
        data_list = [
            ebtmain_pn, ebtmain_qty, ebtmain_supplytype, ebtmain_uit, ebtmain_spec,
            ebtassy_pn, ebtassy_qty, ebtassy_supplytype, ebtassy_uit, ebtassy_spec,
            ebumain_pn, ebumain_qty, ebumain_supplytype, ebumain_uit, ebumain_spec,
            ebrmain_pn, ebrmain_qty, ebrmain_supplytype, ebrmain_uit, ebrmain_spec,
            swassy_pn, swassy_qty, swassy_supplytype, swassy_uit, swassy_spec,
            edid_pn, edid_qty, edid_supplytype, edid_uit, edid_spec,
            plateshield_pn, plateshield_qty, plateshield_supplytype, plateshield_uit, plateshield_spec,
            platesink_pn, platesink_qty, platesink_supplytype, platesink_uit, platesink_spec,
            plateholder_pn, plateholder_qty, plateholder_supplytype, plateholder_uit, plateholder_spec,
            sheetcooper_pn, sheetcooper_qty, sheetcooper_supplytype, sheetcooper_uit, sheetcooper_spec,
            ebrpackage_pn, ebrpackage_qty, ebrpackage_supplytype, ebrpackage_uit, ebrpackage_spec,
            pcbmain_pn, pcbmain_qty, pcbmain_supplytype, pcbmain_uit, pcbmain_spec,
            ebusvc_pn, ebusvc_qty, ebusvc_supplytype, ebusvc_uit, ebusvc_spec,
            ebrsvc_pn, ebrsvc_qty, ebrsvc_supplytype, ebrsvc_uit, ebrsvc_spec,
            plateshieldsvc_pn, plateshieldsvc_qty, plateshieldsvc_supplytype, plateshieldsvc_uit, plateshieldsvc_spec,
            wifiassysvc_pn, wifiassysvc_qty, wifiassysvc_supplytype, wifiassysvc_uit, wifiassysvc_spec,
            speakerright_pn, speakerright_qty, speakerright_supplytype, speakerright_uit, speakerright_spec,
            speakerleft_pn, speakerleft_qty, speakerleft_supplytype, speakerleft_uit, speakerleft_spec,
            speaker_pn, speaker_qty, speaker_supplytype, speaker_uit, speaker_spec,
            powerboard_pn, powerboard_qty, powerboard_supplytype, powerboard_uit, powerboard_spec,
            ebtpowercord_pn, ebtpowercord_qty, ebtpowercord_supplytype, ebtpowercord_uit, ebtpowercord_spec,
            powercordattach_pn, powercordattach_qty, powercordattach_supplytype, powercordattach_uit, powercordattach_spec,
            powercorddetach_pn, powercorddetach_qty, powercorddetach_supplytype, powercorddetach_uit, powercorddetach_spec,
            ffcmain1_pn, ffcmain1_qty, ffcmain1_supplytype, ffcmain1_uit, ffcmain1_spec,
            ffcmain2_pn, ffcmain2_qty, ffcmain2_supplytype, ffcmain2_uit, ffcmain2_spec,
            ffcassy_pn, ffcassy_qty, ffcassy_supplytype, ffcassy_uit, ffcassy_spec,
            harnesssingle_pn, harnesssingle_qty, harnesssingle_supplytype, harnesssingle_uit, harnesssingle_spec,
            harnessmulti_pn, harnessmulti_qty, harnessmulti_supplytype, harnessmulti_uit, harnessmulti_spec,
            irassy_pn, irassy_qty, irassy_supplytype, irassy_uit, irassy_spec,
            wifiassy_pn, wifiassy_qty, wifiassy_supplytype, wifiassy_uit, wifiassy_spec,
            wifimain_pn, wifimain_qty, wifimain_supplytype, wifimain_uit, wifimain_spec,
            remote_pn, remote_qty, remote_supplytype, remote_uit, remote_spec,
            lcon_pn, lcon_qty, lcon_supplytype, lcon_uit, lcon_spec,
            battery_pn, battery_qty, battery_supplytype, battery_uit, battery_spec,
            lconbattery_pn, lconbattery_qty, lconbattery_supplytype, lconbattery_uit, lconbattery_spec,
            ferritcore_pn, ferritcore_qty, ferritcore_supplytype, ferritcore_uit, ferritcore_spec,
            tunercover_pn, tunercover_qty, tunercover_supplytype, tunercover_uit, tunercover_spec,
            tunercoversvc_pn, tunercoversvc_qty, tunercoversvc_supplytype, tunercoversvc_uit, tunercoversvc_spec,
            holdermain_pn, holdermain_qty, holdermain_supplytype, holdermain_uit, holdermain_spec,
            holdersvc_pn, holdersvc_qty, holdersvc_supplytype, holdersvc_uit, holdersvc_spec,
            tape1_pn, tape1_qty, tape1_supplytype, tape1_uit, tape1_spec,
            tape2_pn, tape2_qty, tape2_supplytype, tape2_uit, tape2_spec,
            tape3_pn, tape3_qty, tape3_supplytype, tape3_uit, tape3_spec,
            tape4_pn, tape4_qty, tape4_supplytype, tape4_uit, tape4_spec,
            tape5_pn, tape5_qty, tape5_supplytype, tape5_uit, tape5_spec,
            gasket1_pn, gasket1_qty, gasket1_supplytype, gasket1_uit, gasket1_spec,
            gasket2_pn, gasket2_qty, gasket2_supplytype, gasket2_uit, gasket2_spec,
            gasket3_pn, gasket3_qty, gasket3_supplytype, gasket3_uit, gasket3_spec,
            gasket4_pn, gasket4_qty, gasket4_supplytype, gasket4_uit, gasket4_spec,
            gasket5_pn, gasket5_qty, gasket5_supplytype, gasket5_uit, gasket5_spec,
            damper1_pn, damper1_qty, damper1_supplytype, damper1_uit, damper1_spec,
            damper2_pn, damper2_qty, damper2_supplytype, damper2_uit, damper2_spec,
            damper3_pn, damper3_qty, damper3_supplytype, damper3_uit, damper3_spec,
            damper4_pn, damper4_qty, damper4_supplytype, damper4_uit, damper4_spec,
            damper5_pn, damper5_qty, damper5_supplytype, damper5_uit, damper5_spec
        ]
        
        
        for row in ws.iter_rows(min_row=6, max_row=61, min_col=9, max_col=13):
            for cell in row:
                cell.value = None

        ws["I4"] = str(target_model.split('@')[0])

        for i, row in enumerate(rows):
            for j, column in enumerate(columns):
                ws.cell(row=row, column=column).value = data_list[i * len(columns) + j]

        wb.save("excel/template_part.xlsx")
        print("Development part compare completed")

class initialpart_compare():
    def __init__(self):
        pass
    def target_run(self):
        self.targetpartscrapper()
        # self.targetpart_compare()
        # developmentpartscrapper()
        # initialpartscrapper()
    def targetpartscrapper(self):
        with open(JSON_DIR / "0_initial_ebom.json", "r", encoding="utf-8") as f:
            response_data = json.load(f)
        
        #<Search for specific components in EBOM data (Accessory Assembly)>
        Accesory = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == "00001" and
                "AAA" in "{}".format(item.get("childNameDisplay", "")) and 
                "Accessory Assembly" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))
            ))
            ])
        if not Accesory.empty:
            for idx, row in Accesory.iterrows():
                targetaccessory_pn = row['childNameDisplay']
                targetaccessory_qty = row['bomQuantity']
                targetaccessory_level = row['bomLevel']
                targetaccessory_uit = row['outData.mr_userItemType']
                targetaccessory_supplytype = row['supplyType']
                targetaccessory_state = row['outData.pp_states']
                targetaccessory_parttype = row['dataType']
                targetaccessory_spec = row['outData.mr_siteTechnicalSpec']
                targetaccessory_uniquieid = row['uniqueStr']
        else:
            targetaccessory_pn = ""
            targetaccessory_qty = ""
            targetaccessory_level = ""
            targetaccessory_uit = ""
            targetaccessory_supplytype = ""
            targetaccessory_state = ""
            targetaccessory_parttype = ""
            targetaccessory_spec = ""
            targetaccessory_uniquieid = ""
        #<Search for specific components in EBOM data (Ferrite Core)>
        Ferrit_core = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetaccessory_uniquieid and
                "621" in "{}".format(item.get("childNameDisplay", "")) and
                "Ferrite" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))
                ))
            ])
        if not Ferrit_core.empty:
            for idx, row in Ferrit_core.iterrows():
                targetferritcore_pn = row['childNameDisplay']
                targetferritcore_qty = row['bomQuantity']
                targetferritcore_level = row['bomLevel']
                targetferritcore_uit = row['outData.mr_userItemType']
                targetferritcore_supplytype = row['supplyType']
                targetferritcore_state = row['outData.pp_states']
                targetferritcore_parttype = row['dataType']
                targetferritcore_spec = row['outData.mr_siteTechnicalSpec']
                targetferritcore_uniquieid = row['uniqueStr']
        else:
            targetferritcore_pn = ""
            targetferritcore_qty = ""
            targetferritcore_level = ""
            targetferritcore_uit = ""
            targetferritcore_supplytype = ""
            targetferritcore_state = ""
            targetferritcore_parttype = ""
            targetferritcore_spec = ""
            targetferritcore_uniquieid = ""
        #<Search for specific components in EBOM data (MR battery)
        MR_battery = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetaccessory_uniquieid and
                "EAC" in "{}".format(item.get("childNameDisplay", "")) and
                "Battery" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "LR06" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", ""))) or 
                (item.get("uniqueStrParent") == targetaccessory_uniquieid and
                "691" in "{}".format(item.get("childNameDisplay", "")) and
                "Battery" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "LR06" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", ""))) or
                (item.get("uniqueStrParent") == targetaccessory_uniquieid and
                "EAC" in "{}".format(item.get("childNameDisplay", "")) and
                "Battery" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "LR03" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", ""))) or 
                (item.get("uniqueStrParent") == targetaccessory_uniquieid and 
                "691" in "{}".format(item.get("childNameDisplay", "")) and 
                "Battery" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "LR03" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", ""))
                ))
            ])
        if not MR_battery.empty:
            for idx, row in MR_battery.iterrows():
                targetbattery_pn = row['childNameDisplay']
                targetbattery_qty = row['bomQuantity']
                targetbattery_level = row['bomLevel']
                targetbattery_uit = row['outData.mr_userItemType']
                targetbattery_supplytype = row['supplyType']
                targetbattery_state = row['outData.pp_states']
                targetbattery_parttype = row['dataType']
                targetbattery_spec = row['outData.mr_siteTechnicalSpec']
                targetbattery_uniquieid = row['uniqueStr']
            targetbattery_pn = MR_battery['childNameDisplay'].iloc[0]
            targetbattery_qty = MR_battery['bomQuantity'].iloc[0]
            targetbattery_level = MR_battery['bomLevel'].iloc[0]
            targetbattery_uit = MR_battery['outData.mr_userItemType'].iloc[0]
            targetbattery_supplytype = MR_battery['supplyType'].iloc[0]
            targetbattery_state = MR_battery['outData.pp_states'].iloc[0]
            targetbattery_parttype = MR_battery['dataType'].iloc[0]
            targetbattery_spec = MR_battery['outData.mr_siteTechnicalSpec'].iloc[0]
            targetbattery_uniquieid = MR_battery['uniqueStr'].iloc[0]
        else:
            targetbattery_pn = ""
            targetbattery_qty = ""
            targetbattery_level = ""
            targetbattery_uit = ""
            targetbattery_supplytype = ""
            targetbattery_state = ""
            targetbattery_parttype = ""
            targetbattery_spec = ""
            targetbattery_uniquieid = ""
        #<Search for specific components in EBOM data (L-Con battery)
        Lcon_battery = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                "130" in "{}".format(item.get("childNameDisplay", "")) and
                "Battery" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))
                ))
            ])
        if not Lcon_battery.empty:
            for idx, row in Lcon_battery.iterrows():
                targetlconbattery_pn = row['childNameDisplay']
                targetlconbattery_qty = row['bomQuantity']
                targetlconbattery_level = row['bomLevel']
                targetlconbattery_uit = row['outData.mr_userItemType']
                targetlconbattery_supplytype = row['supplyType']
                targetlconbattery_state = row['outData.pp_states']
                targetlconbattery_parttype = row['dataType']
                targetlconbattery_spec = row['outData.mr_siteTechnicalSpec']
                targetlconbattery_uniquieid = row['uniqueStr']
            targetlconbattery_pn = Lcon_battery['childNameDisplay'].iloc[0]
            targetlconbattery_qty = Lcon_battery['bomQuantity'].iloc[0]
            targetlconbattery_level = Lcon_battery['bomLevel'].iloc[0]
            targetlconbattery_uit = Lcon_battery['outData.mr_userItemType'].iloc[0]
            targetlconbattery_supplytype = Lcon_battery['supplyType'].iloc[0]
            targetlconbattery_state = Lcon_battery['outData.pp_states'].iloc[0]
            targetlconbattery_parttype = Lcon_battery['dataType'].iloc[0]
            targetlconbattery_spec = Lcon_battery['outData.mr_siteTechnicalSpec'].iloc[0]
            targetlconbattery_uniquieid = Lcon_battery['uniqueStr'].iloc[0]
        else:
            targetlconbattery_pn = ""
            targetlconbattery_qty = ""
            targetlconbattery_level = ""
            targetlconbattery_uit = ""
            targetlconbattery_supplytype = ""
            targetlconbattery_state = ""
            targetlconbattery_parttype = ""
            targetlconbattery_spec = ""
            targetlconbattery_uniquieid = ""    
        #<Search for specific components in EBOM data (MR remote)
        MR_remote = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetaccessory_uniquieid and
                "AKB" in "{}".format(item.get("childNameDisplay", "")) and
                "Remote" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "MR" in "{}".format(item.get("outData", {}).get('mr_siteTechnicalSpec', ""))
                ))
            ])
        if not MR_remote.empty:
            for idx, row in MR_remote.iterrows():
                targetremote_pn = row['childNameDisplay']
                targetremote_qty = row['bomQuantity']
                targetremote_level = row['bomLevel']
                targetremote_uit = row['outData.mr_userItemType']
                targetremote_supplytype = row['supplyType']
                targetremote_state = row['outData.pp_states']
                targetremote_parttype = row['dataType']
                targetremote_spec = row['outData.mr_siteTechnicalSpec']
                targetremote_uniquieid = row['uniqueStr']
            targetremote_pn = MR_remote['childNameDisplay'].iloc[0]
            targetremote_qty = MR_remote['bomQuantity'].iloc[0]
            targetremote_level = MR_remote['bomLevel'].iloc[0]
            targetremote_uit = MR_remote['outData.mr_userItemType'].iloc[0]
            targetremote_supplytype = MR_remote['supplyType'].iloc[0]
            targetremote_state = MR_remote['outData.pp_states'].iloc[0]
            targetremote_parttype = MR_remote['dataType'].iloc[0]
            targetremote_spec = MR_remote['outData.mr_siteTechnicalSpec'].iloc[0]
            targetremote_uniquieid = MR_remote['uniqueStr'].iloc[0]
        else:
            targetremote_pn = ""
            targetremote_qty = ""
            targetremote_level = ""
            targetremote_uit = ""
            targetremote_supplytype = ""
            targetremote_state = ""
            targetremote_parttype = ""
            targetremote_spec = ""
            targetremote_uniquieid = ""
        #<Search for specific components in EBOM data (L-Con remote)
        Lcon_remote = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                "AKB" in "{}".format(item.get("childNameDisplay", "")) and
                "Remote" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "L-Con" in "{}".format(item.get("outData", {}).get('mr_siteTechnicalSpec', ""))
                ))
            ])
        if not Lcon_remote.empty:
            for idx, row in Lcon_remote.iterrows():
                targetlconremote_pn = row['childNameDisplay']
                targetlconremote_qty = row['bomQuantity']
                targetlconremote_level = row['bomLevel']
                targetlconremote_uit = row['outData.mr_userItemType']
                targetlconremote_supplytype = row['supplyType']
                targetlconremote_state = row['outData.pp_states']
                targetlconremote_parttype = row['dataType']
                targetlconremote_spec = row['outData.mr_siteTechnicalSpec']
                targetlconremote_uniquieid = row['uniqueStr']
            targetlconremote_pn = Lcon_remote['childNameDisplay'].iloc[0]
            targetlconremote_qty = Lcon_remote['bomQuantity'].iloc[0]
            targetlconremote_level = Lcon_remote['bomLevel'].iloc[0]
            targetlconremote_uit = Lcon_remote['outData.mr_userItemType'].iloc[0]
            targetlconremote_supplytype = Lcon_remote['supplyType'].iloc[0]
            targetlconremote_state = Lcon_remote['outData.pp_states'].iloc[0]
            targetlconremote_parttype = Lcon_remote['dataType'].iloc[0]
            targetlconremote_spec = Lcon_remote['outData.mr_siteTechnicalSpec'].iloc[0]
            targetlconremote_uniquieid = Lcon_remote['uniqueStr'].iloc[0]
        else:
            targetlconremote_pn = ""
            targetlconremote_qty = ""
            targetlconremote_level = ""
            targetlconremote_uit = ""
            targetlconremote_supplytype = ""
            targetlconremote_state = ""
            targetlconremote_parttype = ""
            targetlconremote_spec = ""
            targetlconremote_uniquieid = ""
        #<Search for specific components in EBOM data (Bracket Assy)
        Bracket_Assy = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == "00001" and
                ("ABA" in "{}".format(item.get("childNameDisplay", "")) and 
                "Bracket Assembly,Sub" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))) or
                ("ACQ" in "{}".format(item.get("childNameDisplay", "")) and
                "Bracket Assembly" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))) and
                ("Wifi" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or 
                "IR" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "SUB" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
            ))
            ])
        if not Bracket_Assy.empty:
            for idx, row in Bracket_Assy.iterrows():
                targetbracketassy_pn = row['childNameDisplay']
                targetbracketassy_qty = row['bomQuantity']
                targetbracketassy_level = row['bomLevel']
                targetbracketassy_uit = row['outData.mr_userItemType']
                targetbracketassy_supplytype = row['supplyType']
                targetbracketassy_state = row['outData.pp_states']
                targetbracketassy_parttype = row['dataType']
                targetbracketassy_spec = row['outData.mr_siteTechnicalSpec']
                targetbracketassy_uniquieid = row['uniqueStr']
        else:
            targetbracketassy_pn = ""
            targetbracketassy_qty = ""
            targetbracketassy_level = ""
            targetbracketassy_uit = ""
            targetbracketassy_supplytype = ""
            targetbracketassy_state = ""
            targetbracketassy_parttype = ""
            targetbracketassy_spec = ""
            targetbracketassy_uniquieid = ""
        #<Search for specific components in EBOM data (Wifi Assy)
        EBT_Subassy = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetbracketassy_uniquieid and
                "EBT" in "{}".format(item.get("childNameDisplay", "")) and 
                "Chassis Assembly,Sub" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Wifi" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or 
                "IR" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "SUB" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not EBT_Subassy.empty:
            for idx, row in EBT_Subassy.iterrows():
                targetebtassy_pn = row['childNameDisplay']
                targetebtassy_qty = row['bomQuantity']
                targetebtassy_level = row['bomLevel']
                targetebtassy_uit = row['outData.mr_userItemType']
                targetebtassy_supplytype = row['supplyType']
                targetebtassy_state = row['outData.pp_states']
                targetebtassy_parttype = row['dataType']
                targetebtassy_spec = row['outData.mr_siteTechnicalSpec']
                targetebtassy_uniquieid = row['uniqueStr']
            targetebtassy_pn =EBT_Subassy['childNameDisplay'].iloc[0]
            targetebtassy_qty =EBT_Subassy['bomQuantity'].iloc[0]
            targetebtassy_level =EBT_Subassy['bomLevel'].iloc[0]
            targetebtassy_uit =EBT_Subassy['outData.mr_userItemType'].iloc[0]
            targetebtassy_supplytype =EBT_Subassy['supplyType'].iloc[0]
            targetebtassy_state =EBT_Subassy['outData.pp_states'].iloc[0]
            targetebtassy_parttype =EBT_Subassy['dataType'].iloc[0]
            targetebtassy_spec =EBT_Subassy['outData.mr_siteTechnicalSpec'].iloc[0]
            targetebtassy_uniquieid =EBT_Subassy['uniqueStr'].iloc[0]
        else:
            targetebtassy_pn = ""
            targetebtassy_qty = ""
            targetebtassy_level = ""
            targetebtassy_uit = ""
            targetebtassy_supplytype = ""
            targetebtassy_state = ""
            targetebtassy_parttype = ""
            targetebtassy_spec = ""
            targetebtassy_uniquieid = ""
        #<Search for specific components in EBOM data (Wifi Assy)
        Wifi_assy = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                (item.get("uniqueStrParent") == targetebtassy_uniquieid and
                "EAT" in "{}".format(item.get("childNameDisplay", "")) and 
                "Module,Wifi Bluetooth Module" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "LGSW" in "{}".format(item.get("outData", {}).get('mr_siteTechnicalSpec', ""))) or
                (item.get("uniqueStrParent") == targetebtassy_uniquieid and
                "EBR" in "{}".format(item.get("childNameDisplay", "")) and 
                "PCB Assembly,Sub" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "CKD" in "{}".format(item.get("outData", {}).get('mr_siteTechnicalSpec', "")))
                ))
            ])
        if not Wifi_assy.empty:
            for idx, row in Wifi_assy.iterrows():
                targetwifiassy_pn = row['childNameDisplay']
                targetwifiassy_qty = row['bomQuantity']
                targetwifiassy_level = row['bomLevel']
                targetwifiassy_uit = row['outData.mr_userItemType']
                targetwifiassy_supplytype = row['supplyType']
                targetwifiassy_state = row['outData.pp_states']
                targetwifiassy_parttype = row['dataType']
                targetwifiassy_spec = row['outData.mr_siteTechnicalSpec']
                targetwifiassy_uniquieid = row['uniqueStr']
            targetwifiassy_pn =Wifi_assy['childNameDisplay'].iloc[0]
            targetwifiassy_qty =Wifi_assy['bomQuantity'].iloc[0]
            targetwifiassy_level =Wifi_assy['bomLevel'].iloc[0]
            targetwifiassy_uit =Wifi_assy['outData.mr_userItemType'].iloc[0]
            targetwifiassy_supplytype =Wifi_assy['supplyType'].iloc[0]
            targetwifiassy_state =Wifi_assy['outData.pp_states'].iloc[0]
            targetwifiassy_parttype =Wifi_assy['dataType'].iloc[0]
            targetwifiassy_spec =Wifi_assy['outData.mr_siteTechnicalSpec'].iloc[0]
            targetwifiassy_uniquieid =Wifi_assy['uniqueStr'].iloc[0]
        else:
            targetwifiassy_pn = ""
            targetwifiassy_qty = ""
            targetwifiassy_level = ""
            targetwifiassy_uit = ""
            targetwifiassy_supplytype = ""
            targetwifiassy_state = ""
            targetwifiassy_parttype = ""
            targetwifiassy_spec = ""
            targetwifiassy_uniquieid = ""
        #<Search for specific components in EBOM data (IR Assy)
        IR_assy = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtassy_uniquieid and
                "EBR" in "{}".format(item.get("childNameDisplay", "")) and 
                "PCB Assembly,IR Key" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "IR" in "{}".format(item.get("outData", {}).get('mr_siteTechnicalSpec', ""))
                ))
            ])
        if not IR_assy.empty:
            for idx, row in IR_assy.iterrows():
                targetirassy_pn = row['childNameDisplay']
                targetirassy_qty = row['bomQuantity']
                targetirassy_level = row['bomLevel']
                targetirassy_uit = row['outData.mr_userItemType']
                targetirassy_supplytype = row['supplyType']
                targetirassy_state = row['outData.pp_states']        
                targetirassy_parttype = row['dataType']
                targetirassy_spec = row['outData.mr_siteTechnicalSpec']
                targetirassy_uniquieid = row['uniqueStr']
            targetirassy_pn = IR_assy['childNameDisplay'].iloc[0]
            targetirassy_qty = IR_assy['bomQuantity'].iloc[0]
            targetirassy_level = IR_assy['bomLevel'].iloc[0]
            targetirassy_uit = IR_assy['outData.mr_userItemType'].iloc[0]
            targetirassy_supplytype = IR_assy['supplyType'].iloc[0]
            targetirassy_state = IR_assy['outData.pp_states'].iloc[0]
            targetirassy_parttype = IR_assy['dataType'].iloc[0]
            targetirassy_spec = IR_assy['outData.mr_siteTechnicalSpec'].iloc[0]
            targetirassy_uniquieid = IR_assy['uniqueStr'].iloc[0]
        else:
            targetirassy_pn = ""
            targetirassy_qty = ""
            targetirassy_level = ""
            targetirassy_uit = ""
            targetirassy_supplytype = ""
            targetirassy_state = ""
            targetirassy_parttype = ""
            targetirassy_spec = ""
            targetirassy_uniquieid = ""
        #<Search for specific components in EBOM data (FFC Assy)
        FFC_assy = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtassy_uniquieid and
                "EAD" in "{}".format(item.get("childNameDisplay", "")) and 
                "Cable,FFC" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Wifi" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or 
                "IR" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not FFC_assy.empty:
            for idx, row in FFC_assy.iterrows():
                targetffcassy_pn = row['childNameDisplay']
                targetffcassy_qty = row['bomQuantity']
                targetffcassy_level = row['bomLevel']
                targetffcassy_uit = row['outData.mr_userItemType']
                targetffcassy_supplytype = row['supplyType']
                targetffcassy_state = row['outData.pp_states']
                targetffcassy_parttype = row['dataType']
                targetffcassy_spec = row['outData.mr_siteTechnicalSpec']
                targetffcassy_uniquieid = row['uniqueStr']
            targetffcassy_pn = FFC_assy['childNameDisplay'].iloc[0]
            targetffcassy_qty = FFC_assy['bomQuantity'].iloc[0]
            targetffcassy_level = FFC_assy['bomLevel'].iloc[0]
            targetffcassy_uit = FFC_assy['outData.mr_userItemType'].iloc[0]
            targetffcassy_supplytype = FFC_assy['supplyType'].iloc[0]
            targetffcassy_state = FFC_assy['outData.pp_states'].iloc[0]
            targetffcassy_parttype = FFC_assy['dataType'].iloc[0]
            targetffcassy_spec = FFC_assy['outData.mr_siteTechnicalSpec'].iloc[0]
            targetffcassy_uniquieid = FFC_assy['uniqueStr'].iloc[0]
        else:
            targetffcassy_pn = ""
            targetffcassy_qty = ""
            targetffcassy_level = ""
            targetffcassy_uit = ""
            targetffcassy_supplytype = ""
            targetffcassy_state = ""
            targetffcassy_parttype = ""
            targetffcassy_spec = ""
            targetffcassy_uniquieid = ""
        #<Search for specific components in EBOM data (Speaker Right)
        Speaker_Right = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == "00001" and
                "EAB" in "{}".format(item.get("childNameDisplay", "")) and 
                "Speaker" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "RIGHT" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", ""))
                ))
            ])
        if not Speaker_Right.empty:
            for idx, row in Speaker_Right.iterrows():
                targetspeakerright_pn = row['childNameDisplay']
                targetspeakerright_qty = row['bomQuantity']
                targetspeakerright_level = row['bomLevel']
                targetspeakerright_uit = row['outData.mr_userItemType']
                targetspeakerright_supplytype = row['supplyType']
                targetspeakerright_state = row['outData.pp_states']
                targetspeakerright_parttype = row['dataType']
                targetspeakerright_spec = row['outData.mr_siteTechnicalSpec']
                targetspeakerright_uniquieid = row['uniqueStr']
            targetspeakerright_pn = Speaker_Right['childNameDisplay'].iloc[0]
            targetspeakerright_qty = Speaker_Right['bomQuantity'].iloc[0]
            targetspeakerright_level = Speaker_Right['bomLevel'].iloc[0]
            targetspeakerright_uit = Speaker_Right['outData.mr_userItemType'].iloc[0]
            targetspeakerright_supplytype = Speaker_Right['supplyType'].iloc[0]
            targetspeakerright_state = Speaker_Right['outData.pp_states'].iloc[0]
            targetspeakerright_parttype = Speaker_Right['dataType'].iloc[0]
            targetspeakerright_spec = Speaker_Right['outData.mr_siteTechnicalSpec'].iloc[0]
            targetspeakerright_uniquieid = Speaker_Right['uniqueStr'].iloc[0]
        else:
            targetspeakerright_pn = ""
            targetspeakerright_qty = ""
            targetspeakerright_level = ""
            targetspeakerright_uit = ""
            targetspeakerright_supplytype = ""
            targetspeakerright_state = ""
            targetspeakerright_parttype = ""
            targetspeakerright_spec = ""
            targetspeakerright_uniquieid = ""
        #<Search for specific components in EBOM data (Speaker Left)
        Speaker_Left = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == "00001" and
                "EAB" in "{}".format(item.get("childNameDisplay", "")) and 
                "Speaker" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "LEFT" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", ""))
                ))
            ])
        if not Speaker_Left.empty:
            for idx, row in Speaker_Left.iterrows():
                targetspeakerleft_pn = row['childNameDisplay']
                targetspeakerleft_qty = row['bomQuantity']
                targetspeakerleft_level = row['bomLevel']
                targetspeakerleft_uit = row['outData.mr_userItemType']
                targetspeakerleft_supplytype = row['supplyType']
                targetspeakerleft_state = row['outData.pp_states']
                targetspeakerleft_parttype = row['dataType']
                targetspeakerleft_spec = row['outData.mr_siteTechnicalSpec']
                targetspeakerleft_uniquieid = row['uniqueStr']
            targetspeakerleft_pn = Speaker_Left['childNameDisplay'].iloc[0]
            targetspeakerleft_qty = Speaker_Left['bomQuantity'].iloc[0]
            targetspeakerleft_level = Speaker_Left['bomLevel'].iloc[0]        
            targetspeakerleft_uit = Speaker_Left['outData.mr_userItemType'].iloc[0]
            targetspeakerleft_supplytype = Speaker_Left['supplyType'].iloc[0]
            targetspeakerleft_state = Speaker_Left['outData.pp_states'].iloc[0]
            targetspeakerleft_parttype = Speaker_Left['dataType'].iloc[0]
            targetspeakerleft_spec = Speaker_Left['outData.mr_siteTechnicalSpec'].iloc[0]
            targetspeakerleft_uniquieid = Speaker_Left['uniqueStr'].iloc[0]
        else:
            targetspeakerleft_pn = ""
            targetspeakerleft_qty = ""
            targetspeakerleft_level = ""
            targetspeakerleft_uit = ""
            targetspeakerleft_supplytype = ""
            targetspeakerleft_state = ""
            targetspeakerleft_parttype = ""
            targetspeakerleft_spec = ""
            targetspeakerleft_uniquieid = ""    
        #<Search for specific components in EBOM data (Speaker Assy)
        Speaker_assy = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == "00001" and
                "EAB" in "{}".format(item.get("childNameDisplay", "")) and 
                "Speaker" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))
                ))
            ])
        if not Speaker_assy.empty:
            for idx, row in Speaker_assy.iterrows():
                targetspeaker_pn = row['childNameDisplay']
                targetspeaker_qty = row['bomQuantity']
                targetspeaker_level = row['bomLevel']
                targetspeaker_uit = row['outData.mr_userItemType']
                targetspeaker_supplytype = row['supplyType']
                targetspeaker_state = row['outData.pp_states']
                targetspeaker_parttype = row['dataType']
                targetspeaker_spec = row['outData.mr_siteTechnicalSpec']
                targetspeaker_uniquieid = row['uniqueStr']
            targetspeaker_pn = Speaker_assy['childNameDisplay'].iloc[0]
            targetspeaker_qty = Speaker_assy['bomQuantity'].iloc[0]
            targetspeaker_level = Speaker_assy['bomLevel'].iloc[0]        
            targetspeaker_uit = Speaker_assy['outData.mr_userItemType'].iloc[0]
            targetspeaker_supplytype = Speaker_assy['supplyType'].iloc[0]
            targetspeaker_state = Speaker_assy['outData.pp_states'].iloc[0]
            targetspeaker_parttype = Speaker_assy['dataType'].iloc[0]
            targetspeaker_spec = Speaker_assy['outData.mr_siteTechnicalSpec'].iloc[0]
            targetspeaker_uniquieid = Speaker_assy['uniqueStr'].iloc[0]
        else:
            targetspeaker_pn = ""
            targetspeaker_qty = ""
            targetspeaker_level = ""
            targetspeaker_uit = ""
            targetspeaker_supplytype = ""
            targetspeaker_state = ""
            targetspeaker_parttype = ""
            targetspeaker_spec = ""
            targetspeaker_uniquieid
        #<Search for specific components in EBOM data (FFC Main)
        FFC_Main = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                "EAD" in "{}".format(item.get("childNameDisplay", "")) and 
                "Cable,FFC" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("68P" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or 
                "CEDS" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "VBY1" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "VX1" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "EPI" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        targets_ffc = []  # tampung semua baris
        if not FFC_Main.empty:
            for _, row in FFC_Main.head(5).iterrows():
                targets_ffc.append({
                    "pn":           row.get("childNameDisplay"),
                    "qty":          row.get("bomQuantity"),
                    "level":        row.get("bomLevel"),
                    "uit":          row.get("outData.mr_userItemType"),
                    "supplytype":   row.get("supplyType"),
                    "state":        row.get("outData.pp_states"),
                    "parttype":     row.get("dataType"),
                    "spec":         row.get("outData.mr_siteTechnicalSpec"),
                    "uniqueid":     row.get("uniqueStr"),
                })
        # contoh akses aman:
        if len(targets_ffc) >= 1:
            targetffcmain1_pn = targets_ffc[0]["pn"]
            targetffcmain1_qty = targets_ffc[0]["qty"]
            targetffcmain1_level = targets_ffc[0]["level"]
            targetffcmain1_uit = targets_ffc[0]["uit"]
            targetffcmain1_supplytype = targets_ffc[0]["supplytype"]
            targetffcmain1_state = targets_ffc[0]["state"]
            targetffcmain1_parttype = targets_ffc[0]["parttype"]
            targetffcmain1_spec = targets_ffc[0]["spec"]
            targetffcmain1_uniquieid = targets_ffc[0]["uniqueid"]
        else:
            targetffcmain1_pn = ""
            targetffcmain1_qty = ""
            targetffcmain1_level = ""
            targetffcmain1_uit = ""
            targetffcmain1_supplytype = ""
            targetffcmain1_state = ""
            targetffcmain1_parttype = ""
            targetffcmain1_spec = ""
            targetffcmain1_uniquieid = ""
        if len(targets_ffc) >= 2:
            targetffcmain2_pn = targets_ffc[1]["pn"]
            targetffcmain2_qty = targets_ffc[1]["qty"]
            targetffcmain2_level = targets_ffc[1]["level"]
            targetffcmain2_uit = targets_ffc[1]["uit"]
            targetffcmain2_supplytype = targets_ffc[1]["supplytype"]
            targetffcmain2_state = targets_ffc[1]["state"]
            targetffcmain2_parttype = targets_ffc[1]["parttype"]
            targetffcmain2_spec = targets_ffc[1]["spec"]
            targetffcmain2_uniquieid = targets_ffc[1]["uniqueid"]
        else:
            targetffcmain2_pn = ""
            targetffcmain2_qty = ""
            targetffcmain2_level = ""
            targetffcmain2_uit = ""
            targetffcmain2_supplytype = ""
            targetffcmain2_state = ""
            targetffcmain2_parttype = ""
            targetffcmain2_spec = ""
            targetffcmain2_uniquieid = ""
        #<Search for specific components in EBOM data (EBT Power Cord)
        EBT_Powercord = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == "00001" and
                "EBT" in "{}".format(item.get("childNameDisplay", "")) and 
                "Chassis Assembly,Sub" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("P_Cord Assy" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or 
                "Power Cord" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "Powercord" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "P_Cord" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not EBT_Powercord.empty:
            for idx, row in EBT_Powercord.iterrows():
                targetebtpowercord_pn = row['childNameDisplay']
                targetebtpowercord_qty = row['bomQuantity']
                targetebtpowercord_level = row['bomLevel']
                targetebtpowercord_uit = row['outData.mr_userItemType']
                targetebtpowercord_supplytype = row['supplyType']
                targetebtpowercord_state = row['outData.pp_states']
                targetebtpowercord_parttype = row['dataType']
                targetebtpowercord_spec = row['outData.mr_siteTechnicalSpec']
                targetebtpowercord_uniquieid = row['uniqueStr']
            targetebtpowercord_pn = EBT_Powercord['childNameDisplay'].iloc[0]
            targetebtpowercord_qty = EBT_Powercord['bomQuantity'].iloc[0]
            targetebtpowercord_level = EBT_Powercord['bomLevel'].iloc[0]        
            targetebtpowercord_uit = EBT_Powercord['outData.mr_userItemType'].iloc[0]
            targetebtpowercord_supplytype = EBT_Powercord['supplyType'].iloc[0]
            targetebtpowercord_state = EBT_Powercord['outData.pp_states'].iloc[0]
            targetebtpowercord_parttype = EBT_Powercord['dataType'].iloc[0]
            targetebtpowercord_spec = EBT_Powercord['outData.mr_siteTechnicalSpec'].iloc[0]
            targetebtpowercord_uniquieid = EBT_Powercord['uniqueStr'].iloc[0]
        else:
            targetebtpowercord_pn = ""
            targetebtpowercord_qty = ""
            targetebtpowercord_level = ""
            targetebtpowercord_uit = ""
            targetebtpowercord_supplytype = ""
            targetebtpowercord_state = ""
            targetebtpowercord_parttype = ""
            targetebtpowercord_spec = ""
            targetebtpowercord_uniquieid = ""
        #<Search for specific components in EBOM data (Power Cord Attach)
        Powercord_attach = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtpowercord_uniquieid and
                "EAD" in "{}".format(item.get("childNameDisplay", "")) and 
                "Power Cord,Attach" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("AT" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Powercord_attach.empty:
            for idx, row in Powercord_attach.iterrows():
                targetpowercordattach_pn = row['childNameDisplay']
                targetpowercordattach_qty = row['bomQuantity']
                targetpowercordattach_level = row['bomLevel']
                targetpowercordattach_uit = row['outData.mr_userItemType']
                targetpowercordattach_supplytype = row['supplyType']
                targetpowercordattach_state = row['outData.pp_states']
                targetpowercordattach_parttype = row['dataType']
                targetpowercordattach_spec = row['outData.mr_siteTechnicalSpec']
                targetpowercordattach_uniquieid = row['uniqueStr']
            targetpowercordattach_pn = Powercord_attach['childNameDisplay'].iloc[0]
            targetpowercordattach_qty = Powercord_attach['bomQuantity'].iloc[0]
            targetpowercordattach_level = Powercord_attach['bomLevel'].iloc[0]        
            targetpowercordattach_uit = Powercord_attach['outData.mr_userItemType'].iloc[0]
            targetpowercordattach_supplytype = Powercord_attach['supplyType'].iloc[0]
            targetpowercordattach_state = Powercord_attach['outData.pp_states'].iloc[0]
            targetpowercordattach_parttype = Powercord_attach['dataType'].iloc[0]
            targetpowercordattach_spec = Powercord_attach['outData.mr_siteTechnicalSpec'].iloc[0]
            targetpowercordattach_uniquieid = Powercord_attach['uniqueStr'].iloc[0]
        else:
            targetpowercordattach_pn = ""
            targetpowercordattach_qty = ""
            targetpowercordattach_level = ""
            targetpowercordattach_uit = ""
            targetpowercordattach_supplytype = ""
            targetpowercordattach_state = ""
            targetpowercordattach_parttype = ""
            targetpowercordattach_spec = ""
            targetpowercordattach_uniquieid = ""
        #<Search for specific components in EBOM data (Power Cord Detach)
        Powercord_detach = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                "EAD" in "{}".format(item.get("childNameDisplay", "")) and 
                "Power Cord,Detach" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("DE" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Powercord_detach.empty:
            for idx, row in Powercord_detach.iterrows():
                targetpowercorddetach_pn = row['childNameDisplay']
                targetpowercorddetach_qty = row['bomQuantity']
                targetpowercorddetach_level = row['bomLevel']
                targetpowercorddetach_uit = row['outData.mr_userItemType']
                targetpowercorddetach_supplytype = row['supplyType']
                targetpowercorddetach_state = row['outData.pp_states']
                targetpowercorddetach_parttype = row['dataType']
                targetpowercorddetach_spec = row['outData.mr_siteTechnicalSpec']
                targetpowercorddetach_uniquieid = row['uniqueStr']
            targetpowercorddetach_pn = Powercord_detach['childNameDisplay'].iloc[0]
            targetpowercorddetach_qty = Powercord_detach['bomQuantity'].iloc[0]
            targetpowercorddetach_level = Powercord_detach['bomLevel'].iloc[0]        
            targetpowercorddetach_uit = Powercord_detach['outData.mr_userItemType'].iloc[0]
            targetpowercorddetach_supplytype = Powercord_detach['supplyType'].iloc[0]
            targetpowercorddetach_state = Powercord_detach['outData.pp_states'].iloc[0]
            targetpowercorddetach_parttype = Powercord_detach['dataType'].iloc[0]
            targetpowercorddetach_spec = Powercord_detach['outData.mr_siteTechnicalSpec'].iloc[0]
            targetpowercorddetach_uniquieid = Powercord_detach['uniqueStr'].iloc[0]
        else:
            targetpowercorddetach_pn = ""
            targetpowercorddetach_qty = ""
            targetpowercorddetach_level = ""
            targetpowercorddetach_uit = ""
            targetpowercorddetach_supplytype = ""
            targetpowercorddetach_state = ""
            targetpowercorddetach_parttype = ""
            targetpowercorddetach_spec = ""
            targetpowercorddetach_uniquieid = ""
        #<Search for specific components in EBOM data (Power Board)
        Power_Board = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == "00001" and
                ("EAY" in "{}".format(item.get("childNameDisplay", "")) or
                "EBR" in "{}".format(item.get("childNameDisplay", ""))) and
                "Power" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("LGP" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Power_Board.empty:
            for idx, row in Power_Board.iterrows():
                targetpowerboard_pn = row['childNameDisplay']
                targetpowerboard_qty = row['bomQuantity']
                targetpowerboard_level = row['bomLevel']
                targetpowerboard_uit = row['outData.mr_userItemType']
                targetpowerboard_supplytype = row['supplyType']
                targetpowerboard_state = row['outData.pp_states']
                targetpowerboard_parttype = row['dataType']
                targetpowerboard_spec = row['outData.mr_siteTechnicalSpec']
                targetpowerboard_uniquieid = row['uniqueStr']
            targetpowerboard_pn = Power_Board['childNameDisplay'].iloc[0]
            targetpowerboard_qty = Power_Board['bomQuantity'].iloc[0]
            targetpowerboard_level = Power_Board['bomLevel'].iloc[0]
            targetpowerboard_uit = Power_Board['outData.mr_userItemType'].iloc[0]
            targetpowerboard_supplytype = Power_Board['supplyType'].iloc[0]
            targetpowerboard_state = Power_Board['outData.pp_states'].iloc[0]
            targetpowerboard_parttype = Power_Board['dataType'].iloc[0]
            targetpowerboard_spec = Power_Board['outData.mr_siteTechnicalSpec'].iloc[0]
            targetpowerboard_uniquieid = Power_Board['uniqueStr'].iloc[0]
        else:
            targetpowerboard_pn = ""
            targetpowerboard_qty = ""
            targetpowerboard_level = ""
            targetpowerboard_uit = ""
            targetpowerboard_supplytype = ""
            targetpowerboard_state = ""
            targetpowerboard_parttype = ""
            targetpowerboard_spec = ""
            targetpowerboard_uniquieid = ""
        #<Search for specific components in EBOM data (EBT Main)
        EBT_Main = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == "00001" and
                "EBT" in "{}".format(item.get("childNameDisplay", "")) and 
                "Chassis Assembly" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("MAIN" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not EBT_Main.empty:
            for idx, row in EBT_Main.iterrows():
                targetebtmain_pn = row['childNameDisplay']
                targetebtmain_qty = row['bomQuantity']
                targetebtmain_level = row['bomLevel']
                targetebtmain_uit = row['outData.mr_userItemType']
                targetebtmain_supplytype = row['supplyType']
                targetebtmain_state = row['outData.pp_states']
                targetebtmain_parttype = row['dataType']
                targetebtmain_spec = row['outData.mr_siteTechnicalSpec']
                targetebtmain_uniquieid = row['uniqueStr']
            targetebtmain_pn = EBT_Main['childNameDisplay'].iloc[0]
            targetebtmain_qty = EBT_Main['bomQuantity'].iloc[0]
            targetebtmain_level = EBT_Main['bomLevel'].iloc[0]
            targetebtmain_uit = EBT_Main['outData.mr_userItemType'].iloc[0]
            targetebtmain_supplytype = EBT_Main['supplyType'].iloc[0]
            targetebtmain_state = EBT_Main['outData.pp_states'].iloc[0]
            targetebtmain_parttype = EBT_Main['dataType'].iloc[0]
            targetebtmain_spec = EBT_Main['outData.mr_siteTechnicalSpec'].iloc[0]
            targetebtmain_uniquieid = EBT_Main['uniqueStr'].iloc[0]
        else:
            targetebtmain_pn = ""
            targetebtmain_qty = ""
            targetebtmain_level = ""
            targetebtmain_uit = ""
            targetebtmain_supplytype = ""
            targetebtmain_state = ""
            targetebtmain_parttype = ""
            targetebtmain_spec = ""
            targetebtmain_uniquieid = ""
        #<Search for specific components in EBOM data (Tuner Case Cover)
        Holder_main = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtmain_uniquieid and
                "MEG" in "{}".format(item.get("childNameDisplay", "")) and 
                "Holder" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Holder" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Holder_main.empty:
            for idx, row in Holder_main.iterrows():
                targetholdermain_pn = row['childNameDisplay']
                targetholdermain_qty = row['bomQuantity']
                targetholdermain_level = row['bomLevel']
                targetholdermain_uit = row['outData.mr_userItemType']
                targetholdermain_supplytype = row['supplyType']
                targetholdermain_state = row['outData.pp_states']
                targetholdermain_parttype = row['dataType']
                targetholdermain_spec = row['outData.mr_siteTechnicalSpec']
                targetholdermain_uniquieid = row['uniqueStr']
            targetholdermain_pn = Holder_main['childNameDisplay'].iloc[0]
            targetholdermain_qty = Holder_main['bomQuantity'].iloc[0]
            targetholdermain_level = Holder_main['bomLevel'].iloc[0]
            targetholdermain_uit = Holder_main['outData.mr_userItemType'].iloc[0]
            targetholdermain_supplytype = Holder_main['supplyType'].iloc[0]
            targetholdermain_state = Holder_main['outData.pp_states'].iloc[0]
            targetholdermain_parttype = Holder_main['dataType'].iloc[0]
            targetholdermain_spec = Holder_main['outData.mr_siteTechnicalSpec'].iloc[0]
            targetholdermain_uniquieid = Holder_main['uniqueStr'].iloc[0]
        else:
            targetholdermain_pn = ""
            targetholdermain_qty = ""
            targetholdermain_level = ""
            targetholdermain_uit = ""
            targetholdermain_supplytype = ""
            targetholdermain_state = ""
            targetholdermain_parttype = ""
            targetholdermain_spec = ""
            targetholdermain_uniquieid = ""
        #<Search for specific components in EBOM data (Tuner Case Cover)
        Tuner_cover = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtmain_uniquieid and
                "EBZ" in "{}".format(item.get("childNameDisplay", "")) and 
                "Part" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Tuner" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Tuner_cover.empty:
            for idx, row in Tuner_cover.iterrows():
                targettunercover_pn = row['childNameDisplay']
                targettunercover_qty = row['bomQuantity']
                targettunercover_level = row['bomLevel']
                targettunercover_uit = row['outData.mr_userItemType']
                targettunercover_supplytype = row['supplyType']
                targettunercover_state = row['outData.pp_states']
                targettunercover_parttype = row['dataType']
                targettunercover_spec = row['outData.mr_siteTechnicalSpec']
                targettunercover_uniquieid = row['uniqueStr']
            targettunercover_pn = Tuner_cover['childNameDisplay'].iloc[0]
            targettunercover_qty = Tuner_cover['bomQuantity'].iloc[0]
            targettunercover_level = Tuner_cover['bomLevel'].iloc[0]
            targettunercover_uit = Tuner_cover['outData.mr_userItemType'].iloc[0]
            targettunercover_supplytype = Tuner_cover['supplyType'].iloc[0]
            targettunercover_state = Tuner_cover['outData.pp_states'].iloc[0]
            targettunercover_parttype = Tuner_cover['dataType'].iloc[0]
            targettunercover_spec = Tuner_cover['outData.mr_siteTechnicalSpec'].iloc[0]
            targettunercover_uniquieid = Tuner_cover['uniqueStr'].iloc[0]
        else:
            targettunercover_pn = ""
            targettunercover_qty = ""
            targettunercover_level = ""
            targettunercover_uit = ""
            targettunercover_supplytype = ""
            targettunercover_state = ""
            targettunercover_parttype = ""
            targettunercover_spec = ""
            targettunercover_uniquieid = ""
        #<Search for specific components in EBOM data (Transparent Tape)
        Transparent_Tape = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtmain_uniquieid and
                "961" in "{}".format(item.get("childNameDisplay", "")) and 
                "Tape,Glass Fiber" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("961" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Transparent_Tape.empty:
            for idx, row in Transparent_Tape.iterrows():
                targettransparenttape_pn = row['childNameDisplay']
                targettransparenttape_qty = row['bomQuantity']
                targettransparenttape_level = row['bomLevel']
                targettransparenttape_uit = row['outData.mr_userItemType']
                targettransparenttape_supplytype = row['supplyType']
                targettransparenttape_state = row['outData.pp_states']
                targettransparenttape_parttype = row['dataType']
                targettransparenttape_spec = row['outData.mr_siteTechnicalSpec']
                targettransparenttape_uniquieid = row['uniqueStr']
        else:
            targettransparenttape_pn = ""
            targettransparenttape_qty = ""
            targettransparenttape_level = ""
            targettransparenttape_uit = ""
            targettransparenttape_supplytype = ""
            targettransparenttape_state = ""
            targettransparenttape_parttype = ""
            targettransparenttape_spec = ""
            targettransparenttape_uniquieid = ""
        #<Search for specific components in EBOM data (Harness Single)
        Harness_Single = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtmain_uniquieid and
                "EAD" in "{}".format(item.get("childNameDisplay", "")) and 
                "Harness,Single" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("SMH" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Harness_Single.empty:
            for idx, row in Harness_Single.iterrows():
                targetharnesssingle_pn = row['childNameDisplay']
                targetharnesssingle_qty = row['bomQuantity']
                targetharnesssingle_level = row['bomLevel']
                targetharnesssingle_uit = row['outData.mr_userItemType']
                targetharnesssingle_supplytype = row['supplyType']
                targetharnesssingle_state = row['outData.pp_states']
                targetharnesssingle_parttype = row['dataType']
                targetharnesssingle_spec = row['outData.mr_siteTechnicalSpec']
                targetharnesssingle_uniquieid = row['uniqueStr']
            targetharnesssingle_pn = Harness_Single['childNameDisplay'].iloc[0]
            targetharnesssingle_qty = Harness_Single['bomQuantity'].iloc[0]
            targetharnesssingle_level = Harness_Single['bomLevel'].iloc[0]
            targetharnesssingle_uit = Harness_Single['outData.mr_userItemType'].iloc[0]
            targetharnesssingle_supplytype = Harness_Single['supplyType'].iloc[0]
            targetharnesssingle_state = Harness_Single['outData.pp_states'].iloc[0]
            targetharnesssingle_parttype = Harness_Single['dataType'].iloc[0]
            targetharnesssingle_spec = Harness_Single['outData.mr_siteTechnicalSpec'].iloc[0]
            targetharnesssingle_uniquieid = Harness_Single['uniqueStr'].iloc[0]
        else:
            targetharnesssingle_pn = ""
            targetharnesssingle_qty = ""
            targetharnesssingle_level = ""
            targetharnesssingle_uit = ""
            targetharnesssingle_supplytype = ""
            targetharnesssingle_state = ""
            targetharnesssingle_parttype = ""
            targetharnesssingle_spec = ""
            targetharnesssingle_uniquieid = ""
        #<Search for specific components in EBOM data (Harness Multi)
        Harness_Multi = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtmain_uniquieid and
                "EAD" in "{}".format(item.get("childNameDisplay", "")) and 
                "Harness,Multi" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("250A1" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Harness_Multi.empty:
            for idx, row in Harness_Multi.iterrows():
                targetharnessmulti_pn = row['childNameDisplay']
                targetharnessmulti_qty = row['bomQuantity']
                targetharnessmulti_level = row['bomLevel']
                targetharnessmulti_uit = row['outData.mr_userItemType']
                targetharnessmulti_supplytype = row['supplyType']
                targetharnessmulti_state = row['outData.pp_states']
                targetharnessmulti_parttype = row['dataType']
                targetharnessmulti_spec = row['outData.mr_siteTechnicalSpec']
                targetharnessmulti_uniquieid = row['uniqueStr']
            targetharnessmulti_pn = Harness_Multi['childNameDisplay'].iloc[0]
            targetharnessmulti_qty = Harness_Multi['bomQuantity'].iloc[0]
            targetharnessmulti_level = Harness_Multi['bomLevel'].iloc[0]
            targetharnessmulti_uit = Harness_Multi['outData.mr_userItemType'].iloc[0]
            targetharnessmulti_supplytype = Harness_Multi['supplyType'].iloc[0]
            targetharnessmulti_state = Harness_Multi['outData.pp_states'].iloc[0]
            targetharnessmulti_parttype = Harness_Multi['dataType'].iloc[0]
            targetharnessmulti_spec = Harness_Multi['outData.mr_siteTechnicalSpec'].iloc[0]
            targetharnessmulti_uniquieid = Harness_Multi['uniqueStr'].iloc[0]
        else:
            targetharnessmulti_pn = ""
            targetharnessmulti_qty = ""
            targetharnessmulti_level = ""
            targetharnessmulti_uit = ""
            targetharnessmulti_supplytype = ""
            targetharnessmulti_state = ""
            targetharnessmulti_parttype = ""
            targetharnessmulti_spec = ""
            targetharnessmulti_uniquieid = ""
        #<Search for specific components in EBOM data (Plate Shield Assy)
        Plate_Shield = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtmain_uniquieid and
                "EBS" in "{}".format(item.get("childNameDisplay", "")) and 
                "Electric Parts Assembly,Main" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Shield" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "Plate" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Plate_Shield.empty:
            for idx, row in Plate_Shield.iterrows():
                targetplateshield_pn = row['childNameDisplay']
                targetplateshield_qty = row['bomQuantity']
                targetplateshield_level = row['bomLevel']
                targetplateshield_uit = row['outData.mr_userItemType']
                targetplateshield_supplytype = row['supplyType']
                targetplateshield_state = row['outData.pp_states']
                targetplateshield_parttype = row['dataType']
                targetplateshield_spec = row['outData.mr_siteTechnicalSpec']
                targetplateshield_uniquieid = row['uniqueStr']
            targetplateshield_pn = Plate_Shield['childNameDisplay'].iloc[0]
            targetplateshield_qty = Plate_Shield['bomQuantity'].iloc[0]
            targetplateshield_level = Plate_Shield['bomLevel'].iloc[0]
            targetplateshield_uit = Plate_Shield['outData.mr_userItemType'].iloc[0]
            targetplateshield_supplytype = Plate_Shield['supplyType'].iloc[0]
            targetplateshield_state = Plate_Shield['outData.pp_states'].iloc[0]
            targetplateshield_parttype = Plate_Shield['dataType'].iloc[0]
            targetplateshield_spec = Plate_Shield['outData.mr_siteTechnicalSpec'].iloc[0]
            targetplateshield_uniquieid = Plate_Shield['uniqueStr'].iloc[0]
        else:
            targetplateshield_pn = ""
            targetplateshield_qty = ""
            targetplateshield_level = ""
            targetplateshield_uit = ""
            targetplateshield_supplytype = ""
            targetplateshield_state = ""
            targetplateshield_parttype = ""
            targetplateshield_spec = ""
            targetplateshield_uniquieid = ""
        #<Search for specific components in EBOM data (Plate Shield)
        Plate_Sink = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetplateshield_uniquieid and
                "MED" in "{}".format(item.get("childNameDisplay", "")) or 
                "MGJ" in "{}".format(item.get("childNameDisplay", ""))
                ))
            ])
        if not Plate_Sink.empty:
            for idx, row in Plate_Sink.iterrows():
                targetplatesink_pn = row['childNameDisplay']
                targetplatesink_qty = row['bomQuantity']
                targetplatesink_level = row['bomLevel']
                targetplatesink_uit = row['outData.mr_userItemType']
                targetplatesink_supplytype = row['supplyType']
                targetplatesink_state = row['outData.pp_states']
                targetplatesink_parttype = row['dataType']
                targetplatesink_spec = row['outData.mr_siteTechnicalSpec']
                targetplatesink_uniquieid = row['uniqueStr']
            targetplatesink_pn = Plate_Sink['childNameDisplay'].iloc[0]
            targetplatesink_qty = Plate_Sink['bomQuantity'].iloc[0]
            targetplatesink_level = Plate_Sink['bomLevel'].iloc[0]
            targetplatesink_uit = Plate_Sink['outData.mr_userItemType'].iloc[0]
            targetplatesink_supplytype = Plate_Sink['supplyType'].iloc[0]
            targetplatesink_state = Plate_Sink['outData.pp_states'].iloc[0]
            targetplatesink_parttype = Plate_Sink['dataType'].iloc[0]
            targetplatesink_spec = Plate_Sink['outData.mr_siteTechnicalSpec'].iloc[0]
            targetplatesink_uniquieid = Plate_Sink['uniqueStr'].iloc[0]
        else:
            targetplatesink_pn = ""
            targetplatesink_qty = ""
            targetplatesink_level = ""
            targetplatesink_uit = ""
            targetplatesink_supplytype = ""
            targetplatesink_state = ""
            targetplatesink_parttype = ""
            targetplatesink_spec = ""
            targetplatesink_uniquieid = ""
        #<Search for specific components in EBOM data (Plate Holder)
        Plate_Holder = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetplateshield_uniquieid and
                "MEG" in "{}".format(item.get("childNameDisplay", "")) and
                "Holder" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))
                ))
            ])
        if not Plate_Holder.empty:
            for idx, row in Plate_Holder.iterrows():
                targetplateholder_pn = row['childNameDisplay']
                targetplateholder_qty = row['bomQuantity']
                targetplateholder_level = row['bomLevel']
                targetplateholder_uit = row['outData.mr_userItemType']
                targetplateholder_supplytype = row['supplyType']
                targetplateholder_state = row['outData.pp_states']
                targetplateholder_parttype = row['dataType']
                targetplateholder_spec = row['outData.mr_siteTechnicalSpec']
                targetplateholder_uniquieid = row['uniqueStr']
            targetplateholder_pn = Plate_Holder['childNameDisplay'].iloc[0]
            targetplateholder_qty = Plate_Holder['bomQuantity'].iloc[0]
            targetplateholder_level = Plate_Holder['bomLevel'].iloc[0]
            targetplateholder_uit = Plate_Holder['outData.mr_userItemType'].iloc[0]
            targetplateholder_supplytype = Plate_Holder['supplyType'].iloc[0]
            targetplateholder_state = Plate_Holder['outData.pp_states'].iloc[0]
            targetplateholder_parttype = Plate_Holder['dataType'].iloc[0]
            targetplateholder_spec = Plate_Holder['outData.mr_siteTechnicalSpec'].iloc[0]
            targetplateholder_uniquieid = Plate_Holder['uniqueStr'].iloc[0]
        else:
            targetplateholder_pn = ""
            targetplateholder_qty = ""
            targetplateholder_level = ""
            targetplateholder_uit = ""
            targetplateholder_supplytype = ""
            targetplateholder_state = ""
            targetplateholder_parttype = ""
            targetplateholder_spec = ""
            targetplateholder_uniquieid = ""
        #<Search for specific components in EBOM data (Sheet Cooper)
        Sheet_Cooper = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetplateshield_uniquieid and
                "RAA" in "{}".format(item.get("childNameDisplay", "")) and
                "Sheet,Copper" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))
                ))
            ])
        if not Sheet_Cooper.empty:
            for idx, row in Sheet_Cooper.iterrows():
                targetsheetcooper_pn = row['childNameDisplay']
                targetsheetcooper_qty = row['bomQuantity']
                targetsheetcooper_level = row['bomLevel']
                targetsheetcooper_uit = row['outData.mr_userItemType']
                targetsheetcooper_supplytype = row['supplyType']
                targetsheetcooper_state = row['outData.pp_states']
                targetsheetcooper_parttype = row['dataType']
                targetsheetcooper_spec = row['outData.mr_siteTechnicalSpec']
                targetsheetcooper_uniquieid = row['uniqueStr']
            targetsheetcooper_pn = Sheet_Cooper['childNameDisplay'].iloc[0]
            targetsheetcooper_qty = Sheet_Cooper['bomQuantity'].iloc[0]
            targetsheetcooper_level = Sheet_Cooper['bomLevel'].iloc[0]
            targetsheetcooper_uit = Sheet_Cooper['outData.mr_userItemType'].iloc[0]
            targetsheetcooper_supplytype = Sheet_Cooper['supplyType'].iloc[0]
            targetsheetcooper_state = Sheet_Cooper['outData.pp_states'].iloc[0]
            targetsheetcooper_parttype = Sheet_Cooper['dataType'].iloc[0]
            targetsheetcooper_spec = Sheet_Cooper['outData.mr_siteTechnicalSpec'].iloc[0]
            targetsheetcooper_uniquieid = Sheet_Cooper['uniqueStr'].iloc[0]
        else:
            targetsheetcooper_pn = ""
            targetsheetcooper_qty = ""
            targetsheetcooper_level = ""
            targetsheetcooper_uit = ""
            targetsheetcooper_supplytype = ""
            targetsheetcooper_state = ""
            targetsheetcooper_parttype = ""
            targetsheetcooper_spec = ""
            targetsheetcooper_uniquieid = ""
        #<Search for specific components in EBOM data (EBR Package)
        EBR_Package = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebtmain_uniquieid and
                "EBR" in "{}".format(item.get("childNameDisplay", "")) and 
                "PCB Assembly,Main" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("PAKING" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not EBR_Package.empty:
            for idx, row in EBR_Package.iterrows():
                targetebrpackage_pn = row['childNameDisplay']
                targetebrpackage_qty = row['bomQuantity']
                targetebrpackage_level = row['bomLevel']
                targetebrpackage_uit = row['outData.mr_userItemType']
                targetebrpackage_supplytype = row['supplyType']
                targetebrpackage_state = row['outData.pp_states']
                targetebrpackage_parttype = row['dataType']
                targetebrpackage_spec = row['outData.mr_siteTechnicalSpec']
                targetebrpackage_uniquieid = row['uniqueStr']
            targetebrpackage_pn = EBR_Package['childNameDisplay'].iloc[0]
            targetebrpackage_qty = EBR_Package['bomQuantity'].iloc[0]
            targetebrpackage_level = EBR_Package['bomLevel'].iloc[0]
            targetebrpackage_uit = EBR_Package['outData.mr_userItemType'].iloc[0]
            targetebrpackage_supplytype = EBR_Package['supplyType'].iloc[0]
            targetebrpackage_state = EBR_Package['outData.pp_states'].iloc[0]
            targetebrpackage_parttype = EBR_Package['dataType'].iloc[0]
            targetebrpackage_spec = EBR_Package['outData.mr_siteTechnicalSpec'].iloc[0]
            targetebrpackage_uniquieid = EBR_Package['uniqueStr'].iloc[0]
        else:
            targetebrpackage_pn = ""
            targetebrpackage_qty = ""
            targetebrpackage_level = ""
            targetebrpackage_uit = ""
            targetebrpackage_supplytype = ""
            targetebrpackage_state = ""
            targetebrpackage_parttype = ""
            targetebrpackage_spec = ""
            targetebrpackage_uniquieid = ""
        #<Search for specific components in EBOM data (EBR Package)
        Main_Package = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebrpackage_uniquieid and
                "AGF" in "{}".format(item.get("childNameDisplay", "")) and 
                "Package Assembly" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Package" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Main_Package.empty:
            for idx, row in Main_Package.iterrows():
                targetmainpackage_pn = row['childNameDisplay']
                targetmainpackage_qty = row['bomQuantity']
                targetmainpackage_level = row['bomLevel']
                targetmainpackage_uit = row['outData.mr_userItemType']
                targetmainpackage_supplytype = row['supplyType']
                targetmainpackage_state = row['outData.pp_states']
                targetmainpackage_parttype = row['dataType']
                targetmainpackage_spec = row['outData.mr_siteTechnicalSpec']
                targetmainpackage_uniquieid = row['uniqueStr']
            targetmainpackage_pn = Main_Package['childNameDisplay'].iloc[0]
            targetmainpackage_qty = Main_Package['bomQuantity'].iloc[0]
            targetmainpackage_level = Main_Package['bomLevel'].iloc[0]
            targetmainpackage_uit = Main_Package['outData.mr_userItemType'].iloc[0]
            targetmainpackage_supplytype = Main_Package['supplyType'].iloc[0]
            targetmainpackage_state = Main_Package['outData.pp_states'].iloc[0]
            targetmainpackage_parttype = Main_Package['dataType'].iloc[0]
            targetmainpackage_spec = Main_Package['outData.mr_siteTechnicalSpec'].iloc[0]
            targetmainpackage_uniquieid = Main_Package['uniqueStr'].iloc[0]
        else:
            targetmainpackage_pn = ""
            targetmainpackage_qty = ""
            targetmainpackage_level = ""
            targetmainpackage_uit = ""
            targetmainpackage_supplytype = ""
            targetmainpackage_state = ""
            targetmainpackage_parttype = ""
            targetmainpackage_spec = ""
            targetmainpackage_uniquieid = ""        
        #<Search for specific components in EBOM data (EBU Main)
        is_MRGB9M_model = any(
            "MRGB9M" in item.get("childNameDisplay", "")
            for item in response_data.get("data", [])
        )
        if is_MRGB9M_model:
            #<Search for specific components in EBOM data (EBU Main MRGB9M)
            EBU_Main = pd.json_normalize([
                    item for item in response_data.get("data", [])
                    if (
                        "EBU" in item.get("childNameDisplay", "")
                        and "BPR Total Assembly" in item.get("outData", {}).get("pp_descriptions", "")
                        and "MAIN" in item.get("outData", {}).get("mr_siteTechnicalSpec", "")
                    )
                ])
            if not EBU_Main.empty:
                for idx, row in EBU_Main.iterrows():
                    targetebumain_pn = row['childNameDisplay']
                    targetebumain_qty = row['bomQuantity']
                    targetebumain_level = row['bomLevel']
                    targetebumain_uit = row['outData.mr_userItemType']
                    targetebumain_supplytype = row['supplyType']
                    targetebumain_state = row['outData.pp_states']
                    targetebumain_parttype = row['dataType']
                targetebumain_pn = EBU_Main['childNameDisplay'].iloc[0]
                targetebumain_qty = EBU_Main['bomQuantity'].iloc[0]
                targetebumain_level = EBU_Main['bomLevel'].iloc[0]
                targetebumain_uit = EBU_Main['outData.mr_userItemType'].iloc[0]
                targetebumain_supplytype = EBU_Main['supplyType'].iloc[0]
                targetebumain_state = EBU_Main['outData.pp_states'].iloc[0]
                targetebumain_parttype = EBU_Main['dataType'].iloc[0]
                targetebumain_spec = EBU_Main['outData.mr_siteTechnicalSpec'].iloc[0]
                targetebumain_uniquieid = EBU_Main['uniqueStr'].iloc[0]
            else:
                targetebumain_pn = ""
                targetebumain_qty = ""
                targetebumain_level = ""
                targetebumain_uit = ""
                targetebumain_supplytype = ""
                targetebumain_state = ""
                targetebumain_parttype = ""
                targetebumain_spec = ""
                targetebumain_uniquieid = ""
        else:
            #<Search for specific components in EBOM data (EBU Main)     
            EBU_Main = pd.json_normalize([
                    item for item in response_data.get("data", [])
                    if (
                        item.get("uniqueStrParent") in [
                            targetebtmain_uniquieid,
                            targetebrpackage_uniquieid,
                        ]
                        and "EBU" in item.get("childNameDisplay", "")
                        and "ORP Total Assembly" in item.get("outData", {}).get("pp_descriptions", "")
                        and "MAIN" in item.get("outData", {}).get("mr_siteTechnicalSpec", "")
                    )
                ])
            if not EBU_Main.empty:
                for idx, row in EBU_Main.iterrows():
                    targetebumain_pn = row['childNameDisplay']
                    targetebumain_qty = row['bomQuantity']
                    targetebumain_level = row['bomLevel']
                    targetebumain_uit = row['outData.mr_userItemType']
                    targetebumain_supplytype = row['supplyType']
                    targetebumain_state = row['outData.pp_states']
                    targetebumain_parttype = row['dataType']
                    targetebumain_spec = row['outData.mr_siteTechnicalSpec']
                    targetebumain_uniquieid = row['uniqueStr']
                targetebumain_pn = EBU_Main['childNameDisplay'].iloc[0]
                targetebumain_qty = EBU_Main['bomQuantity'].iloc[0]
                targetebumain_level = EBU_Main['bomLevel'].iloc[0]
                targetebumain_uit = EBU_Main['outData.mr_userItemType'].iloc[0]
                targetebumain_supplytype = EBU_Main['supplyType'].iloc[0]
                targetebumain_state = EBU_Main['outData.pp_states'].iloc[0]
                targetebumain_parttype = EBU_Main['dataType'].iloc[0]
                targetebumain_spec = EBU_Main['outData.mr_siteTechnicalSpec'].iloc[0]
                targetebumain_uniquieid = EBU_Main['uniqueStr'].iloc[0]
            else:
                targetebumain_pn = ""
                targetebumain_qty = ""
                targetebumain_level = ""
                targetebumain_uit = ""
                targetebumain_supplytype = ""
                targetebumain_state = ""
                targetebumain_parttype = ""
                targetebumain_spec = ""
                targetebumain_uniquieid = ""
        #<Search for specific components in EBOM data (EBR Main)
        EBR_Main = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebumain_uniquieid and
                "EBR" in "{}".format(item.get("childNameDisplay", "")) and 
                ("ORP Insert PCB Assembly" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) or
                "BPR Insert PCB Assembly" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))) and
                ("MAIN" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not EBR_Main.empty:
            for idx, row in EBR_Main.iterrows():
                targetebrmain_pn = row['childNameDisplay']
                targetebrmain_qty = row['bomQuantity']
                targetebrmain_level = row['bomLevel']
                targetebrmain_uit = row['outData.mr_userItemType']
                targetebrmain_supplytype = row['supplyType']
                targetebrmain_state = row['outData.pp_states']
                targetebrmain_parttype = row['dataType']
                targetebrmain_spec = row['outData.mr_siteTechnicalSpec']
                targetebrmain_uniquieid = row['uniqueStr']
            targetebrmain_pn = EBR_Main['childNameDisplay'].iloc[0]
            targetebrmain_qty = EBR_Main['bomQuantity'].iloc[0]
            targetebrmain_level = EBR_Main['bomLevel'].iloc[0]
            targetebrmain_uit = EBR_Main['outData.mr_userItemType'].iloc[0]
            targetebrmain_supplytype = EBR_Main['supplyType'].iloc[0]
            targetebrmain_state = EBR_Main['outData.pp_states'].iloc[0]
            targetebrmain_parttype = EBR_Main['dataType'].iloc[0]
            targetebrmain_spec = EBR_Main['outData.mr_siteTechnicalSpec'].iloc[0]
            targetebrmain_uniquieid = EBR_Main['uniqueStr'].iloc[0]
        else:
            targetebrmain_pn = ""
            targetebrmain_qty = ""
            targetebrmain_level = ""
            targetebrmain_uit = ""
            targetebrmain_supplytype = ""
            targetebrmain_state = ""
            targetebrmain_parttype = ""
            targetebrmain_spec = ""
            targetebrmain_uniquieid = ""
        #<Search for specific components in EBOM data (PCB Main)
        PCB_Main = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                # targetebrmain_uniquieid in "{}".format(item.get("uniqueStrParent", "")) and
                "EAX" in "{}".format(item.get("childNameDisplay", "")) and 
                "PCB" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Main" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not PCB_Main.empty:
            for idx, row in PCB_Main.iterrows():
                targetpcbmain_pn = row['childNameDisplay']
                targetpcbmain_qty = row['bomQuantity']
                targetpcbmain_level = row['bomLevel']
                targetpcbmain_uit = row['outData.mr_userItemType']
                targetpcbmain_supplytype = row['supplyType']
                targetpcbmain_state = row['outData.pp_states']
                targetpcbmain_parttype = row['dataType']
                targetpcbmain_spec = row['outData.mr_siteTechnicalSpec']
                targetpcbmain_uniquieid = row['uniqueStr']
            targetpcbmain_pn = PCB_Main['childNameDisplay'].iloc[0]
            targetpcbmain_qty = PCB_Main['bomQuantity'].iloc[0]
            targetpcbmain_level = PCB_Main['bomLevel'].iloc[0]
            targetpcbmain_uit = PCB_Main['outData.mr_userItemType'].iloc[0]
            targetpcbmain_supplytype = PCB_Main['supplyType'].iloc[0]
            targetpcbmain_state = PCB_Main['outData.pp_states'].iloc[0]
            targetpcbmain_parttype = PCB_Main['dataType'].iloc[0]
            targetpcbmain_spec = PCB_Main['outData.mr_siteTechnicalSpec'].iloc[0]
            targetpcbmain_uniquieid = PCB_Main['uniqueStr'].iloc[0]
        else:
            targetpcbmain_pn = ""
            targetpcbmain_qty = ""
            targetpcbmain_level = ""
            targetpcbmain_uit = ""
            targetpcbmain_supplytype = ""
            targetpcbmain_state = ""
            targetpcbmain_parttype = ""
            targetpcbmain_spec = ""
            targetpcbmain_uniquieid = ""
        #<Search for specific components in EBOM data (Wifi Main)
        Wifi_assymain = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                (item.get("uniqueStrParent") == targetebrmain_uniquieid and
                "EAT" in "{}".format(item.get("childNameDisplay", "")) and 
                "Module,Wifi Bluetooth Module" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "LGSW" in "{}".format(item.get("outData", {}).get('mr_siteTechnicalSpec', ""))) or
                (item.get("uniqueStrParent") == targetebrmain_uniquieid and
                "EBR" in "{}".format(item.get("childNameDisplay", "")) and 
                "PCB Assembly,Sub" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                "CKD" in "{}".format(item.get("outData", {}).get('mr_siteTechnicalSpec', "")))
                ))
            ])
        if not Wifi_assymain.empty:
            for idx, row in Wifi_assymain.iterrows():
                targetwifiassymain_pn = row['childNameDisplay']
                targetwifiassymain_qty = row['bomQuantity']
                targetwifiassymain_level = row['bomLevel']
                targetwifiassymain_uit = row['outData.mr_userItemType']
                targetwifiassymain_supplytype = row['supplyType']
                targetwifiassymain_state = row['outData.pp_states']
                targetwifiassymain_parttype = row['dataType']
                targetwifiassymain_spec = row['outData.mr_siteTechnicalSpec']
                targetwifiassymain_uniquieid = row['uniqueStr']
            targetwifiassymain_pn = Wifi_assymain['childNameDisplay'].iloc[0]
            targetwifiassymain_qty = Wifi_assymain['bomQuantity'].iloc[0]
            targetwifiassymain_level = Wifi_assymain['bomLevel'].iloc[0]
            targetwifiassymain_uit = Wifi_assymain['outData.mr_userItemType'].iloc[0]
            targetwifiassymain_supplytype = Wifi_assymain['supplyType'].iloc[0]
            targetwifiassymain_state = Wifi_assymain['outData.pp_states'].iloc[0]
            targetwifiassymain_parttype = Wifi_assymain['dataType'].iloc[0]
            targetwifiassymain_spec = Wifi_assymain['outData.mr_siteTechnicalSpec'].iloc[0]
            targetwifiassymain_uniquieid = Wifi_assymain['uniqueStr'].iloc[0]
        else:
            targetwifiassymain_pn = ""
            targetwifiassymain_qty = ""
            targetwifiassymain_level = ""
            targetwifiassymain_uit = ""
            targetwifiassymain_supplytype = ""
            targetwifiassymain_state = ""
            targetwifiassymain_parttype = ""
            targetwifiassymain_spec = ""
            targetwifiassymain_uniquieid = ""    
        #<Search for specific components in EBOM data (EDID)
        EDID = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                "ECC" in "{}".format(item.get("childNameDisplay", "")) and 
                "EDID Check Sum Assembly" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("EDID" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not EDID.empty:
            for idx, row in EDID.iterrows():
                targetedid_pn = row['childNameDisplay']
                targetedid_qty = row['bomQuantity']
                targetedid_level = row['bomLevel']
                targetedid_uit = row['outData.mr_userItemType']
                targetedid_supplytype = row['supplyType']
                targetedid_state = row['outData.pp_states']
                targetedid_parttype = row['dataType']
                targetedid_spec = row['outData.mr_siteTechnicalSpec']
                targetedid_uniquieid = row['uniqueStr']
            targetedid_pn = EDID['childNameDisplay'].iloc[0]
            targetedid_qty = EDID['bomQuantity'].iloc[0]
            targetedid_level = EDID['bomLevel'].iloc[0]
            targetedid_uit = EDID['outData.mr_userItemType'].iloc[0]
            targetedid_supplytype = EDID['supplyType'].iloc[0]
            targetedid_state = EDID['outData.pp_states'].iloc[0]
            targetedid_parttype = EDID['dataType'].iloc[0]
            targetedid_spec = EDID['outData.mr_siteTechnicalSpec'].iloc[0]
            targetedid_uniquieid = EDID['uniqueStr'].iloc[0]
        else:
            targetedid_pn = ""
            targetedid_qty = ""
            targetedid_level = ""
            targetedid_uit = ""
            targetedid_supplytype = ""
            targetedid_state = ""
            targetedid_parttype = ""
            targetedid_spec = ""
            targetedid_uniquieid = ""
        #<Search for specific components in EBOM data (SW Assy)
        SW_Assy = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                "SAB" in "{}".format(item.get("childNameDisplay", "")) and 
                "S/W Package" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("eMMC" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not SW_Assy.empty:
            for idx, row in SW_Assy.iterrows():
                targetswassy_pn = row['childNameDisplay']
                targetswassy_qty = row['bomQuantity']
                targetswassy_level = row['bomLevel']
                targetswassy_uit = row['outData.mr_userItemType']
                targetswassy_supplytype = row['supplyType']
                targetswassy_state = row['outData.pp_states']
                targetswassy_parttype = row['dataType']
                targetswassy_spec = row['outData.mr_siteTechnicalSpec']
                targetswassy_uniquieid = row['uniqueStr']
            targetswassy_pn = SW_Assy['childNameDisplay'].iloc[0]
            targetswassy_qty = SW_Assy['bomQuantity'].iloc[0]
            targetswassy_level = SW_Assy['bomLevel'].iloc[0]
            targetswassy_uit = SW_Assy['outData.mr_userItemType'].iloc[0]
            targetswassy_supplytype = SW_Assy['supplyType'].iloc[0]
            targetswassy_state = SW_Assy['outData.pp_states'].iloc[0]
            targetswassy_parttype = SW_Assy['dataType'].iloc[0]
            targetswassy_spec = SW_Assy['outData.mr_siteTechnicalSpec'].iloc[0]
            targetswassy_uniquieid = SW_Assy['uniqueStr'].iloc[0]
        else:
            targetswassy_pn = ""
            targetswassy_qty = ""
            targetswassy_level = ""
            targetswassy_uit = ""
            targetswassy_supplytype = ""
            targetswassy_state = ""
            targetswassy_parttype = ""
            targetswassy_spec = ""
            targetswassy_uniquieid = ""
        #<Search for specific components in EBOM data (EBU SVC)
        EBU_SVC = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == "00001" and
                "EBU" in "{}".format(item.get("childNameDisplay", "")) and 
                "Mainboard,ORP Total Assembly,SVC" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Main" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not EBU_SVC.empty:
            for idx, row in EBU_SVC.iterrows():
                targetebusvc_pn = row['childNameDisplay']
                targetebusvc_qty = row['bomQuantity']
                targetebusvc_level = row['bomLevel']
                targetebusvc_uit = row['outData.mr_userItemType']
                targetebusvc_supplytype = row['supplyType']
                targetebusvc_state = row['outData.pp_states']
                targetebusvc_parttype = row['dataType']
                targetebusvc_spec = row['outData.mr_siteTechnicalSpec']
                targetebusvc_uniquieid = row['uniqueStr']
            targetebusvc_pn = EBU_SVC['childNameDisplay'].iloc[0]
            targetebusvc_qty = EBU_SVC['bomQuantity'].iloc[0]
            targetebusvc_level = EBU_SVC['bomLevel'].iloc[0]
            targetebusvc_uit = EBU_SVC['outData.mr_userItemType'].iloc[0]
            targetebusvc_supplytype = EBU_SVC['supplyType'].iloc[0]
            targetebusvc_state = EBU_SVC['outData.pp_states'].iloc[0]
            targetebusvc_parttype = EBU_SVC['dataType'].iloc[0]
            targetebusvc_spec = EBU_SVC['outData.mr_siteTechnicalSpec'].iloc[0]
            targetebusvc_uniquieid = EBU_SVC['uniqueStr'].iloc[0]
        else:
            targetebusvc_pn = ""
            targetebusvc_qty = ""
            targetebusvc_level = ""
            targetebusvc_uit = ""
            targetebusvc_supplytype = ""
            targetebusvc_state = ""
            targetebusvc_parttype = ""
            targetebusvc_spec = ""
            targetebusvc_uniquieid = ""
        #<Search for specific components in EBOM data (Tuner Case Cover)
        Tuner_coversvc = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebusvc_uniquieid and
                "EBZ" in "{}".format(item.get("childNameDisplay", "")) and 
                "Part" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Tuner" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Tuner_coversvc.empty:
            for idx, row in Tuner_coversvc.iterrows():
                targettunercoversvc_pn = row['childNameDisplay']
                targettunercoversvc_qty = row['bomQuantity']
                targettunercoversvc_level = row['bomLevel']
                targettunercoversvc_uit = row['outData.mr_userItemType']
                targettunercoversvc_supplytype = row['supplyType']
                targettunercoversvc_state = row['outData.pp_states']
                targettunercoversvc_parttype = row['dataType']
                targettunercoversvc_spec = row['outData.mr_siteTechnicalSpec']
                targettunercoversvc_uniquieid = row['uniqueStr']
            targettunercoversvc_pn = Tuner_coversvc['childNameDisplay'].iloc[0]
            targettunercoversvc_qty = Tuner_coversvc['bomQuantity'].iloc[0]
            targettunercoversvc_level = Tuner_coversvc['bomLevel'].iloc[0]
            targettunercoversvc_uit = Tuner_coversvc['outData.mr_userItemType'].iloc[0]
            targettunercoversvc_supplytype = Tuner_coversvc['supplyType'].iloc[0]
            targettunercoversvc_state = Tuner_coversvc['outData.pp_states'].iloc[0]
            targettunercoversvc_parttype = Tuner_coversvc['dataType'].iloc[0]
            targettunercoversvc_spec = Tuner_coversvc['outData.mr_siteTechnicalSpec'].iloc[0]
            targettunercoversvc_uniquieid = Tuner_coversvc['uniqueStr'].iloc[0]
        else:
            targettunercoversvc_pn = ""
            targettunercoversvc_qty = ""
            targettunercoversvc_level = ""
            targettunercoversvc_uit = ""
            targettunercoversvc_supplytype = ""
            targettunercoversvc_state = ""
            targettunercoversvc_parttype = ""
            targettunercoversvc_spec = ""
            targettunercoversvc_uniquieid = ""
        #<Search for specific components in EBOM data (Tuner Case Cover)
        Holder_svc = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebusvc_uniquieid and
                "MEG" in "{}".format(item.get("childNameDisplay", "")) and 
                "Holder" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Holder" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Holder_svc.empty:
            for idx, row in Holder_svc.iterrows():
                targetholdersvc_pn = row['childNameDisplay']
                targetholdersvc_qty = row['bomQuantity']
                targetholdersvc_level = row['bomLevel']
                targetholdersvc_uit = row['outData.mr_userItemType']
                targetholdersvc_supplytype = row['supplyType']
                targetholdersvc_state = row['outData.pp_states']
                targetholdersvc_parttype = row['dataType']
                targetholdersvc_spec = row['outData.mr_siteTechnicalSpec']
                targetholdersvc_uniquieid = row['uniqueStr']
            targetholdersvc_pn = Holder_svc['childNameDisplay'].iloc[0]
            targetholdersvc_qty = Holder_svc['bomQuantity'].iloc[0]
            targetholdersvc_level = Holder_svc['bomLevel'].iloc[0]
            targetholdersvc_uit = Holder_svc['outData.mr_userItemType'].iloc[0]
            targetholdersvc_supplytype = Holder_svc['supplyType'].iloc[0]
            targetholdersvc_state = Holder_svc['outData.pp_states'].iloc[0]
            targetholdersvc_parttype = Holder_svc['dataType'].iloc[0]
            targetholdersvc_spec = Holder_svc['outData.mr_siteTechnicalSpec'].iloc[0]
            targetholdersvc_uniquieid = Holder_svc['uniqueStr'].iloc[0]
        else:
            targetholdersvc_pn = ""
            targetholdersvc_qty = ""
            targetholdersvc_level = ""
            targetholdersvc_uit = ""
            targetholdersvc_supplytype = ""
            targetholdersvc_state = ""
            targetholdersvc_parttype = ""
            targetholdersvc_spec = ""
            targetholdersvc_uniquieid = ""
        #<Search for specific components in EBOM data (EBR SVC)
        EBR_SVC = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebusvc_uniquieid and
                "EBR" in "{}".format(item.get("childNameDisplay", "")) and 
                "ORP Insert PCB Assembly" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("MAIN" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not EBR_SVC.empty:
            for idx, row in EBR_SVC.iterrows():
                targetebrsvc_pn = row['childNameDisplay']
                targetebrsvc_qty = row['bomQuantity']
                targetebrsvc_level = row['bomLevel']
                targetebrsvc_uit = row['outData.mr_userItemType']
                targetebrsvc_supplytype = row['supplyType'] 
                targetebrsvc_state = row['outData.pp_states']
                targetebrsvc_parttype = row['dataType']
                targetebrsvc_spec = row['outData.mr_siteTechnicalSpec']
                targetebrsvc_uniquieid = row['uniqueStr']
            targetebrsvc_pn = EBR_SVC['childNameDisplay'].iloc[0]
            targetebrsvc_qty = EBR_SVC['bomQuantity'].iloc[0]
            targetebrsvc_level = EBR_SVC['bomLevel'].iloc[0]
            targetebrsvc_uit = EBR_SVC['outData.mr_userItemType'].iloc[0]
            targetebrsvc_supplytype = EBR_SVC['supplyType'].iloc[0]
            targetebrsvc_state = EBR_SVC['outData.pp_states'].iloc[0]
            targetebrsvc_parttype = EBR_SVC['dataType'].iloc[0]
            targetebrsvc_spec = EBR_SVC['outData.mr_siteTechnicalSpec'].iloc[0]
            targetebrsvc_uniquieid = EBR_SVC['uniqueStr'].iloc[0]
        else:
            targetebrsvc_pn = ""
            targetebrsvc_qty = ""
            targetebrsvc_level = ""
            targetebrsvc_uit = ""
            targetebrsvc_supplytype = ""
            targetebrsvc_state = ""
            targetebrsvc_parttype = ""
            targetebrsvc_spec = ""
            targetebrsvc_uniquieid = ""   
        #<Search for specific components in EBOM data (Plate Shield Assy SVC)
        Plate_Shieldsvc = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStrParent") == targetebusvc_uniquieid and
                "EBS" in "{}".format(item.get("childNameDisplay", "")) and 
                "Electric Parts Assembly,Main" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("Shield" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")) or
                "Plate" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Plate_Shieldsvc.empty:
            for idx, row in Plate_Shieldsvc.iterrows():
                targetplateshieldsvc_pn = row['childNameDisplay']
                targetplateshieldsvc_qty = row['bomQuantity']
                targetplateshieldsvc_level = row['bomLevel']
                targetplateshieldsvc_uit = row['outData.mr_userItemType']
                targetplateshieldsvc_supplytype = row['supplyType']
                targetplateshieldsvc_state = row['outData.pp_states']
                targetplateshieldsvc_parttype = row['dataType']
                targetplateshieldsvc_spec = row['outData.mr_siteTechnicalSpec']
                targetplateshieldsvc_uniquieid = row['uniqueStr']
            targetplateshieldsvc_pn = Plate_Shieldsvc['childNameDisplay'].iloc[0]
            targetplateshieldsvc_qty = Plate_Shieldsvc['bomQuantity'].iloc[0]
            targetplateshieldsvc_level = Plate_Shieldsvc['bomLevel'].iloc[0]
            targetplateshieldsvc_uit = Plate_Shieldsvc['outData.mr_userItemType'].iloc[0]
            targetplateshieldsvc_supplytype = Plate_Shieldsvc['supplyType'].iloc[0]
            targetplateshieldsvc_state = Plate_Shieldsvc['outData.pp_states'].iloc[0]
            targetplateshieldsvc_parttype = Plate_Shieldsvc['dataType'].iloc[0]
            targetplateshieldsvc_spec = Plate_Shieldsvc['outData.mr_siteTechnicalSpec'].iloc[0]
            targetplateshieldsvc_uniquieid = Plate_Shieldsvc['uniqueStr'].iloc[0]
        else:
            targetplateshieldsvc_pn = ""
            targetplateshieldsvc_qty = ""
            targetplateshieldsvc_level = ""
            targetplateshieldsvc_uit = ""
            targetplateshieldsvc_supplytype = ""
            targetplateshieldsvc_state = ""
            targetplateshieldsvc_parttype = ""
            targetplateshieldsvc_spec = ""
            targetplateshieldsvc_uniquieid = ""    
        #<Search for specific components in EBOM data (Wifi SVC)
        Wifi_assysvc = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                targetebrsvc_uniquieid in "{}".format(item.get("uniqueStrParent", "")) and
                "EAT" in "{}".format(item.get("childNameDisplay", "")) and 
                "Module,Wifi Bluetooth Module" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) or
                "LGSW" in "{}".format(item.get("outData", {}).get('mr_siteTechnicalSpec', ""))
                ))
            ])
        if not Wifi_assysvc.empty:
            for idx, row in Wifi_assysvc.iterrows():
                targetwifiassysvc_pn = row['childNameDisplay']
                targetwifiassysvc_qty = row['bomQuantity']
                targetwifiassysvc_level = row['bomLevel']
                targetwifiassysvc_uit = row['outData.mr_userItemType']
                targetwifiassysvc_supplytype = row['supplyType']
                targetwifiassysvc_state = row['outData.pp_states']
                targetwifiassysvc_parttype = row['dataType']
                targetwifiassysvc_spec = row['outData.mr_siteTechnicalSpec']
                targetwifiassysvc_uniquieid = row['uniqueStr']
            targetwifiassysvc_pn = Wifi_assysvc['childNameDisplay'].iloc[0]
            targetwifiassysvc_qty = Wifi_assysvc['bomQuantity'].iloc[0]
            targetwifiassysvc_level = Wifi_assysvc['bomLevel'].iloc[0]
            targetwifiassysvc_uit = Wifi_assysvc['outData.mr_userItemType'].iloc[0]
            targetwifiassysvc_supplytype = Wifi_assysvc['supplyType'].iloc[0]
            targetwifiassysvc_state = Wifi_assysvc['outData.pp_states'].iloc[0]
            targetwifiassysvc_parttype = Wifi_assysvc['dataType'].iloc[0]
            targetwifiassysvc_spec = Wifi_assysvc['outData.mr_siteTechnicalSpec'].iloc[0]
            targetwifiassysvc_uniquieid = Wifi_assysvc['uniqueStr'].iloc[0]
        else:
            targetwifiassysvc_pn = ""
            targetwifiassysvc_qty = ""
            targetwifiassysvc_level = ""
            targetwifiassysvc_uit = ""
            targetwifiassysvc_supplytype = ""
            targetwifiassysvc_state = ""
            targetwifiassysvc_parttype = ""
            targetwifiassysvc_spec = ""
            targetwifiassysvc_uniquieid = ""
        #<Search for specific components in EBOM data (Label)
        Label = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                (item.get("uniqueStrParent") == targetebtmain_uniquieid or
                item.get("uniqueStrParent") == targetebumain_uniquieid or
                item.get("uniqueStrParent") == targetebusvc_uniquieid) and
                "385" in "{}".format(item.get("childNameDisplay", "")) and 
                "Label" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("PRINTING BAR" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
                ))
            ])
        if not Label.empty:
            for idx, row in Label.iterrows():
                targetlabel_pn = row['childNameDisplay']
                targetlabel_qty = row['bomQuantity']
                targetlabel_level = row['bomLevel']
                targetlabel_uit = row['outData.mr_userItemType']
                targetlabel_supplytype = row['supplyType']
                targetlabel_state = row['outData.pp_states']
                targetlabel_parttype = row['dataType']
                targetlabel_spec = row['outData.mr_siteTechnicalSpec']
                targetlabel_uniquieid = row['uniqueStr']
        else:
            targetlabel_pn = ""
            targetlabel_qty = ""
            targetlabel_level = ""
            targetlabel_uit = ""
            targetlabel_supplytype = ""
            targetlabel_state = ""
            targetlabel_parttype = ""
            targetlabel_spec = ""
            targetlabel_uniquieid = ""
        #<Search for specific components in EBOM data (Ribbon)
        Ribbon = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                (item.get("uniqueStrParent") == targetebtmain_uniquieid or
                item.get("uniqueStrParent") == targetebumain_uniquieid or
                item.get("uniqueStrParent") == targetebusvc_uniquieid) and
                "481" in "{}".format(item.get("childNameDisplay", "")) and 
                "Ribbon" in "{}".format(item.get("outData", {}).get("pp_descriptions", "")) and
                ("CUTTING PAPER" in "{}".format(item.get("outData", {}).get("mr_siteTechnicalSpec", "")))
            ))
            ])
        if not Ribbon.empty:
            for idx, row in Ribbon.iterrows():
                targetribbon_pn = row['childNameDisplay']
                targetribbon_qty = row['bomQuantity']
                targetribbon_level = row['bomLevel']
                targetribbon_uit = row['outData.mr_userItemType']
                targetribbon_supplytype = row['supplyType']
                targetribbon_state = row['outData.pp_states']
                targetribbon_parttype = row['dataType']
                targetribbon_spec = row['outData.mr_siteTechnicalSpec']
                targetribbon_uniquieid = row['uniqueStr']
            targetribbon_pn = Ribbon['childNameDisplay'].iloc[0]
        else:
            targetribbon_pn = ""
            targetribbon_qty = ""
            targetribbon_level = ""
            targetribbon_uit = ""
            targetribbon_supplytype = ""
            targetribbon_state = ""
            targetribbon_parttype = ""
            targetribbon_spec = ""
            targetribbon_uniquieid = ""
        #<Search for specific components in EBOM data (Gasket)
        Gasket = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                (item.get("uniqueStrParent") == "00001" or
                item.get("uniqueStrParent") == targetebtmain_uniquieid) and
                "MDS" in "{}".format(item.get("childNameDisplay", "")) and 
                "Gasket" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))
                ))
            ])
        targets_gasket = [] # tampung semua baris
        if not Gasket.empty:
            for _, row in Gasket.head(5).iterrows():
                targets_gasket.append({
                    "pn":           row.get("childNameDisplay"),
                    "qty":          row.get("bomQuantity"),
                    "level":        row.get("bomLevel"),
                    "uit":          row.get("outData.mr_userItemType"),
                    "supplytype":   row.get("supplyType"),
                    "state":        row.get("outData.pp_states"),
                    "parttype":     row.get("dataType"),
                    "spec":         row.get("outData.mr_siteTechnicalSpec"),
                    "uniqueid":     row.get("uniqueStr"),
                })
        # contoh akses aman:
        if len(targets_gasket) >= 1:
            targetgasket1_pn = targets_gasket[0]["pn"]
            targetgasket1_qty = targets_gasket[0]["qty"]
            targetgasket1_level = targets_gasket[0]["level"]
            targetgasket1_uit = targets_gasket[0]["uit"]
            targetgasket1_supplytype = targets_gasket[0]["supplytype"]
            targetgasket1_state = targets_gasket[0]["state"]
            targetgasket1_parttype = targets_gasket[0]["parttype"]
            targetgasket1_spec = targets_gasket[0]["spec"]
            targetgasket1_uniquieid = targets_gasket[0]["uniqueid"]
        else:
            targetgasket1_pn = ""
            targetgasket1_qty = ""
            targetgasket1_level = ""
            targetgasket1_uit = ""
            targetgasket1_supplytype = ""
            targetgasket1_state = ""
            targetgasket1_parttype = ""
            targetgasket1_spec = ""
            targetgasket1_uniquieid = ""
        if len(targets_gasket) >= 2:
            targetgasket2_pn = targets_gasket[1]["pn"]
            targetgasket2_qty = targets_gasket[1]["qty"]
            targetgasket2_level = targets_gasket[1]["level"]
            targetgasket2_uit = targets_gasket[1]["uit"]
            targetgasket2_supplytype = targets_gasket[1]["supplytype"]
            targetgasket2_state = targets_gasket[1]["state"]
            targetgasket2_parttype = targets_gasket[1]["parttype"]
            targetgasket2_spec = targets_gasket[1]["spec"]
            targetgasket2_uniquieid = targets_gasket[1]["uniqueid"]
        else:   
            targetgasket2_pn = ""
            targetgasket2_qty = ""
            targetgasket2_level = ""
            targetgasket2_uit = ""
            targetgasket2_supplytype = ""
            targetgasket2_state = ""
            targetgasket2_parttype = ""
            targetgasket2_spec = ""
            targetgasket2_uniquieid = ""
        if len(targets_gasket) >= 3:
            targetgasket3_pn = targets_gasket[2]["pn"]
            targetgasket3_qty = targets_gasket[2]["qty"]
            targetgasket3_level = targets_gasket[2]["level"]
            targetgasket3_uit = targets_gasket[2]["uit"]
            targetgasket3_supplytype = targets_gasket[2]["supplytype"]
            targetgasket3_state = targets_gasket[2]["state"]
            targetgasket3_parttype = targets_gasket[2]["parttype"]
            targetgasket3_spec = targets_gasket[2]["spec"]
            targetgasket3_uniquieid = targets_gasket[2]["uniqueid"]
        else:
            targetgasket3_pn = ""
            targetgasket3_qty = ""
            targetgasket3_level = ""
            targetgasket3_uit = ""
            targetgasket3_supplytype = ""
            targetgasket3_state = ""
            targetgasket3_parttype = ""
            targetgasket3_spec = ""
            targetgasket3_uniquieid = ""
        if len(targets_gasket) >= 4:
            targetgasket4_pn = targets_gasket[3]["pn"]
            targetgasket4_qty = targets_gasket[3]["qty"]
            targetgasket4_level = targets_gasket[3]["level"]
            targetgasket4_uit = targets_gasket[3]["uit"]
            targetgasket4_supplytype = targets_gasket[3]["supplytype"]
            targetgasket4_state = targets_gasket[3]["state"]
            targetgasket4_parttype = targets_gasket[3]["parttype"]
            targetgasket4_spec = targets_gasket[3]["spec"]
            targetgasket4_uniquieid = targets_gasket[3]["uniqueid"]
        else:
            targetgasket4_pn = ""
            targetgasket4_qty = ""
            targetgasket4_level = ""
            targetgasket4_uit = ""
            targetgasket4_supplytype = ""
            targetgasket4_state = ""
            targetgasket4_parttype = ""
            targetgasket4_spec = ""
            targetgasket4_uniquieid = ""
        if len(targets_gasket) >= 5:
            targetgasket5_pn = targets_gasket[4]["pn"]
            targetgasket5_qty = targets_gasket[4]["qty"]
            targetgasket5_level = targets_gasket[4]["level"]
            targetgasket5_uit = targets_gasket[4]["uit"]
            targetgasket5_supplytype = targets_gasket[4]["supplytype"]
            targetgasket5_state = targets_gasket[4]["state"]
            targetgasket5_parttype = targets_gasket[4]["parttype"]
            targetgasket5_spec = targets_gasket[4]["spec"]
            targetgasket5_uniquieid = targets_gasket[4]["uniqueid"]
        else:
            targetgasket5_pn = ""
            targetgasket5_qty = ""
            targetgasket5_level = ""
            targetgasket5_uit = ""    
            targetgasket5_supplytype = ""
            targetgasket5_state = ""
            targetgasket5_parttype = ""
            targetgasket5_spec = ""
            targetgasket5_uniquieid = ""
        #<Search for specific components in EBOM data (Tape)
        Tape = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                (item.get("uniqueStrParent") == "00001" or
                item.get("uniqueStrParent") ==targetebtmain_uniquieid) and
                "RAB" in "{}".format(item.get("childNameDisplay", "")) and 
                "Tape" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))
                ))
            ])
        targets_tape = []  # tampung semua baris
        if not Tape.empty:
            for _, row in Gasket.head(5).iterrows():
                targets_tape.append({
                    "pn":           row.get("childNameDisplay"),
                    "qty":          row.get("bomQuantity"),
                    "level":        row.get("bomLevel"),
                    "uit":          row.get("outData.mr_userItemType"),
                    "supplytype":   row.get("supplyType"),
                    "state":        row.get("outData.pp_states"),
                    "parttype":     row.get("dataType"),
                    "spec":         row.get("outData.mr_siteTechnicalSpec"),
                    "uniqueid":     row.get("uniqueStr"),
                })
        # contoh akses aman:
        if len(targets_tape) >= 1:
            targettape1_pn = targets_tape[0]["pn"]
            targettape1_qty = targets_tape[0]["qty"]
            targettape1_level = targets_tape[0]["level"]
            targettape1_uit = targets_tape[0]["uit"]
            targettape1_supplytype = targets_tape[0]["supplytype"]
            targettape1_state = targets_tape[0]["state"]
            targettape1_parttype = targets_tape[0]["parttype"]
            targettape1_spec = targets_tape[0]["spec"]
            targettape1_uniquieid = targets_tape[0]["uniqueid"]
        else:
            targettape1_pn = ""
            targettape1_qty = ""
            targettape1_level = ""
            targettape1_uit = ""
            targettape1_supplytype = ""
            targettape1_state = ""
            targettape1_parttype = ""
            targettape1_spec = ""
            targettape1_uniquieid = ""
        if len(targets_tape) >= 2:
            targettape2_pn = targets_tape[1]["pn"]
            targettape2_qty = targets_tape[1]["qty"]
            targettape2_level = targets_tape[1]["level"]
            targettape2_uit = targets_tape[1]["uit"]
            targettape2_supplytype = targets_tape[1]["supplytype"]
            targettape2_state = targets_tape[1]["state"]
            targettape2_parttype = targets_tape[1]["parttype"]
            targettape2_spec = targets_tape[1]["spec"]
            targettape2_uniquieid = targets_tape[1]["uniqueid"]
        else:
            targettape2_pn = ""
            targettape2_qty = ""
            targettape2_level = ""
            targettape2_uit = ""
            targettape2_supplytype = ""
            targettape2_state = ""
            targettape2_parttype = ""
            targettape2_spec = ""
            targettape2_uniquieid = ""
        if len(targets_tape) >= 3:
            targettape3_pn = targets_tape[2]["pn"]
            targettape3_qty = targets_tape[2]["qty"]
            targettape3_level = targets_tape[2]["level"]
            targettape3_uit = targets_tape[2]["uit"]
            targettape3_supplytype = targets_tape[2]["supplytype"]
            targettape3_state = targets_tape[2]["state"]
            targettape3_parttype = targets_tape[2]["parttype"]
            targettape3_spec = targets_tape[2]["spec"]
            targettape3_uniquieid = targets_tape[2]["uniqueid"]
        else:
            targettape3_pn = ""
            targettape3_qty = ""
            targettape3_level = ""
            targettape3_uit = ""
            targettape3_supplytype = ""
            targettape3_state = ""
            targettape3_parttype = ""
            targettape3_spec = ""
            targettape3_uniquieid = ""
        if len(targets_tape) >= 4:
            targettape4_pn = targets_tape[3]["pn"]
            targettape4_qty = targets_tape[3]["qty"]
            targettape4_level = targets_tape[3]["level"]
            targettape4_uit = targets_tape[3]["uit"]
            targettape4_supplytype = targets_tape[3]["supplytype"]
            targettape4_state = targets_tape[3]["state"]
            targettape4_parttype = targets_tape[3]["parttype"]
            targettape4_spec = targets_tape[3]["spec"]
            targettape4_uniquieid = targets_tape[3]["uniqueid"]
        else:
            targettape4_pn = ""
            targettape4_qty = ""
            targettape4_level = ""
            targettape4_uit = ""
            targettape4_supplytype = ""
            targettape4_state = ""
            targettape4_parttype = ""
            targettape4_spec = ""
            targettape4_uniquieid = ""
        if len(targets_tape) >= 5:
            targettape5_pn = targets_tape[4]["pn"]
            targettape5_qty = targets_tape[4]["qty"]
            targettape5_level = targets_tape[4]["level"]
            targettape5_uit = targets_tape[4]["uit"]
            targettape5_supplytype = targets_tape[4]["supplytype"]
            targettape5_state = targets_tape[4]["state"]
            targettape5_parttype = targets_tape[4]["parttype"]
            targettape5_spec = targets_tape[4]["spec"]
            targettape5_uniquieid = targets_tape[4]["uniqueid"]
        else:
            targettape5_pn = ""
            targettape5_qty = ""
            targettape5_level = ""
            targettape5_uit = ""
            targettape5_supplytype = ""
            targettape5_state = ""
            targettape5_parttype = ""
            targettape5_spec = ""
            targettape5_uniquieid = ""
        #<Search for specific components in EBOM data (Damper)
        Damper = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                (item.get("uniqueStrParent") == "00001" or
                item.get("uniqueStrParent") ==targetebtmain_uniquieid) and
                "MCQ" in "{}".format(item.get("childNameDisplay", "")) and 
                "Damper" in "{}".format(item.get("outData", {}).get("pp_descriptions", ""))
                ))
            ])
        targets_damper = []  # tampung semua baris
        if not Damper.empty:
            for _, row in Gasket.head(5).iterrows():
                targets_damper.append({
                    "pn":           row.get("childNameDisplay"),
                    "qty":          row.get("bomQuantity"),
                    "level":        row.get("bomLevel"),
                    "uit":          row.get("outData.mr_userItemType"),
                    "supplytype":   row.get("supplyType"),
                    "state":        row.get("outData.pp_states"),
                    "parttype":     row.get("dataType"),
                    "spec":         row.get("outData.mr_siteTechnicalSpec"),
                    "uniqueid":     row.get("uniqueStr"),
                })
        # contoh akses aman:
        if len(targets_damper) >= 1:
            targetdamper1_pn = targets_damper[0]["pn"]
            targetdamper1_qty = targets_damper[0]["qty"]
            targetdamper1_level = targets_damper[0]["level"]
            targetdamper1_uit = targets_damper[0]["uit"]
            targetdamper1_supplytype = targets_damper[0]["supplytype"]
            targetdamper1_state = targets_damper[0]["state"]
            targetdamper1_parttype = targets_damper[0]["parttype"]
            targetdamper1_spec = targets_damper[0]["spec"]
            targetdamper1_uniquieid = targets_damper[0]["uniqueid"]
        else:
            targetdamper1_pn = ""
            targetdamper1_qty = ""
            targetdamper1_level = ""
            targetdamper1_uit = ""
            targetdamper1_supplytype = ""
            targetdamper1_state = ""
            targetdamper1_parttype = ""
            targetdamper1_spec = ""
            targetdamper1_uniquieid = ""
        if len(targets_damper) >= 2:
            targetdamper2_pn = targets_damper[1]["pn"]
            targetdamper2_qty = targets_damper[1]["qty"]
            targetdamper2_level = targets_damper[1]["level"]
            targetdamper2_uit = targets_damper[1]["uit"]
            targetdamper2_supplytype = targets_damper[1]["supplytype"]
            targetdamper2_state = targets_damper[1]["state"]
            targetdamper2_parttype = targets_damper[1]["parttype"]
            targetdamper2_spec = targets_damper[1]["spec"]
            targetdamper2_uniquieid = targets_damper[1]["uniqueid"]
        else:
            targetdamper2_pn = ""
            targetdamper2_qty = ""
            targetdamper2_level = ""
            targetdamper2_uit = ""
            targetdamper2_supplytype = ""
            targetdamper2_state = ""
            targetdamper2_parttype = ""
            targetdamper2_spec = ""
            targetdamper2_uniquieid = ""
        if len(targets_damper) >= 3:
            targetdamper3_pn = targets_damper[2]["pn"]
            targetdamper3_qty = targets_damper[2]["qty"]
            targetdamper3_level = targets_damper[2]["level"]
            targetdamper3_uit = targets_damper[2]["uit"]
            targetdamper3_supplytype = targets_damper[2]["supplytype"]
            targetdamper3_state = targets_damper[2]["state"]
            targetdamper3_parttype = targets_damper[2]["parttype"]
            targetdamper3_spec = targets_damper[2]["spec"]
            targetdamper3_uniquieid = targets_damper[2]["uniqueid"]
        else:
            targetdamper3_pn = ""
            targetdamper3_qty = ""
            targetdamper3_level = ""
            targetdamper3_uit = ""
            targetdamper3_supplytype = ""
            targetdamper3_state = ""
            targetdamper3_parttype = ""
            targetdamper3_spec = ""
            targetdamper3_uniquieid = ""
        if len(targets_damper) >= 4:
            targetdamper4_pn = targets_damper[3]["pn"]
            targetdamper4_qty = targets_damper[3]["qty"]
            targetdamper4_level = targets_damper[3]["level"]
            targetdamper4_uit = targets_damper[3]["uit"]
            targetdamper4_supplytype = targets_damper[3]["supplytype"]
            targetdamper4_state = targets_damper[3]["state"]
            targetdamper4_parttype = targets_damper[3]["parttype"]
            targetdamper4_spec = targets_damper[3]["spec"]
            targetdamper4_uniquieid = targets_damper[3]["uniqueid"]
        else:
            targetdamper4_pn = ""
            targetdamper4_qty = ""
            targetdamper4_level = ""
            targetdamper4_uit = ""
            targetdamper4_supplytype = ""
            targetdamper4_state = ""
            targetdamper4_parttype = ""
            targetdamper4_spec = ""
            targetdamper4_uniquieid = ""
        if len(targets_damper) >= 5:
            targetdamper5_pn = targets_damper[4]["pn"]
            targetdamper5_qty = targets_damper[4]["qty"]
            targetdamper5_level = targets_damper[4]["level"]
            targetdamper5_uit = targets_damper[4]["uit"]
            targetdamper5_supplytype = targets_damper[4]["supplytype"]
            targetdamper5_state = targets_damper[4]["state"]
            targetdamper5_parttype = targets_damper[4]["parttype"]
            targetdamper5_spec = targets_damper[4]["spec"]
            targetdamper5_uniquieid = targets_damper[4]["uniqueid"]
        else:
            targetdamper5_pn = ""
            targetdamper5_qty = ""
            targetdamper5_level = ""
            targetdamper5_uit = ""
            targetdamper5_supplytype = ""
            targetdamper5_state = ""
            targetdamper5_parttype = ""
            targetdamper5_spec = ""
            targetdamper5_uniquieid = ""
                
        all_hwpart = pd.concat([
            Accesory, Ferrit_core, MR_battery, MR_remote, Lcon_battery, Lcon_remote, 
            Bracket_Assy, EBT_Subassy, Wifi_assy, IR_assy, FFC_assy, Speaker_Right, 
            Speaker_Left, Speaker_assy, FFC_Main, EBT_Powercord, Powercord_attach, 
            Powercord_detach, Power_Board, EBT_Main, Holder_main, Tuner_cover, Transparent_Tape, 
            Harness_Single, Harness_Multi, Plate_Shield, Plate_Sink, Plate_Holder, Sheet_Cooper,
            EBR_Package, Main_Package, EBU_Main, EBR_Main, PCB_Main, Wifi_assymain, EDID, SW_Assy, 
            EBU_SVC, Tuner_coversvc, Holder_svc, EBR_SVC, Plate_Shieldsvc, Wifi_assysvc, 
            Label, Ribbon, Gasket, Tape, Damper
            ], ignore_index=True)
        all_hwpart.to_json("json/1_initial_hwpart.json", orient="records", indent=4)
        print("Initial Part List saved to 1_target_hwpart.json")
        data = [
            {
                "Category": "EBT Main",
                "Part No": targetebtmain_pn, 
                "Qty": targetebtmain_qty, 
                "Supply Type": targetebtmain_supplytype, 
                "UIT": targetebtmain_uit, 
                "Spec": targetebtmain_spec,
            },
            {
                "Category": "EBT Sub",
                "Part No": targetebtassy_pn, 
                "Qty": targetebtassy_qty, 
                "Supply Type": targetebtassy_supplytype, 
                "UIT": targetebtassy_uit, 
                "Spec": targetebtassy_spec,
            },
            {
                "Category": "EBU Main",
                "Part No": targetebumain_pn, 
                "Qty": targetebumain_qty, 
                "Supply Type": targetebumain_supplytype, 
                "UIT": targetebumain_uit, 
                "Spec": targetebumain_spec,
            },
            {
                "Category": "EBR Main",
                "Part No": targetebrmain_pn, 
                "Qty": targetebrmain_qty, 
                "Supply Type": targetebrmain_supplytype, 
                "UIT": targetebrmain_uit, 
                "Spec": targetebrmain_spec,
            },
            {
                "Category": "SW Assy",
                "Part No": targetswassy_pn, 
                "Qty": targetswassy_qty, 
                "Supply Type": targetswassy_supplytype, 
                "UIT": targetswassy_uit, 
                "Spec": targetswassy_spec,
            },
            {
                "Category": "EDID Check Sum Assembly",
                "Part No": targetedid_pn, 
                "Qty": targetedid_qty, 
                "Supply Type": targetedid_supplytype, 
                "UIT": targetedid_uit, 
                "Spec": targetedid_spec,
            },
            {
                "Category": "Plate Shield Assy",
                "Part No": targetplateshield_pn, 
                "Qty": targetplateshield_qty, 
                "Supply Type": targetplateshield_supplytype, 
                "UIT": targetplateshield_uit, 
                "Spec": targetplateshield_spec,
            },
            {
                "Category": "Shield Plate",
                "Part No": targetplatesink_pn, 
                "Qty": targetplatesink_qty, 
                "Supply Type": targetplatesink_supplytype, 
                "UIT": targetplatesink_uit, 
                "Spec": targetplatesink_spec,
            },
            {
                "Category": "Plate Holder",
                "Part No": targetplateholder_pn, 
                "Qty": targetplateholder_qty, 
                "Supply Type": targetplateholder_supplytype, 
                "UIT": targetplateholder_uit, 
                "Spec": targetplateholder_spec,
            },
            {
                "Category": "Sheet Cooper",
                "Part No": targetsheetcooper_pn, 
                "Qty": targetsheetcooper_qty, 
                "Supply Type": targetsheetcooper_supplytype, 
                "UIT": targetsheetcooper_uit, 
                "Spec": targetsheetcooper_spec,
            },
            {
                "Category": "SKD Main Package",
                "Part No": targetmainpackage_pn, 
                "Qty": targetmainpackage_qty, 
                "Supply Type": targetmainpackage_supplytype, 
                "UIT": targetmainpackage_uit, 
                "Spec": targetmainpackage_spec,
            },
            {
                "Category": "PCB",
                "Part No": targetpcbmain_pn, 
                "Qty": targetpcbmain_qty, 
                "Supply Type": targetpcbmain_supplytype, 
                "UIT": targetpcbmain_uit, 
                "Spec": targetpcbmain_spec,
            },
            {
                "Category": "EBU SVC",
                "Part No": targetebusvc_pn, 
                "Qty": targetebusvc_qty, 
                "Supply Type": targetebusvc_supplytype, 
                "UIT": targetebusvc_uit, 
                "Spec": targetebusvc_spec,
            },
            {
                "Category": "EBR SVC",
                "Part No": targetebrsvc_pn, 
                "Qty": targetebrsvc_qty, 
                "Supply Type": targetebrsvc_supplytype, 
                "UIT": targetebrsvc_uit, 
                "Spec": targetebrsvc_spec,
            },
            {
                "Category": "Plate Shield SVC",
                "Part No": targetplateshieldsvc_pn, 
                "Qty": targetplateshieldsvc_qty, 
                "Supply Type": targetplateshieldsvc_supplytype, 
                "UIT": targetplateshieldsvc_uit, 
                "Spec": targetplateshieldsvc_spec,
            },
            {
                "Category": "Wifi Assy SVC",
                "Part No": targetwifiassysvc_pn, 
                "Qty": targetwifiassysvc_qty, 
                "Supply Type": targetwifiassysvc_supplytype, 
                "UIT": targetwifiassysvc_uit, 
                "Spec": targetwifiassysvc_spec,
            },
            {
                "Category": "Speaker Right",
                "Part No": targetspeakerright_pn, 
                "Qty": targetspeakerright_qty, 
                "Supply Type": targetspeakerright_supplytype, 
                "UIT": targetspeakerright_uit, 
                "Spec": targetspeakerright_spec,
            },
            {
                "Category": "Speaker Left",
                "Part No": targetspeakerleft_pn, 
                "Qty": targetspeakerleft_qty, 
                "Supply Type": targetspeakerleft_supplytype, 
                "UIT": targetspeakerleft_uit, 
                "Spec": targetspeakerleft_spec,
            },
            {
                "Category": "SPK Assy",
                "Part No": targetspeaker_pn, 
                "Qty": targetspeaker_qty, 
                "Supply Type": targetspeaker_supplytype, 
                "UIT": targetspeaker_uit, 
                "Spec": targetspeaker_spec,
            },
            {
                "Category": "Power Board",
                "Part No": targetpowerboard_pn, 
                "Qty": targetpowerboard_qty, 
                "Supply Type": targetpowerboard_supplytype, 
                "UIT": targetpowerboard_uit, 
                "Spec": targetpowerboard_spec,
            },
            {
                "Category": "EBT Power Cord",
                "Part No": targetebtpowercord_pn, 
                "Qty": targetebtpowercord_qty, 
                "Supply Type": targetebtpowercord_supplytype, 
                "UIT": targetebtpowercord_uit, 
                "Spec": targetebtpowercord_spec,
            },
            {
                "Category": "Power Cord Attach",
                "Part No": targetpowercordattach_pn, 
                "Qty": targetpowercordattach_qty, 
                "Supply Type": targetpowercordattach_supplytype, 
                "UIT": targetpowercordattach_uit, 
                "Spec": targetpowercordattach_spec,
            },
            {
                "Category": "Power Cord Detach",
                "Part No": targetpowercorddetach_pn, 
                "Qty": targetpowercorddetach_qty, 
                "Supply Type": targetpowercorddetach_supplytype, 
                "UIT": targetpowercorddetach_uit, 
                "Spec": targetpowercorddetach_spec,
            },
            {
                "Category": "Cable FFC Main 1",
                "Part No": targetffcmain1_pn, 
                "Qty": targetffcmain1_qty, 
                "Supply Type": targetffcmain1_supplytype, 
                "UIT": targetffcmain1_uit, 
                "Spec": targetffcmain1_spec,
            },
            {
                "Category": "Cable FFC Main 2",
                "Part No": targetffcmain2_pn, 
                "Qty": targetffcmain2_qty, 
                "Supply Type": targetffcmain2_supplytype, 
                "UIT": targetffcmain2_uit, 
                "Spec": targetffcmain2_spec,
            },
            {
                "Category": "Cable FFC Sub Assy",
                "Part No": targetffcassy_pn, 
                "Qty": targetffcassy_qty, 
                "Supply Type": targetffcassy_supplytype, 
                "UIT": targetffcassy_uit, 
                "Spec": targetffcassy_spec,
            },
            {
                "Category": "Harness Single",
                "Part No": targetharnesssingle_pn, 
                "Qty": targetharnesssingle_qty, 
                "Supply Type": targetharnesssingle_supplytype, 
                "UIT": targetharnesssingle_uit, 
                "Spec": targetharnesssingle_spec,
            },
            {
                "Category": "Harness Multi",
                "Part No": targetharnessmulti_pn, 
                "Qty": targetharnessmulti_qty, 
                "Supply Type": targetharnessmulti_supplytype, 
                "UIT": targetharnessmulti_uit, 
                "Spec": targetharnessmulti_spec,
            },
            {
                "Category": "IR Assy",
                "Part No": targetirassy_pn, 
                "Qty": targetirassy_qty, 
                "Supply Type": targetirassy_supplytype, 
                "UIT": targetirassy_uit, 
                "Spec": targetirassy_spec,
            },
            {
                "Category": "Wifi Assy",
                "Part No": targetwifiassy_pn, 
                "Qty": targetwifiassy_qty, 
                "Supply Type": targetwifiassy_supplytype, 
                "UIT": targetwifiassy_uit, 
                "Spec": targetwifiassy_spec,
            },
            {
                "Category": "Wifi Assy Main",
                "Part No": targetwifiassymain_pn, 
                "Qty": targetwifiassymain_qty, 
                "Supply Type": targetwifiassymain_supplytype, 
                "UIT": targetwifiassymain_uit, 
                "Spec": targetwifiassymain_spec,
            },
            {
                "Category": "MR Remote",
                "Part No": targetremote_pn, 
                "Qty": targetremote_qty, 
                "Supply Type": targetremote_supplytype, 
                "UIT": targetremote_uit, 
                "Spec": targetremote_spec,
            },
            {
                "Category": "L-Con Remote",
                "Part No": targetlconremote_pn, 
                "Qty": targetlconremote_qty, 
                "Supply Type": targetlconremote_supplytype, 
                "UIT": targetlconremote_uit, 
                "Spec": targetlconremote_spec,
            },
            {
                "Category": "MR Battery",
                "Part No": targetbattery_pn, 
                "Qty": targetbattery_qty, 
                "Supply Type": targetbattery_supplytype, 
                "UIT": targetbattery_uit, 
                "Spec": targetbattery_spec,
            },
            {
                "Category": "L-Con Battery",
                "Part No": targetlconbattery_pn, 
                "Qty": targetlconbattery_qty, 
                "Supply Type": targetlconbattery_supplytype, 
                "UIT": targetlconbattery_uit, 
                "Spec": targetlconbattery_spec,
            },
            {
                "Category": "Ferrit Core",
                "Part No": targetferritcore_pn, 
                "Qty": targetferritcore_qty, 
                "Supply Type": targetferritcore_supplytype, 
                "UIT": targetferritcore_uit, 
                "Spec": targetferritcore_spec,
            },
            {
                "Category": "Tuner Cover",
                "Part No": targettunercover_pn, 
                "Qty": targettunercover_qty, 
                "Supply Type": targettunercover_supplytype, 
                "UIT": targettunercover_uit, 
                "Spec": targettunercover_spec,
            },
            {
                "Category": "Tuner Cover SVC",
                "Part No": targettunercoversvc_pn, 
                "Qty": targettunercoversvc_qty, 
                "Supply Type": targettunercoversvc_supplytype, 
                "UIT": targettunercoversvc_uit, 
                "Spec": targettunercoversvc_spec,
            },
            {
                "Category": "Holder",
                "Part No": targetholdermain_pn, 
                "Qty": targetholdermain_qty, 
                "Supply Type": targetholdermain_supplytype, 
                "UIT": targetholdermain_uit, 
                "Spec": targetholdermain_spec,
            },
            {
                "Category": "Holder SVC",
                "Part No": targetholdersvc_pn, 
                "Qty": targetholdersvc_qty, 
                "Supply Type": targetholdersvc_supplytype, 
                "UIT": targetholdersvc_uit, 
                "Spec": targetholdersvc_spec,
            },
            {
                "Category": "Tape",
                "Part No": targettape1_pn, 
                "Qty": targettape1_qty, 
                "Supply Type": targettape1_supplytype, 
                "UIT": targettape1_uit, 
                "Spec": targettape1_spec,
            },
            {
                "Category": "Tape",
                "Part No": targettape2_pn, 
                "Qty": targettape2_qty, 
                "Supply Type": targettape2_supplytype, 
                "UIT": targettape2_uit, 
                "Spec": targettape2_spec,
            },
            {
                "Category": "Tape",
                "Part No": targettape3_pn, 
                "Qty": targettape3_qty, 
                "Supply Type": targettape3_supplytype, 
                "UIT": targettape3_uit, 
                "Spec": targettape3_spec,
            },
            {
                "Category": "Tape",
                "Part No": targettape4_pn, 
                "Qty": targettape4_qty, 
                "Supply Type": targettape4_supplytype, 
                "UIT": targettape4_uit, 
                "Spec": targettape4_spec,
            },
            {
                "Category": "Tape",
                "Part No": targettape5_pn, 
                "Qty": targettape5_qty, 
                "Supply Type": targettape5_supplytype, 
                "UIT": targettape5_uit, 
                "Spec": targettape5_spec,
            },
            {
                "Category": "Gasket",
                "Part No": targetgasket1_pn, 
                "Qty": targetgasket1_qty, 
                "Supply Type": targetgasket1_supplytype, 
                "UIT": targetgasket1_uit, 
                "Spec": targetgasket1_spec,
            },
            {
                "Category": "Gasket",
                "Part No": targetgasket2_pn, 
                "Qty": targetgasket2_qty, 
                "Supply Type": targetgasket2_supplytype, 
                "UIT": targetgasket2_uit, 
                "Spec": targetgasket2_spec,
            },
            {
                "Category": "Gasket",
                "Part No": targetgasket3_pn, 
                "Qty": targetgasket3_qty, 
                "Supply Type": targetgasket3_supplytype, 
                "UIT": targetgasket3_uit, 
                "Spec": targetgasket3_spec,
            },
            {
                "Category": "Gasket",
                "Part No": targetgasket4_pn, 
                "Qty": targetgasket4_qty, 
                "Supply Type": targetgasket4_supplytype, 
                "UIT": targetgasket4_uit, 
                "Spec": targetgasket4_spec,
            },
            {
                "Category": "Gasket",
                "Part No": targetgasket5_pn, 
                "Qty": targetgasket5_qty, 
                "Supply Type": targetgasket5_supplytype, 
                "UIT": targetgasket5_uit, 
                "Spec": targetgasket5_spec,
            },
            {
                "Category": "Damper",
                "Part No": targetdamper1_pn, 
                "Qty": targetdamper1_qty, 
                "Supply Type": targetdamper1_supplytype, 
                "UIT": targetdamper1_uit, 
                "Spec": targetdamper1_spec,
            },
            {
                "Category": "Damper",
                "Part No": targetdamper2_pn, 
                "Qty": targetdamper2_qty, 
                "Supply Type": targetdamper2_supplytype, 
                "UIT": targetdamper2_uit, 
                "Spec": targetdamper2_spec,
            },
            {
                "Category": "Damper",
                "Part No": targetdamper3_pn, 
                "Qty": targetdamper3_qty, 
                "Supply Type": targetdamper3_supplytype, 
                "UIT": targetdamper3_uit, 
                "Spec": targetdamper3_spec,
            },
            {
                "Category": "Damper",
                "Part No": targetdamper4_pn, 
                "Qty": targetdamper4_qty, 
                "Supply Type": targetdamper4_supplytype, 
                "UIT": targetdamper4_uit, 
                "Spec": targetdamper4_spec,
            },
            {
                "Category": "Damper",
                "Part No": targetdamper5_pn, 
                "Qty": targetdamper5_qty, 
                "Supply Type": targetdamper5_supplytype, 
                "UIT": targetdamper5_uit, 
                "Spec": targetdamper5_spec,
            },
        ]
        with open(JSON_DIR / "2_initial_part.json", "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )
        
        part_status = [
            {
                "Category": "EBT Main",
                "Part No": targetebtmain_pn,
                "Qty": targetebtmain_qty,
                "Status": targetebtmain_state,
            },
            {
                "Category": "EBT Sub",
                "Part No": targetebtassy_pn,
                "Qty": targetebtassy_qty,
                "Status": targetebtassy_state,
            },
            {
                "Category": "EBU Main",
                "Part No": targetebumain_pn,
                "Qty": targetebumain_qty,
                "Status": targetebumain_state,
            },
            {
                "Category": "EBR Main",
                "Part No": targetebrmain_pn,
                "Qty": targetebrmain_qty,
                "Status": targetebrmain_state,
            },
            {
                "Category": "SW Assy",
                "Part No": targetswassy_pn,
                "Qty": targetswassy_qty,
                "Status": targetswassy_state,
            },
            {
                "Category": "EDID",
                "Part No": targetedid_pn,
                "Qty": targetedid_qty,
                "Status": targetedid_state,
            },
            {
                "Category": "Plateshield Assy",
                "Part No": targetplateshield_pn,
                "Qty": targetplateshield_qty,
                "Status": targetplateshield_state,
            },
            {
                "Category": "Shield Plate Assy",
                "Part No": targetplatesink_pn,
                "Qty": targetplatesink_qty,
                "Status": targetplatesink_state,
            },
            {
                "Category": "Plate Holder",
                "Part No": targetplateholder_pn,
                "Qty": targetplateholder_qty,
                "Status": targetplateholder_state,
            },
            {
                "Category": "Sheet Cooper",
                "Part No": targetsheetcooper_pn,
                "Qty": targetsheetcooper_qty,
                "Status": targetsheetcooper_state,
            },
            {
                "Category": "SKD Main Package",
                "Part No": targetmainpackage_pn,
                "Qty": targetmainpackage_qty,
                "Status": targetmainpackage_state,
            },
            {
                "Category": "PCB Main",
                "Part No": targetpcbmain_pn,
                "Qty": targetpcbmain_qty,
                "Status": targetpcbmain_state,
            },
            {
                "Category": "EBU SVC",
                "Part No": targetebusvc_pn,
                "Qty": targetebusvc_qty,
                "Status": targetebusvc_state,
            },
            {
                "Category": "EBR SVC",
                "Part No": targetebrsvc_pn,
                "Qty": targetebrsvc_qty,
                "Status": targetebrsvc_state,
            },
            {
                "Category": "Plateshield SVC",
                "Part No": targetplateshieldsvc_pn,
                "Qty": targetplateshieldsvc_qty,
                "Status": targetplateshieldsvc_state,
            },
            {
                "Category": "Wifi Assy SVC",
                "Part No": targetwifiassysvc_pn,
                "Qty": targetwifiassysvc_qty,
                "Status": targetwifiassysvc_state,
            },
            {
                "Category": "Speaker Right",
                "Part No": targetspeakerright_pn,
                "Qty": targetspeakerright_qty,
                "Status": targetspeakerright_state,
            },
            {
                "Category": "Speaker Left",
                "Part No": targetspeakerleft_pn,
                "Qty": targetspeakerleft_qty,
                "Status": targetspeakerleft_state,
            },
            {
                "Category": "Speaker Assy",
                "Part No": targetspeaker_pn,
                "Qty": targetspeaker_qty,
                "Status": targetspeaker_state,
            },
            {
                "Category": "Power Board",
                "Part No": targetpowerboard_pn,
                "Qty": targetpowerboard_qty,
                "Status": targetpowerboard_state,
            },
            {
                "Category": "EBT Power Cord",
                "Part No": targetebtpowercord_pn,
                "Qty": targetebtpowercord_qty,
                "Status": targetebtpowercord_state,
            },
            {
                "Category": "Power Cord Attach",
                "Part No": targetpowercordattach_pn,
                "Qty": targetpowercordattach_qty,
                "Status": targetpowercordattach_state,
            },
            {
                "Category": "Power Cord Detach",
                "Part No": targetpowercorddetach_pn,
                "Qty": targetpowercorddetach_qty,
                "Status": targetpowercorddetach_state,
            },
            {
                "Category": "Cable FFC Main 1",
                "Part No": targetffcmain1_pn,
                "Qty": targetffcmain1_qty,
                "Status": targetffcmain1_state,
            },
            {
                "Category": "Cable FFC Main 2",
                "Part No": targetffcmain2_pn,
                "Qty": targetffcmain2_qty,
                "Status": targetffcmain2_state,
            },
            {
                "Category": "Cable FFC Sub Assy",
                "Part No": targetffcassy_pn,
                "Qty": targetffcassy_qty,
                "Status": targetffcassy_state,
            },
            {
                "Category": "Harness Single",
                "Part No": targetharnesssingle_pn,
                "Qty": targetharnesssingle_qty,
                "Status": targetharnesssingle_state,
            },
            {
                "Category": "Harness Multi",
                "Part No": targetharnessmulti_pn,
                "Qty": targetharnessmulti_qty,
                "Status": targetharnessmulti_state,
            },
            {
                "Category": "IR Assy",
                "Part No": targetirassy_pn,
                "Qty": targetirassy_qty,
                "Status": targetirassy_state,
            },
            {
                "Category": "Wifi Assy",
                "Part No": targetwifiassy_pn,
                "Qty": targetwifiassy_qty,
                "Status": targetwifiassy_state,
            },
            {
                "Category": "Wifi Assy Main",
                "Part No": targetwifiassymain_pn,
                "Qty": targetwifiassymain_qty,
                "Status": targetwifiassymain_state,
            },
            {
                "Category": "MR Remote",
                "Part No": targetremote_pn,
                "Qty": targetremote_qty,
                "Status": targetremote_state,
            },
            {
                "Category": "LCON Remote",
                "Part No": targetlconremote_pn,
                "Qty": targetlconremote_qty,
                "Status": targetlconremote_state,
            },
            {
                "Category": "MR Battery",
                "Part No": targetbattery_pn,
                "Qty": targetbattery_qty,
                "Status": targetbattery_state,
            },
            {
                "Category": "LCON Battery",
                "Part No": targetlconbattery_pn,
                "Qty": targetlconbattery_qty,
                "Status": targetlconbattery_state,
            },
            {
                "Category": "Ferrit Core",
                "Part No": targetferritcore_pn,
                "Qty": targetferritcore_qty,
                "Status": targetferritcore_state,
            },
            {
                "Category": "Tuner Case Cover",
                "Part No": targettunercover_pn,
                "Qty": targettunercover_qty,
                "Status": targettunercover_state,
            },
            {
                "Category": "Tuner Case Cover SVC",
                "Part No": targettunercoversvc_pn,
                "Qty": targettunercoversvc_qty,
                "Status": targettunercoversvc_state,
            },
            {
                "Category": "Holder",
                "Part No": targetholdermain_pn,
                "Qty": targetholdermain_qty,
                "Status": targetholdermain_state,
            },
            {
                "Category": "Holder SVC",
                "Part No": targetholdersvc_pn,
                "Qty": targetholdersvc_qty,
                "Status": targetholdersvc_state,
            },
            {
                "Category": "Tape 1",
                "Part No": targettape1_pn,
                "Qty": targettape1_qty,
                "Status": targettape1_state,
            },
            {
                "Category": "Tape 2",
                "Part No": targettape2_pn,
                "Qty": targettape2_qty,
                "Status": targettape2_state,
            },
            {
                "Category": "Tape 3",
                "Part No": targettape3_pn,
                "Qty": targettape3_qty,
                "Status": targettape3_state,
            },
            {
                "Category": "Tape 4",
                "Part No": targettape4_pn,
                "Qty": targettape4_qty,
                "Status": targettape4_state,
            },
            {
                "Category": "Tape 5",
                "Part No": targettape5_pn,
                "Qty": targettape5_qty,
                "Status": targettape5_state,
            },
            {
                "Category": "Gasket 1",
                "Part No": targetgasket1_pn,
                "Qty": targetgasket1_qty,
                "Status": targetgasket1_state,
            },
            {
                "Category": "Gasket 2",
                "Part No": targetgasket2_pn,
                "Qty": targetgasket2_qty,
                "Status": targetgasket2_state,
            },
            {
                "Category": "Gasket 3",
                "Part No": targetgasket3_pn,
                "Qty": targetgasket3_qty,
                "Status": targetgasket3_state,
            },
            {
                "Category": "Gasket 4",
                "Part No": targetgasket4_pn,
                "Qty": targetgasket4_qty,
                "Status": targetgasket4_state,
            },
            {
                "Category": "Gasket 5",
                "Part No": targetgasket5_pn,
                "Qty": targetgasket5_qty,
                "Status": targetgasket5_state,
            },
            {
                "Category": "Damper 1",
                "Part No": targetdamper1_pn,
                "Qty": targetdamper1_qty,
                "Status": targetdamper1_state,
            },
            {
                "Category": "Damper 2",
                "Part No": targetdamper2_pn,
                "Qty": targetdamper2_qty,
                "Status": targetdamper2_state,
            },
            {
                "Category": "Damper 3",
                "Part No": targetdamper3_pn,
                "Qty": targetdamper3_qty,
                "Status": targetdamper3_state,
            },
            {
                "Category": "Damper 4",
                "Part No": targetdamper4_pn,
                "Qty": targetdamper4_qty,
                "Status": targetdamper4_state,
            },
            {
                "Category": "Damper 5",
                "Part No": targetdamper5_pn,
                "Qty": targetdamper5_qty,
                "Status": targetdamper5_state,
            }
        ]
        with open(JSON_DIR / "4_initial_statuspart.json", "w", encoding="utf-8") as f:
            json.dump(
                part_status,
                f,
                indent=4,
                ensure_ascii=False
            )
        
        return [
            targetebtmain_pn, targetebtmain_qty, targetebtmain_supplytype, targetebtmain_uit, targetebtmain_spec,
            targetebtassy_pn, targetebtassy_qty, targetebtassy_supplytype, targetebtassy_uit, targetebtassy_spec,
            targetebumain_pn, targetebumain_qty, targetebumain_supplytype, targetebumain_uit, targetebumain_spec,
            targetebrmain_pn, targetebrmain_qty, targetebrmain_supplytype, targetebrmain_uit, targetebrmain_spec,
            targetswassy_pn, targetswassy_qty, targetswassy_supplytype, targetswassy_uit, targetswassy_spec,
            targetedid_pn, targetedid_qty, targetedid_supplytype, targetedid_uit, targetedid_spec,
            targetplateshield_pn, targetplateshield_qty, targetplateshield_supplytype, targetplateshield_uit, targetplateshield_spec,
            targetplatesink_pn, targetplatesink_qty, targetplatesink_supplytype, targetplatesink_uit, targetplatesink_spec,
            targetplateholder_pn, targetplateholder_qty, targetplateholder_supplytype, targetplateholder_uit, targetplateholder_spec,
            targetsheetcooper_pn, targetsheetcooper_qty, targetsheetcooper_supplytype, targetsheetcooper_uit, targetsheetcooper_spec,
            targetmainpackage_pn, targetmainpackage_qty, targetmainpackage_supplytype, targetmainpackage_uit, targetmainpackage_spec,
            targetpcbmain_pn, targetpcbmain_qty, targetpcbmain_supplytype, targetpcbmain_uit, targetpcbmain_spec,
            targetebusvc_pn, targetebusvc_qty, targetebusvc_supplytype, targetebusvc_uit, targetebusvc_spec,
            targetebrsvc_pn, targetebrsvc_qty, targetebrsvc_supplytype, targetebrsvc_uit, targetebrsvc_spec,
            targetplateshieldsvc_pn, targetplateshieldsvc_qty, targetplateshieldsvc_supplytype, targetplateshieldsvc_uit, targetplateshieldsvc_spec,
            targetwifiassysvc_pn, targetwifiassysvc_qty, targetwifiassysvc_supplytype, targetwifiassysvc_uit, targetwifiassysvc_spec,
            targetspeakerright_pn, targetspeakerright_qty, targetspeakerright_supplytype, targetspeakerright_uit, targetspeakerright_spec,
            targetspeakerleft_pn, targetspeakerleft_qty, targetspeakerleft_supplytype, targetspeakerleft_uit, targetspeakerleft_spec,
            targetspeaker_pn, targetspeaker_qty, targetspeaker_supplytype, targetspeaker_uit, targetspeaker_spec,
            targetpowerboard_pn, targetpowerboard_qty, targetpowerboard_supplytype, targetpowerboard_uit, targetpowerboard_spec,
            targetebtpowercord_pn, targetebtpowercord_qty, targetebtpowercord_supplytype, targetebtpowercord_uit, targetebtpowercord_spec,
            targetpowercordattach_pn, targetpowercordattach_qty, targetpowercordattach_supplytype, targetpowercordattach_uit, targetpowercordattach_spec,
            targetpowercorddetach_pn, targetpowercorddetach_qty, targetpowercorddetach_supplytype, targetpowercorddetach_uit, targetpowercorddetach_spec,
            targetffcmain1_pn, targetffcmain1_qty, targetffcmain1_supplytype, targetffcmain1_uit, targetffcmain1_spec,
            targetffcmain2_pn, targetffcmain2_qty, targetffcmain2_supplytype, targetffcmain2_uit, targetffcmain2_spec,
            targetffcassy_pn, targetffcassy_qty, targetffcassy_supplytype, targetffcassy_uit, targetffcassy_spec,
            targetharnesssingle_pn, targetharnesssingle_qty, targetharnesssingle_supplytype, targetharnesssingle_uit, targetharnesssingle_spec,
            targetharnessmulti_pn, targetharnessmulti_qty, targetharnessmulti_supplytype, targetharnessmulti_uit, targetharnessmulti_spec,
            targetirassy_pn, targetirassy_qty, targetirassy_supplytype, targetirassy_uit, targetirassy_spec,
            targetwifiassy_pn, targetwifiassy_qty, targetwifiassy_supplytype, targetwifiassy_uit, targetwifiassy_spec,
            targetwifiassymain_pn, targetwifiassymain_qty, targetwifiassymain_supplytype, targetwifiassymain_uit, targetwifiassymain_spec,
            targetremote_pn, targetremote_qty, targetremote_supplytype, targetremote_uit, targetremote_spec,
            targetlconremote_pn, targetlconremote_qty, targetlconremote_supplytype, targetlconremote_uit, targetlconremote_spec,
            targetbattery_pn, targetbattery_qty, targetbattery_supplytype, targetbattery_uit, targetbattery_spec,
            targetlconbattery_pn, targetlconbattery_qty, targetlconbattery_supplytype, targetlconbattery_uit, targetlconbattery_spec,
            targetferritcore_pn, targetferritcore_qty, targetferritcore_supplytype, targetferritcore_uit, targetferritcore_spec,
            targettunercover_pn, targettunercover_qty, targettunercover_supplytype, targettunercover_uit, targettunercover_spec,
            targettunercoversvc_pn, targettunercoversvc_qty, targettunercoversvc_supplytype, targettunercoversvc_uit, targettunercoversvc_spec,
            targetholdermain_pn, targetholdermain_qty, targetholdermain_supplytype, targetholdermain_uit, targetholdermain_spec,
            targetholdersvc_pn, targetholdersvc_qty, targetholdersvc_supplytype, targetholdersvc_uit, targetholdersvc_spec,
            targettape1_pn, targettape1_qty, targettape1_supplytype, targettape1_uit, targettape1_spec,
            targettape2_pn, targettape2_qty, targettape2_supplytype, targettape2_uit, targettape2_spec,
            targettape3_pn, targettape3_qty, targettape3_supplytype, targettape3_uit, targettape3_spec,
            targettape4_pn, targettape4_qty, targettape4_supplytype, targettape4_uit, targettape4_spec,
            targettape5_pn, targettape5_qty, targettape5_supplytype, targettape5_uit, targettape5_spec,
            targetgasket1_pn, targetgasket1_qty, targetgasket1_supplytype, targetgasket1_uit, targetgasket1_spec,
            targetgasket2_pn, targetgasket2_qty, targetgasket2_supplytype, targetgasket2_uit, targetgasket2_spec,
            targetgasket3_pn, targetgasket3_qty, targetgasket3_supplytype, targetgasket3_uit, targetgasket3_spec,
            targetgasket4_pn, targetgasket4_qty, targetgasket4_supplytype, targetgasket4_uit, targetgasket4_spec,
            targetgasket5_pn, targetgasket5_qty, targetgasket5_supplytype, targetgasket5_uit, targetgasket5_spec,
            targetdamper1_pn, targetdamper1_qty, targetdamper1_supplytype, targetdamper1_uit, targetdamper1_spec,
            targetdamper2_pn, targetdamper2_qty, targetdamper2_supplytype, targetdamper2_uit, targetdamper2_spec,
            targetdamper3_pn, targetdamper3_qty, targetdamper3_supplytype, targetdamper3_uit, targetdamper3_spec,
            targetdamper4_pn, targetdamper4_qty, targetdamper4_supplytype, targetdamper4_uit, targetdamper4_spec,
            targetdamper5_pn, targetdamper5_qty, targetdamper5_supplytype, targetdamper5_uit, targetdamper5_spec
        ]
        # Save the extracted data to a JSON file
    def targetpart_compare(self):
        with open(JSON_DIR / "0_initial_ebom.json", "r", encoding="utf-8") as f:
            response_data = json.load(f)



        target_model = pd.json_normalize([
            item for item in response_data.get("data", [])
            if ((
                item.get("uniqueStr") == "00001" 
            ))
            ])
        if not target_model.empty:
                for idx, row in target_model.iterrows():
                    target_model = row['childNameDisplay']
        wb = load_workbook("excel/template_part.xlsx")
        ws = wb["BEN Compare"]

        data = self.targetpartscrapper()
        ebtmain_pn, ebtmain_qty, ebtmain_supplytype, ebtmain_uit, ebtmain_spec = data[0:5]
        ebtassy_pn, ebtassy_qty, ebtassy_supplytype, ebtassy_uit, ebtassy_spec = data[5:10]
        ebumain_pn, ebumain_qty, ebumain_supplytype, ebumain_uit, ebumain_spec = data[10:15]
        ebrmain_pn, ebrmain_qty, ebrmain_supplytype, ebrmain_uit, ebrmain_spec = data[15:20]
        swassy_pn, swassy_qty, swassy_supplytype, swassy_uit, swassy_spec = data[20:25]
        edid_pn, edid_qty, edid_supplytype, edid_uit, edid_spec = data[25:30]
        plateshield_pn, plateshield_qty, plateshield_supplytype, plateshield_uit, plateshield_spec = data[30:35]
        platesink_pn, platesink_qty, platesink_supplytype, platesink_uit, platesink_spec = data[35:40]
        plateholder_pn, plateholder_qty, plateholder_supplytype, plateholder_uit, plateholder_spec = data[40:45]
        sheetcooper_pn, sheetcooper_qty, sheetcooper_supplytype, sheetcooper_uit, sheetcooper_spec = data[45:50]
        ebrpackage_pn, ebrpackage_qty, ebrpackage_supplytype, ebrpackage_uit, ebrpackage_spec = data[50:55]
        pcbmain_pn, pcbmain_qty, pcbmain_supplytype, pcbmain_uit, pcbmain_spec = data[55:60]
        ebusvc_pn, ebusvc_qty, ebusvc_supplytype, ebusvc_uit, ebusvc_spec = data[60:65]
        ebrsvc_pn, ebrsvc_qty, ebrsvc_supplytype, ebrsvc_uit, ebrsvc_spec = data[65:70]
        plateshieldsvc_pn, plateshieldsvc_qty, plateshieldsvc_supplytype, plateshieldsvc_uit, plateshieldsvc_spec = data[70:75]
        wifiassysvc_pn, wifiassysvc_qty, wifiassysvc_supplytype, wifiassysvc_uit, wifiassysvc_spec = data[75:80]
        speakerright_pn, speakerright_qty, speakerright_supplytype, speakerright_uit, speakerright_spec = data[80:85]
        speakerleft_pn, speakerleft_qty, speakerleft_supplytype, speakerleft_uit, speakerleft_spec = data[85:90]
        speaker_pn, speaker_qty, speaker_supplytype, speaker_uit, speaker_spec = data[90:95]
        powerboard_pn, powerboard_qty, powerboard_supplytype, powerboard_uit, powerboard_spec = data[95:100]
        ebtpowercord_pn, ebtpowercord_qty, ebtpowercord_supplytype, ebtpowercord_uit, ebtpowercord_spec = data[100:105]
        powercordattach_pn, powercordattach_qty, powercordattach_supplytype, powercordattach_uit, powercordattach_spec = data[105:110]
        powercorddetach_pn, powercorddetach_qty, powercorddetach_supplytype, powercorddetach_uit, powercorddetach_spec = data[110:115]
        ffcmain1_pn, ffcmain1_qty, ffcmain1_supplytype, ffcmain1_uit, ffcmain1_spec = data[115:120]
        ffcmain2_pn, ffcmain2_qty, ffcmain2_supplytype, ffcmain2_uit, ffcmain2_spec = data[120:125]
        ffcassy_pn, ffcassy_qty, ffcassy_supplytype, ffcassy_uit, ffcassy_spec = data[125:130]
        harnesssingle_pn, harnesssingle_qty, harnesssingle_supplytype, harnesssingle_uit, harnesssingle_spec = data[130:135]
        harnessmulti_pn, harnessmulti_qty, harnessmulti_supplytype, harnessmulti_uit, harnessmulti_spec = data[135:140]
        irassy_pn, irassy_qty, irassy_supplytype, irassy_uit, irassy_spec = data[140:145]
        wifiassy_pn, wifiassy_qty, wifiassy_supplytype, wifiassy_uit, wifiassy_spec = data[145:150]
        wifimain_pn, wifimain_qty, wifimain_supplytype, wifimain_uit, wifimain_spec = data[150:155]
        remote_pn, remote_qty, remote_supplytype, remote_uit, remote_spec = data[155:160]
        lcon_pn, lcon_qty, lcon_supplytype, lcon_uit, lcon_spec = data[160:165]
        battery_pn, battery_qty, battery_supplytype, battery_uit, battery_spec = data[165:170]
        lconbattery_pn, lconbattery_qty, lconbattery_supplytype, lconbattery_uit, lconbattery_spec = data[170:175]
        ferritcore_pn, ferritcore_qty, ferritcore_supplytype, ferritcore_uit, ferritcore_spec = data[175:180]
        tunercover_pn, tunercover_qty, tunercover_supplytype, tunercover_uit, tunercover_spec = data[180:185]
        tunercoversvc_pn, tunercoversvc_qty, tunercoversvc_supplytype, tunercoversvc_uit, tunercoversvc_spec = data[185:190]
        holdermain_pn, holdermain_qty, holdermain_supplytype, holdermain_uit, holdermain_spec = data[190:195]
        holdersvc_pn, holdersvc_qty, holdersvc_supplytype, holdersvc_uit, holdersvc_spec = data[195:200]
        tape1_pn, tape1_qty, tape1_supplytype, tape1_uit, tape1_spec = data[200:205]
        tape2_pn, tape2_qty, tape2_supplytype, tape2_uit, tape2_spec = data[205:210]
        tape3_pn, tape3_qty, tape3_supplytype, tape3_uit, tape3_spec = data[210:215]
        tape4_pn, tape4_qty, tape4_supplytype, tape4_uit, tape4_spec = data[215:220]
        tape5_pn, tape5_qty, tape5_supplytype, tape5_uit, tape5_spec = data[220:225]
        gasket1_pn, gasket1_qty, gasket1_supplytype, gasket1_uit, gasket1_spec = data[225:230]
        gasket2_pn, gasket2_qty, gasket2_supplytype, gasket2_uit, gasket2_spec = data[230:235]
        gasket3_pn, gasket3_qty, gasket3_supplytype, gasket3_uit, gasket3_spec = data[235:240]
        gasket4_pn, gasket4_qty, gasket4_supplytype, gasket4_uit, gasket4_spec = data[240:245]
        gasket5_pn, gasket5_qty, gasket5_supplytype, gasket5_uit, gasket5_spec = data[245:250]
        damper1_pn, damper1_qty, damper1_supplytype, damper1_uit, damper1_spec = data[250:255]
        damper2_pn, damper2_qty, damper2_supplytype, damper2_uit, damper2_spec = data[255:260]
        damper3_pn, damper3_qty, damper3_supplytype, damper3_uit, damper3_spec = data[260:265]
        damper4_pn, damper4_qty, damper4_supplytype, damper4_uit, damper4_spec = data[265:270]
        damper5_pn, damper5_qty, damper5_supplytype, damper5_uit, damper5_spec = data[270:275]

        rows = list(range(6, 61))
        columns = list(range(4, 9))
        data_list = [
            ebtmain_pn, ebtmain_qty, ebtmain_supplytype, ebtmain_uit, ebtmain_spec,
            ebtassy_pn, ebtassy_qty, ebtassy_supplytype, ebtassy_uit, ebtassy_spec,
            ebumain_pn, ebumain_qty, ebumain_supplytype, ebumain_uit, ebumain_spec,
            ebrmain_pn, ebrmain_qty, ebrmain_supplytype, ebrmain_uit, ebrmain_spec,
            swassy_pn, swassy_qty, swassy_supplytype, swassy_uit, swassy_spec,
            edid_pn, edid_qty, edid_supplytype, edid_uit, edid_spec,
            plateshield_pn, plateshield_qty, plateshield_supplytype, plateshield_uit, plateshield_spec,
            platesink_pn, platesink_qty, platesink_supplytype, platesink_uit, platesink_spec,
            plateholder_pn, plateholder_qty, plateholder_supplytype, plateholder_uit, plateholder_spec,
            sheetcooper_pn, sheetcooper_qty, sheetcooper_supplytype, sheetcooper_uit, sheetcooper_spec,
            ebrpackage_pn, ebrpackage_qty, ebrpackage_supplytype, ebrpackage_uit, ebrpackage_spec,
            pcbmain_pn, pcbmain_qty, pcbmain_supplytype, pcbmain_uit, pcbmain_spec,
            ebusvc_pn, ebusvc_qty, ebusvc_supplytype, ebusvc_uit, ebusvc_spec,
            ebrsvc_pn, ebrsvc_qty, ebrsvc_supplytype, ebrsvc_uit, ebrsvc_spec,
            plateshieldsvc_pn, plateshieldsvc_qty, plateshieldsvc_supplytype, plateshieldsvc_uit, plateshieldsvc_spec,
            wifiassysvc_pn, wifiassysvc_qty, wifiassysvc_supplytype, wifiassysvc_uit, wifiassysvc_spec,
            speakerright_pn, speakerright_qty, speakerright_supplytype, speakerright_uit, speakerright_spec,
            speakerleft_pn, speakerleft_qty, speakerleft_supplytype, speakerleft_uit, speakerleft_spec,
            speaker_pn, speaker_qty, speaker_supplytype, speaker_uit, speaker_spec,
            powerboard_pn, powerboard_qty, powerboard_supplytype, powerboard_uit, powerboard_spec,
            ebtpowercord_pn, ebtpowercord_qty, ebtpowercord_supplytype, ebtpowercord_uit, ebtpowercord_spec,
            powercordattach_pn, powercordattach_qty, powercordattach_supplytype, powercordattach_uit, powercordattach_spec,
            powercorddetach_pn, powercorddetach_qty, powercorddetach_supplytype, powercorddetach_uit, powercorddetach_spec,
            ffcmain1_pn, ffcmain1_qty, ffcmain1_supplytype, ffcmain1_uit, ffcmain1_spec,
            ffcmain2_pn, ffcmain2_qty, ffcmain2_supplytype, ffcmain2_uit, ffcmain2_spec,
            ffcassy_pn, ffcassy_qty, ffcassy_supplytype, ffcassy_uit, ffcassy_spec,
            harnesssingle_pn, harnesssingle_qty, harnesssingle_supplytype, harnesssingle_uit, harnesssingle_spec,
            harnessmulti_pn, harnessmulti_qty, harnessmulti_supplytype, harnessmulti_uit, harnessmulti_spec,
            irassy_pn, irassy_qty, irassy_supplytype, irassy_uit, irassy_spec,
            wifiassy_pn, wifiassy_qty, wifiassy_supplytype, wifiassy_uit, wifiassy_spec,
            wifimain_pn, wifimain_qty, wifimain_supplytype, wifimain_uit, wifimain_spec,
            remote_pn, remote_qty, remote_supplytype, remote_uit, remote_spec,
            lcon_pn, lcon_qty, lcon_supplytype, lcon_uit, lcon_spec,
            battery_pn, battery_qty, battery_supplytype, battery_uit, battery_spec,
            lconbattery_pn, lconbattery_qty, lconbattery_supplytype, lconbattery_uit, lconbattery_spec,
            ferritcore_pn, ferritcore_qty, ferritcore_supplytype, ferritcore_uit, ferritcore_spec,
            tunercover_pn, tunercover_qty, tunercover_supplytype, tunercover_uit, tunercover_spec,
            tunercoversvc_pn, tunercoversvc_qty, tunercoversvc_supplytype, tunercoversvc_uit, tunercoversvc_spec,
            holdermain_pn, holdermain_qty, holdermain_supplytype, holdermain_uit, holdermain_spec,
            holdersvc_pn, holdersvc_qty, holdersvc_supplytype, holdersvc_uit, holdersvc_spec,
            tape1_pn, tape1_qty, tape1_supplytype, tape1_uit, tape1_spec,
            tape2_pn, tape2_qty, tape2_supplytype, tape2_uit, tape2_spec,
            tape3_pn, tape3_qty, tape3_supplytype, tape3_uit, tape3_spec,
            tape4_pn, tape4_qty, tape4_supplytype, tape4_uit, tape4_spec,
            tape5_pn, tape5_qty, tape5_supplytype, tape5_uit, tape5_spec,
            gasket1_pn, gasket1_qty, gasket1_supplytype, gasket1_uit, gasket1_spec,
            gasket2_pn, gasket2_qty, gasket2_supplytype, gasket2_uit, gasket2_spec,
            gasket3_pn, gasket3_qty, gasket3_supplytype, gasket3_uit, gasket3_spec,
            gasket4_pn, gasket4_qty, gasket4_supplytype, gasket4_uit, gasket4_spec,
            gasket5_pn, gasket5_qty, gasket5_supplytype, gasket5_uit, gasket5_spec,
            damper1_pn, damper1_qty, damper1_supplytype, damper1_uit, damper1_spec,
            damper2_pn, damper2_qty, damper2_supplytype, damper2_uit, damper2_spec,
            damper3_pn, damper3_qty, damper3_supplytype, damper3_uit, damper3_spec,
            damper4_pn, damper4_qty, damper4_supplytype, damper4_uit, damper4_spec,
            damper5_pn, damper5_qty, damper5_supplytype, damper5_uit, damper5_spec
        ]
        
        
        for row in ws.iter_rows(min_row=6, max_row=61, min_col=4, max_col=8):
            for cell in row:
                cell.value = None

        ws["D4"] = str(target_model.split('@')[0])

        for i, row in enumerate(rows):
            for j, column in enumerate(columns):
                ws.cell(row=row, column=column).value = data_list[i * len(columns) + j]

        #wb.save("excel/template_part.xlsx")
        print("Initial part compare completed")
        #return data

class run_allhwpart():
    def __init__(self):
        pass
    def run(self):
        target_running = targetpart_compare()
        # development_running = developmentpart_compare()
        # initial_running = initialpart_compare()
        target_running.target_run()
        # development_running.target_run()
        # initial_running.target_run()

if __name__ == "__main__":
    running_allpart = run_allhwpart()
    running_allpart.run()
    print("Task completed")