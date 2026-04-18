"""
CrewAI Task Definitions
Each task maps to one agent with a clear expected output.
Tasks are chained — later tasks receive context from earlier ones.
"""

from crewai import Task


def collect_rates_task(agent, user_input: dict) -> Task:
    return Task(
        description=f"""
        Fetch the current Fixed Deposit rates from all 8 Blostem partner banks.
        
        User needs: {user_input.get('tenure_months', 12)}-month FD for ₹{user_input.get('amount', 1000000):,}
        
        Steps:
        1. Use FetchLiveFDRates tool to get all bank rates
        2. Use CompareBankRates tool for the {user_input.get('tenure_months', 12)}-month tenure
        3. Highlight the top 3 banks for this tenure
        4. Note which banks are DICGC insured vs NBFC
        
        Deliver clean, structured data ready for the optimization engine.
        """,
        expected_output="""
        A structured JSON report containing:
        - All 8 banks with their FD rates for all tenures
        - A ranked comparison for the requested tenure
        - DICGC insurance status for each bank
        - Top 3 recommended banks for the requested tenure
        """,
        agent=agent
    )


def analyze_market_task(agent, user_input: dict) -> Task:
    return Task(
        description=f"""
        Analyze the current RBI monetary policy environment and provide
        a clear investment timing signal for FD booking.
        
        The user wants to invest ₹{user_input.get('amount', 1000000):,} for {user_input.get('tenure_months', 12)} months.
        
        Steps:
        1. Use GetRBIRateAnalysis to get current rate cycle status
        2. Use GetMacroIndicators for supporting economic data
        3. Determine: Should the user book NOW or WAIT?
        4. Recommend the optimal tenure based on rate outlook
        5. Identify 2-3 key risks to monitor
        
        Be decisive. Give a clear BOOK NOW / WAIT signal with confidence level.
        """,
        expected_output="""
        A market intelligence report containing:
        - Clear BUY/HOLD signal (Book Now or Wait)
        - Confidence percentage
        - RBI rate outlook for next 3, 6, 12 months  
        - Recommended tenure to maximize rate-lock advantage
        - Top 3 risk factors to watch
        - One-paragraph plain English summary
        """,
        agent=agent
    )


def optimize_portfolio_task(agent, user_input: dict, context: list) -> Task:
    return Task(
        description=f"""
        Run the Particle Swarm Optimization algorithm to find the optimal 
        FD allocation across all 8 banks.
        
        Parameters:
        - Total Amount: ₹{user_input.get('amount', 1000000):,}
        - Risk Profile: {user_input.get('risk_profile', 'moderate')}
        - Tenure: {user_input.get('tenure_months', 12)} months
        
        Steps:
        1. Use RunPSOOptimization tool with the above parameters
        2. Ensure DICGC compliance (max ₹5L per bank)
        3. Apply risk concentration limits:
           - Conservative: max 20% per bank
           - Moderate: max 35% per bank  
           - Aggressive: max 50% per bank
        4. Use BuildFDLadder tool to create the liquidity ladder
        5. Calculate total expected returns and maturity amounts
        
        The PSO must run 60 particles for 200 iterations minimum.
        """,
        expected_output="""
        Complete optimization result containing:
        - Allocation breakdown: amount + weight % per bank
        - Expected interest earned per bank
        - Total maturity amount
        - Effective annual return %
        - PSO fitness score
        - DICGC compliance status
        - FD ladder strategy (3M/6M/9M/12M rungs)
        """,
        agent=agent,
        context=context
    )


def tax_compliance_task(agent, user_input: dict, context: list) -> Task:
    return Task(
        description=f"""
        Analyze the tax implications and compliance requirements for the 
        optimized FD portfolio.
        
        Investment: ₹{user_input.get('amount', 1000000):,}
        
        Steps:
        1. Use CalculateTDSAndTax with the portfolio's expected return
        2. Use VerifyDICGCCompliance on the allocation from the PSO agent
        3. Determine if Form 15G or 15H is needed
        4. Calculate post-tax returns for 0%, 20%, and 30% tax brackets
        5. Provide 3-5 specific tax optimization tips
        
        Be precise about amounts. Give actionable steps, not generic advice.
        """,
        expected_output="""
        Tax and compliance report containing:
        - TDS applicability (yes/no) and estimated TDS amount
        - Net interest after TDS
        - Post-tax returns for each tax bracket
        - Forms to submit (15G/15H) with deadlines
        - DICGC compliance verification
        - 3-5 specific tax optimization actions
        """,
        agent=agent,
        context=context
    )


def user_advisory_task(agent, user_input: dict, context: list) -> Task:
    name = user_input.get("name", "there")
    return Task(
        description=f"""
        Create the final portfolio report for {name}.
        
        Synthesize ALL outputs from the previous agents into one clear, 
        friendly, actionable report. The user's profile:
        - Name: {name}
        - Investment: ₹{user_input.get('amount', 1000000):,}
        - Risk appetite: {user_input.get('risk_profile', 'moderate')}
        - Tenure: {user_input.get('tenure_months', 12)} months
        
        Steps:
        1. Use GeneratePortfolioReport to structure the full report
        2. Use SimplifyForUser to add a plain-language summary
        3. Combine market intelligence, optimization results, and tax advice
        4. Write a warm, personalized opening paragraph for {name}
        5. Include: what to do TODAY (3 clear action steps)
        
        Avoid jargon. Be like a trusted financial advisor talking to a friend.
        Keep numbers clear — show ₹ amounts prominently.
        """,
        expected_output=f"""
        A complete, personalized FD investment report for {name} containing:
        
        1. Personal greeting and portfolio summary
        2. Market timing verdict (why NOW is the right time)
        3. Full allocation table (bank | amount | rate | maturity)
        4. FD ladder schedule (which FD matures when)
        5. Tax summary (TDS, forms needed, estimated savings)
        6. 3 clear action steps to execute today
        7. One-paragraph plain English "bottom line"
        
        Tone: warm, confident, jargon-free. Like a brilliant friend who happens 
        to know everything about Indian fixed income markets.
        """,
        agent=agent,
        context=context
    )
