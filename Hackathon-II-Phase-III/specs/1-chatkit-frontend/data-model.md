# Data Model: ChatKit Frontend

## Frontend-Specific Types

### ChatMessage
Represents a single message in the chat interface
- **id**: Unique identifier for the message
- **content**: Text content of the message
- **role**: Sender role ('user' or 'assistant')
- **timestamp**: When the message was created
- **status**: Message status ('sending', 'sent', 'error', 'confirmed')

### Conversation
Represents a logical grouping of messages for a user session
- **id**: Unique identifier for the conversation
- **userId**: ID of the user who owns this conversation
- **messages**: Array of ChatMessage objects
- **createdAt**: When the conversation was initiated
- **updatedAt**: When the conversation was last updated

### ChatConfig
Configuration object for the ChatKit component
- **domain**: Allowlisted domain for ChatKit
- **backendUrl**: URL of the backend API
- **jwtToken**: JWT for authentication

### APIResponse
Structure for responses from the backend API
- **conversationId**: ID of the conversation
- **assistantMessage**: Response text from the backend
- **success**: Boolean indicating if the request was successful
- **error**: Error details if the request failed

## Validation Rules
- ChatMessage content must not be empty
- ChatMessage role must be either 'user' or 'assistant'
- Conversation must have a valid userId
- JWT token must be present for all API requests