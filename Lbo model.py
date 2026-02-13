
"""
LBO Model - Leveraged Buyout Analysis Tool
The Mountain Path - World of Finance
Prof. V. Ravichandran
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

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

    /* Sidebar styling */
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

    # --- Transaction Assumptions ---
    st.markdown("### 💼 Transaction Assumptions")
    enterprise_value = st.number_input("Enterprise Value ($M)", value=1000.0, step=50.0, format="%.1f")
    entry_multiple = st.number_input("Entry EV/EBITDA Multiple", value=8.0, step=0.5, format="%.1f")
    transaction_fees_pct = st.number_input("Transaction Fees (% of EV)", value=2.0, step=0.5, format="%.1f") / 100
    financing_fees_pct = st.number_input("Financing Fees (% of Debt)", value=1.5, step=0.5, format="%.1f") / 100
    holding_period = st.number_input("Holding Period (Years)", value=5, min_value=1, max_value=10, step=1)
    exit_multiple = st.number_input("Exit EV/EBITDA Multiple", value=8.0, step=0.5, format="%.1f")

    st.markdown("---")

    # --- Operating Assumptions ---
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

    # --- Debt Assumptions ---
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
    mezz_amort = 0.0  # Bullet repayment

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
def run_lbo_model(
    enterprise_value, entry_multiple, transaction_fees_pct, financing_fees_pct,
    holding_period, exit_multiple, base_revenue, revenue_growth, base_ebitda_margin,
    ebitda_margin_improvement, capex_pct_revenue, nwc_pct_revenue, tax_rate,
    da_pct_revenue, senior_a_pct, senior_a_rate, senior_a_amort,
    senior_b_pct, senior_b_rate, senior_b_amort,
    mezz_pct, mezz_rate, mezz_amort, cash_sweep_pct
):
    """Core LBO model engine returning all projection data."""

    # --- Sources & Uses ---
    total_debt_pct = senior_a_pct + senior_b_pct + mezz_pct
    equity_pct = 1.0 - total_debt_pct

    total_debt = enterprise_value * total_debt_pct
    equity_contribution = enterprise_value * equity_pct
    transaction_fees = enterprise_value * transaction_fees_pct
    financing_fees = total_debt * financing_fees_pct

    total_uses = enterprise_value + transaction_fees + financing_fees
    total_equity = total_uses - total_debt  # Equity covers EV shortfall + fees

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
    revenue = []
    ebitda = []
    ebitda_margin = []
    da = []
    ebit = []
    taxes = []
    nopat = []
    capex = []
    delta_nwc = []
    fcf_before_debt = []

    for yr in years:
        if yr == 0:
            rev = base_revenue
        else:
            rev = revenue[-1] * (1 + revenue_growth)
        revenue.append(rev)

        margin = base_ebitda_margin + ebitda_margin_improvement * yr
        ebitda_margin.append(margin)
        ebitda_val = rev * margin
        ebitda.append(ebitda_val)

        da_val = rev * da_pct_revenue
        da.append(da_val)

        ebit_val = ebitda_val - da_val
        ebit.append(ebit_val)

    # Debt schedule
    sa_balance = [senior_a_amount]
    sb_balance = [senior_b_amount]
    mz_balance = [mezz_amount]
    total_debt_bal = [total_debt]

    interest_sa = [0]
    interest_sb = [0]
    interest_mz = [0]
    total_interest = [0]

    mandatory_repay = [0]
    optional_repay = [0]
    total_repay = [0]
    fcf_after_debt = [0]
    levered_fcf = [0]

    for yr in range(1, holding_period + 1):
        # Interest on beginning balance
        int_sa = sa_balance[yr - 1] * senior_a_rate
        int_sb = sb_balance[yr - 1] * senior_b_rate
        int_mz = mz_balance[yr - 1] * mezz_rate
        tot_int = int_sa + int_sb + int_mz

        interest_sa.append(int_sa)
        interest_sb.append(int_sb)
        interest_mz.append(int_mz)
        total_interest.append(tot_int)

        # Tax calculation (interest is tax-deductible)
        taxable_income = ebit[yr] - tot_int
        tax_val = max(0, taxable_income * tax_rate)
        taxes.append(tax_val)
        net_income = taxable_income - tax_val

        # Free cash flow before debt service
        capex_val = revenue[yr] * capex_pct_revenue
        capex.append(capex_val)
        dnwc = (revenue[yr] - revenue[yr - 1]) * nwc_pct_revenue
        delta_nwc.append(dnwc)

        fcf_bd = ebitda[yr] - tot_int - tax_val - capex_val - dnwc
        fcf_before_debt.append(fcf_bd)

        # Mandatory amortization
        mand_sa = min(sa_balance[yr - 1], senior_a_amount * senior_a_amort)
        mand_sb = min(sb_balance[yr - 1], senior_b_amount * senior_b_amort)
        mand_mz = 0
        mand_total = mand_sa + mand_sb + mand_mz
        mandatory_repay.append(mand_total)

        # Cash available for optional repayment (cash sweep)
        cash_after_mand = fcf_bd - mand_total
        opt_repay = max(0, cash_after_mand * cash_sweep_pct) if cash_after_mand > 0 else 0

        # Apply optional repayment waterfall: Senior A → Senior B → Mezz
        remaining_opt = opt_repay
        sa_opt = min(remaining_opt, sa_balance[yr - 1] - mand_sa)
        remaining_opt -= sa_opt
        sb_opt = min(remaining_opt, sb_balance[yr - 1] - mand_sb)
        remaining_opt -= sb_opt
        mz_opt = min(remaining_opt, mz_balance[yr - 1])

        optional_repay.append(sa_opt + sb_opt + mz_opt)
        total_repay.append(mand_total + sa_opt + sb_opt + mz_opt)

        # Update balances
        new_sa = sa_balance[yr - 1] - mand_sa - sa_opt
        new_sb = sb_balance[yr - 1] - mand_sb - sb_opt
        new_mz = mz_balance[yr - 1] - mand_mz - mz_opt
        sa_balance.append(max(0, new_sa))
        sb_balance.append(max(0, new_sb))
        mz_balance.append(max(0, new_mz))
        total_debt_bal.append(max(0, new_sa + new_sb + new_mz))

        lev_fcf = fcf_bd - total_repay[-1]
        levered_fcf.append(lev_fcf)

    # Pad Year 0 for operating items
    taxes.insert(0, 0)
    capex.insert(0, 0)
    delta_nwc.insert(0, 0)
    fcf_before_debt.insert(0, 0)

    # --- Exit & Returns ---
    exit_ebitda = ebitda[holding_period]
    exit_ev = exit_ebitda * exit_multiple
    net_debt_at_exit = total_debt_bal[holding_period]
    equity_at_exit = exit_ev - net_debt_at_exit

    moic = equity_at_exit / total_equity if total_equity > 0 else 0

    # IRR calculation
    irr_cashflows = [-total_equity] + [0] * (holding_period - 1) + [equity_at_exit]
    try:
        irr = np.irr(irr_cashflows) if hasattr(np, 'irr') else np.nan
    except:
        irr = np.nan

    # Manual IRR via Newton's method if np.irr unavailable
    if np.isnan(irr):
        irr = _calculate_irr(irr_cashflows)

    # Credit metrics
    leverage_ratios = [total_debt_bal[i] / ebitda[i] if ebitda[i] > 0 else 0 for i in range(holding_period + 1)]
    interest_coverage = [ebitda[i] / total_interest[i] if total_interest[i] > 0 else float('inf') for i in range(holding_period + 1)]

    return {
        "sources_uses": sources_uses,
        "total_equity": total_equity,
        "total_debt": total_debt,
        "implied_ebitda": implied_ebitda,
        "years": years,
        "revenue": revenue,
        "ebitda": ebitda,
        "ebitda_margin": ebitda_margin,
        "da": da,
        "ebit": ebit,
        "taxes": taxes,
        "capex": capex,
        "delta_nwc": delta_nwc,
        "total_interest": total_interest,
        "fcf_before_debt": fcf_before_debt,
        "mandatory_repay": mandatory_repay,
        "optional_repay": optional_repay,
        "total_repay": total_repay,
        "levered_fcf": levered_fcf,
        "sa_balance": sa_balance,
        "sb_balance": sb_balance,
        "mz_balance": mz_balance,
        "total_debt_bal": total_debt_bal,
        "leverage_ratios": leverage_ratios,
        "interest_coverage": interest_coverage,
        "exit_ebitda": exit_ebitda,
        "exit_ev": exit_ev,
        "net_debt_at_exit": net_debt_at_exit,
        "equity_at_exit": equity_at_exit,
        "moic": moic,
        "irr": irr,
        "irr_cashflows": irr_cashflows,
        "holding_period": holding_period,
    }


def _calculate_irr(cashflows, tol=1e-8, max_iter=1000):
    """Newton-Raphson IRR solver."""
    rate = 0.15  # initial guess
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
# Sources & Uses Table
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">📋 Sources & Uses of Funds</div>', unsafe_allow_html=True)

col_s, col_u = st.columns(2)
with col_s:
    st.markdown("**Sources**")
    s_data = results["sources_uses"]["Sources"]
    df_s = pd.DataFrame({"Item": s_data.keys(), "Amount ($M)": [f"${v:,.1f}" for v in s_data.values()]})
    st.dataframe(df_s, hide_index=True, use_container_width=True)

with col_u:
    st.markdown("**Uses**")
    u_data = results["sources_uses"]["Uses"]
    df_u = pd.DataFrame({"Item": u_data.keys(), "Amount ($M)": [f"${v:,.1f}" for v in u_data.values()]})
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
    "Revenue": [f"${v:,.1f}" for v in results["revenue"]],
    "EBITDA": [f"${v:,.1f}" for v in results["ebitda"]],
    "Margin": [f"{v*100:.1f}%" for v in results["ebitda_margin"]],
    "D&A": [f"${v:,.1f}" for v in results["da"]],
    "CapEx": [f"${v:,.1f}" for v in results["capex"]],
    "∆ NWC": [f"${v:,.1f}" for v in results["delta_nwc"]],
    "Interest": [f"${v:,.1f}" for v in results["total_interest"]],
    "Taxes": [f"${v:,.1f}" for v in results["taxes"]],
}
df_op = pd.DataFrame(op_data)
st.dataframe(df_op, hide_index=True, use_container_width=True)

# Revenue & EBITDA Chart
fig_op = make_subplots(specs=[[{"secondary_y": True}]])
fig_op.add_trace(
    go.Bar(x=[f"Yr {y}" for y in results["years"]], y=results["revenue"],
           name="Revenue", marker_color=LIGHT_BLUE, opacity=0.8),
    secondary_y=False
)
fig_op.add_trace(
    go.Bar(x=[f"Yr {y}" for y in results["years"]], y=results["ebitda"],
           name="EBITDA", marker_color=DARK_BLUE, opacity=0.9),
    secondary_y=False
)
fig_op.add_trace(
    go.Scatter(x=[f"Yr {y}" for y in results["years"]],
               y=[m * 100 for m in results["ebitda_margin"]],
               name="EBITDA Margin %", line=dict(color=GOLD, width=3), mode="lines+markers"),
    secondary_y=True
)
fig_op.update_layout(
    title="Revenue, EBITDA & Margin Progression",
    template="plotly_white", height=400,
    font=dict(family="Source Sans Pro"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    barmode="group"
)
fig_op.update_yaxes(title_text="$M", secondary_y=False)
fig_op.update_yaxes(title_text="Margin %", secondary_y=True)
st.plotly_chart(fig_op, use_container_width=True)


# ─────────────────────────────────────────────
# Debt Schedule
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">🏦 Debt Schedule & Deleveraging</div>', unsafe_allow_html=True)

debt_data = {
    "Year": [f"Year {y}" for y in results["years"]],
    "Senior A Bal": [f"${v:,.1f}" for v in results["sa_balance"]],
    "Senior B Bal": [f"${v:,.1f}" for v in results["sb_balance"]],
    "Mezz Bal": [f"${v:,.1f}" for v in results["mz_balance"]],
    "Total Debt": [f"${v:,.1f}" for v in results["total_debt_bal"]],
    "Leverage (x)": [f"{v:.2f}x" for v in results["leverage_ratios"]],
    "Mand. Repay": [f"${v:,.1f}" for v in results["mandatory_repay"]],
    "Optional Repay": [f"${v:,.1f}" for v in results["optional_repay"]],
}
df_debt = pd.DataFrame(debt_data)
st.dataframe(df_debt, hide_index=True, use_container_width=True)

# Debt waterfall chart
fig_debt = go.Figure()
fig_debt.add_trace(go.Bar(
    x=[f"Yr {y}" for y in results["years"]], y=results["sa_balance"],
    name="Senior A", marker_color=DARK_BLUE
))
fig_debt.add_trace(go.Bar(
    x=[f"Yr {y}" for y in results["years"]], y=results["sb_balance"],
    name="Senior B", marker_color=MEDIUM_BLUE
))
fig_debt.add_trace(go.Bar(
    x=[f"Yr {y}" for y in results["years"]], y=results["mz_balance"],
    name="Mezzanine", marker_color=GOLD
))
fig_debt.add_trace(go.Scatter(
    x=[f"Yr {y}" for y in results["years"]], y=results["leverage_ratios"],
    name="Leverage Ratio", yaxis="y2",
    line=dict(color="#c62828", width=3, dash="dot"), mode="lines+markers"
))
fig_debt.update_layout(
    title="Debt Paydown & Deleveraging Profile",
    barmode="stack", template="plotly_white", height=420,
    font=dict(family="Source Sans Pro"),
    yaxis=dict(title="$M"),
    yaxis2=dict(title="Leverage (x)", overlaying="y", side="right"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02)
)
st.plotly_chart(fig_debt, use_container_width=True)


# ─────────────────────────────────────────────
# Exit Analysis (Returns Bridge)
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
    # Returns bridge waterfall
    entry_equity = results['total_equity']
    ebitda_growth_value = (results['exit_ebitda'] - implied_ebitda) * exit_multiple
    multiple_expansion = (exit_multiple - entry_multiple) * results['exit_ebitda']
    debt_paydown_value = results['total_debt'] - results['net_debt_at_exit']
    # Fees reduce value
    fees = enterprise_value * transaction_fees_pct + results['total_debt'] * financing_fees_pct

    fig_bridge = go.Figure(go.Waterfall(
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "total"],
        x=["Entry Equity", "EBITDA Growth", "Multiple Exp.", "Debt Paydown", "Exit Equity"],
        y=[entry_equity, ebitda_growth_value, multiple_expansion, debt_paydown_value, 0],
        connector={"line": {"color": "#666"}},
        increasing={"marker": {"color": "#2e7d32"}},
        decreasing={"marker": {"color": "#c62828"}},
        totals={"marker": {"color": DARK_BLUE}},
        text=[f"${entry_equity:.0f}M", f"${ebitda_growth_value:.0f}M",
              f"${multiple_expansion:.0f}M", f"${debt_paydown_value:.0f}M",
              f"${results['equity_at_exit']:.0f}M"],
        textposition="outside"
    ))
    fig_bridge.update_layout(
        title="Returns Attribution Bridge",
        template="plotly_white", height=400,
        font=dict(family="Source Sans Pro"),
        yaxis_title="$M",
        showlegend=False
    )
    st.plotly_chart(fig_bridge, use_container_width=True)


# ─────────────────────────────────────────────
# Sensitivity Analysis
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">🔬 Sensitivity Analysis</div>', unsafe_allow_html=True)

st.markdown("""<div class="info-box">
    Two-way sensitivity tables showing how <strong>IRR</strong> and <strong>MOIC</strong> change
    across different <strong>Exit Multiples</strong> and <strong>Revenue Growth</strong> assumptions.
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

