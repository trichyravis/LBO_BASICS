

"""
LBO Investment Model - Verified & Corrected
The Mountain Path - World of Finance
Prof. V. Ravichandran

CRITICAL FIX: Return calculation now correctly adds Sum of Balance FCF
Equity Value at Exit = Exit EV + Accumulated Balance FCF - Remaining Debt

ZERO external chart libraries - uses only Streamlit native components
"""

import streamlit as st
import pandas as pd
import numpy as np

# ============================================================================
# BRANDING & STYLING
# ============================================================================
COLORS = {
    'dark_blue': '#003366',
    'medium_blue': '#004d80',
    'light_blue': '#ADD8E6',
    'accent_gold': '#FFD700',
    'bg_dark': '#0a1628',
    'card_bg': '#112240',
    'text_primary': '#e6f1ff',
    'text_secondary': '#8892b0',
    'success': '#28a745',
    'danger': '#dc3545',
}

BRANDING = {
    'name': 'The Mountain Path - World of Finance',
    'instructor': 'Prof. V. Ravichandran',
    'credentials': '28+ Years Corporate Finance & Banking | 10+ Years Academic Excellence',
    'icon': '🏔️',
}

PAGE_CONFIG = {
    'page_title': 'LBO Model | Mountain Path',
    'page_icon': '🏔️',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded',
}


