"""
Quick setup verification script
Run this to check if your environment is configured correctly
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def check_env_var(var_name: str, description: str, required: bool = True) -> bool:
    """Check if an environment variable is set"""
    value = os.getenv(var_name)
    if value:
        print(f" {var_name}: Set ({description})")
        return True
    else:
        if required:
            print(f" {var_name}: Missing (REQUIRED - {description})")
            return False
        
def check_package(package_name: str) -> bool:
    """Check if a Python package is installed"""
    try:
        __import__(package_name)
        print(f" {package_name}: Installed")
        return True
    except ImportError:
        print(f" {package_name}: Not installed (run: pip install {package_name})")
        return False

def main():
    print("=" * 60)
    print("Task Management Agent - Setup Verification")
    print("=" * 60)
    print()
    
    # Check environment variables
    print("Checking Environment Variables:")
    print("-" * 60)
    required_vars_ok = True
    required_vars_ok &= check_env_var("GEMINI_API_KEY", "Google Gemini API key", required=True)
    required_vars_ok &= check_env_var("LANGFUSE_PUBLIC_KEY", "Langfuse public key", required=True)
    required_vars_ok &= check_env_var("LANGFUSE_SECRET_KEY", "Langfuse secret key", required=True)
    check_env_var("OPENAI_API_KEY", "OpenAI API key (for CrewAI)", required=False)
    check_env_var("SERPER_API_KEY", "Serper Dev API key", required=False)
    
    print()
    
    # Check Python packages
    print("Checking Python Packages:")
    print("-" * 60)
    packages_ok = True
    packages_ok &= check_package("crewai")
    packages_ok &= check_package("langfuse")
    packages_ok &= check_package("google.generativeai")
    packages_ok &= check_package("langchain")
    try:
        import dotenv
        print(" python-dotenv: Installed")
        packages_ok = packages_ok and True
    except ImportError:
        print(" python-dotenv: Not installed (run: pip install python-dotenv)")
        packages_ok = False
    
    print()
    print("=" * 60)
    
    if required_vars_ok and packages_ok:
        print(" Setup looks good! You can run: python main.py")
        return 0
    else:
        print(" Setup incomplete. Please fix the issues above.")
        if not required_vars_ok:
            print("\nMissing required environment variables. Please update your .env file.")
        if not packages_ok:
            print("\nMissing packages. Please run: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())