s1, s2 = st.columns(2)

with s1:
    fig_irr = go.Figure(data=go.Heatmap(
        z=irr_matrix,
        x=[f"{ex:.1f}x" for ex in exit_range],
        y=[f"{g*100:.1f}%" for g in growth_range],
        colorscale=[[0, "#c62828"], [0.4, "#FFD700"], [0.6, "#4CAF50"], [1, "#1B5E20"]],
        text=[[f"{v:.1f}%" for v in row] for row in irr_matrix],
        texttemplate="%{text}",
        textfont={"size": 12, "color": "white"},
        hovertemplate="Exit Multiple: %{x}<br>Rev Growth: %{y}<br>IRR: %{z:.1f}%<extra></extra>",
        colorbar=dict(title="IRR %")
    ))
    fig_irr.update_layout(
        title="IRR Sensitivity (Exit Multiple vs Revenue Growth)",
        xaxis_title="Exit EV/EBITDA Multiple",
        yaxis_title="Revenue Growth Rate",
        template="plotly_white", height=420,
        font=dict(family="Source Sans Pro")
    )
    st.plotly_chart(fig_irr, use_container_width=True)

with s2:
    fig_moic = go.Figure(data=go.Heatmap(
        z=moic_matrix,
        x=[f"{ex:.1f}x" for ex in exit_range],
        y=[f"{g*100:.1f}%" for g in growth_range],
        colorscale=[[0, "#c62828"], [0.35, "#FFD700"], [0.6, "#4CAF50"], [1, "#1B5E20"]],
        text=[[f"{v:.2f}x" for v in row] for row in moic_matrix],
        texttemplate="%{text}",
        textfont={"size": 12, "color": "white"},
        hovertemplate="Exit Multiple: %{x}<br>Rev Growth: %{y}<br>MOIC: %{z:.2f}x<extra></extra>",
        colorbar=dict(title="MOIC")
    ))
    fig_moic.update_layout(
        title="MOIC Sensitivity (Exit Multiple vs Revenue Growth)",
        xaxis_title="Exit EV/EBITDA Multiple",
        yaxis_title="Revenue Growth Rate",
        template="plotly_white", height=420,
        font=dict(family="Source Sans Pro")
    )
    st.plotly_chart(fig_moic, use_container_width=True)

