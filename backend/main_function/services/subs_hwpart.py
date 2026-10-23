import json

class run_subshwpart():
    def __init__(self):
        pass
    def run(self):
        with open("json/1_development_hwpart.json", "r", encoding="utf-8") as f:
            subs_development = json.load(f)

        with open("json/1_initial_hwpart.json", "r", encoding="utf-8") as f:
            subs_initial = json.load(f)

        with open("json/1_target_hwpart.json", "r", encoding="utf-8") as f:
            subs_target = json.load(f)

        filtered_subs_dev = [
            {
                "Part No": item.get("childNameDisplay", ""),
                "Description": item.get("outData.pp_descriptions", ""),
                "BOM Level": item.get("bomLevel", "")
            }
            for item in subs_development
            if item.get("dataType") == "S"
        ]

        filtered_subs_init = [
            {
                "Part No": item.get("childNameDisplay", ""),
                "Description": item.get("outData.pp_descriptions", ""),
                "BOM Level": item.get("bomLevel", "")
            }
            for item in subs_initial
            if item.get("dataType") == "S"
        ]

        filtered_subs_target = [
            {
                "Part No": item.get("childNameDisplay", ""),
                "Description": item.get("outData.pp_descriptions", ""),
                "BOM Level": item.get("bomLevel", "")
            }
            for item in subs_target
            if item.get("dataType") == "S"
        ]

        with open("json/5_development_subspart.json", "w", encoding="utf-8") as f:
            json.dump(filtered_subs_dev, f, ensure_ascii=False, indent=2)

        with open("json/5_initial_subspart.json", "w", encoding="utf-8") as f:
            json.dump(filtered_subs_init, f, ensure_ascii=False, indent=2)

        with open("json/5_target_subspart.json", "w", encoding="utf-8") as f:
            json.dump(filtered_subs_target, f, ensure_ascii=False, indent=2)