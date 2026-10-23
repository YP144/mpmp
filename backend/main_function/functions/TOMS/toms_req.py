import requests
import json


def get_emulator_json(year: str):
    # Changed variable name to 'url' to avoid shadowing the function name
    url = f"http://10.223.226.25:8080/WEBOS{year}/WEBOS{year}_emulator.json?1789960369051"

    emulator_header = {
        "Accept" : "application/json, text/javascript, */*; q=0.01",
        "Referer" : "http://10.223.226.25:8080/WEBOS27/WEBOS27_emulator.html"
    }

    # Pass the 'url' variable here
    emulator_response = requests.get(url, headers=emulator_header)
    
    return emulator_response.json()

def get_machine_json(year: str):
    # Changed variable name to 'url' to avoid shadowing the function name
    url = f"http://10.223.226.25:8080/WEBOS{year}/WEBOS{year}_machine.json?1789960369051"

    machine_header = {
        "Accept" : "application/json, text/javascript, */*; q=0.01",
        "Referer" : "http://10.223.226.25:8080/WEBOS27/WEBOS27_emulator.html"
    }

    # Fixed the typo here: changed 'get_emulator_json' to 'url'
    machine_response = requests.get(url, headers=machine_header)

    return machine_response.json()


class TOMS:
    def __init__(
        self, 
        model_name="WEBOS26", 
        base_url="http://10.223.226.25:8080",
        mock_emulator=None,
        mock_machine=None
    ):
        self.model_name = model_name
        self.base_url = f"{base_url}/{model_name}"
        
        # Use mock data if provided (for testing), otherwise fetch from URL
        if mock_emulator and mock_machine:
            print("Loading mock JSON data for testing...")
            self.emulator = mock_emulator
            self.machine = mock_machine
        else:
            print(f"Fetching emulator data from {self.base_url}...")
            self.emulator = requests.get(f"{self.base_url}/{model_name}_emulator.json").json()
            self.machine = requests.get(f"{self.base_url}/{model_name}_machine.json").json()
        
        self.tool_map = {x["tool_name"]: x for x in self.emulator}
        print(f"Successfully loaded {len(self.emulator)} tool groups.")
        self.selections = {}

    def _index_to_bit(self, option_item, idx):
        order = option_item.get("order")
        if not order:
            return idx
        if idx < len(order):
            return order[idx]
        return idx

    def _calculate_option(self, tool_json, selected_indexes):
        option_num = 0
        for index, selected_index in enumerate(selected_indexes):
            moved_var = sum(tool_json["division_bit"][:index])
            bit_val = self._index_to_bit(tool_json["option_list"][index], selected_index)
            option_num += int(bit_val * (2 ** moved_var))
        return option_num

    def _get_max_bit(self, bit_cnt):
        if bit_cnt == 0:
            return 0
        value = 0
        for _ in range(bit_cnt):
            value = (value << 1) | 1
        return value

    def _bit_to_index(self, option_item, bit_val):
        order = option_item.get("order")
        if not order:
            return bit_val
        for idx, value in enumerate(order):
            if value == bit_val:
                return idx
        return 0

    def decode_tool_option(self, tool_name, option_num):
        tool_json = self.tool_map.get(tool_name)
        if not tool_json:
            return []

        results = []
        for index, option in enumerate(tool_json["option_list"]):
            move_bit = sum(tool_json["division_bit"][:index])
            opt_level = (option_num >> move_bit) & self._get_max_bit(tool_json["division_bit"][index])
            selected_index = self._bit_to_index(option, opt_level)
            
            selected_value = None
            if selected_index < len(option["values"]):
                selected_value = option["values"][selected_index]

            results.append({
                "name": option["name"],
                "selected_index": selected_index,
                "selected_value": selected_value,
                "bit_value": opt_level,
            })
        return results

    def _load_defaults(self, defaults):
        tool_idx = 0
        board_idx = 0
        
        for tool in self.emulator:
            tool_name = tool["tool_name"]
            self.selections[tool_name] = {}
            
            is_board = "Board" in tool_name
            opts = defaults.get("boardOptions", []) if is_board else defaults.get("toolOptions", [])
            current_idx = board_idx if is_board else tool_idx
            
            if current_idx < len(opts):
                default_vals = opts[current_idx]
                for i, opt in enumerate(tool["option_list"]):
                    try:
                        # Safely handle both Dictionary and List structures from the JSON
                        if isinstance(default_vals, dict):
                            val_str = default_vals.get(opt["name"], default_vals.get(str(i), default_vals.get(i)))
                        else:
                            val_str = default_vals[i] if i < len(default_vals) else None
                            
                        if val_str is not None:
                            self.selections[tool_name][opt["name"]] = opt["values"].index(val_str)
                        else:
                            self.selections[tool_name][opt["name"]] = 0
                    except (ValueError, IndexError, KeyError):
                        self.selections[tool_name][opt["name"]] = 0
                        
            if is_board:
                board_idx += 1
            else:
                tool_idx += 1

    def load_machine(self, machine_name):
        machine_name = machine_name.lower()
        for group in self.machine.get("machines", []):
            if machine_name in [m.lower() for m in group.get("machines", [])]:
                defaults = group.get("defaultOptions", {})
                self._load_defaults(defaults)
                print(f"Loaded machine: {machine_name}")
                return
        raise ValueError(f"Machine '{machine_name}' not found")

    def set(self, **kwargs):
        for tool_name, options in kwargs.items():
            if tool_name not in self.tool_map:
                continue
            tool_json = self.tool_map[tool_name]
            if tool_name not in self.selections:
                self.selections[tool_name] = {}
                
            for opt_name, opt_value in options.items():
                opt_def = next((o for o in tool_json["option_list"] if o["name"] == opt_name), None)
                if opt_def and opt_value < len(opt_def["values"]):
                    self.selections[tool_name][opt_name] = opt_value

    def get_tool_value(self, tool_name):
        tool_json = self.tool_map.get(tool_name)
        if not tool_json:
            return 0
        
        selected_indexes = []
        user_selections = self.selections.get(tool_name, {})
        
        for opt in tool_json["option_list"]:
            selected_indexes.append(user_selections.get(opt["name"], 0))
            
        return self._calculate_option(tool_json, selected_indexes)

    def get_crc(self):
        CRC_ID = 0x8005
        board_value = self.get_tool_value("BoardOption")
        
        crc_array = [
            self.get_tool_value("ToolOption1"),
            self.get_tool_value("ToolOption2"),
            self.get_tool_value("ToolOption3"),
            self.get_tool_value("ToolOption4"),
            self.get_tool_value("ToolOption5"),
            self.get_tool_value("ToolOption6"),
            0, 0, 0,
            board_value & 0xFFFFFFFF,
            board_value >> 32,
        ]

        crc_sum = 0
        for value in crc_array:
            value &= 0xFFFFFFFF
            for _ in range(32):
                if ((value >> 31) ^ (crc_sum >> 15)):
                    crc_sum = ((crc_sum << 1) & 0xFFFF) ^ CRC_ID
                else:
                    crc_sum = (crc_sum << 1) & 0xFFFF
                value = (value << 1) & 0xFFFFFFFF
        return crc_sum

    def get_detailed_settings(self):
        output = {}
        for tool in self.emulator:
            tool_name = tool["tool_name"]
            value = self.get_tool_value(tool_name)
            output[tool_name] = {
                "value": value,
                "settings": self.decode_tool_option(tool_name, value)
            }
        return output

    def print_machine(self, machine_name=None):
        """
        Prints every ToolOption and BoardOption setting exactly as shown in the emulator.
        """
        if machine_name:
            self.load_machine(machine_name)

        details = self.get_detailed_settings()

        # ToolOption1 ~ ToolOption9
        for i in range(1, 10):
            tool_name = f"ToolOption{i}"

            if tool_name not in details:
                continue

            value = details[tool_name]["value"]
            print(f"\n{tool_name}: {value}")

            for row in details[tool_name]["settings"]:
                print(f"  {row['name']} = {row['selected_value']}")

        # BoardOption
        if "BoardOption" in details:
            board_value = details["BoardOption"]["value"]
            print(f"\nBoardOption: {board_value}")

            for row in details["BoardOption"]["settings"]:
                print(f"  {row['name']} = {row['selected_value']}")

        # CRC
        print(f"\nToolCRC: {self.get_crc()}")

    def get_output(self):
        """
        Exports the detailed settings and CRC as a dictionary structure.
        """
        details = self.get_detailed_settings()
        output = {}

        for tool_name, data in details.items():
            output[tool_name] = {
                "value": data["value"],
                "settings": {
                    row["name"]: row["selected_value"]
                    for row in data["settings"]
                }
            }

        output["ToolCRC"] = self.get_crc()
        return output
