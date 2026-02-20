import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import re
import time

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
    }
    .step-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        border-left: 5px solid #2a5298;
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
    .status-box {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
        border: 1px solid #c3e6cb;
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
    .result-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    }
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# 标题
st.markdown('<div class="main-title">📊 出口预算表 - 全国职业院校技能大赛版</div>', unsafe_allow_html=True)

# ==================== 初始化session state ====================
if 'product_data' not in st.session_state:
    st.session_state.product_data = {}
if 'hs_data' not in st.session_state:
    st.session_state.hs_data = {}
if 'freight_data' not in st.session_state:
    st.session_state.freight_data = {}
if 'customer_data' not in st.session_state:
    st.session_state.customer_data = {}
if 'data_updated' not in st.session_state:
    st.session_state.data_updated = False
if 'last_update_time' not in st.session_state:
    st.session_state.last_update_time = None
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
if 'total_cost' not in st.session_state:
    st.session_state.total_cost = 0
if 'purchase_total' not in st.session_state:
    st.session_state.purchase_total = 0

# ==================== PAD模拟抓取按钮 ====================
st.markdown("""
<div class="step-container">
    <div class="step-header">
        <span class="step-badge">PAD抓取</span>
        <span class="step-title">Power Automate Desktop 模拟数据抓取</span>
    </div>
</div>
""", unsafe_allow_html=True)

col_pad1, col_pad2, col_pad3 = st.columns([1,2,1])
with col_pad2:
    if st.button("🚀 启动PAD模拟抓取数据", use_container_width=True):
        st.session_state.pad_running = True
        st.session_state.data_updated = False
        
        # 创建进度条模拟PAD运行
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 模拟PAD抓取过程
        steps = [
            "正在启动Power Automate Desktop...",
            "正在打开Excel文件 C:\\Basic Information\\Data.xlsx...",
            "正在读取商品信息表...",
            "正在读取HS编码表...",
            "正在读取运费单价表...",
            "正在读取汇率表...",
            "正在读取客户信息表...",
            "正在整理数据...",
            "正在准备填入Web界面...",
            "数据抓取完成！"
        ]
        
        for i, step in enumerate(steps):
            status_text.text(f"⏳ {step}")
            progress_bar.progress((i + 1) * 10)
            time.sleep(0.3)
        
        # 模拟抓取到的数据
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
        
        st.session_state.hs_data = {
            'hs_code': '8476810000',
            'customs_condition': '无',
            'inspection_type': '无',
            'legal_unit': '台(SET)',
            'pref_tax_rate': 50,
            'vat_rate': 13,
            'export_rebate_rate': 13
        }
        
        st.session_state.freight_data = {
            'lcl_w_normal': 73,
            'lcl_m_normal': 88,
            'container_20_normal': 1452,
            'container_40_normal': 2613,
            'container_40hc_normal': 3135,
            'lcl_w_frozen': 146,
            'lcl_m_frozen': 189,
            'container_20_frozen': 2903,
            'container_40_frozen': 5225,
            'container_40rh_frozen': 6270
        }
        
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
        
        st.session_state.data_updated = True
        st.session_state.last_update_time = datetime.now()
        progress_bar.empty()
        status_text.empty()
        st.success("✅ PAD数据抓取完成！所有数据已更新")
        st.balloons()

# 显示最后更新时间
if st.session_state.last_update_time:
    st.markdown(f"""
    <div class="status-box">
        📅 最后数据更新时间: {st.session_state.last_update_time.strftime('%Y-%m-%d %H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)

# ==================== 第一步：客户信息 ====================
st.markdown("""
<div class="step-container">
    <div class="step-header">
        <span class="step-badge">第一步</span>
        <span class="step-title">客户信息</span>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["出口商信息", "进口商信息"])

with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:
        exporter_name = st.text_input("公司全称", value=st.session_state.customer_data.get('exporter_name', ''))
        exporter_name_short = st.text_input("公司简称", value=st.session_state.customer_data.get('exporter_name_short', ''))
        exporter_name_en = st.text_input("公司英文名", value=st.session_state.customer_data.get('exporter_name_en', ''))
    with col2:
        exporter_address = st.text_input("公司地址", value=st.session_state.customer_data.get('exporter_address', ''))
        exporter_address_en = st.text_input("地址英文", value=st.session_state.customer_data.get('exporter_address_en', ''))
        exporter_contact = st.text_input("企业法人", value=st.session_state.customer_data.get('exporter_contact', ''))
    with col3:
        exporter_contact_en = st.text_input("法人英文", value=st.session_state.customer_data.get('exporter_contact_en', ''))
        exporter_tel = st.text_input("电话/传真", value=st.session_state.customer_data.get('exporter_tel', ''))
        exporter_email = st.text_input("电子邮件", value=st.session_state.customer_data.get('exporter_email', ''))
    
    col4, col5, col6 = st.columns(3)
    with col4:
        exporter_postal = st.text_input("邮政编码", value=st.session_state.customer_data.get('exporter_postal', ''))
        exporter_org_code = st.text_input("组织机构代码", value=st.session_state.customer_data.get('exporter_org_code', ''))
    with col5:
        exporter_social_code = st.text_input("社会信用代码", value=st.session_state.customer_data.get('exporter_social_code', ''))
        exporter_customs_code = st.text_input("海关代码", value=st.session_state.customer_data.get('exporter_customs_code', ''))
    with col6:
        exporter_inspection_code = st.text_input("报检登记号", value=st.session_state.customer_data.get('exporter_inspection_code', ''))

