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

# 标题
st.title("📊 出口预算表 - 全国职业院校技能大赛版")

# ==================== 初始化session state ====================
if 'product_data' not in st.session_state:
    st.session_state.product_data = {}
if 'hs_data' not in st.session_state:
    st.session_state.hs_data = {}
if 'freight_data' not in st.session_state:
    st.session_state.freight_data = {}
if 'customer_data' not in st.session_state:
    st.session_state.customer_data = {}
if 'best_freight' not in st.session_state:
    st.session_state.best_freight = 0
if 'suggested_price' not in st.session_state:
    st.session_state.suggested_price = 0

# ==================== PAD模拟抓取按钮 ====================
st.markdown("### 🚀 PAD数据抓取")

col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("启动PAD模拟抓取数据", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        steps = ["正在启动...", "读取商品信息...", "读取HS信息...", "读取运费信息...", "完成!"]
        for i, step in enumerate(steps):
            status_text.text(step)
            progress_bar.progress((i + 1) * 20)
            time.sleep(0.5)
        
        # 模拟数据
        st.session_state.product_data = {
            'product_code': 'P010',
            'product_name': '自动售货机',
            'product_name_en': 'Vending machine',
            'gross_weight': '280.00KGS/托盘',
            'net_weight': '220.00KGS/托盘',
            'volume': '2.55CBM/托盘',
            'unit_conversion': '1 SET/PALLET'
        }
        
        st.session_state.hs_data = {
            'hs_code': '8476810000',
            'vat_rate': 13,
            'export_rebate_rate': 13
        }
        
        progress_bar.empty()
        status_text.empty()
        st.success("✅ 数据抓取完成！")
        st.balloons()

# ==================== 客户信息 ====================
st.markdown("### 第一步：客户信息")
col_c1, col_c2 = st.columns(2)

with col_c1:
    st.text_input("公司全称", value=st.session_state.customer_data.get('exporter_name', '平尼克国际贸易公司'), key="exporter_name")
    st.text_input("公司英文名", value=st.session_state.customer_data.get('exporter_name_en', 'Pinic International Trading'), key="exporter_name_en")

with col_c2:
    st.text_input("进口商名称", value=st.session_state.customer_data.get('importer_name', '罗伯茨世界贸易有限公司'), key="importer_name")
    st.text_input("进口商英文名", value=st.session_state.customer_data.get('importer_name_en', 'Roberts World Traders Inc.'), key="importer_name_en")

# ==================== 产品信息 ====================
st.markdown("### 第二步：产品信息")
col_p1, col_p2 = st.columns(2)

with col_p1:
    product_code = st.text_input("商品编号", value=st.session_state.product_data.get('product_code', 'P010'), key="product_code")
    product_name = st.text_input("商品名称", value=st.session_state.product_data.get('product_name', '自动售货机'), key="product_name")

with col_p2:
    gross_weight = st.text_input("毛重", value=st.session_state.product_data.get('gross_weight', '280.00KGS/托盘'), key="gross_weight")
    volume = st.text_input("体积", value=st.session_state.product_data.get('volume', '2.55CBM/托盘'), key="volume")
    unit_conversion = st.text_input("单位换算", value=st.session_state.product_data.get('unit_conversion', '1 SET/PALLET'), key="unit_conversion")

# ==================== HS信息 ====================
st.markdown("### 第三步：HS信息")
col_h1, col_h2 = st.columns(2)

with col_h1:
    hs_code = st.text_input("HS编码", value=st.session_state.hs_data.get('hs_code', '8476810000'), key="hs_code")
with col_h2:
    vat_rate = st.number_input("增值税率(%)", value=float(st.session_state.hs_data.get('vat_rate', 13)), key="vat_rate")
    export_rebate_rate = st.number_input("出口退税率(%)", value=float(st.session_state.hs_data.get('export_rebate_rate', 13)), key="export_rebate_rate")

# ==================== 物流信息 ====================
st.markdown("### 第四步：物流信息")
col_l1, col_l2 = st.columns(2)

with col_l1:
    st.markdown("**普柜单价**")
    container_20_normal = st.number_input("20'GP", value=1452, key="container_20_normal")
    container_40_normal = st.number_input("40'GP", value=2613, key="container_40_normal")

with col_l2:
    st.markdown("**冻柜单价**")
    container_20_frozen = st.number_input("20'RF", value=2903, key="container_20_frozen")
    container_40_frozen = st.number_input("40'RF", value=5225, key="container_40_frozen")

# ==================== 交易信息 ====================
st.markdown("### 第五步：交易信息")
col_t1, col_t2, col_t3 = st.columns(3)

with col_t1:
    quantity = st.number_input("交易数量", value=182, step=1, key="quantity")
    purchase_price = st.number_input("采购单价", value=4778.0, step=100.0, key="purchase_price")

with col_t2:
    exchange_rate = st.number_input("USD/CAD 汇率", value=1.368, step=0.001, key="exchange_rate")
    trade_term = st.selectbox("贸易术语", ["FOB", "CIF", "EXW"], key="trade_term")

with col_t3:
    expected_profit_rate = st.slider("预期利润率(%)", 0, 50, 15, key="expected_profit_rate")
    transport_note = st.selectbox("运输要求", ["普通", "冷藏"], key="transport_note")

# ==================== 提取数值 ====================
def extract_number(text):
    try:
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", str(text))
        return float(numbers[0]) if numbers else 0
    except:
        return 0

# 计算
single_gross = extract_number(gross_weight)
single_volume = extract_number(volume)
units_per_package = extract_number(unit_conversion)
total_packages = np.ceil(quantity / units_per_package) if units_per_package > 0 else quantity
total_volume = total_packages * single_volume

# ==================== 计算报价 ====================
st.markdown("### 第六步：计算报价")

col_b1, col_b2 = st.columns(2)
with col_b1:
    if st.button("计算最优集装箱", use_container_width=True):
        # 简单计算
        containers_needed = np.ceil(total_volume / 33)
        st.session_state.best_freight = containers_needed * container_20_normal
        st.success(f"需要 {containers_needed:.0f} 个集装箱")

with col_b2:
    if st.button("计算建议报价", use_container_width=True):
        purchase_total = purchase_price * quantity
        rebate = purchase_total / (1 + vat_rate/100) * (export_rebate_rate/100)
        total_cost = purchase_total - rebate + (st.session_state.best_freight * exchange_rate)
        st.session_state.suggested_price = (total_cost * (1 + expected_profit_rate/100)) / quantity / exchange_rate

if st.session_state.suggested_price > 0:
    st.metric("建议报价", f"${st.session_state.suggested_price:.2f}/台")

# ==================== 保存按钮 ====================
if st.button("💾 保存数据", use_container_width=True):
    st.success("✅ 数据已保存！")
    st.balloons()
