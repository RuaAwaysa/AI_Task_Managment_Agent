# AI Task Manager with Observability

A smart, AI-powered task management system built with **Google Gemini**, **Streamlit**, and **Langfuse**. This application leverages Large Language Models (LLMs) to understand natural language commands for creating, organizing, and managing tasks, while providing full observability into agent performance.

## Features

### AI Capabilities
- **Natural Language Interface**: Chat with your task manager (e.g., "Remind me to submit the report next Friday").
- **Smart Extraction**: Automatically extracts dates, priorities, and task details from text.
- **Auto-Prioritization**: Automatically escalates task priority as due dates approach (< 24h).
- **Semantic Deduplication**: AI analyzes tasks to find and remove duplicates based on meaning, not just exact text matches.

### User Interface (Streamlit)
- **Interactive Task Board**: Visual cards with color-coded priorities and status.
- **Countdown Timers**: Real-time countdowns for due dates; turns red when < 1 hour remains.
- **Chat & Actions**: Hybrid interface combining chat bot and point-and-click actions (Edit/Delete).
- **Filtering & Sorting**: Filter by status or sort by priority automatically.

### Observability (Langfuse)
- **Full Tracing**: Track every agent interaction, token usage, and latency.
- **Event Logging**: Monitor specific actions like task creation, deletion, and errors.
- **Debug & Analytics**: Gain insights into how the LLM is performing.

## Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **AI Model**: [Google Gemini (via Google Generative AI SDK)](https://ai.google.dev/)
- **Observability**: [Langfuse](https://langfuse.com/)
- **Language**: Python 3.10+

## Getting Started

### Prerequisites
- Python 3.8 or higher
- A Google Cloud Project with Gemini API enabled
- A Langfuse account (Cloud or Self-hosted)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/RuaAwaysa/AI_Task_Managment_Agent.git
   cd AI_Task_Managment_Agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   Create a `.env` file in the root directory with the following keys:
   ```env
   # Google Gemini API
   GEMINI_API_KEY=your_gemini_api_key_here
   GOOGLE_API_KEY=your_gemini_api_key_here

   # Langfuse Observability
   LANGFUSE_PUBLIC_KEY=pk-lf-...
   LANGFUSE_SECRET_KEY=sk-lf-...
   LANGFUSE_HOST=https://cloud.langfuse.com
   ```

## Running the Application

### Web Interface
Launch the Streamlit dashboard:
```bash
streamlit run streamlit_app.py
```

### Interactive Mode

The application provides an interactive menu:
2. **Use Google ADK Agent**: Interact with the Google Gemini-powered agent
3. **Run Demo Script**: Execute a pre-configured demo showing both agents
4. **Exit**: Close the application

### Example Commands

Once in interactive mode, you can use natural language commands:

**Creating Tasks:**
- "Create a high priority task: Complete project documentation"
- "Add a task to review code changes by tomorrow"
- "New task: Finish report, priority high, due 2025-12-30"

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
│   ├── __init__.py          # CrewAI agent implementation
│   └── google_adk_agent.py      # Google ADK agent implementation
├── tools/
│   ├── __init__.py
│   ├── task_tools.py            # Task management tools
│   ├── serper_tool.py            # Searching tool
│   └── calendar_tool.py         # Google Calendar integration
├── observability/
│   ├── __init__.py
│   └── langfuse_config.py       # Langfuse configuration and utilities
├── main.py                      # Main entry point
├── streamlit_app.py             # Streamlit App UI
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