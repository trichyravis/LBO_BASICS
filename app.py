
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
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
        
        .metric-card {{
            background: {COLORS['card_bg']};
            border: 1px solid rgba(255,215,0,0.3);
            border-radius: 10px;
            padding: 1.2rem;
            text-align: center;
            margin-bottom: 0.8rem;
        }}

        .metric-card .value {{
            color: {COLORS['accent_gold']};
            font-size: 1.6rem;
            font-weight: 700;
            font-family: 'Playfair Display', serif;
        }}

        .formula-box {{
            background: rgba(0,51,102,0.5);
            border: 1px solid {COLORS['accent_gold']};
            border-radius: 8px;
            padding: 1rem 1.5rem;
            color: {COLORS['text_primary']};
            margin: 0.8rem 0;
        }}

        .fix-banner {{
            background: linear-gradient(90deg, #1a472a, #2d6a3e);
            border: 2px solid {COLORS['success']};
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1.5rem;
            color: white;
        }}
        
        .section-title {{
            font-family: 'Playfair Display', serif;
            color: {COLORS['accent_gold']};
            font-size: 1.3rem;
            border-bottom: 2px solid rgba(255,215,0,0.3);
            padding-bottom: 0.5rem;
            margin: 1.5rem 0 1rem;
        }}
    </style>
    """, unsafe_allow_html=True)

def fmt_m(value):
    return f"${value/1e6:,.1f}M"

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
        self.entry_ebitda = params['ltm_ebitda']

    def project(self):
        results = []
        current_debt = self.debt
        prev_revenue = self.p['ltm_revenue']
        accumulated_balance_fcf = 0.0
        
        for year in range(1, self.p['hold_years'] + 1):
            revenue = prev_revenue * (1 + self.p['revenue_growth'])
            ebitda = revenue * self.p['ebitda_margin']
            
            ebit = ebitda - self.p['depreciation']
            interest = current_debt * self.p['interest_rate']
            ebt = ebit - interest
            tax = max(0, ebt * self.p['tax_rate'])
            net_income = ebt - tax
            
            # Cash Flow Logic
            nwc_outflow = revenue * self.p['nwc_pct']
            fcf = net_income + self.p['depreciation'] - self.p['capex'] - nwc_outflow
            
            mandatory_repay = current_debt * self.p['mandatory_repay_pct']
            balance_fcf = fcf - mandatory_repay
            accumulated_balance_fcf += balance_fcf
            
            ending_debt = current_debt - mandatory_repay
            
            results.append({
                'Year': year,
                'Calendar_Year': 2024 + year,
                'Revenue': revenue,
                'EBITDA': ebitda,
                'Interest': interest,
                'Net_Income': net_income,
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
        if self.df is None: self.project()
        final = self.df.iloc[-1]
        
        exit_ev = final['EBITDA'] * self.p['exit_multiple']
        accumulated_fcf = final['Accumulated_Balance_FCF']
        remaining_debt = final['Ending_Debt']
        
        # EQUITY PROCEEDS = Exit Enterprise Value + Cash sitting on BS - Remaining Debt
        equity_proceeds = exit_ev + accumulated_fcf - remaining_debt
        
        moic = equity_proceeds / self.equity if self.equity > 0 else 0
        irr = (moic ** (1 / self.p['hold_years'])) - 1 if moic > 0 else 0
        
        return {
            'exit_ebitda': final['EBITDA'],
            'exit_ev': exit_ev,
            'accumulated_fcf': accumulated_fcf,
            'remaining_debt': remaining_debt,
            'equity_proceeds': equity_proceeds,
            'moic': moic,
            'irr': irr,
            'debt_paydown': self.debt - remaining_debt
        }

def main():
    st.set_page_config(**PAGE_CONFIG)
    apply_styles()
    
    # Header
    st.markdown(f"""<div class="header-container"><h1>{BRANDING['icon']} LBO Investment Model</h1>
                <p>{BRANDING['name']}</p></div>""", unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header("📋 Parameters")
    purchase_price = st.sidebar.number_input("Purchase Price", 100_000_000, step=1_000_000)
    debt_pct = st.sidebar.slider("Debt %", 40, 80, 60) / 100
    exit_multiple = st.sidebar.number_input("Exit Multiple", 5.0, 15.0, 8.0)
    hold_years = st.sidebar.slider("Hold Years", 3, 7, 5)
    
    rev_growth = st.sidebar.slider("Revenue Growth %", 0, 20, 5) / 100
    ebitda_margin = st.sidebar.slider("EBITDA Margin %", 10, 50, 25) / 100
    
    params = {
        'purchase_price': purchase_price,
        'fee_pct': 0.02,
        'debt_pct': debt_pct,
        'ltm_revenue': 100_000_000,
        'ltm_ebitda': 100_000_000 * ebitda_margin,
        'revenue_growth': rev_growth,
        'ebitda_margin': ebitda_margin,
        'tax_rate': 0.25,
        'capex': 5_000_000,
        'depreciation': 3_000_000,
        'nwc_pct': 0.01,
        'interest_rate': 0.07,
        'mandatory_repay_pct': 0.10,
        'exit_multiple': exit_multiple,
        'hold_years': hold_years
    }
    
    model = LBOModel(params)
    df = model.project()
    returns = model.get_returns()

    t1, t2, t3 = st.tabs(["Transaction", "Projections", "Returns"])
    
    with t1:
        st.markdown('<div class="section-title">Sources & Uses</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        col1.metric("Sponsor Equity", fmt_m(model.equity))
        col2.metric("Debt Raised", fmt_m(model.debt))
        st.dataframe(df[['Calendar_Year', 'Beginning_Debt', 'Ending_Debt']], use_container_width=True)

    with t2:
        st.markdown('<div class="section-title">Operating Projections</div>', unsafe_allow_html=True)
        st.dataframe(df.style.format(precision=0), use_container_width=True)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Calendar_Year'], y=df['EBITDA'], name="EBITDA", line=dict(color=COLORS['accent_gold'])))
        fig.update_layout(title="EBITDA Over Hold Period", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with t3:
        st.markdown('<div class="fix-banner"><b>Exit Equity Value</b> = Exit EV + Accumulated Cash - Debt</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.markdown(f'<div class="metric-card"><div class="value">{returns["moic"]:.2f}x</div><p>MOIC</p></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card"><div class="value">{returns["irr"]*100:.1f}%</div><p>IRR</p></div>', unsafe_allow_html=True)
        
        st.markdown(f"""<div class="formula-box">
            <b>Exit Waterfall:</b><br>
            Exit Enterprise Value: {fmt_m(returns['exit_ev'])}<br>
            + Total Cash Generated: {fmt_m(returns['accumulated_fcf'])}<br>
            - Debt Outstanding: {fmt_m(returns['remaining_debt'])}<br>
            = <b>Net Proceeds: {fmt_m(returns['equity_proceeds'])}</b>
        </div>""", unsafe_allow_html=True)

if __name__ == '__main__':
    main()
