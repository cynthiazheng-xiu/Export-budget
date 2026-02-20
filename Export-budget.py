import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import re
import os
import openpyxl

# 页面配置
st.set_page_config(
    page_title="出口预算表 - 技能大赛版",
    page_icon="📊",
    layout="wide"
)

# 自定义样式
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        color: white;
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 15px;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .step-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        border-left: 5px solid #2a5298;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .step-header {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
        background-color: #e9ecef;
        padding: 10px 15px;
        border-radius: 8px;
    }
    .step-badge {
        background-color: #2a5298;
        color: white;
        padding: 8px 20px;
        border-radius: 25px;
        font-size: 1rem;
        font-weight: bold;
        margin-right: 20px;
        min-width: 120px;
        text-align: center;
    }
    .step-title {
        font-size: 1.3rem;
        color: #1e3c72;
        font-weight: 600;
    }
    .fetch-button {
        background-color: #28a745;
        color: white;
        border: none;
        padding: 5px 15px;
        border-radius: 5px;
        cursor: pointer;
        font-size: 0.9rem;
    }
    .fetch-button:hover {
        background-color: #218838;
    }
    .search-box {
        background-color: #e3f2fd;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #2196f3;
        margin-bottom: 15px;
    }
    .file-path {
        font-family: monospace;
        background-color: #f5f5f5;
        padding: 5px 10px;
        border-radius: 3px;
        border: 1px solid #ddd;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
        margin: 10px 0;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
        margin: 10px 0;
    }
    .excel-table {
        background-color: white;
        border: 2px solid #dee2e6;
        border-radius: 8px;
        padding: 0;
        margin: 15px 0;
        overflow: hidden;
    }
    .excel-header {
        background-color: #2a5298;
        color: white;
        font-weight: bold;
        padding: 12px;
        display: grid;
        grid-template-columns: 150px 200px 200px 1fr;
    }
    .excel-row {
        display: grid;
        grid-template-columns: 150px 200px 200px 1fr;
        border-bottom: 1px solid #dee2e6;
        padding: 10px;
    }
    .excel-row:nth-child(even) {
        background-color: #f8f9fa;
    }
    .excel-row:hover {
        background-color: #e9ecef;
    }
    .result-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# 标题
st.markdown('<div class="main-title">📊 出口预算表 - 全国职业院校技能大赛版</div>', unsafe_allow_html=True)

# ==================== Excel文件路径设置 ====================
st.sidebar.markdown("### 📁 Excel数据源设置")
excel_path = st.sidebar.text_input("Excel文件路径", value=r"C:\Basic Information\Data.xlsx")
st.sidebar.markdown(f"<div class='file-path'>当前路径: {excel_path}</div>", unsafe_allow_html=True)

# 检查文件是否存在
file_exists = os.path.exists(excel_path)
if file_exists:
    st.sidebar.success("✅ Excel文件存在")
else:
    st.sidebar.error("❌ Excel文件不存在，请检查路径")

# ==================== 读取Excel表格的函数 ====================
@st.cache_data(ttl=10)  # 缓存10秒，这样文件更新后可以重新读取
def read_excel_sheet(file_path, sheet_name):
    """读取Excel指定sheet"""
    try:
        if os.path.exists(file_path):
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            return df
        else:
            return None
    except Exception as e:
        st.error(f"读取Excel出错: {str(e)}")
        return None

# ==================== 从商品信息表查找商品的函数 ====================
def find_product_by_code_or_name(df, search_term):
    """根据商品编号或英文名称查找商品"""
    if df is None or df.empty:
        return None
    
    # 假设商品信息表的格式：
    # 第4行开始是数据，D列是商品编号，E列是商品名称，F列是英文名称
    try:
        # 获取数据区域（从第4行开始）
        data = df.iloc[3:].copy()
        data.columns = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U']
        
        # 查找匹配的行
        mask = (data['D'].astype(str).str.contains(str(search_term), na=False)) | \
               (data['F'].astype(str).str.contains(str(search_term), na=False, case=False))
        
        matches = data[mask]
        if not matches.empty:
            return matches.iloc[0].to_dict()
        return None
    except Exception as e:
        st.error(f"查找商品出错: {str(e)}")
        return None