with tab2:
    col1, col2, col3 = st.columns(3)
    with col1:
        importer_name = st.text_input("进口商名称", value=st.session_state.customer_data.get('importer_name', ''))
        importer_name_en = st.text_input("进口商英文名", value=st.session_state.customer_data.get('importer_name_en', ''))
    with col2:
        importer_address = st.text_input("进口商地址", value=st.session_state.customer_data.get('importer_address', ''))
        importer_address_en = st.text_input("地址英文", value=st.session_state.customer_data.get('importer_address_en', ''))
    with col3:
        importer_contact = st.text_input("联系人", value=st.session_state.customer_data.get('importer_contact', ''))
        importer_contact_en = st.text_input("联系人英文", value=st.session_state.customer_data.get('importer_contact_en', ''))
    
    col4, col5, col6 = st.columns(3)
    with col4:
        importer_tel = st.text_input("电话", value=st.session_state.customer_data.get('importer_tel', ''))
        importer_email = st.text_input("邮箱", value=st.session_state.customer_data.get('importer_email', ''))
    with col5:
        importer_postal = st.text_input("邮编", value=st.session_state.customer_data.get('importer_postal', ''))
        importer_org_code = st.text_input("组织机构代码", value=st.session_state.customer_data.get('importer_org_code', ''))
    with col6:
        importer_inspection_code = st.text_input("报检登记号", value=st.session_state.customer_data.get('importer_inspection_code', ''))
        importer_customs_code = st.text_input("海关代码", value=st.session_state.customer_data.get('importer_customs_code', ''))

# ==================== 第二步：产品信息 ====================
st.markdown("""
<div class="step-container">
    <div class="step-header">
        <span class="step-badge">第二步</span>
        <span class="step-title">产品信息</span>
    </div>
</div>
""", unsafe_allow_html=True)

col_prod1, col_prod2 = st.columns(2)

with col_prod1:
    product_code = st.text_input("商品编号", value=st.session_state.product_data.get('product_code', 'P010'))
    product_name = st.text_input("商品名称", value=st.session_state.product_data.get('product_name', '自动售货机'))
    product_name_en = st.text_input("英文名称", value=st.session_state.product_data.get('product_name_en', 'Vending machine'))
    product_type = st.text_input("货物类型", value=st.session_state.product_data.get('product_type', '机器、机械器具、电气设备及其零件'))
    model_cn = st.text_input("规格型号(中文)", value=st.session_state.product_data.get('model_cn', '型号：MF-782'))
    model_en = st.text_input("规格型号(英文)", value=st.session_state.product_data.get('model_en', 'Model:mf-782'))

with col_prod2:
    sales_unit = st.text_input("销售单位", value=st.session_state.product_data.get('sales_unit', '台(SET)'))
    package_unit = st.text_input("包装单位", value=st.session_state.product_data.get('package_unit', '托盘(PALLET)'))
    unit_conversion = st.text_input("单位换算", value=st.session_state.product_data.get('unit_conversion', '1 SET/PALLET'))
    gross_weight = st.text_input("毛重", value=st.session_state.product_data.get('gross_weight', '280.00KGS/托盘'))
    net_weight = st.text_input("净重", value=st.session_state.product_data.get('net_weight', '220.00KGS/托盘'))
    volume = st.text_input("体积", value=st.session_state.product_data.get('volume', '2.55CBM/托盘'))
    transport_desc = st.text_input("运输说明", value=st.session_state.product_data.get('transport_desc', '无'))

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
    hs_code = st.text_input("HS编码", value=st.session_state.hs_data.get('hs_code', '8476810000'))
    customs_condition = st.text_input("海关监管条件", value=st.session_state.hs_data.get('customs_condition', '无'))
    inspection_type = st.text_input("检验检疫类别", value=st.session_state.hs_data.get('inspection_type', '无'))

