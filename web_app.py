import streamlit as st
import json
import os
from datetime import datetime

# ========== 数据存储配置（和原代码兼容） ==========
DATA_FILE = "ray_detection_records.json"

# 初始化数据
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
    except Exception as e:
        st.error(f"保存失败：{str(e)}")
        return False

# 初始化全局数据
if "records" not in st.session_state:
    st.session_state.records = load_records()
if "next_id" not in st.session_state:
    st.session_state.next_id = max([r["id"] for r in st.session_state.records], default=0) + 1 if st.session_state.records else 1

# ========== 网页界面配置 ==========
st.set_page_config(
    page_title="射线检测参数管理",
    page_icon="📝",
    layout="wide"  # 宽屏布局
)

# 标题
st.title("📝 射线检测参数管理系统")

# 选项卡：录入/查询
tab1, tab2 = st.tabs(["参数录入", "数据查询/删除"])

# ========== 1. 参数录入面板 ==========
with tab1:
    st.subheader("参数录入")
    
    # 表单布局
    with st.form(key="input_form", clear_on_submit=True):
        # 设备选择
        device = st.selectbox(
            "选择设备",
            ["九兆", "055射线机", "002射线机", "2505周向机", "450射线机", "Ir192"]
        )
        
        # 透照类型
        sheet_type = st.selectbox("选择透照类型", ["单片", "双片"])
        
        # 基础参数
        col1, col2 = st.columns(2)
        with col1:
            thickness = st.text_input("厚度 (mm)（仅数字）", placeholder="例如：10")
        with col2:
            focal_length = st.text_input("焦距 (mm)（仅数字）", placeholder="例如：800")
        
        # 设备专属参数（动态显示）
        param1 = param2 = param3 = param4 = ""
        if device == "九兆":
            param1 = st.text_input("剂量 (Gy)", placeholder="例如：5")
        elif device in ["055射线机", "002射线机", "2505周向机"]:
            col3, col4 = st.columns(2)
            with col3:
                param1 = st.text_input("电压 (kV)", placeholder="例如：150")
            with col4:
                param2 = st.text_input("时间 (s)", placeholder="例如：30")
        elif device == "450射线机":
            col3, col4 = st.columns(2)
            with col3:
                param1 = st.text_input("电压 (kV)", placeholder="例如：200")
                param3 = st.text_input("焦点 (mm)", placeholder="例如：2")
            with col4:
                param2 = st.text_input("电流 (mA)", placeholder="例如：5")
                param4 = st.text_input("时间 (s)", placeholder="例如：40")
        elif device == "Ir192":
            col3, col4 = st.columns(2)
            with col3:
                param1 = st.text_input("活度 (Ci)", placeholder="例如：10")
            with col4:
                param2 = st.text_input("时间 (s)", placeholder="例如：25")
        
        # 提交按钮
        submit_btn = st.form_submit_button("提交数据", type="primary")
        
        # 提交逻辑
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
                if save_records(st.session_state.records):
                    st.session_state.next_id += 1
                    st.success("✅ 数据提交成功！")
                else:
                    st.error("❌ 数据保存失败！")

# ========== 2. 数据查询/删除面板 ==========
with tab2:
    st.subheader("数据查询/删除")
    
    # 查询条件
    col1, col2, col3 = st.columns(3)
    with col1:
        query_device = st.selectbox("筛选设备（可选）", [""] + ["九兆", "055射线机", "002射线机", "2505周向机", "450射线机", "Ir192"])
    with col2:
        query_sheet = st.selectbox("筛选透照类型（可选）", [""] + ["单片", "双片"])
    with col3:
        query_thickness = st.text_input("筛选厚度 (mm)（可选）", placeholder="例如：10")
    
    # 查询按钮
    if st.button("执行查询", type="secondary"):
        # 筛选数据
        matched = []
        for record in st.session_state.records:
            if query_device and record["device"] != query_device:
                continue
            if query_sheet and record["sheet_type"] != query_sheet:
                continue
            if query_thickness and record["thickness"] != query_thickness:
                continue
            matched.append(record)
        
        # 显示结果
        if not matched:
            st.info("ℹ️ 未找到匹配的记录")
        else:
            st.subheader(f"查询结果（共{len(matched)}条）")
            # 遍历显示每条记录
            for idx, record in enumerate(matched):
                # 记录卡片
                with st.expander(f"📋 记录ID：{record['id']} | 设备：{record['device']} | 录入时间：{record['full_time']}", expanded=True):
                    # 显示详情
                    st.write(f"""
                    - 透照类型：{record['sheet_type']}
                    - 厚度：{record['thickness']}mm
                    - 焦距：{record['focal_length']}mm
                    """)
                    
                    # 显示设备专属参数
                    if record["device"] == "九兆":
                        st.write(f"- 剂量：{record['param1']}Gy")
                    elif record["device"] in ["055射线机", "002射线机", "2505周向机"]:
                        st.write(f"- 电压：{record['param1']}kV | 时间：{record['param2']}s")
                    elif record["device"] == "450射线机":
                        st.write(f"- 电压：{record['param1']}kV | 电流：{record['param2']}mA | 焦点：{record['param3']}mm | 时间：{record['param4']}s")
                    elif record["device"] == "Ir192":
                        st.write(f"- 活度：{record['param1']}Ci | 时间：{record['param2']}s")
                    
                    # 删除按钮
                    if st.button(f"删除本条记录（ID：{record['id']}）", key=f"del_{idx}", type="destructive"):
                        # 从全局数据中删除
                        st.session_state.records = [r for r in st.session_state.records if r["id"] != record["id"]]
                        save_records(st.session_state.records)
                        st.success(f"✅ 记录ID：{record['id']} 已删除！")
                        # 刷新页面
                        st.rerun()

# ========== 底部信息 ==========
st.divider()
st.caption(f"📊 总记录数：{len(st.session_state.records)} | 最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
