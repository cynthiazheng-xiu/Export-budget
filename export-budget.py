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
    .company-info {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# 标题
st.markdown('<div class="main-title">📊 出口预算表 - 全国职业院校技能大赛版</div>', unsafe_allow_html=True)

# ==================== 侧边栏：公司信息 ====================
with st.sidebar:
    st.markdown("## 🏢 本公司信息")
    st.markdown('<div class="company-info">', unsafe_allow_html=True)
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("**出口商**")
        exporter_name = st.text_input("公司全称", "平尼克国际贸易公司", key="sidebar_exporter")
        exporter_contact = st.text_input("联系人", "阿卜杜勒贾里勒", key="sidebar_contact")
        exporter_tel = st.text_input("电话", "82-266-2402192", key="sidebar_tel")
    
    with col_s2:
        st.markdown("**进口商**")
        importer_name = st.text_input("进口商名称", "罗伯茨世界贸易有限公司", key="sidebar_importer")
        importer_contact = st.text_input("进口商联系人", "艾伦·博尔赫斯", key="sidebar_importer_contact")
        importer_tel = st.text_input("进口商电话", "82-775-6178091", key="sidebar_importer_tel")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📁 数据抓取")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🚀 抓取数据", use_container_width=True):
            with st.spinner("正在抓取数据..."):
                time.sleep(1.5)
                st.session_state.data_updated = True
                st.session_state.last_update_time = datetime.now()
            st.success("✅ 抓取成功！")
    
    with col_btn2:
        if st.button("🧹 清除数据", use_container_width=True):
            st.session_state.data_updated = False
            st.session_state.last_update_time = None
            st.rerun()
    
    if st.session_state.get('last_update_time'):
        st.caption(f"最后更新: {st.session_state.last_update_time.strftime('%H:%M:%S')}")

# ==================== 初始化session state ====================
if 'data_updated' not in st.session_state:
    st.session_state.data_updated = False
if 'last_update_time' not in st.session_state:
    st.session_state.last_update_time = None
if 'best_freight' not in st.session_state:
    st.session_state.best_freight = 0
if 'suggested_price' not in st.session_state:
    st.session_state.suggested_price = 0
if 'calculated' not in st.session_state:
    st.session_state.calculated = False

# ==================== 默认数据（仅在抓取后显示）====================
default_product = {
    'product_code': 'P010',
    'product_name': '自动售货机',
    'product_name_en': 'Vending machine',
    'product_type': '机器、机械器具、电气设备及其零件',
    'sales_unit': '台(SET)',
    'package_unit': '托盘(PALLET)',
    'unit_conversion': '1 SET/PALLET',
    'gross_weight': '280.00KGS/托盘',
    'net_weight': '220.00KGS/托盘',
    'volume': '2.55CBM/托盘'
}

default_hs = {
    'hs_code': '8476810000',
    'customs_condition': '无',
    'inspection_type': '无',
    'legal_unit': '台(SET)',
    'vat_rate': 13,
    'export_rebate_rate': 13
}

default_freight = {
    'container_20_normal': 1452,
    'container_40_normal': 2613,
    'container_40hc_normal': 3135,
    'container_20_frozen': 2903,
    'container_40_frozen': 5225,
    'container_40rh_frozen': 6270
}

