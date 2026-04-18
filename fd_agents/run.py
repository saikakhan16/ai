#!/usr/bin/env python3
"""
FD Portfolio Optimizer — Setup & Launcher
Initializes environment and offers menu to run API, CLI, or direct optimization
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from dotenv import load_dotenv


def print_banner():
    """Print ASCII banner"""
    print("""
    ╔═════════════════════════════════════════════════════════════════════╗
    ║                                                                       ║
    ║          FD PORTFOLIO OPTIMIZER — v3.0                              ║
    ║          Fixed Deposit Allocation across 8 Indian Banks              ║
    ║          Powered by Groq (Llama 3.3 70B) + PSO Algorithm            ║
    ║                                                                       ║
    ╚═════════════════════════════════════════════════════════════════════╝
    """)


def check_env_file():
    """Check and setup .env file"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("  [!] .env file not found")
            print("  [*] Creating .env from .env.example...")
            env_file.write_text(env_example.read_text())
            print("  [OK] Created .env")
        else:
            print("  [ERROR] Neither .env nor .env.example found!")
            return False
    
    # Load and verify
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    
    if not api_key or api_key == "your_groq_api_key_here":
        print("\n  [!] GROQ_API_KEY not configured in .env")
        print("  [*] Get API key from: https://console.groq.com/")
        
        user_key = input("  Enter your GROQ_API_KEY (or skip to continue): ").strip()
        if user_key:
            # Update .env file
            env_content = env_file.read_text()
            env_content = env_content.replace(
                "GROQ_API_KEY=your_groq_api_key_here",
                f"GROQ_API_KEY={user_key}"
            )
            env_file.write_text(env_content)
            print("  [OK] API key saved to .env")
            load_dotenv(dotenv_path=env_file)
        else:
            print("  [!] Continuing without API key (some features may not work)")
    else:
        print("  [OK] GROQ_API_KEY found in .env")
    
    return True


def check_dependencies():
    """Check if required packages are installed"""
    required = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "groq",
        "crewai",
        "python-dotenv",
        "tenacity"
    ]
    
    print("\n  Checking dependencies...")
    missing = []
    
    try:
        import pkg_resources
        installed = {pkg.key for pkg in pkg_resources.working_set}
        
        for pkg in required:
            if pkg.replace("-", "_") not in installed:
                missing.append(pkg)
        
        if missing:
            print(f"  [!] Missing packages: {', '.join(missing)}")
            install_choice = input("  Install now? (y/n): ").lower()
            if install_choice == "y":
                print("  Installing dependencies...")
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
                print("  [OK] Dependencies installed")
            else:
                print("  [!] Running without all dependencies (may fail)")
                return False
        else:
            print("  [OK] All dependencies installed")
        
        return True
    except Exception as e:
        print(f"  [!] Could not verify dependencies: {e}")
        return False


def menu():
    """Show main menu"""
    print("\n  Select Mode:")
    print("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  1. REST API             (Start web server + docs)")
    print("  2. Interactive CLI      (Desktop terminal interface)")
    print("  3. Quick CLI            (Command-line arguments)")
    print("  4. Direct Optimization  (Single run, no server)")
    print("  5. View Configuration   (Show current settings)")
    print("  6. Exit")
    print("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    choice = input("  Enter choice (1-6): ").strip()
    return choice


def run_api():
    """Start REST API server"""
    print("\n  Starting API server...")
    print("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  [*] Server: http://localhost:8000")
    print("  [*] Docs:   http://localhost:8000/docs")
    print("  [*] ReDoc:  http://localhost:8000/redoc")
    print("  [*] Press Ctrl+C to stop server")
    print("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    try:
        subprocess.run([sys.executable, "api_new.py"], check=True)
    except KeyboardInterrupt:
        print("\n  [OK] Server stopped")
    except Exception as e:
        print(f"  [ERROR] Failed to start API: {e}")


def run_cli_interactive():
    """Run interactive CLI"""
    try:
        subprocess.run([sys.executable, "cli.py"], check=True)
    except Exception as e:
        print(f"  [ERROR] CLI failed: {e}")


def run_cli_quick():
    """Run CLI with arguments"""
    print("\n  Quick CLI Mode")
    print("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    try:
        amount = float(input("  Amount (Rs): ₹ "))
        
        print("\n  Risk Profile:")
        print("    1. Conservative")
        print("    2. Moderate")
        print("    3. Aggressive")
        risk_idx = input("  Choose (1-3): ").strip()
        risk = ["conservative", "moderate", "aggressive"][int(risk_idx) - 1]
        
        print("\n  Tenure:")
        print("    1. 3m   2. 6m   3. 9m   4. 12m   5. 18m   6. 24m")
        tenure_idx = int(input("  Choose (1-6): ").strip())
        tenures = [3, 6, 9, 12, 18, 24]
        tenure = tenures[tenure_idx - 1]
        
        name = input("\n  Your name: ").strip() or "Investor"
        
        # Run optimization
        cmd = [
            sys.executable, "cli.py",
            "--amount", str(int(amount)),
            "--risk", risk,
            "--tenure", str(tenure),
            "--name", name,
            "--save"
        ]
        subprocess.run(cmd, check=True)
    
    except Exception as e:
        print(f"  [ERROR] {e}")


def run_direct():
    """Run direct optimization"""
    print("\n  Direct Optimization")
    print("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    try:
        subprocess.run([sys.executable, "simple_main.py"], check=True)
    except Exception as e:
        print(f"  [ERROR] {e}")


def show_config():
    """Show current configuration"""
    print("\n  Current Configuration")
    print("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    try:
        from settings import get_config_summary
        import json
        config = get_config_summary()
        print(json.dumps(config, indent=2))
    except Exception as e:
        print(f"  [ERROR] Could not load config: {e}")
    
    input("\n  Press Enter to continue...")


def main():
    """Main launcher"""
    print_banner()
    
    # Setup checks
    print("\n  Setting up...")
    print("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    if not check_env_file():
        sys.exit(1)
    
    if not check_dependencies():
        print("\n  [!] Some dependencies missing, but continuing...")
    
    print("\n  [OK] Setup complete!")
    
    # Main loop
    while True:
        choice = menu()
        
        if choice == "1":
            run_api()
        elif choice == "2":
            run_cli_interactive()
        elif choice == "3":
            run_cli_quick()
        elif choice == "4":
            run_direct()
        elif choice == "5":
            show_config()
        elif choice == "6":
            print("\n  Goodbye!")
            sys.exit(0)
        else:
            print("\n  [ERROR] Invalid choice, try again")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Goodbye!")
        sys.exit(0)
