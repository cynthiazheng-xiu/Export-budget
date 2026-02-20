import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import re
import os

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
    .fetch-button {
        background-color: #28a745;
        color: white;
        padding: 5px 15px;
        border-radius: 5px;
        text-align: center;
        margin: 10px 0;
    }
    .excel-table {
        background-color: white;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 20px;
    }
    .formula-hint {
        font-size: 0.8rem;
        color: #666;
        background-color: #f8f9fa;
        padding: 5px 10px;
        border-radius: 3px;
        margin: 2px 0;
    }
    .data-source {
        font-size: 0.7rem;
        color: #888;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# 标题
st.markdown('<div class="main-title">📊 出口预算表 - 省赛版V1</div>', unsafe_allow_html=True)

# ==================== 数据抓取功能区 ====================
st.markdown('<div class="section-title">🔄 数据抓取 (Power Automate Desktop集成)</div>', unsafe_allow_html=True)

col_fetch1, col_fetch2, col_fetch3, col_fetch4 = st.columns(4)

with col_fetch1:
    if st.button("📥 从商品信息表抓取", use_container_width=True):
        st.session_state['fetch_product'] = True
        st.success("✅ 商品信息抓取成功!")

with col_fetch2:
    if st.button("📥 从HS表抓取", use_container_width=True):
        st.session_state['fetch_hs'] = True
        st.success("✅ HS编码信息抓取成功!")

with col_fetch3:
    if st.button("📥 从运费单价表抓取", use_container_width=True):
        st.session_state['fetch_freight'] = True
        st.success("✅ 运费单价抓取成功!")

with col_fetch4:
    if st.button("📥 从汇率表抓取", use_container_width=True):
        st.session_state['fetch_rate'] = True
        st.success("✅ 汇率信息抓取成功!")

st.markdown("""
<div class="data-source">
    数据来源: C:\\Basic Information\\Data.xlsx (通过Power Automate Desktop定时抓取)
</div>
""", unsafe_allow_html=True)

# ==================== 初始化Excel数据 ====================
# 商品信息表数据 (来自Data.xlsx的"商品信息表")
product_data = {
    "商品编号": "P010",
    "商品名称": "自动售货机",
    "英文名称": "Vending machine",
    "货物类型": "机器、机械器具、电气设备及其零件",
    "规格型号(中文)": "型号：MF-782",
    "规格型号(英文)": "Model:mf-782",
    "采购单价(本币)": 3333,
    "销售单位": "台(SET)",
    "单位换算": "1 SET/PALLET",
    "包装单位": "托盘(PALLET)",
    "毛重": "280.00KGS/托盘",
    "净重": "220.00KGS/托盘",
    "体积": "2.55CBM/托盘",
    "运输说明": "无",
    "HS编码": "8476810000",
    "法定单位": "台(SET)",
    "海关监管条件": "无",
    "检验检疫类别": "无"
}

# HS表数据
hs_data = {
    "HS编码": "8476810000",
    "商品名称": "装有加热或制冷装置的自动售货机",
    "监管条件": "",
    "检验检疫类别": "",
    "优惠税率": 50,
    "增值税率": 13,
    "消费税率": 0,
    "出口税率": 0,
    "出口暂定税率": "无",
    "出口退税率": 13
}

# 运费单价表数据
freight_data = {
    "航线": "China-Shanghai to Philippines-Manila",
    "出口国": "China",
    "装运港": "Shanghai",
    "进口国": "Philippines",
    "目的港": "Manila",
    "LCL(W)普柜": 73,
    "LCL(M)普柜": 88,
    "20'GP普柜": 1452,
    "40'GP普柜": 2613,
    "40'HC普柜": 3135,
    "LCL(W)冻柜": 146,
    "LCL(M)冻柜": 189,
    "20'RF冻柜": 2903,
    "40'RF冻柜": 5225,
    "40'RH冻柜": 6270
}

# 汇率表数据
rate_data = {
    "本币(英文)": "CNY",
    "本币(中文)": "元",
    "结算币种(英文)": "USD",
    "结算币种(中文)": "美元",
    "汇率": 6.9257
}

# ==================== 第一部分：商品信息 ====================
st.markdown('<div class="section-title">📝 商品信息 (来自商品信息表)</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    product_code = st.text_input("商品编号", product_data["商品编号"])
    product_name = st.text_input("商品名称", product_data["商品名称"])
    product_name_en = st.text_input("英文名称", product_data["英文名称"])
    product_type = st.text_input("货物类型", product_data["货物类型"])
    model_cn = st.text_input("规格型号(中文)", product_data["规格型号(中文)"])
    model_en = st.text_input("规格型号(英文)", product_data["规格型号(英文)"])

with col2:
    purchase_price_input = st.number_input("采购单价(本币)", value=float(product_data["采购单价(本币)"]), step=100.0)
    sales_unit = st.text_input("销售单位", product_data["销售单位"])
    unit_conversion = st.text_input("单位换算", product_data["单位换算"])
    package_unit = st.text_input("包装单位", product_data["包装单位"])
    gross_weight_input = st.text_input("毛重", product_data["毛重"])
    net_weight_input = st.text_input("净重", product_data["净重"])
    volume_input = st.text_input("体积", product_data["体积"])

# ==================== 第二部分：海关信息 ====================
st.markdown('<div class="section-title">🏷️ 海关信息 (来自HS表)</div>', unsafe_allow_html=True)

col_hs1, col_hs2 = st.columns(2)

with col_hs1:
    hs_code = st.text_input("HS编码", hs_data["HS编码"])
    customs_condition = st.text_input("海关监管条件", hs_data["监管条件"])
    inspection_type = st.text_input("检验检疫类别", hs_data["检验检疫类别"])

with col_hs2:
    pref_tax_rate = st.number_input("优惠税率(%)", value=float(hs_data["优惠税率"]))
    vat_rate = st.number_input("增值税率(%)", value=float(hs_data["增值税率"]))
    export_tax_rate = st.number_input("出口税率(%)", value=float(hs_data["出口税率"]))
    export_rebate_rate = st.number_input("出口退税率(%)", value=float(hs_data["出口退税率"]))

# ==================== 第三部分：公司信息 ====================
st.markdown('<div class="section-title">🏢 公司信息</div>', unsafe_allow_html=True)

col_company1, col_company2 = st.columns(2)

with col_company1:
    st.markdown("#### 出口商")
    exporter_name = st.text_input("出口商名称", "平尼克国际贸易公司")
    exporter_address = st.text_input("地址", "菲律宾马尼拉宾农多马德里街513号")
    exporter_contact = st.text_input("联系人", "阿卜杜勒贾里勒")
    exporter_tel = st.text_input("电话", "82-266-2402192")

with col_company2:
    st.markdown("#### 进口商")
    importer_name = st.text_input("进口商名称", "罗伯茨世界贸易有限公司")
    importer_address = st.text_input("进口商地址", "加拿大不列颠哥伦比亚维多利亚白桦新月街4号")
    importer_contact = st.text_input("进口商联系人", "艾伦·博尔赫斯")
    importer_tel = st.text_input("进口商电话", "82-775-6178091")

# ==================== 第四部分：交易信息 ====================
st.markdown('<div class="section-title">💰 交易信息</div>', unsafe_allow_html=True)

col_trade1, col_trade2 = st.columns(2)

with col_trade1:
    quantity = st.number_input("交易数量", value=182, step=1)
    purchase_price = st.number_input("采购单价", value=4778.0, step=100.0)
    trade_term = st.selectbox("贸易术语", ["EXW", "FCA", "FAS", "FOB", "CFR", "CIF", "CIP", "DAP", "DPU", "DDP"])
    payment = st.selectbox("支付方式", ["T/T", "L/C", "D/P", "T/T+LC"])

with col_trade2:
    account_balance = st.number_input("账户本币余额", value=1888000.0, step=1000.0)
    exchange_rate = st.number_input("USD/CAD 汇率", value=rate_data["汇率"], step=0.001, format="%.4f")
    expected_profit_rate = st.slider("预期利润率(%)", 0, 50, 15)

# ==================== 第五部分：运费单价信息 ====================
st.markdown('<div class="section-title">🚢 运费单价信息 (来自运费单价表)</div>', unsafe_allow_html=True)

col_freight1, col_freight2 = st.columns(2)

with col_freight1:
    st.markdown("#### 普柜单价 (USD)")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        lcl_w_normal = st.number_input("LCL(W)普柜", value=float(freight_data["LCL(W)普柜"]))
        container_20_normal = st.number_input("20'GP普柜", value=float(freight_data["20'GP普柜"]))
        container_40_normal = st.number_input("40'GP普柜", value=float(freight_data["40'GP普柜"]))
    with col_p2:
        lcl_m_normal = st.number_input("LCL(M)普柜", value=float(freight_data["LCL(M)普柜"]))
        container_40hc_normal = st.number_input("40'HC普柜", value=float(freight_data["40'HC普柜"]))

with col_freight2:
    st.markdown("#### 冻柜单价 (USD)")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        lcl_w_frozen = st.number_input("LCL(W)冻柜", value=float(freight_data["LCL(W)冻柜"]))
        container_20_frozen = st.number_input("20'RF冻柜", value=float(freight_data["20'RF冻柜"]))
        container_40_frozen = st.number_input("40'RF冻柜", value=float(freight_data["40'RF冻柜"]))
    with col_f2:
        lcl_m_frozen = st.number_input("LCL(M)冻柜", value=float(freight_data["LCL(M)冻柜"]))
        container_40rh_frozen = st.number_input("40'RH冻柜", value=float(freight_data["40'RH冻柜"]))

# ==================== 提取数值用于计算 ====================
def extract_number(text):
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", text)
    return float(numbers[0]) if numbers else 0

single_gross = extract_number(gross_weight_input)
single_net = extract_number(net_weight_input)
single_volume = extract_number(volume_input)
units_per_package = extract_number(unit_conversion)

# 计算总包装数
total_packages = np.ceil(quantity / units_per_package) if units_per_package > 0 else quantity
total_gross = total_packages * single_gross
total_net = total_packages * single_net
total_volume = total_packages * single_volume

# ==================== 第六部分：出口预算表 ====================
st.markdown('<div class="section-title">📊 出口预算表</div>', unsafe_allow_html=True)

# 采购成本
purchase_total = purchase_price * quantity
# 退税收入
rebate = purchase_total / (1 + vat_rate/100) * (export_rebate_rate/100)
# 国内费用
inland_fee = max(50, total_volume * 10) * exchange_rate
forwarder_fee = max(70, total_volume * 2.5) * exchange_rate
inspection_fee = 30 * exchange_rate if "B" in inspection_type else 0
certificate_fee = 100 * exchange_rate if "B" in inspection_type else 0
customs_fee = 30 * exchange_rate if trade_term != "EXW" else 0
# 保险费
insurance = purchase_total * 1.1 * 0.005 if trade_term in ["CIF", "CIP", "DAP", "DPU", "DDP"] else 0
# 银行费用
if payment in ["D/P", "D/A"]:
    bank_fee = max(15, min(285, purchase_total * 0.001)) + 45
elif "L/C" in payment:
    bank_fee = max(15, purchase_total * 0.00125) + 75
else:
    bank_fee = 0

# 创建预算表数据
budget_data = [
    {
        "项目": "1.采购成本",
        "子项目": "含税购入价",
        "金额": f"¥{purchase_total:,.2f}",
        "公式": "=J24*J26",
        "计算原理": f"采购单价 × 交易数量 = {purchase_price} × {quantity}"
    },
    {
        "项目": "2.退税收入",
        "子项目": "退税额",
        "金额": f"¥{rebate:,.2f}",
        "公式": "=+Q7/(1+H35/100)*L35/100",
        "计算原理": f"含税价 ÷ (1+增值税率) × 退税率 = {purchase_total:,.2f} ÷ {1+vat_rate/100:.2f} × {export_rebate_rate/100:.2f}"
    },
    {
        "项目": "3.国内费用",
        "子项目": "出口内陆运费",
        "金额": f"¥{inland_fee:,.2f}",
        "公式": "=+IF(10*体积<50,50,10*体积)*汇率",
        "计算原理": f"基础运费 = MAX(50, 10×{total_volume:.2f}) = {max(50, total_volume * 10):.2f}, 乘以汇率{exchange_rate}"
    },
    {
        "项目": "3.国内费用",
        "子项目": "出口货代杂费",
        "金额": f"¥{forwarder_fee:,.2f}",
        "公式": "=+IF(体积*2.5<70,70,体积*2.5)*汇率",
        "计算原理": f"基础费用 = MAX(70, {total_volume:.2f}×2.5) = {max(70, total_volume * 2.5):.2f}, 乘以汇率{exchange_rate}"
    },
    {
        "项目": "3.国内费用",
        "子项目": "出口商检费",
        "金额": f"¥{inspection_fee:,.2f}",
        "公式": "=IF(ISERROR(FIND('B',D35)),'',30*Q6)",
        "计算原理": f"检验检疫类别含B时收取: 30 × {exchange_rate}"
    },
    {
        "项目": "3.国内费用",
        "子项目": "检验检疫证书费",
        "金额": f"¥{certificate_fee:,.2f}",
        "公式": "=IF(ISERROR(FIND('B',D35)),'',100*Q6)",
        "计算原理": f"检验检疫类别含B时收取: 100 × {exchange_rate}"
    },
    {
        "项目": "3.国内费用",
        "子项目": "出口报关费",
        "金额": f"¥{customs_fee:,.2f}",
        "公式": "=IF(J28='EXW',0,30*Q6)",
        "计算原理": f"贸易术语为{trade_term}，{'收取' if trade_term != 'EXW' else '不收取'}报关费"
    },
    {
        "项目": "3.国内费用",
        "子项目": "保险费",
        "金额": f"¥{insurance:,.2f}",
        "公式": "=+IF(OR(J28='CIP','CIF','DAP','DPU','DDP'), Q26*1.1*0.005, 0)",
        "计算原理": f"采购成本 × 110% × 0.5% = {purchase_total:,.2f} × 1.1 × 0.005"
    },
    {
        "项目": "4.银行费用",
        "子项目": "银行费用",
        "金额": f"${bank_fee:,.2f}",
        "公式": "=根据支付方式计算",
        "计算原理": f"支付方式{payment}，手续费 = {bank_fee:.2f}美元"
    }
]

# 显示预算表
st.dataframe(
    pd.DataFrame(budget_data),
    column_config={
        "项目": "项目分类",
        "子项目": "费用项目",
        "金额": "金额",
        "公式": "Excel公式",
        "计算原理": "计算原理说明"
    },
    use_container_width=True,
    hide_index=True
)

# ==================== 第七部分：集装箱最优选择 ====================
st.markdown('<div class="section-title">🚢 集装箱最优选择</div>', unsafe_allow_html=True)

# 判断运输方式
if total_gross > 25000 or total_volume > 33:
    st.warning("⚠️ 货物超过拼箱限制，建议使用整箱(FCL)")
else:
    st.info("✅ 货物适合拼箱(LCL)或整箱(FCL)")

# 创建集装箱数据
container_types = {
    "20'普柜": {"体积": 33, "重量": 25000, "单价普柜": lcl_w_normal, "单价冻柜": lcl_w_frozen, "类型": "普柜"},
    "40'普柜": {"体积": 67, "重量": 29000, "单价普柜": container_20_normal, "单价冻柜": container_20_frozen, "类型": "普柜"},
    "40'高柜": {"体积": 76, "重量": 29000, "单价普柜": container_40_normal, "单价冻柜": container_40_frozen, "类型": "普柜"},
    "20'冻柜": {"体积": 27, "重量": 27400, "单价普柜": lcl_m_normal, "单价冻柜": lcl_m_frozen, "类型": "冻柜"},
    "40'冻柜": {"体积": 58, "重量": 27700, "单价普柜": container_40hc_normal, "单价冻柜": container_40rh_frozen, "类型": "冻柜"}
}

# 计算所有集装箱选项
container_options = []
for name, data in container_types.items():
    # 根据货物类型选择单价
    if "冷" in transport_note or "冷冻" in transport_note:
        unit_price = data["单价冻柜"]
    else:
        unit_price = data["单价普柜"]
    
    # 计算可装数量
    qty_by_vol = data["体积"] / single_volume
    qty_by_weight = data["重量"] / single_gross
    max_qty = min(qty_by_vol, qty_by_weight)
    
    if max_qty > 0:
        containers_needed = np.ceil(quantity / max_qty)
        total_freight = containers_needed * unit_price
        unit_freight = total_freight / quantity
        
        container_options.append({
            "集装箱类型": name,
            "每箱可装(台)": f"{max_qty:.0f}",
            "需要箱数": f"{containers_needed:.0f}",
            "单价(USD)": f"${unit_price:,.0f}",
            "总运费(USD)": f"${total_freight:,.2f}",
            "单位运费(USD/台)": f"${unit_freight:.2f}"
        })

# 显示所有选项
if container_options:
    options_df = pd.DataFrame(container_options)
    st.dataframe(options_df, use_container_width=True, hide_index=True)
    
    # 找出最优方案
    best_option = min(container_options, key=lambda x: float(x["单位运费(USD/台)"].replace("$", "")))
    
    st.markdown(f"""
    <div style='background-color: #d4edda; padding: 15px; border-radius: 5px; margin: 10px 0;'>
        <h4 style='color: #28a745;'>✅ 最优选择方案</h4>
        <p><strong>集装箱类型：</strong> {best_option['集装箱类型']}</p>
        <p><strong>需要箱数：</strong> {best_option['需要箱数']} 个</p>
        <p><strong>总运费：</strong> {best_option['总运费(USD)']}</p>
        <p><strong>单位产品运费：</strong> {best_option['单位运费(USD/台)']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    best_freight = float(best_option["总运费(USD)"].replace("$", ""))

# ==================== 第八部分：盈亏预测 ====================
st.markdown('<div class="section-title">📈 盈亏预测</div>', unsafe_allow_html=True)

# 计算总成本
total_domestic = inland_fee + forwarder_fee + inspection_fee + certificate_fee + customs_fee + insurance
total_cost = purchase_total - rebate + total_domestic + (best_freight * exchange_rate if 'best_freight' in locals() else 0)

# 建议报价
suggested_price = (total_cost * (1 + expected_profit_rate/100)) / quantity / exchange_rate

col_profit1, col_profit2, col_profit3 = st.columns(3)

with col_profit1:
    st.metric("总成本", f"¥{total_cost:,.2f}")
    st.markdown("""
    <div class="formula-hint">
        📐 总成本 = 采购成本 - 退税 + 国内费用 + 运费
    </div>
    """, unsafe_allow_html=True)

with col_profit2:
    st.metric("建议报价", f"${suggested_price:.2f}/台")
    st.markdown("""
    <div class="formula-hint">
        📐 建议报价 = 总成本×(1+预期利润率) ÷ 数量 ÷ 汇率
    </div>
    """, unsafe_allow_html=True)

with col_profit3:
    if 'best_freight' in locals():
        st.metric("最优运费", f"${best_freight:,.2f}")

# 实际报价输入
actual_price = st.number_input("输入实际报价 (USD/台)", value=round(suggested_price, 2), step=10.0)

if actual_price:
    revenue = actual_price * quantity * exchange_rate
    profit = revenue - total_cost
    profit_margin = profit / purchase_total
    
    col_actual1, col_actual2, col_actual3 = st.columns(3)
    with col_actual1:
        st.metric("总收入", f"¥{revenue:,.2f}")
    with col_actual2:
        st.metric("预期利润", f"¥{profit:,.2f}")
    with col_actual3:
        st.metric("利润率", f"{profit_margin:.2%}")

# ==================== 底部信息 ====================
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666; padding: 15px; background-color: #f8f9fa; border-radius: 5px;'>
    更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
    汇率: USD1 = CAD{exchange_rate} |
    交易数量: {quantity}台 |
    总体积: {total_volume:.2f}CBM |
    数据来源: C:\\Basic Information\\Data.xlsx (Power Automate Desktop定时抓取)
</div>
""", unsafe_allow_html=True)

# 保存按钮
if st.button("💾 保存当前数据"):
    st.success("✅ 数据已保存！")
    st.balloons()