# --- Sensitivity Tables ---
st.markdown("**IRR Sensitivity Table (%)**")
df_irr_sens = pd.DataFrame(
    irr_matrix,
    index=[f"Growth {g*100:.1f}%" for g in growth_range],
    columns=[f"Exit {ex:.1f}x" for ex in exit_range]
).round(1)
st.dataframe(df_irr_sens.style.format("{:.1f}%").background_gradient(
    cmap="RdYlGn", vmin=0, vmax=40
), use_container_width=True)

st.markdown("**MOIC Sensitivity Table**")
df_moic_sens = pd.DataFrame(
    moic_matrix,
    index=[f"Growth {g*100:.1f}%" for g in growth_range],
    columns=[f"Exit {ex:.1f}x" for ex in exit_range]
).round(2)
st.dataframe(df_moic_sens.style.format("{:.2f}x").background_gradient(
    cmap="RdYlGn", vmin=1, vmax=4
), use_container_width=True)


# ─────────────────────────────────────────────
# Additional: Leverage Sensitivity
# ─────────────────────────────────────────────
with st.expander("📊 Additional: IRR vs Leverage Sensitivity"):
    st.markdown("How does the capital structure (total debt as % of EV) impact sponsor IRR?")
    leverage_pcts = np.arange(0.40, 0.85, 0.05)
    irr_by_leverage = []
    for lev in leverage_pcts:
        # Distribute proportionally
        ratio_a = senior_a_pct / (senior_a_pct + senior_b_pct + mezz_pct) if (senior_a_pct + senior_b_pct + mezz_pct) > 0 else 0.5
        ratio_b = senior_b_pct / (senior_a_pct + senior_b_pct + mezz_pct) if (senior_a_pct + senior_b_pct + mezz_pct) > 0 else 0.33
        ratio_m = 1 - ratio_a - ratio_b
        res = run_lbo_model(
            enterprise_value, entry_multiple, transaction_fees_pct, financing_fees_pct,
            holding_period, exit_multiple, base_revenue, revenue_growth, base_ebitda_margin,
            ebitda_margin_improvement, capex_pct_revenue, nwc_pct_revenue, tax_rate,
            da_pct_revenue, lev * ratio_a, senior_a_rate, senior_a_amort,
            lev * ratio_b, senior_b_rate, senior_b_amort,
            lev * ratio_m, mezz_rate, mezz_amort, cash_sweep_pct
        )
        irr_by_leverage.append(res["irr"] * 100)

    fig_lev = go.Figure()
    fig_lev.add_trace(go.Scatter(
        x=[f"{l*100:.0f}%" for l in leverage_pcts], y=irr_by_leverage,
        mode="lines+markers+text",
        text=[f"{v:.1f}%" for v in irr_by_leverage],
        textposition="top center",
        line=dict(color=DARK_BLUE, width=3),
        marker=dict(size=10, color=GOLD, line=dict(color=DARK_BLUE, width=2))
    ))
    fig_lev.update_layout(
        title="IRR Sensitivity to Leverage (Total Debt / EV)",
        xaxis_title="Debt as % of Enterprise Value",
        yaxis_title="IRR (%)",
        template="plotly_white", height=400,
        font=dict(family="Source Sans Pro")
    )
    st.plotly_chart(fig_lev, use_container_width=True)


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
