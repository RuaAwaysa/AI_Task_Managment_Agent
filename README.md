# AI Task Management Agent System with Observability

A comprehensive task management system powered by AI agents, integrating CrewAI and Google ADK (Gemini) frameworks with Langfuse observability for tracking, logging, and monitoring agent usage.

## 🎯 Project Overview

This project demonstrates the integration of multiple AI agent frameworks for task management with comprehensive observability. The system allows users to interact with AI agents to create, manage, and track tasks while capturing detailed traces, logs, and metrics through Langfuse.

## Features

- **Dual Agent Framework Support**
  - **CrewAI Agent**: Multi-agent orchestration for task management
  - **Google ADK Agent**: Google Gemini-powered agent for task operations

- **Task Management Capabilities**
  - Create tasks with title, description, priority, and due dates
  - List and filter tasks by status
  - Update task status and priority
  - Delete tasks
  - Get task statistics and analytics

- **Observability (Langfuse Integration)**
  - Real-time tracing of agent executions
  - Detailed logging of all operations
  - Metrics and performance tracking
  - Event logging for debugging and analysis

## 🛠️ Tech Stack

- **AI Frameworks**
  - CrewAI: Multi-agent orchestration framework
  - Google ADK: Google's Agent Development Kit with Gemini API

- **Observability**
  - Langfuse: Open-source LLM observability platform

- **APIs & Services**
  - Google Gemini API (for Google ADK agent)
  - OpenAI API (optional, for CrewAI)
  - Langfuse Cloud/Server

## Prerequisites

- Python 3.8 or higher
- GitHub Code Spaces (recommended)
- API Keys:
  - **GEMINI_API_KEY**: Google Gemini API key from [aistudio.google.com](https://aistudio.google.com)
  - **LANGFUSE_PUBLIC_KEY** & **LANGFUSE_SECRET_KEY**: From [Langfuse Cloud](https://cloud.langfuse.com) or self-hosted instance
  - **OPENAI_API_KEY** : From [platform.openai.com](https://platform.openai.com) for CrewAI

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/RuaAwaysa/task_mangment_observability.git
   cd task-agent-observability
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the root directory with the following keys:
   ```env
   # Required
   GEMINI_API_KEY=your_gemini_api_key_here
   GOOGLE_API_KEY=your_gemini_api_key_here  # Can be same as GEMINI_API_KEY
   
   # Langfuse Observability (Required)
   LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
   LANGFUSE_SECRET_KEY=your_langfuse_secret_key
   LANGFUSE_HOST=https://cloud.langfuse.com  # Or your self-hosted URL
   ```
## 📖 Usage

### Running the Application

```bash
python main.py
```

### Interactive Mode

The application provides an interactive menu:

1. **Use CrewAI Agent**: Interact with the CrewAI-powered task management agent
2. **Use Google ADK Agent**: Interact with the Google Gemini-powered agent
3. **Run Demo Script**: Execute a pre-configured demo showing both agents
4. **Exit**: Close the application

### Example Commands

Once in interactive mode, you can use natural language commands:

**Creating Tasks:**
- "Create a high priority task: Complete project documentation"
- "Add a task to review code changes by tomorrow"
- "New task: Finish report, priority high, due 2024-12-30"

**Listing Tasks:**
- "Show me all tasks"
- "List pending tasks"
- "Get all in-progress tasks"

**Updating Tasks:**
- "Mark task ID 1 as completed"
- "Update task ID 2 to high priority"
- "Change task ID 1 status to in_progress"

**Statistics:**
- "Show me task statistics"
- "Get task overview"
- "What are my task statistics?"

### Programmatic Usage

You can also use the agents programmatically:

```python
from agents.task_manager import TaskManager

# Using Google ADK Agent
manager = TaskManager(agent_type="google_adk")
response = manager.process("Create a task to finish the report")
print(response)

# Using CrewAI Agent
manager = TaskManager(agent_type="crewai")
response = manager.process("List all pending tasks")
print(response)
```

## Observability with Langfuse

This project integrates Langfuse for comprehensive observability:

### Features

- **Traces**: Every agent execution creates a trace with metadata
- **Spans**: Individual operations within traces are logged as spans
- **Events**: Custom events are logged for important operations
- **Metrics**: Performance and usage metrics are automatically collected

### Accessing Observability Data

1. **Langfuse Cloud**: Visit [cloud.langfuse.com](https://cloud.langfuse.com) and log in
2. **Self-hosted**: Access your Langfuse instance URL

In the Langfuse dashboard, you'll see:
- All agent executions with timestamps
- Request/response data
- Execution times and performance metrics
- Error logs and debugging information
- Agent-specific metrics

### Viewing Logs

The observability module automatically logs:
- Agent initialization events
- Task creation/update/deletion events
- Task listing and statistics requests
- Calendar operations (if enabled)
- Errors and exceptions

## Project Structure

```
task-agent-observability/
├── agents/
│   ├── __init__.py
│   ├── crewai_agent.py          # CrewAI agent implementation
│   ├── google_adk_agent.py      # Google ADK agent implementation
│   └── task_manager.py          # Main orchestrator
├── tools/
│   ├── __init__.py
│   ├── task_tools.py            # Task management tools
│   └── calendar_tool.py         # Google Calendar integration
├── observability/
│   ├── __init__.py
│   └── langfuse_config.py       # Langfuse configuration and utilities
├── main.py                      # Main entry point
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── .env                         # Environment variables (create this)
```

## Why Langfuse?

Langfuse was chosen for observability because:

1. **Comprehensive Tracking**: Provides traces, spans, and events for complete visibility
2. **Easy Integration**: Simple Python SDK with decorators and context management
3. **Open Source**: Self-hostable option available
4. **Cloud Option**: Managed service available for easy setup
5. **Rich Dashboard**: Beautiful UI for exploring traces and metrics
6. **Production Ready**: Used by many production LLM applications
7. **Active Development**: Regularly updated with new features

## Testing

Run the demo script to test both agents:

```bash
python main.py
# Select option 3: Run Demo Script
```

This will execute a series of test commands and demonstrate:
- Task creation
- Task listing
- Statistics retrieval
- Observability logging
