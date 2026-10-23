import json, re
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font
from openpyxl.formatting.rule import FormulaRule
import polars as pl
from pathlib import Path
from zipfile import BadZipFile
import zlib
from openpyxl import load_workbook

"""Global variables to store the calculated values."""
"""Tool+Board Value"""
tooloption1 = None
tooloption2 = None
tooloption3 = None
tooloption4 = None
tooloption5 = None
tooloption6 = None
boardoption = None
""""""""""""""""""""
"""Tool Option 1"""
inch_code = None
tool_code= None
panel_code = None
pmic_mode = None
backlight_type = None
localdim_block = None
adjust_vcom = None
""""""""""""""""""""
"""Tool Option 2"""
audiopw_volt = None
pwm2_duty = None	
max_pwm = None
scanning_bl = None
bpl_type = None
powermode_select = None
eyesensor_gain = None
standard_backlight = None
vividsports_bl = None
""""""""""""""""""""
"""Tool Option 3"""
panelgamut_type = None
motionpro_mode = None
support_dolbyvisionhdr = None
ampchip_type = None
audiospk_watt = None
support_luminanceup = None
support_vrr = None
support_freesync = None
aisound_type = None
dolbyvison_precisiondetail = None
pwmfreq_double = None
motion_booster = None
oleddpc_type = None
support_freesyncpro = None
""""""""""""""""""""
"""Tool Option 4"""
logo_light = None
support_fancontrol = None
camera_type = None
support_wol = None
hdmiswitch_type = None
moving_speaker = None
support_irblaster = None
mirror_mode = None
screenroller_motor = None
motiondetect_sensor = None
lcdscreen_cooling = None
support_lan = None
special_edition = None
optical_jack = None
farfield_voice = None
type_cctric = None
aiart_extension = None
board_design = None
emmc_density = None
""""""""""""""""""""
"""Tool Option 5"""
videoadc_index = None
audioadc_index = None
usb_count = None
usb_1 = None
usb_2 = None
usb_3 = None
support_headphone = None
ciap_key = None
dtcpap_key = None
macap_key = None
esnap_key = None
widevineap_key = None
ciecpap_key = None
atsc30_key = None
new_erp = None
oled_cpc = None
pd_charge = None
""""""""""""""""""""
"""Tool Option 6"""
digital_eye = None
energy_star = None
adaptivedim_default = None
adaptive_dimming = None
default_backlight = None
sound_mode = None
isf_mode = None
set_id = None
support_calmansw = None
dvr_ready = None
audio_lineout = None
wifi_bt = None
wifi_assy_type = None
motion_remocon = None
audioeq_eye = None
edid_type = None
""""""""""""""""""""
"""Board Option"""
panel_type = None
panel_interface = None
panel_resolution = None
panel_maxframerate = None
panel_maxbit = None
panel_divisiontype = None
external_frc = None
ddr_size = None
country_type = None
tuner_type = None
micom_localkey = None
arrlon_control = None
irled_control = None
model_type = None
weeturnkey_version = None


BASE_DIR = Path(__file__).resolve().parents[1]
TEMPLATE_OPTION_PATH = BASE_DIR / "excel" / "template_option.xlsx"

def safe_load_workbook(path):
    try:
        return load_workbook(filename=path)
    except (BadZipFile, zlib.error) as e:
        raise RuntimeError(
            f"Excel file is corrupted or invalid: {path}. "
            "Please replace template_option.xlsx with a valid .xlsx file."
        ) from e

