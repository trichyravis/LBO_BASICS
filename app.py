
"""
LBO Model - Leveraged Buyout Analysis Tool
The Mountain Path - World of Finance
Prof. V. Ravichandran
"""

import streamlit as st
import numpy as np
import pandas as pd

# ─────────────────────────────────────────────
# Page Config & Styling
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="LBO Model | The Mountain Path",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Mountain Path Design System
DARK_BLUE = "#003366"
MEDIUM_BLUE = "#004d80"
GOLD = "#FFD700"
LIGHT_BLUE = "#ADD8E6"
WHITE = "#FFFFFF"
LIGHT_BG = "#F0F4F8"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Sans+Pro:wght@300;400;600;700&display=swap');

    .stApp {{
        background: linear-gradient(180deg, {LIGHT_BG} 0%, {WHITE} 100%);
    }}

    .hero-header {{
        background: linear-gradient(135deg, {DARK_BLUE} 0%, {MEDIUM_BLUE} 60%, #006699 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0,51,102,0.3);
    }}
    .hero-header::before {{
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(255,215,0,0.15) 0%, transparent 70%);
        border-radius: 50%;
    }}
    .hero-title {{
        font-family: 'Playfair Display', serif;
        font-size: 2.4rem;
        font-weight: 900;
        color: {WHITE};
        margin: 0;
        letter-spacing: -0.5px;
    }}
    .hero-subtitle {{
        font-family: 'Source Sans Pro', sans-serif;
        font-size: 1.1rem;
        color: {GOLD};
        margin-top: 0.3rem;
        font-weight: 600;
    }}
    .hero-brand {{
        font-family: 'Source Sans Pro', sans-serif;
        font-size: 0.85rem;
        color: rgba(255,255,255,0.7);
        margin-top: 0.5rem;
    }}

    .metric-card {{
        background: {WHITE};
        border-radius: 12px;
        padding: 1.2rem;
        border-left: 4px solid {GOLD};
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        text-align: center;
    }}
    .metric-label {{
        font-family: 'Source Sans Pro', sans-serif;
        font-size: 0.8rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }}
    .metric-value {{
        font-family: 'Playfair Display', serif;
        font-size: 2rem;
        font-weight: 900;
        color: {DARK_BLUE};
        margin: 0.3rem 0;
    }}
    .metric-value.green {{ color: #2e7d32; }}
    .metric-value.red {{ color: #c62828; }}

    .section-header {{
        font-family: 'Playfair Display', serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: {DARK_BLUE};
        border-bottom: 3px solid {GOLD};
        padding-bottom: 0.5rem;
        margin: 1.5rem 0 1rem 0;
    }}

    .info-box {{
        background: linear-gradient(135deg, #E8F0FE 0%, #F0F4F8 100%);
        border-left: 4px solid {DARK_BLUE};
        padding: 1rem 1.2rem;
        border-radius: 0 8px 8px 0;
        font-family: 'Source Sans Pro', sans-serif;
        font-size: 0.9rem;
        color: #333;
        margin: 0.5rem 0;
    }}

    .footer {{
        text-align: center;
        padding: 1.5rem;
        margin-top: 2rem;
        border-top: 2px solid {GOLD};
        font-family: 'Source Sans Pro', sans-serif;
        color: #666;
        font-size: 0.85rem;
    }}

    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {DARK_BLUE} 0%, {MEDIUM_BLUE} 100%);
    }}
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {{
        color: {WHITE} !important;
    }}

    div[data-testid="stExpander"] {{
        background: {WHITE};
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Hero Header
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="hero-header">
    <div class="hero-title">📊 Leveraged Buyout (LBO) Model</div>
    <div class="hero-subtitle">Complete LBO Analysis with IRR, MOIC & Sensitivity Analysis</div>
    <div class="hero-brand">The Mountain Path – World of Finance | Prof. V. Ravichandran</div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Sidebar – All Input Assumptions
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏔️ LBO Assumptions")

    st.markdown("### 💼 Transaction Assumptions")
    enterprise_value = st.number_input("Enterprise Value ($M)", value=1000.0, step=50.0, format="%.1f")
    entry_multiple = st.number_input("Entry EV/EBITDA Multiple", value=8.0, step=0.5, format="%.1f")
    transaction_fees_pct = st.number_input("Transaction Fees (% of EV)", value=2.0, step=0.5, format="%.1f") / 100
    financing_fees_pct = st.number_input("Financing Fees (% of Debt)", value=1.5, step=0.5, format="%.1f") / 100
    holding_period = st.number_input("Holding Period (Years)", value=5, min_value=1, max_value=10, step=1)
    exit_multiple = st.number_input("Exit EV/EBITDA Multiple", value=8.0, step=0.5, format="%.1f")

    st.markdown("---")

    st.markdown("### 📈 Operating Assumptions")
    base_revenue = st.number_input("Base Year Revenue ($M)", value=500.0, step=25.0, format="%.1f")
    revenue_growth = st.number_input("Annual Revenue Growth (%)", value=5.0, step=0.5, format="%.1f") / 100
    base_ebitda_margin = st.number_input("Base EBITDA Margin (%)", value=25.0, step=1.0, format="%.1f") / 100
    ebitda_margin_improvement = st.number_input("Annual Margin Improvement (bps)", value=50.0, step=10.0, format="%.0f") / 10000
    capex_pct_revenue = st.number_input("CapEx (% of Revenue)", value=4.0, step=0.5, format="%.1f") / 100
    nwc_pct_revenue = st.number_input("∆ NWC (% of Revenue Change)", value=10.0, step=1.0, format="%.1f") / 100
    tax_rate = st.number_input("Tax Rate (%)", value=25.0, step=1.0, format="%.1f") / 100
    da_pct_revenue = st.number_input("D&A (% of Revenue)", value=3.0, step=0.5, format="%.1f") / 100

    st.markdown("---")

    st.markdown("### 🏦 Debt Assumptions")
    st.markdown("**Tranche 1: Senior Secured (Term Loan A)**")
    senior_a_pct = st.number_input("Senior A (% of EV)", value=30.0, step=5.0, format="%.1f", key="sa_pct") / 100
    senior_a_rate = st.number_input("Senior A Interest Rate (%)", value=5.0, step=0.25, format="%.2f", key="sa_rate") / 100
    senior_a_amort = st.number_input("Senior A Annual Amort. (%)", value=5.0, step=1.0, format="%.1f", key="sa_amort") / 100

    st.markdown("**Tranche 2: Senior Secured (Term Loan B)**")
    senior_b_pct = st.number_input("Senior B (% of EV)", value=20.0, step=5.0, format="%.1f", key="sb_pct") / 100
    senior_b_rate = st.number_input("Senior B Interest Rate (%)", value=7.0, step=0.25, format="%.2f", key="sb_rate") / 100
    senior_b_amort = st.number_input("Senior B Annual Amort. (%)", value=1.0, step=0.5, format="%.1f", key="sb_amort") / 100

    st.markdown("**Tranche 3: Subordinated / Mezzanine**")
    mezz_pct = st.number_input("Mezzanine (% of EV)", value=10.0, step=5.0, format="%.1f", key="mz_pct") / 100
    mezz_rate = st.number_input("Mezzanine Interest Rate (%)", value=10.0, step=0.5, format="%.2f", key="mz_rate") / 100
    mezz_amort = 0.0

    cash_sweep_pct = st.number_input("Cash Sweep (% of Excess FCF)", value=50.0, step=10.0, format="%.1f") / 100

    st.markdown("---")
    st.markdown("**Sensitivity Ranges**")
    sens_exit_low = st.number_input("Exit Multiple Low", value=6.0, step=0.5, format="%.1f")
    sens_exit_high = st.number_input("Exit Multiple High", value=10.0, step=0.5, format="%.1f")
    sens_growth_low = st.number_input("Revenue Growth Low (%)", value=2.0, step=0.5, format="%.1f") / 100
    sens_growth_high = st.number_input("Revenue Growth High (%)", value=8.0, step=0.5, format="%.1f") / 100


# ─────────────────────────────────────────────
# LBO Engine
# ─────────────────────────────────────────────
def _calculate_irr(cashflows, tol=1e-8, max_iter=1000):
    """Newton-Raphson IRR solver."""
    rate = 0.15
    for _ in range(max_iter):
        npv = sum(cf / (1 + rate) ** t for t, cf in enumerate(cashflows))
        dnpv = sum(-t * cf / (1 + rate) ** (t + 1) for t, cf in enumerate(cashflows))
        if abs(dnpv) < 1e-14:
            break
        new_rate = rate - npv / dnpv
        if abs(new_rate - rate) < tol:
            return new_rate
        rate = new_rate
    return rate


def run_lbo_model(
    enterprise_value, entry_multiple, transaction_fees_pct, financing_fees_pct,
    holding_period, exit_multiple, base_revenue, revenue_growth, base_ebitda_margin,
    ebitda_margin_improvement, capex_pct_revenue, nwc_pct_revenue, tax_rate,
    da_pct_revenue, senior_a_pct, senior_a_rate, senior_a_amort,
    senior_b_pct, senior_b_rate, senior_b_amort,
    mezz_pct, mezz_rate, mezz_amort, cash_sweep_pct
):
    """Core LBO model engine."""

    # --- Sources & Uses ---
    total_debt_pct = senior_a_pct + senior_b_pct + mezz_pct
    total_debt = enterprise_value * total_debt_pct
    transaction_fees = enterprise_value * transaction_fees_pct
    financing_fees = total_debt * financing_fees_pct
    total_uses = enterprise_value + transaction_fees + financing_fees
    total_equity = total_uses - total_debt

    senior_a_amount = enterprise_value * senior_a_pct
    senior_b_amount = enterprise_value * senior_b_pct
    mezz_amount = enterprise_value * mezz_pct
    implied_ebitda = enterprise_value / entry_multiple if entry_multiple > 0 else 0

    sources_uses = {
        "Sources": {
            "Senior Secured A (TLA)": senior_a_amount,
            "Senior Secured B (TLB)": senior_b_amount,
            "Mezzanine / Sub Debt": mezz_amount,
            "Sponsor Equity": total_equity,
            "Total Sources": total_uses,
        },
        "Uses": {
            "Enterprise Value": enterprise_value,
            "Transaction Fees": transaction_fees,
            "Financing Fees": financing_fees,
            "Total Uses": total_uses,
        }
    }

    # --- Operating Projections ---
    years = list(range(0, holding_period + 1))
    revenue, ebitda, ebitda_margin, da, ebit = [], [], [], [], []
    taxes, capex, delta_nwc, fcf_before_debt = [0], [0], [0], [0]

    for yr in years:
        rev = base_revenue if yr == 0 else revenue[-1] * (1 + revenue_growth)
        revenue.append(rev)
        margin = base_ebitda_margin + ebitda_margin_improvement * yr
        ebitda_margin.append(margin)
        ebitda.append(rev * margin)
        da.append(rev * da_pct_revenue)
        ebit.append(ebitda[-1] - da[-1])

    # --- Debt Schedule ---
    sa_balance, sb_balance, mz_balance = [senior_a_amount], [senior_b_amount], [mezz_amount]
    total_debt_bal = [total_debt]
    interest_sa, interest_sb, interest_mz, total_interest = [0], [0], [0], [0]
    mandatory_repay, optional_repay, total_repay, levered_fcf = [0], [0], [0], [0]

    for yr in range(1, holding_period + 1):
        int_sa = sa_balance[yr - 1] * senior_a_rate
        int_sb = sb_balance[yr - 1] * senior_b_rate
        int_mz = mz_balance[yr - 1] * mezz_rate
        tot_int = int_sa + int_sb + int_mz

        interest_sa.append(int_sa)
        interest_sb.append(int_sb)
        interest_mz.append(int_mz)
        total_interest.append(tot_int)

        taxable_income = ebit[yr] - tot_int
        tax_val = max(0, taxable_income * tax_rate)
        taxes.append(tax_val)

        capex_val = revenue[yr] * capex_pct_revenue
        capex.append(capex_val)
        dnwc = (revenue[yr] - revenue[yr - 1]) * nwc_pct_revenue
        delta_nwc.append(dnwc)

        fcf_bd = ebitda[yr] - tot_int - tax_val - capex_val - dnwc
        fcf_before_debt.append(fcf_bd)

        mand_sa = min(sa_balance[yr - 1], senior_a_amount * senior_a_amort)
        mand_sb = min(sb_balance[yr - 1], senior_b_amount * senior_b_amort)
        mand_total = mand_sa + mand_sb
        mandatory_repay.append(mand_total)

        cash_after_mand = fcf_bd - mand_total
        opt_repay = max(0, cash_after_mand * cash_sweep_pct) if cash_after_mand > 0 else 0

        remaining_opt = opt_repay
        sa_opt = min(remaining_opt, sa_balance[yr - 1] - mand_sa)
        remaining_opt -= sa_opt
        sb_opt = min(remaining_opt, sb_balance[yr - 1] - mand_sb)
        remaining_opt -= sb_opt
        mz_opt = min(remaining_opt, mz_balance[yr - 1])

        optional_repay.append(sa_opt + sb_opt + mz_opt)
        total_repay.append(mand_total + sa_opt + sb_opt + mz_opt)

        new_sa = max(0, sa_balance[yr - 1] - mand_sa - sa_opt)
        new_sb = max(0, sb_balance[yr - 1] - mand_sb - sb_opt)
        new_mz = max(0, mz_balance[yr - 1] - mz_opt)
        sa_balance.append(new_sa)
        sb_balance.append(new_sb)
        mz_balance.append(new_mz)
        total_debt_bal.append(new_sa + new_sb + new_mz)

        levered_fcf.append(fcf_bd - total_repay[-1])

    # --- Exit & Returns ---
    exit_ebitda = ebitda[holding_period]
    exit_ev = exit_ebitda * exit_multiple
    net_debt_at_exit = total_debt_bal[holding_period]
    equity_at_exit = exit_ev - net_debt_at_exit
    moic = equity_at_exit / total_equity if total_equity > 0 else 0

    irr_cashflows = [-total_equity] + [0] * (holding_period - 1) + [equity_at_exit]
    irr = _calculate_irr(irr_cashflows)

    leverage_ratios = [total_debt_bal[i] / ebitda[i] if ebitda[i] > 0 else 0 for i in range(holding_period + 1)]

    return {
        "sources_uses": sources_uses,
        "total_equity": total_equity, "total_debt": total_debt,
        "implied_ebitda": implied_ebitda, "years": years,
        "revenue": revenue, "ebitda": ebitda, "ebitda_margin": ebitda_margin,
        "da": da, "ebit": ebit, "taxes": taxes, "capex": capex,
        "delta_nwc": delta_nwc, "total_interest": total_interest,
        "fcf_before_debt": fcf_before_debt,
        "mandatory_repay": mandatory_repay, "optional_repay": optional_repay,
        "total_repay": total_repay, "levered_fcf": levered_fcf,
        "sa_balance": sa_balance, "sb_balance": sb_balance,
        "mz_balance": mz_balance, "total_debt_bal": total_debt_bal,
        "leverage_ratios": leverage_ratios,
        "exit_ebitda": exit_ebitda, "exit_ev": exit_ev,
        "net_debt_at_exit": net_debt_at_exit, "equity_at_exit": equity_at_exit,
        "moic": moic, "irr": irr, "holding_period": holding_period,
    }


# ─────────────────────────────────────────────
# Run the Model
# ─────────────────────────────────────────────
results = run_lbo_model(
    enterprise_value, entry_multiple, transaction_fees_pct, financing_fees_pct,
    holding_period, exit_multiple, base_revenue, revenue_growth, base_ebitda_margin,
    ebitda_margin_improvement, capex_pct_revenue, nwc_pct_revenue, tax_rate,
    da_pct_revenue, senior_a_pct, senior_a_rate, senior_a_amort,
    senior_b_pct, senior_b_rate, senior_b_amort,
    mezz_pct, mezz_rate, mezz_amort, cash_sweep_pct
)

# ─────────────────────────────────────────────
# Key Metrics Dashboard
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">🎯 Key Return Metrics</div>', unsafe_allow_html=True)

irr_val = results["irr"]
moic_val = results["moic"]
irr_color = "green" if irr_val >= 0.20 else ("" if irr_val >= 0.15 else "red")
moic_color = "green" if moic_val >= 2.5 else ("" if moic_val >= 2.0 else "red")

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">IRR</div>
        <div class="metric-value {irr_color}">{irr_val*100:.1f}%</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">MOIC</div>
        <div class="metric-value {moic_color}">{moic_val:.2f}x</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Equity Invested</div>
        <div class="metric-value">${results['total_equity']:.0f}M</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Equity at Exit</div>
        <div class="metric-value">${results['equity_at_exit']:.0f}M</div>
    </div>""", unsafe_allow_html=True)
with c5:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Exit Leverage</div>
        <div class="metric-value">{results['leverage_ratios'][-1]:.1f}x</div>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Sources & Uses
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">📋 Sources & Uses of Funds</div>', unsafe_allow_html=True)

col_s, col_u = st.columns(2)
with col_s:
    st.markdown("**Sources**")
    s_data = results["sources_uses"]["Sources"]
    df_s = pd.DataFrame({"Item": list(s_data.keys()), "Amount ($M)": [f"${v:,.1f}" for v in s_data.values()]})
    st.dataframe(df_s, hide_index=True, use_container_width=True)

with col_u:
    st.markdown("**Uses**")
    u_data = results["sources_uses"]["Uses"]
    df_u = pd.DataFrame({"Item": list(u_data.keys()), "Amount ($M)": [f"${v:,.1f}" for v in u_data.values()]})
    st.dataframe(df_u, hide_index=True, use_container_width=True)

implied_ebitda = results["implied_ebitda"]
st.markdown(f"""<div class="info-box">
    <strong>Implied Entry EBITDA:</strong> ${implied_ebitda:,.1f}M &nbsp;|&nbsp;
    <strong>Total Leverage:</strong> {(results['total_debt']/implied_ebitda):.1f}x EBITDA &nbsp;|&nbsp;
    <strong>Equity Check:</strong> {(results['total_equity']/enterprise_value*100):.1f}% of EV
</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Operating Projections
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">📈 Operating Model Projections</div>', unsafe_allow_html=True)

op_data = {
    "Year": [f"Year {y}" for y in results["years"]],
    "Revenue ($M)": [f"${v:,.1f}" for v in results["revenue"]],
    "EBITDA ($M)": [f"${v:,.1f}" for v in results["ebitda"]],
    "Margin (%)": [f"{v*100:.1f}%" for v in results["ebitda_margin"]],
    "D&A ($M)": [f"${v:,.1f}" for v in results["da"]],
    "CapEx ($M)": [f"${v:,.1f}" for v in results["capex"]],
    "∆ NWC ($M)": [f"${v:,.1f}" for v in results["delta_nwc"]],
    "Interest ($M)": [f"${v:,.1f}" for v in results["total_interest"]],
    "Taxes ($M)": [f"${v:,.1f}" for v in results["taxes"]],
}
st.dataframe(pd.DataFrame(op_data), hide_index=True, use_container_width=True)

# Revenue & EBITDA Chart
chart_df = pd.DataFrame({
    "Year": [f"Yr {y}" for y in results["years"]],
    "Revenue": results["revenue"],
    "EBITDA": results["ebitda"],
}).set_index("Year")
st.bar_chart(chart_df, color=[LIGHT_BLUE, DARK_BLUE])

# Margin trend
margin_df = pd.DataFrame({
    "Year": [f"Yr {y}" for y in results["years"]],
    "EBITDA Margin (%)": [m * 100 for m in results["ebitda_margin"]],
}).set_index("Year")
st.line_chart(margin_df, color=[GOLD])


# ─────────────────────────────────────────────
# Debt Schedule
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">🏦 Debt Schedule & Deleveraging</div>', unsafe_allow_html=True)

debt_data = {
    "Year": [f"Year {y}" for y in results["years"]],
    "Senior A ($M)": [f"${v:,.1f}" for v in results["sa_balance"]],
    "Senior B ($M)": [f"${v:,.1f}" for v in results["sb_balance"]],
    "Mezz ($M)": [f"${v:,.1f}" for v in results["mz_balance"]],
    "Total Debt ($M)": [f"${v:,.1f}" for v in results["total_debt_bal"]],
    "Leverage (x)": [f"{v:.2f}x" for v in results["leverage_ratios"]],
    "Mand. Repay ($M)": [f"${v:,.1f}" for v in results["mandatory_repay"]],
    "Opt. Repay ($M)": [f"${v:,.1f}" for v in results["optional_repay"]],
}
st.dataframe(pd.DataFrame(debt_data), hide_index=True, use_container_width=True)

# Debt balance chart
debt_chart_df = pd.DataFrame({
    "Year": [f"Yr {y}" for y in results["years"]],
    "Senior A": results["sa_balance"],
    "Senior B": results["sb_balance"],
    "Mezzanine": results["mz_balance"],
}).set_index("Year")
st.bar_chart(debt_chart_df, color=[DARK_BLUE, MEDIUM_BLUE, GOLD])

# Leverage ratio trend
lev_df = pd.DataFrame({
    "Year": [f"Yr {y}" for y in results["years"]],
    "Leverage Ratio (x)": results["leverage_ratios"],
}).set_index("Year")
st.line_chart(lev_df, color=["#c62828"])


# ─────────────────────────────────────────────
# Exit & Returns
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">🚀 Exit & Returns Analysis</div>', unsafe_allow_html=True)

ec1, ec2 = st.columns(2)
with ec1:
    exit_data = {
        "Metric": [
            "Exit Year EBITDA", "Exit Multiple", "Exit Enterprise Value",
            "Less: Net Debt at Exit", "Equity Value at Exit",
            "Sponsor Equity Invested", "MOIC", "IRR"
        ],
        "Value": [
            f"${results['exit_ebitda']:,.1f}M", f"{exit_multiple:.1f}x",
            f"${results['exit_ev']:,.1f}M", f"${results['net_debt_at_exit']:,.1f}M",
            f"${results['equity_at_exit']:,.1f}M", f"${results['total_equity']:,.1f}M",
            f"{results['moic']:.2f}x", f"{results['irr']*100:.1f}%"
        ]
    }
    st.dataframe(pd.DataFrame(exit_data), hide_index=True, use_container_width=True)

with ec2:
    # Returns attribution
    entry_equity = results['total_equity']
    ebitda_growth_value = (results['exit_ebitda'] - implied_ebitda) * exit_multiple
    multiple_expansion = (exit_multiple - entry_multiple) * results['exit_ebitda']
    debt_paydown_value = results['total_debt'] - results['net_debt_at_exit']

    attrib_df = pd.DataFrame({
        "Component": ["EBITDA Growth", "Multiple Expansion", "Debt Paydown"],
        "Value ($M)": [ebitda_growth_value, multiple_expansion, debt_paydown_value]
    }).set_index("Component")
    st.markdown("**Returns Attribution Bridge**")
    st.bar_chart(attrib_df, color=[DARK_BLUE])

    st.markdown(f"""<div class="info-box">
        <strong>Entry Equity:</strong> ${entry_equity:,.0f}M →
        <strong>Exit Equity:</strong> ${results['equity_at_exit']:,.0f}M<br>
        <strong>Value Created:</strong> ${results['equity_at_exit'] - entry_equity:,.0f}M
        ({(results['equity_at_exit']/entry_equity - 1)*100:.0f}% return)
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Sensitivity Analysis
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">🔬 Sensitivity Analysis</div>', unsafe_allow_html=True)

st.markdown("""<div class="info-box">
    Two-way sensitivity tables: <strong>IRR</strong> and <strong>MOIC</strong> across
    <strong>Exit Multiples</strong> (columns) × <strong>Revenue Growth</strong> (rows).
</div>""", unsafe_allow_html=True)

exit_range = np.linspace(sens_exit_low, sens_exit_high, 5)
growth_range = np.linspace(sens_growth_low, sens_growth_high, 5)

irr_matrix = np.zeros((len(growth_range), len(exit_range)))
moic_matrix = np.zeros((len(growth_range), len(exit_range)))

for i, g in enumerate(growth_range):
    for j, ex in enumerate(exit_range):
        res = run_lbo_model(
            enterprise_value, entry_multiple, transaction_fees_pct, financing_fees_pct,
            holding_period, ex, base_revenue, g, base_ebitda_margin,
            ebitda_margin_improvement, capex_pct_revenue, nwc_pct_revenue, tax_rate,
            da_pct_revenue, senior_a_pct, senior_a_rate, senior_a_amort,
            senior_b_pct, senior_b_rate, senior_b_amort,
            mezz_pct, mezz_rate, mezz_amort, cash_sweep_pct
        )
        irr_matrix[i, j] = res["irr"] * 100
        moic_matrix[i, j] = res["moic"]


def style_irr(val):
    try:
        v = float(str(val).replace('%', ''))
        if v >= 25: return 'background-color: #a5d6a7; font-weight: bold; color: #1b5e20'
        elif v >= 20: return 'background-color: #c8e6c9; color: #2e7d32'
        elif v >= 15: return 'background-color: #fff9c4; color: #f57f17'
        elif v >= 10: return 'background-color: #ffcc80; color: #e65100'
        else: return 'background-color: #ef9a9a; font-weight: bold; color: #b71c1c'
    except: return ''


def style_moic(val):
    try:
        v = float(str(val).replace('x', ''))
        if v >= 3.0: return 'background-color: #a5d6a7; font-weight: bold; color: #1b5e20'
        elif v >= 2.5: return 'background-color: #c8e6c9; color: #2e7d32'
        elif v >= 2.0: return 'background-color: #fff9c4; color: #f57f17'
        elif v >= 1.5: return 'background-color: #ffcc80; color: #e65100'
        else: return 'background-color: #ef9a9a; font-weight: bold; color: #b71c1c'
    except: return ''


s1, s2 = st.columns(2)

with s1:
    st.markdown("**IRR Sensitivity Table (%)**")
    df_irr = pd.DataFrame(
        irr_matrix,
        index=[f"Growth {g*100:.1f}%" for g in growth_range],
        columns=[f"Exit {ex:.1f}x" for ex in exit_range]
    ).round(1)
    styled_irr = df_irr.style.format("{:.1f}%").map(style_irr)
    st.dataframe(styled_irr, use_container_width=True)

with s2:
    st.markdown("**MOIC Sensitivity Table**")
    df_moic = pd.DataFrame(
        moic_matrix,
        index=[f"Growth {g*100:.1f}%" for g in growth_range],
        columns=[f"Exit {ex:.1f}x" for ex in exit_range]
    ).round(2)
    styled_moic = df_moic.style.format("{:.2f}x").map(style_moic)
    st.dataframe(styled_moic, use_container_width=True)


# ─────────────────────────────────────────────
# Additional: Leverage Sensitivity
# ─────────────────────────────────────────────
with st.expander("📊 Additional: IRR vs Leverage Sensitivity"):
    st.markdown("Impact of capital structure (total debt as % of EV) on sponsor IRR:")
    leverage_pcts = np.arange(0.40, 0.85, 0.05)
    irr_by_leverage = []
    total_base = senior_a_pct + senior_b_pct + mezz_pct
    for lev in leverage_pcts:
        if total_base > 0:
            ra, rb, rm = senior_a_pct/total_base, senior_b_pct/total_base, mezz_pct/total_base
        else:
            ra, rb, rm = 0.5, 0.33, 0.17
        res = run_lbo_model(
            enterprise_value, entry_multiple, transaction_fees_pct, financing_fees_pct,
            holding_period, exit_multiple, base_revenue, revenue_growth, base_ebitda_margin,
            ebitda_margin_improvement, capex_pct_revenue, nwc_pct_revenue, tax_rate,
            da_pct_revenue, lev*ra, senior_a_rate, senior_a_amort,
            lev*rb, senior_b_rate, senior_b_amort,
            lev*rm, mezz_rate, mezz_amort, cash_sweep_pct
        )
        irr_by_leverage.append(res["irr"] * 100)

    lev_chart_df = pd.DataFrame({
        "Debt / EV": [f"{l*100:.0f}%" for l in leverage_pcts],
        "IRR (%)": irr_by_leverage,
    }).set_index("Debt / EV")
    st.line_chart(lev_chart_df, color=[DARK_BLUE])

    lev_table = pd.DataFrame({
        "Debt / EV": [f"{l*100:.0f}%" for l in leverage_pcts],
        "Sponsor IRR": [f"{v:.1f}%" for v in irr_by_leverage],
    })
    st.dataframe(lev_table, hide_index=True, use_container_width=True)


# ─────────────────────────────────────────────
# Additional: Holding Period Sensitivity
# ─────────────────────────────────────────────
with st.expander("📊 Additional: IRR & MOIC vs Holding Period"):
    hold_years = list(range(3, 9))
    hold_irrs, hold_moics = [], []
    for hp in hold_years:
        res = run_lbo_model(
            enterprise_value, entry_multiple, transaction_fees_pct, financing_fees_pct,
            hp, exit_multiple, base_revenue, revenue_growth, base_ebitda_margin,
            ebitda_margin_improvement, capex_pct_revenue, nwc_pct_revenue, tax_rate,
            da_pct_revenue, senior_a_pct, senior_a_rate, senior_a_amort,
            senior_b_pct, senior_b_rate, senior_b_amort,
            mezz_pct, mezz_rate, mezz_amort, cash_sweep_pct
        )
        hold_irrs.append(res["irr"] * 100)
        hold_moics.append(res["moic"])

    hp_df = pd.DataFrame({
        "Holding Period": [f"{y} Years" for y in hold_years],
        "IRR (%)": [f"{v:.1f}%" for v in hold_irrs],
        "MOIC": [f"{v:.2f}x" for v in hold_moics],
    })
    st.dataframe(hp_df, hide_index=True, use_container_width=True)

    hp_chart = pd.DataFrame({
        "Year": [f"{y}yr" for y in hold_years],
        "IRR (%)": hold_irrs,
    }).set_index("Year")
    st.bar_chart(hp_chart, color=[DARK_BLUE])


# ─────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
    <strong>The Mountain Path – World of Finance</strong><br>
    Prof. V. Ravichandran | 28+ Years Corporate Finance & Banking Experience | 10+ Years Academic Excellence<br>
    <em>LBO Model v1.0 – For Educational Purposes</em>
</div>
""", unsafe_allow_html=True)
