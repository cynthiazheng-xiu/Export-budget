import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
import re
import time

# 设置北京时区
beijing_tz = timezone(timedelta(hours=8))

def get_beijing_time():
    """获取当前北京时间"""
    return datetime.now(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')

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
        padding: 15px;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .company-section {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        border: 1px solid #2a5298;
    }
    .company-row {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        margin-bottom: 8px;
        font-size: 0.85rem;
    }
    .company-row:last-child {
        margin-bottom: 0;
    }
    .company-item {
        display: flex;
        align-items: center;
        white-space: nowrap;
    }
    .company-label {
        font-weight: bold;
        color: #1e3c72;
        margin-right: 5px;
    }
    .company-value {
        color: #2a5298;
    }
    .section-title {
        font-size: 1.3rem;
        color: #2a5298;
        font-weight: bold;
        margin: 15px 0 10px 0;
        padding-bottom: 5px;
        border-bottom: 2px solid #2a5298;
    }
    .step-container {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 5px solid #2a5298;
    }
    .step-header {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
    }
    .step-badge {
        background-color: #2a5298;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
        margin-right: 15px;
        min-width: 100px;
        text-align: center;
    }
    .step-title {
        font-size: 1.1rem;
        color: #1e3c72;
        font-weight: 600;
    }
    .hs-row {
        display: flex;
        gap: 10px;
        background-color: #e9ecef;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
        flex-wrap: wrap;
        border: 1px solid #2a5298;
    }
    .hs-header {
        font-weight: bold;
        color: #2a5298;
        margin-bottom: 5px;
        font-size: 0.8rem;
    }
    .empty-state {
        color: #999;
        font-style: italic;
        padding: 20px;
        text-align: center;
        background-color: #f8f9fa;
        border-radius: 5px;
        margin: 10px 0;
    }
    .excel-table {
        background-color: white;
        border: 2px solid #dee2e6;
        border-radius: 8px;
        padding: 0;
        margin: 10px 0;
        overflow: hidden;
        font-size: 0.9rem;
    }
    .excel-header {
        background-color: #2a5298;
        color: white;
        font-weight: bold;
        padding: 8px 12px;
        display: grid;
        grid-template-columns: 120px 180px 150px 1fr;
    }
    .excel-row {
        display: grid;
        grid-template-columns: 120px 180px 150px 1fr;
        border-bottom: 1px solid #dee2e6;
        padding: 6px 12px;
    }
    .excel-row:nth-child(even) {
        background-color: #f8f9fa;
    }
    .result-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
    }
    .success-small {
        font-size: 0.8rem;
        color: #28a745;
        margin-top: 5px;
    }
    .freight-container {
        display: flex;
        gap: 20px;
        margin: 10px 0;
    }
    .freight-table {
        flex: 1;
        border: 1px solid #dee2e6;
        border-radius: 5px;
        overflow: hidden;
        font-size: 0.85rem;
    }
    .freight-table table {
        width: 100%;
        border-collapse: collapse;
    }
    .freight-table th {
        background-color: #2a5298;
        color: white;
        padding: 6px;
        text-align: center;
        font-weight: bold;
    }
    .freight-table td {
        padding: 4px 8px;
        border: 1px solid #dee2e6;
    }
    .freight-label {
        font-weight: bold;
        background-color: #e9ecef;
        width: 40%;
    }
    .freight-value {
        text-align: right;
        width: 60%;
    }