with col_hs2:
    legal_unit = st.text_input("法定单位", value=st.session_state.hs_data.get('legal_unit', '台(SET)'))
    pref_tax_rate = st.number_input("优惠税率(%)", value=float(st.session_state.hs_data.get('pref_tax_rate', 50)))
    vat_rate = st.number_input("增值税率(%)", value=float(st.session_state.hs_data.get('vat_rate', 13)))
    export_rebate_rate = st.number_input("出口退税率(%)", value=float(st.session_state.hs_data.get('export_rebate_rate', 13)))

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
    st.markdown("**普柜单价 (USD)**")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        lcl_w_normal = st.number_input("LCL(W)", value=st.session_state.freight_data.get('lcl_w_normal', 73))
        container_20_normal = st.number_input("20'GP", value=st.session_state.freight_data.get('container_20_normal', 1452))
        container_40_normal = st.number_input("40'GP", value=st.session_state.freight_data.get('container_40_normal', 2613))
    with col_p2:
        lcl_m_normal = st.number_input("LCL(M)", value=st.session_state.freight_data.get('lcl_m_normal', 88))
        container_40hc_normal = st.number_input("40'HC", value=st.session_state.freight_data.get('container_40hc_normal', 3135))

with col_log2:
    st.markdown("**冻柜单价 (USD)**")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        lcl_w_frozen = st.number_input("LCL(W)冻", value=st.session_state.freight_data.get('lcl_w_frozen', 146))
        container_20_frozen = st.number_input("20'RF", value=st.session_state.freight_data.get('container_20_frozen', 2903))
        container_40_frozen = st.number_input("40'RF", value=st.session_state.freight_data.get('container_40_frozen', 5225))
    with col_f2:
        lcl_m_frozen = st.number_input("LCL(M)冻", value=st.session_state.freight_data.get('lcl_m_frozen', 189))
        container_40rh_frozen = st.number_input("40'RH", value=st.session_state.freight_data.get('container_40rh_frozen', 6270))

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

# 显示计算结果
st.markdown("### 📦 货物总量计算")
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric("总包装数", f"{total_packages:.0f} 个")
with col_m2:
    st.metric("总毛重", f"{total_gross:,.0f} KGS")
with col_m3:
    st.metric("总净重", f"{total_net:,.0f} KGS")
with col_m4:
    st.metric("总体积", f"{total_volume:.2f} CBM")

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
            "20'普柜": {"体积": 33, "重量": 25000, "单价": container_20_normal},
            "40'普柜": {"体积": 67, "重量": 29000, "单价": container_40_normal},
            "40'高柜": {"体积": 76, "重量": 29000, "单价": container_40hc_normal},
            "20'冻柜": {"体积": 27, "重量": 27400, "单价": container_20_frozen},
            "40'冻柜": {"体积": 58, "重量": 27700, "单价": container_40_frozen},
            "40'冻高": {"体积": 66, "重量": 29000, "单价": container_40rh_frozen}
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
            # 找出单位运费最低的方案
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

# 国内费用合计
st.markdown(f"""
<div class="excel-row" style="background-color: #e9ecef;">
    <div class="excel-label"></div>
    <div class="excel-sub"><strong>国内费用合计</strong></div>
    <div class="excel-amount"><strong>¥{domestic_total:,.2f}</strong></div>
    <div class="excel-principle">各项国内费用相加</div>
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
        <div class="excel-principle">根据支付方式计算</div>
    </div>
    """, unsafe_allow_html=True)

# 6. 总成本
total_cost_final = total_cost_before_freight + (st.session_state.best_freight * exchange_rate)
st.markdown(f"""
<div class="excel-row" style="background-color: #2a5298; color: white; font-weight: bold;">
    <div class="excel-label">6.总成本</div>
    <div class="excel-sub">=1-2+3+4+5</div>
    <div class="excel-amount">¥{total_cost_final:,.2f}</div>
    <div class="excel-principle" style="color: white;">采购成本 - 退税 + 国内费用 + 银行费用 + 运费</div>
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ==================== 输入单价反算利润率 ====================
st.markdown("### 📈 输入实际报价反算利润率")

col_rev1, col_rev2 = st.columns(2)

with col_rev1:
    test_price = st.number_input("输入测试报价 (USD/台)", 
                                value=round(st.session_state.suggested_price if st.session_state.suggested_price > 0 else 100, 2), 
                                step=10.0)

if test_price > 0 and st.session_state.best_freight > 0:
    total_cost_with_freight = total_cost_before_freight + (st.session_state.best_freight * exchange_rate)
    revenue = test_price * quantity * exchange_rate
    profit = revenue - total_cost_with_freight
    profit_margin = profit / purchase_total if purchase_total > 0 else 0
    
    col_rev2, col_rev3 = st.columns(2)
    with col_rev2:
        st.metric("预期利润", f"¥{profit:,.2f}")
    with col_rev3:
        target = expected_profit_rate / 100
        st.metric("实际利润率", f"{profit_margin:.2%}", 
                 delta=f"{'✅ 达到目标' if profit_margin >= target else '❌ 低于目标'}",
                 delta_color="normal" if profit_margin >= target else "inverse")

# ==================== 底部信息 ====================
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666; padding: 10px; background-color: #f8f9fa; border-radius: 5px;'>
    <div>运行模式: Streamlit Cloud | PAD模拟抓取已就绪</div>
    <div>更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
</div>
""", unsafe_allow_html=True)

# 保存按钮
if st.button("💾 保存当前数据", use_container_width=True):
    st.success("✅ 数据已保存到会话中！")
    st.balloons()
