import streamlit as st
import json
import os
from datetime import datetime
import hmac
import pandas as pd
from io import BytesIO

# ========== 1. 页面配置 & 内置初始密码登录（带登录按钮） ==========
st.set_page_config(
    page_title="射线检测管理系统",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 内置初始密码（你可以在这里修改）
DEFAULT_PASSWORD = "qdls123456"

def check_password():
    with st.form("login_form", clear_on_submit=False):
        st.title("🔐 射线检测系统 - 登录")
        password = st.text_input("请输入密码", type="password", key="password")
        submit_btn = st.form_submit_button("登录")

    def password_entered():
        if hmac.compare_digest(password, DEFAULT_PASSWORD):
            st.session_state["logged_in"] = True
        else:
            st.session_state["logged_in"] = False

    if submit_btn:
        password_entered()

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        if submit_btn and not st.session_state["logged_in"]:
            st.error("密码错误，请重试")
        return False
    return True

if not check_password():
    st.stop()

# ========== 2. 数据存储初始化 ==========
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

# ========== 3. 工具函数 ==========
def get_extra_text(device_name, record):
    if device_name in ["九兆", "四兆"]:
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

# ========== 4. 多设备数据导出为Excel（使用openpyxl引擎） ==========
def export_to_excel(records):
    output = BytesIO()
    # 使用openpyxl引擎，无需安装xlsxwriter
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # 按设备分组导出为不同Sheet
        devices = list(set([r["device"] for r in records]))
        for idx, device in enumerate(devices, 1):
            device_records = [r for r in records if r["device"] == device]
            df = pd.DataFrame(device_records)
            
            # 曝光曲线数据：实时计算厚度与剂量/电压的关系
            if device in ["九兆", "四兆"]:
                df["曝光曲线（厚度-剂量）"] = df.apply(lambda x: f"{x['thickness']}mm → {x['param1']}Gy", axis=1)
            elif device in ["055射线机", "002射线机", "2505周向机"]:
                df["曝光曲线（厚度-电压）"] = df.apply(lambda x: f"{x['thickness']}mm → {x['param1']}kV", axis=1)
            elif device == "450射线机":
                df["曝光曲线（厚度-电压）"] = df.apply(lambda x: f"{x['thickness']}mm → {x['param1']}kV", axis=1)
            elif device == "Ir192":
                df["曝光曲线（厚度-活度）"] = df.apply(lambda x: f"{x['thickness']}mm → {x['param1']}Ci", axis=1)
            
            df.to_excel(writer, sheet_name=f"Sheet{idx}（{device}）", index=False)
    
    output.seek(0)
    return output

# ========== 5. 页面主体 ==========
st.title("📝 射线检测数据管理系统")
st.divider()

tab1, tab2, tab3 = st.tabs(["📤 数据录入", "🔍 数据查询/删除", "📥 数据导出"])

# ========== 6. 数据录入面板 ==========
with tab1:
    st.subheader("参数录入")
    
    device = st.selectbox(
        "选择设备",
        ["九兆", "四兆", "055射线机", "002射线机", "2505周向机", "450射线机", "Ir192"],
        key="device_select"
    )
    
    if "current_device" not in st.session_state or st.session_state.current_device != device:
        st.session_state.current_device = device
        st.rerun()
    
    with st.form(key="input_form", clear_on_submit=True):
        sheet_type = st.selectbox(
            "选择透照类型",
            ["单片", "双片"],
            key="sheet_select"
        )
        
        thickness = st.text_input("厚度 (mm)", key="thickness")
        focal_length = st.text_input("焦距 (mm)（仅数字）", key="focal")
        
        st.subheader("设备专属参数")
        param1 = param2 = param3 = param4 = ""
        
        if st.session_state.current_device in ["九兆", "四兆"]:
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
        
        submit_btn = st.form_submit_button("✅ 提交数据")
        
        if submit_btn:
            if not focal_length.isdigit():
                st.error("❌ 焦距必须输入数字！")
            else:
                new_record = {
                    "id": st.session_state.next_id,
                    "device": st.session_state.current_device,
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

# ========== 7. 数据查询/删除面板 ==========
with tab2:
    st.subheader("数据查询/删除")
    
    query_device = st.selectbox(
        "选择查询设备（可选）",
        [""] + ["九兆", "四兆", "055射线机", "002射线机", "2505周向机", "450射线机", "Ir192"],
        key="query_device"
    )
    query_sheet = st.selectbox(
        "选择透照类型（可选）",
        [""] + ["单片", "双片"],
        key="query_sheet"
    )
    query_thickness = st.text_input("厚度 (mm)（可选）", key="query_thickness")
    
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
                        if record["device"] in ["九兆", "四兆"]:
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

# ========== 8. 数据导出面板 ==========
with tab3:
    st.subheader("📥 数据导出（多设备分Sheet）")
    
    if st.session_state.records:
        excel_file = export_to_excel(st.session_state.records)
        st.download_button(
            label="📥 导出所有数据为Excel",
            data=excel_file,
            file_name=f"射线检测数据_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.info("💡 导出说明：\n- 不同设备的数据会自动分到不同Sheet\n- 每个Sheet包含实时计算的曝光曲线数据\n- 曝光曲线格式：厚度 → 剂量/电压/活度")
    else:
        st.warning("⚠️ 暂无数据可导出，请先录入数据")

# ========== 9. 底部信息 ==========
st.divider()
st.caption(f"📊 系统总记录数：{len(st.session_state.records)} | 最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

