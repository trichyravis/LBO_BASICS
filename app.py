
"""
LBO Investment Model - Verified & Corrected
The Mountain Path - World of Finance
Prof. V. Ravichandran

CRITICAL FIX: Return calculation now correctly adds Sum of Balance FCF
Equity Value at Exit = Exit EV + Accumulated Balance FCF - Remaining Debt

UPDATED: All monetary inputs are entered in MILLIONS.
ZERO external chart libraries - uses only Streamlit native components
"""

import streamlit as st
import pandas as pd
import numpy as np

# ============================================================================
# SCALING (NEW - ALL VALUES ENTERED IN MILLIONS)
# ============================================================================
SCALE = 1_000_000  # User inputs treated as millions


# ============================================================================
# BRANDING & STYLING (UNCHANGED)
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

# ================= FORMAT =================
def fmt_m(value, decimals=1):
    if abs(value) >= 1e6:
        return f"${value / 1e6:,.{decimals}f}M"
    else:
        return f"${value:,.0f}"


# ============================================================================
# LBO MODEL ENGINE (UNCHANGED)
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

    # ========= SIDEBAR INPUTS (UPDATED TO MILLIONS) =========

    purchase_price = st.sidebar.number_input(
        "Purchase Price (in millions)", value=100, step=10, format="%d"
    )

    fee_pct = st.sidebar.slider("Fees & Expenses (%)", 1.0, 10.0, 2.0, 0.5) / 100
    debt_pct = st.sidebar.slider("Debt / Purchase Price (%)", 40.0, 80.0, 60.0, 5.0) / 100
    exit_multiple = st.sidebar.number_input("Exit EBITDA Multiple", value=10.0, step=0.5, format="%.1f")
    hold_years = st.sidebar.selectbox("Holding Period (Years)", [3, 4, 5, 6, 7], index=2)

    ltm_revenue = st.sidebar.number_input(
        "LTM Revenue (in millions)", value=100, step=10, format="%d"
    )

    ebitda_margin = st.sidebar.slider("EBITDA Margin (%)", 10.0, 50.0, 25.0, 1.0) / 100
    revenue_growth = st.sidebar.slider("Revenue Growth (%)", 1.0, 20.0, 5.0, 0.5) / 100
    tax_rate = st.sidebar.slider("Tax Rate (%)", 15.0, 35.0, 25.0, 1.0) / 100

    capex = st.sidebar.number_input(
        "Annual CapEx (in millions)", value=5, step=1, format="%d"
    )

    depreciation = st.sidebar.number_input(
        "Annual Depreciation (in millions)", value=3, step=1, format="%d"
    )

    nwc_pct = st.sidebar.slider("NWC Change (% of Revenue)", -5.0, 5.0, -1.0, 0.5) / 100
    interest_rate = st.sidebar.slider("Interest Rate (%)", 3.0, 12.0, 7.0, 0.5) / 100
    mandatory_repay_pct = st.sidebar.slider("Mandatory Repayment (%)", 5.0, 20.0, 10.0, 1.0) / 100

    ltm_ebitda = ltm_revenue * ebitda_margin

    # ========= APPLY SCALING =========
    params = {
        'purchase_price': purchase_price * SCALE,
        'fee_pct': fee_pct,
        'debt_pct': debt_pct,
        'ltm_revenue': ltm_revenue * SCALE,
        'ltm_ebitda': ltm_ebitda * SCALE,
        'ebitda_margin': ebitda_margin,
        'revenue_growth': revenue_growth,
        'tax_rate': tax_rate,
        'capex': capex * SCALE,
        'depreciation': depreciation * SCALE,
        'nwc_pct': nwc_pct,
        'interest_rate': interest_rate,
        'mandatory_repay_pct': mandatory_repay_pct,
        'exit_multiple': exit_multiple,
        'hold_years': hold_years,
    }

    model = LBOModel(params)
    model.project()
    returns = model.get_returns()

    st.title("🏔️ LBO Investment Model (All Inputs in Millions)")
    st.metric("MOIC", f"{returns['moic']:.2f}x")
    st.metric("IRR", f"{returns['irr']*100:.1f}%")
    st.metric("Equity Value at Exit", fmt_m(returns['equity_proceeds']))


if __name__ == '__main__':
    main()
