"""
FD Portfolio Optimizer — Command Line Interface
Interactive terminal tool for portfolio optimization
"""

import sys
import json
from datetime import datetime
from pathlib import Path
import argparse

from simple_main import run_fd_optimizer


def print_header(title: str):
    """Print styled header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_section(title: str):
    """Print section header"""
    print(f"\n{title}")
    print("-" * 70)


def get_amount() -> float:
    """Get investment amount with validation"""
    while True:
        try:
            amount_str = input("Enter investment amount (Rs): ₹ ").strip()
            amount = float(amount_str)
            if amount < 100000:
                print("  ERROR: Minimum investment is Rs 1 Lakh (100,000)")
                continue
            if amount > 100000000:
                print("  ERROR: Maximum investment is Rs 10 Crore (100,000,000)")
                continue
            return amount
        except ValueError:
            print("  ERROR: Please enter a valid number")


def get_tenure() -> int:
    """Get tenure with validation"""
    valid_tenures = [3, 6, 9, 12, 18, 24]
    print("\nSelect tenure (months):")
    for i, t in enumerate(valid_tenures, 1):
        print(f"  {i}. {t} months")
    
    while True:
        try:
            choice = int(input("  Choose option (1-6): ").strip())
            if 1 <= choice <= 6:
                return valid_tenures[choice - 1]
            print("  ERROR: Please enter 1-6")
        except ValueError:
            print("  ERROR: Please enter a number")


def get_risk_profile() -> str:
    """Get risk profile with validation"""
    profiles = {
        "1": "conservative",
        "2": "moderate",
        "3": "aggressive"
    }
    
    print("\nSelect risk profile:")
    print("  1. Conservative (low risk, lower returns)")
    print("  2. Moderate (balanced risk/return)")
    print("  3. Aggressive (high risk, higher returns)")
    
    while True:
        choice = input("  Choose option (1-3): ").strip()
        if choice in profiles:
            return profiles[choice]
        print("  ERROR: Please enter 1, 2, or 3")


def get_name() -> str:
    """Get investor name"""
    name = input("\nEnter your name (optional, press Enter for 'Investor'): ").strip()
    return name if name else "Investor"


def save_report(report: str, name: str) -> str:
    """Save report to file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"fd_portfolio_report_{timestamp}.txt"
    filepath = Path(filename)
    
    try:
        filepath.write_text(report)
        print(f"\n  Report saved to: {filepath.absolute()}")
        return str(filepath)
    except Exception as e:
        print(f"  WARNING: Could not save report: {e}")
        return ""


def interactive_mode():
    """Interactive CLI mode"""
    print_header("FD PORTFOLIO OPTIMIZER - Interactive Mode")
    
    print("This tool optimizes your Fixed Deposit allocation across 8 banks")
    print("using a Particle Swarm Optimization algorithm.\n")
    
    # Get user inputs
    print_section("STEP 1: Investment Amount")
    amount = get_amount()
    print(f"  Selected: Rs {amount:,.0f}")
    
    print_section("STEP 2: Investment Tenure")
    tenure = get_tenure()
    print(f"  Selected: {tenure} months")
    
    print_section("STEP 3: Risk Profile")
    risk_profile = get_risk_profile()
    print(f"  Selected: {risk_profile.upper()}")
    
    print_section("STEP 4: Your Name")
    name = get_name()
    print(f"  Hello {name}!")
    
    # Run optimization
    print_section("STEP 5: Running PSO Optimization")
    print("  Processing... This may take 10-30 seconds\n")
    
    try:
        user_input = {
            "amount": amount,
            "risk_profile": risk_profile,
            "tenure_months": tenure,
            "name": name
        }
        
        report = run_fd_optimizer(user_input)
        
        # Display report
        print_section("YOUR PORTFOLIO RECOMMENDATION")
        print(report)
        
        # Option to save
        print_section("Save Report?")
        save_choice = input("Save report to file? (y/n): ").strip().lower()
        if save_choice == "y":
            save_report(report, name)
        
        print("\n" + "=" * 70)
        print("  Thank you for using FD Portfolio Optimizer!")
        print("=" * 70 + "\n")
        
        return True
    
    except Exception as e:
        print(f"\n  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def quick_mode(args):
    """Quick mode with command-line arguments"""
    user_input = {
        "amount": args.amount,
        "risk_profile": args.risk_profile,
        "tenure_months": args.tenure,
        "name": args.name
    }
    
    print_header("FD PORTFOLIO OPTIMIZER - Quick Mode")
    print(f"Amount: Rs {args.amount:,}")
    print(f"Risk: {args.risk_profile}")
    print(f"Tenure: {args.tenure} months")
    print(f"Name: {args.name}\n")
    
    try:
        report = run_fd_optimizer(user_input)
        print(report)
        
        if args.save:
            save_report(report, args.name)
        
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="FD Portfolio Optimizer - Allocate funds across 8 banks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py                                  # Interactive mode
  python cli.py --amount 1000000 --risk moderate # Quick mode
  python cli.py --amount 500000 --tenure 18 --save  # Quick + save report
        """
    )
    
    parser.add_argument(
        "--amount",
        type=float,
        default=None,
        help="Investment amount (Rs)"
    )
    parser.add_argument(
        "--risk",
        "--risk-profile",
        dest="risk_profile",
        choices=["conservative", "moderate", "aggressive"],
        default="moderate",
        help="Risk profile (default: moderate)"
    )
    parser.add_argument(
        "--tenure",
        type=int,
        choices=[3, 6, 9, 12, 18, 24],
        default=12,
        help="Tenure in months (default: 12)"
    )
    parser.add_argument(
        "--name",
        default="Investor",
        help="Investor name (default: Investor)"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save report to file"
    )
    
    args = parser.parse_args()
    
    # Determine mode
    if args.amount is None:
        # Interactive mode
        success = interactive_mode()
    else:
        # Quick mode with arguments
        success = quick_mode(args)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
