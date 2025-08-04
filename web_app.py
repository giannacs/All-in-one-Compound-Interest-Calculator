import streamlit as st
import matplotlib.pyplot as plt

def compound_interest_with_monthly_net_rate(
    initial_investment,
    annual_interest_rate,
    annual_fee_rate,
    years,
    monthly_contribution,
    yearly_salary,
    employer_match_rate=0.0,
    employer_match_cap=0.0,
    annual_lump_sum=0.0
):
    # Monthly derived rates
    monthly_interest_rate = (1 + annual_interest_rate) ** (1 / 12) - 1
    monthly_fee_rate = (1 + annual_fee_rate) ** (1 / 12) - 1
    net_monthly_rate = (1 + monthly_interest_rate) * (1 - monthly_fee_rate) - 1

    # Employer match cap
    max_employer_annual_match = employer_match_rate * yearly_salary

    # Initialize balances
    balance_with_fees = initial_investment
    balance_without_fees = initial_investment

    # Track results
    balances = []
    total_employer_contrib = 0.0
    total_employee_contrib = 0.0

    for year in range(years):
        employer_match_accum = 0.0

        for month in range(12):
            # Employer match calculation
            potential_match = monthly_contribution * employer_match_cap
            remaining_match = max_employer_annual_match - employer_match_accum
            employer_match = min(potential_match, max(remaining_match, 0))
            employer_match_accum += employer_match

            # Total contribution this month
            total_contribution = monthly_contribution + employer_match

            # Apply contributions
            balance_with_fees += total_contribution
            balance_without_fees += total_contribution

            # Apply interest
            balance_with_fees *= (1 + net_monthly_rate)
            balance_without_fees *= (1 + monthly_interest_rate)

            # Track contributions
            total_employee_contrib += monthly_contribution
            total_employer_contrib += employer_match

        # Annual lump sum
        balance_with_fees += annual_lump_sum
        balance_without_fees += annual_lump_sum
        total_employee_contrib += annual_lump_sum

        balances.append(balance_with_fees)

    # Final calculations
    total_interest_earned = balance_with_fees - total_employee_contrib - total_employer_contrib
    total_fees_paid = balance_without_fees - balance_with_fees

    summary = {
        "total_employee_contributions": total_employee_contrib,
        "total_employer_contributions": total_employer_contrib,
        "total_interest_earned": total_interest_earned,
        "total_fees_paid": total_fees_paid,
        "final_balance": balance_with_fees,
        "final_balance_without_fees": balance_without_fees
    }

    return balances, summary


def format_currency(x):
    if x >= 1_000_000:
        return f'${x/1_000_000:.1f}M'
    elif x >= 1_000:
        return f'${x/1_000:.0f}K'
    return f'${x:.0f}'

def plot_compound_interest_streamlit(
    initial_investment,
    annual_interest_rate,
    annual_fee_rate,
    years,
    monthly_contribution,
    yearly_salary,
    employer_match_rate,
    employer_match_cap,
    annual_lump_sum
):
    with_fees, summary_with_fees = compound_interest_with_monthly_net_rate(
        initial_investment,
        annual_interest_rate,
        annual_fee_rate,
        years,
        monthly_contribution,
        yearly_salary,
        employer_match_rate,
        employer_match_cap,
        annual_lump_sum
    )
    without_fees, summary_without_fees = compound_interest_with_monthly_net_rate(
        initial_investment,
        annual_interest_rate,
        0.0,
        years,
        monthly_contribution,
        yearly_salary,
        employer_match_rate,
        employer_match_cap,
        annual_lump_sum
    )
    
    final_year = years
    balance_with_fees = with_fees[-1]
    balance_without_fees = without_fees[-1]
    diff = balance_without_fees - balance_with_fees
    mid_y = (balance_without_fees + balance_with_fees) / 2

    plt.figure(figsize=(10, 6))
    plt.plot(range(1, years + 1), with_fees, label='With Fees', color='tab:blue', linewidth=3)
    plt.plot(range(1, years + 1), without_fees, label='Without Fees', color='tab:orange', linewidth=3)

    plt.axvline(x=final_year, color='gray', linestyle='--', alpha=0.7)

    plt.text(final_year + final_year*0.01, balance_with_fees - balance_with_fees * 0.05, 
             f"{format_currency(balance_with_fees)}", 
             color='tab:blue', fontsize=14, va='center')

    plt.text(final_year - final_year*0.11, balance_without_fees + balance_without_fees * 0.01, 
             f"{format_currency(balance_without_fees)}", 
             color='tab:orange', fontsize=14, va='center')

    plt.annotate(
        '', 
        xy=(final_year + final_year*0.01, balance_without_fees), 
        xytext=(final_year + final_year*0.01, balance_with_fees),
        arrowprops=dict(arrowstyle='<->', color='black', lw=2)
    )
    plt.text(
        final_year + final_year*0.03, mid_y, 
        f"{format_currency(diff)}", 
        fontsize=14, color='red', 
        va='center', ha='left'
    )

    plt.title('Compound Interest Growth Over Time', fontsize=16)
    plt.xlabel('Years', fontsize=16)
    plt.ylabel('Balance', fontsize=16)
    plt.legend(fontsize=14)
    plt.grid(True)
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: format_currency(x)))
    plt.tight_layout()

    st.pyplot(plt.gcf())
    plt.clf()

    return summary_with_fees

