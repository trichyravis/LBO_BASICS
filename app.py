
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
        .stApp {{ background: linear-gradient(135deg, {COLORS['bg_dark']} 0%, {COLORS['dark_blue']} 50%, #0d2137 100%); }}
        section[data-testid="stSidebar"] {{ background: linear-gradient(180deg, {COLORS['bg_dark']} 0%, {COLORS['dark_blue']} 100%); border-right: 1px solid rgba(255,215,0,0.2); }}
        section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span {{ color: {COLORS['text_primary']} !important; }}
        section[data-testid="stSidebar"] input {{ color: #1a1a2e !important; background-color: #ffffff !important; }}
        .header-container {{ background: linear-gradient(135deg, {COLORS['dark_blue']}, {COLORS['medium_blue']}); border: 2px solid {COLORS['accent_gold']}; border-radius: 12px; padding: 1.5rem 2rem; margin-bottom: 1.5rem; text-align: center; }}
        .header-container h1 {{ font-family: 'Playfair Display', serif; color: {COLORS['accent_gold']}; margin: 0; font-size: 2rem; }}
        .metric-card {{ background: {COLORS['card_bg']}; border: 1px solid rgba(255,215,0,0.3); border-radius: 10px; padding: 1.2rem; text-align: center; margin-bottom: 0.8rem; }}
        .metric-card .value {{ color: {COLORS['accent_gold']}; font-size: 1.6rem; font-weight: 700; font-family: 'Playfair Display', serif; }}
        .formula-box {{ background: rgba(0,51,102,0.5); border: 1px solid {COLORS['accent_gold']}; border-radius: 8px; padding: 1rem 1.5rem; color: {COLORS['text_primary']}; margin: 0.8rem 0; }}
        .section-title {{ font-family: 'Playfair Display', serif; color: {COLORS['accent_gold']}; font-size: 1.3rem; border-bottom: 2px solid rgba(255,215,0,0.3); padding-bottom: 0.5rem; margin: 1.5rem 0 1rem; }}
        footer {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

def fmt_m(value, decimals=1):
    if abs(value) >= 1e6: return f"${value / 1e6:,.{decimals}f}M"
    return f"${value:,.0f}"

# ============================================================================
# LBO MODEL ENGINE
# ============================================================================
class LBOModel:
    def __init__(self, params):
        self.p = params
        self.purchase_price = params['purchase_price']
        self.fees = params['purchase_price'] * params['fee_pct']
        self.total_cost = self.purchase_price + self.fees
        self.debt = params['purchase_price'] * params['debt_pct']
        self.equity = self.total_cost - self.debt

    def project(self):
        results = []
        current_debt = self.debt
        prev_rev = self.p['ltm_revenue']
        acc_bal_fcf = 0.0
        for year in range(1, self.p['hold_years'] + 1):
            rev = prev_rev * (1 + self.p['revenue_growth'])
            ebitda = rev * self.p['ebitda_margin']
            ni = (ebitda - self.p['depreciation'] - (current_debt * self.p['interest_rate'])) * (1 - self.p['tax_rate'])
            fcf = ni + self.p['depreciation'] - self.p['capex'] - (rev * self.p['nwc_pct'])
            repay = current_debt * self.p['mandatory_repay_pct']
            bal_fcf = fcf - repay
            acc_bal_fcf += bal_fcf
            
            results.append({
                'Year': year,
                'Revenue': rev,
                'EBITDA': ebitda,
                'FCF': fcf,
                'Debt_Repayment': repay,
                'Ending_Debt': current_debt - repay,
                'Accumulated_Cash': acc_bal_fcf
            })
            current_debt -= repay
            prev_rev = rev
        self.df = pd.DataFrame(results)
        return self.df

    def get_returns(self):
        if self.df is None: self.project()
        final = self.df.iloc[-1]
        exit_ev = final['EBITDA'] * self.p['exit_multiple']
        # CORRECTED FORMULA: Proceeds = Exit EV + Cash - Remaining Debt
        proceeds = exit_ev + final['Accumulated_Cash'] - final['Ending_Debt']
        moic = proceeds / self.equity if self.equity > 0 else 0
        irr = (moic ** (1 / self.p['hold_years'])) - 1 if moic > 0 else 0
        return {'moic': moic, 'irr': irr, 'exit_ev': exit_ev, 'acc_fcf': final['Accumulated_Cash'], 'debt': final['Ending_Debt'], 'ebitda': final['EBITDA']}

def main():
    st.set_page_config(**PAGE_CONFIG)
    apply_styles()
    st.markdown(f'<div class="header-container"><h1>{BRANDING["icon"]} LBO Investment Model</h1><p>{BRANDING["name"]}</p></div>', unsafe_allow_html=True)

    # Sidebar Inputs in '000s
    st.sidebar.markdown(f"<p style='color:{COLORS['accent_gold']}; font-weight:700;'>📋 Transaction (in '000s)</p>", unsafe_allow_html=True)
    price_k = st.sidebar.number_input("Purchase Price", value=100_000, step=1_000)
    debt_p = st.sidebar.slider("Debt %", 40, 80, 60) / 100
    exit_m_input = st.sidebar.number_input("Exit Multiple", value=10.0, step=0.5)
    
    st.sidebar.markdown(f"<p style='color:{COLORS['accent_gold']}; font-weight:700;'>📊 Operating (in '000s)</p>", unsafe_allow_html=True)
    rev_k = st.sidebar.number_input("LTM Revenue", value=100_000, step=1_000)
    growth_p = st.sidebar.slider("Revenue Growth (%)", 1.0, 15.0, 5.0) / 100
    capex_k = st.sidebar.number_input("Annual CapEx", value=5_000)
    dep_k = st.sidebar.number_input("Annual Depreciation", value=3_000)

    params = {
        'purchase_price': price_k * 1000, 'fee_pct': 0.02, 'debt_pct': debt_p,
        'ltm_revenue': rev_k * 1000, 'ebitda_margin': 0.25, 'revenue_growth': growth_p,
        'tax_rate': 0.25, 'capex': capex_k * 1000, 'depreciation': dep_k * 1000, 'nwc_pct': 0.01,
        'interest_rate': 0.07, 'mandatory_repay_pct': 0.10, 'exit_multiple': exit_m_input, 'hold_years': 5
    }

    model = LBOModel(params)
    df_res = model.project()
    ret = model.get_returns()

    tab1, tab2, tab3, tab4 = st.tabs(["📋 Summary", "📊 Projections", "🎯 Returns", "📈 Sensitivity"])

    with tab1:
        st.markdown('<div class="section-title">Transaction Overview</div>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Purchase Price", fmt_m(model.purchase_price))
        col2.metric("Total Debt", fmt_m(model.debt))
        col3.metric("Sponsor Equity", fmt_m(model.equity))
        col4.metric("Entry EV/EBITDA", f"{model.purchase_price / (rev_k * 1000 * 0.25):.1f}x")

    with tab2:
        st.markdown('<div class="section-title">Projected Cash Flows</div>', unsafe_allow_html=True)
        st.dataframe(df_res.style.format(precision=0), use_container_width=True)
        st.download_button("📥 Download CSV", df_res.to_csv(index=False), "lbo_model_export.csv")

    with tab3:
        st.markdown('<div class="section-title">Exit Waterfall</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.markdown(f'<div class="metric-card"><div class="label">MOIC</div><div class="value">{ret["moic"]:.2f}x</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card"><div class="label">IRR</div><div class="value">{ret["irr"]*100:.1f}%</div></div>', unsafe_allow_html=True)
        
        st.markdown(f"""<div class="formula-box">
            <b>Net Proceeds Calculation:</b><br>
            Exit Enterprise Value: {fmt_m(ret['exit_ev'])}<br>
            + Accumulated Cash: {fmt_m(ret['acc_fcf'])}<br>
            - Remaining Debt: {fmt_m(ret['debt'])}<br>
            <hr>
            <b>Net Equity Proceeds: {fmt_m(ret['proceeds'])}</b>
        </div>""", unsafe_allow_html=True)

    with tab4:
        st.markdown('<div class="section-title">IRR Sensitivity Matrix</div>', unsafe_allow_html=True)
        m_range = [exit_m_input + i*0.5 for i in range(-2, 3)]
        g_range = [growth_p + i*0.01 for i in range(-2, 3)]
        
        sens_data = []
        for g in g_range:
            row = []
            for m in m_range:
                s_params = params.copy()
                s_params.update({'revenue_growth': g, 'exit_multiple': m})
                s_model = LBOModel(s_params)
                s_model.project()
                row.append(f"{s_model.get_returns()['irr']*100:.1f}%")
            sens_data.append(row)
            
        sens_df = pd.DataFrame(sens_data, index=[f"{g*100:.1f}% Growth" for g in g_range], 
                               columns=[f"{m:.1f}x Exit" for m in m_range])
        st.table(sens_df)

if __name__ == '__main__':
    main()
