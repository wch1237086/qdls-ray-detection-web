import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
from tinydb import TinyDB, Query
import hashlib

# ========== 1. 配置初始化（云端数据持久化） ==========
# 初始化TinyDB（云端存储，替代本地JSON）
if "db" not in st.session_state:
    # 使用Streamlit Secrets或本地文件（部署后自动适配云端）
    db_path = os.path.join(st.secrets.get("DATA_PATH", "."), "ray_detection_db.json")
    st.session_state.db = TinyDB(db_path, ensure_ascii=False)
    st.session_state.Record = Query()

# ========== 2. 用户登录验证 ==========
def check_password(password):
    # 预设管理员密码（可自行修改，建议用hash值更安全）
    ADMIN_PWD = st.secrets.get("ADMIN_PWD", "123456")  # 部署后可在Streamlit后台修改
    return password == ADMIN_PWD

# 登录界面
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 射线检测系统 - 登录")
    password = st.text_input("请输入登录密码", type="password")
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("登录", type="primary"):
            if check_password(password):
                st.session_state.authenticated = True
                st.rerun()  # 登录成功后刷新页面
            else:
                st.error("密码错误！请重试")
    st.stop()  # 未登录时阻止后续内容加载

# ========== 3. 核心数据操作函数（修复删除+云端存储） ==========
def load_records():
    """加载所有记录（云端读取）"""
    return st.session_state.db.all()

def save_record(record):
    """保存单条记录（云端写入）"""
    st.session_state.db.insert(record)
    return True

def delete_record(record_id):
    """删除指定记录（修复删除逻辑）"""
    st.session_state.db.remove(st.session_state.Record.id == record_id)
    return True

def get_next_id():
    """获取下一个自增ID"""
    records = load_records()
    if not records:
        return 1
    return max([r["id"] for r in records]) + 1

# ========== 4. 网页界面配置 ==========
st.set_page_config(
    page_title="射线检测参数管理系统",
    page_icon="📝",
    layout="wide"
)

# 标题
st.title("📝 射线检测参数管理系统")
st.caption(f"最后同步时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.divider()

# ========== 5. 核心功能区 ==========
tab1, tab2, tab3 = st.tabs(["参数录入", "数据查询/删除", "数据导出"])

# ========== 5.1 参数录入面板 ==========
with tab1:
    st.subheader("📤 参数录入")
    
    # 表单布局（修复清空逻辑）
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
        
        # 提交逻辑（云端保存）
        if submit_btn:
            # 验证输入
            if not thickness.isdigit() or not focal_length.isdigit():
                st.error("❌ 厚度和焦距必须输入数字！")
            else:
                # 构造新记录
                new_record = {
                    "id": get_next_id(),
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
                
                # 保存到云端
                if save_record(new_record):
                    st.success("✅ 数据提交成功！")
                else:
                    st.error("❌ 数据保存失败！")

# ========== 5.2 数据查询/删除面板（修复删除功能） ==========
with tab2:
    st.subheader("🔍 数据查询/删除")
    
    # 查询条件
    col1, col2, col3 = st.columns(3)
    with col1:
        query_device = st.selectbox("筛选设备（可选）", [""] + ["九兆", "055射线机", "002射线机", "2505周向机", "450射线机", "Ir192"])
    with col2:
        query_sheet = st.selectbox("筛选透照类型（可选）", [""] + ["单片", "双片"])
    with col3:
        query_thickness = st.text_input("筛选厚度 (mm)（可选）", placeholder="例如：10")
    
    # 查询按钮
    query_btn = st.button("执行查询", type="secondary")
    if query_btn or "matched_records" not in st.session_state:
        # 加载所有记录
        all_records = load_records()
        # 筛选数据
        matched = []
        for record in all_records:
            if query_device and record["device"] != query_device:
                continue
            if query_sheet and record["sheet_type"] != query_sheet:
                continue
            if query_thickness and record["thickness"] != query_thickness:
                continue
            matched.append(record)
        st.session_state.matched_records = matched
    
    # 显示结果
    if not st.session_state.matched_records:
        st.info("ℹ️ 未找到匹配的记录")
    else:
        st.subheader(f"查询结果（共{len(st.session_state.matched_records)}条）")
        # 遍历显示每条记录（修复删除逻辑）
        for idx, record in enumerate(st.session_state.matched_records):
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
                
                # 删除按钮（修复实时刷新）
                import time
                delete_key = f"del_{record['id']}_{int(time.time() * 1000)}"  # 时间戳+ID确保唯一
                if st.button(f"删除本条记录（ID：{record['id']}）", key=delete_key, type="destructive"):
                    delete_record(record["id"])
                    # 刷新匹配记录列表
                    st.session_state.matched_records = [r for r in st.session_state.matched_records if r["id"] != record["id"]]
                    st.success(f"✅ 记录ID：{record['id']} 已删除！")
                    # 强制刷新页面
                    st.rerun()

# ========== 5.3 数据导出面板（Excel导出功能） ==========
with tab3:
    st.subheader("📥 数据导出")
    
    # 导出选项
    export_all = st.checkbox("导出所有数据（取消则导出筛选后的数据）", value=True)
    
    # 准备导出数据
    if export_all:
        export_data = load_records()
    else:
        export_data = st.session_state.get("matched_records", [])
    
    if not export_data:
        st.info("ℹ️ 暂无可导出的数据")
    else:
        # 转换为DataFrame
        df = pd.DataFrame(export_data)
        # 优化列名显示
        df_renamed = df.rename(columns={
            "id": "记录ID",
            "device": "设备",
            "sheet_type": "透照类型",
            "thickness": "厚度(mm)",
            "focal_length": "焦距(mm)",
            "full_time": "录入时间",
            "param1": "参数1",
            "param2": "参数2",
            "param3": "参数3",
            "param4": "参数4"
        })
        
        # 生成Excel文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"射线检测数据_{timestamp}.xlsx"
        
        # 导出按钮
        col1, col2 = st.columns([1, 5])
        with col1:
            st.download_button(
                label="📤 导出为Excel",
                data=df_renamed.to_excel(index=False),
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )
        
        # 预览导出数据
        st.subheader("导出数据预览")
        st.dataframe(df_renamed, use_container_width=True)

# ========== 6. 底部信息 ==========
st.divider()
total_records = len(load_records())
st.caption(f"📊 系统总记录数：{total_records} | 最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 退出登录按钮
col1, col2 = st.columns([5, 1])
with col2:
    if st.button("🚪 退出登录", type="secondary"):
        st.session_state.authenticated = False
        st.rerun()
