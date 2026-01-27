import streamlit as st
import json
import os
from datetime import datetime
import sys

# ========== 1. 页面配置 & 数据存储初始化 ==========
# 页面基础配置（适配手机+电脑）
st.set_page_config(
    page_title="射线检测管理系统",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 数据文件路径（适配Streamlit云端部署）
DATA_FILE = "ray_detection_records.json"
if "DATA_PATH" in st.secrets:
    DATA_FILE = os.path.join(st.secrets["DATA_PATH"], DATA_FILE)

# 初始化会话状态（避免重复加载）
if "records" not in st.session_state:
    # 加载数据
    def load_records():
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            except:
                return []
        return []
    
    # 保存数据
    def save_records(records):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    st.session_state.records = load_records()
    st.session_state.save_records = save_records
    # 计算下一个ID
    if st.session_state.records:
        st.session_state.next_id = max([r["id"] for r in st.session_state.records]) + 1
    else:
        st.session_state.next_id = 1

# ========== 2. 工具函数 ==========
def get_extra_text(device_name, record):
    """生成设备专属参数文本"""
    if device_name == "九兆":
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

# 选项卡：录入/查询（对应Kivy的两个Screen）
tab1, tab2 = st.tabs(["📤 数据录入", "🔍 数据查询/删除"])

# ========== 4. 数据录入面板（对应InputScreen） ==========
with tab1:
    st.subheader("参数录入")
    
    # 表单布局（清空逻辑与Kivy一致）
    with st.form(key="input_form", clear_on_submit=True):
        # 设备选择（替代Spinner）
        device = st.selectbox(
            "选择设备",
            ["九兆", "055射线机", "002射线机", "2505周向机", "450射线机", "Ir192"],
            key="device_select"
        )
        
        # 透照类型
        sheet_type = st.selectbox(
            "选择透照类型",
            ["单片", "双片"],
            key="sheet_select"
        )
        
        # 基础参数
        col1, col2 = st.columns(2)
        with col1:
            thickness = st.text_input("厚度 (mm)（仅数字）", key="thickness")
        with col2:
            focal_length = st.text_input("焦距 (mm)（仅数字）", key="focal")
        
        # 设备专属参数（动态显示，对应update_param_inputs）
        st.subheader("设备专属参数")
        param1 = param2 = param3 = param4 = ""
        
        if device == "九兆":
            param1 = st.text_input("剂量 (Gy)", key="param1")
        elif device in ["055射线机", "002射线机", "2505周向机"]:
            col3, col4 = st.columns(2)
            with col3:
                param1 = st.text_input("电压 (kV)", key="param1")
            with col4:
                param2 = st.text_input("时间 (s)", key="param2")
        elif device == "450射线机":
            col3, col4 = st.columns(2)
            with col3:
                param1 = st.text_input("电压 (kV)", key="param1")
                param3 = st.text_input("焦点 (mm)", key="param3")
            with col4:
                param2 = st.text_input("电流 (mA)", key="param2")
                param4 = st.text_input("时间 (s)", key="param4")
        elif device == "Ir192":
            col3, col4 = st.columns(2)
            with col3:
                param1 = st.text_input("活度 (Ci)", key="param1")
            with col4:
                param2 = st.text_input("时间 (s)", key="param2")
        
        # 提交按钮（替代Kivy的submit_btn）
        submit_btn = st.form_submit_button("✅ 提交数据", type="primary")
        
        # 提交逻辑（与Kivy一致）
        if submit_btn:
            # 验证输入
            if not thickness.isdigit() or not focal_length.isdigit():
                st.error("❌ 厚度和焦距必须输入数字！")
            else:
                # 构造新记录
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
                
                # 保存数据
                st.session_state.records.append(new_record)
                if st.session_state.save_records(st.session_state.records):
                    st.success("✅ 数据提交成功！")
                    st.session_state.next_id += 1
                else:
                    st.error("❌ 数据保存失败！")

# ========== 5. 数据查询/删除面板（对应QueryScreen） ==========
with tab2:
    st.subheader("数据查询/删除")
    
    # 查询条件（与Kivy一致）
    st.subheader("查询条件")
    col1, col2, col3 = st.columns(3)
    with col1:
        query_device = st.selectbox(
            "选择查询设备（可选）",
            [""] + ["九兆", "055射线机", "002射线机", "2505周向机", "450射线机", "Ir192"],
            key="query_device"
        )
    with col2:
        query_sheet = st.selectbox(
            "选择透照类型（可选）",
            [""] + ["单片", "双片"],
            key="query_sheet"
        )
    with col3:
        query_thickness = st.text_input("厚度 (mm)（可选，仅数字）", key="query_thickness")
    
    # 查询按钮
    query_btn = st.button("🔍 执行查询", type="secondary")
    
    # 执行查询（默认加载所有数据）
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
    
    # 显示查询结果
    st.subheader(f"查询结果（共{len(st.session_state.matched_records)}条）")
    
    if not st.session_state.matched_records:
        st.info("ℹ️ 未找到匹配的记录")
    else:
        # 遍历显示记录（替代Kivy的ScrollView+BoxLayout）
        for record in st.session_state.matched_records:
            # 记录卡片（替代ColoredBoxLayout）
            with st.expander(f"📋 记录ID：{record['id']} | 设备：{record['device']}", expanded=True):
                # 基本信息（与Kivy一致）
                extra_text = get_extra_text(record["device"], record)
                st.write(f"""
                - 透照类型：{record['sheet_type']}
                - 厚度：{record['thickness']}mm | 焦距：{record['focal_length']}mm
                - {extra_text}
                - 录入时间：{record['full_time']}
                """)
                
                # 操作按钮（详情+删除，对应Kivy的detail_btn/delete_btn）
                col1, col2 = st.columns(2)
                with col1:
                    # 查看详情（替代Popup）
                    if st.button(f"📄 查看详情（ID：{record['id']}）", key=f"detail_{record['id']}"):
                        detail_text = f"""
                        📋 记录详情（ID：{record['id']}）
                        ├─ 设备：{record['device']}
                        ├─ 透照类型：{record['sheet_type']}
                        ├─ 厚度：{record['thickness']}mm
                        ├─ 焦距：{record['focal_length']}mm
                        ├─ 录入时间：{record['full_time']}
                        """
                        # 设备专属参数
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
                    # 删除记录（修复版，避免key冲突）
                    import time
                    delete_key = f"del_{record['id']}_{int(time.time() * 1000)}"
                    if st.button(f"🗑️ 删除记录（ID：{record['id']}）", key=delete_key, type="destructive"):
                        # 移除记录
                        st.session_state.records = [r for r in st.session_state.records if r["id"] != record["id"]]
                        st.session_state.matched_records = [r for r in st.session_state.matched_records if r["id"] != record["id"]]
                        # 保存数据
                        st.session_state.save_records(st.session_state.records)
                        st.success(f"✅ 记录ID：{record['id']} 已删除！")
                        st.rerun()  # 刷新页面

# ========== 6. 底部信息 ==========
st.divider()
st.caption(f"📊 系统总记录数：{len(st.session_state.records)} | 最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
