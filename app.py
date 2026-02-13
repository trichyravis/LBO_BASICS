
"""
LBO Investment Model - MILLIONS VERSION
The Mountain Path - World of Finance
Prof. V. Ravichandran

All monetary inputs are entered in MILLIONS.
Internally scaled to full dollar values.
"""

import streamlit as st
import pandas as pd
import numpy as np

# ============================================================================
# SCALING (ALL VALUES ENTERED IN MILLIONS)
# ============================================================================
SCALE = 1_000_000  # User inputs treated as millions


# ============================================================================
# HELPER FORMAT FUNCTION
# ============================================================================
def fmt_m(value, decimals=1):
    """Format as millions"""
    return f"${value / 1_000_000:,.{decimals}f}M"


# ============================================================================
# LBO MODEL ENGINE
# ============================================================================
class LBOModel:
    def __init__(self, params):
        self.p = params
        self.df = None

        self.purchase_price = params['purchase_price']
        self.fees = self.purchase_price * params['fee_pct']
        self.total_cost = self.purchase_price + self.fees
        self.debt = self.purchase_price * params['debt_pct']
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
                'Revenue': revenue,
                'EBITDA': ebitda,
                'Net_Income': net_income,
                'Levered_FCF': fcf,
                'Balance_FCF': balance_fcf,
                'Accumulated_FCF': accumulated_balance_fcf,
                'Beginning_Debt': current_debt,
                'Ending_Debt': ending_debt,
            })

            current_debt = ending_debt
            prev_revenue = revenue

        self.df = pd.DataFrame(results)
        return self.df

    def get_returns(self):
        final = self.df.iloc[-1]

        exit_ebitda = final['EBITDA']
        exit_ev = exit_ebitda * self.exit_multiple
        accumulated_fcf = final['Accumulated_FCF']
        remaining_debt = final['Ending_Debt']

        equity_proceeds = exit_ev + accumulated_fcf - remaining_debt

        moic = equity_proceeds / self.equity
        irr = (moic ** (1 / self.hold_years)) - 1

        return {
            'exit_ev': exit_ev,
            'equity_proceeds': equity_proceeds,
            'moic': moic,
            'irr': irr,
        }


# ============================================================================
# MAIN APP
# ============================================================================
def main():
    st.set_page_config(page_title="LBO Model (Millions)", layout="wide")

    st.title("🏔️ LBO Investment Model (All Inputs in Millions)")

    # Sidebar Inputs
    purchase_price = st.sidebar.number_input("Purchase Price (in millions)", value=100, step=10)
    fee_pct = st.sidebar.slider("Fees (%)", 1.0, 10.0, 2.0) / 100
    debt_pct = st.sidebar.slider("Debt (%)", 40.0, 80.0, 60.0) / 100
    exit_multiple = st.sidebar.number_input("Exit Multiple", value=10.0)
    hold_years = st.sidebar.selectbox("Holding Period", [3,4,5,6], index=2)

    ltm_revenue = st.sidebar.number_input("LTM Revenue (in millions)", value=100, step=10)
    ebitda_margin = st.sidebar.slider("EBITDA Margin (%)", 10.0, 50.0, 25.0) / 100
    revenue_growth = st.sidebar.slider("Revenue Growth (%)", 1.0, 20.0, 5.0) / 100
    tax_rate = st.sidebar.slider("Tax Rate (%)", 15.0, 35.0, 25.0) / 100
    capex = st.sidebar.number_input("CapEx (in millions)", value=5, step=1)
    depreciation = st.sidebar.number_input("Depreciation (in millions)", value=3, step=1)
    nwc_pct = st.sidebar.slider("NWC (% of Revenue)", -5.0, 5.0, -1.0) / 100

    interest_rate = st.sidebar.slider("Interest Rate (%)", 3.0, 12.0, 7.0) / 100
    mandatory_repay_pct = st.sidebar.slider("Mandatory Repayment (%)", 5.0, 20.0, 10.0) / 100

    ltm_ebitda = ltm_revenue * ebitda_margin

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
    df = model.project()
    returns = model.get_returns()

    st.subheader("Projection Table")
    display_df = df.copy()
    for col in display_df.columns:
        if col != "Year":
            display_df[col] = display_df[col].apply(fmt_m)
    st.dataframe(display_df)

    st.subheader("Exit & Returns")
    st.metric("Exit Enterprise Value", fmt_m(returns['exit_ev']))
    st.metric("Equity Value at Exit", fmt_m(returns['equity_proceeds']))
    st.metric("MOIC", f"{returns['moic']:.2f}x")
    st.metric("IRR", f"{returns['irr']*100:.1f}%")


if __name__ == "__main__":
    main()
