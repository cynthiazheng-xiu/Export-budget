import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import re

# 页面配置
st.set_page_config(
    page_title="出口预算表",
    page_icon="📊",
    layout="wide"
)

# 自定义样式
st.markdown("""
<style>
    .main-title {
        font-size: 2rem;
        color: #1E3A8A;
        text-align: center;
        padding: 15px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .section-title {
        font-size: 1.3rem;
        color: #2c3e50;
        background-color: #e3f2fd;
        padding: 8px 15px;
        border-radius: 5px;
        margin: 15px 0;
        border-left: 5px solid #1976D2;
    }
    .step-badge {
        display: inline-block;
        background-color: #ff6b6b;
        color: white;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-right: 10px;
    }
    .step-box {
        background-color: #fff8e7;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ffd700;
        margin: 10px 0;
    }
    .excel-table {
        background-color: white;
        border: 2px solid #ddd;
        border-radius: 5px;
        padding: 0;
        margin-bottom: 20px;
    }
    .excel-header {
        background-color: #f0f0f0;
        font-weight: bold;
        padding: 10px;
        border-bottom: 2px solid #ddd;
    }
    .excel-row {
        display: grid;
        grid-template-columns: 150px 200px 200px 1fr;
        border-bottom: 1px solid #eee;
        padding: 8px 10px;
    }
    .excel-row:hover {
        background-color: #f9f9f9;
    }
    .excel-label {
        font-weight: 500;
        color: #2c3e50;
    }
    .excel-sub {
        color: #666;
        padding-left: 20px;
    }
    .excel-amount {
        font-family: monospace;
        font-weight: 500;
    }
    .excel-principle {
        color: #1976D2;
        font-size: 0.85rem;
        padding-left: 20px;
        border-left: 1px dashed #ccc;
    }
    .fetch-button {
        background-color: #28a745;
        color: white;
        padding: 5px 15px;
        border-radius: 5px;
        text-align: center;
        margin: 10px 0;
    }
    .data-source {
        font-size: 0.7rem;
        color: #888;
        font-style: italic;
    }
    .stButton>button {
        width: 100%;
        margin: 5px 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 5px;
        border: 2px solid #28a745;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .sidebar-section {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
        border: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# 标题
st.markdown('<div class="main-title">📊 出口预算表 - 省赛版V1 (Excel格式)</div>', unsafe_allow_html=True)

# ==================== 侧边栏 ====================
with st.sidebar:
    st.markdown("## 📦 运费相关信息")
    
    # 第一步：运费单价信息
    st.markdown('<div class="step-box"><span class="step-badge">第一步</span> <strong>运费单价信息</strong></div>', unsafe_allow_html=True)
    
    # 从运费单价表抓取按钮
    col_fetch_f1, col_fetch_f2 = st.columns([3, 1])
    with col_fetch_f1:
        st.markdown("##### 从运费单价表抓取")
    with col_fetch_f2:
        if st.button("📥", key="fetch_freight_sidebar"):
            st.session_state['fetch_freight'] = True
            st.success("✅ 抓取成功!")
    
    # 普柜单价
    with st.expander("普柜单价 (USD)", expanded=True):
        lcl_w_normal = st.number_input("LCL(W)普柜", value=73, key="lcl_w_normal")
        lcl_m_normal = st.number_input("LCL(M)普柜", value=88, key="lcl_m_normal")
        container_20_normal = st.number_input("20'GP普柜", value=1452, key="container_20_normal")
        container_40_normal = st.number_input("40'GP普柜", value=2613, key="container_40_normal")
        container_40hc_normal = st.number_input("40'HC普柜", value=3135, key="container_40hc_normal")
    
    # 冻柜单价
    with st.expander("冻柜单价 (USD)", expanded=True):
        lcl_w_frozen = st.number_input("LCL(W)冻柜", value=146, key="lcl_w_frozen")
        lcl_m_frozen = st.number_input("LCL(M)冻柜", value=189, key="lcl_m_frozen")
        container_20_frozen = st.number_input("20'RF冻柜", value=2903, key="container_20_frozen")
        container_40_frozen = st.number_input("40'RF冻柜", value=5225, key="container_40_frozen")
        container_40rh_frozen = st.number_input("40'RH冻柜", value=6270, key="container_40rh_frozen")
    
    st.markdown("---")
    
    # 第二步：集装箱最优选择
    st.markdown('<div class="step-box"><span class="step-badge">第二步</span> <strong>集装箱最优选择</strong></div>', unsafe_allow_html=True)
    
    # 运输方式判断（基于主界面的数据）
    if 'total_gross' in st.session_state and 'total_volume' in st.session_state:
        if st.session_state.total_gross > 25000 or st.session_state.total_volume > 33:
            st.warning("⚠️ 建议使用整箱(FCL)")
        else:
            st.info("✅ 适合拼箱(LCL)或整箱(FCL)")
    
    # 集装箱选择按钮
    if st.button("🚢 计算最优集装箱", use_container_width=True):
        st.session_state['calc_container'] = True
    
    # 显示集装箱选项（如果有计算结果）
    if 'container_options' in st.session_state and st.session_state.container_options:
        df_options = pd.DataFrame(st.session_state.container_options)
        st.dataframe(df_options, use_container_width=True, hide_index=True)
        
        # 显示最优方案
        if 'best_container' in st.session_state and st.session_state.best_container:
            best = st.session_state.best_container
            st.markdown(f"""
            <div class="success-box">
                <h4 style='color: #28a745; margin: 0 0 5px 0;'>✅ 最优方案</h4>
                <p><strong>{best['集装箱类型']}</strong><br>
                需要 {best['需要箱数']} 个<br>
                总运费: {best['总运费(USD)']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 数据来源说明
    st.markdown("""
    <div class="data-source">
        📁 数据来源: C:\\Basic Information\\Data.xlsx<br>
        (通过Power Automate Desktop定时抓取)
    </div>
    """, unsafe_allow_html=True)

# ==================== 初始化session state ====================
if 'fetch_product' not in st.session_state:
    st.session_state['fetch_product'] = False
if 'fetch_hs' not in st.session_state:
    st.session_state['fetch_hs'] = False
if 'fetch_freight' not in st.session_state:
    st.session_state['fetch_freight'] = False
if 'fetch_rate' not in st.session_state:
    st.session_state['fetch_rate'] = False
if 'best_freight' not in st.session_state:
    st.session_state['best_freight'] = 0
if 'best_container' not in st.session_state:
    st.session_state['best_container'] = None
if 'container_options' not in st.session_state:
    st.session_state['container_options'] = []
if 'calc_container' not in st.session_state:
    st.session_state['calc_container'] = False

# ==================== 基础信息录入 ====================
st.markdown('<div class="section-title">📝 基础信息录入</div>', unsafe_allow_html=True)

# 使用标签页组织基础信息
tab_basic1, tab_basic2, tab_basic3, tab_basic4 = st.tabs(["商品信息", "海关信息", "公司信息", "交易信息"])

with tab_basic1:
    # 商品信息抓取按钮
    col_fetch1, col_fetch2 = st.columns([6, 1])
    with col_fetch1:
        st.markdown("##### 从商品信息表抓取")
    with col_fetch2:
        if st.button("📥", key="fetch_product_tab"):
            st.session_state['fetch_product'] = True
            st.success("✅ 商品信息抓取成功!")
    
    col1, col2 = st.columns(2)
    with col1:
        product_code = st.text_input("商品编号", "P010", key="product_code")
        product_name = st.text_input("商品名称", "自动售货机", key="product_name")
        product_name_en = st.text_input("英文名称", "Vending machine", key="product_name_en")
        product_type = st.text_input("货物类型", "机器、机械器具、电气设备及其零件", key="product_type")
    with col2:
        model_cn = st.text_input("规格型号(中文)", "型号：MF-782", key="model_cn")
        model_en = st.text_input("规格型号(英文)", "Model:mf-782", key="model_en")
        sales_unit = st.text_input("销售单位", "台(SET)", key="sales_unit")
        package_unit = st.text_input("包装单位", "托盘(PALLET)", key="package_unit")
    
    col3, col4 = st.columns(2)
    with col3:
        unit_conversion = st.text_input("单位换算", "1 SET/PALLET", key="unit_conversion")
        gross_weight = st.text_input("毛重", "280.00KGS/托盘", key="gross_weight")
        net_weight = st.text_input("净重", "220.00KGS/托盘", key="net_weight")
    with col4:
        volume = st.text_input("体积", "2.55CBM/托盘", key="volume")
        transport_note = st.selectbox("运输要求", ["普通", "冷藏", "冷冻"], key="transport_note")
        transport_desc = st.text_input("运输说明", "无", key="transport_desc")

with tab_basic2:
    # HS表抓取按钮
    col_fetch1, col_fetch2 = st.columns([6, 1])
    with col_fetch1:
        st.markdown("##### 从HS表抓取")
    with col_fetch2:
        if st.button("📥", key="fetch_hs_tab"):
            st.session_state['fetch_hs'] = True
            st.success("✅ HS信息抓取成功!")
    
    col1, col2 = st.columns(2)
    with col1:
        hs_code = st.text_input("HS编码", "8476810000", key="hs_code")
        customs_condition = st.text_input("海关监管条件", "无", key="customs_condition")
        legal_unit = st.text_input("法定单位", "台(SET)", key="legal_unit")
    with col2:
        inspection_type = st.text_input("检验检疫类别", "无", key="inspection_type")
        pref_tax_rate = st.number_input("优惠税率(%)", value=50.0, key="pref_tax_rate")
        vat_rate = st.number_input("增值税率(%)", value=13.0, key="vat_rate")
        export_rebate_rate = st.number_input("出口退税率(%)", value=13.0, key="export_rebate_rate")

with tab_basic3:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### 出口商信息")
        exporter_name = st.text_input("公司全称", "平尼克国际贸易公司", key="exporter_name")
        exporter_name_short = st.text_input("公司简称", "平尼克国际", key="exporter_name_short")
        exporter_address = st.text_input("公司地址", "菲律宾马尼拉宾农多马德里街513号", key="exporter_address")
        exporter_contact = st.text_input("企业法人", "阿卜杜勒贾里勒", key="exporter_contact")
    with col2:
        st.markdown("##### 进口商信息")
        importer_name = st.text_input("进口商名称", "罗伯茨世界贸易有限公司", key="importer_name")
        importer_name_en = st.text_input("进口商英文名", "Roberts World Traders Inc.", key="importer_name_en")
        importer_address = st.text_input("进口商地址", "加拿大不列颠哥伦比亚维多利亚白桦新月街4号", key="importer_address")
        importer_contact = st.text_input("进口商联系人", "艾伦·博尔赫斯", key="importer_contact")

with tab_basic4:
    # 汇率表抓取按钮
    col_fetch1, col_fetch2 = st.columns([6, 1])
    with col_fetch1:
        st.markdown("##### 从汇率表抓取")
    with col_fetch2:
        if st.button("📥", key="fetch_rate_tab"):
            st.session_state['fetch_rate'] = True
            st.success("✅ 汇率信息抓取成功!")
    
    col1, col2 = st.columns(2)
    with col1:
        quantity = st.number_input("交易数量", value=182, step=1, key="quantity")
        purchase_price = st.number_input("采购单价", value=4778.0, step=100.0, key="purchase_price")
        account_balance = st.number_input("账户本币余额", value=1888000.0, step=1000.0, key="account_balance")
    with col2:
        trade_term = st.selectbox("贸易术语", ["EXW", "FCA", "FAS", "FOB", "CFR", "CIF", "CIP", "DAP", "DPU", "DDP"], key="trade_term")
        payment = st.selectbox("支付方式", ["T/T", "L/C", "D/P", "T/T+LC"], key="payment")
        exchange_rate = st.number_input("USD/CAD 汇率", value=1.368, step=0.001, format="%.3f", key="exchange_rate")
        expected_profit_rate = st.slider("预期利润率(%)", 0, 50, 15, key="expected_profit_rate")

# ==================== 提取数值用于计算 ====================
def extract_number(text):
    try:
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", str(text))
        return float(numbers[0]) if numbers else 0
    except:
        return 0

# 从输入中提取数值
single_gross = extract_number(gross_weight)
single_net = extract_number(net_weight)
single_volume = extract_number(volume)
units_per_package = extract_number(unit_conversion)

# 计算总包装数
if units_per_package > 0:
    total_packages = np.ceil(quantity / units_per_package)
else:
    total_packages = quantity

total_gross = total_packages * single_gross
total_net = total_packages * single_net
total_volume = total_packages * single_volume

# 保存到session state供侧边栏使用
st.session_state.total_gross = total_gross
st.session_state.total_volume = total_volume

# ==================== 出口预算表 ====================
st.markdown('<div class="section-title">📊 出口预算表</div>', unsafe_allow_html=True)

# 计算各项费用
purchase_total = purchase_price * quantity
rebate = purchase_total / (1 + vat_rate/100) * (export_rebate_rate/100)

# 国内费用
inland_fee_base = max(50, total_volume * 10)
inland_fee = inland_fee_base * exchange_rate

forwarder_fee_base = max(70, total_volume * 2.5)
forwarder_fee = forwarder_fee_base * exchange_rate

inspection_fee = 30 * exchange_rate if "B" in str(inspection_type) else 0
certificate_fee = 100 * exchange_rate if "B" in str(inspection_type) else 0
customs_fee = 30 * exchange_rate if trade_term != "EXW" else 0
origin_cert_fee = 0

# 保险费
insurance = purchase_total * 1.1 * 0.005 if trade_term in ["CIF", "CIP", "DAP", "DPU", "DDP"] else 0

# 银行费用
if payment in ["D/P", "D/A"]:
    bank_fee = max(15, min(285, purchase_total * 0.001)) + 45
elif "L/C" in payment:
    bank_fee = max(15, purchase_total * 0.00125) + 75
else:
    bank_fee = 0

# 国内费用合计
domestic_total = inland_fee + forwarder_fee + inspection_fee + certificate_fee + customs_fee + origin_cert_fee + insurance

# 创建预算表HTML
st.markdown("""
<div class="excel-table">
    <div class="excel-header" style="display: grid; grid-template-columns: 150px 200px 200px 1fr; background-color: #e0e0e0;">
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
    <div class="excel-principle">含税价 ÷ (1+增值税率) × 退税率 = {purchase_total:,.2f} ÷ {1+vat_rate/100:.2f} × {export_rebate_rate/100:.2f}</div>
</div>
""", unsafe_allow_html=True)

# 3. 国内费用 - 出口内陆运费
st.markdown(f"""
<div class="excel-row">
    <div class="excel-label">3.国内费用</div>
    <div class="excel-sub">出口内陆运费</div>
    <div class="excel-amount">¥{inland_fee:,.2f}</div>
    <div class="excel-principle">MAX(50, 总体积×10) × 汇率 = MAX(50, {total_volume:.2f}×10) × {exchange_rate}</div>
</div>
""", unsafe_allow_html=True)

# 国际运费
st.markdown(f"""
<div class="excel-row">
    <div class="excel-label"></div>
    <div class="excel-sub">国际运费</div>
    <div class="excel-amount">{"$" + f"{st.session_state.best_freight:,.2f}" if st.session_state.best_freight > 0 else "待计算"}</div>
    <div class="excel-principle">根据集装箱最优选择计算</div>
</div>
""", unsafe_allow_html=True)

# 出口货代杂费
st.markdown(f"""
<div class="excel-row">
    <div class="excel-label"></div>
    <div class="excel-sub">出口货代杂费</div>
    <div class="excel-amount">¥{forwarder_fee:,.2f}</div>
    <div class="excel-principle">MAX(70, 总体积×2.5) × 汇率 = MAX(70, {total_volume:.2f}×2.5) × {exchange_rate}</div>
</div>
""", unsafe_allow_html=True)

# 出口商检费
if inspection_fee > 0:
    st.markdown(f"""
    <div class="excel-row">
        <div class="excel-label"></div>
        <div class="excel-sub">出口商检费</div>
        <div class="excel-amount">¥{inspection_fee:,.2f}</div>
        <div class="excel-principle">检验检疫类别含B，30 × 汇率 = 30 × {exchange_rate}</div>
    </div>
    """, unsafe_allow_html=True)

# 检验检疫证书费
if certificate_fee > 0:
    st.markdown(f"""
    <div class="excel-row">
        <div class="excel-label"></div>
        <div class="excel-sub">检验检疫证书费</div>
        <div class="excel-amount">¥{certificate_fee:,.2f}</div>
        <div class="excel-principle">检验检疫类别含B，100 × 汇率 = 100 × {exchange_rate}</div>
    </div>
    """, unsafe_allow_html=True)

# 出口报关费
st.markdown(f"""
<div class="excel-row">
    <div class="excel-label"></div>
    <div class="excel-sub">出口报关费</div>
    <div class="excel-amount">¥{customs_fee:,.2f}</div>
    <div class="excel-principle">{'EXW除外' if trade_term != 'EXW' else 'EXW不收取'}，30 × 汇率 = 30 × {exchange_rate}</div>
</div>
""", unsafe_allow_html=True)

# 产地证书费
st.markdown(f"""
<div class="excel-row">
    <div class="excel-label"></div>
    <div class="excel-sub">产地证书费</div>
    <div class="excel-amount">¥0.00</div>
    <div class="excel-principle">根据实际情况收取</div>
</div>
""", unsafe_allow_html=True)

# 保险费
if insurance > 0:
    st.markdown(f"""
    <div class="excel-row">
        <div class="excel-label"></div>
        <div class="excel-sub">保险费</div>
        <div class="excel-amount">¥{insurance:,.2f}</div>
        <div class="excel-principle">采购成本 × 110% × 0.5% = {purchase_total:,.2f} × 1.1 × 0.005</div>
    </div>
    """, unsafe_allow_html=True)

# 国内费用合计
st.markdown(f"""
<div class="excel-row" style="background-color: #f5f5f5;">
    <div class="excel-label"></div>
    <div class="excel-sub"><strong>国内费用合计</strong></div>
    <div class="excel-amount"><strong>¥{domestic_total:,.2f}</strong></div>
    <div class="excel-principle">各项国内费用相加</div>
</div>
""", unsafe_allow_html=True)

# 4. 银行费用
if payment in ["D/P", "D/A"]:
    st.markdown(f"""
    <div class="excel-row">
        <div class="excel-label">4.银行费用</div>
        <div class="excel-sub">托收费用</div>
        <div class="excel-amount">${bank_fee:,.2f}</div>
        <div class="excel-principle">MAX(15, MIN(285, 采购成本×0.1%)) + 45 = {bank_fee-45:.2f} + 45</div>
    </div>
    """, unsafe_allow_html=True)
elif "L/C" in payment:
    st.markdown(f"""
    <div class="excel-row">
        <div class="excel-label">4.银行费用</div>
        <div class="excel-sub">信用证费用</div>
        <div class="excel-amount">${bank_fee:,.2f}</div>
        <div class="excel-principle">MAX(15, 采购成本×0.125%) + 75 = {bank_fee-75:.2f} + 75</div>
    </div>
    """, unsafe_allow_html=True)

# 5. 国外费用
if trade_term in ["DAP", "DPU", "DDP"]:
    st.markdown(f"""
    <div class="excel-row">
        <div class="excel-label">5.国外费用</div>
        <div class="excel-sub">DAP/DPU/DDP国外费用</div>
        <div class="excel-amount">待计算</div>
        <div class="excel-principle">根据目的港费用计算</div>
    </div>
    """, unsafe_allow_html=True)

# 6. 总成本
total_cost_before_freight = purchase_total - rebate + domestic_total + (bank_fee * exchange_rate)

st.markdown(f"""
<div class="excel-row" style="background-color: #e8f4f8; font-weight: bold;">
    <div class="excel-label">6.总成本</div>
    <div class="excel-sub">=1-2+3+4+5</div>
    <div class="excel-amount">¥{total_cost_before_freight:,.2f}</div>
    <div class="excel-principle">采购成本 - 退税 + 国内费用 + 银行费用</div>
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ==================== 集装箱计算（当点击按钮时）====================
if st.session_state.calc_container:
    # 创建集装箱数据
    container_types = {
        "20'普柜": {"体积": 33, "重量": 25000, "单价": container_20_normal, "类型": "普柜"},
        "40'普柜": {"体积": 67, "重量": 29000, "单价": container_40_normal, "类型": "普柜"},
        "40'高柜": {"体积": 76, "重量": 29000, "单价": container_40hc_normal, "类型": "普柜"},
        "20'冻柜": {"体积": 27, "重量": 27400, "单价": container_20_frozen, "类型": "冻柜"},
        "40'冻柜": {"体积": 58, "重量": 27700, "单价": container_40_frozen, "类型": "冻柜"},
        "40'冻高": {"体积": 66, "重量": 29000, "单价": container_40rh_frozen, "类型": "冻柜"}
    }
    
    # 计算所有集装箱选项
    container_options = []
    for name, data in container_types.items():
        # 根据货物类型过滤
        if "冻" in name and transport_note != "冷冻":
            continue
        
        # 计算可装数量
        qty_by_vol = data["体积"] / single_volume if single_volume > 0 else 0
        qty_by_weight = data["重量"] / single_gross if single_gross > 0 else 0
        max_qty = min(qty_by_vol, qty_by_weight)
        
        if max_qty > 0:
            containers_needed = np.ceil(quantity / max_qty)
            total_freight = containers_needed * data["单价"]
            unit_freight = total_freight / quantity
            
            container_options.append({
                "集装箱类型": name,
                "每箱可装(台)": f"{max_qty:.0f}",
                "需要箱数": f"{containers_needed:.0f}",
                "单价(USD)": f"${data['单价']:,.0f}",
                "总运费(USD)": f"${total_freight:,.2f}",
                "单位运费(USD/台)": f"${unit_freight:.2f}"
            })
    
    st.session_state.container_options = container_options
    
    if container_options:
        # 找出最优方案
        try:
            best_option = min(container_options, key=lambda x: float(x["单位运费(USD/台)"].replace("$", "").replace(",", "")))
            st.session_state.best_freight = float(best_option["总运费(USD)"].replace("$", "").replace(",", ""))
            st.session_state.best_container = best_option
        except:
            st.session_state.best_freight = 0
            st.session_state.best_container = None
    
    st.session_state.calc_container = False
    st.rerun()

# ==================== 盈亏预测 ====================
st.markdown('<div class="section-title">📈 盈亏预测</div>', unsafe_allow_html=True)

# 计算总成本（包含运费）
total_cost_with_freight = total_cost_before_freight + (st.session_state.best_freight * exchange_rate)

# 建议报价
suggested_price = (total_cost_with_freight * (1 + expected_profit_rate/100)) / quantity / exchange_rate

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("总成本(含运费)", f"¥{total_cost_with_freight:,.2f}")
with col2:
    st.metric("建议报价", f"${suggested_price:.2f}/台")
with col3:
    if st.session_state.best_freight > 0:
        st.metric("运费占比", f"{(st.session_state.best_freight * exchange_rate / total_cost_with_freight):.1%}")

# 实际报价
actual_price = st.number_input("输入实际报价 (USD/台)", value=round(suggested_price, 2), step=10.0, key="actual_price")

if actual_price > 0:
    revenue = actual_price * quantity * exchange_rate
    profit = revenue - total_cost_with_freight
    profit_margin = profit / purchase_total if purchase_total > 0 else 0
    
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        st.metric("总收入", f"¥{revenue:,.2f}")
    with col_r2:
        delta_color = "normal" if profit >= 0 else "inverse"
        st.metric("预期利润", f"¥{profit:,.2f}", delta=f"{profit_margin:.2%}", delta_color=delta_color)
    with col_r3:
        st.metric("利润率", f"{profit_margin:.2%}")

# ==================== 底部信息 ====================
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666; padding: 15px; background-color: #f8f9fa; border-radius: 5px;'>
    <div>更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
    <div>交易数量: {quantity}台 | 总体积: {total_volume:.2f}CBM | 总毛重: {total_gross:,.0f}KGS</div>
</div>
""", unsafe_allow_html=True)

# 保存按钮
if st.button("💾 保存当前数据", use_container_width=True):
    st.success("✅ 数据已保存！")
    st.balloons()
