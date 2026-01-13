"""
Main Entry Point for Task Management AI Agent System
CLI mode for testing Google ADK Agent before Streamlit UI
"""

import os
import sys
from dotenv import load_dotenv

from agents.google_adk_agent import GoogleADKAgent
from observability.langfuse_config import (
    get_langfuse_client,
    log_agent_event
)

load_dotenv()


def print_banner():
    print("=" * 60)
    print(" AI Agent System - CLI Test Mode")
    print("=" * 60)
    print("Integrated with:")
    print("  • Google ADK (Gemini)")
    print("  • Serper (Web Search)")
    print("  • Langfuse Observability")
    print("=" * 60)
    print()


def check_environment():
    required_vars = [
        "GEMINI_API_KEY",
        "LANGFUSE_PUBLIC_KEY",
        "LANGFUSE_SECRET_KEY",
    ]

    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nPlease add them to your .env file.")
        return False

    return True


def run_interactive_mode():
    print("\n" + "=" * 60)
    print(" Google ADK Agent - Interactive Mode")
    print(" Type 'exit' to quit")
    print("=" * 60 + "\n")

    try:
        agent = GoogleADKAgent()
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return

    while True:
        try:
            user_input = input("[You] > ").strip()

            if user_input.lower() == "exit":
                print("\n👋 Goodbye!")
                log_agent_event("application_exit", "main", {"status": "normal"})
                break

            if not user_input:
                continue

            log_agent_event(
                "user_input",
                "google_adk",
                {"input": user_input}
            )

            print("\n⏳ Processing...\n")

            response = agent.process_request(user_input)

            log_agent_event(
                "agent_response",
                "google_adk",
                {"response": response}
            )

            print(f"🤖 Agent Response:\n{response}\n")

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user")
            log_agent_event("application_exit", "main", {"status": "keyboard_interrupt"})
            break

        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            log_agent_event(
                "runtime_error",
                "main",
                {"error": str(e)}
            )


def main():
    print_banner()

    if not check_environment():
        sys.exit(1)

    try:
        get_langfuse_client()
        print("✅ Langfuse initialized\n")
        log_agent_event("application_started", "main", {"status": "success"})
    except Exception as e:
        print(f"⚠️ Langfuse not initialized: {e}\n")

    run_interactive_mode()


if __name__ == "__main__":
    main()