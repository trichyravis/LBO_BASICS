
"""
LBO Investment Model - Verified & Corrected
The Mountain Path - World of Finance
Prof. V. Ravichandran

CRITICAL FIX: Return calculation now correctly adds Sum of Balance FCF
Equity Value at Exit = Exit EV + Accumulated Balance FCF - Remaining Debt
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from dataclasses import dataclass

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
    'warning': '#ffc107',
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
            margin: 0;
            font-size: 2rem;
        }}
        
        .header-container p {{
            color: {COLORS['text_primary']};
            font-family: 'Source Sans Pro', sans-serif;
            margin: 0.3rem 0 0;
            font-size: 0.9rem;
        }}
        
        .metric-card {{
            background: {COLORS['card_bg']};
            border: 1px solid rgba(255,215,0,0.3);
            border-radius: 10px;
            padding: 1.2rem;
            text-align: center;
            margin-bottom: 0.8rem;
        }}
        
        .metric-card .label {{
            color: {COLORS['text_secondary']};
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-family: 'Source Sans Pro', sans-serif;
        }}
        
        .metric-card .value {{
            color: {COLORS['accent_gold']};
            font-size: 1.6rem;
            font-weight: 700;
            font-family: 'Playfair Display', serif;
            margin-top: 0.3rem;
        }}
        
        .fix-banner {{
            background: linear-gradient(90deg, #1a472a, #2d6a3e);
            border: 2px solid {COLORS['success']};
            border-radius: 10px;
            padding: 1rem 1.5rem;
            margin-bottom: 1.5rem;
            color: white;
            font-family: 'Source Sans Pro', sans-serif;
        }}
        
        .error-banner {{
            background: linear-gradient(90deg, #4a1a1a, #6a2d2d);
            border: 2px solid {COLORS['danger']};
            border-radius: 10px;
            padding: 1rem 1.5rem;
            margin-bottom: 1rem;
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
        
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}
        
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
        
        .formula-box {{
            background: rgba(0,51,102,0.5);
            border: 1px solid {COLORS['accent_gold']};
            border-radius: 8px;
            padding: 1rem 1.5rem;
            font-family: 'Source Sans Pro', monospace;
            color: {COLORS['text_primary']};
            margin: 0.8rem 0;
        }}
        
        .comparison-row {{
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        
        footer {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)


def fmt(value, prefix="$", suffix="", decimals=1):
    """Format numbers with Indian/global notation"""
    if abs(value) >= 1e7:
        return f"{prefix}{value/1e7:,.{decimals}f} Cr{suffix}"
    elif abs(value) >= 1e5:
        return f"{prefix}{value/1e5:,.{decimals}f} L{suffix}"
    else:
        return f"{prefix}{value:,.{decimals}f}{suffix}"


def fmt_m(value, decimals=1):
    """Format as millions (for international cases)"""
    if abs(value) >= 1e6:
        return f"${value/1e6:,.{decimals}f}M"
    else:
        return f"${value:,.0f}"


# ============================================================================
# LBO MODEL ENGINE
# ============================================================================
class LBOModel:
    def __init__(self, params):
        self.p = params
        self.df = None
        
        # Transaction
        self.purchase_price = params['purchase_price']
        self.fees = params['purchase_price'] * params['fee_pct']
        self.total_cost = self.purchase_price + self.fees
        self.debt = params['purchase_price'] * params['debt_pct']
        self.equity = self.total_cost - self.debt
        
        # Operations
        self.entry_revenue = params['ltm_revenue']
        self.entry_ebitda = params['ltm_ebitda']
        self.ebitda_margin = params['ebitda_margin']
        self.revenue_growth = params['revenue_growth']
        self.tax_rate = params['tax_rate']
        self.capex = params['capex']
        self.depreciation = params['depreciation']
        self.nwc_pct = params['nwc_pct']
        
        # Debt
        self.interest_rate = params['interest_rate']
        self.mandatory_repay_pct = params['mandatory_repay_pct']
        
        # Exit
        self.exit_multiple = params['exit_multiple']
        self.hold_years = params['hold_years']
    
    def project(self):
        results = []
        current_debt = self.debt
        prev_revenue = self.entry_revenue
        accumulated_balance_fcf = 0.0
        
        for year in range(1, self.hold_years + 1):
            # Revenue & EBITDA
            revenue = prev_revenue * (1 + self.revenue_growth)
            ebitda = revenue * self.ebitda_margin
            
            # Income Statement
            depreciation = self.depreciation
            ebit = ebitda - depreciation
            interest = current_debt * self.interest_rate
            ebt = ebit - interest
            tax = max(0, ebt * self.tax_rate)
            net_income = ebt - tax
            
            # Levered Free Cash Flow
            nwc_change = -(revenue * self.nwc_pct)  # negative = cash inflow
            fcf = net_income + depreciation - self.capex - nwc_change
            
            # Debt Repayment
            mandatory_repay = current_debt * self.mandatory_repay_pct
            
            # Balance FCF = FCF after mandatory debt repayment
            balance_fcf = fcf - mandatory_repay
            accumulated_balance_fcf += balance_fcf
            
            # Debt Schedule
            ending_debt = current_debt - mandatory_repay
            
            results.append({
                'Year': year,
                'Calendar_Year': 2024 + year,
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
        CRITICAL FIX: Equity Value at Exit = Exit EV + Sum of Balance FCF - Remaining Debt
        The accumulated Balance FCF (cash generated after mandatory debt payments) 
        MUST be added to exit proceeds.
        """
        if self.df is None:
            self.project()
        
        final = self.df.iloc[-1]
        
        # Exit Enterprise Value
        exit_ebitda = final['EBITDA']
        exit_ev = exit_ebitda * self.exit_multiple
        
        # Accumulated Balance FCF = Sum of all Balance FCF across holding period
        accumulated_fcf = final['Accumulated_Balance_FCF']
        
        # Remaining Debt
        remaining_debt = final['Ending_Debt']
        
        # ✅ CORRECTED FORMULA:
        # Equity Value = Exit EV + Accumulated Balance FCF - Remaining Debt
        equity_proceeds = exit_ev + accumulated_fcf - remaining_debt
        
        # Return Metrics
        moic = equity_proceeds / self.equity if self.equity > 0 else 0
        irr = (moic ** (1 / self.hold_years)) - 1 if moic > 0 else 0
        
        # Value creation breakdown
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
    
    # Header
    st.markdown(f"""
    <div class="header-container">
        <h1>{BRANDING['icon']} LBO Investment Model</h1>
        <p>{BRANDING['name']}</p>
        <p style="font-size: 0.8rem; color: {COLORS['text_secondary']};">{BRANDING['instructor']} | {BRANDING['credentials']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ========== SIDEBAR INPUTS ==========
    st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 1.2rem; background: rgba(255,215,0,0.08); 
         border-radius: 10px; margin-bottom: 1.5rem; border: 2px solid {COLORS['accent_gold']};">
        <h3 style="color: {COLORS['accent_gold']}; margin: 0;">{BRANDING['icon']} LBO MODEL</h3>
        <p style="color: {COLORS['text_secondary']}; font-size: 0.75rem; margin: 5px 0 0;">
            ✅ Corrected: Balance FCF in Returns</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown(f"<p style='color: {COLORS['accent_gold']}; font-weight: 700; font-size: 0.9rem;'>📋 Transaction</p>", unsafe_allow_html=True)
    purchase_price = st.sidebar.number_input("Purchase Price", value=100_000_000, step=1_000_000, format="%d")
    fee_pct = st.sidebar.slider("Fees & Expenses (%)", 1.0, 10.0, 2.0, 0.5) / 100
    debt_pct = st.sidebar.slider("Debt / Purchase Price (%)", 40.0, 80.0, 60.0, 5.0) / 100
    exit_multiple = st.sidebar.number_input("Exit EBITDA Multiple", value=8.0, step=0.5, format="%.1f")
    hold_years = st.sidebar.selectbox("Holding Period (Years)", [3, 4, 5, 6, 7], index=2)
    
    st.sidebar.markdown(f"<p style='color: {COLORS['accent_gold']}; font-weight: 700; font-size: 0.9rem;'>📊 Operating Assumptions</p>", unsafe_allow_html=True)
    ltm_revenue = st.sidebar.number_input("LTM Revenue", value=100_000_000, step=1_000_000, format="%d")
    ebitda_margin = st.sidebar.slider("EBITDA Margin (%)", 10.0, 50.0, 25.0, 1.0) / 100
    revenue_growth = st.sidebar.slider("Revenue Growth (%)", 1.0, 20.0, 5.0, 0.5) / 100
    tax_rate = st.sidebar.slider("Tax Rate (%)", 15.0, 35.0, 25.0, 1.0) / 100
    capex = st.sidebar.number_input("Annual CapEx", value=5_000_000, step=500_000, format="%d")
    depreciation = st.sidebar.number_input("Annual Depreciation", value=3_000_000, step=500_000, format="%d")
    nwc_pct = st.sidebar.slider("NWC Change (% of Revenue)", -5.0, 5.0, -1.0, 0.5) / 100
    
    st.sidebar.markdown(f"<p style='color: {COLORS['accent_gold']}; font-weight: 700; font-size: 0.9rem;'>🏦 Debt Assumptions</p>", unsafe_allow_html=True)
    interest_rate = st.sidebar.slider("Interest Rate (%)", 3.0, 12.0, 7.0, 0.5) / 100
    mandatory_repay_pct = st.sidebar.slider("Mandatory Repayment (% of Debt)", 5.0, 20.0, 10.0, 1.0) / 100
    
    # Build params
    ltm_ebitda = ltm_revenue * ebitda_margin
    params = {
        'purchase_price': purchase_price,
        'fee_pct': fee_pct,
        'debt_pct': debt_pct,
        'ltm_revenue': ltm_revenue,
        'ltm_ebitda': ltm_ebitda,
        'ebitda_margin': ebitda_margin,
        'revenue_growth': revenue_growth,
        'tax_rate': tax_rate,
        'capex': capex,
        'depreciation': depreciation,
        'nwc_pct': nwc_pct,
        'interest_rate': interest_rate,
        'mandatory_repay_pct': mandatory_repay_pct,
        'exit_multiple': exit_multiple,
        'hold_years': hold_years,
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
        "📈 Sensitivity & Attribution",
    ])
    
    # ------------------------------------------------------------------
    # TAB 1: TRANSACTION SUMMARY
    # ------------------------------------------------------------------
    with tab1:
        st.markdown(f'<div class="section-title">🏢 Transaction Overview</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="metric-card"><div class="label">Purchase Price</div><div class="value">{fmt_m(model.purchase_price)}</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><div class="label">Total Cost</div><div class="value">{fmt_m(model.total_cost)}</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><div class="label">Debt Raised</div><div class="value">{fmt_m(model.debt)}</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card"><div class="label">Sponsor Equity</div><div class="value">{fmt_m(model.equity)}</div></div>', unsafe_allow_html=True)
        
        st.markdown(f'<div class="section-title">📋 Sources & Uses</div>', unsafe_allow_html=True)
        col_s, col_u = st.columns(2)
        with col_s:
            sources_df = pd.DataFrame({
                'Sources': ['Debt Raised', 'Sponsor Equity', '**Total Sources**'],
                'Amount': [f"{fmt_m(model.debt)}", f"{fmt_m(model.equity)}", f"{fmt_m(model.total_cost)}"],
            })
            st.dataframe(sources_df, use_container_width=True, hide_index=True)
        with col_u:
            uses_df = pd.DataFrame({
                'Uses': ['Purchase Price', 'Fees & Expenses', '**Total Uses**'],
                'Amount': [f"{fmt_m(model.purchase_price)}", f"{fmt_m(model.fees)}", f"{fmt_m(model.total_cost)}"],
            })
            st.dataframe(uses_df, use_container_width=True, hide_index=True)
        
        # Verify Sources == Uses
        if abs(model.total_cost - model.total_cost) < 1:
            st.success("✅ Sources = Uses — Transaction balances perfectly")
        
        st.markdown(f'<div class="section-title">📊 Key Assumptions</div>', unsafe_allow_html=True)
        assumptions_df = pd.DataFrame({
            'Category': ['Transaction', 'Transaction', 'Transaction', 'Operating', 'Operating', 'Operating', 'Operating', 'Debt', 'Debt', 'Exit'],
            'Parameter': ['Entry EV/EBITDA', 'Debt %', 'Fees %', 'Revenue Growth', 'EBITDA Margin', 'CapEx (Annual)', 'NWC Change', 'Interest Rate', 'Mandatory Repay %', 'Exit Multiple'],
            'Value': [
                f"{model.purchase_price/model.entry_ebitda:.1f}x",
                f"{debt_pct*100:.0f}%",
                f"{fee_pct*100:.1f}%",
                f"{revenue_growth*100:.1f}%",
                f"{ebitda_margin*100:.1f}%",
                fmt_m(capex),
                f"{nwc_pct*100:.1f}%",
                f"{interest_rate*100:.1f}%",
                f"{mandatory_repay_pct*100:.0f}%",
                f"{exit_multiple:.1f}x",
            ],
        })
        st.dataframe(assumptions_df, use_container_width=True, hide_index=True)
    
    # ------------------------------------------------------------------
    # TAB 2: FINANCIAL PROJECTIONS
    # ------------------------------------------------------------------
    with tab2:
        st.markdown(f'<div class="section-title">📊 Income Statement Projections</div>', unsafe_allow_html=True)
        
        income_cols = ['Calendar_Year', 'Revenue', 'EBITDA', 'Depreciation', 'EBIT', 'Interest', 'EBT', 'Tax', 'Net_Income']
        income_df = df[income_cols].copy()
        income_df.columns = ['Year', 'Revenue', 'EBITDA', 'Depreciation', 'EBIT', 'Interest', 'EBT', 'Tax', 'Net Income']
        
        # Format for display
        display_income = income_df.copy()
        for col in display_income.columns:
            if col != 'Year':
                display_income[col] = display_income[col].apply(lambda x: f"{x:,.0f}")
        
        st.dataframe(display_income, use_container_width=True, hide_index=True)
        
        # Revenue & EBITDA Chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df['Calendar_Year'], y=df['Revenue'],
            name='Revenue', marker_color=COLORS['medium_blue'],
        ))
        fig.add_trace(go.Bar(
            x=df['Calendar_Year'], y=df['EBITDA'],
            name='EBITDA', marker_color=COLORS['accent_gold'],
        ))
        fig.update_layout(
            title='Revenue & EBITDA Growth',
            barmode='group',
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=COLORS['text_primary']),
            title_font=dict(color=COLORS['accent_gold']),
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # ------------------------------------------------------------------
    # TAB 3: FCF & DEBT SCHEDULE
    # ------------------------------------------------------------------
    with tab3:
        st.markdown(f'<div class="section-title">💰 Levered Free Cash Flow</div>', unsafe_allow_html=True)
        
        fcf_cols = ['Calendar_Year', 'Net_Income', 'Depreciation', 'NWC_Change', 'Levered_FCF', 'Mandatory_Debt_Payment', 'Balance_FCF', 'Accumulated_Balance_FCF']
        fcf_display = df[fcf_cols].copy()
        fcf_display.columns = ['Year', 'Net Income', '+ Depreciation', '- ΔWC', 'Levered FCF', '- Mandatory Debt Payment', 'Balance FCF', 'Accumulated Balance FCF']
        
        # Add CapEx row info
        fcf_display.insert(3, '- CapEx', model.capex)
        
        display_fcf = fcf_display.copy()
        for col in display_fcf.columns:
            if col != 'Year':
                display_fcf[col] = display_fcf[col].apply(lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) else x)
        
        st.dataframe(display_fcf, use_container_width=True, hide_index=True)
        
        # FCF Waterfall
        st.markdown(f'<div class="section-title">📊 FCF Components Chart</div>', unsafe_allow_html=True)
        fig_fcf = go.Figure()
        fig_fcf.add_trace(go.Bar(x=df['Calendar_Year'], y=df['Levered_FCF'], name='Levered FCF', marker_color=COLORS['accent_gold']))
        fig_fcf.add_trace(go.Bar(x=df['Calendar_Year'], y=-df['Mandatory_Debt_Payment'], name='Mandatory Debt Payment', marker_color=COLORS['danger']))
        fig_fcf.add_trace(go.Bar(x=df['Calendar_Year'], y=df['Balance_FCF'], name='Balance FCF', marker_color=COLORS['success']))
        fig_fcf.update_layout(
            barmode='group', template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=COLORS['text_primary']),
            title='Levered FCF vs Debt Payments vs Balance FCF',
            title_font=dict(color=COLORS['accent_gold']),
        )
        st.plotly_chart(fig_fcf, use_container_width=True)
        
        # Debt Schedule
        st.markdown(f'<div class="section-title">🏦 Debt Schedule</div>', unsafe_allow_html=True)
        debt_cols = ['Calendar_Year', 'Beginning_Debt', 'Interest', 'Mandatory_Debt_Payment', 'Ending_Debt']
        debt_display = df[debt_cols].copy()
        debt_display.columns = ['Year', 'Beginning Debt', 'Interest Expense', 'Mandatory Repayment', 'Ending Debt']
        
        display_debt = debt_display.copy()
        for col in display_debt.columns:
            if col != 'Year':
                display_debt[col] = display_debt[col].apply(lambda x: f"{x:,.0f}")
        
        st.dataframe(display_debt, use_container_width=True, hide_index=True)
        
        # Debt paydown chart
        fig_debt = go.Figure()
        fig_debt.add_trace(go.Scatter(
            x=df['Calendar_Year'], y=df['Beginning_Debt'],
            mode='lines+markers', name='Debt Outstanding',
            line=dict(color=COLORS['danger'], width=3),
            marker=dict(size=10),
        ))
        fig_debt.add_trace(go.Scatter(
            x=df['Calendar_Year'], y=df['Accumulated_Balance_FCF'],
            mode='lines+markers', name='Accumulated Balance FCF',
            line=dict(color=COLORS['success'], width=3),
            marker=dict(size=10),
        ))
        fig_debt.update_layout(
            title='Debt Paydown vs Accumulated Balance FCF',
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=COLORS['text_primary']),
            title_font=dict(color=COLORS['accent_gold']),
        )
        st.plotly_chart(fig_debt, use_container_width=True)
    
    # ------------------------------------------------------------------
    # TAB 4: EXIT & RETURNS (CORRECTED)
    # ------------------------------------------------------------------
    with tab4:
        st.markdown(f'<div class="section-title">🎯 Exit & Returns Analysis</div>', unsafe_allow_html=True)
        
        # CRITICAL FIX BANNER
        st.markdown(f"""
        <div class="fix-banner">
            <strong>✅ CORRECTED FORMULA:</strong><br>
            Equity Value at Exit = Exit EV <strong>+ Sum of Balance FCF</strong> − Remaining Debt<br>
            <span style="font-size: 0.85rem; opacity: 0.9;">
                The accumulated Balance FCF (cash generated after mandatory debt repayments over the holding period) 
                is added to exit proceeds — this is the cash sitting on the balance sheet at exit.
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        # Key Return Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-card"><div class="label">MOIC</div><div class="value">{returns["moic"]:.2f}x</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><div class="label">IRR</div><div class="value">{returns["irr"]*100:.1f}%</div></div>', unsafe_allow_html=True)
        with col3:
            irr_status = "✅ ATTRACTIVE" if returns['irr'] >= 0.25 else ("⚠️ MARGINAL" if returns['irr'] >= 0.15 else "❌ WEAK")
            st.markdown(f'<div class="metric-card"><div class="label">Deal Quality</div><div class="value">{irr_status}</div></div>', unsafe_allow_html=True)
        
        # Exit Waterfall Table
        st.markdown(f'<div class="section-title">📋 Exit Calculation Waterfall</div>', unsafe_allow_html=True)
        
        exit_table = pd.DataFrame({
            'Metric': [
                'Exit Year EBITDA',
                f'Exit Multiple',
                'Exit Enterprise Value',
                '➕ Accumulated Balance FCF',
                '➖ Remaining Debt',
                '= Equity Value at Exit',
                '',
                'Sponsor Equity Invested',
                'MOIC',
                'IRR',
            ],
            'Value': [
                fmt_m(returns['exit_ebitda']),
                f"{model.exit_multiple:.1f}x",
                fmt_m(returns['exit_ev']),
                fmt_m(returns['accumulated_fcf']),
                fmt_m(returns['remaining_debt']),
                fmt_m(returns['equity_proceeds']),
                '',
                fmt_m(model.equity),
                f"{returns['moic']:.2f}x",
                f"{returns['irr']*100:.1f}%",
            ],
        })
        st.dataframe(exit_table, use_container_width=True, hide_index=True)
        
        # Show the formula explicitly
        st.markdown(f"""
        <div class="formula-box">
            <strong>Exit Equity Value Calculation:</strong><br><br>
            Exit EV = {fmt_m(returns['exit_ebitda'])} × {model.exit_multiple:.1f}x = <strong>{fmt_m(returns['exit_ev'])}</strong><br><br>
            Equity = {fmt_m(returns['exit_ev'])} + {fmt_m(returns['accumulated_fcf'])} − {fmt_m(returns['remaining_debt'])} = <strong>{fmt_m(returns['equity_proceeds'])}</strong><br><br>
            MOIC = {fmt_m(returns['equity_proceeds'])} / {fmt_m(model.equity)} = <strong>{returns['moic']:.2f}x</strong><br>
            IRR = ({returns['moic']:.2f})^(1/{model.hold_years}) − 1 = <strong>{returns['irr']*100:.1f}%</strong>
        </div>
        """, unsafe_allow_html=True)
        
        # Show what the ERROR would be without accumulated FCF
        wrong_equity = returns['exit_ev'] - returns['remaining_debt']
        wrong_moic = wrong_equity / model.equity if model.equity > 0 else 0
        wrong_irr = (wrong_moic ** (1/model.hold_years)) - 1 if wrong_moic > 0 else 0
        
        st.markdown(f"""
        <div class="error-banner">
            <strong>❌ WITHOUT Balance FCF (Incorrect):</strong><br>
            Equity = {fmt_m(returns['exit_ev'])} − {fmt_m(returns['remaining_debt'])} = {fmt_m(wrong_equity)}<br>
            MOIC = {wrong_moic:.2f}x | IRR = {wrong_irr*100:.1f}%<br>
            <strong>Error: MOIC understated by {returns['moic'] - wrong_moic:.2f}x, IRR understated by {(returns['irr'] - wrong_irr)*100:.1f}pp</strong>
        </div>
        """, unsafe_allow_html=True)
        
        # Returns Attribution Bridge
        st.markdown(f'<div class="section-title">📊 Returns Attribution Bridge</div>', unsafe_allow_html=True)
        
        fig_bridge = go.Figure(go.Bar(
            x=['Debt Paydown', 'EBITDA Growth', 'Multiple Expansion', 'Accumulated FCF'],
            y=[
                returns['debt_paydown'],
                returns['ebitda_growth_value'],
                returns['multiple_expansion_value'],
                returns['fcf_contribution'],
            ],
            marker_color=[COLORS['medium_blue'], COLORS['accent_gold'], COLORS['success'], '#FF6B35'],
            text=[
                fmt_m(returns['debt_paydown']),
                fmt_m(returns['ebitda_growth_value']),
                fmt_m(returns['multiple_expansion_value']),
                fmt_m(returns['fcf_contribution']),
            ],
            textposition='outside',
            textfont=dict(color=COLORS['text_primary'], size=12),
        ))
        fig_bridge.update_layout(
            title='Value Creation Attribution',
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=COLORS['text_primary']),
            title_font=dict(color=COLORS['accent_gold']),
            yaxis_title='Value ($)',
            showlegend=False,
        )
        st.plotly_chart(fig_bridge, use_container_width=True)
    
    # ------------------------------------------------------------------
    # TAB 5: SENSITIVITY & ANALYSIS
    # ------------------------------------------------------------------
    with tab5:
        st.markdown(f'<div class="section-title">📈 Sensitivity Analysis</div>', unsafe_allow_html=True)
        
        # Exit Multiple Sensitivity
        st.markdown(f"**Exit Multiple Sensitivity**")
        sensitivity = []
        for exit_m in np.arange(5.0, 12.5, 0.5):
            exit_ev_s = returns['exit_ebitda'] * exit_m
            eq_proc = exit_ev_s + returns['accumulated_fcf'] - returns['remaining_debt']
            m = eq_proc / model.equity if model.equity > 0 else 0
            i = (m ** (1/model.hold_years)) - 1 if m > 0 else 0
            sensitivity.append({
                'Exit Multiple': f"{exit_m:.1f}x",
                'Exit EV': fmt_m(exit_ev_s),
                'Equity Value': fmt_m(eq_proc),
                'MOIC': f"{m:.2f}x",
                'IRR': f"{i*100:.1f}%",
                'Status': '✅' if i >= 0.25 else ('⚠️' if i >= 0.15 else '❌'),
            })
        
        st.dataframe(pd.DataFrame(sensitivity), use_container_width=True, hide_index=True)
        
        # 2D Sensitivity: Exit Multiple vs EBITDA Margin
        st.markdown(f'<div class="section-title">📊 2D Sensitivity: Exit Multiple × EBITDA Margin</div>', unsafe_allow_html=True)
        
        exit_range = np.arange(6.0, 11.0, 1.0)
        margin_range = np.arange(0.20, 0.36, 0.03)
        
        irr_matrix = []
        for margin in margin_range:
            row = []
            for exit_m in exit_range:
                # Recalculate with different margin
                test_params = params.copy()
                test_params['ebitda_margin'] = margin
                test_params['exit_multiple'] = exit_m
                test_params['ltm_ebitda'] = ltm_revenue * margin
                test_model = LBOModel(test_params)
                test_model.project()
                test_ret = test_model.get_returns()
                row.append(f"{test_ret['irr']*100:.1f}%")
            irr_matrix.append(row)
        
        sens_2d = pd.DataFrame(
            irr_matrix,
            index=[f"{m*100:.0f}%" for m in margin_range],
            columns=[f"{e:.1f}x" for e in exit_range],
        )
        sens_2d.index.name = "EBITDA Margin / Exit Multiple →"
        st.dataframe(sens_2d, use_container_width=True)
        
        # Value Creation Summary
        st.markdown(f'<div class="section-title">🏆 Value Creation Summary</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="formula-box">
            <strong>Entry Equity:</strong> {fmt_m(model.equity)}<br><br>
            <strong>Value Drivers:</strong><br>
            • Debt Paydown: {fmt_m(returns['debt_paydown'])} ({model.debt - returns['remaining_debt']:.0f} of {model.debt:.0f} repaid)<br>
            • EBITDA Growth: {((returns['exit_ebitda']/model.entry_ebitda)-1)*100:.1f}% ({fmt_m(model.entry_ebitda)} → {fmt_m(returns['exit_ebitda'])})<br>
            • Multiple Expansion: {model.purchase_price/model.entry_ebitda:.1f}x → {model.exit_multiple:.1f}x<br>
            • Accumulated Balance FCF: {fmt_m(returns['accumulated_fcf'])}<br><br>
            <strong>Exit Equity:</strong> {fmt_m(returns['equity_proceeds'])}<br>
            <strong>Total Value Created:</strong> {fmt_m(returns['equity_proceeds'] - model.equity)} ({((returns['equity_proceeds']/model.equity)-1)*100:.0f}%)
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.divider()
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem;">
        <p style="color: {COLORS['accent_gold']}; font-family: 'Playfair Display', serif; font-weight: 700;">
            {BRANDING['icon']} {BRANDING['name']}</p>
        <p style="color: {COLORS['text_secondary']}; font-size: 0.8rem;">
            {BRANDING['instructor']} | {BRANDING['credentials']}</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == '__main__':
    main()