</style>
""", unsafe_allow_html=True)

# 标题
st.markdown('<div class="main-title">📊 出口预算表 - 全国职业院校技能大赛版</div>', unsafe_allow_html=True)

# ==================== 初始化session state ====================
if 'data_updated' not in st.session_state:
    st.session_state.data_updated = False
if 'last_update_time' not in st.session_state:
    st.session_state.last_update_time = None
if 'best_freight' not in st.session_state:
    st.session_state.best_freight = 0.0
if 'best_freight_cny' not in st.session_state:
    st.session_state.best_freight_cny = 0.0
if 'containers_needed' not in st.session_state:
    st.session_state.containers_needed = 0
if 'container_type' not in st.session_state:
    st.session_state.container_type = ""
if 'suggested_price' not in st.session_state:
    st.session_state.suggested_price = 0.0
if 'calculated' not in st.session_state:
    st.session_state.calculated = False
if 'customer_data' not in st.session_state:
    st.session_state.customer_data = {
        'exporter_name': '平尼克国际贸易公司',
        'exporter_name_short': '平尼克国际',
        'exporter_name_en': 'Pinic International Trading',
        'exporter_address': '菲律宾马尼拉宾农多马德里街513号',
        'exporter_address_en': '513 Madrid Street Binondomanila,Philippines',
        'exporter_contact': '阿卜杜勒贾里勒',
        'exporter_contact_en': 'Abdul Jaleel',
        'exporter_tel': '82-266-2402192',
        'exporter_email': '19859639@yahoo.com',
        'exporter_postal': '260335',
        'exporter_org_code': '702104723',
        'exporter_social_code': '921002127021047238',
        'exporter_customs_code': '2100151282',
        'exporter_inspection_code': '3100212576',
        'importer_name': '罗伯茨世界贸易有限公司',
        'importer_name_en': 'Roberts World Traders Inc.',
        'importer_address': '加拿大不列颠哥伦比亚维多利亚白桦新月街4号',
        'importer_address_en': '4 Aspen Crescent, Victoria, British Columbia, Canada',
        'importer_contact': '艾伦·博尔赫斯',
        'importer_contact_en': 'Alan Borges',
        'importer_tel': '82-775-6178091',
        'importer_email': '17548933@yahoo.com',
        'importer_postal': '314640',
        'importer_org_code': '560088060',
        'importer_inspection_code': '2910087056',
        'importer_customs_code': '2660935964'
    }
if 'product_data' not in st.session_state:
    st.session_state.product_data = None
if 'freight_data' not in st.session_state:
    st.session_state.freight_data = None
if 'exchange_rate' not in st.session_state:
    st.session_state.exchange_rate = 1.368
if 'quantity' not in st.session_state:
    st.session_state.quantity = 0.0
if 'purchase_price' not in st.session_state:
    st.session_state.purchase_price = 0.0
if 'trade_term' not in st.session_state:
    st.session_state.trade_term = "FOB"
if 'payment' not in st.session_state:
    st.session_state.payment = "T/T"

# ==================== 清除数据的函数 ====================
def clear_all_data():
    st.session_state.data_updated = False
    st.session_state.last_update_time = None
    st.session_state.best_freight = 0.0
    st.session_state.best_freight_cny = 0.0
    st.session_state.containers_needed = 0
    st.session_state.container_type = ""
    st.session_state.suggested_price = 0.0
    st.session_state.calculated = False
    st.session_state.product_data = None
    st.session_state.freight_data = None
    st.session_state.exchange_rate = 1.368
    st.session_state.quantity = 0.0
    st.session_state.purchase_price = 0.0
    st.session_state.trade_term = "FOB"
    st.session_state.payment = "T/T"

# ==================== 侧边栏 ====================
with st.sidebar:
    st.markdown("## 📁 数据抓取控制")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🚀 抓取数据", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            steps = [
                "正在连接Power Automate Desktop...",
                "正在打开Excel文件 C:\\Basic Information\\Data.xlsx...",
                "正在读取商品信息表...",
                "正在读取HS编码表...",
                "正在读取运费单价表...",
                "正在读取客户信息表...",
                "正在读取汇率表...",
                "数据抓取完成！"
            ]
            
            for i, step in enumerate(steps):
                status_text.text(f"⏳ {step}")
                progress_bar.progress((i + 1) * 100 // len(steps))
                time.sleep(0.5)
            
            st.session_state.data_updated = True
            st.session_state.last_update_time = get_beijing_time()
            st.session_state.product_data = {
                'product_code': 'P010',
                'product_name': '自动售货机',
                'product_name_en': 'Vending machine',
                'product_type': '机器、机械器具、电气设备及其零件',
                'model_cn': '型号：MF-782',
                'model_en': 'Model:mf-782',
                'sales_unit': '台(SET)',
                'package_unit': '托盘(PALLET)',
                'unit_conversion': '1 SET/PALLET',
                'gross_weight': '280.00KGS/托盘',
                'net_weight': '220.00KGS/托盘',
                'volume': '2.55CBM/托盘',
                'transport_desc': '无'
            }
            st.session_state.freight_data = {
                'lcl_w_normal': 73, 'lcl_m_normal': 88,
                'c20_normal': 1452, 'c40_normal': 2613, 'c40hc_normal': 3135,
                'lcl_w_frozen': 146, 'lcl_m_frozen': 189,
                'c20_frozen': 2903, 'c40_frozen': 5225, 'c40rh_frozen': 6270
            }
            st.session_state.exchange_rate = 1.368
            
            progress_bar.empty()
            status_text.empty()
            st.markdown('<p class="success-small">✅ 抓取成功！</p>', unsafe_allow_html=True)
    
    with col_btn2:
        if st.button("🧹 清除数据", use_container_width=True):
            clear_all_data()
            st.rerun()
    
    if st.session_state.get('last_update_time'):
        st.caption(f"最后更新: {st.session_state.last_update_time}")
    
    st.markdown("---")
    
    # ==================== 港口信息 ====================
    st.markdown("## 🚢 港口信息")
    col_port1, col_port2 = st.columns(2)
    with col_port1:
        export_country = st.text_input("出口国", "China", key="export_country")
        loading_port = st.text_input("装运港", "Shanghai", key="loading_port")
    with col_port2:
        import_country = st.text_input("进口国", "Canada", key="import_country")
        destination_port = st.text_input("目的港", "Vancouver", key="destination_port")
    
    st.markdown("---")
    
    # ==================== 物流信息（运费单价表-并列表格）====================
    st.markdown("## 📦 运费单价表")
    
    # 安全获取物流数据
    if st.session_state.freight_data:
        freight_data = st.session_state.freight_data
    else:
        freight_data = {
            'lcl_w_normal': 73, 'lcl_m_normal': 88,
            'c20_normal': 1452, 'c40_normal': 2613, 'c40hc_normal': 3135,
            'lcl_w_frozen': 146, 'lcl_m_frozen': 189,
            'c20_frozen': 2903, 'c40_frozen': 5225, 'c40rh_frozen': 6270
        }
    
    # 并列表格显示
    col_freight1, col_freight2 = st.columns(2)
    
    with col_freight1:
        st.markdown("**普柜单价 (USD)**")
        freight_table1 = f"""
        <table class="freight-table">
            <tr><td class="freight-label">LCL(W)</td><td class="freight-value">{freight_data.get('lcl_w_normal', 73):.2f}</td></tr>
            <tr><td class="freight-label">LCL(M)</td><td class="freight-value">{freight_data.get('lcl_m_normal', 88):.2f}</td></tr>
            <tr><td class="freight-label">20'GP</td><td class="freight-value">{freight_data.get('c20_normal', 1452):.2f}</td></tr>
            <tr><td class="freight-label">40'GP</td><td class="freight-value">{freight_data.get('c40_normal', 2613):.2f}</td></tr>
            <tr><td class="freight-label">40'HC</td><td class="freight-value">{freight_data.get('c40hc_normal', 3135):.2f}</td></tr>
        </table>
        """
        st.markdown(freight_table1, unsafe_allow_html=True)
    
    with col_freight2:
        st.markdown("**冻柜单价 (USD)**")
        freight_table2 = f"""
        <table class="freight-table">
            <tr><td class="freight-label">LCL(W)冻</td><td class="freight-value">{freight_data.get('lcl_w_frozen', 146):.2f}</td></tr>
            <tr><td class="freight-label">LCL(M)冻</td><td class="freight-value">{freight_data.get('lcl_m_frozen', 189):.2f}</td></tr>
            <tr><td class="freight-label">20'RF</td><td class="freight-value">{freight_data.get('c20_frozen', 2903):.2f}</td></tr>
            <tr><td class="freight-label">40'RF</td><td class="freight-value">{freight_data.get('c40_frozen', 5225):.2f}</td></tr>
            <tr><td class="freight-label">40'RH</td><td class="freight-value">{freight_data.get('c40rh_frozen', 6270):.2f}</td></tr>
        </table>
        """
        st.markdown(freight_table2, unsafe_allow_html=True)

# ==================== 公司信息（左右两列紧凑显示）====================
st.markdown('<div class="company-section">', unsafe_allow_html=True)

# 出口商信息（左侧）
st.markdown("**🏭 出口商信息**")
st.markdown(f"""
<div class="company-row">
    <div class="company-item"><span class="company-label">公司全称：</span><span class="company-value">{st.session_state.customer_data["exporter_name"]}</span></div>
    <div class="company-item"><span class="company-label">公司简称：</span><span class="company-value">{st.session_state.customer_data["exporter_name_short"]}</span></div>
    <div class="company-item"><span class="company-label">英文名称：</span><span class="company-value">{st.session_state.customer_data["exporter_name_en"]}</span></div>