class target_tooloption:
    def __init__(self, json_path: str = f"./backend/main_function/json/0_target_ebom.json", verbose: bool = False, auto_run: bool = True):
        """
        json_path : path file JSON EBOM
        verbose   : True -> print detail per baris (seperti kode Anda), False -> silent
        auto_run  : True -> langsung proses saat inisialisasi; hasil ada di self.df_parsed
        """
        self.json_path = json_path
        self.verbose = verbose
        self.target_parsed = pd.DataFrame()
        self.target_jobexplanation = pd.DataFrame()
        self.last_details = {"PN": "N/A", "Spec": "N/A", "UniqueID": "N/A", "JobExplanation": "N/A"}

        if auto_run:
            self.target_parsed = self.run()
    def run(self) -> pd.DataFrame:
        global tooloption1
        global tooloption2
        global tooloption3
        global tooloption4
        global tooloption5
        global tooloption6
        global boardoption
        # ---------- Load JSON secara robust ----------
        with open(self.json_path, "r", encoding="utf-8") as f:
            tooloption_data = json.load(f)

        target_model = pd.json_normalize([
        item for item in tooloption_data.get("data", [])
        if ((
            item.get("uniqueStr") == "00001" 
           ))
        ])
        if not target_model.empty:
            for idx, row in target_model.iterrows():
                target_model = row['childNameDisplay']
        
        # Normalisasi top-level → list of dict (candidates)
        if isinstance(tooloption_data, dict):
            candidates = tooloption_data.get("data", [])
            if not isinstance(candidates, list):
                candidates = [candidates]
        elif isinstance(tooloption_data, list):
            candidates = tooloption_data
        else:
            candidates = []

        # Helper kecil untuk cast ke string aman
        def _to_text(x):
            if x is None:
                return ""
            if isinstance(x, (list, tuple, set)):
                return " ".join(map(str, x))
            return str(x)

        # ---------- Filter sesuai kriteria ----------
        filtered = []
        for item in candidates:
            if not isinstance(item, dict):
                continue
            uniqueStr = _to_text(item.get("uniqueStr", ""))
            uniqueStrParent = _to_text(item.get("uniqueStrParent", ""))
            childNameDisplay = _to_text(item.get("childNameDisplay", ""))

            outData = item.get("outData", {})
            if isinstance(outData, list):
                outData = outData[0] if outData else {}

            pp_descriptions = _to_text(outData.get("pp_descriptions", ""))
            mr_siteTechnicalSpec = _to_text(outData.get("mr_siteTechnicalSpec", ""))

            cond = (
                uniqueStrParent == "00001" and
                ("EBT" in childNameDisplay) and
                ("Chassis Assembly" in pp_descriptions) and
                ("MAIN" in mr_siteTechnicalSpec)
            )
            if cond:
                filtered.append(item)

        target_jobexplanation = pd.json_normalize(filtered)
        self.target_jobexplanation = target_jobexplanation

        # ---------- Jika tidak ada data ----------
        if target_jobexplanation.empty:
            if self.verbose:
                print("❌ Target Job Explanation not found in EBOM data.")
            self.last_details = {
                "PN": "N/A", "Spec": "N/A", "UniqueID": "N/A", "JobExplanation": "N/A"
            }
            return pd.DataFrame()

        # ---------- Helper regex kecil (inline) ----------
        get_match = lambda text, pattern, group=1, flags=0, default=None: (
            (m.group(group).strip() if (m := re.search(pattern, text, flags)) else default)
            if isinstance(text, str) else default
        )

        # ---------- Parsing per baris ----------
        records = []

        for idx, df_row in target_jobexplanation.iterrows():
            # Ambil metadata sumber (aman terhadap missing key)
            try:
                targetebtmain_pn = df_row["childNameDisplay"]
            except Exception:
                targetebtmain_pn = None

            try:
                targetebtmain_spec = df_row["outData.mr_siteTechnicalSpec"]
            except Exception:
                targetebtmain_spec = None

            try:
                targetebtmain_jobexplanation = df_row["jobExplanation"]
            except Exception:
                targetebtmain_jobexplanation = ""

            try:
                targetebtmain_uniquieid = df_row["uniqueStr"]
            except Exception:
                targetebtmain_uniquieid = None

            text = str(targetebtmain_jobexplanation) if targetebtmain_jobexplanation is not None else ""

            if self.verbose:
                print(text)

            out = {}

            # Field utama (aman)
            out["Job Explanation"] = get_match(text, r"Job Explanation:\s*\[(.*?)\]")
            out["Board Option"]    = get_match(text, r"Board Option:([^/]+)")
            bt_crc   = get_match(text, r"Board\+ToolCRC:([^/]+)")
            area_str = get_match(text, r"Area Code:([^/]+)")
            out["Country Group"]   = get_match(text, r"Country Group:([^/]+)")
            out["Country"]   = get_match(text, r"Country:([^/]+)")

            # Konversi numerik aman
            if bt_crc is not None and str(bt_crc).strip().isdigit():
                out["Board+ToolCRC"] = int(str(bt_crc).strip())
            else:
                out["Board+ToolCRC"] = bt_crc

            if area_str is not None and str(area_str).strip().isdigit():
                out["Area Code"] = int(str(area_str).strip())
            else:
                out["Area Code"] = area_str

            # Tool Option -> kolom terpisah (toleran spasi/pemisah)
            tool_inner = get_match(text, r"Tool Option\(([^)]+)\)")
            if tool_inner:
                # Split default pakai koma; jika ada pemisah lain, ganti dengan regex split: r"[;,]\s*"
                for pair in re.split(r"[,\s]+", tool_inner.strip()):
                    if ":" in pair:
                        k, v = pair.split(":", 1)
                        k = k.strip()
                        v = v.strip()
                        col = f"Tool Option {k}"
                        out[col] = int(v) if v.isdigit() else v

            # Flags Yes/No → boolean
            for token in text.split("/"):
                token = token.strip()
                m = re.search(r"^(.*?)\s*\[(Yes|No)\]\s*$", token, flags=re.IGNORECASE)
                if m:
                    key = m.group(1).strip()
                    val = m.group(2).strip().lower() == "yes"
                    out[key] = "Yes" if val else "No"

            # Tambahkan metadata sumber
            out["childNameDisplay"]     = targetebtmain_pn
            out["mr_siteTechnicalSpec"] = targetebtmain_spec
            out["uniqueStr"]            = targetebtmain_uniquieid
            out["_row_index"]           = idx

            # Simpan untuk info last detail (opsional)
            self.last_details = {
                "PN": targetebtmain_pn,
                "Spec": targetebtmain_spec,
                "UniqueID": targetebtmain_uniquieid,
                "JobExplanation": targetebtmain_jobexplanation
            }
            records.append(out)
            # Output seperti kode Anda (dikendalikan verbose)
            if self.verbose:
                df_one = pd.DataFrame([out])
                print(df_one.columns.tolist())
                print(df_one.head(1).T)
                print("success")
            
        df_parsed = pd.DataFrame(records)

        target_boardoption = df_parsed.iloc[0]['Board Option']
        target_toolopt1 = df_parsed.iloc[0]['Tool Option 1']
        target_toolopt2 = df_parsed.iloc[0]['Tool Option 2']
        target_toolopt3 = df_parsed.iloc[0]['Tool Option 3']
        target_toolopt4 = df_parsed.iloc[0]['Tool Option 4']
        target_toolopt5 = df_parsed.iloc[0]['Tool Option 5']
        target_toolopt6 = df_parsed.iloc[0]['Tool Option 6']

        tooloption1 = int(target_toolopt1)
        tooloption2 = int(target_toolopt2)
        tooloption3 = int(target_toolopt3)
        tooloption4 = int(target_toolopt4)
        tooloption5 = int(target_toolopt5)
        tooloption6 = int(target_toolopt6)
        boardoption = int(target_boardoption,16)

        calc_toolopt1 = calculate_tooloption1()
        calc_toolopt2 = calculate_tooloption2()
        calc_toolopt3 = calculate_tooloption3()
        calc_toolopt4 = calculate_tooloption4()
        calc_toolopt5 = calculate_tooloption5()
        calc_toolopt6 = calculate_tooloption6()
        calc_boardopt = calculate_boardoption()

        self.result_tooloption1 = calc_toolopt1.toolopt1_run()
        self.result_tooloption2 = calc_toolopt2.toolopt2_run()
        self.result_tooloption3 = calc_toolopt3.toolopt3_run()
        self.result_tooloption4 = calc_toolopt4.toolopt4_run()
        self.result_tooloption5 = calc_toolopt5.toolopt5_run()
        self.result_tooloption6 = calc_toolopt6.toolopt6_run()
        self.result_boardoption = calc_boardopt.boardoption_run()
        key_records = []
        key_records.append([
            {
                "Inch Code": inch_code,
                "Tool": tool_code,
                "Panel Code": panel_code,
                "Pmic set Mode": pmic_mode,
                "Backlight Type": backlight_type,
                "Local Dim Block": localdim_block,
                "Adjust LCD VCOM": adjust_vcom
            },
            {
                "Audio Power Volt": audiopw_volt,
                "PWM2 Duty": pwm2_duty,
                "Max PWM": max_pwm,
                "Scanning B/L": scanning_bl,
                "BPL Current Type": bpl_type,
                "Power Mode Select": powermode_select,
                "Eye Sensor LED Gain Control": eyesensor_gain,
                "Standard Backlight": standard_backlight,
                "Vivid Sports Backlight": vividsports_bl
            },
            {
                "Panel Gamut Type": panelgamut_type,
                "Motion Pro Mode": motionpro_mode,
                "Support Dolby Vision HDR": support_dolbyvisionhdr,
                "Audio Amp": ampchip_type,
                "Speaker Watt": audiospk_watt,
                "Luminance Up": support_luminanceup,
                "Support VRR": support_vrr,
                "Support Freesync": support_freesync,
                "AI Sound": aisound_type,
                "Dolby Vison Precision Detail": dolbyvison_precisiondetail,
                "PWM Freq. double": pwmfreq_double,
                "Motion Booster": motion_booster,
                "OLED DPC Type": oleddpc_type,
                "Support Freesync Pro": support_freesyncpro
            },
            {
                "Logo Light": logo_light,
                "Fan Control": support_fancontrol,
                "Camera Ready": camera_type,
                "WOL": support_wol,
                "HDMI Switch IC": hdmiswitch_type,
                "Moving Speaker": moving_speaker,
                "Support IR Blaster": support_irblaster,
                "Mirror Mode": mirror_mode,
                "Screen Roller Motor": screenroller_motor,
                "Motion Detect Sensor": motiondetect_sensor,
                "LCD Screen Cooling": lcdscreen_cooling,
                "LAN Support": support_lan,
                "Special Edition": special_edition,
                "Support Optical Jack": optical_jack,
                "Support Far Field Voice": farfield_voice,
                "Type-C controller IC": type_cctric,
                "AI Art Extension": aiart_extension,
                "Board Design": board_design,
                "EMMC Density": emmc_density
            },
            {
                "Video ADC Index": videoadc_index,
                "Audio ADC Index": audioadc_index,
                "USB Count": usb_count,
                "USB 1": usb_1,
                "USB 2": usb_2,
                "USB 3": usb_3,
                "Headphone": support_headphone,
                "CI_AP Key": ciap_key,
                "DTCP_AP Key": dtcpap_key,
                "MAC_AP Key": macap_key,
                "ESN_AP Key": esnap_key,
                "Widevine_AP Key": widevineap_key,
                "CI_ECP_AP Key": ciecpap_key,
                "ATSC 3.0 (KR) Key": atsc30_key,
                "New ErP": new_erp,
                "OLED CPC": oled_cpc,
                "PD Charge": pd_charge
            },
            {
                "Digital Eye": digital_eye,
                "Energy Star": energy_star,
                "AdaptiveDim Default": adaptivedim_default,
                "Adaptive Dimming": adaptive_dimming,
                "Default Backlight": default_backlight,
                "Sound Mode": sound_mode,
                "ISF": isf_mode,
                "Set ID": set_id,
                "Support Calman SW": support_calmansw,
                "DVR Ready": dvr_ready,
                "Audio Line Out": audio_lineout,
                "WIFI/BT": wifi_bt,
                "WIFI assy type": wifi_assy_type,
                "Motion Remocon": motion_remocon,
                "AudioEQ Eye": audioeq_eye,
                "EDID Type": edid_type
            },
            {
                "Panel Type": panel_type,
                "Panel Interface": panel_interface,
                "Panel Resolution": panel_resolution,
                "Panel Max Frame Rate": panel_maxframerate,
                "Panel Max Bit": panel_maxbit,
                "Panel Division Type": panel_divisiontype,
                "External Frc Type": external_frc,
                "DDR Size": ddr_size,
                "Country Type": country_type,
                "Tuner Type": tuner_type,
                "Micom LocalKey Type": micom_localkey,
                "AR RL on Control": arrlon_control,
                "IR LED Control": irled_control,
                "Model Type": model_type,
                "Wee Turnkey Version": weeturnkey_version
            }
        ])
        key_df_parsed = pd.DataFrame(key_records)

        key_value = [
            {
                "Inch Code": inch_code,
                "Tool": tool_code,
                "Panel Code": panel_code,
                "Pmic set Mode": pmic_mode,
                "Backlight Type": backlight_type,
                "Local Dim Block": localdim_block,
                "Adjust LCD VCOM": adjust_vcom
            },
            {
                "Audio Power Volt": audiopw_volt,
                "PWM2 Duty": pwm2_duty,
                "Max PWM": max_pwm,
                "Scanning B/L": scanning_bl,
                "BPL Current Type": bpl_type,
                "Power Mode Select": powermode_select,
                "Eye Sensor LED Gain Control": eyesensor_gain,
                "Standard Backlight": standard_backlight,
                "Vivid Sports Backlight": vividsports_bl
            },
            {
                "Panel Gamut Type": panelgamut_type,
                "Motion Pro Mode": motionpro_mode,
                "Support Dolby Vision HDR": support_dolbyvisionhdr,
                "Audio Amp": ampchip_type,
                "Speaker Watt": audiospk_watt,
                "Luminance Up": support_luminanceup,
                "Support VRR": support_vrr,
                "Support Freesync": support_freesync,
                "AI Sound": aisound_type,
                "Dolby Vison Precision Detail": dolbyvison_precisiondetail,
                "PWM Freq. double": pwmfreq_double,
                "Motion Booster": motion_booster,
                "OLED DPC Type": oleddpc_type,
                "Support Freesync Pro": support_freesyncpro
            },
            {
                "Logo Light": logo_light,
                "Fan Control": support_fancontrol,
                "Camera Ready": camera_type,
                "WOL": support_wol,
                "HDMI Switch IC": hdmiswitch_type,
                "Moving Speaker": moving_speaker,
                "Support IR Blaster": support_irblaster,
                "Mirror Mode": mirror_mode,
                "Screen Roller Motor": screenroller_motor,
                "Motion Detect Sensor": motiondetect_sensor,
                "LCD Screen Cooling": lcdscreen_cooling,
                "LAN Support": support_lan,
                "Special Edition": special_edition,
                "Support Optical Jack": optical_jack,
                "Support Far Field Voice": farfield_voice,
                "Type-C controller IC": type_cctric,
                "AI Art Extension": aiart_extension,
                "Board Design": board_design,
                "EMMC Density": emmc_density
            },
            {
                "Video ADC Index": videoadc_index,
                "Audio ADC Index": audioadc_index,
                "USB Count": usb_count,
                "USB 1": usb_1,
                "USB 2": usb_2,
                "USB 3": usb_3,
                "Headphone": support_headphone,
                "CI_AP Key": ciap_key,
                "DTCP_AP Key": dtcpap_key,
                "MAC_AP Key": macap_key,
                "ESN_AP Key": esnap_key,
                "Widevine_AP Key": widevineap_key,
                "CI_ECP_AP Key": ciecpap_key,
                "ATSC 3.0 (KR) Key": atsc30_key,
                "New ErP": new_erp,
                "OLED CPC": oled_cpc,
                "PD Charge": pd_charge
            },
            {
                "Digital Eye": digital_eye,
                "Energy Star": energy_star,
                "AdaptiveDim Default": adaptivedim_default,
                "Adaptive Dimming": adaptive_dimming,
                "Default Backlight": default_backlight,
                "Sound Mode": sound_mode,
                "ISF": isf_mode,
                "Set ID": set_id,
                "Support Calman SW": support_calmansw,
                "DVR Ready": dvr_ready,
                "Audio Line Out": audio_lineout,
                "WIFI/BT": wifi_bt,
                "WIFI assy type": wifi_assy_type,
                "Motion Remocon": motion_remocon,
                "AudioEQ Eye": audioeq_eye,
                "EDID Type": edid_type
            },
            {
                "Panel Type": panel_type,
                "Panel Interface": panel_interface,
                "Panel Resolution": panel_resolution,
                "Panel Max Frame Rate": panel_maxframerate,
                "Panel Max Bit": panel_maxbit,
                "Panel Division Type": panel_divisiontype,
                "External Frc Type": external_frc,
                "DDR Size": ddr_size,
                "Country Type": country_type,
                "Tuner Type": tuner_type,
                "Micom LocalKey Type": micom_localkey,
                "AR RL on Control": arrlon_control,
                "IR LED Control": irled_control,
                "Model Type": model_type,
                "Wee Turnkey Version": weeturnkey_version
            }
        ]
        
        key_value_df = pd.DataFrame(key_value)
        data = [
        {
            "Tool Option 1": str(df_parsed.iloc[0]['Tool Option 1']),
            "Tool Option 2": str(df_parsed.iloc[0]['Tool Option 2']),
            "Tool Option 3": str(df_parsed.iloc[0]['Tool Option 3']),
            "Tool Option 4": str(df_parsed.iloc[0]['Tool Option 4']),
            "Tool Option 5": str(df_parsed.iloc[0]['Tool Option 5']),
            "Tool Option 6": str(df_parsed.iloc[0]['Tool Option 6']),
            "Board Option": str(df_parsed.iloc[0]['Board Option']),
            "Board+ToolCRC": str(df_parsed.iloc[0]['Board+ToolCRC']),
            "Area Code": str(df_parsed.iloc[0]['Area Code']),
            "Country Group": str(df_parsed.iloc[0]['Country Group']),
            "Country": str(df_parsed.iloc[0]['Country']),
            "Model Write": str(df_parsed.iloc[0]['Model Write']),
            "CI+": str(df_parsed.iloc[0]['CI+']),
            # "MAC": str(df_parsed.iloc[0]['MAC']),
            "ESN": str(df_parsed.iloc[0]['ESN']),
            "Widevine": str(df_parsed.iloc[0]['Widevine']),
            "Built Wifi": str(df_parsed.iloc[0]['Built Wifi']),
            "DVBS": str(df_parsed.iloc[0]['DVBS']),
            "DVBS2": str(df_parsed.iloc[0]['DVBS2']),
            "Marlin": str(df_parsed.iloc[0]['Marlin']),
            "HDCP 2.0 Rx": str(df_parsed.iloc[0]['HDCP 2.0 Rx']),
            "HDCP 2.0 Tx": str(df_parsed.iloc[0]['HDCP 2.0 Tx']),
            "DTCP Rx": str(df_parsed.iloc[0]['DTCP Rx']),
            "Japan LNB": str(df_parsed.iloc[0]['Japan LNB']),
            "HDCP 1.4 Rx": str(df_parsed.iloc[0]['HDCP 1.4 Rx']),
            "V-com": str(df_parsed.iloc[0]['V-com']),
            "MFi": str(df_parsed.iloc[0]['MFi']),
            "ATSC3.0": str(df_parsed.iloc[0]['ATSC3.0']),
            "OLED Panel ID": str(df_parsed.iloc[0]['OLED Panel ID']),
            "CI+ECP": str(df_parsed.iloc[0]['CI+ECP']),
            "QUBYX": str(df_parsed.iloc[0]['QUBYX']),
            "Inch Code": str(key_value_df.iloc[0]['Inch Code']),
            "Tool": str(key_value_df.iloc[0]['Tool']),
            "Panel Code": str(key_value_df.iloc[0]['Panel Code']),
            "Pmic set Mode": str(key_value_df.iloc[0]['Pmic set Mode']),
            "Backlight Type": str(key_value_df.iloc[0]['Backlight Type']),
            "Local Dim Block": str(key_value_df.iloc[0]['Local Dim Block']),
            "Adjust LCD VCOM": str(key_value_df.iloc[0]['Adjust LCD VCOM']),
            "Audio Power Volt": str(key_value_df.iloc[1]['Audio Power Volt']),
            "PWM2 Duty": str(key_value_df.iloc[1]['PWM2 Duty']),
            "Max PWM": str(key_value_df.iloc[1]['Max PWM']),
            "Scanning B/L": str(key_value_df.iloc[1]['Scanning B/L']),
            "BPL Current Type": str(key_value_df.iloc[1]['BPL Current Type']),
            "Power Mode Select": str(key_value_df.iloc[1]['Power Mode Select']),
            "Eye Sensor LED Gain Control": str(key_value_df.iloc[1]['Eye Sensor LED Gain Control']),
            "Standard Backlight": str(key_value_df.iloc[1]['Standard Backlight']),
            "Vivid Sports Backlight": str(key_value_df.iloc[1]['Vivid Sports Backlight']),
            "Panel Gamut Type": str(key_value_df.iloc[2]['Panel Gamut Type']),
            "Motion Pro Mode": str(key_value_df.iloc[2]['Motion Pro Mode']),
            "Support Dolby Vision HDR": str(key_value_df.iloc[2]['Support Dolby Vision HDR']),
            "Audio Amp": str(key_value_df.iloc[2]['Audio Amp']),
            "Speaker Watt.": str(key_value_df.iloc[2]['Speaker Watt']),
            "Luminance Up": str(key_value_df.iloc[2]['Luminance Up']),
            "Support VRR": str(key_value_df.iloc[2]['Support VRR']),
            "Support Freesync": str(key_value_df.iloc[2]['Support Freesync']),
            "AI Sound": str(key_value_df.iloc[2]['AI Sound']),
            "Dolby Vison Precision Detail": str(key_value_df.iloc[2]['Dolby Vison Precision Detail']),
            "PWM Freq. double": str(key_value_df.iloc[2]['PWM Freq. double']),
            "Motion Booster": str(key_value_df.iloc[2]['Motion Booster']),
            "OLED DPC Type": str(key_value_df.iloc[2]['OLED DPC Type']),
            "Support Freesync Pro": str(key_value_df.iloc[2]['Support Freesync Pro']),
            "Logo Light": str(key_value_df.iloc[3]['Logo Light']),
            "Fan Control": str(key_value_df.iloc[3]['Fan Control']),
            "Camera Ready": str(key_value_df.iloc[3]['Camera Ready']),
            "WOL": str(key_value_df.iloc[3]['WOL']),
            "HDMI Switch IC": str(key_value_df.iloc[3]['HDMI Switch IC']),
            "Moving Speaker": str(key_value_df.iloc[3]['Moving Speaker']),
            "Support IR Blaster": str(key_value_df.iloc[3]['Support IR Blaster']),
            "Mirror Mode": str(key_value_df.iloc[3]['Mirror Mode']),
            "Screen Roller Motor": str(key_value_df.iloc[3]['Screen Roller Motor']),
            "Motion Detect Sensor": str(key_value_df.iloc[3]['Motion Detect Sensor']),
            "LCD Screen Cooling": str(key_value_df.iloc[3]['LCD Screen Cooling']),
            "LAN Support": str(key_value_df.iloc[3]['LAN Support']),
            "Special Edition": str(key_value_df.iloc[3]['Special Edition']),
            "Support Optical Jack": str(key_value_df.iloc[3]['Support Optical Jack']),
            "Support Far Field Voice": str(key_value_df.iloc[3]['Support Far Field Voice']),
            "Type-C controller IC": str(key_value_df.iloc[3]['Type-C controller IC']),
            "AI Art Extension": str(key_value_df.iloc[3]['AI Art Extension']),
            "Board Design": str(key_value_df.iloc[3]['Board Design']),
            "EMMC Density": str(key_value_df.iloc[3]['EMMC Density']),
            "Video ADC Index": str(key_value_df.iloc[4]['Video ADC Index']),
            "Audio ADC Index": str(key_value_df.iloc[4]['Audio ADC Index']),
            "USB Count": str(key_value_df.iloc[4]['USB Count']),
            "USB 1": str(key_value_df.iloc[4]['USB 1']),
            "USB 2": str(key_value_df.iloc[4]['USB 2']),
            "USB 3": str(key_value_df.iloc[4]['USB 3']),
            "Headphone": str(key_value_df.iloc[4]['Headphone']),
            "CI_AP Key": str(key_value_df.iloc[4]['CI_AP Key']),
            "DTCP_AP Key": str(key_value_df.iloc[4]['DTCP_AP Key']),
            "MAC_AP Key": str(key_value_df.iloc[4]['MAC_AP Key']),
            "ESN_AP Key": str(key_value_df.iloc[4]['ESN_AP Key']),
            "Widevine_AP Key": str(key_value_df.iloc[4]['Widevine_AP Key']),
            "CI_ECP_AP Key": str(key_value_df.iloc[4]['CI_ECP_AP Key']),
            "ATSC 3.0 (KR) Key": str(key_value_df.iloc[4]['ATSC 3.0 (KR) Key']),
            "New ErP": str(key_value_df.iloc[4]['New ErP']),
            "OLED CPC": str(key_value_df.iloc[4]['OLED CPC']),
            "PD Charge": str(key_value_df.iloc[4]['PD Charge']),
            "Digital Eye": str(key_value_df.iloc[5]['Digital Eye']),
            "Energy Star": str(key_value_df.iloc[5]['Energy Star']),
            "AdaptiveDim Default": str(key_value_df.iloc[5]['AdaptiveDim Default']),
            "Adaptive Dimming": str(key_value_df.iloc[5]['Adaptive Dimming']),
            "Default Backlight": str(key_value_df.iloc[5]['Default Backlight']),
            "Sound Mode": str(key_value_df.iloc[5]['Sound Mode']),
            "ISF": str(key_value_df.iloc[5]['ISF']),
            "Set ID": str(key_value_df.iloc[5]['Set ID']),
            "Support Calman SW": str(key_value_df.iloc[5]['Support Calman SW']),
            "DVR Ready": str(key_value_df.iloc[5]['DVR Ready']),
            "Audio Line Out": str(key_value_df.iloc[5]['Audio Line Out']),
            "WIFI/BT": str(key_value_df.iloc[5]['WIFI/BT']),
            "WIFI assy type": str(key_value_df.iloc[5]['WIFI assy type']),
            "Motion Remocon": str(key_value_df.iloc[5]['Motion Remocon']),
            "AudioEQ Eye": str(key_value_df.iloc[5]['AudioEQ Eye']),
            "EDID Type": str(key_value_df.iloc[5]['EDID Type']),
            "Panel Type": str(key_value_df.iloc[6]['Panel Type']),
            "Panel Interface": str(key_value_df.iloc[6]['Panel Interface']),
            "Panel Resolution": str(key_value_df.iloc[6]['Panel Resolution']),
            "Panel Max Frame Rate": str(key_value_df.iloc[6]['Panel Max Frame Rate']),
            "Panel Max Bit": str(key_value_df.iloc[6]['Panel Max Bit']),
            "Panel Division Type": str(key_value_df.iloc[6]['Panel Division Type']),
            "External Frc Type": str(key_value_df.iloc[6]['External Frc Type']),
            "DDR Size": str(key_value_df.iloc[6]['DDR Size']),
            "Country Type": str(key_value_df.iloc[6]['Country Type']),
            "Tuner Type": str(key_value_df.iloc[6]['Tuner Type']),
            "Micom LocalKey Type": str(key_value_df.iloc[6]['Micom LocalKey Type']),
            "AR RL on Control": str(key_value_df.iloc[6]['AR RL on Control']),
            "IR LED Control": str(key_value_df.iloc[6]['IR LED Control']),
            "Model Type": str(key_value_df.iloc[6]['Model Type']),
            "Wee Turnkey Version": str(key_value_df.iloc[6]['Wee Turnkey Version']),
            }
        ]

        with open("json/3_target_tooloption.json", "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

        #wb = load_workbook(filename="excel/template_option.xlsx")
        wb = safe_load_workbook(TEMPLATE_OPTION_PATH)
        ws = wb["BEN Compare"]
        
        for row in ws.iter_rows(min_row=4, max_row=132, min_col=6, max_col=6):
            for cell in row:
                cell.value = ""

        ws["F4"] = str(target_model.split('@')[0])
        key_val = df_parsed.iloc[0]  # Series baris pertama
        key_col = [
            'Tool Option 1','Tool Option 2','Tool Option 3','Tool Option 4','Tool Option 5','Tool Option 6',
            'Board Option','Board+ToolCRC','Area Code','Country Group','Country','Model Write','CI+','MAC','ESN',
            'Widevine','Built Wifi','DVBS','DVBS2','Marlin','HDCP 2.0 Rx','HDCP 2.0 Tx','DTCP Rx','Japan LNB',
            'HDCP 1.4 Rx','V-com','MFi','ATSC3.0','OLED Panel ID','CI+ECP','QUBYX'
            ]

        key_start_row = 5  # D41
        key_col_idx = 6     # D = kolom ke-4

        for i, col_name in enumerate(key_col):
            row = key_start_row + i
            value = key_val.get(col_name, "")  # aman bila kolom tidak ada
            ws.cell(row=row, column=key_col_idx, value=value if value is not None else "")
        
        key_option = key_df_parsed.iloc[0]
        tool_option1 = key_option[0]
        tool_option2 = key_option[1]
        tool_option3 = key_option[2]
        tool_option4 = key_option[3]
        tool_option5 = key_option[4]
        tool_option6 = key_option[5]
        board_option = key_option[6]

        fields_0 = [
            'Inch Code',
            'Tool',
            'Panel Code',
            'Pmic set Mode',
            'Backlight Type',
            'Local Dim Block',
            'Adjust LCD VCOM',
        ]

        fields_1 = [
            'Audio Power Volt',
            'PWM2 Duty',
            'Max PWM',
            'Scanning B/L',
            'BPL Current Type',
            'Power Mode Select',
            'Eye Sensor LED Gain Control',
            'Standard Backlight',
            'Vivid Sports Backlight',
        ]

        fields_2 = [
            "Panel Gamut Type",
            "Motion Pro Mode",
            "Support Dolby Vision HDR",
            "Audio Amp",
            "Speaker Watt",
            "Luminance Up",
            "Support VRR",
            "Support Freesync",
            "AI Sound",
            "Dolby Vison Precision Detail",
            "PWM Freq. double",
            "Motion Booster",
            "OLED DPC Type",
            "Support Freesync Pro"
        ]

        fields_3 = [
            "Logo Light",
            "Fan Control",
            "Camera Ready",
            "WOL",
            "HDMI Switch IC",
            "Moving Speaker",
            "Support IR Blaster",
            "Mirror Mode",
            "Screen Roller Motor",
            "Motion Detect Sensor",
            "LCD Screen Cooling",
            "LAN Support",
            "Special Edition",
            "Support Optical Jack",
            "Support Far Field Voice",
            "Type-C controller IC",
            "AI Art Extension",
            "Board Design",
            "EMMC Density"
        ]

        fields_4 = [
            "Video ADC Index",
            "Audio ADC Index",
            "USB Count",
            "USB 1",
            "USB 2",
            "USB 3",
            "Headphone",
            "CI_AP Key",
            "DTCP_AP Key",
            "MAC_AP Key",
            "ESN_AP Key",
            "Widevine_AP Key",
            "CI_ECP_AP Key",
            "ATSC 3.0 (KR) Key",
            "New ErP",
            "OLED CPC",
            "PD Charge"
        ]

        fields_5 = [
            "Digital Eye",
            "Energy Star",
            "AdaptiveDim Default",
            "Adaptive Dimming",
            "Default Backlight",
            "Sound Mode",
            "ISF",
            "Set ID",
            "Support Calman SW",
            "DVR Ready",
            "Audio Line Out",
            "WIFI/BT",         
            "WIFI assy type",
            "Motion Remocon",
            "AudioEQ Eye",
            "EDID Type"
        ]

        fields_6 = [
            "Panel Type",
            "Panel Interface",
            "Panel Resolution",
            "Panel Max Frame Rate",
            "Panel Max Bit",
            "Panel Division Type",
            "External Frc Type",
            "DDR Size",
            "Country Type",
            "Tuner Type",
            "Micom LocalKey Type",
            "AR RL on Control",
            "IR LED Control",
            "Model Type",
            "Wee Turnkey Version"
        ]

        option_start_row = 36
        option_col_idx = 6
        r = option_start_row

        for key in fields_0:
            ws.cell(row=r, column=option_col_idx, value=tool_option1[key])
            r += 1
        for key in fields_1:
            ws.cell(row=r, column=option_col_idx, value=tool_option2[key])
            r += 1
        for key in fields_2:
            ws.cell(row=r, column=option_col_idx, value=tool_option3[key])
            r += 1
        for key in fields_3:
            ws.cell(row=r, column=option_col_idx, value=tool_option4[key])
            r += 1
        for key in fields_4:
            ws.cell(row=r, column=option_col_idx, value=tool_option5[key])
            r += 1
        for key in fields_5:
            ws.cell(row=r, column=option_col_idx, value=tool_option6[key])
            r += 1
        for key in fields_6:
            ws.cell(row=r, column=option_col_idx, value=board_option[key])
            r += 1
      
        #wb.save("excel/template_option.xlsx")
        wb.save(TEMPLATE_OPTION_PATH)

class development_tooloption:
    def __init__(self, json_path: str = "json/0_development_ebom.json", verbose: bool = False, auto_run: bool = True):
        """
        json_path : path file JSON EBOM
        verbose   : True -> print detail per baris (seperti kode Anda), False -> silent
        auto_run  : True -> langsung proses saat inisialisasi; hasil ada di self.df_parsed
        """
        self.json_path = json_path
        self.verbose = verbose
        self.development_parsed = pd.DataFrame()
        self.development_jobexplanation = pd.DataFrame()
        self.last_details = {"PN": "N/A", "Spec": "N/A", "UniqueID": "N/A", "JobExplanation": "N/A"}

        if auto_run:
            self.development_parsed = self.run()
    def run(self) -> pd.DataFrame:
        global tooloption1
        global tooloption2
        global tooloption3
        global tooloption4
        global tooloption5
        global tooloption6
        global boardoption
        # ---------- Load JSON secara robust ----------
        with open(self.json_path, "r", encoding="utf-8") as f:
            tooloption_data = json.load(f)
        
        development_model = pd.json_normalize([
        item for item in tooloption_data.get("data", [])
        if ((
            item.get("uniqueStr") == "00001" 
           ))
        ])
        if not development_model.empty:
            for idx, row in development_model.iterrows():
                development_model = row['childNameDisplay']

        # Normalisasi top-level → list of dict (candidates)
        if isinstance(tooloption_data, dict):
            candidates = tooloption_data.get("data", [])
            if not isinstance(candidates, list):
                candidates = [candidates]
        elif isinstance(tooloption_data, list):
            candidates = tooloption_data
        else:
            candidates = []

        # Helper kecil untuk cast ke string aman
        def _to_text(x):
            if x is None:
                return ""
            if isinstance(x, (list, tuple, set)):
                return " ".join(map(str, x))
            return str(x)

        # ---------- Filter sesuai kriteria ----------
        filtered = []
        for item in candidates:
            if not isinstance(item, dict):
                continue

            uniqueStrParent = _to_text(item.get("uniqueStrParent", ""))
            childNameDisplay = _to_text(item.get("childNameDisplay", ""))

            outData = item.get("outData", {})
            if isinstance(outData, list):
                outData = outData[0] if outData else {}

            pp_descriptions = _to_text(outData.get("pp_descriptions", ""))
            mr_siteTechnicalSpec = _to_text(outData.get("mr_siteTechnicalSpec", ""))

            cond = (
                uniqueStrParent == "00001" and
                ("EBT" in childNameDisplay) and
                ("Chassis Assembly" in pp_descriptions) and
                ("MAIN" in mr_siteTechnicalSpec)
            )
            if cond:
                filtered.append(item)

        target_jobexplanation = pd.json_normalize(filtered)
        self.development_jobexplanation = target_jobexplanation

        # ---------- Jika tidak ada data ----------
        if target_jobexplanation.empty:
            if self.verbose:
                print("❌ Target Job Explanation not found in EBOM data.")
            self.last_details = {
                "PN": "N/A", "Spec": "N/A", "UniqueID": "N/A", "JobExplanation": "N/A"
            }
            return pd.DataFrame()

        # ---------- Helper regex kecil (inline) ----------
        get_match = lambda text, pattern, group=1, flags=0, default=None: (
            (m.group(group).strip() if (m := re.search(pattern, text, flags)) else default)
            if isinstance(text, str) else default
        )

        # ---------- Parsing per baris ----------
        records = []

        for idx, df_row in target_jobexplanation.iterrows():
            # Ambil metadata sumber (aman terhadap missing key)
            try:
                targetebtmain_pn = df_row["childNameDisplay"]
            except Exception:
                targetebtmain_pn = None

            try:
                targetebtmain_spec = df_row["outData.mr_siteTechnicalSpec"]
            except Exception:
                targetebtmain_spec = None

            try:
                targetebtmain_jobexplanation = df_row["jobExplanation"]
            except Exception:
                targetebtmain_jobexplanation = ""

            try:
                targetebtmain_uniquieid = df_row["uniqueStr"]
            except Exception:
                targetebtmain_uniquieid = None

            text = str(targetebtmain_jobexplanation) if targetebtmain_jobexplanation is not None else ""

            if self.verbose:
                print(text)

            out = {}

            # Field utama (aman)
            out["Job Explanation"] = get_match(text, r"Job Explanation:\s*\[(.*?)\]")
            out["Board Option"]    = get_match(text, r"Board Option:([^/]+)")
            bt_crc   = get_match(text, r"Board\+ToolCRC:([^/]+)")
            area_str = get_match(text, r"Area Code:([^/]+)")
            out["Country Group"]   = get_match(text, r"Country Group:([^/]+)")
            out["Country"]   = get_match(text, r"Country:([^/]+)")

            # Konversi numerik aman
            if bt_crc is not None and str(bt_crc).strip().isdigit():
                out["Board+ToolCRC"] = int(str(bt_crc).strip())
            else:
                out["Board+ToolCRC"] = bt_crc

            if area_str is not None and str(area_str).strip().isdigit():
                out["Area Code"] = int(str(area_str).strip())
            else:
                out["Area Code"] = area_str

            # Tool Option -> kolom terpisah (toleran spasi/pemisah)
            tool_inner = get_match(text, r"Tool Option\(([^)]+)\)")
            if tool_inner:
                # Split default pakai koma; jika ada pemisah lain, ganti dengan regex split: r"[;,]\s*"
                for pair in re.split(r"[,\s]+", tool_inner.strip()):
                    if ":" in pair:
                        k, v = pair.split(":", 1)
                        k = k.strip()
                        v = v.strip()
                        col = f"Tool Option {k}"
                        out[col] = int(v) if v.isdigit() else v

            # Flags Yes/No → boolean
            for token in text.split("/"):
                token = token.strip()
                m = re.search(r"^(.*?)\s*\[(Yes|No)\]\s*$", token, flags=re.IGNORECASE)
                if m:
                    key = m.group(1).strip()
                    val = m.group(2).strip().lower() == "yes"
                    out[key] = "Yes" if val else "No"

            # Tambahkan metadata sumber
            out["childNameDisplay"]     = targetebtmain_pn
            out["mr_siteTechnicalSpec"] = targetebtmain_spec
            out["uniqueStr"]            = targetebtmain_uniquieid
            out["_row_index"]           = idx

            # Simpan untuk info last detail (opsional)
            self.last_details = {
                "PN": targetebtmain_pn,
                "Spec": targetebtmain_spec,
                "UniqueID": targetebtmain_uniquieid,
                "JobExplanation": targetebtmain_jobexplanation
            }
            records.append(out)
            # Output seperti kode Anda (dikendalikan verbose)
            if self.verbose:
                df_one = pd.DataFrame([out])
                print(df_one.columns.tolist())
                print(df_one.head(1).T)
                print("success")

        df_parsed = pd.DataFrame(records)

        target_boardoption = df_parsed.iloc[0]['Board Option']
        target_toolopt1 = df_parsed.iloc[0]['Tool Option 1']
        target_toolopt2 = df_parsed.iloc[0]['Tool Option 2']
        target_toolopt3 = df_parsed.iloc[0]['Tool Option 3']
        target_toolopt4 = df_parsed.iloc[0]['Tool Option 4']
        target_toolopt5 = df_parsed.iloc[0]['Tool Option 5']
        target_toolopt6 = df_parsed.iloc[0]['Tool Option 6']

        tooloption1 = int(target_toolopt1)
        tooloption2 = int(target_toolopt2)
        tooloption3 = int(target_toolopt3)
        tooloption4 = int(target_toolopt4)
        tooloption5 = int(target_toolopt5)
        tooloption6 = int(target_toolopt6)
        boardoption = int(target_boardoption,16)

        calc_toolopt1 = calculate_tooloption1()
        calc_toolopt2 = calculate_tooloption2()
        calc_toolopt3 = calculate_tooloption3()
        calc_toolopt4 = calculate_tooloption4()
        calc_toolopt5 = calculate_tooloption5()
        calc_toolopt6 = calculate_tooloption6()
        calc_boardopt = calculate_boardoption()

        self.result_tooloption1 = calc_toolopt1.toolopt1_run()
        self.result_tooloption2 = calc_toolopt2.toolopt2_run()
        self.result_tooloption3 = calc_toolopt3.toolopt3_run()
        self.result_tooloption4 = calc_toolopt4.toolopt4_run()
        self.result_tooloption5 = calc_toolopt5.toolopt5_run()
        self.result_tooloption6 = calc_toolopt6.toolopt6_run()
        self.result_boardoption = calc_boardopt.boardoption_run()
        key_records = []
        key_records.append([
            {
                "Inch Code": inch_code,
                "Tool": tool_code,
                "Panel Code": panel_code,
                "Pmic set Mode": pmic_mode,
                "Backlight Type": backlight_type,
                "Local Dim Block": localdim_block,
                "Adjust LCD VCOM": adjust_vcom
            },
            {
                "Audio Power Volt": audiopw_volt,
                "PWM2 Duty": pwm2_duty,
                "Max PWM": max_pwm,
                "Scanning B/L": scanning_bl,
                "BPL Current Type": bpl_type,
                "Power Mode Select": powermode_select,
                "Eye Sensor LED Gain Control": eyesensor_gain,
                "Standard Backlight": standard_backlight,
                "Vivid Sports Backlight": vividsports_bl
            },
            {
                "Panel Gamut Type": panelgamut_type,
                "Motion Pro Mode": motionpro_mode,
                "Support Dolby Vision HDR": support_dolbyvisionhdr,
                "Audio Amp": ampchip_type,
                "Speaker Watt": audiospk_watt,
                "Luminance Up": support_luminanceup,
                "Support VRR": support_vrr,
                "Support Freesync": support_freesync,
                "AI Sound": aisound_type,
                "Dolby Vison Precision Detail": dolbyvison_precisiondetail,
                "PWM Freq. double": pwmfreq_double,
                "Motion Booster": motion_booster,
                "OLED DPC Type": oleddpc_type,
                "Support Freesync Pro": support_freesyncpro
            },
            {
                "Logo Light": logo_light,
                "Fan Control": support_fancontrol,
                "Camera Ready": camera_type,
                "WOL": support_wol,
                "HDMI Switch IC": hdmiswitch_type,
                "Moving Speaker": moving_speaker,
                "Support IR Blaster": support_irblaster,
                "Mirror Mode": mirror_mode,
                "Screen Roller Motor": screenroller_motor,
                "Motion Detect Sensor": motiondetect_sensor,
                "LCD Screen Cooling": lcdscreen_cooling,
                "LAN Support": support_lan,
                "Special Edition": special_edition,
                "Support Optical Jack": optical_jack,
                "Support Far Field Voice": farfield_voice,
                "Type-C controller IC": type_cctric,
                "AI Art Extension": aiart_extension,
                "Board Design": board_design,
                "EMMC Density": emmc_density
            },
            {
                "Video ADC Index": videoadc_index,
                "Audio ADC Index": audioadc_index,
                "USB Count": usb_count,
                "USB 1": usb_1,
                "USB 2": usb_2,
                "USB 3": usb_3,
                "Headphone": support_headphone,
                "CI_AP Key": ciap_key,
                "DTCP_AP Key": dtcpap_key,
                "MAC_AP Key": macap_key,
                "ESN_AP Key": esnap_key,
                "Widevine_AP Key": widevineap_key,
                "CI_ECP_AP Key": ciecpap_key,
                "ATSC 3.0 (KR) Key": atsc30_key,
                "New ErP": new_erp,
                "OLED CPC": oled_cpc,
                "PD Charge": pd_charge
            },
            {
                "Digital Eye": digital_eye,
                "Energy Star": energy_star,
                "AdaptiveDim Default": adaptivedim_default,
                "Adaptive Dimming": adaptive_dimming,
                "Default Backlight": default_backlight,
                "Sound Mode": sound_mode,
                "ISF": isf_mode,
                "Set ID": set_id,
                "Support Calman SW": support_calmansw,
                "DVR Ready": dvr_ready,
                "Audio Line Out": audio_lineout,
                "WIFI/BT": wifi_bt,
                "WIFI assy type": wifi_assy_type,
                "Motion Remocon": motion_remocon,
                "AudioEQ Eye": audioeq_eye,
                "EDID Type": edid_type
            },
            {
                "Panel Type": panel_type,
                "Panel Interface": panel_interface,
                "Panel Resolution": panel_resolution,
                "Panel Max Frame Rate": panel_maxframerate,
                "Panel Max Bit": panel_maxbit,
                "Panel Division Type": panel_divisiontype,
                "External Frc Type": external_frc,
                "DDR Size": ddr_size,
                "Country Type": country_type,
                "Tuner Type": tuner_type,
                "Micom LocalKey Type": micom_localkey,
                "AR RL on Control": arrlon_control,
                "IR LED Control": irled_control,
                "Model Type": model_type,
                "Wee Turnkey Version": weeturnkey_version
            }
        ])
        key_df_parsed = pd.DataFrame(key_records)

        data = {
            "Tool Option Value": df_parsed.to_dict(orient="records"),
            "Tool Option Key": key_df_parsed.to_dict(orient="records")
        }

        key_value = [
            {
                "Inch Code": inch_code,
                "Tool": tool_code,
                "Panel Code": panel_code,
                "Pmic set Mode": pmic_mode,
                "Backlight Type": backlight_type,
                "Local Dim Block": localdim_block,
                "Adjust LCD VCOM": adjust_vcom
            },
            {
                "Audio Power Volt": audiopw_volt,
                "PWM2 Duty": pwm2_duty,
                "Max PWM": max_pwm,
                "Scanning B/L": scanning_bl,
                "BPL Current Type": bpl_type,
                "Power Mode Select": powermode_select,
                "Eye Sensor LED Gain Control": eyesensor_gain,
                "Standard Backlight": standard_backlight,
                "Vivid Sports Backlight": vividsports_bl
            },
            {
                "Panel Gamut Type": panelgamut_type,
                "Motion Pro Mode": motionpro_mode,
                "Support Dolby Vision HDR": support_dolbyvisionhdr,
                "Audio Amp": ampchip_type,
                "Speaker Watt": audiospk_watt,
                "Luminance Up": support_luminanceup,
                "Support VRR": support_vrr,
                "Support Freesync": support_freesync,
                "AI Sound": aisound_type,
                "Dolby Vison Precision Detail": dolbyvison_precisiondetail,
                "PWM Freq. double": pwmfreq_double,
                "Motion Booster": motion_booster,
                "OLED DPC Type": oleddpc_type,
                "Support Freesync Pro": support_freesyncpro
            },
            {
                "Logo Light": logo_light,
                "Fan Control": support_fancontrol,
                "Camera Ready": camera_type,
                "WOL": support_wol,
                "HDMI Switch IC": hdmiswitch_type,
                "Moving Speaker": moving_speaker,
                "Support IR Blaster": support_irblaster,
                "Mirror Mode": mirror_mode,
                "Screen Roller Motor": screenroller_motor,
                "Motion Detect Sensor": motiondetect_sensor,
                "LCD Screen Cooling": lcdscreen_cooling,
                "LAN Support": support_lan,
                "Special Edition": special_edition,
                "Support Optical Jack": optical_jack,
                "Support Far Field Voice": farfield_voice,
                "Type-C controller IC": type_cctric,
                "AI Art Extension": aiart_extension,
                "Board Design": board_design,
                "EMMC Density": emmc_density
            },
            {
                "Video ADC Index": videoadc_index,
                "Audio ADC Index": audioadc_index,
                "USB Count": usb_count,
                "USB 1": usb_1,
                "USB 2": usb_2,
                "USB 3": usb_3,
                "Headphone": support_headphone,
                "CI_AP Key": ciap_key,
                "DTCP_AP Key": dtcpap_key,
                "MAC_AP Key": macap_key,
                "ESN_AP Key": esnap_key,
                "Widevine_AP Key": widevineap_key,
                "CI_ECP_AP Key": ciecpap_key,
                "ATSC 3.0 (KR) Key": atsc30_key,
                "New ErP": new_erp,
                "OLED CPC": oled_cpc,
                "PD Charge": pd_charge
            },
            {
                "Digital Eye": digital_eye,
                "Energy Star": energy_star,
                "AdaptiveDim Default": adaptivedim_default,
                "Adaptive Dimming": adaptive_dimming,
                "Default Backlight": default_backlight,
                "Sound Mode": sound_mode,
                "ISF": isf_mode,
                "Set ID": set_id,
                "Support Calman SW": support_calmansw,
                "DVR Ready": dvr_ready,
                "Audio Line Out": audio_lineout,
                "WIFI/BT": wifi_bt,
                "WIFI assy type": wifi_assy_type,
                "Motion Remocon": motion_remocon,
                "AudioEQ Eye": audioeq_eye,
                "EDID Type": edid_type
            },
            {
                "Panel Type": panel_type,
                "Panel Interface": panel_interface,
                "Panel Resolution": panel_resolution,
                "Panel Max Frame Rate": panel_maxframerate,
                "Panel Max Bit": panel_maxbit,
                "Panel Division Type": panel_divisiontype,
                "External Frc Type": external_frc,
                "DDR Size": ddr_size,
                "Country Type": country_type,
                "Tuner Type": tuner_type,
                "Micom LocalKey Type": micom_localkey,
                "AR RL on Control": arrlon_control,
                "IR LED Control": irled_control,
                "Model Type": model_type,
                "Wee Turnkey Version": weeturnkey_version
            }
        ]
        
        key_value_df = pd.DataFrame(key_value)
        data = [
        {
            "Tool Option 1": str(df_parsed.iloc[0]['Tool Option 1']),
            "Tool Option 2": str(df_parsed.iloc[0]['Tool Option 2']),
            "Tool Option 3": str(df_parsed.iloc[0]['Tool Option 3']),
            "Tool Option 4": str(df_parsed.iloc[0]['Tool Option 4']),
            "Tool Option 5": str(df_parsed.iloc[0]['Tool Option 5']),
            "Tool Option 6": str(df_parsed.iloc[0]['Tool Option 6']),
            "Board Option": str(df_parsed.iloc[0]['Board Option']),
            "Board+ToolCRC": str(df_parsed.iloc[0]['Board+ToolCRC']),
            "Area Code": str(df_parsed.iloc[0]['Area Code']),
            "Country Group": str(df_parsed.iloc[0]['Country Group']),
            "Country": str(df_parsed.iloc[0]['Country']),
            "Model Write": str(df_parsed.iloc[0]['Model Write']),
            "CI+": str(df_parsed.iloc[0]['CI+']),
            # "MAC": str(df_parsed.iloc[0]['MAC']),
            "ESN": str(df_parsed.iloc[0]['ESN']),
            "Widevine": str(df_parsed.iloc[0]['Widevine']),
            "Built Wifi": str(df_parsed.iloc[0]['Built Wifi']),
            "DVBS": str(df_parsed.iloc[0]['DVBS']),
            "DVBS2": str(df_parsed.iloc[0]['DVBS2']),
            "Marlin": str(df_parsed.iloc[0]['Marlin']),
            "HDCP 2.0 Rx": str(df_parsed.iloc[0]['HDCP 2.0 Rx']),
            "HDCP 2.0 Tx": str(df_parsed.iloc[0]['HDCP 2.0 Tx']),
            "DTCP Rx": str(df_parsed.iloc[0]['DTCP Rx']),
            "Japan LNB": str(df_parsed.iloc[0]['Japan LNB']),
            "HDCP 1.4 Rx": str(df_parsed.iloc[0]['HDCP 1.4 Rx']),
            "V-com": str(df_parsed.iloc[0]['V-com']),
            "MFi": str(df_parsed.iloc[0]['MFi']),
            "ATSC3.0": str(df_parsed.iloc[0]['ATSC3.0']),
            "OLED Panel ID": str(df_parsed.iloc[0]['OLED Panel ID']),
            "CI+ECP": str(df_parsed.iloc[0]['CI+ECP']),
            "QUBYX": str(df_parsed.iloc[0]['QUBYX']),
            "Inch Code": str(key_value_df.iloc[0]['Inch Code']),
            "Tool": str(key_value_df.iloc[0]['Tool']),
            "Panel Code": str(key_value_df.iloc[0]['Panel Code']),
            "Pmic set Mode": str(key_value_df.iloc[0]['Pmic set Mode']),
            "Backlight Type": str(key_value_df.iloc[0]['Backlight Type']),
            "Local Dim Block": str(key_value_df.iloc[0]['Local Dim Block']),
            "Adjust LCD VCOM": str(key_value_df.iloc[0]['Adjust LCD VCOM']),
            "Audio Power Volt": str(key_value_df.iloc[1]['Audio Power Volt']),
            "PWM2 Duty": str(key_value_df.iloc[1]['PWM2 Duty']),
            "Max PWM": str(key_value_df.iloc[1]['Max PWM']),
            "Scanning B/L": str(key_value_df.iloc[1]['Scanning B/L']),
            "BPL Current Type": str(key_value_df.iloc[1]['BPL Current Type']),
            "Power Mode Select": str(key_value_df.iloc[1]['Power Mode Select']),
            "Eye Sensor LED Gain Control": str(key_value_df.iloc[1]['Eye Sensor LED Gain Control']),
            "Standard Backlight": str(key_value_df.iloc[1]['Standard Backlight']),
            "Vivid Sports Backlight": str(key_value_df.iloc[1]['Vivid Sports Backlight']),
            "Panel Gamut Type": str(key_value_df.iloc[2]['Panel Gamut Type']),
            "Motion Pro Mode": str(key_value_df.iloc[2]['Motion Pro Mode']),
            "Support Dolby Vision HDR": str(key_value_df.iloc[2]['Support Dolby Vision HDR']),
            "Audio Amp": str(key_value_df.iloc[2]['Audio Amp']),
            "Speaker Watt.": str(key_value_df.iloc[2]['Speaker Watt']),
            "Luminance Up": str(key_value_df.iloc[2]['Luminance Up']),
            "Support VRR": str(key_value_df.iloc[2]['Support VRR']),
            "Support Freesync": str(key_value_df.iloc[2]['Support Freesync']),
            "AI Sound": str(key_value_df.iloc[2]['AI Sound']),
            "Dolby Vison Precision Detail": str(key_value_df.iloc[2]['Dolby Vison Precision Detail']),
            "PWM Freq. double": str(key_value_df.iloc[2]['PWM Freq. double']),
            "Motion Booster": str(key_value_df.iloc[2]['Motion Booster']),
            "OLED DPC Type": str(key_value_df.iloc[2]['OLED DPC Type']),
            "Support Freesync Pro": str(key_value_df.iloc[2]['Support Freesync Pro']),
            "Logo Light": str(key_value_df.iloc[3]['Logo Light']),
            "Fan Control": str(key_value_df.iloc[3]['Fan Control']),
            "Camera Ready": str(key_value_df.iloc[3]['Camera Ready']),
            "WOL": str(key_value_df.iloc[3]['WOL']),
            "HDMI Switch IC": str(key_value_df.iloc[3]['HDMI Switch IC']),
            "Moving Speaker": str(key_value_df.iloc[3]['Moving Speaker']),
            "Support IR Blaster": str(key_value_df.iloc[3]['Support IR Blaster']),
            "Mirror Mode": str(key_value_df.iloc[3]['Mirror Mode']),
            "Screen Roller Motor": str(key_value_df.iloc[3]['Screen Roller Motor']),
            "Motion Detect Sensor": str(key_value_df.iloc[3]['Motion Detect Sensor']),
            "LCD Screen Cooling": str(key_value_df.iloc[3]['LCD Screen Cooling']),
            "LAN Support": str(key_value_df.iloc[3]['LAN Support']),
            "Special Edition": str(key_value_df.iloc[3]['Special Edition']),
            "Support Optical Jack": str(key_value_df.iloc[3]['Support Optical Jack']),
            "Support Far Field Voice": str(key_value_df.iloc[3]['Support Far Field Voice']),
            "Type-C controller IC": str(key_value_df.iloc[3]['Type-C controller IC']),
            "AI Art Extension": str(key_value_df.iloc[3]['AI Art Extension']),
            "Board Design": str(key_value_df.iloc[3]['Board Design']),
            "EMMC Density": str(key_value_df.iloc[3]['EMMC Density']),
            "Video ADC Index": str(key_value_df.iloc[4]['Video ADC Index']),
            "Audio ADC Index": str(key_value_df.iloc[4]['Audio ADC Index']),
            "USB Count": str(key_value_df.iloc[4]['USB Count']),
            "USB 1": str(key_value_df.iloc[4]['USB 1']),
            "USB 2": str(key_value_df.iloc[4]['USB 2']),
            "USB 3": str(key_value_df.iloc[4]['USB 3']),
            "Headphone": str(key_value_df.iloc[4]['Headphone']),
            "CI_AP Key": str(key_value_df.iloc[4]['CI_AP Key']),
            "DTCP_AP Key": str(key_value_df.iloc[4]['DTCP_AP Key']),
            "MAC_AP Key": str(key_value_df.iloc[4]['MAC_AP Key']),
            "ESN_AP Key": str(key_value_df.iloc[4]['ESN_AP Key']),
            "Widevine_AP Key": str(key_value_df.iloc[4]['Widevine_AP Key']),
            "CI_ECP_AP Key": str(key_value_df.iloc[4]['CI_ECP_AP Key']),
            "ATSC 3.0 (KR) Key": str(key_value_df.iloc[4]['ATSC 3.0 (KR) Key']),
            "New ErP": str(key_value_df.iloc[4]['New ErP']),
            "OLED CPC": str(key_value_df.iloc[4]['OLED CPC']),
            "PD Charge": str(key_value_df.iloc[4]['PD Charge']),
            "Digital Eye": str(key_value_df.iloc[5]['Digital Eye']),
            "Energy Star": str(key_value_df.iloc[5]['Energy Star']),
            "AdaptiveDim Default": str(key_value_df.iloc[5]['AdaptiveDim Default']),
            "Adaptive Dimming": str(key_value_df.iloc[5]['Adaptive Dimming']),
            "Default Backlight": str(key_value_df.iloc[5]['Default Backlight']),
            "Sound Mode": str(key_value_df.iloc[5]['Sound Mode']),
            "ISF": str(key_value_df.iloc[5]['ISF']),
            "Set ID": str(key_value_df.iloc[5]['Set ID']),
            "Support Calman SW": str(key_value_df.iloc[5]['Support Calman SW']),
            "DVR Ready": str(key_value_df.iloc[5]['DVR Ready']),
            "Audio Line Out": str(key_value_df.iloc[5]['Audio Line Out']),
            "WIFI/BT": str(key_value_df.iloc[5]['WIFI/BT']),
            "WIFI assy type": str(key_value_df.iloc[5]['WIFI assy type']),
            "Motion Remocon": str(key_value_df.iloc[5]['Motion Remocon']),
            "AudioEQ Eye": str(key_value_df.iloc[5]['AudioEQ Eye']),
            "EDID Type": str(key_value_df.iloc[5]['EDID Type']),
            "Panel Type": str(key_value_df.iloc[6]['Panel Type']),
            "Panel Interface": str(key_value_df.iloc[6]['Panel Interface']),
            "Panel Resolution": str(key_value_df.iloc[6]['Panel Resolution']),
            "Panel Max Frame Rate": str(key_value_df.iloc[6]['Panel Max Frame Rate']),
            "Panel Max Bit": str(key_value_df.iloc[6]['Panel Max Bit']),
            "Panel Division Type": str(key_value_df.iloc[6]['Panel Division Type']),
            "External Frc Type": str(key_value_df.iloc[6]['External Frc Type']),
            "DDR Size": str(key_value_df.iloc[6]['DDR Size']),
            "Country Type": str(key_value_df.iloc[6]['Country Type']),
            "Tuner Type": str(key_value_df.iloc[6]['Tuner Type']),
            "Micom LocalKey Type": str(key_value_df.iloc[6]['Micom LocalKey Type']),
            "AR RL on Control": str(key_value_df.iloc[6]['AR RL on Control']),
            "IR LED Control": str(key_value_df.iloc[6]['IR LED Control']),
            "Model Type": str(key_value_df.iloc[6]['Model Type']),
            "Wee Turnkey Version": str(key_value_df.iloc[6]['Wee Turnkey Version']),
            }
        ]

        with open("json/3_development_tooloption.json", "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

        wb = load_workbook(filename="excel/template_option.xlsx")
        ws = wb["BEN Compare"]
        
        for row in ws.iter_rows(min_row=4, max_row=132, min_col=5, max_col=5):
            for cell in row:
                cell.value = ""

        ws["E4"] = str(development_model.split('@')[0])
        key_val = df_parsed.iloc[0]  # Series baris pertama
        key_col = [
            'Tool Option 1','Tool Option 2','Tool Option 3','Tool Option 4','Tool Option 5','Tool Option 6',
            'Board Option','Board+ToolCRC','Area Code','Country Group','Country','Model Write','CI+','MAC','ESN',
            'Widevine','Built Wifi','DVBS','DVBS2','Marlin','HDCP 2.0 Rx','HDCP 2.0 Tx','DTCP Rx','Japan LNB',
            'HDCP 1.4 Rx','V-com','MFi','ATSC3.0','OLED Panel ID','CI+ECP','QUBYX'
            ]

        key_start_row = 5  # D41
        key_col_idx = 5    # D = kolom ke-4

        for i, col_name in enumerate(key_col):
            row = key_start_row + i
            value = key_val.get(col_name, "")  # aman bila kolom tidak ada
            ws.cell(row=row, column=key_col_idx, value=value if value is not None else "")
        
        key_option = key_df_parsed.iloc[0]
        tool_option1 = key_option[0]
        tool_option2 = key_option[1]
        tool_option3 = key_option[2]
        tool_option4 = key_option[3]
        tool_option5 = key_option[4]
        tool_option6 = key_option[5]
        board_option = key_option[6]

        fields_0 = [
            'Inch Code',
            'Tool',
            'Panel Code',
            'Pmic set Mode',
            'Backlight Type',
            'Local Dim Block',
            'Adjust LCD VCOM',
        ]

        fields_1 = [
            'Audio Power Volt',
            'PWM2 Duty',
            'Max PWM',
            'Scanning B/L',
            'BPL Current Type',
            'Power Mode Select',
            'Eye Sensor LED Gain Control',
            'Standard Backlight',
            'Vivid Sports Backlight',
        ]

        fields_2 = [
            "Panel Gamut Type",
            "Motion Pro Mode",
            "Support Dolby Vision HDR",
            "Audio Amp",
            "Speaker Watt",
            "Luminance Up",
            "Support VRR",
            "Support Freesync",
            "AI Sound",
            "Dolby Vison Precision Detail",
            "PWM Freq. double",
            "Motion Booster",
            "OLED DPC Type",
            "Support Freesync Pro"
        ]

        fields_3 = [
            "Logo Light",
            "Fan Control",
            "Camera Ready",
            "WOL",
            "HDMI Switch IC",
            "Moving Speaker",
            "Support IR Blaster",
            "Mirror Mode",
            "Screen Roller Motor",
            "Motion Detect Sensor",
            "LCD Screen Cooling",
            "LAN Support",
            "Special Edition",
            "Support Optical Jack",
            "Support Far Field Voice",
            "Type-C controller IC",
            "AI Art Extension",
            "Board Design",
            "EMMC Density"
        ]

        fields_4 = [
            "Video ADC Index",
            "Audio ADC Index",
            "USB Count",
            "USB 1",
            "USB 2",
            "USB 3",
            "Headphone",
            "CI_AP Key",
            "DTCP_AP Key",
            "MAC_AP Key",
            "ESN_AP Key",
            "Widevine_AP Key",
            "CI_ECP_AP Key",
            "ATSC 3.0 (KR) Key",
            "New ErP",
            "OLED CPC",
            "PD Charge"
        ]

        fields_5 = [
            "Digital Eye",
            "Energy Star",
            "AdaptiveDim Default",
            "Adaptive Dimming",
            "Default Backlight",
            "Sound Mode",
            "ISF",
            "Set ID",
            "Support Calman SW",
            "DVR Ready",
            "Audio Line Out",
            "WIFI/BT",         
            "WIFI assy type",
            "Motion Remocon",
            "AudioEQ Eye",
            "EDID Type"
        ]

        fields_6 = [
            "Panel Type",
            "Panel Interface",
            "Panel Resolution",
            "Panel Max Frame Rate",
            "Panel Max Bit",
            "Panel Division Type",
            "External Frc Type",
            "DDR Size",
            "Country Type",
            "Tuner Type",
            "Micom LocalKey Type",
            "AR RL on Control",
            "IR LED Control",
            "Model Type",
            "Wee Turnkey Version"
        ]

        option_start_row = 36
        option_col_idx = 5
        r = option_start_row

        for key in fields_0:
            ws.cell(row=r, column=option_col_idx, value=tool_option1[key])
            r += 1
        for key in fields_1:
            ws.cell(row=r, column=option_col_idx, value=tool_option2[key])
            r += 1
        for key in fields_2:
            ws.cell(row=r, column=option_col_idx, value=tool_option3[key])
            r += 1
        for key in fields_3:
            ws.cell(row=r, column=option_col_idx, value=tool_option4[key])
            r += 1
        for key in fields_4:
            ws.cell(row=r, column=option_col_idx, value=tool_option5[key])
            r += 1
        for key in fields_5:
            ws.cell(row=r, column=option_col_idx, value=tool_option6[key])
            r += 1
        for key in fields_6:
            ws.cell(row=r, column=option_col_idx, value=board_option[key])
            r += 1
      
        wb.save("excel/template_option.xlsx")

class initial_tooloption:
    def __init__(self, json_path: str = "json/0_initial_ebom.json", verbose: bool = False, auto_run: bool = True):
        """
        json_path : path file JSON EBOM
        verbose   : True -> print detail per baris (seperti kode Anda), False -> silent
        auto_run  : True -> langsung proses saat inisialisasi; hasil ada di self.df_parsed
        """
        self.json_path = json_path
        self.verbose = verbose
        self.initial_parsed = pd.DataFrame()
        self.initial_jobexplanation = pd.DataFrame()
        self.last_details = {"PN": "N/A", "Spec": "N/A", "UniqueID": "N/A", "JobExplanation": "N/A"}

        if auto_run:
            self.initial_parsed = self.run()
    def run(self) -> pd.DataFrame:
        global tooloption1
        global tooloption2
        global tooloption3
        global tooloption4
        global tooloption5
        global tooloption6
        global boardoption
        # ---------- Load JSON secara robust ----------
        with open(self.json_path, "r", encoding="utf-8") as f:
            tooloption_data = json.load(f)

        initial_model = pd.json_normalize([
        item for item in tooloption_data.get("data", [])
        if ((
            item.get("uniqueStr") == "00001" 
           ))
        ])
        if not initial_model.empty:
            for idx, row in initial_model.iterrows():
                initial_model = row['childNameDisplay']

        # Normalisasi top-level → list of dict (candidates)
        if isinstance(tooloption_data, dict):
            candidates = tooloption_data.get("data", [])
            if not isinstance(candidates, list):
                candidates = [candidates]
        elif isinstance(tooloption_data, list):
            candidates = tooloption_data
        else:
            candidates = []

        # Helper kecil untuk cast ke string aman
        def _to_text(x):
            if x is None:
                return ""
            if isinstance(x, (list, tuple, set)):
                return " ".join(map(str, x))
            return str(x)

        # ---------- Filter sesuai kriteria ----------
        filtered = []
        for item in candidates:
            if not isinstance(item, dict):
                continue

            uniqueStrParent = _to_text(item.get("uniqueStrParent", ""))
            childNameDisplay = _to_text(item.get("childNameDisplay", ""))

            outData = item.get("outData", {})
            if isinstance(outData, list):
                outData = outData[0] if outData else {}

            pp_descriptions = _to_text(outData.get("pp_descriptions", ""))
            mr_siteTechnicalSpec = _to_text(outData.get("mr_siteTechnicalSpec", ""))

            cond = (
                uniqueStrParent == "00001" and
                ("EBT" in childNameDisplay) and
                ("Chassis Assembly" in pp_descriptions) and
                ("MAIN" in mr_siteTechnicalSpec)
            )
            if cond:
                filtered.append(item)

        target_jobexplanation = pd.json_normalize(filtered)
        self.initial_jobexplanation = target_jobexplanation

        # ---------- Jika tidak ada data ----------
        if target_jobexplanation.empty:
            if self.verbose:
                print("❌ Target Job Explanation not found in EBOM data.")
            self.last_details = {
                "PN": "N/A", "Spec": "N/A", "UniqueID": "N/A", "JobExplanation": "N/A"
            }
            return pd.DataFrame()

        # ---------- Helper regex kecil (inline) ----------
        get_match = lambda text, pattern, group=1, flags=0, default=None: (
            (m.group(group).strip() if (m := re.search(pattern, text, flags)) else default)
            if isinstance(text, str) else default
        )

        # ---------- Parsing per baris ----------
        records = []

        for idx, df_row in target_jobexplanation.iterrows():
            # Ambil metadata sumber (aman terhadap missing key)
            try:
                targetebtmain_pn = df_row["childNameDisplay"]
            except Exception:
                targetebtmain_pn = None

            try:
                targetebtmain_spec = df_row["outData.mr_siteTechnicalSpec"]
            except Exception:
                targetebtmain_spec = None

            try:
                targetebtmain_jobexplanation = df_row["jobExplanation"]
            except Exception:
                targetebtmain_jobexplanation = ""

            try:
                targetebtmain_uniquieid = df_row["uniqueStr"]
            except Exception:
                targetebtmain_uniquieid = None

            text = str(targetebtmain_jobexplanation) if targetebtmain_jobexplanation is not None else ""

            if self.verbose:
                print(text)

            out = {}

            # Field utama (aman)
            out["Job Explanation"] = get_match(text, r"Job Explanation:\s*\[(.*?)\]")
            out["Board Option"]    = get_match(text, r"Board Option:([^/]+)")
            bt_crc   = get_match(text, r"Board\+ToolCRC:([^/]+)")
            area_str = get_match(text, r"Area Code:([^/]+)")
            out["Country Group"]   = get_match(text, r"Country Group:([^/]+)")
            out["Country"]   = get_match(text, r"Country:([^/]+)")

            # Konversi numerik aman
            if bt_crc is not None and str(bt_crc).strip().isdigit():
                out["Board+ToolCRC"] = int(str(bt_crc).strip())
            else:
                out["Board+ToolCRC"] = bt_crc

            if area_str is not None and str(area_str).strip().isdigit():
                out["Area Code"] = int(str(area_str).strip())
            else:
                out["Area Code"] = area_str

            # Tool Option -> kolom terpisah (toleran spasi/pemisah)
            tool_inner = get_match(text, r"Tool Option\(([^)]+)\)")
            if tool_inner:
                # Split default pakai koma; jika ada pemisah lain, ganti dengan regex split: r"[;,]\s*"
                for pair in re.split(r"[,\s]+", tool_inner.strip()):
                    if ":" in pair:
                        k, v = pair.split(":", 1)
                        k = k.strip()
                        v = v.strip()
                        col = f"Tool Option {k}"
                        out[col] = int(v) if v.isdigit() else v

            # Flags Yes/No → boolean
            for token in text.split("/"):
                token = token.strip()
                m = re.search(r"^(.*?)\s*\[(Yes|No)\]\s*$", token, flags=re.IGNORECASE)
                if m:
                    key = m.group(1).strip()
                    val = m.group(2).strip().lower() == "yes"
                    out[key] = "Yes" if val else "No"

            # Tambahkan metadata sumber
            out["childNameDisplay"]     = targetebtmain_pn
            out["mr_siteTechnicalSpec"] = targetebtmain_spec
            out["uniqueStr"]            = targetebtmain_uniquieid
            out["_row_index"]           = idx

            # Simpan untuk info last detail (opsional)
            self.last_details = {
                "PN": targetebtmain_pn,
                "Spec": targetebtmain_spec,
                "UniqueID": targetebtmain_uniquieid,
                "JobExplanation": targetebtmain_jobexplanation
            }
            records.append(out)
            # Output seperti kode Anda (dikendalikan verbose)
            if self.verbose:
                df_one = pd.DataFrame([out])
                print(df_one.columns.tolist())
                print(df_one.head(1).T)
                print("success")
            
        df_parsed = pd.DataFrame(records)

        target_boardoption = df_parsed.iloc[0]['Board Option']
        target_toolopt1 = df_parsed.iloc[0]['Tool Option 1']
        target_toolopt2 = df_parsed.iloc[0]['Tool Option 2']
        target_toolopt3 = df_parsed.iloc[0]['Tool Option 3']
        target_toolopt4 = df_parsed.iloc[0]['Tool Option 4']
        target_toolopt5 = df_parsed.iloc[0]['Tool Option 5']
        target_toolopt6 = df_parsed.iloc[0]['Tool Option 6']

        tooloption1 = int(target_toolopt1)
        tooloption2 = int(target_toolopt2)
        tooloption3 = int(target_toolopt3)
        tooloption4 = int(target_toolopt4)
        tooloption5 = int(target_toolopt5)
        tooloption6 = int(target_toolopt6)
        boardoption = int(target_boardoption,16)

        calc_toolopt1 = calculate_tooloption1()
        calc_toolopt2 = calculate_tooloption2()
        calc_toolopt3 = calculate_tooloption3()
        calc_toolopt4 = calculate_tooloption4()
        calc_toolopt5 = calculate_tooloption5()
        calc_toolopt6 = calculate_tooloption6()
        calc_boardopt = calculate_boardoption()

        self.result_tooloption1 = calc_toolopt1.toolopt1_run()
        self.result_tooloption2 = calc_toolopt2.toolopt2_run()
        self.result_tooloption3 = calc_toolopt3.toolopt3_run()
        self.result_tooloption4 = calc_toolopt4.toolopt4_run()
        self.result_tooloption5 = calc_toolopt5.toolopt5_run()
        self.result_tooloption6 = calc_toolopt6.toolopt6_run()
        self.result_boardoption = calc_boardopt.boardoption_run()
        key_records = []
        key_records.append([
            {
                "Inch Code": inch_code,
                "Tool": tool_code,
                "Panel Code": panel_code,
                "Pmic set Mode": pmic_mode,
                "Backlight Type": backlight_type,
                "Local Dim Block": localdim_block,
                "Adjust LCD VCOM": adjust_vcom
            },
            {
                "Audio Power Volt": audiopw_volt,
                "PWM2 Duty": pwm2_duty,
                "Max PWM": max_pwm,
                "Scanning B/L": scanning_bl,
                "BPL Current Type": bpl_type,
                "Power Mode Select": powermode_select,
                "Eye Sensor LED Gain Control": eyesensor_gain,
                "Standard Backlight": standard_backlight,
                "Vivid Sports Backlight": vividsports_bl
            },
            {
                "Panel Gamut Type": panelgamut_type,
                "Motion Pro Mode": motionpro_mode,
                "Support Dolby Vision HDR": support_dolbyvisionhdr,
                "Audio Amp": ampchip_type,
                "Speaker Watt": audiospk_watt,
                "Luminance Up": support_luminanceup,
                "Support VRR": support_vrr,
                "Support Freesync": support_freesync,
                "AI Sound": aisound_type,
                "Dolby Vison Precision Detail": dolbyvison_precisiondetail,
                "PWM Freq. double": pwmfreq_double,
                "Motion Booster": motion_booster,
                "OLED DPC Type": oleddpc_type,
                "Support Freesync Pro": support_freesyncpro
            },
            {
                "Logo Light": logo_light,
                "Fan Control": support_fancontrol,
                "Camera Ready": camera_type,
                "WOL": support_wol,
                "HDMI Switch IC": hdmiswitch_type,
                "Moving Speaker": moving_speaker,
                "Support IR Blaster": support_irblaster,
                "Mirror Mode": mirror_mode,
                "Screen Roller Motor": screenroller_motor,
                "Motion Detect Sensor": motiondetect_sensor,
                "LCD Screen Cooling": lcdscreen_cooling,
                "LAN Support": support_lan,
                "Special Edition": special_edition,
                "Support Optical Jack": optical_jack,
                "Support Far Field Voice": farfield_voice,
                "Type-C controller IC": type_cctric,
                "AI Art Extension": aiart_extension,
                "Board Design": board_design,
                "EMMC Density": emmc_density
            },
            {
                "Video ADC Index": videoadc_index,
                "Audio ADC Index": audioadc_index,
                "USB Count": usb_count,
                "USB 1": usb_1,
                "USB 2": usb_2,
                "USB 3": usb_3,
                "Headphone": support_headphone,
                "CI_AP Key": ciap_key,
                "DTCP_AP Key": dtcpap_key,
                "MAC_AP Key": macap_key,
                "ESN_AP Key": esnap_key,
                "Widevine_AP Key": widevineap_key,
                "CI_ECP_AP Key": ciecpap_key,
                "ATSC 3.0 (KR) Key": atsc30_key,
                "New ErP": new_erp,
                "OLED CPC": oled_cpc,
                "PD Charge": pd_charge
            },
            {
                "Digital Eye": digital_eye,
                "Energy Star": energy_star,
                "AdaptiveDim Default": adaptivedim_default,
                "Adaptive Dimming": adaptive_dimming,
                "Default Backlight": default_backlight,
                "Sound Mode": sound_mode,
                "ISF": isf_mode,
                "Set ID": set_id,
                "Support Calman SW": support_calmansw,
                "DVR Ready": dvr_ready,
                "Audio Line Out": audio_lineout,
                "WIFI/BT": wifi_bt,
                "WIFI assy type": wifi_assy_type,
                "Motion Remocon": motion_remocon,
                "AudioEQ Eye": audioeq_eye,
                "EDID Type": edid_type
            },
            {
                "Panel Type": panel_type,
                "Panel Interface": panel_interface,
                "Panel Resolution": panel_resolution,
                "Panel Max Frame Rate": panel_maxframerate,
                "Panel Max Bit": panel_maxbit,
                "Panel Division Type": panel_divisiontype,
                "External Frc Type": external_frc,
                "DDR Size": ddr_size,
                "Country Type": country_type,
                "Tuner Type": tuner_type,
                "Micom LocalKey Type": micom_localkey,
                "AR RL on Control": arrlon_control,
                "IR LED Control": irled_control,
                "Model Type": model_type,
                "Wee Turnkey Version": weeturnkey_version
            }
        ])
        key_df_parsed = pd.DataFrame(key_records)
        
        key_value = [
            {
                "Inch Code": inch_code,
                "Tool": tool_code,
                "Panel Code": panel_code,
                "Pmic set Mode": pmic_mode,
                "Backlight Type": backlight_type,
                "Local Dim Block": localdim_block,
                "Adjust LCD VCOM": adjust_vcom
            },
            {
                "Audio Power Volt": audiopw_volt,
                "PWM2 Duty": pwm2_duty,
                "Max PWM": max_pwm,
                "Scanning B/L": scanning_bl,
                "BPL Current Type": bpl_type,
                "Power Mode Select": powermode_select,
                "Eye Sensor LED Gain Control": eyesensor_gain,
                "Standard Backlight": standard_backlight,
                "Vivid Sports Backlight": vividsports_bl
            },
            {
                "Panel Gamut Type": panelgamut_type,
                "Motion Pro Mode": motionpro_mode,
                "Support Dolby Vision HDR": support_dolbyvisionhdr,
                "Audio Amp": ampchip_type,
                "Speaker Watt": audiospk_watt,
                "Luminance Up": support_luminanceup,
                "Support VRR": support_vrr,
                "Support Freesync": support_freesync,
                "AI Sound": aisound_type,
                "Dolby Vison Precision Detail": dolbyvison_precisiondetail,
                "PWM Freq. double": pwmfreq_double,
                "Motion Booster": motion_booster,
                "OLED DPC Type": oleddpc_type,
                "Support Freesync Pro": support_freesyncpro
            },
            {
                "Logo Light": logo_light,
                "Fan Control": support_fancontrol,
                "Camera Ready": camera_type,
                "WOL": support_wol,
                "HDMI Switch IC": hdmiswitch_type,
                "Moving Speaker": moving_speaker,
                "Support IR Blaster": support_irblaster,
                "Mirror Mode": mirror_mode,
                "Screen Roller Motor": screenroller_motor,
                "Motion Detect Sensor": motiondetect_sensor,
                "LCD Screen Cooling": lcdscreen_cooling,
                "LAN Support": support_lan,
                "Special Edition": special_edition,
                "Support Optical Jack": optical_jack,
                "Support Far Field Voice": farfield_voice,
                "Type-C controller IC": type_cctric,
                "AI Art Extension": aiart_extension,
                "Board Design": board_design,
                "EMMC Density": emmc_density
            },
            {
                "Video ADC Index": videoadc_index,
                "Audio ADC Index": audioadc_index,
                "USB Count": usb_count,
                "USB 1": usb_1,
                "USB 2": usb_2,
                "USB 3": usb_3,
                "Headphone": support_headphone,
                "CI_AP Key": ciap_key,
                "DTCP_AP Key": dtcpap_key,
                "MAC_AP Key": macap_key,
                "ESN_AP Key": esnap_key,
                "Widevine_AP Key": widevineap_key,
                "CI_ECP_AP Key": ciecpap_key,
                "ATSC 3.0 (KR) Key": atsc30_key,
                "New ErP": new_erp,
                "OLED CPC": oled_cpc,
                "PD Charge": pd_charge
            },
            {
                "Digital Eye": digital_eye,
                "Energy Star": energy_star,
                "AdaptiveDim Default": adaptivedim_default,
                "Adaptive Dimming": adaptive_dimming,
                "Default Backlight": default_backlight,
                "Sound Mode": sound_mode,
                "ISF": isf_mode,
                "Set ID": set_id,
                "Support Calman SW": support_calmansw,
                "DVR Ready": dvr_ready,
                "Audio Line Out": audio_lineout,
                "WIFI/BT": wifi_bt,
                "WIFI assy type": wifi_assy_type,
                "Motion Remocon": motion_remocon,
                "AudioEQ Eye": audioeq_eye,
                "EDID Type": edid_type
            },
            {
                "Panel Type": panel_type,
                "Panel Interface": panel_interface,
                "Panel Resolution": panel_resolution,
                "Panel Max Frame Rate": panel_maxframerate,
                "Panel Max Bit": panel_maxbit,
                "Panel Division Type": panel_divisiontype,
                "External Frc Type": external_frc,
                "DDR Size": ddr_size,
                "Country Type": country_type,
                "Tuner Type": tuner_type,
                "Micom LocalKey Type": micom_localkey,
                "AR RL on Control": arrlon_control,
                "IR LED Control": irled_control,
                "Model Type": model_type,
                "Wee Turnkey Version": weeturnkey_version
            }
        ]
        
        key_value_df = pd.DataFrame(key_value)
        data = [
        {
            "Tool Option 1": str(df_parsed.iloc[0]['Tool Option 1']),
            "Tool Option 2": str(df_parsed.iloc[0]['Tool Option 2']),
            "Tool Option 3": str(df_parsed.iloc[0]['Tool Option 3']),
            "Tool Option 4": str(df_parsed.iloc[0]['Tool Option 4']),
            "Tool Option 5": str(df_parsed.iloc[0]['Tool Option 5']),
            "Tool Option 6": str(df_parsed.iloc[0]['Tool Option 6']),
            "Board Option": str(df_parsed.iloc[0]['Board Option']),
            "Board+ToolCRC": str(df_parsed.iloc[0]['Board+ToolCRC']),
            "Area Code": str(df_parsed.iloc[0]['Area Code']),
            "Country Group": str(df_parsed.iloc[0]['Country Group']),
            "Country": str(df_parsed.iloc[0]['Country']),
            "Model Write": str(df_parsed.iloc[0]['Model Write']),
            "CI+": str(df_parsed.iloc[0]['CI+']),
            # "MAC": str(df_parsed.iloc[0]['MAC']),
            "ESN": str(df_parsed.iloc[0]['ESN']),
            "Widevine": str(df_parsed.iloc[0]['Widevine']),
            "Built Wifi": str(df_parsed.iloc[0]['Built Wifi']),
            "DVBS": str(df_parsed.iloc[0]['DVBS']),
            "DVBS2": str(df_parsed.iloc[0]['DVBS2']),
            "Marlin": str(df_parsed.iloc[0]['Marlin']),
            "HDCP 2.0 Rx": str(df_parsed.iloc[0]['HDCP 2.0 Rx']),
            "HDCP 2.0 Tx": str(df_parsed.iloc[0]['HDCP 2.0 Tx']),
            "DTCP Rx": str(df_parsed.iloc[0]['DTCP Rx']),
            "Japan LNB": str(df_parsed.iloc[0]['Japan LNB']),
            "HDCP 1.4 Rx": str(df_parsed.iloc[0]['HDCP 1.4 Rx']),
            "V-com": str(df_parsed.iloc[0]['V-com']),
            "MFi": str(df_parsed.iloc[0]['MFi']),
            "ATSC3.0": str(df_parsed.iloc[0]['ATSC3.0']),
            "OLED Panel ID": str(df_parsed.iloc[0]['OLED Panel ID']),
            "CI+ECP": str(df_parsed.iloc[0]['CI+ECP']),
            "QUBYX": str(df_parsed.iloc[0]['QUBYX']),
            "Inch Code": str(key_value_df.iloc[0]['Inch Code']),
            "Tool": str(key_value_df.iloc[0]['Tool']),
            "Panel Code": str(key_value_df.iloc[0]['Panel Code']),
            "Pmic set Mode": str(key_value_df.iloc[0]['Pmic set Mode']),
            "Backlight Type": str(key_value_df.iloc[0]['Backlight Type']),
            "Local Dim Block": str(key_value_df.iloc[0]['Local Dim Block']),
            "Adjust LCD VCOM": str(key_value_df.iloc[0]['Adjust LCD VCOM']),
            "Audio Power Volt": str(key_value_df.iloc[1]['Audio Power Volt']),
            "PWM2 Duty": str(key_value_df.iloc[1]['PWM2 Duty']),
            "Max PWM": str(key_value_df.iloc[1]['Max PWM']),
            "Scanning B/L": str(key_value_df.iloc[1]['Scanning B/L']),
            "BPL Current Type": str(key_value_df.iloc[1]['BPL Current Type']),
            "Power Mode Select": str(key_value_df.iloc[1]['Power Mode Select']),
            "Eye Sensor LED Gain Control": str(key_value_df.iloc[1]['Eye Sensor LED Gain Control']),
            "Standard Backlight": str(key_value_df.iloc[1]['Standard Backlight']),
            "Vivid Sports Backlight": str(key_value_df.iloc[1]['Vivid Sports Backlight']),
            "Panel Gamut Type": str(key_value_df.iloc[2]['Panel Gamut Type']),
            "Motion Pro Mode": str(key_value_df.iloc[2]['Motion Pro Mode']),
            "Support Dolby Vision HDR": str(key_value_df.iloc[2]['Support Dolby Vision HDR']),
            "Audio Amp": str(key_value_df.iloc[2]['Audio Amp']),
            "Speaker Watt.": str(key_value_df.iloc[2]['Speaker Watt']),
            "Luminance Up": str(key_value_df.iloc[2]['Luminance Up']),
            "Support VRR": str(key_value_df.iloc[2]['Support VRR']),
            "Support Freesync": str(key_value_df.iloc[2]['Support Freesync']),
            "AI Sound": str(key_value_df.iloc[2]['AI Sound']),
            "Dolby Vison Precision Detail": str(key_value_df.iloc[2]['Dolby Vison Precision Detail']),
            "PWM Freq. double": str(key_value_df.iloc[2]['PWM Freq. double']),
            "Motion Booster": str(key_value_df.iloc[2]['Motion Booster']),
            "OLED DPC Type": str(key_value_df.iloc[2]['OLED DPC Type']),
            "Support Freesync Pro": str(key_value_df.iloc[2]['Support Freesync Pro']),
            "Logo Light": str(key_value_df.iloc[3]['Logo Light']),
            "Fan Control": str(key_value_df.iloc[3]['Fan Control']),
            "Camera Ready": str(key_value_df.iloc[3]['Camera Ready']),
            "WOL": str(key_value_df.iloc[3]['WOL']),
            "HDMI Switch IC": str(key_value_df.iloc[3]['HDMI Switch IC']),
            "Moving Speaker": str(key_value_df.iloc[3]['Moving Speaker']),
            "Support IR Blaster": str(key_value_df.iloc[3]['Support IR Blaster']),
            "Mirror Mode": str(key_value_df.iloc[3]['Mirror Mode']),
            "Screen Roller Motor": str(key_value_df.iloc[3]['Screen Roller Motor']),
            "Motion Detect Sensor": str(key_value_df.iloc[3]['Motion Detect Sensor']),
            "LCD Screen Cooling": str(key_value_df.iloc[3]['LCD Screen Cooling']),
            "LAN Support": str(key_value_df.iloc[3]['LAN Support']),
            "Special Edition": str(key_value_df.iloc[3]['Special Edition']),
            "Support Optical Jack": str(key_value_df.iloc[3]['Support Optical Jack']),
            "Support Far Field Voice": str(key_value_df.iloc[3]['Support Far Field Voice']),
            "Type-C controller IC": str(key_value_df.iloc[3]['Type-C controller IC']),
            "AI Art Extension": str(key_value_df.iloc[3]['AI Art Extension']),
            "Board Design": str(key_value_df.iloc[3]['Board Design']),
            "EMMC Density": str(key_value_df.iloc[3]['EMMC Density']),
            "Video ADC Index": str(key_value_df.iloc[4]['Video ADC Index']),
            "Audio ADC Index": str(key_value_df.iloc[4]['Audio ADC Index']),
            "USB Count": str(key_value_df.iloc[4]['USB Count']),
            "USB 1": str(key_value_df.iloc[4]['USB 1']),
            "USB 2": str(key_value_df.iloc[4]['USB 2']),
            "USB 3": str(key_value_df.iloc[4]['USB 3']),
            "Headphone": str(key_value_df.iloc[4]['Headphone']),
            "CI_AP Key": str(key_value_df.iloc[4]['CI_AP Key']),
            "DTCP_AP Key": str(key_value_df.iloc[4]['DTCP_AP Key']),
            "MAC_AP Key": str(key_value_df.iloc[4]['MAC_AP Key']),
            "ESN_AP Key": str(key_value_df.iloc[4]['ESN_AP Key']),
            "Widevine_AP Key": str(key_value_df.iloc[4]['Widevine_AP Key']),
            "CI_ECP_AP Key": str(key_value_df.iloc[4]['CI_ECP_AP Key']),
            "ATSC 3.0 (KR) Key": str(key_value_df.iloc[4]['ATSC 3.0 (KR) Key']),
            "New ErP": str(key_value_df.iloc[4]['New ErP']),
            "OLED CPC": str(key_value_df.iloc[4]['OLED CPC']),
            "PD Charge": str(key_value_df.iloc[4]['PD Charge']),
            "Digital Eye": str(key_value_df.iloc[5]['Digital Eye']),
            "Energy Star": str(key_value_df.iloc[5]['Energy Star']),
            "AdaptiveDim Default": str(key_value_df.iloc[5]['AdaptiveDim Default']),
            "Adaptive Dimming": str(key_value_df.iloc[5]['Adaptive Dimming']),
            "Default Backlight": str(key_value_df.iloc[5]['Default Backlight']),
            "Sound Mode": str(key_value_df.iloc[5]['Sound Mode']),
            "ISF": str(key_value_df.iloc[5]['ISF']),
            "Set ID": str(key_value_df.iloc[5]['Set ID']),
            "Support Calman SW": str(key_value_df.iloc[5]['Support Calman SW']),
            "DVR Ready": str(key_value_df.iloc[5]['DVR Ready']),
            "Audio Line Out": str(key_value_df.iloc[5]['Audio Line Out']),
            "WIFI/BT": str(key_value_df.iloc[5]['WIFI/BT']),
            "WIFI assy type": str(key_value_df.iloc[5]['WIFI assy type']),
            "Motion Remocon": str(key_value_df.iloc[5]['Motion Remocon']),
            "AudioEQ Eye": str(key_value_df.iloc[5]['AudioEQ Eye']),
            "EDID Type": str(key_value_df.iloc[5]['EDID Type']),
            "Panel Type": str(key_value_df.iloc[6]['Panel Type']),
            "Panel Interface": str(key_value_df.iloc[6]['Panel Interface']),
            "Panel Resolution": str(key_value_df.iloc[6]['Panel Resolution']),
            "Panel Max Frame Rate": str(key_value_df.iloc[6]['Panel Max Frame Rate']),
            "Panel Max Bit": str(key_value_df.iloc[6]['Panel Max Bit']),
            "Panel Division Type": str(key_value_df.iloc[6]['Panel Division Type']),
            "External Frc Type": str(key_value_df.iloc[6]['External Frc Type']),
            "DDR Size": str(key_value_df.iloc[6]['DDR Size']),
            "Country Type": str(key_value_df.iloc[6]['Country Type']),
            "Tuner Type": str(key_value_df.iloc[6]['Tuner Type']),
            "Micom LocalKey Type": str(key_value_df.iloc[6]['Micom LocalKey Type']),
            "AR RL on Control": str(key_value_df.iloc[6]['AR RL on Control']),
            "IR LED Control": str(key_value_df.iloc[6]['IR LED Control']),
            "Model Type": str(key_value_df.iloc[6]['Model Type']),
            "Wee Turnkey Version": str(key_value_df.iloc[6]['Wee Turnkey Version']),
            }
        ]
        with open("json/3_initial_tooloption.json", "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

        wb = load_workbook(filename="excel/template_option.xlsx")
        ws = wb["BEN Compare"]
        
        for row in ws.iter_rows(min_row=4, max_row=132, min_col=4, max_col=4):
            for cell in row:
                cell.value = ""

        ws["D4"] = str(initial_model.split('@')[0])
        key_val = df_parsed.iloc[0]  # Series baris pertama
        key_col = [
            'Tool Option 1','Tool Option 2','Tool Option 3','Tool Option 4','Tool Option 5','Tool Option 6',
            'Board Option','Board+ToolCRC','Area Code','Country Group','Country','Model Write','CI+','MAC','ESN',
            'Widevine','Built Wifi','DVBS','DVBS2','Marlin','HDCP 2.0 Rx','HDCP 2.0 Tx','DTCP Rx','Japan LNB',
            'HDCP 1.4 Rx','V-com','MFi','ATSC3.0','OLED Panel ID','CI+ECP','QUBYX'
            ]

        key_start_row = 5  # D41
        key_col_idx = 4    # D = kolom ke-4

        for i, col_name in enumerate(key_col):
            row = key_start_row + i
            value = key_val.get(col_name, "")  # aman bila kolom tidak ada
            ws.cell(row=row, column=key_col_idx, value=value if value is not None else "")
        
        key_option = key_df_parsed.iloc[0]
        tool_option1 = key_option[0]
        tool_option2 = key_option[1]
        tool_option3 = key_option[2]
        tool_option4 = key_option[3]
        tool_option5 = key_option[4]
        tool_option6 = key_option[5]
        board_option = key_option[6]

        fields_0 = [
            'Inch Code',
            'Tool',
            'Panel Code',
            'Pmic set Mode',
            'Backlight Type',
            'Local Dim Block',
            'Adjust LCD VCOM',
        ]

        fields_1 = [
            'Audio Power Volt',
            'PWM2 Duty',
            'Max PWM',
            'Scanning B/L',
            'BPL Current Type',
            'Power Mode Select',
            'Eye Sensor LED Gain Control',
            'Standard Backlight',
            'Vivid Sports Backlight',
        ]

        fields_2 = [
            "Panel Gamut Type",
            "Motion Pro Mode",
            "Support Dolby Vision HDR",
            "Audio Amp",
            "Speaker Watt",
            "Luminance Up",
            "Support VRR",
            "Support Freesync",
            "AI Sound",
            "Dolby Vison Precision Detail",
            "PWM Freq. double",
            "Motion Booster",
            "OLED DPC Type",
            "Support Freesync Pro"
        ]

        fields_3 = [
            "Logo Light",
            "Fan Control",
            "Camera Ready",
            "WOL",
            "HDMI Switch IC",
            "Moving Speaker",
            "Support IR Blaster",
            "Mirror Mode",
            "Screen Roller Motor",
            "Motion Detect Sensor",
            "LCD Screen Cooling",
            "LAN Support",
            "Special Edition",
            "Support Optical Jack",
            "Support Far Field Voice",
            "Type-C controller IC",
            "AI Art Extension",
            "Board Design",
            "EMMC Density"
        ]

        fields_4 = [
            "Video ADC Index",
            "Audio ADC Index",
            "USB Count",
            "USB 1",
            "USB 2",
            "USB 3",
            "Headphone",
            "CI_AP Key",
            "DTCP_AP Key",
            "MAC_AP Key",
            "ESN_AP Key",
            "Widevine_AP Key",
            "CI_ECP_AP Key",
            "ATSC 3.0 (KR) Key",
            "New ErP",
            "OLED CPC",
            "PD Charge"
        ]

        fields_5 = [
            "Digital Eye",
            "Energy Star",
            "AdaptiveDim Default",
            "Adaptive Dimming",
            "Default Backlight",
            "Sound Mode",
            "ISF",
            "Set ID",
            "Support Calman SW",
            "DVR Ready",
            "Audio Line Out",
            "WIFI/BT",         
            "WIFI assy type",
            "Motion Remocon",
            "AudioEQ Eye",
            "EDID Type"
        ]

        fields_6 = [
            "Panel Type",
            "Panel Interface",
            "Panel Resolution",
            "Panel Max Frame Rate",
            "Panel Max Bit",
            "Panel Division Type",
            "External Frc Type",
            "DDR Size",
            "Country Type",
            "Tuner Type",
            "Micom LocalKey Type",
            "AR RL on Control",
            "IR LED Control",
            "Model Type",
            "Wee Turnkey Version"
        ]

        option_start_row = 36
        option_col_idx = 4
        r = option_start_row

        for key in fields_0:
            ws.cell(row=r, column=option_col_idx, value=tool_option1[key])
            r += 1
        for key in fields_1:
            ws.cell(row=r, column=option_col_idx, value=tool_option2[key])
            r += 1
        for key in fields_2:
            ws.cell(row=r, column=option_col_idx, value=tool_option3[key])
            r += 1
        for key in fields_3:
            ws.cell(row=r, column=option_col_idx, value=tool_option4[key])
            r += 1
        for key in fields_4:
            ws.cell(row=r, column=option_col_idx, value=tool_option5[key])
            r += 1
        for key in fields_5:
            ws.cell(row=r, column=option_col_idx, value=tool_option6[key])
            r += 1
        for key in fields_6:
            ws.cell(row=r, column=option_col_idx, value=board_option[key])
            r += 1
      
        wb.save("excel/template_option.xlsx")

class calculate_tooloption1():
    def __init__(self):
        self.toolopt1_run()
        pass
    def toolopt1_run(self):
        self.calculate_inch_code(tooloption1)
        self.calculate_tool(tooloption1)
        self.calculate_panel_code(tooloption1)
        self.calculate_pmic_mode(tooloption1)
        self.calculate_backlight_type(tooloption1)
        self.calculate_localdim_block(tooloption1)
        self.calculate_adjust_vcom(tooloption1)
    def calculate_inch_code(self,toolopt1):
        global inch_code
        inch_max_val = 64
        inch_step_val = 1
        inch_start_val = 0
        inch_min_index = 1

        inch_code_array = [
        "Auto",
        "22", "23", "24", "26", "27", "28", "32", "37", "39", "40",
        "42", "43", "47", "48", "49", "50",
        "55", "58", "60",
        "65", "70", "75", "77", "79",
        "82", "83", "84", "85", "86", "88",
        "97", "98", "100", "105", "120", "136"
    ]
        inch_code_val = [inch_start_val + i * inch_step_val for i in range((inch_max_val - inch_start_val)//inch_step_val + 1)]
        inch_code_data = list(zip(inch_code_array, inch_code_val))
        # print(inch_code_data)
        mod_result = toolopt1 % inch_max_val
        indirect_value = inch_code_val[inch_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_inch_code = result

        if index_inch_code >= len(inch_code_array):
            print("Index exceeds the length of the list")
        else:
            inch_code = inch_code_array[index_inch_code]
    def calculate_tool(self,toolopt1):
        global tool_code
        tool_max_val = 4096
        tool_step_val = 64
        tool_start_val = 0
        tool_min_index = 1

        tool_array = [
        "R1", "Z5", "T4", "W6", "G6", "C6", "CS6", "B6", "B6E", "REV1", "REV2",
        "MLED95", "MLED9M", "MLED85",
        "QNED90", "QNED85", "QNED82", "QNED80", "QNED70",
        "REV3", "REV4", "REV5", "REV6",
        "NU90", "NU85", "NU80",
        "REV7", "REV8", "REV9", "REV10",
        "LB65", "LR63", "LB70",
        "REV11", "REV12", "REV13",
        "ART10", "ART90",
        "LX1T", "LX3Q", "LX5Q", "LX6T",
        "REV14", "REV15", "REV16", "REV17",
        "JDM_TPV", "JDM_TCL", "JDM_BOE", "JDM_MOKA",
        "JDM_MOKA_UHD", "JDM_MOKA_LOW",
        "REV18", "REV19",
        "U50", "U60", "U70", "U80", "U88", "U90"
    ]
        tool_val = [tool_start_val + i * tool_step_val for i in range((tool_max_val - tool_start_val)//tool_step_val + 1)]
        tool_data = list(zip(tool_array, tool_val))
        # print(tool_data)
        mod_result = toolopt1 % tool_max_val
        indirect_value = tool_val[tool_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_tool = result

        if index_tool >= len(tool_array):
            print("Index exceeds the length of the list")
        else:
            tool_code= tool_array[index_tool]
    def calculate_panel_code(self,toolopt1):
        global panel_code
        panel_code_max_val = 131072
        panel_code_step_val = 4096
        panel_code_start_val = 0
        panel_code_min_index = 1

        panel_code_array = [
        "A", "B", "C", "D", "E", "F", "G", "H",
        "J", "K", "L", "M", "N",
        "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"
    ]
        panel_code_val = [panel_code_start_val + i * panel_code_step_val for i in range((panel_code_max_val - panel_code_start_val)//panel_code_step_val + 1)]
        panel_code_data = list(zip(panel_code_array, panel_code_val))
        # print(panel_code_data)
        mod_result = toolopt1 % panel_code_max_val
        indirect_value = panel_code_val[panel_code_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_tool = result

        if index_tool >= len(panel_code_array):
            print("Index exceeds the length of the list")
        else:
            panel_code = panel_code_array[index_tool]   
    def calculate_pmic_mode(self,toolopt1):
        global pmic_mode
        pmic_mode_max_val = 1048576
        pmic_mode_step_val = 131072
        pmic_mode_start_val = 0
        pmic_mode_min_index = 1

        pmic_mode_array = [
        "off", "on"
        ]
        pmic_mode_val = [pmic_mode_start_val + i * pmic_mode_step_val for i in range((pmic_mode_max_val - pmic_mode_start_val)//pmic_mode_step_val + 1)]
        pmic_mode_data = list(zip(pmic_mode_array, pmic_mode_val))
        # print(pmic_mode_data)
        mod_result = toolopt1 % pmic_mode_max_val
        indirect_value = pmic_mode_val[pmic_mode_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_tool = result

        if index_tool >= len(pmic_mode_array):
            print("Index exceeds the length of the list")
        else:
            pmic_mode = pmic_mode_array[index_tool]
    def calculate_backlight_type(self,toolopt1):
        global backlight_type
        backlight_type_max_val = 33554432
        backlight_type_step_val = 1048576
        backlight_type_start_val = 0
        backlight_type_min_index = 1

        backlight_type_array = [
        "Direct",
        "EdgeLed",
        "Oled",
        "Direct_VI",
        "Direct_SKY",
        "MINI_LED",
        "MLS"
    ]
        backlight_type_val = [backlight_type_start_val + i * backlight_type_step_val for i in range((backlight_type_max_val - backlight_type_start_val)//backlight_type_step_val + 1)]
        backlight_type_data = list(zip(backlight_type_array, backlight_type_val))
        # print(backlight_type_data)
        mod_result = toolopt1 % backlight_type_max_val
        indirect_value = backlight_type_val[backlight_type_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_tool = result

        if index_tool >= len(backlight_type_array):
            print("Index exceeds the length of the list")
        else:
            backlight_type = backlight_type_array[index_tool]  
    def calculate_localdim_block(self,toolopt1):
        global localdim_block
        localdim_block_max_val = 1073741824
        localdim_block_step_val = 33554432
        localdim_block_start_val = 0
        localdim_block_min_index = 1

        localdim_block_array = [
            "off",
            "2", "6", "12", "40", "48", "50", "60",
            "90", "96", "108", "120", "144", "160", "180", "192",
            "208", "216", "225", "270", "288", "308",
            "504", "640", "720", "960", "1200", "1440", "1800", "1920", "2400"
        ]
        localdim_block_val = [localdim_block_start_val + i * localdim_block_step_val for i in range((localdim_block_max_val - localdim_block_start_val)//localdim_block_step_val + 1)]
        localdim_block_data = list(zip(localdim_block_array, localdim_block_val))
        # print(localdim_block_data)
        mod_result = toolopt1 % localdim_block_max_val
        indirect_value = localdim_block_val[localdim_block_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_tool = result

        if index_tool >= len(localdim_block_array):
            print("Index exceeds the length of the list")
        else:
            localdim_block = localdim_block_array[index_tool]
    def calculate_adjust_vcom(self,toolopt1):
        global adjust_vcom
        adjust_vcom_max_val = 1073741824
        adjust_vcom_step_val = 1073741824
        adjust_vcom_start_val = 0
        adjust_vcom_min_index = 1

        adjust_vcom_array = [
        "off", "on"
        ]
        adjust_vcom_val = [adjust_vcom_start_val + i * adjust_vcom_step_val for i in range((adjust_vcom_max_val - adjust_vcom_start_val)//adjust_vcom_step_val + 1)]
        adjust_vcom_data = list(zip(adjust_vcom_array, adjust_vcom_val))
        # print(adjust_vcom_data)
        indirect_value = adjust_vcom_val[adjust_vcom_min_index]
        result = toolopt1 // indirect_value
        # print(result)
        index_tool = result

        if index_tool >= len(adjust_vcom_array):
            print("Index exceeds the length of the list")
        else:
            adjust_vcom = adjust_vcom_array[index_tool]

class calculate_tooloption2():
    def __init__(self):
        self.toolopt2_run()
        pass
    def toolopt2_run(self):
        self.calculate_audiopw_volt(tooloption2)
        self.calculate_pwm2_duty(tooloption2)
        self.calculate_max_pwm(tooloption2)
        self.calculate_scanning_bl(tooloption2)
        self.calculate_bpl_type(tooloption2)
        self.calculate_powermode_select(tooloption2)
        self.calculate_eyesensor_gain(tooloption2)
        self.calculate_standard_backlight(tooloption2)
        self.calculate_vividsport_bl(tooloption2)
    def calculate_audiopw_volt(self,toolopt2):
        global audiopw_volt
        audiopw_volt_max_val = 8
        audiopw_volt_step_val = 1
        audiopw_volt_start_val = 0
        audiopw_volt_min_index = 1

        audiopw_volt_array = [
        "7V", "24V", "17V", "20V", "22V", "19V", "13V", "18V"
    ]
        audiopw_volt_val = [audiopw_volt_start_val + i * audiopw_volt_step_val for i in range((audiopw_volt_max_val - audiopw_volt_start_val)//audiopw_volt_step_val + 1)]
        audiopw_volt_data = list(zip(audiopw_volt_array, audiopw_volt_val))
        # print(audiopw_volt_data)
        mod_result = toolopt2 % audiopw_volt_max_val
        indirect_value = audiopw_volt_val[audiopw_volt_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_audiopw_volt = result

        if index_audiopw_volt >= len(audiopw_volt_array):
            print("Index exceeds the length of the list")
        else:
            audiopw_volt = audiopw_volt_array[index_audiopw_volt]
    def calculate_pwm2_duty(self,toolopt2):
        global pwm2_duty
        pwm2_duty_max_val = 64
        pwm2_duty_step_val = 8
        pwm2_duty_start_val = 0
        pwm2_duty_min_index = 1

        pwm2_duty_array = [
        "28", "34", "41", "47", "53", "59", "66", "72"
    ]
        pwm2_duty_val = [pwm2_duty_start_val + i * pwm2_duty_step_val for i in range((pwm2_duty_max_val - pwm2_duty_start_val)//pwm2_duty_step_val + 1)]
        pwm2_duty_data = list(zip(pwm2_duty_array, pwm2_duty_val))
        # print(pwm2_duty_data)
        mod_result = toolopt2 % pwm2_duty_max_val
        indirect_value = pwm2_duty_val[pwm2_duty_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_pwm2_duty = result

        if index_pwm2_duty >= len(pwm2_duty_array):
            print("Index exceeds the length of the list")
        else:
            pwm2_duty = pwm2_duty_array[index_pwm2_duty]
    def calculate_max_pwm(self,toolopt2):
        global max_pwm
        max_pwm_max_val = 1024
        max_pwm_step_val = 64
        max_pwm_start_val = 0
        max_pwm_min_index = 1

        max_pwm_array = [
        "default", "5per", "10per", "15per", "20per", "25per",
        "30per", "35per", "40per", "45per", "50per", "55per",
        "60per", "65per", "70per", "75per"
    ]
        max_pwm_val = [max_pwm_start_val + i * max_pwm_step_val for i in range((max_pwm_max_val - max_pwm_start_val)//max_pwm_step_val + 1)]
        max_pwm_data = list(zip(max_pwm_array, max_pwm_val))
        # print(max_pwm_data)
        mod_result = toolopt2 % max_pwm_max_val
        indirect_value = max_pwm_val[max_pwm_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_max_pwm = result

        if index_max_pwm >= len(max_pwm_array):
            print("Index exceeds the length of the list")
        else:
            max_pwm = max_pwm_array[index_max_pwm]
    def calculate_scanning_bl(self,toolopt2):
        global scanning_bl
        scanning_bl_max_val = 2048
        scanning_bl_step_val = 1024
        scanning_bl_start_val = 0
        scanning_bl_min_index = 1

        scanning_bl_array = [
        "off", "on"
    ]
        scanning_bl_val = [scanning_bl_start_val + i * scanning_bl_step_val for i in range((scanning_bl_max_val - scanning_bl_start_val)//scanning_bl_step_val + 1)]
        scanning_bl_data = list(zip(scanning_bl_array, scanning_bl_val))
        # print(scanning_bl_data)
        mod_result = toolopt2 % scanning_bl_max_val
        indirect_value = scanning_bl_val[scanning_bl_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_scanning_bl = result

        if index_scanning_bl >= len(scanning_bl_array):
            print("Index exceeds the length of the list")
        else:
            scanning_bl = scanning_bl_array[index_scanning_bl]
    def calculate_bpl_type(self,toolopt2):
        global bpl_type
        bpl_type_max_val = 16384
        bpl_type_step_val = 2048
        bpl_type_start_val = 0
        bpl_type_min_index = 1

        bpl_type_array = [
        "off", "120", "130", "110", "105", "98_LGD", "high BPL"
    ]
        bpl_type_val = [bpl_type_start_val + i * bpl_type_step_val for i in range((bpl_type_max_val - bpl_type_start_val)//bpl_type_step_val + 1)]
        bpl_type_data = list(zip(bpl_type_array, bpl_type_val))
        # print(bpl_type_data)
        mod_result = toolopt2 % bpl_type_max_val
        indirect_value = bpl_type_val[bpl_type_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_bpl_type = result

        if index_bpl_type >= len(bpl_type_array):
            print("Index exceeds the length of the list")
        else:
            bpl_type = bpl_type_array[index_bpl_type]
    def calculate_powermode_select(self,toolopt2):
        global powermode_select
        powermode_select_max_val = 65536
        powermode_select_step_val = 16384
        powermode_select_start_val = 0
        powermode_select_min_index = 1

        powermode_select_array = [
        "off", "", "mode 2", ""
    ]
        powermode_select_val = [powermode_select_start_val + i * powermode_select_step_val for i in range((powermode_select_max_val - powermode_select_start_val)//powermode_select_step_val + 1)]
        powermode_select_data = list(zip(powermode_select_array, powermode_select_val))
        # print(powermode_select_data)
        mod_result = toolopt2 % powermode_select_max_val
        indirect_value = powermode_select_val[powermode_select_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_powermode_select = result

        if index_powermode_select >= len(powermode_select_array):
            print("Index exceeds the length of the list")
        else:
            powermode_select = powermode_select_array[index_powermode_select]
    def calculate_eyesensor_gain(self,toolopt2):
        global eyesensor_gain
        eyesensor_gain_max_val = 4194304
        eyesensor_gain_step_val = 65536
        eyesensor_gain_start_val = 0
        eyesensor_gain_min_index = 1

        eyesensor_gain_array = [
        "-100Per", "-95Per", "-90Per", "-85Per", "-80Per", "-75Per",
        "-70Per", "-65Per", "-60Per", "-55Per", "-50Per", "-45Per",
        "-40Per", "-35Per", "-30Per", "-25Per", "-20Per", "-15Per",
        "-10Per", "-5Per", "default", "5Per", "10Per", "15Per",
        "20Per", "25Per", "30Per", "35Per", "40Per", "45Per",
        "50Per", "55Per", "60Per", "65Per", "70Per", "75Per",
        "80Per", "85Per", "90Per", "95Per", "100Per"
    ]
        eyesensor_gain_val = [eyesensor_gain_start_val + i * eyesensor_gain_step_val for i in range((eyesensor_gain_max_val - eyesensor_gain_start_val)//eyesensor_gain_step_val + 1)]
        eyesensor_gain_data = list(zip(eyesensor_gain_array, eyesensor_gain_val))
        # print(eyesensor_gain_data)
        mod_result = toolopt2 % eyesensor_gain_max_val
        indirect_value = eyesensor_gain_val[eyesensor_gain_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_eyesensor_gain = result

        if index_eyesensor_gain >= len(eyesensor_gain_array):
            print("Index exceeds the length of the list")
        else:
            eyesensor_gain = eyesensor_gain_array[index_eyesensor_gain]
    def calculate_standard_backlight(self,toolopt2):
        global standard_backlight
        standard_backlight_max_val = 134217728
        standard_backlight_step_val = 4194304
        standard_backlight_start_val = 0
        standard_backlight_min_index = 1

        standard_backlight_array = [
        "default", "95", "90", "85", "80", "75", "70", "65",
        "60", "55", "50", "45", "40", "35", "30", "25"
    ]
        standard_backlight_val = [standard_backlight_start_val + i * standard_backlight_step_val for i in range((standard_backlight_max_val - standard_backlight_start_val)//standard_backlight_step_val + 1)]
        standard_backlight_data = list(zip(standard_backlight_array, standard_backlight_val))
        # print(standard_backlight_data)
        mod_result = toolopt2 % standard_backlight_max_val
        indirect_value = standard_backlight_val[standard_backlight_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_standard_backlight = result

        if index_standard_backlight >= len(standard_backlight_array):
            print("Index exceeds the length of the list")
        else:
            standard_backlight = standard_backlight_array[index_standard_backlight]
    def calculate_vividsport_bl(self,toolopt2):
        global vividsports_bl
        vividsports_bl_max_val = 134217728
        vividsports_bl_step_val = 134217728
        vividsports_bl_start_val = 0
        vividsports_bl_min_index = 1

        vividsports_bl_array = [
        "default", "95", "90", "85", "80", "75", "70", "65", "60"
    ]
        vividsports_bl_val = [vividsports_bl_start_val + i * vividsports_bl_step_val for i in range((vividsports_bl_max_val - vividsports_bl_start_val)//vividsports_bl_step_val + 1)]
        vividsports_bl_data = list(zip(vividsports_bl_array, vividsports_bl_val))
        # print(vividsports_bl_data)
        indirect_value = vividsports_bl_val[vividsports_bl_min_index]
        result = toolopt2 // indirect_value
        # print(result)
        index_vividsports_bl = result

        if index_vividsports_bl >= len(vividsports_bl_array):
            print("Index exceeds the length of the list")
        else:
            vividsports_bl = vividsports_bl_array[index_vividsports_bl]

    """Calculations for Tool Option 3"""

class calculate_tooloption3():
    def __init__(self):
        self.toolopt3_run()
        pass
    def toolopt3_run(self):
        self.calculate_panelgamut_type(tooloption3)
        self.calculate_motionpro_mode(tooloption3)
        self.calculate_support_dolbyvisionhdr(tooloption3)
        self.calculate_ampchip_type(tooloption3)
        self.calculate_audiospk_watt(tooloption3)
        self.calculate_support_luminanceup(tooloption3)
        self.calculate_support_vrr(tooloption3)
        self.calculate_support_freesync(tooloption3)
        self.calculate_aisound_type(tooloption3)
        self.calculate_dolbyvison_precisiondetail(tooloption3)
        self.calculate_pwmfreq_double(tooloption3)
        self.calculate_motion_booster(tooloption3)
        self.calculate_oleddpc_type(tooloption3)
        self.calculate_support_freesyncpro(tooloption3) 
    def calculate_panelgamut_type(self,toolopt3):
        global panelgamut_type
        panelgamut_type_max_val = 8
        panelgamut_type_step_val = 1
        panelgamut_type_start_val = 0
        panelgamut_type_min_index = 1

        panelgamut_type_array = [
        "Normal", "WCG lcd", "led cw16"
    ]
        panelgamut_type_val = [panelgamut_type_start_val + i * panelgamut_type_step_val for i in range((panelgamut_type_max_val - panelgamut_type_start_val)//panelgamut_type_step_val + 1)]
        panelgamut_type_data = list(zip(panelgamut_type_array, panelgamut_type_val))
        # print(panelgamut_type_data)
        mod_result = toolopt3 % panelgamut_type_max_val
        indirect_value = panelgamut_type_val[panelgamut_type_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_panelgamut_type = result

        if index_panelgamut_type >= len(panelgamut_type_array):
            print("Index exceeds the length of the list")
        else:
            panelgamut_type = panelgamut_type_array[index_panelgamut_type]
    def calculate_motionpro_mode(self,toolopt3):
        global motionpro_mode
        motionpro_mode_max_val = 64
        motionpro_mode_step_val = 8
        motionpro_mode_start_val = 0
        motionpro_mode_min_index = 1

        motionpro_mode_array = [
        "off", "OLED Motion Pro", "OLED Motion", "LCD Motion Pro", "LCD Motion Pro Auto"
    ]
        motionpro_mode_val = [motionpro_mode_start_val + i * motionpro_mode_step_val for i in range((motionpro_mode_max_val - motionpro_mode_start_val)//motionpro_mode_step_val + 1)]
        motionpro_mode_data = list(zip(motionpro_mode_array, motionpro_mode_val))
        # print(motionpro_mode_data)
        mod_result = toolopt3 % motionpro_mode_max_val
        indirect_value = motionpro_mode_val[motionpro_mode_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_motionpro_mode = result

        if index_motionpro_mode >= len(motionpro_mode_array):
            print("Index exceeds the length of the list")
        else:
            motionpro_mode = motionpro_mode_array[index_motionpro_mode]
    def calculate_support_dolbyvisionhdr(self,toolopt3):
        global support_dolbyvisionhdr
        support_dolbyvisionhdr_max_val = 128
        support_dolbyvisionhdr_step_val = 64
        support_dolbyvisionhdr_start_val = 0
        support_dolbyvisionhdr_min_index = 1

        support_dolbyvisionhdr_array = [
        "off", "on"
    ]
        support_dolbyvisionhdr_val = [support_dolbyvisionhdr_start_val + i * support_dolbyvisionhdr_step_val for i in range((support_dolbyvisionhdr_max_val - support_dolbyvisionhdr_start_val)//support_dolbyvisionhdr_step_val + 1)]
        support_dolbyvisionhdr_data = list(zip(support_dolbyvisionhdr_array, support_dolbyvisionhdr_val))
        # print(support_dolbyvisionhdr_data)
        mod_result = toolopt3 % support_dolbyvisionhdr_max_val
        indirect_value = support_dolbyvisionhdr_val[support_dolbyvisionhdr_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_support_dolbyvisionhdr = result

        if index_support_dolbyvisionhdr >= len(support_dolbyvisionhdr_array):
            print("Index exceeds the length of the list")
        else:
            support_dolbyvisionhdr = support_dolbyvisionhdr_array[index_support_dolbyvisionhdr]
    def calculate_ampchip_type(self,toolopt3):
        global ampchip_type
        ampchip_type_max_val = 2048
        ampchip_type_step_val = 128
        ampchip_type_start_val = 0
        ampchip_type_min_index = 1

        ampchip_type_array = [
        "None", "1amp", "2amp", "3amp", "4amp", "5amp", "6amp",
        "on"
    ]
        ampchip_type_val = [ampchip_type_start_val + i * ampchip_type_step_val for i in range((ampchip_type_max_val - ampchip_type_start_val)//ampchip_type_step_val + 1)]
        ampchip_type_data = list(zip(ampchip_type_array, ampchip_type_val))
        # print(ampchip_type_data)
        mod_result = toolopt3 % ampchip_type_max_val
        indirect_value = ampchip_type_val[ampchip_type_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_ampchip_type = result

        if index_ampchip_type >= len(ampchip_type_array):
            print("Index exceeds the length of the list")
        else:
            ampchip_type = ampchip_type_array[index_ampchip_type]
    def calculate_audiospk_watt(self,toolopt3):
        global audiospk_watt
        audiospk_watt_max_val = 32768
        audiospk_watt_step_val = 2048
        audiospk_watt_start_val = 0
        audiospk_watt_min_index = 1

        audiospk_watt_array = [
        "20W", "10W", "15W", "5W", "7W"
    ]
        audiospk_watt_val = [audiospk_watt_start_val + i * audiospk_watt_step_val for i in range((audiospk_watt_max_val - audiospk_watt_start_val)//audiospk_watt_step_val + 1)]
        audiospk_watt_data = list(zip(audiospk_watt_array, audiospk_watt_val))
        # print(audiospk_watt_data)
        mod_result = toolopt3 % audiospk_watt_max_val
        indirect_value = audiospk_watt_val[audiospk_watt_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_audiospk_watt = result

        if index_audiospk_watt >= len(audiospk_watt_array):
            print("Index exceeds the length of the list")
        else:
            audiospk_watt = audiospk_watt_array[index_audiospk_watt]
    def calculate_support_luminanceup(self,toolopt3):
        global support_luminanceup
        support_luminanceup_max_val = 65536
        support_luminanceup_step_val = 32768
        support_luminanceup_start_val = 0
        support_luminanceup_min_index = 1

        support_luminanceup_array = [
        "off", "on"
    ]
        support_luminanceup_val = [support_luminanceup_start_val + i * support_luminanceup_step_val for i in range((support_luminanceup_max_val - support_luminanceup_start_val)//support_luminanceup_step_val + 1)]
        support_luminanceup_data = list(zip(support_luminanceup_array, support_luminanceup_val))
        # print(support_luminanceup_data)
        mod_result = toolopt3 % support_luminanceup_max_val
        indirect_value = support_luminanceup_val[support_luminanceup_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_support_luminanceup = result

        if index_support_luminanceup >= len(support_luminanceup_array):
            print("Index exceeds the length of the list")
        else:
            support_luminanceup = support_luminanceup_array[index_support_luminanceup]
    def calculate_support_vrr(self,toolopt3):
        global support_vrr
        support_vrr_max_val = 524288
        support_vrr_step_val = 65536
        support_vrr_start_val = 0
        support_vrr_min_index = 1

        support_vrr_array = [
        "VRR_off", "VRR_on", "Gsync"
    ]
        support_vrr_val = [support_vrr_start_val + i * support_vrr_step_val for i in range((support_vrr_max_val - support_vrr_start_val)//support_vrr_step_val + 1)]
        support_vrr_data = list(zip(support_vrr_array, support_vrr_val))
        # print(support_vrr_data)
        mod_result = toolopt3 % support_vrr_max_val
        indirect_value = support_vrr_val[support_vrr_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_support_vrr = result

        if index_support_vrr >= len(support_vrr_array):
            print("Index exceeds the length of the list")
        else:
            support_vrr = support_vrr_array[index_support_vrr]
    def calculate_support_freesync(self,toolopt3):
        global support_freesync
        support_freesync_max_val = 1048576
        support_freesync_step_val = 524288
        support_freesync_start_val = 0
        support_freesync_min_index = 1

        support_freesync_array = [
        "off", "on"
    ]
        support_freesync_val = [support_freesync_start_val + i * support_freesync_step_val for i in range((support_freesync_max_val - support_freesync_start_val)//support_freesync_step_val + 1)]
        support_freesync_data = list(zip(support_freesync_array, support_freesync_val))
        # print(support_freesync_data)
        mod_result = toolopt3 % support_freesync_max_val
        indirect_value = support_freesync_val[support_freesync_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_support_freesync = result

        if index_support_freesync >= len(support_freesync_array):
            print("Index exceeds the length of the list")
        else:
            support_freesync = support_freesync_array[index_support_freesync]
    def calculate_aisound_type(self,toolopt3):
        global aisound_type
        aisound_type_max_val = 2097152
        aisound_type_step_val = 1048576
        aisound_type_start_val = 0
        aisound_type_min_index = 1

        aisound_type_array = [
        "Basic", "Pro"
    ]
        aisound_type_val = [aisound_type_start_val + i * aisound_type_step_val for i in range((aisound_type_max_val - aisound_type_start_val)//aisound_type_step_val + 1)]
        aisound_type_data = list(zip(aisound_type_array, aisound_type_val))
        # print(aisound_type_data)
        mod_result = toolopt3 % aisound_type_max_val
        indirect_value = aisound_type_val[aisound_type_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_aisound_type = result

        if index_aisound_type >= len(aisound_type_array):
            print("Index exceeds the length of the list")
        else:
            aisound_type = aisound_type_array[index_aisound_type]
    def calculate_dolbyvison_precisiondetail(self,toolopt3):
        global dolbyvison_precisiondetail
        dolbyvison_precisiondetail_max_val = 4194304
        dolbyvison_precisiondetail_step_val = 2097152
        dolbyvison_precisiondetail_start_val = 0
        dolbyvison_precisiondetail_min_index = 1

        dolbyvison_precisiondetail_array = [
        "off", "on"
    ]
        dolbyvison_precisiondetail_val = [dolbyvison_precisiondetail_start_val + i * dolbyvison_precisiondetail_step_val for i in range((dolbyvison_precisiondetail_max_val - dolbyvison_precisiondetail_start_val)//dolbyvison_precisiondetail_step_val + 1)]
        dolbyvison_precisiondetail_data = list(zip(dolbyvison_precisiondetail_array, dolbyvison_precisiondetail_val))
        # print(dolbyvison_precisiondetail_data)
        mod_result = toolopt3 % dolbyvison_precisiondetail_max_val
        indirect_value = dolbyvison_precisiondetail_val[dolbyvison_precisiondetail_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_dolbyvison_precisiondetail = result

        if index_dolbyvison_precisiondetail >= len(dolbyvison_precisiondetail_array):
            print("Index exceeds the length of the list")
        else:
            dolbyvison_precisiondetail = dolbyvison_precisiondetail_array[index_dolbyvison_precisiondetail]
    def calculate_pwmfreq_double(self,toolopt3):
        global pwmfreq_double
        pwmfreq_double_max_val = 8388608
        pwmfreq_double_step_val = 4194304
        pwmfreq_double_start_val = 0
        pwmfreq_double_min_index = 1

        pwmfreq_double_array = [
        "off", "on"
    ]
        pwmfreq_double_val = [pwmfreq_double_start_val + i * pwmfreq_double_step_val for i in range((pwmfreq_double_max_val - pwmfreq_double_start_val)//pwmfreq_double_step_val + 1)]
        pwmfreq_double_data = list(zip(pwmfreq_double_array, pwmfreq_double_val))
        # print(pwmfreq_double_data)
        mod_result = toolopt3 % pwmfreq_double_max_val
        indirect_value = pwmfreq_double_val[pwmfreq_double_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_pwmfreq_double = result

        if index_pwmfreq_double >= len(pwmfreq_double_array):
            print("Index exceeds the length of the list")
        else:
            pwmfreq_double = pwmfreq_double_array[index_pwmfreq_double]
    def calculate_motion_booster(self,toolopt3):
        global motion_booster
        motion_booster_max_val = 16777216
        motion_booster_step_val = 8388608
        motion_booster_start_val = 0
        motion_booster_min_index = 1

        motion_booster_array = [
        "off", "on"
    ]
        motion_booster_val = [motion_booster_start_val + i * motion_booster_step_val for i in range((motion_booster_max_val - motion_booster_start_val)//motion_booster_step_val + 1)]
        motion_booster_data = list(zip(motion_booster_array, motion_booster_val))
        # print(motion_booster_data)
        mod_result = toolopt3 % motion_booster_max_val
        indirect_value = motion_booster_val[motion_booster_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_motion_booster = result

        if index_motion_booster >= len(motion_booster_array):
            print("Index exceeds the length of the list")
        else:
            motion_booster = motion_booster_array[index_motion_booster]
    def calculate_oleddpc_type(self,toolopt3):
        global oleddpc_type
        oleddpc_type_max_val = 67108864
        oleddpc_type_step_val = 16777216
        oleddpc_type_start_val = 0
        oleddpc_type_min_index = 1

        oleddpc_type_array = [
        "off", "W-DPC", "Adaptive DPC"
        ]
        oleddpc_type_val = [oleddpc_type_start_val + i * oleddpc_type_step_val for i in range((oleddpc_type_max_val - oleddpc_type_start_val)//oleddpc_type_step_val + 1)]
        oleddpc_type_data = list(zip(oleddpc_type_array, oleddpc_type_val))
        # print(oleddpc_type_data)
        mod_result = toolopt3 % oleddpc_type_max_val
        indirect_value = oleddpc_type_val[oleddpc_type_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_oleddpc_type = result

        if index_oleddpc_type >= len(oleddpc_type_array):
            print("Index exceeds the length of the list")
        else:
            oleddpc_type = oleddpc_type_array[index_oleddpc_type]
    def calculate_support_freesyncpro(self,toolopt3):
        global support_freesyncpro
        support_freesyncpro_max_val = 67108864
        support_freesyncpro_step_val = 67108864
        support_freesyncpro_start_val = 0
        support_freesyncpro_min_index = 1

        support_freesyncpro_array = [
        "off", "on"  
    ]
        support_freesyncpro_val = [support_freesyncpro_start_val + i * support_freesyncpro_step_val for i in range((support_freesyncpro_max_val - support_freesyncpro_start_val)//support_freesyncpro_step_val + 1)]
        support_freesyncpro_data = list(zip(support_freesyncpro_array, support_freesyncpro_val))
        # print(support_freesyncpro_data)
        indirect_value = support_freesyncpro_val[support_freesyncpro_min_index]
        result = toolopt3 // indirect_value
        # print(result)
        index_support_freesyncpro = result

        if index_support_freesyncpro >= len(support_freesyncpro_array):
            print("Index exceeds the length of the list")
        else:
            support_freesyncpro = support_freesyncpro_array[index_support_freesyncpro]

class calculate_tooloption4():
    def __init__(self):
        self.toolopt4_run()
        pass
    def toolopt4_run(self):
        self.calculate_logo_light(tooloption4)
        self.calculate_support_fancontrol(tooloption4)
        self.calculate_camera_type(tooloption4)
        self.calculate_support_wol(tooloption4)
        self.calculate_hdmiswitch_type(tooloption4)
        self.calculate_moving_speaker(tooloption4)
        self.calculate_support_irblaster(tooloption4)
        self.calculate_mirror_mode(tooloption4)
        self.calculate_screenroller_motor(tooloption4)
        self.calculate_motiondetect_sensor(tooloption4)
        self.calculate_lcdscreen_cooling(tooloption4)
        self.calculate_support_lan(tooloption4)
        self.calculate_special_edition(tooloption4)
        self.calculate_optical_jack(tooloption4)
        self.calculate_farfield_voice(tooloption4)
        self.calculate_type_cctric(tooloption4)
        self.calculate_aiart_extension(tooloption4)
        self.calculate_board_design(tooloption4)
        self.calculate_emmc_density(tooloption4)
    def calculate_logo_light(self,toolopt4):
        global logo_light
        logo_light_max_val = 2
        logo_light_step_val = 1
        logo_light_start_val = 0
        logo_light_min_index = 1

        logo_light_array = [
        "off", "on"
    ]
        logo_light_val = [logo_light_start_val + i * logo_light_step_val for i in range((logo_light_max_val - logo_light_start_val)//logo_light_step_val + 1)]
        logo_light_data = list(zip(logo_light_array, logo_light_val))
        # print(logo_light_data)
        mod_result = toolopt4 % logo_light_max_val
        indirect_value = logo_light_val[logo_light_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_logo_light = result

        if index_logo_light >= len(logo_light_array):
            print("Index exceeds the length of the list")
        else:
            logo_light = logo_light_array[index_logo_light]
    def calculate_support_fancontrol(self,toolopt4):
        global support_fancontrol
        support_fancontrol_max_val = 4
        support_fancontrol_step_val = 2
        support_fancontrol_start_val = 0
        support_fancontrol_min_index = 1

        support_fancontrol_array = [
        "off", "on"
    ]
        support_fancontrol_val = [support_fancontrol_start_val + i * support_fancontrol_step_val for i in range((support_fancontrol_max_val - support_fancontrol_start_val)//support_fancontrol_step_val + 1)]
        support_fancontrol_data = list(zip(support_fancontrol_array, support_fancontrol_val))
        # print(support_fancontrol_data)
        mod_result = toolopt4 % support_fancontrol_max_val
        indirect_value = support_fancontrol_val[support_fancontrol_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_support_fancontrol = result

        if index_support_fancontrol >= len(support_fancontrol_array):
            print("Index exceeds the length of the list")
        else:
            support_fancontrol = support_fancontrol_array[index_support_fancontrol]
    def calculate_camera_type(self,toolopt4):
        global camera_type
        camera_type_max_val = 16
        camera_type_step_val = 4
        camera_type_start_val = 0
        camera_type_min_index = 1

        camera_type_array = [
        "Not support", "Ready", "Builtin", "Both"
    ]
        camera_type_val = [camera_type_start_val + i * camera_type_step_val for i in range((camera_type_max_val - camera_type_start_val)//camera_type_step_val + 1)]
        camera_type_data = list(zip(camera_type_array, camera_type_val))
        # print(camera_type_data)
        mod_result = toolopt4 % camera_type_max_val
        indirect_value = camera_type_val[camera_type_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_camera_type = result

        if index_camera_type >= len(camera_type_array):
            print("Index exceeds the length of the list")
        else:
            camera_type = camera_type_array[index_camera_type]
        support_fancontrol_max_val = 4
        support_fancontrol_step_val = 2
        support_fancontrol_start_val = 0
        support_fancontrol_min_index = 1

        support_fancontrol_array = [
        "off", "on"
        ]
        support_fancontrol_val = [support_fancontrol_start_val + i * support_fancontrol_step_val for i in range((support_fancontrol_max_val - support_fancontrol_start_val)//support_fancontrol_step_val + 1)]
        support_fancontrol_data = list(zip(support_fancontrol_array, support_fancontrol_val))
        # print(support_fancontrol_data)
        mod_result = toolopt4 % support_fancontrol_max_val
        indirect_value = support_fancontrol_val[support_fancontrol_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_support_fancontrol = result

        if index_support_fancontrol >= len(support_fancontrol_array):
            print("Index exceeds the length of the list")
        else:
            support_fancontrol = support_fancontrol_array[index_support_fancontrol]
    def calculate_support_wol(self,toolopt4):
        global support_wol
        support_wol_max_val = 32
        support_wol_step_val = 16
        support_wol_start_val = 0
        support_wol_min_index = 1

        support_wol_array = [
        "off", "on"
    ]
        support_wol_val = [support_wol_start_val + i * support_wol_step_val for i in range((support_wol_max_val - support_wol_start_val)//support_wol_step_val + 1)]
        support_wol_data = list(zip(support_wol_array, support_wol_val))
        # print(support_wol_data)
        mod_result = toolopt4 % support_wol_max_val
        indirect_value = support_wol_val[support_wol_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_support_wol = result

        if index_support_wol >= len(support_wol_array):
            print("Index exceeds the length of the list")
        else:
            support_wol = support_wol_array[index_support_wol]
    def calculate_hdmiswitch_type(self,toolopt4):
        global hdmiswitch_type
        hdmiswitch_type_max_val = 256
        hdmiswitch_type_step_val = 32
        hdmiswitch_type_start_val = 0
        hdmiswitch_type_min_index = 1

        hdmiswitch_type_array = [
        "None", "Hawk2"    
    ]
        hdmiswitch_type_val = [hdmiswitch_type_start_val + i * hdmiswitch_type_step_val for i in range((hdmiswitch_type_max_val - hdmiswitch_type_start_val)//hdmiswitch_type_step_val + 1)]
        hdmiswitch_type_data = list(zip(hdmiswitch_type_array, hdmiswitch_type_val))
        # print(hdmiswitch_type_data)
        mod_result = toolopt4 % hdmiswitch_type_max_val
        indirect_value = hdmiswitch_type_val[hdmiswitch_type_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_hdmiswitch_type = result

        if index_hdmiswitch_type >= len(hdmiswitch_type_array):
            print("Index exceeds the length of the list")
        else:
            hdmiswitch_type = hdmiswitch_type_array[index_hdmiswitch_type]
    def calculate_moving_speaker(self,toolopt4):
        global moving_speaker
        moving_speaker_max_val = 512
        moving_speaker_step_val = 256
        moving_speaker_start_val = 0
        moving_speaker_min_index = 1

        moving_speaker_array = [
        "off", "on"
    ]
        moving_speaker_val = [moving_speaker_start_val + i * moving_speaker_step_val for i in range((moving_speaker_max_val - moving_speaker_start_val)//moving_speaker_step_val + 1)]
        moving_speaker_data = list(zip(moving_speaker_array, moving_speaker_val))
        # print(moving_speaker_data)
        mod_result = toolopt4 % moving_speaker_max_val
        indirect_value = moving_speaker_val[moving_speaker_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_moving_speaker = result

        if index_moving_speaker >= len(moving_speaker_array):
            print("Index exceeds the length of the list")
        else:
            moving_speaker = moving_speaker_array[index_moving_speaker]
    def calculate_support_irblaster(self,toolopt4):
        global support_irblaster
        support_irblaster_max_val = 1024
        support_irblaster_step_val = 512
        support_irblaster_start_val = 0
        support_irblaster_min_index = 1

        support_irblaster_array = [
        "off", "on"
    ]
        support_irblaster_val = [support_irblaster_start_val + i * support_irblaster_step_val for i in range((support_irblaster_max_val - support_irblaster_start_val)//support_irblaster_step_val + 1)]
        support_irblaster_data = list(zip(support_irblaster_array, support_irblaster_val))
        # print(support_irblaster_data)
        mod_result = toolopt4 % support_irblaster_max_val
        indirect_value = support_irblaster_val[support_irblaster_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_support_irblaster = result

        if index_support_irblaster >= len(support_irblaster_array):
            print("Index exceeds the length of the list")
        else:
            support_irblaster = support_irblaster_array[index_support_irblaster]
    def calculate_mirror_mode(self,toolopt4):
        global mirror_mode
        mirror_mode_max_val = 2048
        mirror_mode_step_val = 1024
        mirror_mode_start_val = 0
        mirror_mode_min_index = 1

        mirror_mode_array = [
        "off", "on"
    ]
        mirror_mode_val = [mirror_mode_start_val + i * mirror_mode_step_val for i in range((mirror_mode_max_val - mirror_mode_start_val)//mirror_mode_step_val + 1)]
        mirror_mode_data = list(zip(mirror_mode_array, mirror_mode_val))
        # print(mirror_mode_data)
        mod_result = toolopt4 % mirror_mode_max_val
        indirect_value = mirror_mode_val[mirror_mode_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_mirror_mode = result

        if index_mirror_mode >= len(mirror_mode_array):
            print("Index exceeds the length of the list")
        else:
            mirror_mode = mirror_mode_array[index_mirror_mode]
    def calculate_screenroller_motor(self,toolopt4):
        global screenroller_motor
        screenroller_motor_max_val = 4096
        screenroller_motor_step_val = 2048
        screenroller_motor_start_val = 0
        screenroller_motor_min_index = 1

        screenroller_motor_array = [
        "off", "on"
    ]
        screenroller_motor_val = [screenroller_motor_start_val + i * screenroller_motor_step_val for i in range((screenroller_motor_max_val - screenroller_motor_start_val)//screenroller_motor_step_val + 1)]
        screenroller_motor_data = list(zip(screenroller_motor_array, screenroller_motor_val))
        # print(screenroller_motor_data)
        mod_result = toolopt4 % screenroller_motor_max_val
        indirect_value = screenroller_motor_val[screenroller_motor_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_screenroller_motor = result

        if index_screenroller_motor >= len(screenroller_motor_array):
            print("Index exceeds the length of the list")
        else:
            screenroller_motor = screenroller_motor_array[index_screenroller_motor]
    def calculate_motiondetect_sensor(self,toolopt4):
        global motiondetect_sensor
        motiondetect_sensor_max_val = 16384
        motiondetect_sensor_step_val = 4096
        motiondetect_sensor_start_val = 0
        motiondetect_sensor_min_index = 1

        motiondetect_sensor_array = [
        "off", "ToF_TBD_22Y", "CAM_ART&R2_21Y"
    ]
        motiondetect_sensor_val = [motiondetect_sensor_start_val + i * motiondetect_sensor_step_val for i in range((motiondetect_sensor_max_val - motiondetect_sensor_start_val)//motiondetect_sensor_step_val + 1)]
        motiondetect_sensor_data = list(zip(motiondetect_sensor_array, motiondetect_sensor_val))
        # print(motiondetect_sensor_data)
        mod_result = toolopt4 % motiondetect_sensor_max_val
        indirect_value = motiondetect_sensor_val[motiondetect_sensor_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_motiondetect_sensor = result

        if index_motiondetect_sensor >= len(motiondetect_sensor_array):
            print("Index exceeds the length of the list")
        else:
            motiondetect_sensor = motiondetect_sensor_array[index_motiondetect_sensor]
    def calculate_lcdscreen_cooling(self,toolopt4):
        global lcdscreen_cooling
        lcdscreen_cooling_max_val = 131072
        lcdscreen_cooling_step_val = 16384
        lcdscreen_cooling_start_val = 0
        lcdscreen_cooling_min_index = 1

        lcdscreen_cooling_array = [
        "off", "Step1", "Step2", "Step3", "Step4", "Step5", "Step6", "Step7"
    ]
        lcdscreen_cooling_val = [lcdscreen_cooling_start_val + i * lcdscreen_cooling_step_val for i in range((lcdscreen_cooling_max_val - lcdscreen_cooling_start_val)//lcdscreen_cooling_step_val + 1)]
        lcdscreen_cooling_data = list(zip(lcdscreen_cooling_array, lcdscreen_cooling_val))
        # print(lcdscreen_cooling_data)
        mod_result = toolopt4 % lcdscreen_cooling_max_val
        indirect_value = lcdscreen_cooling_val[lcdscreen_cooling_min_index]
        result = mod_result // indirect_value
        # print(result)
        index_lcdscreen_cooling = result

        if index_lcdscreen_cooling >= len(lcdscreen_cooling_array):
            print("Index exceeds the length of the list")
        else:
            lcdscreen_cooling = lcdscreen_cooling_array[index_lcdscreen_cooling]
    def calculate_support_lan(self,toolopt4):
        global support_lan
        support_lan_max_val = 262144
        support_lan_step_val = 131072
        support_lan_start_val = 0
        support_lan_min_index = 1

        support_lan_array = [
        "on", "off"
    ]
        support_lan_val = [support_lan_start_val + i * support_lan_step_val for i in range((support_lan_max_val - support_lan_start_val)//support_lan_step_val + 1)]
        support_lan_data = list(zip(support_lan_array, support_lan_val))
        # print(support_lan_data)
        mod_result = toolopt4 % support_lan_max_val
        indirect_value = support_lan_val[support_lan_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_support_lan = result

        if index_support_lan >= len(support_lan_array):
            print("Index exceeds the length of the list")
        else:
            support_lan = support_lan_array[index_support_lan]
    def calculate_special_edition(self,toolopt4):
        global special_edition
        special_edition_max_val = 2097152
        special_edition_step_val = 262144
        special_edition_start_val = 0
        special_edition_min_index = 1

        special_edition_array = [
        "off", "Starwars", "Twins_23", "Senior", "Club", "Picture & Sound"
    ]
        special_edition_val = [special_edition_start_val + i * special_edition_step_val for i in range((special_edition_max_val - special_edition_start_val)//special_edition_step_val + 1)]
        special_edition_data = list(zip(special_edition_array, special_edition_val))
        # print(special_edition_data)
        mod_result = toolopt4 % special_edition_max_val
        indirect_value = special_edition_val[special_edition_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_special_edition = result

        if index_special_edition >= len(special_edition_array):
            print("Index exceeds the length of the list")
        else:
            special_edition = special_edition_array[index_special_edition]
    def calculate_optical_jack(self,toolopt4):
        global optical_jack
        optical_jack_max_val = 4194304
        optical_jack_step_val = 2097152
        optical_jack_start_val = 0
        optical_jack_min_index = 1

        optical_jack_array = [
        "on", "off"  
    ]
        optical_jack_val = [optical_jack_start_val + i * optical_jack_step_val for i in range((optical_jack_max_val - optical_jack_start_val)//optical_jack_step_val + 1)]
        optical_jack_data = list(zip(optical_jack_array, optical_jack_val))
        # print(optical_jack_data)
        mod_result = toolopt4 % optical_jack_max_val
        indirect_value = optical_jack_val[optical_jack_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_optical_jack = result

        if index_optical_jack >= len(optical_jack_array):
            print("Index exceeds the length of the list")
        else:
            optical_jack = optical_jack_array[index_optical_jack]
    def calculate_farfield_voice(self,toolopt4):
        global farfield_voice
        farfield_voice_max_val = 16777216
        farfield_voice_step_val = 4194304
        farfield_voice_start_val = 0
        farfield_voice_min_index = 1

        farfield_voice_array = [
        "off", "On with switch", "On without switch"
    ]
        farfield_voice_val = [farfield_voice_start_val + i * farfield_voice_step_val for i in range((farfield_voice_max_val - farfield_voice_start_val)//farfield_voice_step_val + 1)]
        farfield_voice_data = list(zip(farfield_voice_array, farfield_voice_val))
        # print(farfield_voice_data)
        mod_result = toolopt4 % farfield_voice_max_val
        indirect_value = farfield_voice_val[farfield_voice_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_farfield_voice = result

        if index_farfield_voice >= len(farfield_voice_array):
            print("Index exceeds the length of the list")
        else:
            farfield_voice = farfield_voice_array[index_farfield_voice]
    def calculate_type_cctric(self,toolopt4):
        global type_cctric
        type_cctric_max_val = 67108864
        type_cctric_step_val = 16777216
        type_cctric_start_val = 0
        type_cctric_min_index = 1

        type_cctric_array = [
        "None", "RTS5450M", "Builtin", "RTS5453P"
    ]
        type_cctric_val = [type_cctric_start_val + i * type_cctric_step_val for i in range((type_cctric_max_val - type_cctric_start_val)//type_cctric_step_val + 1)]
        type_cctric_data = list(zip(type_cctric_array, type_cctric_val))
        # print(type_cctric_data)
        mod_result = toolopt4 % type_cctric_max_val
        indirect_value = type_cctric_val[type_cctric_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_type_cctric = result

        if index_type_cctric >= len(type_cctric_array):
            print("Index exceeds the length of the list")
        else:
            type_cctric = type_cctric_array[index_type_cctric]
    def calculate_aiart_extension(self,toolopt4):
        global aiart_extension
        aiart_extension_max_val = 134217728
        aiart_extension_step_val = 67108864
        aiart_extension_start_val = 0
        aiart_extension_min_index = 1

        aiart_extension_array = [
        "off", "on"
    ]
        aiart_extension_val = [aiart_extension_start_val + i * aiart_extension_step_val for i in range((aiart_extension_max_val - aiart_extension_start_val)//aiart_extension_step_val + 1)]
        aiart_extension_data = list(zip(aiart_extension_array, aiart_extension_val))
        # print(aiart_extension_data)
        mod_result = toolopt4 % aiart_extension_max_val
        indirect_value = aiart_extension_val[aiart_extension_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_aiart_extension = result

        if index_aiart_extension >= len(aiart_extension_array):
            print("Index exceeds the length of the list")
        else:
            aiart_extension = aiart_extension_array[index_aiart_extension]
    def calculate_board_design(self,toolopt4):
        global board_design
        board_design_max_val = 402653184
        board_design_step_val = 134217728
        board_design_start_val = 0
        board_design_min_index = 1

        board_design_array = [
        "L", "C", "T"
    ]
        board_design_val = [board_design_start_val + i * board_design_step_val for i in range((board_design_max_val - board_design_start_val)//board_design_step_val + 1)]
        board_design_data = list(zip(board_design_array, board_design_val))
        # print(board_design_data)
        mod_result = toolopt4 % board_design_max_val
        indirect_value = board_design_val[board_design_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_board_design = result

        if index_board_design >= len(board_design_array):
            print("Index exceeds the length of the list")
        else:
            board_design = board_design_array[index_board_design]
    def calculate_emmc_density(self,toolopt4):
        global emmc_density
        emmc_density_max_val = 402653184
        emmc_density_step_val = 402653184
        emmc_density_start_val = 0
        emmc_density_min_index = 1

        emmc_density_array = [
        "off", "on"
        ]
        emmc_density_val = [emmc_density_start_val + i * emmc_density_step_val for i in range((emmc_density_max_val - emmc_density_start_val)//emmc_density_step_val + 1)]
        emmc_density_data = list(zip(emmc_density_array, emmc_density_val))
        # print(emmc_density_data)
        indirect_value = emmc_density_val[emmc_density_min_index]

        result = toolopt4 // indirect_value
        # print(result)
        index_emmc_density = result

        if index_emmc_density >= len(emmc_density_array):
            print("Index exceeds the length of the list")
        else:
            emmc_density = emmc_density_array[index_emmc_density]

class calculate_tooloption5():
    def __init__(self):
        self.toolopt5_run()
        pass
    def toolopt5_run(self):
        self.calculate_videoadc_index(tooloption5)
        self.calculate_audioadc_index(tooloption5)
        self.calculate_usb_count(tooloption5)
        self.calculate_usb_1(tooloption5)
        self.calculate_usb_2(tooloption5)
        self.calculate_usb_3(tooloption5)
        self.calculate_support_headphone(tooloption5)
        self.calculate_ciap_key(tooloption5)
        self.calculate_dtcpap_key(tooloption5)
        self.calculate_macap_key(tooloption5)
        self.calculate_esnap_key(tooloption5)
        self.calculate_widevineap_key(tooloption5)
        self.calculate_ciecpap_key(tooloption5)
        self.calculate_atsc30_key(tooloption5)
        self.calculate_new_erp(tooloption5)
        self.calculate_oled_cpc(tooloption5)
        self.calculate_pd_charge(tooloption5)
    def calculate_videoadc_index(self,toolopt5):
        global videoadc_index
        videoadc_index_max_val = 16
        videoadc_index_step_val = 1
        videoadc_index_start_val = 0
        videoadc_index_min_index = 1

        videoadc_index_array = [
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"
    ]
        videoadc_index_val = [videoadc_index_start_val + i * videoadc_index_step_val for i in range((videoadc_index_max_val - videoadc_index_start_val)//videoadc_index_step_val + 1)]
        videoadc_index_data = list(zip(videoadc_index_array, videoadc_index_val))
        # print(videoadc_index_data)
        mod_result = toolopt5 % videoadc_index_max_val
        indirect_value = videoadc_index_val[videoadc_index_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_videoadc_index = result

        if index_videoadc_index >= len(videoadc_index_array):
            print("Index exceeds the length of the list")
        else:
            videoadc_index = videoadc_index_array[index_videoadc_index]
    def calculate_audioadc_index(self,toolopt5):
        global audioadc_index
        audioadc_index_max_val = 256
        audioadc_index_step_val = 16
        audioadc_index_start_val = 0
        audioadc_index_min_index = 1

        audioadc_index_array = [
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"
    ]
        audioadc_index_val = [audioadc_index_start_val + i * audioadc_index_step_val for i in range((audioadc_index_max_val - audioadc_index_start_val)//audioadc_index_step_val + 1)]
        audioadc_index_data = list(zip(audioadc_index_array, audioadc_index_val))
        # print(audioadc_index_data)
        mod_result = toolopt5 % audioadc_index_max_val
        indirect_value = audioadc_index_val[audioadc_index_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_audioadc_index = result

        if index_audioadc_index >= len(audioadc_index_array):
            print("Index exceeds the length of the list")
        else:
            audioadc_index = audioadc_index_array[index_audioadc_index]
    def calculate_usb_count(self,toolopt5):
        global usb_count
        usb_count_max_val = 1024
        usb_count_step_val = 256
        usb_count_start_val = 0
        usb_count_min_index = 1

        usb_count_array = [
        "1", "2", "3", "4"
    ]
        usb_count_val = [usb_count_start_val + i * usb_count_step_val for i in range((usb_count_max_val - usb_count_start_val)//usb_count_step_val + 1)]
        usb_count_data = list(zip(usb_count_array, usb_count_val))
        # print(usb_count_data)
        mod_result = toolopt5 % usb_count_max_val
        indirect_value = usb_count_val[usb_count_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_usb_count = result

        if index_usb_count >= len(usb_count_array):
            print("Index exceeds the length of the list")
        else:
            usb_count = usb_count_array[index_usb_count]
    def calculate_usb_1(self,toolopt5):
        global usb_1
        usb_1_max_val = 4096
        usb_1_step_val = 1024
        usb_1_start_val = 0
        usb_1_min_index = 1

        usb_1_array = [
        "usb_none", "usb ctl1", "usb ctl2", "usb ctl3"
    ]
        usb_1_val = [usb_1_start_val + i * usb_1_step_val for i in range((usb_1_max_val - usb_1_start_val)//usb_1_step_val + 1)]
        usb_1_data = list(zip(usb_1_array, usb_1_val))
        # print(usb_1_data)
        mod_result = toolopt5 % usb_1_max_val
        indirect_value = usb_1_val[usb_1_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_usb_1 = result

        if index_usb_1 >= len(usb_1_array):
            print("Index exceeds the length of the list")
        else:
            usb_1 = usb_1_array[index_usb_1]
    def calculate_usb_2(self,toolopt5):
        global usb_2
        usb_2_max_val = 16384
        usb_2_step_val = 4096
        usb_2_start_val = 0
        usb_2_min_index = 1

        usb_2_array = [
        "usb none", "usb ctl1", "usb ctl2", "usb ctl3"  
    ]
        usb_2_val = [usb_2_start_val + i * usb_2_step_val for i in range((usb_2_max_val - usb_2_start_val)//usb_2_step_val + 1)]
        usb_2_data = list(zip(usb_2_array, usb_2_val))
        # print(usb_2_data)
        mod_result = toolopt5 % usb_2_max_val
        indirect_value = usb_2_val[usb_2_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_usb_2 = result

        if index_usb_2 >= len(usb_2_array):
            print("Index exceeds the length of the list")
        else:
            usb_2 = usb_2_array[index_usb_2]
    def calculate_usb_3(self,toolopt5):
        global usb_3
        usb_3_max_val = 65536
        usb_3_step_val = 16384
        usb_3_start_val = 0
        usb_3_min_index = 1

        usb_3_array = [
        "usb none", "usb ctl1", "usb ctl2", "usb ctl3"  
    ]
        usb_3_val = [usb_3_start_val + i * usb_3_step_val for i in range((usb_3_max_val - usb_3_start_val)//usb_3_step_val + 1)]
        usb_3_data = list(zip(usb_3_array, usb_3_val))
        # print(usb_3_data)
        mod_result = toolopt5 % usb_3_max_val
        indirect_value = usb_3_val[usb_3_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_usb_3 = result

        if index_usb_3 >= len(usb_3_array):
            print("Index exceeds the length of the list")
        else:
            usb_3 = usb_3_array[index_usb_3]
    def calculate_support_headphone(self,toolopt5):
        global support_headphone
        support_headphone_max_val = 131072
        support_headphone_step_val = 65536
        support_headphone_start_val = 0
        support_headphone_min_index = 1

        support_headphone_array = [
        "off", "on"
    ]
        support_headphone_val = [support_headphone_start_val + i * support_headphone_step_val for i in range((support_headphone_max_val - support_headphone_start_val)//support_headphone_step_val + 1)]
        support_headphone_data = list(zip(support_headphone_array, support_headphone_val))
        # print(support_headphone_data)
        mod_result = toolopt5 % support_headphone_max_val
        indirect_value = support_headphone_val[support_headphone_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_support_headphone = result

        if index_support_headphone >= len(support_headphone_array):
            print("Index exceeds the length of the list")
        else:
            support_headphone = support_headphone_array[index_support_headphone]
    def calculate_ciap_key(self,toolopt5):
        global ciap_key
        ciap_key_max_val = 262144
        ciap_key_step_val = 131072
        ciap_key_start_val = 0
        ciap_key_min_index = 1

        ciap_key_array = [
        "off", "on"
    ]
        ciap_key_val = [ciap_key_start_val + i * ciap_key_step_val for i in range((ciap_key_max_val - ciap_key_start_val)//ciap_key_step_val + 1)]
        ciap_key_data = list(zip(ciap_key_array, ciap_key_val))
        # print(ciap_key_data)
        mod_result = toolopt5 % ciap_key_max_val
        indirect_value = ciap_key_val[ciap_key_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_ciap_key = result

        if index_ciap_key >= len(ciap_key_array):
            print("Index exceeds the length of the list")
        else:
            ciap_key = ciap_key_array[index_ciap_key]
    def calculate_dtcpap_key(self,toolopt5):
        global dtcpap_key
        dtcpap_key_max_val = 524288
        dtcpap_key_step_val = 262144
        dtcpap_key_start_val = 0
        dtcpap_key_min_index = 1

        dtcpap_key_array = [
        "off", "on"
    ]
        dtcpap_key_val = [dtcpap_key_start_val + i * dtcpap_key_step_val for i in range((dtcpap_key_max_val - dtcpap_key_start_val)//dtcpap_key_step_val + 1)]
        dtcpap_key_data = list(zip(dtcpap_key_array, dtcpap_key_val))
        # print(dtcpap_key_data)
        mod_result = toolopt5 % dtcpap_key_max_val
        indirect_value = dtcpap_key_val[dtcpap_key_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_dtcpap_key = result

        if index_dtcpap_key >= len(dtcpap_key_array):
            print("Index exceeds the length of the list")
        else:
            dtcpap_key = dtcpap_key_array[index_dtcpap_key]
    def calculate_macap_key(self,toolopt5):
        global macap_key
        macap_key_max_val = 1048576
        macap_key_step_val = 524288
        macap_key_start_val = 0
        macap_key_min_index = 1

        macap_key_array = [
        "off", "on"
    ]
        macap_key_val = [macap_key_start_val + i * macap_key_step_val for i in range((macap_key_max_val - macap_key_start_val)//macap_key_step_val + 1)]
        macap_key_data = list(zip(macap_key_array, macap_key_val))
        # print(macap_key_data)
        mod_result = toolopt5 % macap_key_max_val
        indirect_value = macap_key_val[macap_key_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_macap_key = result

        if index_macap_key >= len(macap_key_array):
            print("Index exceeds the length of the list")
        else:
            macap_key = macap_key_array[index_macap_key]
    def calculate_esnap_key(self,toolopt5):
        global esnap_key
        esnap_key_max_val = 2097152
        esnap_key_step_val = 1048576
        esnap_key_start_val = 0
        esnap_key_min_index = 1

        esnap_key_array = [
        "off", "on"
    ]
        esnap_key_val = [esnap_key_start_val + i * esnap_key_step_val for i in range((esnap_key_max_val - esnap_key_start_val)//esnap_key_step_val + 1)]
        esnap_key_data = list(zip(esnap_key_array, esnap_key_val))
        # print(esnap_key_data)
        mod_result = toolopt5 % esnap_key_max_val
        indirect_value = esnap_key_val[esnap_key_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_esnap_key = result

        if index_esnap_key >= len(esnap_key_array):
            print("Index exceeds the length of the list")
        else:
            esnap_key = esnap_key_array[index_esnap_key]
    def calculate_widevineap_key(self,toolopt5):
        global widevineap_key
        widevineap_key_max_val = 4194304
        widevineap_key_step_val = 2097152
        widevineap_key_start_val = 0
        widevineap_key_min_index = 1

        widevineap_key_array = [
        "off", "on"
    ]
        widevineap_key_val = [widevineap_key_start_val + i * widevineap_key_step_val for i in range((widevineap_key_max_val - widevineap_key_start_val)//widevineap_key_step_val + 1)]
        widevineap_key_data = list(zip(widevineap_key_array, widevineap_key_val))
        # print(widevineap_key_data)
        mod_result = toolopt5 % widevineap_key_max_val
        indirect_value = widevineap_key_val[widevineap_key_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_widevineap_key = result

        if index_widevineap_key >= len(widevineap_key_array):
            print("Index exceeds the length of the list")
        else:
            widevineap_key = widevineap_key_array[index_widevineap_key]
    def calculate_ciecpap_key(self,toolopt5):
        global ciecpap_key
        ciecpap_key_max_val = 8388608
        ciecpap_key_step_val = 4194304
        ciecpap_key_start_val = 0
        ciecpap_key_min_index = 1

        ciecpap_key_array = [
        "off", "on"
    ]
        ciecpap_key_val = [ciecpap_key_start_val + i * ciecpap_key_step_val for i in range((ciecpap_key_max_val - ciecpap_key_start_val)//ciecpap_key_step_val + 1)]
        ciecpap_key_data = list(zip(ciecpap_key_array, ciecpap_key_val))
        # print(ciecpap_key_data)
        mod_result = toolopt5 % ciecpap_key_max_val
        indirect_value = ciecpap_key_val[ciecpap_key_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_ciecpap_key = result

        if index_ciecpap_key >= len(ciecpap_key_array):
            print("Index exceeds the length of the list")
        else:
            ciecpap_key = ciecpap_key_array[index_ciecpap_key]
    def calculate_atsc30_key(self,toolopt5):
        global atsc30_key
        atsc30_key_max_val = 16777216
        atsc30_key_step_val = 8388608
        atsc30_key_start_val = 0
        atsc30_key_min_index = 1

        atsc30_key_array = [
        "off", "on"
    ]
        atsc30_key_val = [atsc30_key_start_val + i * atsc30_key_step_val for i in range((atsc30_key_max_val - atsc30_key_start_val)//atsc30_key_step_val + 1)]
        atsc30_key_data = list(zip(atsc30_key_array, atsc30_key_val))
        # print(atsc30_key_data)
        mod_result = toolopt5 % atsc30_key_max_val
        indirect_value = atsc30_key_val[atsc30_key_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_atsc30_key = result

        if index_atsc30_key >= len(atsc30_key_array):
            print("Index exceeds the length of the list")
        else:
            atsc30_key = atsc30_key_array[index_atsc30_key]
    def calculate_new_erp(self,toolopt5):
        global new_erp
        new_erp_max_val = 33554432
        new_erp_step_val = 16777216
        new_erp_start_val = 0
        new_erp_min_index = 1

        new_erp_array = [
        "off", "on"
    ]
        new_erp_val = [new_erp_start_val + i * new_erp_step_val for i in range((new_erp_max_val - new_erp_start_val)//new_erp_step_val + 1)]
        new_erp_data = list(zip(new_erp_array, new_erp_val))
        # print(new_erp_data)
        mod_result = toolopt5 % new_erp_max_val
        indirect_value = new_erp_val[new_erp_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_new_erp = result

        if index_new_erp >= len(new_erp_array):
            print("Index exceeds the length of the list")
        else:
            new_erp = new_erp_array[index_new_erp]
    def calculate_oled_cpc(self,toolopt5):
        global oled_cpc
        oled_cpc_max_val = 134217728
        oled_cpc_step_val = 33554432
        oled_cpc_start_val = 0
        oled_cpc_min_index = 1

        oled_cpc_array = [
        "Default", "25", "30", "35"
    ]
        oled_cpc_val = [oled_cpc_start_val + i * oled_cpc_step_val for i in range((oled_cpc_max_val - oled_cpc_start_val)//oled_cpc_step_val + 1)]
        oled_cpc_data = list(zip(oled_cpc_array, oled_cpc_val))
        # print(oled_cpc_data)
        mod_result = toolopt5 % oled_cpc_max_val
        indirect_value = oled_cpc_val[oled_cpc_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_oled_cpc = result

        if index_oled_cpc >= len(oled_cpc_array):
            print("Index exceeds the length of the list")
        else:
            oled_cpc = oled_cpc_array[index_oled_cpc]
    def calculate_pd_charge(self,toolopt5):
        global pd_charge
        pd_charge_max_val = 134217728
        pd_charge_step_val = 134217728
        pd_charge_start_val = 0
        pd_charge_min_index = 1

        pd_charge_array = [
        "NA", "15W", "45W", "60W", "65W", "90W", "96W", "140W"
    ]
        pd_charge_val = [pd_charge_start_val + i * pd_charge_step_val for i in range((pd_charge_max_val - pd_charge_start_val)//pd_charge_step_val + 1)]
        pd_charge_data = list(zip(pd_charge_array, pd_charge_val))
        # print(pd_charge_data)
        indirect_value = pd_charge_val[pd_charge_min_index]

        result = toolopt5 // indirect_value
        # print(result)
        index_pd_charge = result

        if index_pd_charge >= len(pd_charge_array):
            print("Index exceeds the length of the list")
        else:
            pd_charge = pd_charge_array[index_pd_charge]     

class calculate_tooloption6():
    def __init__(self):
        self.toolopt6_run()
        pass
    def toolopt6_run(self):
        self.calculation_digital_eye(tooloption6)
        self.calculate_energy_star(tooloption6)
        self.calculate_adaptivedim_default(tooloption6)
        self.calculate_adaptive_dimming(tooloption6)
        self.calculate_default_backlight(tooloption6)
        self.calculate_sound_mode(tooloption6)
        self.calculate_isf_mode(tooloption6)
        self.calculate_set_id(tooloption6)
        self.calculate_support_calmansw(tooloption6)
        self.calculate_dvr_ready(tooloption6)
        self.calculate_audio_lineout(tooloption6)
        self.calculate_wifi_bt(tooloption6)
        self.calculate_wifi_assy_type(tooloption6)
        self.calculate_motion_remocon(tooloption6)
        self.calculate_audioeq_eye(tooloption6)
        self.calculate_edid_type(tooloption6)
    def calculation_digital_eye(self,toolopt6):
        global digital_eye
        digital_eye_max_val = 4
        digital_eye_step_val = 1
        digital_eye_start_val = 0
        digital_eye_min_index = 1

        digital_eye_array = [
        "off", "Eye_Sensor", "RGB_Sensor", "OTP_eyeSensor"
    ]
        digital_eye_val = [digital_eye_start_val + i * digital_eye_step_val for i in range((digital_eye_max_val - digital_eye_start_val)//digital_eye_step_val + 1)]
        digital_eye_data = list(zip(digital_eye_array, digital_eye_val))
        # print(digital_eye_data)
        mod_result = toolopt6 % digital_eye_max_val
        indirect_value = digital_eye_val[digital_eye_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_digital_eye = result

        if index_digital_eye >= len(digital_eye_array):
            print("Index exceeds the length of the list")
        else:
            digital_eye = digital_eye_array[index_digital_eye]
    def calculate_energy_star(self,toolopt6):
        global energy_star
        energy_star_max_val = 8
        energy_star_step_val = 4
        energy_star_start_val = 0
        energy_star_min_index = 1

        energy_star_array = [
        "off", "on"
    ]
        energy_star_val = [energy_star_start_val + i * energy_star_step_val for i in range((energy_star_max_val - energy_star_start_val)//energy_star_step_val + 1)]
        energy_star_data = list(zip(energy_star_array, energy_star_val))
        # print(energy_star_data)
        mod_result = toolopt6 % energy_star_max_val
        indirect_value = energy_star_val[energy_star_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_energy_star = result

        if index_energy_star >= len(energy_star_array):
            print("Index exceeds the length of the list")
        else:
            energy_star = energy_star_array[index_energy_star]
    def calculate_adaptivedim_default(self,toolopt6):
        global adaptivedim_default
        adaptivedim_default_max_val = 16
        adaptivedim_default_step_val = 8
        adaptivedim_default_start_val = 0
        adaptivedim_default_min_index = 1

        adaptivedim_default_array = [
        "off", "on"
    ]
        adaptivedim_default_val = [adaptivedim_default_start_val + i * adaptivedim_default_step_val for i in range((adaptivedim_default_max_val - adaptivedim_default_start_val)//adaptivedim_default_step_val + 1)]
        adaptivedim_default_data = list(zip(adaptivedim_default_array, adaptivedim_default_val))
        # print(adaptivedim_default_data)
        mod_result = toolopt6 % adaptivedim_default_max_val
        indirect_value = adaptivedim_default_val[adaptivedim_default_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_adaptivedim_default = result

        if index_adaptivedim_default >= len(adaptivedim_default_array):
            print("Index exceeds the length of the list")
        else:
            adaptivedim_default = adaptivedim_default_array[index_adaptivedim_default]
    def calculate_adaptive_dimming(self,toolopt6):
        global adaptive_dimming
        adaptive_dimming_max_val = 256
        adaptive_dimming_step_val = 16
        adaptive_dimming_start_val = 0
        adaptive_dimming_min_index = 1

        adaptive_dimming_array = [
        "Step1", "Step2", "Step3", "Step4", "Step5", "Step6", "Step7", "Step8", "Step9", "Step10", "Step11", "Step12"
    ]
        adaptive_dimming_val = [adaptive_dimming_start_val + i * adaptive_dimming_step_val for i in range((adaptive_dimming_max_val - adaptive_dimming_start_val)//adaptive_dimming_step_val + 1)]
        adaptive_dimming_data = list(zip(adaptive_dimming_array, adaptive_dimming_val))
        # print(adaptive_dimming_data)
        mod_result = toolopt6 % adaptive_dimming_max_val
        indirect_value = adaptive_dimming_val[adaptive_dimming_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_adaptive_dimming = result

        if index_adaptive_dimming >= len(adaptive_dimming_array):
            print("Index exceeds the length of the list")
        else:
            adaptive_dimming = adaptive_dimming_array[index_adaptive_dimming]
    def calculate_default_backlight(self,toolopt6):
        global default_backlight
        default_backlight_max_val = 4096
        default_backlight_step_val = 256
        default_backlight_start_val = 0
        default_backlight_min_index = 1

        default_backlight_array = [
        "25~29", "30~34", "35~39", "40~44", "45~49",
        "50~54", "55~59", "60~64", "65~69", "70~74",
        "75~79", "80~84", "85~89", "90~94", "95~99",
        "100"
    ]
        default_backlight_val = [default_backlight_start_val + i * default_backlight_step_val for i in range((default_backlight_max_val - default_backlight_start_val)//default_backlight_step_val + 1)]
        default_backlight_data = list(zip(default_backlight_array, default_backlight_val))
        # print(default_backlight_data)
        mod_result = toolopt6 % default_backlight_max_val
        indirect_value = default_backlight_val[default_backlight_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_default_backlight = result

        if index_default_backlight >= len(default_backlight_array):
            print("Index exceeds the length of the list")
        else:
            default_backlight = default_backlight_array[index_default_backlight]
    def calculate_sound_mode(self,toolopt6):
        global sound_mode
        sound_mode_max_val = 16384
        sound_mode_step_val = 4096
        sound_mode_start_val = 0
        sound_mode_min_index = 1

        sound_mode_array = [
        "LG Sound Engine", "Dolby Atmos", "Sound Engine Lite"
    ]
        sound_mode_val = [sound_mode_start_val + i * sound_mode_step_val for i in range((sound_mode_max_val - sound_mode_start_val)//sound_mode_step_val + 1)]
        sound_mode_data = list(zip(sound_mode_array, sound_mode_val))
        # print(sound_mode_data)
        mod_result = toolopt6 % sound_mode_max_val
        indirect_value = sound_mode_val[sound_mode_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_sound_mode = result

        if index_sound_mode >= len(sound_mode_array):
            print("Index exceeds the length of the list")
        else:
            sound_mode = sound_mode_array[index_sound_mode]
    def calculate_isf_mode(self,toolopt6):
        global isf_mode
        isf_mode_max_val = 32768
        isf_mode_step_val = 16384
        isf_mode_start_val = 0
        isf_mode_min_index = 1

        isf_mode_array = [
        "off", "on"
    ]
        isf_mode_val = [isf_mode_start_val + i * isf_mode_step_val for i in range((isf_mode_max_val - isf_mode_start_val)//isf_mode_step_val + 1)]
        isf_mode_data = list(zip(isf_mode_array, isf_mode_val))
        # print(isf_mode_data)
        mod_result = toolopt6 % isf_mode_max_val
        indirect_value = isf_mode_val[isf_mode_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_isf_mode = result

        if index_isf_mode >= len(isf_mode_array):
            print("Index exceeds the length of the list")
        else:
            isf_mode = isf_mode_array[index_isf_mode]
    def calculate_set_id(self,toolopt6):
        global set_id
        set_id_max_val = 65536
        set_id_step_val = 32768
        set_id_start_val = 0
        set_id_min_index = 1

        set_id_array = [
        "off", "on"
    ]
        set_id_val = [set_id_start_val + i * set_id_step_val for i in range((set_id_max_val - set_id_start_val)//set_id_step_val + 1)]
        set_id_data = list(zip(set_id_array, set_id_val))
        # print(set_id_data)
        mod_result = toolopt6 % set_id_max_val
        indirect_value = set_id_val[set_id_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_set_id = result

        if index_set_id >= len(set_id_array):
            print("Index exceeds the length of the list")
        else:
            set_id = set_id_array[index_set_id]
    def calculate_support_calmansw(self,toolopt6):
        global support_calmansw
        support_calmansw_max_val = 131072
        support_calmansw_step_val = 65536
        support_calmansw_start_val = 0
        support_calmansw_min_index = 1

        support_calmansw_array = [
        "off", "on"
    ]
        support_calmansw_val = [support_calmansw_start_val + i * support_calmansw_step_val for i in range((support_calmansw_max_val - support_calmansw_start_val)//support_calmansw_step_val + 1)]
        support_calmansw_data = list(zip(support_calmansw_array, support_calmansw_val))
        # print(support_calmansw_data)
        mod_result = toolopt6 % support_calmansw_max_val
        indirect_value = support_calmansw_val[support_calmansw_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_support_calmansw = result

        if index_support_calmansw >= len(support_calmansw_array):
            print("Index exceeds the length of the list")
        else:
            support_calmansw = support_calmansw_array[index_support_calmansw]
    def calculate_dvr_ready(self,toolopt6):
        global dvr_ready
        dvr_ready_max_val = 262144
        dvr_ready_step_val = 131072
        dvr_ready_start_val = 0
        dvr_ready_min_index = 1

        dvr_ready_array = [
        "off", "on"
    ]
        dvr_ready_val = [dvr_ready_start_val + i * dvr_ready_step_val for i in range((dvr_ready_max_val - dvr_ready_start_val)//dvr_ready_step_val + 1)]
        dvr_ready_data = list(zip(dvr_ready_array, dvr_ready_val))
        # print(dvr_ready_data)
        mod_result = toolopt6 % dvr_ready_max_val
        indirect_value = dvr_ready_val[dvr_ready_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_dvr_ready = result

        if index_dvr_ready >= len(dvr_ready_array):
            print("Index exceeds the length of the list")
        else:
            dvr_ready = dvr_ready_array[index_dvr_ready]
    def calculate_audio_lineout(self,toolopt6):
        global audio_lineout
        audio_lineout_max_val = 524288
        audio_lineout_step_val = 262144
        audio_lineout_start_val = 0
        audio_lineout_min_index = 1

        audio_lineout_array = [
        "off", "on"
    ]
        audio_lineout_val = [audio_lineout_start_val + i * audio_lineout_step_val for i in range((audio_lineout_max_val - audio_lineout_start_val)//audio_lineout_step_val + 1)]
        audio_lineout_data = list(zip(audio_lineout_array, audio_lineout_val))
        # print(audio_lineout_data)
        mod_result = toolopt6 % audio_lineout_max_val
        indirect_value = audio_lineout_val[audio_lineout_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_audio_lineout = result

        if index_audio_lineout >= len(audio_lineout_array):
            print("Index exceeds the length of the list")
        else:
            audio_lineout = audio_lineout_array[index_audio_lineout]
    def calculate_wifi_bt(self,toolopt6):
        global wifi_bt
        wifi_bt_max_val = 2097152
        wifi_bt_step_val = 524288
        wifi_bt_start_val = 0
        wifi_bt_min_index = 1

        wifi_bt_array = [
        "Ready", "Wi-Fi Only", "WiFi BT", "None"
    ]
        wifi_bt_val = [wifi_bt_start_val + i * wifi_bt_step_val for i in range((wifi_bt_max_val - wifi_bt_start_val)//wifi_bt_step_val + 1)]
        wifi_bt_data = list(zip(wifi_bt_array, wifi_bt_val))
        # print(wifi_bt_data)
        mod_result = toolopt6 % wifi_bt_max_val
        indirect_value = wifi_bt_val[wifi_bt_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_wifi_bt = result

        if index_wifi_bt >= len(wifi_bt_array):
            print("Index exceeds the length of the list")
        else:
            wifi_bt = wifi_bt_array[index_wifi_bt]
    def calculate_wifi_assy_type(self,toolopt6):
        global wifi_assy_type
        wifi_assy_type_max_val = 33554432
        wifi_assy_type_step_val = 2097152
        wifi_assy_type_start_val = 0
        wifi_assy_type_min_index = 1

        wifi_assy_type_array = [
        "11ax_26Y","Dual_21Y","Single_26Y","Single_21Y",
        "Single_20Y","None","11ax","Single_22Y","Dual_26Y",
        "Dual_23Y","Single_23Y","M_Single_24Y"
    ]
        wifi_assy_type_val = [wifi_assy_type_start_val + i * wifi_assy_type_step_val for i in range((wifi_assy_type_max_val - wifi_assy_type_start_val)//wifi_assy_type_step_val + 1)]
        wifi_assy_type_data = list(zip(wifi_assy_type_array, wifi_assy_type_val))
        # print(wifi_assy_type_data)
        mod_result = toolopt6 % wifi_assy_type_max_val
        indirect_value = wifi_assy_type_val[wifi_assy_type_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_wifi_assy_type = result

        if index_wifi_assy_type >= len(wifi_assy_type_array):
            print("Index exceeds the length of the list")
        else:
            wifi_assy_type = wifi_assy_type_array[index_wifi_assy_type]
    def calculate_motion_remocon(self,toolopt6):
        global motion_remocon
        motion_remocon_max_val = 67108864
        motion_remocon_step_val = 33554432
        motion_remocon_start_val = 0
        motion_remocon_min_index = 1
        motion_remocon_array = [
        "off", "on"
    ]
        motion_remocon_val = [motion_remocon_start_val + i * motion_remocon_step_val for i in range((motion_remocon_max_val - motion_remocon_start_val)//motion_remocon_step_val + 1)]
        motion_remocon_data = list(zip(motion_remocon_array, motion_remocon_val))
        # print(motion_remocon_data)
        mod_result = toolopt6 % motion_remocon_max_val
        indirect_value = motion_remocon_val[motion_remocon_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_motion_remocon = result

        if index_motion_remocon >= len(motion_remocon_array):
            print("Index exceeds the length of the list")
        else:
            motion_remocon = motion_remocon_array[index_motion_remocon]
    def calculate_audioeq_eye(self,toolopt6):
        global audioeq_eye
        audioeq_eye_max_val = 268435456
        audioeq_eye_step_val = 67108864
        audioeq_eye_start_val = 0
        audioeq_eye_min_index = 1
        audioeq_eye_array = [
        "Default", "Type1", "Type2", "Type3"
    ]
        audioeq_eye_val = [audioeq_eye_start_val + i * audioeq_eye_step_val for i in range((audioeq_eye_max_val - audioeq_eye_start_val)//audioeq_eye_step_val + 1)]
        audioeq_eye_data = list(zip(audioeq_eye_array, audioeq_eye_val))
        # print(audioeq_eye_data)
        mod_result = toolopt6 % audioeq_eye_max_val
        indirect_value = audioeq_eye_val[audioeq_eye_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_audioeq_eye = result

        if index_audioeq_eye >= len(audioeq_eye_array):
            print("Index exceeds the length of the list")
        else:
            audioeq_eye = audioeq_eye_array[index_audioeq_eye]
    def calculate_edid_type(self,toolopt6):
        global edid_type
        edid_type_max_val = 268435456
        edid_type_step_val = 268435456
        edid_type_start_val = 0
        edid_type_min_index = 1
        edid_type_array = [
        "ac3", "", "TrueHD", ""
    ]
        edid_type_val = [edid_type_start_val + i * edid_type_step_val for i in range((edid_type_max_val - edid_type_start_val)//edid_type_step_val + 1)]
        edid_type_data = list(zip(edid_type_array, edid_type_val))
        # print(edid_type_data)
        indirect_value = edid_type_val[edid_type_min_index]

        result = toolopt6 // indirect_value
        # print(result)
        index_edid_type = result

        if index_edid_type >= len(edid_type_array):
            print("Index exceeds the length of the list")
        else:
            edid_type = edid_type_array[index_edid_type]     

class calculate_boardoption():
    def __init__(self):
        self.boardoption_run()
        pass
    def boardoption_run(self):
        self.calculation_panel_type(boardoption)
        self.calculation_panel_interface(boardoption)
        self.calculation_panel_resolution(boardoption)
        self.calculation_panel_maxframerate(boardoption)
        self.calculation_panel_maxbit(boardoption)
        self.calculation_panel_divisiontype(boardoption)
        self.calculation_external_frc(boardoption)
        self.calculation_ddr_size(boardoption)
        self.calculation_country_type(boardoption)
        self.calculation_tuner_type(boardoption)
        self.calculation_micom_localkey(boardoption)
        self.calculation_arrlon_control(boardoption)
        self.calculation_irled_control(boardoption)
        self.calculation_model_type(boardoption)
        self.calculation_weeturnkey_version(boardoption)
    def calculation_panel_type(self,boardopt):
        global panel_type
        panel_type_max_val = 4
        panel_type_step_val = 1
        panel_type_start_val = 0
        panel_type_min_index = 1

        panel_type_array = [
        "None", "OLED", "LCD"
    ]
        panel_type_val = [panel_type_start_val + i * panel_type_step_val for i in range((panel_type_max_val - panel_type_start_val)//panel_type_step_val + 1)]
        panel_type_data = list(zip(panel_type_array, panel_type_val))
        # print(panel_type_data)
        mod_result = boardopt % panel_type_max_val
        indirect_value = panel_type_val[panel_type_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_panel_type = result

        if index_panel_type >= len(panel_type_array):
            print("Index exceeds the length of the list")
        else:
            panel_type = panel_type_array[index_panel_type]
    def calculation_panel_interface(self,boardopt):
        global panel_interface
        panel_interface_max_val = 32
        panel_interface_step_val = 4
        panel_interface_start_val = 0
        panel_interface_min_index = 1

        panel_interface_array = [
        "vby1 4byte", "vby1 5byte", "CEDS/CSPI", "EPI", "LVDS", "eDP"
    ]
        panel_interface_val = [panel_interface_start_val + i * panel_interface_step_val for i in range((panel_interface_max_val - panel_interface_start_val)//panel_interface_step_val + 1)]
        panel_interface_data = list(zip(panel_interface_array, panel_interface_val))
        # print(panel_interface_data)
        mod_result = boardopt % panel_interface_max_val
        indirect_value = panel_interface_val[panel_interface_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_panel_interface = result

        if index_panel_interface >= len(panel_interface_array):
            print("Index exceeds the length of the list")
        else:
            panel_interface = panel_interface_array[index_panel_interface]
    def calculation_panel_resolution(self,boardopt):
        global panel_resolution
        panel_resolution_max_val = 512
        panel_resolution_step_val = 32
        panel_resolution_start_val = 0
        panel_resolution_min_index = 1

        panel_resolution_array = [
        "HD", "FHD", "WFHD", "QHD", "WQHD", "WQHD+", "UHD", "WUHD", "5K", "6K", "8K"
    ]
        panel_resolution_val = [panel_resolution_start_val + i * panel_resolution_step_val for i in range((panel_resolution_max_val - panel_resolution_start_val)//panel_resolution_step_val + 1)]
        panel_resolution_data = list(zip(panel_resolution_array, panel_resolution_val))
        # print(panel_resolution_data)
        mod_result = boardopt % panel_resolution_max_val
        indirect_value = panel_resolution_val[panel_resolution_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_panel_resolution = result

        if index_panel_resolution >= len(panel_resolution_array):
            print("Index exceeds the length of the list")
        else:
            panel_resolution = panel_resolution_array[index_panel_resolution]
    def calculation_panel_maxframerate(self,boardopt):
        global panel_maxframerate
        panel_maxframerate_max_val = 8192
        panel_maxframerate_step_val = 512
        panel_maxframerate_start_val = 0
        panel_maxframerate_min_index = 1

        panel_maxframerate_array = [
        "50/60", "100/120", "144", "165", "180", "200", "240", "300", "360", "480"
    ]
        panel_maxframerate_val = [panel_maxframerate_start_val + i * panel_maxframerate_step_val for i in range((panel_maxframerate_max_val - panel_maxframerate_start_val)//panel_maxframerate_step_val + 1)]
        panel_maxframerate_data = list(zip(panel_maxframerate_array, panel_maxframerate_val))
        # print(panel_maxframerate_data)
        mod_result = boardopt % panel_maxframerate_max_val
        indirect_value = panel_maxframerate_val[panel_maxframerate_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_panel_maxframerate = result

        if index_panel_maxframerate >= len(panel_maxframerate_array):
            print("Index exceeds the length of the list")
        else:
            panel_maxframerate = panel_maxframerate_array[index_panel_maxframerate]
    def calculation_panel_maxbit(self,boardopt):
        global panel_maxbit
        panel_maxbit_max_val = 65536
        panel_maxbit_step_val = 8192
        panel_maxbit_start_val = 0
        panel_maxbit_min_index = 1

        panel_maxbit_array = [
        "8", "10", "11", "12", "13"
    ]
        panel_maxbit_val = [panel_maxbit_start_val + i * panel_maxbit_step_val for i in range((panel_maxbit_max_val - panel_maxbit_start_val)//panel_maxbit_step_val + 1)]
        panel_maxbit_data = list(zip(panel_maxbit_array, panel_maxbit_val))
        # print(panel_maxbit_data)
        mod_result = boardopt % panel_maxbit_max_val
        indirect_value = panel_maxbit_val[panel_maxbit_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_panel_maxbit = result

        if index_panel_maxbit >= len(panel_maxbit_array):
            print("Index exceeds the length of the list")
        else:
            panel_maxbit = panel_maxbit_array[index_panel_maxbit]
    def calculation_panel_divisiontype(self,boardopt):
        global panel_divisiontype
        panel_divisiontype_max_val = 262144
        panel_divisiontype_step_val = 65536
        panel_divisiontype_start_val = 0
        panel_divisiontype_min_index = 1

        panel_divisiontype_array = [
        "non-division", "2 division", "4 division",	"8 division"
    ]
        panel_divisiontype_val = [panel_divisiontype_start_val + i * panel_divisiontype_step_val for i in range((panel_divisiontype_max_val - panel_divisiontype_start_val)//panel_divisiontype_step_val + 1)]
        panel_divisiontype_data = list(zip(panel_divisiontype_array, panel_divisiontype_val))
        # print(panel_divisiontype_data)
        mod_result = boardopt % panel_divisiontype_max_val
        indirect_value = panel_divisiontype_val[panel_divisiontype_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_panel_divisiontype = result

        if index_panel_divisiontype >= len(panel_divisiontype_array):
            print("Index exceeds the length of the list")
        else:
            panel_divisiontype = panel_divisiontype_array[index_panel_divisiontype]
    def calculation_external_frc(self,boardopt):
        global external_frc
        external_frc_max_val = 2097152
        external_frc_step_val = 262144
        external_frc_start_val = 0
        external_frc_min_index = 1

        external_frc_array = [
        "None", "F22", "KLD(KGAI)"
    ]
        external_frc_val = [external_frc_start_val + i * external_frc_step_val for i in range((external_frc_max_val - external_frc_start_val)//external_frc_step_val + 1)]
        external_frc_data = list(zip(external_frc_array, external_frc_val))
        # print(external_frc_data)
        mod_result = boardopt % external_frc_max_val
        indirect_value = external_frc_val[external_frc_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_external_frc = result

        if index_external_frc >= len(external_frc_array):
            print("Index exceeds the length of the list")
        else:
            external_frc = external_frc_array[index_external_frc]
    def calculation_ddr_size(self,boardopt):
        global ddr_size
        ddr_size_max_val = 16777216
        ddr_size_step_val = 2097152
        ddr_size_start_val = 0
        ddr_size_min_index = 1

        ddr_size_array = [
        "1.0 GB", "1.5 GB", "2.0 GB", "2.5 GB", "3.0 GB", "3.5 GB", "4.0 GB"
    ]
        ddr_size_val = [ddr_size_start_val + i * ddr_size_step_val for i in range((ddr_size_max_val - ddr_size_start_val)//ddr_size_step_val + 1)]
        ddr_size_data = list(zip(ddr_size_array, ddr_size_val))
        # print(ddr_size_data)
        mod_result = boardopt % ddr_size_max_val
        indirect_value = ddr_size_val[ddr_size_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_ddr_size = result

        if index_ddr_size >= len(ddr_size_array):
            print("Index exceeds the length of the list")
        else:
            ddr_size = ddr_size_array[index_ddr_size]
    def calculation_country_type(self,boardopt):
        global country_type
        country_type_max_val = 134217728
        country_type_step_val = 16777216
        country_type_start_val = 0
        country_type_min_index = 1

        country_type_array = [
        "BR/TW/COLOM/AJ", "CN/HK", "EU/JA", "Not Used (WEE only - TW/COLOM/AJ)", "KR", "US", "JP"
    ]
        country_type_val = [country_type_start_val + i * country_type_step_val for i in range((country_type_max_val - country_type_start_val)//country_type_step_val + 1)]
        country_type_data = list(zip(country_type_array, country_type_val))
        # print(country_type_data)
        mod_result = boardopt % country_type_max_val
        indirect_value = country_type_val[country_type_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_country_type = result

        if index_country_type >= len(country_type_array):
            print("Index exceeds the length of the list")
        else:
            country_type = country_type_array[index_country_type]
    def calculation_tuner_type(self,boardopt):
        global tuner_type
        tuner_type_max_val = 1073741824
        tuner_type_step_val = 134217728
        tuner_type_start_val = 0
        tuner_type_min_index = 1

        tuner_type_array = [
        "Type 0", "Type 1", "Type 2", "Type 3", "Type 4", "Type 5", "Tunerless", "Type 7"
    ]
        tuner_type_val = [tuner_type_start_val + i * tuner_type_step_val for i in range((tuner_type_max_val - tuner_type_start_val)//tuner_type_step_val + 1)]
        tuner_type_data = list(zip(tuner_type_array, tuner_type_val))
        # print(tuner_type_data)
        mod_result = boardopt % tuner_type_max_val
        indirect_value = tuner_type_val[tuner_type_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_tuner_type = result

        if index_tuner_type >= len(tuner_type_array):
            print("Index exceeds the length of the list")
        else:
            tuner_type = tuner_type_array[index_tuner_type]
    def calculation_micom_localkey(self,boardopt):
        global micom_localkey
        micom_localkey_max_val = 4294967296
        micom_localkey_step_val = 1073741824
        micom_localkey_start_val = 0
        micom_localkey_min_index = 1

        micom_localkey_array = [
        "1 key", "5 key", "7 key"
    ]
        micom_localkey_val = [micom_localkey_start_val + i * micom_localkey_step_val for i in range((micom_localkey_max_val - micom_localkey_start_val)//micom_localkey_step_val + 1)]
        micom_localkey_data = list(zip(micom_localkey_array, micom_localkey_val))
        # print(micom_localkey_data)
        mod_result = boardopt % micom_localkey_max_val
        indirect_value = micom_localkey_val[micom_localkey_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_micom_localkey = result

        if index_micom_localkey >= len(micom_localkey_array):
            print("Index exceeds the length of the list")
        else:
            micom_localkey = micom_localkey_array[index_micom_localkey]
    def calculation_arrlon_control(self,boardopt):
        global arrlon_control
        arrlon_control_max_val = 8589934592
        arrlon_control_step_val = 4294967296
        arrlon_control_start_val = 0
        arrlon_control_min_index = 1

        arrlon_control_array = [
        "Enable", "Disable"
    ]
        arrlon_control_val = [arrlon_control_start_val + i * arrlon_control_step_val for i in range((arrlon_control_max_val - arrlon_control_start_val)//arrlon_control_step_val + 1)]
        arrlon_control_data = list(zip(arrlon_control_array, arrlon_control_val))
        # print(arrlon_control_data)
        mod_result = boardopt % arrlon_control_max_val
        indirect_value = arrlon_control_val[arrlon_control_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_arrlon_control = result

        if index_arrlon_control >= len(arrlon_control_array):
            print("Index exceeds the length of the list")
        else:
            arrlon_control = arrlon_control_array[index_arrlon_control]
    def calculation_irled_control(self,boardopt):
        global irled_control
        irled_control_max_val = 17179869184
        irled_control_step_val = 8589934592
        irled_control_start_val = 0
        irled_control_min_index = 1

        irled_control_array = [
        "GPIO", "PWM"
    ]
        irled_control_val = [irled_control_start_val + i * irled_control_step_val for i in range((irled_control_max_val - irled_control_start_val)//irled_control_step_val + 1)]
        irled_control_data = list(zip(irled_control_array, irled_control_val))
        # print(irled_control_data)
        mod_result = boardopt % irled_control_max_val
        indirect_value = irled_control_val[irled_control_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_irled_control = result

        if index_irled_control >= len(irled_control_array):
            print("Index exceeds the length of the list")
        else:
            irled_control = irled_control_array[index_irled_control]
    def calculation_model_type(self,boardopt):
        global model_type
        model_type_max_val = 137438953472
        model_type_step_val = 17179869184
        model_type_start_val = 0
        model_type_min_index = 1

        model_type_array = [
        "None", "WirelessAV", "NMRM"
    ]
        model_type_val = [model_type_start_val + i * model_type_step_val for i in range((model_type_max_val - model_type_start_val)//model_type_step_val + 1)]
        model_type_data = list(zip(model_type_array, model_type_val))
        # print(model_type_data)
        mod_result = boardopt % model_type_max_val
        indirect_value = model_type_val[model_type_min_index]

        result = mod_result // indirect_value
        # print(result)
        index_model_type = result

        if index_model_type >= len(model_type_array):
            print("Index exceeds the length of the list")
        else:
            model_type = model_type_array[index_model_type]
    def calculation_weeturnkey_version(self,boardopt):
        global weeturnkey_version
        weeturnkey_version_max_val = 137438953472
        weeturnkey_version_step_val = 137438953472
        weeturnkey_version_start_val = 0
        weeturnkey_version_min_index = 1

        weeturnkey_version_array = [
        "T2.0", "T3.0",	"T4.0",	"T5.0"
    ]
        weeturnkey_version_val = [weeturnkey_version_start_val + i * weeturnkey_version_step_val for i in range((weeturnkey_version_max_val - weeturnkey_version_start_val)//weeturnkey_version_step_val + 1)]
        weeturnkey_version_data = list(zip(weeturnkey_version_array, weeturnkey_version_val))
        # print(weeturnkey_version_data)
        indirect_value = weeturnkey_version_val[weeturnkey_version_min_index]

        result = boardopt // indirect_value
        # print(result)
        index_weeturnkey_version = result

        if index_weeturnkey_version >= len(weeturnkey_version_array):
            print("Index exceeds the length of the list")
        else:
            weeturnkey_version = weeturnkey_version_array[index_weeturnkey_version]

class run_tooloption():
    def __init__(self):
        pass
    def run(self):
        target_parsing = target_tooloption()
        development_parsing = development_tooloption()
        initial_parsing = initial_tooloption()

if __name__ == "__main__":
    running_tooloption = run_tooloption()
    running_tooloption.run()
    # initial_run = initial_tooloptionkey()



def getToolinfo(tool1, tool2, tool3, tool4, tool5, tool6, boardopt: str):
    target_boardoption = boardopt
    tooloption1 = tool1
    tooloption2 = tool2
    tooloption3 = tool3
    tooloption4 = tool4
    tooloption5 = tool5
    tooloption6 = tool6
    boardoption = int(target_boardoption,16)
  
    #GetBoardcheck = calculate_boardoption()
    GetTool1check = calculate_tooloption1()
    GetTool2check = calculate_tooloption2()
    GetTool3check = calculate_tooloption3()
    GetTool4check = calculate_tooloption4()
    GetTool5check = calculate_tooloption5()
    GetTool6check = calculate_tooloption6()
    GetBoardcheck = calculate_boardoption()

    GetTool1 = {
        "inch_code": inch_code,
        "tool_code": tool_code,
        "panel_code": panel_code,
        "pmic_mode": pmic_mode,
        "backlight_type": backlight_type,
        "localdin_block": localdim_block,
        "adjust_vcom": adjust_vcom
    }

    key_value = [
                {
                    "Inch Code": inch_code,
                    "Tool": tool_code,
                    "Panel Code": panel_code,
                    "Pmic set Mode": pmic_mode,
                    "Backlight Type": backlight_type,
                    "Local Dim Block": localdim_block,
                    "Adjust LCD VCOM": adjust_vcom,
                    "Audio Power Volt": audiopw_volt,
                    "PWM2 Duty": pwm2_duty,
                    "Max PWM": max_pwm,
                    "Scanning B/L": scanning_bl,
                    "BPL Current Type": bpl_type,
                    "Power Mode Select": powermode_select,
                    "Eye Sensor LED Gain Control": eyesensor_gain,
                    "Standard Backlight": standard_backlight,
                    "Vivid Sports Backlight": vividsports_bl,
                    "Panel Gamut Type": panelgamut_type,
                    "Motion Pro Mode": motionpro_mode,
                    "Support Dolby Vision HDR": support_dolbyvisionhdr,
                    "Audio Amp": ampchip_type,
                    "Speaker Watt": audiospk_watt,
                    "Luminance Up": support_luminanceup,
                    "Support VRR": support_vrr,
                    "Support Freesync": support_freesync,
                    "AI Sound": aisound_type,
                    "Dolby Vison Precision Detail": dolbyvison_precisiondetail,
                    "PWM Freq. double": pwmfreq_double,
                    "Motion Booster": motion_booster,
                    "OLED DPC Type": oleddpc_type,
                    "Support Freesync Pro": support_freesyncpro,
                    "Logo Light": logo_light,
                    "Fan Control": support_fancontrol,
                    "Camera Ready": camera_type,
                    "WOL": support_wol,
                    "HDMI Switch IC": hdmiswitch_type,
                    "Moving Speaker": moving_speaker,
                    "Support IR Blaster": support_irblaster,
                    "Mirror Mode": mirror_mode,
                    "Screen Roller Motor": screenroller_motor,
                    "Motion Detect Sensor": motiondetect_sensor,
                    "LCD Screen Cooling": lcdscreen_cooling,
                    "LAN Support": support_lan,
                    "Special Edition": special_edition,
                    "Support Optical Jack": optical_jack,
                    "Support Far Field Voice": farfield_voice,
                    "Type-C controller IC": type_cctric,
                    "AI Art Extension": aiart_extension,
                    "Board Design": board_design,
                    "EMMC Density": emmc_density,
                    "Video ADC Index": videoadc_index,
                    "Audio ADC Index": audioadc_index,
                    "USB Count": usb_count,
                    "USB 1": usb_1,
                    "USB 2": usb_2,
                    "USB 3": usb_3,
                    "Headphone": support_headphone,
                    "CI_AP Key": ciap_key,
                    "DTCP_AP Key": dtcpap_key,
                    "MAC_AP Key": macap_key,
                    "ESN_AP Key": esnap_key,
                    "Widevine_AP Key": widevineap_key,
                    "CI_ECP_AP Key": ciecpap_key,
                    "ATSC 3.0 (KR) Key": atsc30_key,
                    "New ErP": new_erp,
                    "OLED CPC": oled_cpc,
                    "PD Charge": pd_charge,
                    "Digital Eye": digital_eye,
                    "Energy Star": energy_star,
                    "AdaptiveDim Default": adaptivedim_default,
                    "Adaptive Dimming": adaptive_dimming,
                    "Default Backlight": default_backlight,
                    "Sound Mode": sound_mode,
                    "ISF": isf_mode,
                    "Set ID": set_id,
                    "Support Calman SW": support_calmansw,
                    "DVR Ready": dvr_ready,
                    "Audio Line Out": audio_lineout,
                    "WIFI/BT": wifi_bt,
                    "WIFI assy type": wifi_assy_type,
                    "Motion Remocon": motion_remocon,
                    "AudioEQ Eye": audioeq_eye,
                    "EDID Type": edid_type,
                    "Panel Type": panel_type,
                    "Panel Interface": panel_interface,
                    "Panel Resolution": panel_resolution,
                    "Panel Max Frame Rate": panel_maxframerate,
                    "Panel Max Bit": panel_maxbit,
                    "Panel Division Type": panel_divisiontype,
                    "External Frc Type": external_frc,
                    "DDR Size": ddr_size,
                    "Country Type": country_type,
                    "Tuner Type": tuner_type,
                    "Micom LocalKey Type": micom_localkey,
                    "AR RL on Control": arrlon_control,
                    "IR LED Control": irled_control,
                    "Model Type": model_type,
                    "Wee Turnkey Version": weeturnkey_version
                }
            ]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            

    df = pl.DataFrame(
        list(key_value[0].items()),
        schema=["Properties", "Target Model"]
    )

    return df