def generate_text_summary(summary):
    return f"""
    **Investment Summary**

    - Final Balance: ${summary['final_balance']:,.2f}
    - Total Employee Contributions: ${summary['total_employee_contributions']:,.2f}
    - Total Employer Contributions: ${summary['total_employer_contributions']:,.2f}
    - Total Interest Earned: ${summary['total_interest_earned']:,.2f}
    - Total Fees Paid: ${summary['total_fees_paid']:,.2f}
    """

def main():
    # Optional: display an intro HTML block at the top
    description = r"""
    # Compound Interest Calculator 

    This calculator estimates the compounded growth of an investment over time, considering monthly contributions, employer matching, fees, and annual lump sum contributions. Relevant information about any combination of input parameters is summarized at the end. For any questions email me at: giannacs@mail.uc.edu 

    ---

    ### 1. Initial Parameters

    - **Initial Investment:** The starting amount of money invested, denoted as $P_0$.
    - **Annual Interest Rate:** The nominal yearly growth rate $ r $ (expressed as a decimal, e.g., 7% = 0.07).
    - **Annual Fee Rate:** The yearly fees or expenses ratio $ f $, deducted from returns.
    - **Years:** Total investment duration $ n $ years.
    - **Monthly Contribution:** The fixed amount $ C $ contributed every month.
    - **Yearly Salary:** $ S $, used to calculate employer match limits.
    - **Employer Match Rate:** Maximum percentage $ m $ of salary that employer will contribute annually (e.g., 5% = 0.05).
    - **Employer Match Cap:** Employer matches contributions dollar-for-dollar up to a fraction $ c $ per dollar contributed (e.g., 0.5 means 50 cents per $1 contributed).
    - **Annual Lump Sum:** Extra yearly one-time addition $ L $.

    ---

    ### 2. Monthly Rates

    The annual interest and fee rates are converted to monthly equivalents assuming compounding:

    $$
    r_{month} = (1 + r)^{\frac{1}{12}} - 1
    $$
    $$
    f_{month} = (1 + f)^{\frac{1}{12}} - 1
    $$

    The net monthly growth rate after fees is:

    $$
    r_{net} = (1 + r_{month})(1 - f_{month}) - 1
    $$

    ---

    ### 3. Employer Matching

    - Maximum employer annual contribution is:

    $$
    M = m \times S
    $$

    - Each month, employer matches employee contributions dollar-for-dollar up to cap $ c $:

    $$
    \text{Potential match} = c \times C
    $$

    - The actual monthly employer match is the lesser of potential match or remaining annual cap:

    $$
    \text{Employer match}_t = \min(\text{Potential match}, \max(M - \text{accumulated match}, 0))
    $$

    ---

    ### 4. Compound Interest Calculation (per month)

    Each month, the balance updates as follows:

    1. Add contributions:

    $$
    B_{t} = B_{t-1} + C + \text{Employer match}_t
    $$

    2. Apply net growth rate:

    $$
    B_{t} = B_{t} \times (1 + r_{net})
    $$

    ---

    ### 5. Annual Lump Sum

    At the end of each year, the annual lump sum $ L $ is added:

    $$
    B_{year} = B_{year} + L
    $$

    ---

    ### 6. Summary

    The calculator outputs:

    - Final balance after $ n $ years.
    - Total employee contributions.
    - Total employer contributions.
    - Total interest earned (net of fees).
    - Total fees paid.

    ---

    """

    st.markdown(description)

    st.title("Projected growth with and without fees")

    st.sidebar.header("Input Parameters")

    initial_investment = st.sidebar.number_input("Initial Investment ($)", value=10000, min_value=0, max_value=10000000 ,step=1000)
    annual_interest_rate_percent = st.sidebar.slider("Annual Interest Rate (%)", 0.0, 20.0, 7.0, 0.1)
    annual_fee_rate_percent = st.sidebar.slider("Annual Fee Rate (%)", 0.0, 5.0, 1.0, 0.01)
    years = st.sidebar.slider("Years", 10, 60, 30)
    monthly_contribution = st.sidebar.number_input("Monthly Contribution ($)", value=500, min_value=0, max_value=20000 ,step=50)
    yearly_salary = st.sidebar.number_input("Yearly Salary ($)", value=60000, min_value=20000, max_value=2000000 ,step=10000)
    employer_match_rate_percent = st.sidebar.slider("Employer Match Rate (% of salary)", 0.0, 20.0, 5.0, 0.1)
    employer_match_cap = st.sidebar.slider("Employer Match Cap (\\$  matched per \\$ contributed)", 0.0, 1.0, 0.5, 0.01)
    annual_lump_sum = st.sidebar.number_input("Annual Lump Sum Contribution ($)", value=5000, min_value=0, max_value=10000000 ,step=1000)

    # Convert to decimal fractions
    annual_interest_rate = annual_interest_rate_percent / 100
    annual_fee_rate = annual_fee_rate_percent / 100
    employer_match_rate = employer_match_rate_percent / 100

    summary = plot_compound_interest_streamlit(
        initial_investment,
        annual_interest_rate,
        annual_fee_rate,
        years,
        monthly_contribution,
        yearly_salary,
        employer_match_rate,
        employer_match_cap,
        annual_lump_sum
    )
    st.markdown(generate_text_summary(summary))



    



if __name__ == "__main__":
    main()
