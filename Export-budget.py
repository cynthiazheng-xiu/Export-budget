import subprocess
import sys

# 安装需要的包
packages = ['plotly', 'pandas', 'numpy']
for package in packages:
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import re
import plotly.graph_objects as go

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
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 30px;
    }
    .section-title {
        font-size: 1.5rem;
        color: #2c3e50;
        border-left: 5px solid #3498db;
        padding-left: 15px;
        margin: 20px 0;
    }
    .metric-box {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .formula-hint {
        font-size: 0.8rem;
        color: #666;
        background-color: #f8f9fa;
        padding: 5px 10px;
        border-radius: 5px;
        border-left: 3px solid #3498db;
        margin: 5px 0 10px 0;
        font-family: monospace;
    }
    .calculation-box {
        background-color: #f0f8ff;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# 标题
st.markdown('<div class="main-title">📊 出口预算表系统 - 省赛版V1</div>', unsafe_allow_html=True)

# 从文本中提取数字的函数
def extract_number(text):
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", text)
    return float(numbers[0]) if numbers else 0

# 侧边栏 - 基础设置
with st.sidebar:
    st.markdown("### ⚙️ 基础设置")
    
    # 汇率设置
    exchange_rate = st.number_input("USD/CAD 汇率", value=1.368, step=0.001, format="%.3f")
    st.markdown('<div class="formula-hint">公式: USD1 = CAD' + str(exchange_rate) + '</div>', unsafe_allow_html=True)
    
    # 账户信息
    account_balance = st.number_input("账户余额", value=1888000.0, step=1000.0)
    
    st.markdown("---")
    st.markdown("### 📦 集装箱数据")
    
    container_types = {
        "20'普柜": {"体积": 33, "重量": 25000, "单价": 1452, "冷冻": False},
        "40'普柜": {"体积": 67, "重量": 29000, "单价": 2613, "冷冻": False},
        "40'高柜": {"体积": 76, "重量": 29000, "单价": 3135, "冷冻": False},
        "20'冻柜": {"体积": 27, "重量": 27400, "单价": 2903, "冷冻": True},
        "40'冻柜": {"体积": 58, "重量": 27700, "单价": 5225, "冷冻": True},
        "40'冻高": {"体积": 66, "重量": 29000, "单价": 6270, "冷冻": True}
    }

# 主界面 - 两列布局
col1, col2 = st.columns([1, 1])

# ==================== 左侧：商品信息 ====================
with col1:
    st.markdown('<div class="section-title">📝 商品信息</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown("#### 基础信息")
        product_code = st.text_input("商品编号", "P010")
        product_name = st.text_input("商品名称", "自动售货机")
        hs_code = st.text_input("HS编码", "8476810000")
        
        st.markdown("#### 包装信息")
        col_a, col_b = st.columns(2)
        with col_a:
            package_unit = st.text_input("包装单位", "托盘(PALLET)")
            gross_weight = st.text_input("毛重", "280.00KGS/托盘")
            volume = st.text_input("体积", "2.55CBM/托盘")
        with col_b:
            unit_convert = st.text_input("单位换算", "1 SET/PALLET")
            net_weight = st.text_input("净重", "220.00KGS/托盘")
            transport_note = st.selectbox("运输要求", ["普通", "冷藏", "冷冻"])

# ==================== 右侧：交易信息 ====================
with col2:
    st.markdown('<div class="section-title">💰 交易信息</div>', unsafe_allow_html=True)
    
    with st.container():
        col_c, col_d = st.columns(2)
        with col_c:
            purchase_price = st.number_input("采购单价", value=4778.0, step=100.0)
            quantity = st.number_input("交易数量", value=182, step=1)
        with col_d:
            trade_term = st.selectbox("贸易术语", ["EXW", "FCA", "FAS", "FOB", "CFR", "CIF", "CIP", "DAP", "DPU", "DDP"])
            payment = st.selectbox("支付方式", ["T/T", "L/C", "D/P", "T/T+LC"])
        
        vat_rate = st.number_input("增值税率(%)", value=13.0) / 100
        rebate_rate = st.number_input("出口退税率(%)", value=13.0) / 100

# ==================== 计算区域 ====================
st.markdown('<div class="section-title">📊 计算结果</div>', unsafe_allow_html=True)

# 提取包装数据
single_gross = extract_number(gross_weight)
single_net = extract_number(net_weight)
single_volume = extract_number(volume)
units_per_package = extract_number(unit_convert)

# 计算总包装数
total_packages = np.ceil(quantity / units_per_package) if units_per_package > 0 else quantity

# 计算总重量和体积
total_gross = total_packages * single_gross
total_net = total_packages * single_net
total_volume = total_packages * single_volume

# 显示基本计算
col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)

with col_metric1:
    st.metric("总包装数", f"{total_packages:.0f}")
    st.markdown("""
    <div class="formula-hint">
        📐 公式: =ROUNDUP(交易数量/单位换算,0)<br>
        =ROUNDUP(""" + str(quantity) + """/""" + str(units_per_package) + """,0) = """ + str(total_packages) + """
    </div>
    """, unsafe_allow_html=True)

with col_metric2:
    st.metric("总毛重(KGS)", f"{total_gross:,.0f}")
    st.markdown("""
    <div class="formula-hint">
        📐 公式: 总包装数 × 单件毛重<br>
        =""" + str(total_packages) + """ × """ + str(single_gross) + """ = """ + f"{total_gross:,.0f}" + """
    </div>
    """, unsafe_allow_html=True)

with col_metric3:
    st.metric("总净重(KGS)", f"{total_net:,.0f}")
    st.markdown("""
    <div class="formula-hint">
        📐 公式: 总包装数 × 单件净重<br>
        =""" + str(total_packages) + """ × """ + str(single_net) + """ = """ + f"{total_net:,.0f}" + """
    </div>
    """, unsafe_allow_html=True)

with col_metric4:
    st.metric("总体积(CBM)", f"{total_volume:,.2f}")
    st.markdown("""
    <div class="formula-hint">
        📐 公式: 总包装数 × 单件体积<br>
        =""" + str(total_packages) + """ × """ + str(single_volume) + """ = """ + f"{total_volume:,.2f}" + """
    </div>
    """, unsafe_allow_html=True)

# ==================== 成本计算 ====================
st.markdown("### 💰 成本明细")

col_cost1, col_cost2, col_cost3 = st.columns(3)

with col_cost1:
    st.markdown("#### 采购成本")
    purchase_total = purchase_price * quantity
    st.metric("含税购入价", f"¥{purchase_total:,.2f}")
    st.markdown("""
    <div class="formula-hint">
        📐 公式: =采购单价 × 交易数量<br>
        =""" + str(purchase_price) + """ × """ + str(quantity) + """ = """ + f"{purchase_total:,.2f}" + """
    </div>
    """, unsafe_allow_html=True)
    
    rebate = purchase_total / (1 + vat_rate) * rebate_rate
    st.metric("退税收入", f"¥{rebate:,.2f}")
    st.markdown("""
    <div class="formula-hint">
        📐 公式: =含税购入价/(1+增值税率)×出口退税率<br>
        =""" + f"{purchase_total:,.2f}" + """/(1+""" + str(vat_rate*100) + """%)×""" + str(rebate_rate*100) + """% = """ + f"{rebate:,.2f}" + """
    </div>
    """, unsafe_allow_html=True)

with col_cost2:
    st.markdown("#### 国内费用")
    # 内陆运费（按体积计算，最低50）
    inland_fee_base = max(50, total_volume * 10)
    inland_fee = inland_fee_base * exchange_rate
    st.metric("内陆运费", f"¥{inland_fee:,.2f}")
    st.markdown("""
    <div class="formula-hint">
        📐 公式: =IF(10×总体积<50,50,10×总体积)×汇率<br>
        =IF(10×""" + f"{total_volume:.2f}" + """<50,50,""" + f"{10*total_volume:.2f}" + """)×""" + str(exchange_rate) + """ = """ + f"{inland_fee:,.2f}" + """
    </div>
    """, unsafe_allow_html=True)
    
    # 报关报检费
    customs_fee = 30 * exchange_rate
    inspection_fee = 30 * exchange_rate
    st.metric("报关+报检", f"¥{customs_fee + inspection_fee:,.2f}")
    st.markdown("""
    <div class="formula-hint">
        📐 公式: =IF(贸易术语="EXW",0,30×汇率) + 30×汇率<br>
        =30×""" + str(exchange_rate) + """ + 30×""" + str(exchange_rate) + """ = """ + f"{customs_fee + inspection_fee:,.2f}" + """
    </div>
    """, unsafe_allow_html=True)

with col_cost3:
    st.markdown("#### 其他费用")
    # 保险费（CIF/CIP等情况）
    if trade_term in ["CIF", "CIP", "DAP", "DPU", "DDP"]:
        insurance = purchase_total * 1.1 * 0.005
        st.metric("保险费", f"¥{insurance:,.2f}")
        st.markdown("""
        <div class="formula-hint">
            📐 公式: =采购成本×110%×0.5%<br>
            =""" + f"{purchase_total:,.2f}" + """×1.1×0.005 = """ + f"{insurance:,.2f}" + """
        </div>
        """, unsafe_allow_html=True)
    
    # 银行费用
    if "L/C" in payment:
        lc_fee = max(15, purchase_total * 0.00125) + 75
        st.metric("信用证费", f"${lc_fee:.2f}")
        st.markdown("""
        <div class="formula-hint">
            📐 公式: =MAX(15,采购成本×0.125%)+75<br>
            =MAX(15,""" + f"{purchase_total*0.00125:.2f}" + """)+75 = """ + f"{lc_fee:.2f}" + """
        </div>
        """, unsafe_allow_html=True)
    elif payment in ["D/P", "D/A"]:
        collection_fee = max(15, min(285, purchase_total * 0.001)) + 45
        st.metric("托收费", f"${collection_fee:.2f}")
        st.markdown("""
        <div class="formula-hint">
            📐 公式: =MAX(15,MIN(285,采购成本×0.1%))+45<br>
            =MAX(15,MIN(285,""" + f"{purchase_total*0.001:.2f}" + """))+45 = """ + f"{collection_fee:.2f}" + """
        </div>
        """, unsafe_allow_html=True)

# ==================== 运费计算 ====================
st.markdown("### 🚢 运费计算")

# 判断运输方式
if total_gross > 25000 or total_volume > 33:
    st.warning("⚠️ 货物超过拼箱限制，建议使用整箱(FCL)")
    shipping_type = "FCL"
    st.markdown("""
    <div class="formula-hint">
        📐 判断逻辑: IF(总毛重>25000 OR 总体积>33, "FCL", "LCL/FCL")<br>
        总毛重=""" + f"{total_gross:,.0f}" + """ > 25000?""" + str(total_gross > 25000) + """, 总体积=""" + f"{total_volume:.2f}" + """ > 33?""" + str(total_volume > 33) + """
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("✅ 货物适合拼箱(LCL)或整箱(FCL)")
    shipping_type = "LCL/FCL"

# 集装箱选择
st.markdown("#### 选择集装箱类型")

# 创建集装箱选择列表
valid_containers = []
for name, data in container_types.items():
    if data["冷冻"] and transport_note != "冷冻":
        continue
    valid_containers.append(name)

selected_container = st.selectbox("集装箱类型", valid_containers)

if selected_container:
    container = container_types[selected_container]
    
    # 计算每箱可装数量
    qty_by_vol = container["体积"] / single_volume
    qty_by_weight = container["重量"] / single_gross
    max_qty_per_container = min(qty_by_vol, qty_by_weight)
    
    # 计算需要多少箱
    containers_needed = np.ceil(quantity / max_qty_per_container)
    total_freight = containers_needed * container["单价"]
    
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.metric("每箱可装", f"{max_qty_per_container:.0f}台")
        st.markdown("""
        <div class="formula-hint">
            📐 公式: =MIN(柜体积/单件体积, 柜重量/单件毛重)<br>
            =MIN(""" + str(container["体积"]) + """/""" + f"{single_volume:.2f}" + """, """ + str(container["重量"]) + """/""" + f"{single_gross:.2f}" + """)<br>
            =MIN(""" + f"{qty_by_vol:.2f}" + """, """ + f"{qty_by_weight:.2f}" + """) = """ + f"{max_qty_per_container:.0f}" + """
        </div>
        """, unsafe_allow_html=True)
    
    with col_f2:
        st.metric("需要箱数", f"{containers_needed:.0f}")
        st.markdown("""
        <div class="formula-hint">
            📐 公式: =ROUNDUP(交易数量/每箱可装数量,0)<br>
            =ROUNDUP(""" + str(quantity) + """/""" + f"{max_qty_per_container:.2f}" + """,0) = """ + f"{containers_needed:.0f}" + """
        </div>
        """, unsafe_allow_html=True)
    
    with col_f3:
        st.metric("运费(USD)", f"${total_freight:,.2f}")
        st.markdown("""
        <div class="formula-hint">
            📐 公式: =需要箱数 × 柜单价<br>
            =""" + f"{containers_needed:.0f}" + """ × """ + str(container["单价"]) + """ = """ + f"{total_freight:,.2f}" + """
        </div>
        """, unsafe_allow_html=True)

# ==================== 利润分析 ====================
st.markdown("### 📈 利润预测")

col_p1, col_p2 = st.columns(2)

with col_p1:
    st.markdown("#### 报价设置")
    profit_rate = st.slider("预期利润率(%)", 0, 50, 15) / 100
    
    # 计算总成本和报价
    total_cost = purchase_total - rebate
    suggested_price = (total_cost * (1 + profit_rate)) / quantity / exchange_rate
    
    st.metric("建议报价(USD/台)", f"${suggested_price:.2f}")
    st.markdown("""
    <div class="formula-hint">
        📐 公式: =[(采购成本-退税收入)×(1+预期利润率)]/(交易数量×汇率)<br>
        =[(""" + f"{purchase_total:,.2f}" + """ - """ + f"{rebate:,.2f}" + """)×(1+""" + f"{profit_rate:.0%}" + """)]/(""" + str(quantity) + """×""" + str(exchange_rate) + """)<br>
        =""" + f"{suggested_price:.2f}" + """
    </div>
    """, unsafe_allow_html=True)
    
    actual_price = st.number_input("实际报价(USD/台)", value=round(suggested_price, 2), step=10.0)

with col_p2:
    st.markdown("#### 盈亏分析")
    revenue = actual_price * quantity * exchange_rate
    expense = purchase_total - rebate
    
    profit = revenue - expense
    profit_margin = profit / purchase_total
    
    st.metric("总收入", f"¥{revenue:,.2f}")
    st.markdown("""
    <div class="formula-hint">
        📐 公式: =实际报价 × 交易数量 × 汇率<br>
        =""" + str(actual_price) + """ × """ + str(quantity) + """ × """ + str(exchange_rate) + """ = """ + f"{revenue:,.2f}" + """
    </div>
    """, unsafe_allow_html=True)
    
    st.metric("总支出", f"¥{expense:,.2f}")
    st.markdown("""
    <div class="formula-hint">
        📐 公式: =采购成本 - 退税收入<br>
        =""" + f"{purchase_total:,.2f}" + """ - """ + f"{rebate:,.2f}" + """ = """ + f"{expense:,.2f}" + """
    </div>
    """, unsafe_allow_html=True)
    
    st.metric("预期利润", f"¥{profit:,.2f}")
    st.markdown("""
    <div class="formula-hint">
        📐 公式: =总收入 - 总支出<br>
        =""" + f"{revenue:,.2f}" + """ - """ + f"{expense:,.2f}" + """ = """ + f"{profit:,.2f}" + """
    </div>
    """, unsafe_allow_html=True)
    
    st.metric("利润率", f"{profit_margin:.2%}")
    st.markdown("""
    <div class="formula-hint">
        📐 公式: =预期利润 / 采购成本<br>
        =""" + f"{profit:,.2f}" + """ / """ + f"{purchase_total:,.2f}" + """ = """ + f"{profit_margin:.2%}" + """
    </div>
    """, unsafe_allow_html=True)

# ==================== 数据可视化 ====================
st.markdown("### 📊 成本构成图")

# 准备图表数据
cost_data = pd.DataFrame({
    '项目': ['采购成本', '退税收入(减项)', '国内费用', '运费'],
    '金额': [
        purchase_total,
        -rebate,
        inland_fee + customs_fee + inspection_fee,
        total_freight * exchange_rate if selected_container else 0
    ]
})

fig = px.pie(cost_data, values='金额', names='项目', 
             title='成本构成分析 (退税收入为负数表示收入)',
             color_discrete_sequence=px.colors.qualitative.Set3)
st.plotly_chart(fig, use_container_width=True)

# 添加公式汇总说明
with st.expander("📚 查看所有公式汇总"):
    st.markdown("""
    ### 主要计算公式汇总
    
    | 项目 | Excel公式 | 说明 |
    |------|----------|------|
    | 总包装数 | `=ROUNDUP(J24/LEFT(E12,FIND(" ",E12)-1),0)` | 交易数量 ÷ 单位换算，向上取整 |
    | 总毛重 | `=ROUNDUP($J$24/LEFT($E$12,FIND(" ",$E$12)-1),0)*(LEFT($C$13,FIND("K",$C$13)-1)-LEFT($E$13,FIND("K",$E$13)-1))+J24*(LEFT($E$13,FIND("K",$E$13)-1)/LEFT($E$12,FIND(" ",$E$12)-1))` | 包装毛重 + 产品净重 |
    | 总净重 | `=J24*(LEFT($E$13,FIND("K",$E$13)-1)/LEFT($E$12,FIND(" ",$E$12)-1))` | 交易数量 × 单件净重 |
    | 总体积 | `=ROUNDUP($J$24/LEFT($E$12,FIND(" ",$E$12)-1),0)*LEFT($C$14,FIND("C",$C$14)-1)` | 包装数 × 单件体积 |
    | 退税收入 | `=+Q7/(1+H35/100)*L35/100` | 含税价 ÷ (1+增值税率) × 退税率 |
    | 内陆运费 | `=+IF(10*LEFT(C14,FIND("C",C14)-1)*ROUNDUP(J24/LEFT(E12,FIND(" ",E12)-1),0)<50,50,LEFT(C14,FIND("C",C14)-1)*ROUNDUP(J24/LEFT(E12,FIND(" ",E12)-1),0)*10)*Q6` | 按体积计算，最低50，乘以汇率 |
    | 保险费 | `=+IF(OR(J28="CIP", J28="CIF", J28="DAP", J28="DPU", J28="DDP"), Q26*1.1*0.005, 0)` | 特定贸易术语下，成本×110%×0.5% |
    | 信用证费 | `=IF(M30="","",(IF(Q26*M30*0.125/100/Q6<15,15,Q26*M30*0.125/100/Q6)+75)*Q6)` | 最低15美元+75美元操作费 |
    | 托收费 | `=+IF(L30="","",IF(Q26*L30/Q6*0.001<15,15,IF(Q26*L30/Q6*0.001>285,285,Q26*L30/Q6*0.001))*Q6+45*Q6)` | 0.1%费用，15-285美元之间+45美元 |
    | 报价 | `=Q24*(1+J32)/J24/Q6` | 总成本×(1+利润率) ÷ 数量 ÷ 汇率 |
    """)

# ==================== 底部信息 ====================
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: gray; padding: 10px;'>
    更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
    汇率: USD1 = CAD{exchange_rate} |
    交易数量: {quantity}台
</div>
""", unsafe_allow_html=True)

# 保存功能
if st.button("💾 保存当前数据"):
    st.success("✅ 数据已保存！")
    st.balloons()
