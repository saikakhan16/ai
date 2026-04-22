"""
CrewAI Task Definitions (4-Agent Version)
Each task maps to one agent with a clear expected output.
Tasks are chained — later tasks receive context from earlier ones.
"""

from crewai import Task


def collect_rates_task(agent, user_input: dict) -> Task:
    return Task(
        description=f"""
        Fetch the current Fixed Deposit rates from all 8 Blostem partner banks
        and prepare structured data for optimization.
        
        User needs: {user_input.get('tenure_months', 12)}-month FD for ₹{user_input.get('amount', 1000000):,}
        
        Use the fetch_live_fd_rates and compare_bank_rates tools to:
        1. Get all bank rates
        2. Compare banks for the {user_input.get('tenure_months', 12)}-month tenure
        3. Highlight top 3 banks
        4. Note DICGC insurance status
        """,
        expected_output="""
        Structured JSON with:
        - All 8 banks and their FD rates
        - Ranked comparison for requested tenure
        - DICGC insurance status
        - Top 3 recommended banks
        """,
        agent=agent
    )


def optimize_portfolio_task(agent, user_input: dict, context: list) -> Task:
    return Task(
        description=f"""
        Run PSO algorithm to find optimal FD allocation across all 8 banks.
        
        Parameters:
        - Total Amount: ₹{user_input.get('amount', 1000000):,}
        - Risk Profile: {user_input.get('risk_profile', 'moderate')}
        - Tenure: {user_input.get('tenure_months', 12)} months
        
        Use run_pso_optimization to:
        1. Allocate funds across banks
        2. Ensure DICGC compliance (max ₹5L per bank)
        3. Respect risk limits
        4. Calculate expected returns
        """,
        expected_output="""
        Optimization result with:
        - Allocation: amount + weight % per bank
        - Expected interest per bank
        - Total maturity amount
        - Effective annual return %
        - DICGC compliance status
        - FD ladder strategy
        """,
        agent=agent,
        context=context
    )


def comparison_task(agent, user_input: dict, context: list) -> Task:
    """Task for the FD vs Alternatives Comparator Agent."""
    return Task(
        description=f"""
        Compare Fixed Deposits against alternative investment instruments.

        User profile:
        - Tax slab: {user_input.get('tax_slab_pct', 30)}%
        - Tenure: {user_input.get('tenure_months', 12)} months
        - Risk profile: {user_input.get('risk_profile', 'moderate')}
        - Investment amount: Rs{user_input.get('amount', 1000000):,}

        Use the compare_investment_alternatives tool to:
        1. Calculate pre-tax and post-tax returns for FD, Debt MF, SGB, RD, PPF
        2. Fetch current CPI inflation for real-return calculation (fallback 5.5%)
        3. Score each instrument on risk (1-10) and liquidity (1-10)
        4. Generate a comparison table and a personalised allocation recommendation
        """,
        expected_output="""
        Comparison table showing all 5 instruments with:
        - Pre-tax returns
        - Post-tax returns at user's slab
        - Inflation-adjusted real returns
        - Risk score (1-10) and Liquidity score (1-10)
        - Allocation recommendation with instruments to avoid
        """,
        agent=agent,
        context=context,
    )


def user_advisory_task(agent, user_input: dict, context: list) -> Task:
    name = user_input.get("name", "there")
    return Task(
        description=f"""
        Create final portfolio report for {name}.
        
        Synthesize optimization results into clear, actionable report:
        - Name: {name}
        - Investment: ₹{user_input.get('amount', 1000000):,}
        - Risk appetite: {user_input.get('risk_profile', 'moderate')}
        - Tenure: {user_input.get('tenure_months', 12)} months
        
        Use generate_portfolio_report to:
        1. Structure the full report
        2. Add personal greeting for {name}
        3. Show allocation table (bank | amount | rate | maturity)
        4. List 3 clear action steps
        5. Keep tone warm, jargon-free
        """,
        expected_output=f"""
        Complete personalized report for {name} with:
        1. Personal greeting
        2. Portfolio summary & allocation table
        3. Tax summary
        4. 3 clear action steps
        5. Bottom-line summary
        """,
        agent=agent,
        context=context
    )