# ==================== 第一步：产品信息 ====================
st.markdown("""
<div class="step-container">
    <div class="step-header">
        <span class="step-badge">第一步</span>
        <span class="step-title">产品信息</span>
    </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.data_updated:
    col_prod1, col_prod2 = st.columns(2)

    with col_prod1:
        product_code = st.text_input("商品编号", value=default_product['product_code'], key="product_code")
        product_name = st.text_input("商品名称", value=default_product['product_name'], key="product_name")
        product_name_en = st.text_input("英文名称", value=default_product['product_name_en'], key="product_name_en")
        product_type = st.text_input("货物类型", value=default_product['product_type'], key="product_type")

    with col_prod2:
        sales_unit = st.text_input("销售单位", value=default_product['sales_unit'], key="sales_unit")
        package_unit = st.text_input("包装单位", value=default_product['package_unit'], key="package_unit")
        unit_conversion = st.text_input("单位换算", value=default_product['unit_conversion'], key="unit_conversion")
        gross_weight = st.text_input("毛重", value=default_product['gross_weight'], key="gross_weight")
        net_weight = st.text_input("净重", value=default_product['net_weight'], key="net_weight")
        volume = st.text_input("体积", value=default_product['volume'], key="volume")
else:
    st.markdown("""
    <div class="empty-state">
        ⏳ 请点击侧边栏的"抓取数据"按钮获取产品信息
    </div>
    """, unsafe_allow_html=True)

# ==================== 第二步：HS信息 ====================
st.markdown("""
<div class="step-container">
    <div class="step-header">
        <span class="step-badge">第二步</span>
        <span class="step-title">HS信息</span>
    </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.data_updated:
    col_hs1, col_hs2 = st.columns(2)

    with col_hs1:
        hs_code = st.text_input("HS编码", value=default_hs['hs_code'], key="hs_code")
        customs_condition = st.text_input("海关监管条件", value=default_hs['customs_condition'], key="customs_condition")
        inspection_type = st.text_input("检验检疫类别", value=default_hs['inspection_type'], key="inspection_type")

    with col_hs2:
        legal_unit = st.text_input("法定单位", value=default_hs['legal_unit'], key="legal_unit")
        vat_rate = st.number_input("增值税率(%)", value=default_hs['vat_rate'], key="vat_rate")
        export_rebate_rate = st.number_input("出口退税率(%)", value=default_hs['export_rebate_rate'], key="export_rebate_rate")
else:
    st.markdown("""
    <div class="empty-state">
        ⏳ 请先抓取数据获取HS信息
    </div>
    """, unsafe_allow_html=True)

# ==================== 第三步：物流信息 ====================
st.markdown("""
<div class="step-container">
    <div class="step-header">
        <span class="step-badge">第三步</span>
        <span class="step-title">物流信息</span>
    </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.data_updated:
    col_log1, col_log2 = st.columns(2)

    with col_log1:
        st.markdown("**普柜单价 (USD)**")
        container_20_normal = st.number_input("20'GP", value=default_freight['container_20_normal'], key="container_20_normal")
        container_40_normal = st.number_input("40'GP", value=default_freight['container_40_normal'], key="container_40_normal")
        container_40hc_normal = st.number_input("40'HC", value=default_freight['container_40hc_normal'], key="container_40hc_normal")

    with col_log2:
        st.markdown("**冻柜单价 (USD)**")
        container_20_frozen = st.number_input("20'RF", value=default_freight['container_20_frozen'], key="container_20_frozen")
        container_40_frozen = st.number_input("40'RF", value=default_freight['container_40_frozen'], key="container_40_frozen")
        container_40rh_frozen = st.number_input("40'RH", value=default_freight['container_40rh_frozen'], key="container_40rh_frozen")
else:
    st.markdown("""
    <div class="empty-state">
        ⏳ 请先抓取数据获取物流信息
    </div>
    """, unsafe_allow_html=True)

# ==================== 第四步：交易信息 ====================
st.markdown("""
<div class="step-container">
    <div class="step-header">
        <span class="step-badge">第四步</span>
        <span class="step-title">交易信息</span>
    </div>
</div>
""", unsafe_allow_html=True)

col_trade1, col_trade2, col_trade3 = st.columns(3)

with col_trade1:
    quantity = st.number_input("交易数量", value=182, step=1, key="quantity")
    purchase_price = st.number_input("采购单价", value=4778.0, step=100.0, key="purchase_price")

with col_trade2:
    exchange_rate = st.number_input("USD/CAD 汇率", value=1.368, step=0.001, format="%.3f", key="exchange_rate")
    trade_term = st.selectbox("贸易术语", ["FOB", "CIF", "EXW", "CFR", "CIP"], key="trade_term")

with col_trade3:
    expected_profit_rate = st.slider("预期利润率(%)", 0, 50, 15, key="expected_profit_rate")
    transport_note = st.selectbox("运输要求", ["普通", "冷藏"], key="transport_note")

# ==================== 提取数值用于计算 ====================
def extract_number(text):
    try:
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", str(text))
        return float(numbers[0]) if numbers else 0
    except:
        return 0

# 只有有数据时才计算
if st.session_state.data_updated:
    single_gross = extract_number(gross_weight)
    single_volume = extract_number(volume)
    units_per_package = extract_number(unit_conversion)

    if units_per_package > 0:
        total_packages = np.ceil(quantity / units_per_package)
    else:
        total_packages = quantity

    total_gross = total_packages * single_gross
    total_volume = total_packages * single_volume

    # 显示计算结果
    st.markdown("### 📦 货物总量计算")
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("总包装数", f"{total_packages:.0f} 个")
    with col_m2:
        st.metric("总毛重", f"{total_gross:,.0f} KGS")
    with col_m3:
        st.metric("总体积", f"{total_volume:.2f} CBM")

    # ==================== 第五步：计算报价 ====================
    st.markdown("""
    <div class="step-container">
        <div class="step-header">
            <span class="step-badge">第五步</span>
            <span class="step-title">计算报价</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_calc1, col_calc2 = st.columns(2)

    with col_calc1:
        if st.button("🚢 计算运费", use_container_width=True):
            containers_needed = np.ceil(total_volume / 33)
            if transport_note == "冷藏":
                st.session_state.best_freight = containers_needed * container_20_frozen
            else:
                st.session_state.best_freight = containers_needed * container_20_normal
            st.session_state.calculated = True
            st.success(f"需要 {containers_needed:.0f} 个集装箱，运费 ${st.session_state.best_freight:,.2f}")

    with col_calc2:
        if st.button("💰 计算报价", use_container_width=True):
            purchase_total = purchase_price * quantity
            rebate = purchase_total / (1 + vat_rate/100) * (export_rebate_rate/100)
            total_cost = purchase_total - rebate + (st.session_state.best_freight * exchange_rate)
            st.session_state.suggested_price = (total_cost * (1 + expected_profit_rate/100)) / quantity / exchange_rate
            st.session_state.total_cost = total_cost

    # 显示计算结果 - 报价和反算利润率并排
    if st.session_state.calculated and st.session_state.suggested_price > 0:
        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            st.markdown("##### 💰 建议报价")
            st.markdown(f"<div class='result-box'>${st.session_state.suggested_price:.2f}/台</div>", unsafe_allow_html=True)
        
        with col_res2:
            st.markdown("##### 📈 反算利润率")
            
            # 计算总成本用于反算
            purchase_total = purchase_price * quantity
            rebate = purchase_total / (1 + vat_rate/100) * (export_rebate_rate/100)
            inland_fee = max(50, total_volume * 10) * exchange_rate
            forwarder_fee = max(70, total_volume * 2.5) * exchange_rate
            customs_fee = 30 * exchange_rate if trade_term != "EXW" else 0
            total_cost = purchase_total - rebate + inland_fee + forwarder_fee + customs_fee + (st.session_state.best_freight * exchange_rate)
            
            # 输入测试价格
            test_price = st.number_input("输入测试报价 (USD/台)", 
                                        value=float(st.session_state.suggested_price),
                                        step=5.0, format="%.2f", key="test_price")
            
            if test_price > 0:
                revenue = test_price * quantity * exchange_rate
                profit = revenue - total_cost
                profit_margin = profit / purchase_total if purchase_total > 0 else 0
                
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    st.metric("利润", f"¥{profit:,.0f}")
                with col_p2:
                    target = expected_profit_rate / 100
                    delta = "✅" if profit_margin >= target else "❌"
                    st.metric("利润率", f"{profit_margin:.1%}", delta=delta)

    # ==================== 第六步：出口预算表 ====================
    st.markdown("""
    <div class="step-container">
        <div class="step-header">
            <span class="step-badge">第六步</span>
            <span class="step-title">出口预算表</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 计算费用
    purchase_total = purchase_price * quantity
    rebate = purchase_total / (1 + vat_rate/100) * (export_rebate_rate/100)
    inland_fee = max(50, total_volume * 10) * exchange_rate
    forwarder_fee = max(70, total_volume * 2.5) * exchange_rate
    customs_fee = 30 * exchange_rate if trade_term != "EXW" else 0

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

    st.markdown(f"""
    <div class="excel-row">
        <div class="excel-label">1.采购成本</div>
        <div class="excel-sub">含税购入价</div>
        <div class="excel-amount">¥{purchase_total:,.2f}</div>
        <div class="excel-principle">{purchase_price} × {quantity}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="excel-row">
        <div class="excel-label">2.退税收入</div>
        <div class="excel-sub">退税额</div>
        <div class="excel-amount">¥{rebate:,.2f}</div>
        <div class="excel-principle">含税价÷(1+{vat_rate}%)×{export_rebate_rate}%</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="excel-row">
        <div class="excel-label">3.国内费用</div>
        <div class="excel-sub">内陆运费</div>
        <div class="excel-amount">¥{inland_fee:,.2f}</div>
        <div class="excel-principle">MAX(50, {total_volume:.1f}×10)×{exchange_rate}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="excel-row">
        <div class="excel-label"></div>
        <div class="excel-sub">国际运费</div>
        <div class="excel-amount">${st.session_state.best_freight:,.2f}</div>
        <div class="excel-principle">集装箱运费</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="excel-row">
        <div class="excel-label"></div>
        <div class="excel-sub">货代杂费</div>
        <div class="excel-amount">¥{forwarder_fee:,.2f}</div>
        <div class="excel-principle">MAX(70, {total_volume:.1f}×2.5)×{exchange_rate}</div>
    </div>
    """, unsafe_allow_html=True)

    if customs_fee > 0:
        st.markdown(f"""
        <div class="excel-row">
            <div class="excel-label"></div>
            <div class="excel-sub">报关费</div>
            <div class="excel-amount">¥{customs_fee:,.2f}</div>
            <div class="excel-principle">30×{exchange_rate}</div>
        </div>
        """, unsafe_allow_html=True)

    total_cost = purchase_total - rebate + inland_fee + forwarder_fee + customs_fee + (st.session_state.best_freight * exchange_rate)

    st.markdown(f"""
    <div class="excel-row" style="background-color: #2a5298; color: white; font-weight: bold;">
        <div class="excel-label">总成本</div>
        <div class="excel-sub">=1-2+3</div>
        <div class="excel-amount">¥{total_cost:,.2f}</div>
        <div class="excel-principle" style="color: white;">采购-退税+国内费用+运费</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="empty-state">
        ⏳ 请先抓取数据，然后进行交易信息填写和计算
    </div>
    """, unsafe_allow_html=True)

# ==================== 底部信息 ====================
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666; padding: 10px; background-color: #f8f9fa; border-radius: 5px;'>
    <div>更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
</div>
""", unsafe_allow_html=True)