def apply_styles():
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Source+Sans+Pro:wght@300;400;600;700&display=swap');

        .stApp {{
            background: linear-gradient(135deg, {COLORS['bg_dark']} 0%, {COLORS['dark_blue']} 50%, #0d2137 100%);
        }}

        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {COLORS['bg_dark']} 0%, {COLORS['dark_blue']} 100%);
            border-right: 1px solid rgba(255,215,0,0.2);
        }}

        /* Force all sidebar text to be light colored */
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] .stSlider label,
        section[data-testid="stSidebar"] .stNumberInput label,
        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
        section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] label,
        section[data-testid="stSidebar"] .stSlider [data-testid="stTickBarMin"],
        section[data-testid="stSidebar"] .stSlider [data-testid="stTickBarMax"] {{
            color: {COLORS['text_primary']} !important;
        }}

        /* Slider current value text */
        section[data-testid="stSidebar"] [data-testid="stThumbValue"],
        section[data-testid="stSidebar"] .stSlider div[data-testid="stTickBarMin"],
        section[data-testid="stSidebar"] .stSlider div[data-testid="stTickBarMax"] {{
            color: {COLORS['accent_gold']} !important;
        }}

        /* Number input and select box text inside fields */
        section[data-testid="stSidebar"] input {{
            color: #1a1a2e !important;
            background-color: #ffffff !important;
        }}
        section[data-testid="stSidebar"] select,
        section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] span {{
            color: {COLORS['text_primary']} !important;
        }}

        .header-container {{
            background: linear-gradient(135deg, {COLORS['dark_blue']}, {COLORS['medium_blue']});
            border: 2px solid {COLORS['accent_gold']};
            border-radius: 12px;
            padding: 1.5rem 2rem;
            margin-bottom: 1.5rem;
            text-align: center;
        }}
        .header-container h1 {{
            font-family: 'Playfair Display', serif;
            color: {COLORS['accent_gold']};
            margin: 0; font-size: 2rem;
        }}
        .header-container p {{
            color: {COLORS['text_primary']};
            font-family: 'Source Sans Pro', sans-serif;
            margin: 0.3rem 0 0; font-size: 0.9rem;
        }}

        .metric-card {{
            background: {COLORS['card_bg']};
            border: 1px solid rgba(255,215,0,0.3);
            border-radius: 10px;
            padding: 1.2rem; text-align: center;
            margin-bottom: 0.8rem;
        }}
        .metric-card .label {{
            color: {COLORS['text_secondary']};
            font-size: 0.8rem; text-transform: uppercase;
            letter-spacing: 1px;
            font-family: 'Source Sans Pro', sans-serif;
        }}
        .metric-card .value {{
            color: {COLORS['accent_gold']};
            font-size: 1.6rem; font-weight: 700;
            font-family: 'Playfair Display', serif;
            margin-top: 0.3rem;
        }}

        .fix-banner {{
            background: linear-gradient(90deg, #1a472a, #2d6a3e);
            border: 2px solid {COLORS['success']};
            border-radius: 10px;
            padding: 1rem 1.5rem; margin-bottom: 1.5rem;
            color: white;
            font-family: 'Source Sans Pro', sans-serif;
        }}
        .error-banner {{
            background: linear-gradient(90deg, #4a1a1a, #6a2d2d);
            border: 2px solid {COLORS['danger']};
            border-radius: 10px;
            padding: 1rem 1.5rem; margin-bottom: 1rem;
            color: white;
            font-family: 'Source Sans Pro', sans-serif;
        }}

        .section-title {{
            font-family: 'Playfair Display', serif;
            color: {COLORS['accent_gold']};
            font-size: 1.3rem;
            border-bottom: 2px solid rgba(255,215,0,0.3);
            padding-bottom: 0.5rem;
            margin: 1.5rem 0 1rem;
        }}

        .formula-box {{
            background: rgba(0,51,102,0.5);
            border: 1px solid {COLORS['accent_gold']};
            border-radius: 8px;
            padding: 1rem 1.5rem;
            font-family: 'Source Sans Pro', monospace;
            color: {COLORS['text_primary']};
            margin: 0.8rem 0;
        }}

        .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
        .stTabs [data-baseweb="tab"] {{
            background: {COLORS['card_bg']};
            border: 1px solid rgba(255,215,0,0.3);
            border-radius: 8px;
            color: {COLORS['text_primary']};
            font-family: 'Source Sans Pro', sans-serif;
            padding: 0.5rem 1rem;
        }}
        .stTabs [aria-selected="true"] {{
            background: {COLORS['dark_blue']};
            border: 2px solid {COLORS['accent_gold']};
            color: {COLORS['accent_gold']};
        }}

        div[data-testid="stDataFrame"] {{
            border: 1px solid rgba(255,215,0,0.2);
            border-radius: 8px;
        }}

        footer {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)


def fmt_m(value, decimals=1):
    """Format as millions"""
    if abs(value) >= 1e6:
        return f"${value / 1e6:,.{decimals}f}M"
    else:
        return f"${value:,.0f}"


# ============================================================================
# LBO MODEL ENGINE
# ============================================================================
class LBOModel:
    def __init__(self, params):
        self.p = params
        self.df = None

        self.purchase_price = params['purchase_price']
        self.fees = params['purchase_price'] * params['fee_pct']
        self.total_cost = self.purchase_price + self.fees
        self.debt = params['purchase_price'] * params['debt_pct']
        self.equity = self.total_cost - self.debt

        self.entry_revenue = params['ltm_revenue']
        self.entry_ebitda = params['ltm_ebitda']
        self.ebitda_margin = params['ebitda_margin']
        self.revenue_growth = params['revenue_growth']
        self.tax_rate = params['tax_rate']
        self.capex = params['capex']
        self.depreciation = params['depreciation']
        self.nwc_pct = params['nwc_pct']

        self.interest_rate = params['interest_rate']
        self.mandatory_repay_pct = params['mandatory_repay_pct']

        self.exit_multiple = params['exit_multiple']
        self.hold_years = params['hold_years']

    def project(self):
        results = []
        current_debt = self.debt
        prev_revenue = self.entry_revenue
        accumulated_balance_fcf = 0.0

        for year in range(1, self.hold_years + 1):
            revenue = prev_revenue * (1 + self.revenue_growth)
            ebitda = revenue * self.ebitda_margin
            depreciation = self.depreciation
            ebit = ebitda - depreciation
            interest = current_debt * self.interest_rate
            ebt = ebit - interest
            tax = max(0, ebt * self.tax_rate)
            net_income = ebt - tax

            nwc_change = revenue * self.nwc_pct
            fcf = net_income + depreciation - self.capex - nwc_change

            mandatory_repay = current_debt * self.mandatory_repay_pct
            balance_fcf = fcf - mandatory_repay
            accumulated_balance_fcf += balance_fcf
            ending_debt = current_debt - mandatory_repay

            results.append({
                'Year': year,
                'Calendar_Year': 2024 + year - 1,
                'Revenue': revenue,
                'EBITDA': ebitda,
                'Depreciation': depreciation,
                'EBIT': ebit,
                'Interest': interest,
                'EBT': ebt,
                'Tax': tax,
                'Net_Income': net_income,
                'NWC_Change': nwc_change,
                'Levered_FCF': fcf,
                'Mandatory_Debt_Payment': mandatory_repay,
                'Balance_FCF': balance_fcf,
                'Accumulated_Balance_FCF': accumulated_balance_fcf,
                'Beginning_Debt': current_debt,
                'Ending_Debt': ending_debt,
            })

            current_debt = ending_debt
            prev_revenue = revenue

        self.df = pd.DataFrame(results)
        return self.df

    def get_returns(self):
        """
        CRITICAL FIX:
        Equity Value at Exit = Exit EV + Sum of Balance FCF - Remaining Debt
        """
        if self.df is None:
            self.project()

        final = self.df.iloc[-1]
        exit_ebitda = final['EBITDA']
        exit_ev = exit_ebitda * self.exit_multiple
        accumulated_fcf = final['Accumulated_Balance_FCF']
        remaining_debt = final['Ending_Debt']

        equity_proceeds = exit_ev + accumulated_fcf - remaining_debt

        moic = equity_proceeds / self.equity if self.equity > 0 else 0
        irr = (moic ** (1 / self.hold_years)) - 1 if moic > 0 else 0

        entry_ev_multiple = self.purchase_price / self.entry_ebitda
        debt_paydown = self.debt - remaining_debt
        ebitda_growth_value = (exit_ebitda - self.entry_ebitda) * entry_ev_multiple
        multiple_expansion_value = (self.exit_multiple - entry_ev_multiple) * exit_ebitda
        fcf_contribution = accumulated_fcf

        return {
            'exit_ebitda': exit_ebitda,
            'exit_ev': exit_ev,
            'accumulated_fcf': accumulated_fcf,
            'remaining_debt': remaining_debt,
            'equity_proceeds': equity_proceeds,
            'moic': moic,
            'irr': irr,
            'debt_paydown': debt_paydown,
            'ebitda_growth_value': ebitda_growth_value,
            'multiple_expansion_value': multiple_expansion_value,
            'fcf_contribution': fcf_contribution,
        }


# ============================================================================
# MAIN APPLICATION
# ============================================================================
def main():
    st.set_page_config(**PAGE_CONFIG)
    apply_styles()

    st.markdown(f"""
    <div class="header-container">
        <h1>{BRANDING['icon']} LBO Investment Model</h1>
        <p>{BRANDING['name']}</p>
        <p style="font-size:0.8rem; color:{COLORS['text_secondary']};">
            {BRANDING['instructor']} | {BRANDING['credentials']}</p>
    </div>
    """, unsafe_allow_html=True)

    # ========== SIDEBAR ==========
    st.sidebar.markdown(f"""
    <div style="text-align:center; padding:1.2rem; background:rgba(255,215,0,0.08);
         border-radius:10px; margin-bottom:1.5rem; border:2px solid {COLORS['accent_gold']};">
        <h3 style="color:{COLORS['accent_gold']}; margin:0;">{BRANDING['icon']} LBO MODEL</h3>
        <p style="color:{COLORS['text_secondary']}; font-size:0.75rem; margin:5px 0 0;">
            </p>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown(f"<p style='color:{COLORS['accent_gold']}; font-weight:700;'>📋 Transaction</p>",
                         unsafe_allow_html=True)
    purchase_price = st.sidebar.number_input("Purchase Price", value=100_000_000, step=1_000_000, format="%d")
    fee_pct = st.sidebar.slider("Fees & Expenses (%)", 1.0, 10.0, 2.0, 0.5) / 100
    debt_pct = st.sidebar.slider("Debt / Purchase Price (%)", 40.0, 80.0, 60.0, 5.0) / 100
    exit_multiple = st.sidebar.number_input("Exit EBITDA Multiple", value=10.0, step=0.5, format="%.1f")
    hold_years = st.sidebar.selectbox("Holding Period (Years)", [3, 4, 5, 6, 7], index=2)

    st.sidebar.markdown(f"<p style='color:{COLORS['accent_gold']}; font-weight:700;'>📊 Operating</p>",
                         unsafe_allow_html=True)
    ltm_revenue = st.sidebar.number_input("LTM Revenue", value=100_000_000, step=1_000_000, format="%d")
    ebitda_margin = st.sidebar.slider("EBITDA Margin (%)", 10.0, 50.0, 25.0, 1.0) / 100
    revenue_growth = st.sidebar.slider("Revenue Growth (%)", 1.0, 20.0, 5.0, 0.5) / 100
    tax_rate = st.sidebar.slider("Tax Rate (%)", 15.0, 35.0, 25.0, 1.0) / 100
    capex = st.sidebar.number_input("Annual CapEx", value=5_000_000, step=500_000, format="%d")
    depreciation = st.sidebar.number_input("Annual Depreciation", value=3_000_000, step=500_000, format="%d")
    nwc_pct = st.sidebar.slider("NWC Change (% of Revenue)", -5.0, 5.0, -1.0, 0.5) / 100

    st.sidebar.markdown(f"<p style='color:{COLORS['accent_gold']}; font-weight:700;'>🏦 Debt</p>",
                         unsafe_allow_html=True)
    interest_rate = st.sidebar.slider("Interest Rate (%)", 3.0, 12.0, 7.0, 0.5) / 100
    mandatory_repay_pct = st.sidebar.slider("Mandatory Repayment (%)", 5.0, 20.0, 10.0, 1.0) / 100

    ltm_ebitda = ltm_revenue * ebitda_margin
    params = {
        'purchase_price': purchase_price, 'fee_pct': fee_pct, 'debt_pct': debt_pct,
        'ltm_revenue': ltm_revenue, 'ltm_ebitda': ltm_ebitda,
        'ebitda_margin': ebitda_margin, 'revenue_growth': revenue_growth,
        'tax_rate': tax_rate, 'capex': capex, 'depreciation': depreciation,
        'nwc_pct': nwc_pct, 'interest_rate': interest_rate,
        'mandatory_repay_pct': mandatory_repay_pct,
        'exit_multiple': exit_multiple, 'hold_years': hold_years,
    }

    model = LBOModel(params)
    df = model.project()
    returns = model.get_returns()

    # ========== TABS ==========
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Transaction Summary",
        "📊 Financial Projections",
        "💰 FCF & Debt Schedule",
        "🎯 Exit & Returns",
        "📈 Sensitivity",
    ])

    # TAB 1
    with tab1:
        st.markdown('<div class="section-title">🏢 Transaction Overview</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="metric-card"><div class="label">Purchase Price</div>'
                        f'<div class="value">{fmt_m(model.purchase_price)}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><div class="label">Total Cost</div>'
                        f'<div class="value">{fmt_m(model.total_cost)}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card"><div class="label">Debt Raised</div>'
                        f'<div class="value">{fmt_m(model.debt)}</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="metric-card"><div class="label">Sponsor Equity</div>'
                        f'<div class="value">{fmt_m(model.equity)}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">📋 Sources & Uses</div>', unsafe_allow_html=True)
        cs, cu = st.columns(2)
        with cs:
            st.dataframe(pd.DataFrame({
                'Sources': ['Debt Raised', 'Sponsor Equity', '**Total**'],
                'Amount': [fmt_m(model.debt), fmt_m(model.equity), fmt_m(model.total_cost)],
            }), use_container_width=True, hide_index=True)
        with cu:
            st.dataframe(pd.DataFrame({
                'Uses': ['Purchase Price', 'Fees & Expenses', '**Total**'],
                'Amount': [fmt_m(model.purchase_price), fmt_m(model.fees), fmt_m(model.total_cost)],
            }), use_container_width=True, hide_index=True)
        st.success("✅ Sources = Uses — Transaction balances perfectly")

        st.markdown('<div class="section-title">📊 Key Assumptions</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({
            'Category': ['Transaction', 'Transaction', 'Transaction', 'Operating', 'Operating',
                          'Operating', 'Operating', 'Debt', 'Debt', 'Exit'],
            'Parameter': ['Entry EV/EBITDA', 'Debt %', 'Fees %', 'Revenue Growth', 'EBITDA Margin',
                          'CapEx', 'NWC Change', 'Interest Rate', 'Mandatory Repay %', 'Exit Multiple'],
            'Value': [
                f"{model.purchase_price / model.entry_ebitda:.1f}x",
                f"{debt_pct * 100:.0f}%", f"{fee_pct * 100:.1f}%",
                f"{revenue_growth * 100:.1f}%", f"{ebitda_margin * 100:.1f}%",
                fmt_m(capex), f"{nwc_pct * 100:.1f}%",
                f"{interest_rate * 100:.1f}%", f"{mandatory_repay_pct * 100:.0f}%",
                f"{exit_multiple:.1f}x",
            ],
        }), use_container_width=True, hide_index=True)

    # TAB 2
    with tab2:
        st.markdown('<div class="section-title">📊 Income Statement Projections</div>', unsafe_allow_html=True)
        income_display = df[['Calendar_Year', 'Revenue', 'EBITDA', 'Depreciation',
                             'EBIT', 'Interest', 'EBT', 'Tax', 'Net_Income']].copy()
        income_display.columns = ['Year', 'Revenue', 'EBITDA', 'Depreciation',
                                  'EBIT', 'Interest', 'EBT', 'Tax', 'Net Income']
        for col in income_display.columns:
            if col != 'Year':
                income_display[col] = income_display[col].apply(lambda x: f"{x:,.0f}")
        st.dataframe(income_display, use_container_width=True, hide_index=True)

        st.markdown('<div class="section-title">📈 Revenue & EBITDA Growth</div>', unsafe_allow_html=True)
        chart_data = df[['Calendar_Year', 'Revenue', 'EBITDA']].copy()
        chart_data = chart_data.set_index('Calendar_Year')
        st.bar_chart(chart_data)

    # TAB 3
    with tab3:
        st.markdown('<div class="section-title">💰 Levered Free Cash Flow</div>', unsafe_allow_html=True)
        fcf_display = df[['Calendar_Year', 'Net_Income', 'Depreciation', 'NWC_Change',
                          'Levered_FCF', 'Mandatory_Debt_Payment',
                          'Balance_FCF', 'Accumulated_Balance_FCF']].copy()
        fcf_display.insert(3, 'CapEx', model.capex)
        fcf_display.columns = ['Year', 'Net Income', '+ Depreciation', 'Less: Chg NWC',
                               '- CapEx', 'Levered FCF', '- Debt Repay',
                               'Balance FCF', 'Accum Bal FCF']
        for col in fcf_display.columns:
            if col != 'Year':
                fcf_display[col] = fcf_display[col].apply(
                    lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) else x)
        st.dataframe(fcf_display, use_container_width=True, hide_index=True)

        st.markdown('<div class="section-title">📈 FCF Components</div>', unsafe_allow_html=True)
        fcf_chart = df[['Calendar_Year', 'Levered_FCF', 'Balance_FCF']].copy()
        fcf_chart = fcf_chart.set_index('Calendar_Year')
        fcf_chart.columns = ['Levered FCF', 'Balance FCF']
        st.bar_chart(fcf_chart)

        st.markdown('<div class="section-title">🏦 Debt Schedule</div>', unsafe_allow_html=True)
        debt_display = df[['Calendar_Year', 'Beginning_Debt', 'Interest',
                           'Mandatory_Debt_Payment', 'Ending_Debt']].copy()
        debt_display.columns = ['Year', 'Beginning Debt', 'Interest', 'Mandatory Repayment', 'Ending Debt']
        for col in debt_display.columns:
            if col != 'Year':
                debt_display[col] = debt_display[col].apply(lambda x: f"{x:,.0f}")
        st.dataframe(debt_display, use_container_width=True, hide_index=True)

        st.markdown('<div class="section-title">📉 Debt vs Accumulated FCF</div>', unsafe_allow_html=True)
        debt_chart = df[['Calendar_Year', 'Ending_Debt', 'Accumulated_Balance_FCF']].copy()
        debt_chart = debt_chart.set_index('Calendar_Year')
        debt_chart.columns = ['Remaining Debt', 'Accumulated Balance FCF']
        st.line_chart(debt_chart)

    # TAB 4 - EXIT & RETURNS (CORRECTED)
    with tab4:
        st.markdown('<div class="section-title">🎯 Exit & Returns Analysis</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="fix-banner">
            <strong>✅ CORRECTED FORMULA:</strong><br>
            Equity Value at Exit = Exit EV <strong>+ Sum of Balance FCF</strong> − Remaining Debt<br>
            <span style="font-size:0.85rem; opacity:0.9;">
                The accumulated Balance FCF (cash generated after mandatory debt repayments)
                is added to exit proceeds.</span>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="metric-card"><div class="label">MOIC</div>'
                        f'<div class="value">{returns["moic"]:.2f}x</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><div class="label">IRR</div>'
                        f'<div class="value">{returns["irr"] * 100:.1f}%</div></div>', unsafe_allow_html=True)
        with c3:
            status = "✅ ATTRACTIVE" if returns['irr'] >= 0.25 else (
                "⚠️ MARGINAL" if returns['irr'] >= 0.15 else "❌ WEAK")
            st.markdown(f'<div class="metric-card"><div class="label">Deal Quality</div>'
                        f'<div class="value">{status}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">📋 Exit Calculation Waterfall</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({
            'Metric': [
                'Exit Year EBITDA', 'Exit Multiple', 'Exit Enterprise Value',
                '➕ Accumulated Balance FCF', '➖ Remaining Debt',
                '= Equity Value at Exit', '',
                'Sponsor Equity Invested', 'MOIC', 'IRR',
            ],
            'Value': [
                fmt_m(returns['exit_ebitda']), f"{model.exit_multiple:.1f}x",
                fmt_m(returns['exit_ev']),
                fmt_m(returns['accumulated_fcf']),
                fmt_m(returns['remaining_debt']),
                fmt_m(returns['equity_proceeds']), '',
                fmt_m(model.equity),
                f"{returns['moic']:.2f}x", f"{returns['irr'] * 100:.1f}%",
            ],
        }), use_container_width=True, hide_index=True)

        st.markdown(f"""
        <div class="formula-box">
            <strong>Exit Equity Value Calculation:</strong><br><br>
            Exit EV = {fmt_m(returns['exit_ebitda'])} × {model.exit_multiple:.1f}x
            = <strong>{fmt_m(returns['exit_ev'])}</strong><br><br>
            Equity = {fmt_m(returns['exit_ev'])} + {fmt_m(returns['accumulated_fcf'])}
            − {fmt_m(returns['remaining_debt'])}
            = <strong>{fmt_m(returns['equity_proceeds'])}</strong><br><br>
            MOIC = {fmt_m(returns['equity_proceeds'])} / {fmt_m(model.equity)}
            = <strong>{returns['moic']:.2f}x</strong><br>
            IRR = ({returns['moic']:.2f})^(1/{model.hold_years}) − 1
            = <strong>{returns['irr'] * 100:.1f}%</strong>
        </div>
        """, unsafe_allow_html=True)

        wrong_eq = returns['exit_ev'] - returns['remaining_debt']
        wrong_moic = wrong_eq / model.equity if model.equity > 0 else 0
        wrong_irr = (wrong_moic ** (1 / model.hold_years)) - 1 if wrong_moic > 0 else 0

        st.markdown(f"""

        """, unsafe_allow_html=True)

        st.markdown('<div class="section-title">📊 Returns Attribution Bridge</div>', unsafe_allow_html=True)
        bridge_data = pd.DataFrame({
            'Value': [
                returns['debt_paydown'],
                returns['ebitda_growth_value'],
                returns['multiple_expansion_value'],
                returns['fcf_contribution'],
            ]
        }, index=['Debt Paydown', 'EBITDA Growth', 'Multiple Expansion', 'Accumulated FCF'])
        st.bar_chart(bridge_data)

    # TAB 5 - SENSITIVITY
    with tab5:
        st.markdown('<div class="section-title">📈 Exit Multiple Sensitivity</div>', unsafe_allow_html=True)
        sensitivity = []
        for exit_m in np.arange(5.0, 12.5, 0.5):
            exit_ev_s = returns['exit_ebitda'] * exit_m
            eq_proc = exit_ev_s + returns['accumulated_fcf'] - returns['remaining_debt']
            m = eq_proc / model.equity if model.equity > 0 else 0
            i = (m ** (1 / model.hold_years)) - 1 if m > 0 else 0
            sensitivity.append({
                'Exit Multiple': f"{exit_m:.1f}x",
                'Exit EV': fmt_m(exit_ev_s),
                'Equity Value': fmt_m(eq_proc),
                'MOIC': f"{m:.2f}x",
                'IRR': f"{i * 100:.1f}%",
                'Status': '✅' if i >= 0.25 else ('⚠️' if i >= 0.15 else '❌'),
            })
        st.dataframe(pd.DataFrame(sensitivity), use_container_width=True, hide_index=True)

        st.markdown('<div class="section-title">📊 2D Sensitivity: Exit Multiple × EBITDA Margin</div>',
                    unsafe_allow_html=True)
        exit_range = np.arange(6.0, 11.0, 1.0)
        margin_range = np.arange(0.20, 0.36, 0.03)
        irr_matrix = []
        for margin in margin_range:
            row = []
            for exit_m in exit_range:
                tp = params.copy()
                tp['ebitda_margin'] = margin
                tp['exit_multiple'] = exit_m
                tp['ltm_ebitda'] = ltm_revenue * margin
                tm = LBOModel(tp)
                tm.project()
                tr = tm.get_returns()
                row.append(f"{tr['irr'] * 100:.1f}%")
            irr_matrix.append(row)
        sens_2d = pd.DataFrame(irr_matrix,
                               index=[f"{m * 100:.0f}%" for m in margin_range],
                               columns=[f"{e:.1f}x" for e in exit_range])
        sens_2d.index.name = "EBITDA Margin ↓ / Exit Multiple →"
        st.dataframe(sens_2d, use_container_width=True)

        st.markdown('<div class="section-title">🏆 Value Creation Summary</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="formula-box">
            <strong>Entry Equity:</strong> {fmt_m(model.equity)}<br><br>
            <strong>Value Drivers:</strong><br>
            • Debt Paydown: {fmt_m(returns['debt_paydown'])}<br>
            • EBITDA Growth: {((returns['exit_ebitda'] / model.entry_ebitda) - 1) * 100:.1f}%
              ({fmt_m(model.entry_ebitda)} → {fmt_m(returns['exit_ebitda'])})<br>
            • Multiple Expansion: {model.purchase_price / model.entry_ebitda:.1f}x → {model.exit_multiple:.1f}x<br>
            • Accumulated Balance FCF: {fmt_m(returns['accumulated_fcf'])}<br><br>
            <strong>Exit Equity:</strong> {fmt_m(returns['equity_proceeds'])}<br>
            <strong>Total Value Created:</strong>
            {fmt_m(returns['equity_proceeds'] - model.equity)}
            ({((returns['equity_proceeds'] / model.equity) - 1) * 100:.0f}%)
        </div>
        """, unsafe_allow_html=True)

    # Footer
    st.divider()
    st.markdown(f"""
    <div style="text-align:center; padding:1rem;">
        <p style="color:{COLORS['accent_gold']}; font-family:'Playfair Display', serif; font-weight:700;">
            {BRANDING['icon']} {BRANDING['name']}</p>
        <p style="color:{COLORS['text_secondary']}; font-size:0.8rem;">
            {BRANDING['instructor']} | {BRANDING['credentials']}</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == '__main__':
    main()
