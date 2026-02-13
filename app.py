
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

        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span {{
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
            font-family: 'Source Sans Pro', sans-serif;
        }}
        .metric-card .value {{
            color: {COLORS['accent_gold']};
            font-size: 1.6rem; font-weight: 700;
            font-family: 'Playfair Display', serif;
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
            color: {COLORS['text_primary']};
            margin: 0.8rem 0;
        }}

        footer {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

def fmt_m(value, decimals=1):
    if abs(value) >= 1e6:
        return f"${value / 1e6:,.{decimals}f}M"
    return f"${value:,.0f}"

# ============================================================================
# LBO MODEL ENGINE
# ============================================================================
class LBOModel:
    def __init__(self, params):
        self.p = params
        self.purchase_price = params['purchase_price']
        self.debt = params['purchase_price'] * params['debt_pct']
        self.equity = (self.purchase_price * (1 + params['fee_pct'])) - self.debt
        self.df = None

    def project(self):
        results = []
        current_debt = self.debt
        prev_rev = self.p['ltm_revenue']
        acc_bal_fcf = 0.0

        for year in range(1, self.p['hold_years'] + 1):
            rev = prev_rev * (1 + self.p['revenue_growth'])
            ebitda = rev * self.p['ebitda_margin']
            ebit = ebitda - self.p['depreciation']
            interest = current_debt * self.p['interest_rate']
            ebt = ebit - interest
            tax = max(0, ebt * self.p['tax_rate'])
            ni = ebt - tax
            
            fcf = ni + self.p['depreciation'] - self.p['capex'] - (rev * self.p['nwc_pct'])
            repay = current_debt * self.p['mandatory_repay_pct']
            bal_fcf = fcf - repay
            acc_bal_fcf += bal_fcf
            
            results.append({
                'Year': year,
                'Calendar_Year': 2024 + year - 1,
                'EBITDA': ebitda,
                'Ending_Debt': current_debt - repay,
                'Accumulated_Balance_FCF': acc_bal_fcf
            })
            current_debt -= repay
            prev_rev = rev

        self.df = pd.DataFrame(results)
        return self.df

    def get_returns(self):
        if self.df is None: self.project()
        final = self.df.iloc[-1]
        exit_ev = final['EBITDA'] * self.p['exit_multiple']
        equity_proceeds = exit_ev + final['Accumulated_Balance_FCF'] - final['Ending_Debt']
        moic = equity_proceeds / self.equity
        irr = (moic ** (1 / self.p['hold_years'])) - 1
        return {'exit_ev': exit_ev, 'acc_fcf': final['Accumulated_Balance_FCF'], 
                'rem_debt': final['Ending_Debt'], 'proceeds': equity_proceeds, 
                'moic': moic, 'irr': irr, 'exit_ebitda': final['EBITDA']}

def main():
    st.set_page_config(**PAGE_CONFIG)
    apply_styles()

    st.markdown(f'<div class="header-container"><h1>{BRANDING['icon']} LBO Investment Model</h1><p>{BRANDING['name']}</p></div>', unsafe_allow_html=True)

    # Sidebar
    st.sidebar.title("Model Inputs")
    price = st.sidebar.number_input("Purchase Price", 100_000_000, step=1_000_000)
    debt_p = st.sidebar.slider("Debt %", 40, 80, 60) / 100
    exit_m = st.sidebar.number_input("Exit Multiple", 5.0, 15.0, 10.0)
    hold = st.sidebar.selectbox("Hold Period", [3, 5, 7], index=1)

    params = {
        'purchase_price': price, 'fee_pct': 0.02, 'debt_pct': debt_p,
        'ltm_revenue': 100_000_000, 'ebitda_margin': 0.25, 'ltm_ebitda': 25_000_000,
        'revenue_growth': 0.05, 'tax_rate': 0.25, 'capex': 5_000_000,
        'depreciation': 3_000_000, 'nwc_pct': 0.01, 'interest_rate': 0.07,
        'mandatory_repay_pct': 0.10, 'exit_multiple': exit_m, 'hold_years': hold
    }

    model = LBOModel(params)
    model.project()
    ret = model.get_returns()

    tab1, tab2 = st.tabs(["📊 Projections", "🎯 Exit & Returns"])

    with tab1:
        st.markdown('<div class="section-title">Financial Summary</div>', unsafe_allow_html=True)
        st.dataframe(model.df, use_container_width=True)

    with tab2:
        st.markdown('<div class="section-title">Exit Waterfall</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.markdown(f'<div class="metric-card"><div class="label">MOIC</div><div class="value">{ret["moic"]:.2f}x</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card"><div class="label">IRR</div><div class="value">{ret["irr"]*100:.1f}%</div></div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="formula-box">
            <strong>Equity Value at Exit:</strong><br>
            Exit Enterprise Value: {fmt_m(ret['exit_ev'])}<br>
            + Accumulated Balance FCF: {fmt_m(ret['acc_fcf'])}<br>
            - Remaining Debt: {fmt_m(ret['rem_debt'])}<br>
            <hr>
            <strong>Total Equity Proceeds: {fmt_m(ret['proceeds'])}</strong>
        </div>
        """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
