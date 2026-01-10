"""
Main Entry Point for Task Management AI Agent System
This demonstrates the integration of CrewAI and Google ADK agents with observability
"""
import os
import sys
from dotenv import load_dotenv
from agents.task_manager import TaskManager
from observability.langfuse_config import get_langfuse_client, log_agent_event

load_dotenv()

def print_banner():
    """Print welcome banner"""
    print("=" * 60)
    print(" AI Task Management Agent System")
    print("=" * 60)
    print("Integrated with:")
    print("  • CrewAI Framework")
    print("  • Google ADK (Gemini)")
    print("  • Langfuse Observability")
    print("=" * 60)
    print()

def print_menu():
    """Print interactive menu"""
    print("\nOptions:")
    print("1. Use CrewAI Agent")
    print("2. Use Google ADK Agent")
    print("3. Run Demo Script (automated)")
    print("4. Exit")
    print()

def run_interactive_mode(agent_type: str):
    """Run interactive mode with selected agent"""
    agent_name = "CrewAI" if agent_type == "crewai" else "Google ADK"
    print(f"\n{'='*60}")
    print(f"Using {agent_name} Agent")
    print("Type 'exit' to return to menu")
    print("Type 'help' for example commands")
    print(f"{'='*60}\n")
    
    try:
        manager = TaskManager(agent_type=agent_type)
    except Exception as e:
        print(f"Error initializing agent: {e}")
        print("Please check your .env file and API keys.")
        return
    
    while True:
        try:
            user_input = input(f"[{agent_name}] > ").strip()
            
            if user_input.lower() == 'exit':
                break
            elif user_input.lower() == 'help':
                print("\nExample commands:")
                print("  • Create a task: 'Create a task to finish the report by tomorrow'")
                print("  • List tasks: 'Show me all pending tasks'")
                print("  • Update task: 'Mark task 1 as completed'")
                print("  • Get statistics: 'Show me task statistics'")
                print()
                continue
            elif not user_input:
                continue
            
            print("\nProcessing...")
            response = manager.process(user_input)
            print(f"\n{response}\n")
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {e}\n")

def run_demo_script():
    """Run a demo script showing both agents"""
    print("\n" + "="*60)
    print("Running Demo Script")
    print("="*60 + "\n")
    
    demo_requests = [
        "Create a high priority task: Complete project documentation",
        "Create a medium priority task: Review code changes",
        "List all tasks",
        "Show me task statistics",
    ]
    
    # Test Google ADK Agent
    print("="*60)
    print("Testing Google ADK Agent")
    print("="*60 + "\n")
    
    try:
        google_manager = TaskManager(agent_type="google_adk")
        for i, request in enumerate(demo_requests, 1):
            print(f"\n[{i}] Request: {request}")
            print("-" * 60)
            response = google_manager.process(request)
            print(f"Response: {response}\n")
    except Exception as e:
        print(f" Error with Google ADK agent: {e}\n")
    
    # Test CrewAI Agent
    print("\n" + "="*60)
    print("Testing CrewAI Agent")
    print("="*60 + "\n")
    
    try:
        crewai_manager = TaskManager(agent_type="crewai")
        for i, request in enumerate(demo_requests[:2], 1):  # Use fewer requests for CrewAI
            print(f"\n[{i}] Request: {request}")
            print("-" * 60)
            response = crewai_manager.process(request)
            print(f"Response: {response}\n")
    except Exception as e:
        print(f" Error with CrewAI agent: {e}\n")
    
    print("\n" + "="*60)
    print("Demo completed! Check Langfuse dashboard for traces and metrics.")
    print("="*60 + "\n")

def check_environment():
    """Check if required environment variables are set"""
    required_vars = {
        "GEMINI_API_KEY": "Google Gemini API key",
        "LANGFUSE_PUBLIC_KEY": "Langfuse public key",
        "LANGFUSE_SECRET_KEY": "Langfuse secret key",
    }
    
    optional_vars = {
        "OPENAI_API_KEY": "OpenAI API key (for CrewAI)",
    }
    
    missing = []
    warnings = []
    
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing.append(f"{var} ({description})")
    
    for var, description in optional_vars.items():
        if not os.getenv(var):
            warnings.append(f"{var} ({description})")
    
    if missing:
        print("Missing required environment variables:")
        for var in missing:
            print(f"  {var}")
        print("\nPlease add these to your .env file.")
        return False
    
    if warnings:
        print("Optional environment variables not set (may limit functionality):")
        for var in warnings:
            print(f"   • {var}")
        print()
    
    return True

def main():
    """Main function"""
    print_banner()
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Initialize observability
    try:
        langfuse = get_langfuse_client()
        log_agent_event("application_started", "main", {"status": "success"})
        print("Observability (Langfuse) initialized\n")
    except Exception as e:
        print(f" Warning: Could not initialize Langfuse: {e}\n")
        print("Continuing without observability...\n")
    
    # Main loop
    while True:
        print_menu()
        try:
            choice = input("Select an option (1-4): ").strip()
            
            if choice == '1':
                run_interactive_mode("crewai")
            elif choice == '2':
                run_interactive_mode("google_adk")
            elif choice == '3':
                run_demo_script()
            elif choice == '4':
                print("\n Goodbye!")
                log_agent_event("application_exited", "main", {"status": "normal"})
                break
            else:
                print("Invalid choice. Please select 1-4.\n")
        
        except KeyboardInterrupt:
            print("\n\n Goodbye!")
            log_agent_event("application_exited", "main", {"status": "interrupted"})
            break
        except Exception as e:
            print(f"\nError: {e}\n")

if __name__ == "__main__":
    main()