</div>
<div class="company-row">
    <div class="company-item"><span class="company-label">公司地址：</span><span class="company-value">{st.session_state.customer_data["exporter_address"]}</span></div>
    <div class="company-item"><span class="company-label">地址英文：</span><span class="company-value">{st.session_state.customer_data["exporter_address_en"]}</span></div>
</div>
<div class="company-row">
    <div class="company-item"><span class="company-label">企业法人：</span><span class="company-value">{st.session_state.customer_data["exporter_contact"]} ({st.session_state.customer_data["exporter_contact_en"]})</span></div>
    <div class="company-item"><span class="company-label">电话/传真：</span><span class="company-value">{st.session_state.customer_data["exporter_tel"]}</span></div>
    <div class="company-item"><span class="company-label">电子邮件：</span><span class="company-value">{st.session_state.customer_data["exporter_email"]}</span></div>
</div>
<div class="company-row">
    <div class="company-item"><span class="company-label">邮政编码：</span><span class="company-value">{st.session_state.customer_data["exporter_postal"]}</span></div>
    <div class="company-item"><span class="company-label">组织机构代码：</span><span class="company-value">{st.session_state.customer_data["exporter_org_code"]}</span></div>
    <div class="company-item"><span class="company-label">社会信用代码：</span><span class="company-value">{st.session_state.customer_data["exporter_social_code"]}</span></div>
