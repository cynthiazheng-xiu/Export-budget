import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import re
import time

st.set_page_config(page_title="出口预算表", page_icon="📊", layout="wide")

# 标题
st.title("📊 出口预算表 - 技能大赛版")

# 初始化数据
if 'data' not in st.session_state:
    st.session_state.data = {}

# PAD抓取按钮
if st.button("🚀 PAD抓取数据"):
    with st.spinner("正在抓取数据..."):
        time.sleep(2)
        st.session_state.data = {
            'product_code': 'P010',
            'product_name': '自动售货机',
            'gross_weight': '280.00KGS/托盘',
            'volume': '2.55CBM/托盘',
            'hs_code': '8476810000',
            'vat_rate': 13,
            'rebate_rate': 13
        }
    st.success("✅ 数据抓取完成！")
    st.balloons()

# 客户信息
st.header("第一步：客户信息")
col1, col2 = st.columns(2)
with col1:
    st.text_input("出口商名称", "平尼克国际贸易公司")
with col2:
    st.text_input("进口商名称", "罗伯茨世界贸易有限公司")

# 产品信息
st.header("第二步：产品信息")
col1, col2 = st.columns(2)
with col1:
    product_code = st.text_input("商品编号", st.session_state.data.get('product_code', 'P010'))
    product_name = st.text_input("商品名称", st.session_state.data.get('product_name', '自动售货机'))
with col2:
    gross_weight = st.text_input("毛重", st.session_state.data.get('gross_weight', '280.00KGS/托盘'))
    volume = st.text_input("体积", st.session_state.data.get('volume', '2.55CBM/托盘'))

# 交易信息
st.header("第三步：交易信息")
col1, col2, col3 = st.columns(3)
with col1:
    quantity = st.number_input("交易数量", 182)
    price = st.number_input("采购单价", 4778.0)
with col2:
    exchange_rate = st.number_input("汇率", 1.368)
    profit_rate = st.slider("预期利润率%", 0, 50, 15)

# 计算按钮
if st.button("计算报价"):
    total = price * quantity
    suggested = total * (1 + profit_rate/100) / quantity / exchange_rate
    st.success(f"建议报价: ${suggested:.2f}/台")

st.markdown("---")
st.caption(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
