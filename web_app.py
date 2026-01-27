import streamlit as st
import json
import os
from datetime import datetime

# 页面配置
st.set_page_config(page_title="射线检测管理系统", page_icon="📝", layout="wide")

# 数据存储
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

def get_extra_text(device_name, record):
    if device_name == "九兆":
        return f"剂量：{record.get('param1', '无')}Gy"
    elif device_name in ["055射线机", "002射线机", "2505周向机"]:
        return f"电压：{record.get('param1', '无')}kV | 时间：{record.get('param2', '无')}s"
    elif device_name == "450射线机":
        return f"电压：{record.get('param1', '无')}kV | 电流：{record.get('param2', '无')}mA | 焦点：{record.get('param3', '无')}mm | 时间：{record.get('param4', '无')}s"
    elif device_name == "Ir192":
        return f"活度：{record.get('param1', '无')}Ci | 时间：{record.get('param2', '无')}s"
    else:
        return "无额外参数"

# 页面主体
st.title("📝 射线检测数据管理系统")
st.divider()

tab1, tab2 = st.tabs(["📤 数据录入", "🔍 数据查询/删除"])

# 数据录入面板
with tab1:
    st.subheader("参数录入")
    
    with st.form(key="input_form", clear_on_submit=True):
        device = st.selectbox(
            "选择设备",
            ["九兆", "055射线机", "002射线机", "2505周向机", "450射线机", "Ir192"],
            key="device_select"
        )
        
        sheet_type = st.selectbox(
            "选择透照类型",
            ["单片", "双片"],
            key="sheet_select"
        )
        
        thickness = st.text_input("厚度 (mm)（仅数字）", key="thickness")
        focal_length = st.text_input("焦距 (mm)（仅数字）", key="focal")
        
        st.subheader("设备专属参数")
        param1 = param2 = param3 = param4 = ""
        
        if device == "九兆":
            param1 = st.text_input("剂量 (Gy)", key="param1")
        elif device in ["055射线机", "002射线机", "2505周向机"]:
            param1 = st.text_input("电压 (kV)", key="param1")
            param2 = st.text_input("时间 (s)", key="param2")
        elif device == "450射线机":
            param1 = st.text_input("电压 (kV)", key="param1")
            param2 = st.text_input("电流 (mA)", key="param2")
            param3 = st.text_input("焦点 (mm)", key="param3")
            param4 = st.text_input("时间 (s)", key="param4")
        elif device == "Ir192":
            param1 = st.text_input("活度 (Ci)", key="param1")
            param2 = st.text_input("时间 (s)", key="param2")
        
        submit_btn = st.form_submit_button("✅ 提交数据")
        
        if submit_btn:
            if not thickness.isdigit() or not focal_length.isdigit():
                st.error("❌ 厚度和焦距必须输入数字！")
            else:
                new_record = {
                    "id": st.session_state.next_id,
                    "device": device,
                    "sheet_type": sheet_type,
                    "thickness": thickness,
                    "focal_length": focal_length,
                    "full_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "param1": param1,
                    "param2": param2,
                    "param3": param3,
                    "param4": param4
                }
                st.session_state.records.append(new_record)
                if st.session_state.save_records(st.session_state.records):
                    st.success("✅ 数据提交成功！")
                    st.session_state.next_id += 1
                else:
                    st.error("❌ 数据保存失败！")

# 数据查询/删除面板
with tab2:
    st.subheader("数据查询/删除")
    
    query_device = st.selectbox(
        "选择查询设备（可选）",
        [""] + ["九兆", "055射线机", "002射线机", "2505周向机", "450射线机", "Ir192"],
        key="query_device"
    )
    query_sheet = st.selectbox(
        "选择透照类型（可选）",
        [""] + ["单片", "双片"],
        key="query_sheet"
    )
    query_thickness = st.text_input("厚度 (mm)（可选，仅数字）", key="query_thickness")
    
    query_btn = st.button("🔍 执行查询")
    
    if query_btn or "matched_records" not in st.session_state:
        device = query_device.strip()
        sheet = query_sheet.strip()
        thickness = query_thickness.strip()
        
        matched = []
        for record in st.session_state.records:
            if device and record["device"] != device:
                continue
            if sheet and record["sheet_type"] != sheet:
                continue
            if thickness and record["thickness"] != thickness:
                continue
            matched.append(record)
        
        st.session_state.matched_records = matched
    
    st.subheader(f"查询结果（共{len(st.session_state.matched_records)}条）")
    
    if not st.session_state.matched_records:
        st.info("ℹ️ 未找到匹配的记录")
    else:
        for record in st.session_state.matched_records:
            with st.expander(f"📋 记录ID：{record['id']} | 设备：{record['device']}", expanded=True):
                extra_text = get_extra_text(record["device"], record)
                st.write(f"""
                - 透照类型：{record['sheet_type']}
                - 厚度：{record['thickness']}mm | 焦距：{record['focal_length']}mm
                - {extra_text}
                - 录入时间：{record['full_time']}
                """)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"📄 查看详情（ID：{record['id']}）", key=f"detail_{record['id']}"):
                        detail_text = f"""
                        📋 记录详情（ID：{record['id']}）
                        ├─ 设备：{record['device']}
                        ├─ 透照类型：{record['sheet_type']}
                        ├─ 厚度：{record['thickness']}mm
                        ├─ 焦距：{record['focal_length']}mm
                        ├─ 录入时间：{record['full_time']}
                        """
                        if record["device"] == "九兆":
                            detail_text += f"└─ 剂量：{record.get('param1', '无')}Gy"
                        elif record["device"] in ["055射线机", "002射线机", "2505周向机"]:
                            detail_text += f"""
                            ├─ 电压：{record.get('param1', '无')}kV
                            └─ 时间：{record.get('param2', '无')}s
                            """
                        elif record["device"] == "450射线机":
                            detail_text += f"""
                            ├─ 电压：{record.get('param1', '无')}kV
                            ├─ 电流：{record.get('param2', '无')}mA
                            ├─ 焦点：{record.get('param3', '无')}mm
                            └─ 时间：{record.get('param4', '无')}s
                            """
                        elif record["device"] == "Ir192":
                            detail_text += f"""
                            ├─ 活度：{record.get('param1', '无')}Ci
                            └─ 时间：{record.get('param2', '无')}s
                            """
                        st.text(detail_text)
                
                with col2:
                    delete_key = f"delete_record_{record['id']}"
                    if st.button(f"🗑️ 删除记录（ID：{record['id']}）", key=delete_key):
                        st.session_state.records = [r for r in st.session_state.records if r["id"] != record["id"]]
                        st.session_state.matched_records = [r for r in st.session_state.matched_records if r["id"] != record["id"]]
                        st.session_state.save_records(st.session_state.records)
                        st.success(f"✅ 记录ID：{record['id']} 已删除！")
                        try:
                            st.experimental_rerun()
                        except:
                            st.rerun()

st.divider()
st.caption(f"📊 系统总记录数：{len(st.session_state.records)} | 最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
