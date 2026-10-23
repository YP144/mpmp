from TOMS.toms_req import get_emulator_json, get_machine_json, TOMS

emulator_json = get_emulator_json("27")
machine_json = get_machine_json("27")

# 1. Initialize the emulator using the loaded local JSON data
emu = TOMS(
    model_name="WEBOS26", 
    mock_emulator=emulator_json, 
    mock_machine=machine_json
)

# 2. Load the machine profile and print formatted console output
print("\n--- CONSOLE OUTPUT ---")
#emu.print_machine("k26")

# 4. Print the pretty JSON version
print("\n--- JSON OUTPUT (After Override) ---")
print(json.dumps(emu.get_output(), indent=4))

# 5. Decode Specific Raw Values
print("\n--- DECODING SPECIFIC RAW VALUES ---")

# Define the raw values you want to decode. 
raw_inputs = {
    "ToolOption1": 218240,                  
    "ToolOption2": 1343510,                  
    "ToolOption3": 5343361,                  
    "ToolOption4": 31455744,                  
    "ToolOption5": 2623542,                  
    "ToolOption6": 582208827,                  
    "BoardOption": int("1284000CA", 16)    # Converting hex string to integer
}

for tool_name, raw_value in raw_inputs.items():
    print(f"\n{tool_name}: {raw_value} (Hex: {hex(raw_value).upper()})")
    
    # Use the built-in decoder to get the settings for this specific number
    decoded_settings = emu.decode_tool_option(tool_name, raw_value)
    
    if not decoded_settings:
        print("  [!] No settings found or tool does not exist in emulator JSON.")
        continue
        
    # Print the decoded settings in a clean format
    for row in decoded_settings:
        print(f"  {row['name']:<30} = {row['selected_value']}")