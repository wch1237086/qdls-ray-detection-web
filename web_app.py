import streamlit as st
import json
import os
from datetime import datetime

# ========== 1. 页面配置 & 数据存储初始化 ==========
st.set_page_config(
    page_title="射线检测管理系统",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DATA_FILE = "ray_detection_records.json"
if "DATA_PATH" in st.secrets:
    DATA_FILE = os.path.join(st.secrets["DATA_PATH"], DATA_FILE)

if "records" not in st.session_state:
    def load_records():
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            except:
                return []
        return []
    
    def save_records(records):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    st.session_state.records = load_records()
    st.session_state.save_records = save_records
    st.session_state.next_id = max([r["id"] for r in st.session_state.records], default=0) + 1 if st.session_state.records else 1

# ========== 2. 工具函数 ==========
def get_extra_text(device_name, record):
    if device_name in ["九兆", "四兆"]:  # 新增「四兆」，参数与九兆一致
        return f"剂量：{record.get('param1', '无')}Gy"
    elif device_name in ["055射线机", "002射线机", "2505周向机"]:
        return f"电压：{record.get('param1', '无')}kV | 时间：{record.get('param2', '无')}s"
    elif device_name == "450射线机":
        return (f"电压：{record.get('param1', '无')}kV | 电流：{record.get('param2', '无')}mA | "
                f"焦点：{record.get('param3', '无')}mm | 时间：{record.get('param4', '无')}s")
    elif device_name == "Ir192":
        return f"活度：{record.get('param1', '无')}Ci | 时间：{record.get('param2', '无')}s"
    else:
        return "无额外参数"

# ========== 3. 页面主体 ==========
st.title("📝 射线检测数据管理系统")
st.divider()

tab1, tab2 = st.tabs(["📤 数据录入", "🔍 数据查询/删除"])

# ========== 4. 数据录入面板 ==========
with tab1:
    st.subheader("参数录入")
    
    # 设备选择：新增「四兆」
    device = st.selectbox(
        "选择设备",
        ["九兆", "四兆", "055射线机", "002射线机", "2505周向机", "450射线机", "Ir192"],
        key="device_select"
    )
    
    # 跟踪设备变化，触发实时刷新
    if "current_device" not in st.session_state or st.session_state.current_device != device:
        st.session_state.current_device = device
        st.rerun()
    
    with st.form(key="input_form", clear_on_submit=True):
        sheet_type = st.selectbox(
            "选择透照类型",
            ["单片", "双片"],
            key="sheet_select"
        )
        
        thickness = st.text_input("厚度 (mm)（仅数字）", key="thickness")
        focal_length = st.text_input("焦距 (mm)（仅数字）", key="focal")
        
        st.subheader("设备专属参数")
        param1 = param2 = param3 = param4 = ""
        
        # 根据当前设备动态显示参数
        if st.session_state.current_device in ["九兆", "四兆"]:  # 四兆参数与九兆一致
            param1 = st.text_input("剂量 (Gy)", key="param1")
        elif st.session_state.current_device in ["055射线机", "002射线机", "2505周向机"]:
            param1 = st.text_input("电压 (kV)", key="param1")
            param2 = st.text_input("时间 (s)", key="param2")
        elif st.session_state.current_device == "450射线机":
            param1 = st.text_input("电压 (kV)", key="param1")
            param2 = st.text_input("电流 (mA)", key="param2")
            param3 = st.text_input("焦点 (mm)", key="param3")
            param4 = st.text_input("时间 (s)", key="param4")
        elif st.session_state.current_device == "Ir192":
            param1 = st.text_input("活度 (Ci)", key="param1")
            param2 = st.text_input("时间 (s)", key="param2")
        
真正的form_submit_button(extra_text =)
        
        记录 submit_btn:
            记录 写 thickness.- 透照类型：() 记录 - 厚度： focal_length.记录():
                st.mm|焦距：(记录)
            毫米:
- 录入时间：{
                    "id"记录session_state.next_id,
                    "device"col1, col2 = st.session_state.current_device,
                    "sheet_type"列
                    "thickness"与
                    "focal_length"如果
                    "full_time"按钮f查看详情帐号ID：().记录(）"),
                    "param1", key=
                    "param2"记录
                    "param3"detail_text =
膨胀器 f you you|you：[“sheet_type”]
                }
展开=
如果厚度和记录[“厚度”]！=厚度：
持续
st.session_state.matched_records = matched
st.子标题（f"mayoto you Mao（{len(st. session_state. matched_records)}"）
如果不是 st.session_state.matched_records：

st.info（[yodo❤️未找到匹配的记录]）
st.session_state.matched_records中的记录：
使用 st.expander（f"you youth yodo weak ID:{record['ID']}|yodo:{record['device']}"，expanded=True）：
    
extra_text = get_extra_text(record["device"], record)
-透照类型：{record['sheet_type']}
-厚度：{record[]}mm|you:{record['focal_length]}mm
- {extra_text}
        key="query_device"
    )
-录入时间：{记录[*]}
col1, col2 = st.columns(2)
与1：
        key="query_sheet"
    )
如果 st. button（f"yoau yoau you yoau you broyoto（ID:{record['ID']}）"，key=f"detail_{record['ID']}"）：
    
detail_text = f"""
    
记录详情（ID:bioms{record['ID]}）
-设备：{record['device']}
-透照类型：{record['sheet_type']}
副标题f查询结果()
        
长度[]
        条）"如果不 st.session_state.信息:
            "ℹ️ 未找到匹配的记录"其他的为记录["device"]在
                与
            膨胀器f记录记录| 设备：["sheet_type"]记录
                展开=
            if thickness and record["thickness"] != thickness:
                continue
            matched.append(record)
        
st.session_state.matched_records = matched
    
st.子标题（f"查询结果（{len（st. session_state. matched_records）}"）
    
如果不是st.session_state.matched_records：
st.info（“yodo️未找到匹配的记录”）
    else:
st.session_state.matched_records中的记录：
使用st.expander（f"you youth记录 ID:{record['ID']}|yodo：{record['device']}"，expanded=True）：
extra_text = get_extra_text(record["device"], record)
                st.write(f"""
-透照类型：{record['sheet_type']}
-厚度：{record['厚度']}mm|you：{record['focal_length']}mm
- {extra_text}
-录入时间：{record['全职]}
                """)
                
col1, col2 = st.columns(2)
与1：
如果st.button（f"yoau查看详情（ID:{record['ID']}）"，key=f"detail_{record['ID']}"）：
detail_text = f"""
记录详情（ID:bioms{record['ID]}）
-设备：{record['device']}
-透照类型：{record['sheet_type']}
记录
如果
如果
                        """
[厚度（mm）]
col1, col2 = st.
列
“厚度”与
[focal_length]如果
“全职”
                            """
"param1", key=
[param2]记录
"param3"detail_text =
[param4]记录详情 ID:
st.session_state.记录.）（new_record）
-设备:st. You_
detail_text+={record.在（'param3'，[055 mayodo]]]]][[param1]，[002 yodo]）}[2505 yodo]}-
'无'{创纪录
否则如果{record.[450 yodo yodo]（'param2'，-you：）}
无纪录
st.-透照类型：
                            """
st.session_state.next_id += 1
                
├─ 厚度：:
记录（com）
# ========== 5. 数据查询/删除面板 ==========
附表2：
子标题（[bribroyou]）
# 查询设备选择：新增「四兆」
query_device = st.selectbox(
"选择查询设备（可选）",
[]+[九兆]，[055]，[002]，[2505]，[450]，[Ir192]
query_sheet = st.selectbox(
"选择透照类型（可选）",

[..]+[单片]，[..]
query_weight=st. text_input（"厚度（mm）（mm）（mayoto，mayoto）"，key="query_weight"）
query_btn=st.按钮（[you yout you you you]）