# ==================== 从HS表查找的函数 ====================
def find_hs_by_code(df, hs_code):
    """根据HS编码查找HS信息"""
    if df is None or df.empty:
        return None
    
    try:
        # HS表格式：第4行开始是数据，D列是HS编码
        data = df.iloc[3:].copy()
        data.columns = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N']
        
        mask = data['D'].astype(str).str.contains(str(hs_code), na=False)
        matches = data[mask]
        if not matches.empty:
            return matches.iloc[0].to_dict()
        return None
    except Exception as e:
        st.error(f"查找HS信息出错: {str(e)}")
        return None

# ==================== 从运费单价表查找的函数 ====================
def find_freight_by_route(df, export_country, import_country):
    """根据进出口国查找运费单价"""
    if df is None or df.empty:
        return None
    
    try:
        # 运费单价表格式
        data = df.iloc[3:].copy()  # 从第4行开始
        # 这里需要根据实际的Excel结构调整列映射
        return None
    except Exception as e:
        st.error(f"查找运费信息出错: {str(e)}")
        return None

# ==================== 初始化session state ====================
if 'best_freight' not in st.session_state:
    st.session_state.best_freight = 0
if 'best_container' not in st.session_state:
    st.session_state.best_container = None
if 'container_options' not in st.session_state:
    st.session_state.container_options = []
if 'suggested_price' not in st.session_state:
    st.session_state.suggested_price = 0
if 'calculated' not in st.session_state:
    st.session_state.calculated = False
if 'product_data' not in st.session_state:
    st.session_state.product_data = {}
if 'hs_data' not in st.session_state:
    st.session_state.hs_data = {}

# ==================== 第一步：客户信息 ====================
st.markdown("""
<div class="step-container">
    <div class="step-header">
        <span class="step-badge">第一步</span>
        <span class="step-title">客户信息</span>
    </div>
</div>
""", unsafe_allow_html=True)

col_cust1, col_cust2 = st.columns(2)

with col_cust1:
    st.markdown("##### 出口商信息")
    if st.button("📥 从客户信息表抓取", key="fetch_customer"):
        df = read_excel_sheet(excel_path, "客户信息表")
        if df is not None:
            st.success("✅ 客户信息抓取成功!")
            # 这里可以根据实际Excel格式填充数据
        else:
            st.error("无法读取客户信息表")
    
    exporter_name = st.text_input("公司全称", "平尼克国际贸易公司")
    exporter_name_short = st.text_input("公司简称", "平尼克国际")
    exporter_name_en = st.text_input("公司英文名", "Pinic International Trading")
    exporter_address = st.text_input("公司地址", "菲律宾马尼拉宾农多马德里街513号")

with col_cust2:
    st.markdown("##### 进口商信息")
    importer_name = st.text_input("进口商名称", "罗伯茨世界贸易有限公司")
    importer_name_en = st.text_input("进口商英文名", "Roberts World Traders Inc.")
    importer_address = st.text_input("进口商地址", "加拿大不列颠哥伦比亚维多利亚白桦新月街4号")
    importer_contact = st.text_input("进口商联系人", "艾伦·博尔赫斯")

