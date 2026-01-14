# Databricks Chatbot Application

An AI-powered conversational interface that leverages Databricks' model serving infrastructure to provide intelligent chat interactions. The application enables users to have real-time conversations with AI models (specifically Claude Sonnet 4.5) while maintaining persistent chat history and providing feedback mechanisms.

## Features

- Real-time chat interface with streaming AI responses
- **Intelligent Query Routing**: Automatically routes data queries to Genie Space and general questions to Claude LLM
- Chat history persistence across sessions
- Message regeneration capability
- User feedback system (thumbs up/down ratings)
- Secure token-based authentication
- Rate limiting and error handling

## Intelligent Query Routing

The chatbot implements intelligent query routing between two services:

### Data Queries (Genie Space)
Queries about data, metrics, clients, and database information are automatically routed to the Genie Space MCP server. This includes questions like:
- "How many clients have housing risk?"
- "Show me the demographics breakdown"
- "What is the average outcome score?"
- "List all clients with disability needs"
- "Find records with mental health support"

### General Queries (Claude LLM)
Conversational, creative, or analytical questions that don't require data access are routed to the Claude LLM endpoint:
- "Explain machine learning"
- "What is artificial intelligence?"
- "Write a summary of best practices"
- "How does natural language processing work?"

### Routing Logic
The routing decision is based on keyword detection with confidence scoring:
- Data-related keywords: "how many", "show me", "query", "table", "clients", "metrics", "count", "list", "find", "database", "housing risk", "disability", "mental health", etc.
- General keywords: "explain", "what is", "how does", "write", "create", "define", "describe", etc.

If a query matches data keywords with sufficient confidence (>=50%), it's routed to Genie Space. Otherwise, it defaults to Claude LLM. If Genie Space fails, the system gracefully falls back to Claude LLM.

### Configuration
The routing can be enabled/disabled via environment variables:
```bash
GENIE_MCP_ENABLED=true  # Enable/disable Genie routing (default: true)
GENIE_SPACE_ID=01f0eaaeedaf11b7b236db1eb5bbd243  # Genie Space ID
```

## Architecture

The application follows a three-tier architecture:

**Frontend**: React-based single-page application (SPA) compiled to static assets

**Backend**: FastAPI application with asynchronous request handling

**Data Layer**: SQLite database for local persistence

**External Integration**: Databricks model serving endpoints for AI inference

### Tech Stack

**Backend**:
- FastAPI 0.104.1
- Uvicorn 0.24.0
- Pydantic 2.4.2
- SQLite for chat history storage
- Gunicorn for production deployment

**Frontend**:
- React 19
- TypeScript
- React Router DOM
- Axios for HTTP requests
- Styled Components

## Project Structure

```
databricks-chatbot/
├── main.py                 # FastAPI application entry point
├── chat_database.py        # Database access layer (SQLite)
├── token_minter.py         # Authentication handling
├── models.py               # Pydantic data models and schemas
├── utils/                  # Helper functions and utilities
├── app.yaml                # Deployment configuration
├── requirements.txt        # Python dependencies
├── frontend/               # React application
│   ├── src/                # Source code
│   ├── public/             # Static HTML and metadata
│   ├── build/              # Compiled frontend artifacts
│   ├── package.json        # Frontend dependencies
│   └── tsconfig.json       # TypeScript configuration
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- Databricks workspace with model serving endpoint configured

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/archerzou/databricks-chatbot.git
cd databricks-chatbot
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables by creating a `.env` file:
```bash
SERVING_ENDPOINT_NAME=databricks-claude-sonnet-4-5
DATABRICKS_HOST=your-databricks-host.azuredatabricks.net
DATABRICKS_TOKEN=your-databricks-token
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Build the production version:
```bash
npm run build
```

### Running the Application

**Development mode**:
```bash
python main.py
```

**Production mode** (with Gunicorn):
```bash
gunicorn -w 2 --worker-class uvicorn.workers.UvicornWorker main:app
```

The application will be available at `http://localhost:8000`.

## Example Interface

Here's how the chat interface looks:

![Databricks Chat Interface](./utils/Databricks_chatbot_app.png)

## Key Components

| Component | Description |
|-----------|-------------|
| `main.py` | FastAPI application entry point with HTTP routes for chat, history, and user management |
| `chat_database.py` | Thread-safe SQLite operations with connection pooling for chat persistence |
| `models.py` | Pydantic models for request/response validation (MessageResponse, ChatHistoryItem, etc.) |
| `token_minter.py` | Authentication module for validating user tokens |
| `utils/` | Helper functions for Databricks API communication and rate limiting |

## Database Schema

The application uses SQLite with three main tables:

- **sessions**: Chat session metadata (session_id, user_id, first_query, timestamp)
- **messages**: Individual chat messages (message_id, session_id, content, role, model)
- **message_ratings**: User feedback (message_id, user_id, rating)

## Deployment

The application is configured for deployment using Gunicorn with Uvicorn workers. See `app.yaml` for deployment configuration:

```yaml
command:
  - gunicorn
  - main:app
  - -w 2
  - --worker-class uvicorn.workers.UvicornWorker

env:
  - name: SERVING_ENDPOINT_NAME
    value: databricks-claude-sonnet-4-5
  - name: DATABRICKS_HOST
    value: your-databricks-host.azuredatabricks.net
```

## License

This project is proprietary software.
