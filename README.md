# Databricks Chatbot Application

Chat applications powered by Databricks' model serving endpoints. This project provides a foundation for creating interactive chat interfaces that leverage Databricks' powerful AI framework and model serving infrastructure.

## Features

- 🚀 Real-time chat interface
- 💾 Chat history persistence
- 🔄 Message regeneration capability
- ⚡ Streaming responses
- 🔒 Secure authentication
- 🎯 Rate limiting and error handling
- 🔀 Dynamic serving endpoint selection via UI dropdown

## Architecture

The application is built with:
- FastAPI for the backend API
- SQLite for chat history storage
- Async/await patterns for efficient request handling
- Dependency injection for clean code organization
- React frontend with Mantine UI components
- TypeScript for type safety

## Getting Started

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Building the Frontend

[1]. Navigate to the frontend directory:

```bash
cd frontend
```

[2]. Install dependencies:

```bash
npm install
```

[3]. Build the production version:

```bash
npm run build
```

4. Run the application:
```bash
python main.py
```

## Example Interface

Here's how the chat interface looks like

![Databricks Chat Interface](./utils/Databricks_chatbot_app.png)

## Key Components

- `main.py`: FastAPI application entry point
- `utils/`: Helper functions and utilities
- `models.py`: Data models and schemas
- `chat_database.py`: Database interactions
- `token_minter.py`: Authentication handling

## Dynamic Endpoint Selection

The application supports dynamic selection of Databricks serving endpoints via a UI dropdown. This allows users to switch between different AI models without requiring configuration changes.

### Backend API

The backend provides the following endpoint for fetching available serving endpoints:

```
GET /chat-api/serving-endpoints
```

Returns a list of available Databricks serving endpoints with their metadata:

```json
{
  "endpoints": [
    {
      "name": "endpoint-name",
      "state": "READY",
      "creator": "user@example.com",
      "creation_timestamp": 1234567890
    }
  ]
}
```

### Frontend Component

The endpoint selector is implemented using Mantine UI's Combobox component, located in the top navigation bar. It features:

- Loading state while fetching endpoints
- Error handling for API failures
- Accessible dropdown with ARIA labels
- Responsive design for mobile/tablet/desktop

### Configuration

The `SERVING_ENDPOINT_NAME` environment variable in `app.yaml` is now optional. If not set, users must select an endpoint from the UI dropdown before sending messages.