# ==================== 第二步：产品信息 ====================
st.markdown("""
<div class="step-container">
    <div class="step-header">
        <span class="step-badge">第二步</span>
        <span class="step-title">产品信息</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 商品搜索框
st.markdown('<div class="search-box">', unsafe_allow_html=True)
col_search1, col_search2 = st.columns([3, 1])
with col_search1:
    search_term = st.text_input("请输入商品编号或英文名称进行搜索", placeholder="例如: P010 或 Vending machine")
with col_search2:
    if st.button("🔍 搜索商品", use_container_width=True):
        if file_exists and search_term:
            df_product = read_excel_sheet(excel_path, "商品信息表")
            product_info = find_product_by_code_or_name(df_product, search_term)
            if product_info:
                st.session_state.product_data = product_info
                st.success(f"✅ 找到商品: {product_info.get('E', '未知')}")
            else:
                st.error("未找到匹配的商品")
st.markdown('</div>', unsafe_allow_html=True)

col_prod1, col_prod2 = st.columns(2)

with col_prod1:
    # 从session state获取数据，如果没有则用默认值
    product_code = st.text_input("商品编号", value=st.session_state.product_data.get('D', 'P010'))
    product_name = st.text_input("商品名称", value=st.session_state.product_data.get('E', '自动售货机'))
    product_name_en = st.text_input("英文名称", value=st.session_state.product_data.get('F', 'Vending machine'))
    product_type = st.text_input("货物类型", value=st.session_state.product_data.get('G', '机器、机械器具、电气设备及其零件'))

with col_prod2:
    sales_unit = st.text_input("销售单位", value=st.session_state.product_data.get('K', '台(SET)'))
    package_unit = st.text_input("包装单位", value=st.session_state.product_data.get('M', '托盘(PALLET)'))
    unit_conversion = st.text_input("单位换算", value=st.session_state.product_data.get('L', '1 SET/PALLET'))
    
    # 毛重、净重、体积需要从后面的列获取
    gross_weight = st.text_input("毛重", value=st.session_state.product_data.get('N', '280.00KGS/托盘'))
    net_weight = st.text_input("净重", value=st.session_state.product_data.get('O', '220.00KGS/托盘'))
    volume = st.text_input("体积", value=st.session_state.product_data.get('P', '2.55CBM/托盘'))

# ==================== 第三步：HS信息 ====================
st.markdown("""
<div class="step-container">
    <div class="step-header">
        <span class="step-badge">第三步</span>
        <span class="step-title">HS信息</span>
    </div>
</div>
""", unsafe_allow_html=True)

col_hs1, col_hs2 = st.columns(2)

with col_hs1:
    hs_search = st.text_input("请输入HS编码", value=st.session_state.product_data.get('Q', '8476810000'))
    if st.button("📥 从HS表抓取", key="fetch_hs"):
        if file_exists:
            df_hs = read_excel_sheet(excel_path, "HS表")
            hs_info = find_hs_by_code(df_hs, hs_search)
            if hs_info:
                st.session_state.hs_data = hs_info
                st.success("✅ HS信息抓取成功!")
            else:
                st.error("未找到匹配的HS编码")
    
    hs_code = st.text_input("HS编码", value=hs_search)
    customs_condition = st.text_input("海关监管条件", value=st.session_state.hs_data.get('F', '无'))
    inspection_type = st.text_input("检验检疫类别", value=st.session_state.hs_data.get('G', '无'))

with col_hs2:
    legal_unit = st.text_input("法定单位", value=st.session_state.product_data.get('R', '台(SET)'))
    pref_tax_rate = st.number_input("优惠税率(%)", value=float(st.session_state.hs_data.get('H', 50)))
    vat_rate = st.number_input("增值税率(%)", value=float(st.session_state.hs_data.get('I', 13)))
    export_rebate_rate = st.number_input("出口退税率(%)", value=float(st.session_state.hs_data.get('N', 13)))

# ==================== 第四步：物流信息 ====================
st.markdown("""
<div class="step-container">
    <div class="step-header">
        <span class="step-badge">第四步</span>
        <span class="step-title">物流信息</span>
    </div>
</div>
""", unsafe_allow_html=True)

col_log1, col_log2 = st.columns(2)

with col_log1:
    if st.button("📥 从运费单价表抓取", key="fetch_freight"):
        if file_exists:
            df_freight = read_excel_sheet(excel_path, "运费单价")
            if df_freight is not None:
                st.success("✅ 物流信息抓取成功!")
                # 这里可以根据实际Excel格式填充数据
    
    st.markdown("**普柜单价 (USD)**")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        lcl_w_normal = st.number_input("LCL(W)", value=73)
        container_20_normal = st.number_input("20'GP", value=1452)
        container_40_normal = st.number_input("40'GP", value=2613)
    with col_p2:
        lcl_m_normal = st.number_input("LCL(M)", value=88)
        container_40hc_normal = st.number_input("40'HC", value=3135)

with col_log2:
    st.markdown("**冻柜单价 (USD)**")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        lcl_w_frozen = st.number_input("LCL(W)冻", value=146)
        container_20_frozen = st.number_input("20'RF", value=2903)
        container_40_frozen = st.number_input("40'RF", value=5225)
    with col_f2:
        lcl_m_frozen = st.number_input("LCL(M)冻", value=189)
        container_40rh_frozen = st.number_input("40'RH", value=6270)

# ==================== 第五步：交易信息 ====================
st.markdown("""
<div class="step-container">
    <div class="step-header">
        <span class="step-badge">第五步</span>
        <span class="step-title">交易信息</span>
    </div>
</div>
""", unsafe_allow_html=True)

col_trade1, col_trade2, col_trade3 = st.columns(3)

with col_trade1:
    if st.button("📥 从汇率表抓取", key="fetch_rate"):
        if file_exists:
            df_rate = read_excel_sheet(excel_path, "汇率表")
            if df_rate is not None:
                st.success("✅ 汇率信息抓取成功!")
                # 这里可以根据实际Excel格式填充数据
    
    quantity = st.number_input("交易数量", value=182, step=1)
    purchase_price = st.number_input("采购单价", value=4778.0, step=100.0)

with col_trade2:
    account_balance = st.number_input("账户本币余额", value=1888000.0, step=1000.0)
    exchange_rate = st.number_input("USD/CAD 汇率", value=1.368, step=0.001, format="%.3f")
    trade_term = st.selectbox("贸易术语", ["EXW", "FCA", "FAS", "FOB", "CFR", "CIF", "CIP", "DAP", "DPU", "DDP"])

with col_trade3:
    payment = st.selectbox("支付方式", ["T/T", "L/C", "D/P", "T/T+LC"])
    expected_profit_rate = st.slider("预期利润率(%)", 0, 50, 15)
    transport_note = st.selectbox("运输要求", ["普通", "冷藏", "冷冻"])

# ==================== 提取数值用于计算 ====================
def extract_number(text):
    try:
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", str(text))
        return float(numbers[0]) if numbers else 0
    except:
        return 0

# 计算货物总量
single_gross = extract_number(gross_weight)
single_net = extract_number(net_weight)
single_volume = extract_number(volume)
units_per_package = extract_number(unit_conversion)

if units_per_package > 0:
    total_packages = np.ceil(quantity / units_per_package)
else:
    total_packages = quantity

total_gross = total_packages * single_gross
total_net = total_packages * single_net
total_volume = total_packages * single_volume

# ==================== 第六步：计算报价 ====================
st.markdown("""
<div class="step-container">
    <div class="step-header">
        <span class="step-badge">第六步</span>
        <span class="step-title">计算报价</span>
    </div>
</div>
""", unsafe_allow_html=True)

col_calc1, col_calc2 = st.columns(2)

with col_calc1:
    if st.button("🚢 计算最优集装箱", use_container_width=True):
        # 创建集装箱数据
        container_types = {
            "20'普柜": {"体积": 33, "重量": 25000, "单价": container_20_normal, "类型": "普柜"},
            "40'普柜": {"体积": 67, "重量": 29000, "单价": container_40_normal, "类型": "普柜"},
            "40'高柜": {"体积": 76, "重量": 29000, "单价": container_40hc_normal, "类型": "普柜"},
            "20'冻柜": {"体积": 27, "重量": 27400, "单价": container_20_frozen, "类型": "冻柜"},
            "40'冻柜": {"体积": 58, "重量": 27700, "单价": container_40_frozen, "类型": "冻柜"},
            "40'冻高": {"体积": 66, "重量": 29000, "单价": container_40rh_frozen, "类型": "冻柜"}
        }
        
        container_options = []
        for name, data in container_types.items():
            if "冻" in name and transport_note != "冷冻":
                continue
            
            qty_by_vol = data["体积"] / single_volume if single_volume > 0 else 0
            qty_by_weight = data["重量"] / single_gross if single_gross > 0 else 0
            max_qty = min(qty_by_vol, qty_by_weight)
            
            if max_qty > 0:
                containers_needed = np.ceil(quantity / max_qty)
                total_freight = containers_needed * data["单价"]
                unit_freight = total_freight / quantity
                
                container_options.append({
                    "类型": name,
                    "可装数量": f"{max_qty:.0f}台",
                    "需要箱数": f"{containers_needed:.0f}个",
                    "总运费": f"${total_freight:,.2f}",
                    "单位运费": f"${unit_freight:.2f}/台"
                })
        
        st.session_state.container_options = container_options
        
        if container_options:
            best_option = min(container_options, key=lambda x: float(x["单位运费"].replace("$/台", "").replace("$", "").replace(",", "")))
            st.session_state.best_freight = float(best_option["总运费"].replace("$", "").replace(",", ""))
            st.session_state.best_container = best_option
            st.session_state.calculated = True

with col_calc2:
    if st.button("💰 计算建议报价", use_container_width=True):
        # 计算各项费用
        purchase_total = purchase_price * quantity
        rebate = purchase_total / (1 + vat_rate/100) * (export_rebate_rate/100)
        
        inland_fee = max(50, total_volume * 10) * exchange_rate
        forwarder_fee = max(70, total_volume * 2.5) * exchange_rate
        inspection_fee = 30 * exchange_rate if "B" in str(inspection_type) else 0
        certificate_fee = 100 * exchange_rate if "B" in str(inspection_type) else 0
        customs_fee = 30 * exchange_rate if trade_term != "EXW" else 0
        insurance = purchase_total * 1.1 * 0.005 if trade_term in ["CIF", "CIP", "DAP", "DPU", "DDP"] else 0
        
        if payment in ["D/P", "D/A"]:
            bank_fee = max(15, min(285, purchase_total * 0.001)) + 45
        elif "L/C" in payment:
            bank_fee = max(15, purchase_total * 0.00125) + 75
        else:
            bank_fee = 0
        
        domestic_total = inland_fee + forwarder_fee + inspection_fee + certificate_fee + customs_fee + insurance
        total_cost_before_freight = purchase_total - rebate + domestic_total + (bank_fee * exchange_rate)
        total_cost = total_cost_before_freight + (st.session_state.best_freight * exchange_rate)
        
        st.session_state.suggested_price = (total_cost * (1 + expected_profit_rate/100)) / quantity / exchange_rate
        st.session_state.total_cost = total_cost
        st.session_state.purchase_total = purchase_total

# 显示计算结果
if st.session_state.calculated:
    col_res1, col_res2, col_res3 = st.columns(3)
    
    with col_res1:
        st.markdown("##### 最优集装箱方案")
        if st.session_state.best_container:
            st.info(f"**{st.session_state.best_container['类型']}**\n\n"
                   f"需要 {st.session_state.best_container['需要箱数']}\n\n"
                   f"总运费 {st.session_state.best_container['总运费']}")
    
    with col_res2:
        st.markdown("##### 建议报价")
        st.markdown(f"<div class='result-box' style='padding:10px;'>${st.session_state.suggested_price:.2f}/台</div>", unsafe_allow_html=True)
    
    with col_res3:
        st.markdown("##### 总成本")
        st.markdown(f"<div class='result-box' style='padding:10px;'>¥{st.session_state.total_cost:,.2f}</div>", unsafe_allow_html=True)

# ==================== 第七步：出口预算表 ====================
st.markdown("""
<div class="step-container">
    <div class="step-header">
        <span class="step-badge">第七步</span>
        <span class="step-title">出口预算表</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 计算所有费用用于预算表
purchase_total = purchase_price * quantity
rebate = purchase_total / (1 + vat_rate/100) * (export_rebate_rate/100)
inland_fee = max(50, total_volume * 10) * exchange_rate
forwarder_fee = max(70, total_volume * 2.5) * exchange_rate
inspection_fee = 30 * exchange_rate if "B" in str(inspection_type) else 0
certificate_fee = 100 * exchange_rate if "B" in str(inspection_type) else 0
customs_fee = 30 * exchange_rate if trade_term != "EXW" else 0
insurance = purchase_total * 1.1 * 0.005 if trade_term in ["CIF", "CIP", "DAP", "DPU", "DDP"] else 0

if payment in ["D/P", "D/A"]:
    bank_fee = max(15, min(285, purchase_total * 0.001)) + 45
elif "L/C" in payment:
    bank_fee = max(15, purchase_total * 0.00125) + 75
else:
    bank_fee = 0

domestic_total = inland_fee + forwarder_fee + inspection_fee + certificate_fee + customs_fee + insurance
total_cost_before_freight = purchase_total - rebate + domestic_total + (bank_fee * exchange_rate)

# 创建预算表
st.markdown("""
<div class="excel-table">
    <div class="excel-header">
        <div>项目</div>
        <div>费用项目</div>
        <div>金额</div>
        <div>计算原理</div>
    </div>
""", unsafe_allow_html=True)

# 1. 采购成本
st.markdown(f"""
<div class="excel-row">
    <div class="excel-label">1.采购成本</div>
    <div class="excel-sub">含税购入价</div>
    <div class="excel-amount">¥{purchase_total:,.2f}</div>
    <div class="excel-principle">采购单价 × 交易数量 = {purchase_price} × {quantity}</div>
</div>
""", unsafe_allow_html=True)

# 2. 退税收入
st.markdown(f"""
<div class="excel-row">
    <div class="excel-label">2.退税收入</div>
    <div class="excel-sub">退税额</div>
    <div class="excel-amount">¥{rebate:,.2f}</div>
    <div class="excel-principle">含税价 ÷ (1+增值税率) × 退税率</div>
</div>
""", unsafe_allow_html=True)

# 3. 国内费用
st.markdown(f"""
<div class="excel-row">
    <div class="excel-label">3.国内费用</div>
    <div class="excel-sub">出口内陆运费</div>
    <div class="excel-amount">¥{inland_fee:,.2f}</div>
    <div class="excel-principle">MAX(50, 体积×10) × 汇率</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="excel-row">
    <div class="excel-label"></div>
    <div class="excel-sub">国际运费</div>
    <div class="excel-amount">${st.session_state.best_freight:,.2f}</div>
    <div class="excel-principle">集装箱最优选择</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="excel-row">
    <div class="excel-label"></div>
    <div class="excel-sub">出口货代杂费</div>
    <div class="excel-amount">¥{forwarder_fee:,.2f}</div>
    <div class="excel-principle">MAX(70, 体积×2.5) × 汇率</div>
</div>
""", unsafe_allow_html=True)

if customs_fee > 0:
    st.markdown(f"""
    <div class="excel-row">
        <div class="excel-label"></div>
        <div class="excel-sub">出口报关费</div>
        <div class="excel-amount">¥{customs_fee:,.2f}</div>
        <div class="excel-principle">30 × 汇率</div>
    </div>
    """, unsafe_allow_html=True)

if insurance > 0:
    st.markdown(f"""
    <div class="excel-row">
        <div class="excel-label"></div>
        <div class="excel-sub">保险费</div>
        <div class="excel-amount">¥{insurance:,.2f}</div>
        <div class="excel-principle">采购成本 × 110% × 0.5%</div>
    </div>
    """, unsafe_allow_html=True)

# 6. 总成本
st.markdown(f"""
<div class="excel-row" style="background-color: #2a5298; color: white; font-weight: bold;">
    <div class="excel-label">6.总成本</div>
    <div class="excel-sub">=1-2+3+4+5</div>
    <div class="excel-amount">¥{total_cost_before_freight + (st.session_state.best_freight * exchange_rate):,.2f}</div>
    <div class="excel-principle" style="color: white;">采购成本 - 退税 + 国内费用 + 银行费用 + 运费</div>
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ==================== 输入单价反算利润率 ====================
st.markdown("### 📈 输入实际报价反算利润率")

col_rev1, col_rev2, col_rev3 = st.columns(3)

with col_rev1:
    test_price = st.number_input("输入测试报价 (USD/台)", 
                                value=round(st.session_state.suggested_price if st.session_state.suggested_price > 0 else 100, 2), 
                                step=10.0)

if test_price > 0:
    total_cost_with_freight = total_cost_before_freight + (st.session_state.best_freight * exchange_rate)
    revenue = test_price * quantity * exchange_rate
    profit = revenue - total_cost_with_freight
    profit_margin = profit / purchase_total if purchase_total > 0 else 0
    
    col_rev2, col_rev3 = st.columns(2)
    with col_rev2:
        st.metric("预期利润", f"¥{profit:,.2f}")
    with col_rev3:
        st.metric("实际利润率", f"{profit_margin:.2%}", 
                 delta="达到目标" if profit_margin >= expected_profit_rate/100 else "低于目标",
                 delta_color="normal" if profit_margin >= expected_profit_rate/100 else "inverse")

# ==================== 底部信息 ====================
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666; padding: 10px; background-color: #f8f9fa; border-radius: 5px;'>
    <div>数据来源: {excel_path} | 文件存在: {'是' if file_exists else '否'}</div>
    <div>更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
</div>
""", unsafe_allow_html=True)

# 保存按钮
if st.button("💾 保存当前数据", use_container_width=True):
    st.success("✅ 数据已保存！")
    st.balloons()