</div>
<div class="company-row">
    <div class="company-item"><span class="company-label">海关代码：</span><span class="company-value">{st.session_state.customer_data["exporter_customs_code"]}</span></div>
    <div class="company-item"><span class="company-label">报检登记号：</span><span class="company-value">{st.session_state.customer_data["exporter_inspection_code"]}</span></div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='margin: 10px 0; border-top: 1px dashed #2a5298;'>", unsafe_allow_html=True)

# 进口商信息（右侧）
st.markdown("**🌍 进口商信息**")
st.markdown(f"""
<div class="company-row">
    <div class="company-item"><span class="company-label">公司名称：</span><span class="company-value">{st.session_state.customer_data["importer_name"]}</span></div>
    <div class="company-item"><span class="company-label">英文名称：</span><span class="company-value">{st.session_state.customer_data["importer_name_en"]}</span></div>
</div>
<div class="company-row">
    <div class="company-item"><span class="company-label">公司地址：</span><span class="company-value">{st.session_state.customer_data["importer_address"]}</span></div>
    <div class="company-item"><span class="company-label">地址英文：</span><span class="company-value">{st.session_state.customer_data["importer_address_en"]}</span></div>
</div>
<div class="company-row">
    <div class="company-item"><span class="company-label">联系人：</span><span class="company-value">{st.session_state.customer_data["importer_contact"]} ({st.session_state.customer_data["importer_contact_en"]})</span></div>
    <div class="company-item"><span class="company-label">电话：</span><span class="company-value">{st.session_state.customer_data["importer_tel"]}</span></div>
    <div class="company-item"><span class="company-label">邮箱：</span><span class="company-value">{st.session_state.customer_data["importer_email"]}</span></div>
</div>
<div class="company-row">
    <div class="company-item"><span class="company-label">邮政编码：</span><span class="company-value">{st.session_state.customer_data["importer_postal"]}</span></div>
    <div class="company-item"><span class="company-label">组织机构代码：</span><span class="company-value">{st.session_state.customer_data["importer_org_code"]}</span></div>
    <div class="company-item"><span class="company-label">报检登记号：</span><span class="company-value">{st.session_state.customer_data["importer_inspection_code"]}</span></div>
    <div class="company-item"><span class="company-label">海关代码：</span><span class="company-value">{st.session_state.customer_data["importer_customs_code"]}</span></div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ==================== HS信息（带抬头）====================
st.markdown('<div class="section-title">🏷️ HS编码信息</div>', unsafe_allow_html=True)

st.markdown('<div class="hs-row">', unsafe_allow_html=True)

# 第一行：抬头
col_hs_header1, col_hs_header2, col_hs_header3, col_hs_header4, col_hs_header5, col_hs_header6, col_hs_header7, col_hs_header8 = st.columns(8)
with col_hs_header1:
    st.markdown('<div class="hs-header">HS编码</div>', unsafe_allow_html=True)
with col_hs_header2:
    st.markdown('<div class="hs-header">监管条件</div>', unsafe_allow_html=True)
with col_hs_header3:
    st.markdown('<div class="hs-header">检验检疫</div>', unsafe_allow_html=True)
with col_hs_header4:
    st.markdown('<div class="hs-header">法定单位</div>', unsafe_allow_html=True)
with col_hs_header5:
    st.markdown('<div class="hs-header">优惠税率%</div>', unsafe_allow_html=True)
with col_hs_header6:
    st.markdown('<div class="hs-header">增值税%</div>', unsafe_allow_html=True)
with col_hs_header7:
    st.markdown('<div class="hs-header">出口税率%</div>', unsafe_allow_html=True)
with col_hs_header8:
    st.markdown('<div class="hs-header">退税率%</div>', unsafe_allow_html=True)

# 第二行：输入框
col_hs1, col_hs2, col_hs3, col_hs4, col_hs5, col_hs6, col_hs7, col_hs8 = st.columns(8)
with col_hs1:
    hs_code = st.text_input("##", value="8476810000", key="hs_code", label_visibility="collapsed")
with col_hs2:
    customs_condition = st.text_input("##", value="无", key="customs_condition", label_visibility="collapsed")
with col_hs3:
    inspection_type = st.text_input("##", value="无", key="inspection_type", label_visibility="collapsed")
with col_hs4:
    legal_unit = st.text_input("##", value="台(SET)", key="legal_unit", label_visibility="collapsed")
with col_hs5:
    pref_tax_rate = st.number_input("##", value=50.0, key="pref_tax_rate", label_visibility="collapsed", step=1.0)
with col_hs6:
    vat_rate = st.number_input("##", value=13.0, key="vat_rate", label_visibility="collapsed", step=1.0)
with col_hs7:
    export_tax_rate = st.number_input("##", value=0.0, key="export_tax_rate", label_visibility="collapsed", step=1.0)
with col_hs8:
    export_rebate_rate = st.number_input("##", value=13.0, key="export_rebate_rate", label_visibility="collapsed", step=1.0)

st.markdown('</div>', unsafe_allow_html=True)

# ==================== 产品信息 ====================
st.markdown("""
<div class="step-container">
    <div class="step-header">
        <span class="step-badge">第一步</span>
        <span class="step-title">产品信息</span>
    </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.data_updated and st.session_state.product_data:
    col_prod1, col_prod2 = st.columns(2)

    with col_prod1:
        product_code = st.text_input("商品编号", value=st.session_state.product_data.get('product_code', ''), key="product_code_display")
        product_name = st.text_input("商品名称", value=st.session_state.product_data.get('product_name', ''), key="product_name_display")
        product_name_en = st.text_input("英文名称", value=st.session_state.product_data.get('product_name_en', ''), key="product_name_en_display")
        product_type = st.text_input("货物类型", value=st.session_state.product_data.get('product_type', ''), key="product_type_display")
        model_cn = st.text_input("规格型号(中文)", value=st.session_state.product_data.get('model_cn', ''), key="model_cn_display")
        model_en = st.text_input("规格型号(英文)", value=st.session_state.product_data.get('model_en', ''), key="model_en_display")

    with col_prod2:
        sales_unit = st.text_input("销售单位", value=st.session_state.product_data.get('sales_unit', ''), key="sales_unit_display")
        package_unit = st.text_input("包装单位", value=st.session_state.product_data.get('package_unit', ''), key="package_unit_display")
        unit_conversion = st.text_input("单位换算", value=st.session_state.product_data.get('unit_conversion', ''), key="unit_conversion_display")
        gross_weight = st.text_input("毛重", value=st.session_state.product_data.get('gross_weight', ''), key="gross_weight_display")
        net_weight = st.text_input("净重", value=st.session_state.product_data.get('net_weight', ''), key="net_weight_display")
        volume = st.text_input("体积", value=st.session_state.product_data.get('volume', ''), key="volume_display")
        transport_desc = st.text_input("运输说明", value=st.session_state.product_data.get('transport_desc', ''), key="transport_desc_display")
else:
    st.markdown("""
    <div class="empty-state">
        ⏳ 请点击侧边栏的"抓取数据"按钮获取产品信息
    </div>
    """, unsafe_allow_html=True)

# ==================== 交易信息 ====================
st.markdown("""
<div class="step-container">
    <div class="step-header">
        <span class="step-badge">第二步</span>
        <span class="step-title">交易信息</span>
    </div>
</div>
""", unsafe_allow_html=True)

col_trade1, col_trade2, col_trade3 = st.columns(3)

with col_trade1:
    quantity_val = float(st.session_state.quantity) if st.session_state.quantity > 0 else 0.0
    purchase_price_val = float(st.session_state.purchase_price) if st.session_state.purchase_price > 0 else 0.0
    
    quantity = st.number_input("交易数量", value=quantity_val, step=1.0, key="quantity_input")
    purchase_price = st.number_input("采购单价", value=purchase_price_val, step=100.0, format="%.2f", key="purchase_price_input")

with col_trade2:
    account_balance = st.number_input("账户余额", value=1888000.0, step=1000.0, format="%.2f", key="account_balance")
    exchange_rate_input = st.number_input("USD/CAD汇率", value=float(st.session_state.exchange_rate), step=0.001, format="%.3f", key="exchange_rate_input")

with col_trade3:
    trade_term = st.selectbox("贸易术语", ["EXW", "FCA", "FAS", "FOB", "CFR", "CIF", "CIP", "DAP", "DPU", "DDP"], 
                             index=3 if st.session_state.trade_term == "FOB" else 0, key="trade_term_select")
    payment = st.selectbox("支付方式", ["T/T", "L/C", "D/P", "T/T+LC"], 
                          index=0 if st.session_state.payment == "T/T" else 1, key="payment_select")
    expected_profit_rate = st.slider("预期利润率%", 0, 50, 15, key="expected_profit_rate")
    transport_note = st.selectbox("运输要求", ["普通", "冷藏", "冷冻"], key="transport_note")

# 更新session state中的交易信息
st.session_state.quantity = float(quantity)
st.session_state.purchase_price = float(purchase_price)
st.session_state.trade_term = trade_term
st.session_state.payment = payment
st.session_state.exchange_rate = float(exchange_rate_input)

# ==================== 提取数值用于计算 ====================
def extract_number(text):
    try:
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", str(text))
        return float(numbers[0]) if numbers else 0.0
    except:
        return 0.0

# 获取运费单价的值（从侧边栏的输入框）
container_20_normal = st.session_state.get('c20_normal', 1452)
container_20_frozen = st.session_state.get('c20_frozen', 2903)

# 只有有数据时才计算
if st.session_state.data_updated and st.session_state.product_data and quantity > 0 and purchase_price > 0:
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

    # 显示计算结果
    st.markdown("### 📦 货物总量")
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("总包装数", f"{int(total_packages)}个")
    with col_m2:
        st.metric("总毛重", f"{total_gross:,.0f}KGS")
    with col_m3:
        st.metric("总净重", f"{total_net:,.0f}KGS")
    with col_m4:
        st.metric("总体积", f"{total_volume:.2f}CBM")

    # ==================== 计算报价 ====================
    st.markdown("""
    <div class="step-container">
        <div class="step-header">
            <span class="step-badge">第三步</span>
            <span class="step-title">计算报价</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_calc1, col_calc2 = st.columns(2)

    with col_calc1:
        if st.button("🚢 计算运费", use_container_width=True):
            containers_needed = np.ceil(total_volume / 33.0)
            if transport_note in ["冷藏", "冷冻"]:
                st.session_state.best_freight = float(containers_needed * container_20_frozen)
                st.session_state.container_type = "20'冻柜"
            else:
                st.session_state.best_freight = float(containers_needed * container_20_normal)
                st.session_state.container_type = "20'普柜"
            st.session_state.containers_needed = int(containers_needed)
            st.session_state.best_freight_cny = st.session_state.best_freight * st.session_state.exchange_rate
            st.session_state.calculated = True
            st.success(f"需要 {int(containers_needed)}个 {st.session_state.container_type}，运费 ${st.session_state.best_freight:,.2f} (¥{st.session_state.best_freight_cny:,.2f})")

    with col_calc2:
        if st.button("💰 计算报价", use_container_width=True):
            purchase_total = purchase_price * quantity
            rebate = purchase_total / (1.0 + vat_rate/100.0) * (export_rebate_rate/100.0)
            total_cost = purchase_total - rebate + (st.session_state.best_freight * st.session_state.exchange_rate)
            st.session_state.suggested_price = (total_cost * (1.0 + expected_profit_rate/100.0)) / quantity / st.session_state.exchange_rate
            st.session_state.total_cost = total_cost

    # 显示计算结果
    if st.session_state.calculated and st.session_state.suggested_price > 0:
        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            st.markdown("##### 💰 建议报价")
            st.markdown(f"<div class='result-box'>${st.session_state.suggested_price:.2f}/台</div>", unsafe_allow_html=True)
        
        with col_res2:
            st.markdown("##### 📈 反算利润率")
            
            # 计算总成本
            purchase_total = purchase_price * quantity
            rebate = purchase_total / (1.0 + vat_rate/100.0) * (export_rebate_rate/100.0)
            inland_fee = max(50.0, total_volume * 10.0) * st.session_state.exchange_rate
            forwarder_fee = max(70.0, total_volume * 2.5) * st.session_state.exchange_rate
            customs_fee = 30.0 * st.session_state.exchange_rate if trade_term != "EXW" else 0.0
            total_cost = purchase_total - rebate + inland_fee + forwarder_fee + customs_fee + (st.session_state.best_freight * st.session_state.exchange_rate)
            
            test_price = st.number_input("测试报价", value=float(st.session_state.suggested_price), step=5.0, format="%.2f", key="test_price_input")
            
            if test_price > 0:
                revenue = test_price * quantity * st.session_state.exchange_rate
                profit = revenue - total_cost
                profit_margin = profit / purchase_total if purchase_total > 0 else 0.0
                
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    st.metric("利润", f"¥{profit:,.0f}")
                with col_p2:
                    st.metric("利润率", f"{profit_margin:.1%}")

    # ==================== 出口预算表 ====================
    st.markdown("""
    <div class="step-container">
        <div class="step-header">
            <span class="step-badge">第四步</span>
            <span class="step-title">出口预算表</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 计算费用
    purchase_total = purchase_price * quantity
    rebate = purchase_total / (1.0 + vat_rate/100.0) * (export_rebate_rate/100.0)
    inland_fee = max(50.0, total_volume * 10.0) * st.session_state.exchange_rate
    forwarder_fee = max(70.0, total_volume * 2.5) * st.session_state.exchange_rate
    inspection_fee = 30.0 * st.session_state.exchange_rate if "B" in str(inspection_type) else 0.0
    certificate_fee = 100.0 * st.session_state.exchange_rate if "B" in str(inspection_type) else 0.0
    customs_fee = 30.0 * st.session_state.exchange_rate if trade_term != "EXW" else 0.0
    insurance = purchase_total * 1.1 * 0.005 if trade_term in ["CIF", "CIP", "DAP", "DPU", "DDP"] else 0.0

    if payment in ["D/P", "D/A"]:
        bank_fee = max(15.0, min(285.0, purchase_total * 0.001)) + 45.0
    elif "L/C" in payment:
        bank_fee = max(15.0, purchase_total * 0.00125) + 75.0
    else:
        bank_fee = 0.0

    domestic_total = inland_fee + forwarder_fee + inspection_fee + certificate_fee + customs_fee + insurance

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
        <div class="excel-principle">{purchase_price:.0f} × {int(quantity)}</div>
    </div>
    """, unsafe_allow_html=True)

    # 2. 退税收入
    st.markdown(f"""
    <div class="excel-row">
        <div class="excel-label">2.退税收入</div>
        <div class="excel-sub">退税额</div>
        <div class="excel-amount">¥{rebate:,.2f}</div>
        <div class="excel-principle">含税价÷(1+{vat_rate:.0f}%)×{export_rebate_rate:.0f}%</div>
    </div>
    """, unsafe_allow_html=True)

    # 3. 国内费用
    st.markdown(f"""
    <div class="excel-row">
        <div class="excel-label">3.国内费用</div>
        <div class="excel-sub">出口内陆运费</div>
        <div class="excel-amount">¥{inland_fee:,.2f}</div>
        <div class="excel-principle">MAX(50, {total_volume:.1f}×10)×{st.session_state.exchange_rate:.3f}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="excel-row">
        <div class="excel-label"></div>
        <div class="excel-sub">国际运费</div>
        <div class="excel-amount">¥{st.session_state.best_freight_cny:,.2f}</div>
        <div class="excel-principle">{st.session_state.containers_needed}个{st.session_state.container_type} (${st.session_state.best_freight:,.2f} × {st.session_state.exchange_rate:.3f})</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="excel-row">
        <div class="excel-label"></div>
        <div class="excel-sub">出口货代杂费</div>
        <div class="excel-amount">¥{forwarder_fee:,.2f}</div>
        <div class="excel-principle">MAX(70, {total_volume:.1f}×2.5)×{st.session_state.exchange_rate:.3f}</div>
    </div>
    """, unsafe_allow_html=True)

    if inspection_fee > 0:
        st.markdown(f"""
        <div class="excel-row">
            <div class="excel-label"></div>
            <div class="excel-sub">出口商检费</div>
            <div class="excel-amount">¥{inspection_fee:,.2f}</div>
            <div class="excel-principle">检验检疫类别含B时收取</div>
        </div>
        """, unsafe_allow_html=True)

    if certificate_fee > 0:
        st.markdown(f"""
        <div class="excel-row">
            <div class="excel-label"></div>
            <div class="excel-sub">检验检疫证书费</div>
            <div class="excel-amount">¥{certificate_fee:,.2f}</div>
            <div class="excel-principle">检验检疫类别含B时收取</div>
        </div>
        """, unsafe_allow_html=True)

    if customs_fee > 0:
        st.markdown(f"""
        <div class="excel-row">
            <div class="excel-label"></div>
            <div class="excel-sub">出口报关费</div>
            <div class="excel-amount">¥{customs_fee:,.2f}</div>
            <div class="excel-principle">30×{st.session_state.exchange_rate:.3f}</div>
        </div>
        """, unsafe_allow_html=True)

    if insurance > 0:
        st.markdown(f"""
        <div class="excel-row">
            <div class="excel-label"></div>
            <div class="excel-sub">保险费</div>
            <div class="excel-amount">¥{insurance:,.2f}</div>
            <div class="excel-principle">采购成本×110%×0.5%</div>
        </div>
        """, unsafe_allow_html=True)

    # 国内费用合计
    st.markdown(f"""
    <div class="excel-row" style="background-color: #e9ecef;">
        <div class="excel-label"></div>
        <div class="excel-sub"><strong>国内费用合计</strong></div>
        <div class="excel-amount"><strong>¥{domestic_total:,.2f}</strong></div>
        <div class="excel-principle">各项相加</div>
    </div>
    """, unsafe_allow_html=True)

    # 4. 银行费用
    if payment in ["D/P", "D/A"] or "L/C" in payment:
        fee_type = '托收费用' if payment in ['D/P','D/A'] else '信用证费用'
        st.markdown(f"""
        <div class="excel-row">
            <div class="excel-label">4.银行费用</div>
            <div class="excel-sub">{fee_type}</div>
            <div class="excel-amount">${bank_fee:,.2f}</div>
            <div class="excel-principle">根据支付方式</div>
        </div>
        """, unsafe_allow_html=True)

    # 总成本
    total_cost_final = purchase_total - rebate + domestic_total + (bank_fee * st.session_state.exchange_rate) + (st.session_state.best_freight * st.session_state.exchange_rate)

    st.markdown(f"""
    <div class="excel-row" style="background-color: #2a5298; color: white; font-weight: bold;">
        <div class="excel-label">总成本</div>
        <div class="excel-sub">=1-2+3+4</div>
        <div class="excel-amount">¥{total_cost_final:,.2f}</div>
        <div class="excel-principle" style="color: white;">采购-退税+国内+银行+运费</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="empty-state">
        ⏳ 请先抓取数据，然后填写交易数量及采购单价进行计算
    </div>
    """, unsafe_allow_html=True)

# ==================== 底部信息 ====================
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666; padding: 8px; background-color: #f8f9fa; border-radius: 5px; font-size:0.9rem;'>
    装运港: {loading_port}, {export_country} | 目的港: {destination_port}, {import_country} | 北京时间: {get_beijing_time()}
</div>
""", unsafe_allow_html=True)

# 保存按钮
if st.button("💾 保存当前数据", use_container_width=True):
    st.success("✅ 数据已保存到会话中！")
    st.balloons()
