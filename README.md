# AI Fashion Chatbot

A personalized fashion recommendation chatbot built with Rasa and Flask, featuring a modern web interface.

## Features

- 🤖 **AI-Powered Recommendations**: Get personalized fashion suggestions based on your preferences
- 🎨 **Smart Filtering**: Filter by category, gender, color, occasion, and style
- 📱 **Modern Web Interface**: Beautiful, responsive chat interface
- 🛍️ **Real Data**: Uses cleaned fashion dataset with 1000+ products
- 💬 **Natural Conversations**: Understands natural language queries

## Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Clone and setup**:
```bash
git clone <repository-url>
cd Fashion-ai-chatbot
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Start the chatbot**:
```bash
python start_chatbot.py
```

4. **Open your browser**:
Navigate to http://localhost:5050

## Usage

### Web Interface
- Open http://localhost:5050 in your browser
- Start chatting with the fashion assistant
- Ask for recommendations, trending styles, or fashion advice

### Example Conversations
- "I need fashion advice"
- "I want dresses for a party"
- "Show me casual tops for women"
- "What's trending in fashion?"
- "I need shoes for work"

### Manual Startup (Alternative)

If you prefer to start services manually:

1. **Start Rasa actions server**:
```bash
rasa run actions
```

2. **Start Rasa server** (in new terminal):
```bash
rasa run --enable-api --cors "*" --port 5005
```

3. **Start web interface** (in new terminal):
```bash
python app.py
```

## Project Structure

```
Fashion-ai-chatbot/
├── app.py                 # Flask web interface
├── start_chatbot.py       # Startup script
├── requirements.txt       # Python dependencies
├── config.yml            # Rasa configuration
├── domain.yml            # Rasa domain
├── endpoints.yml         # Rasa endpoints
├── actions/
│   └── actions.py        # Custom actions
├── data/
│   ├── nlu.yml          # Training data
│   ├── stories.yml      # Conversation flows
│   ├── rules.yml        # Conversation rules
│   └── fashion_data_cleaned.csv  # Fashion dataset
├── templates/
│   └── index.html       # Web interface template
└── models/              # Trained Rasa models
```

## Configuration

### Environment Variables
- `RASA_API_URL`: Rasa server URL (default: http://localhost:5005/webhooks/rest/webhook)

### Ports
- **Web Interface**: 5050
- **Rasa Server**: 5005
- **Actions Server**: 5055

## API Endpoints

### Web Interface
- `GET /` - Main chat interface
- `POST /chat` - Send message to chatbot
- `GET /health` - Health check
- `GET /status` - Service status

### Rasa Server
- `POST /webhooks/rest/webhook` - Chat endpoint
- `GET /status` - Rasa server status

## Troubleshooting

### Common Issues

1. **Port already in use**:
   - Kill existing processes: `pkill -f rasa` or `pkill -f python`
   - Or change ports in configuration files

2. **Rasa server not starting**:
   - Check if model exists: `ls models/`
   - Retrain model: `rasa train`

3. **Actions server issues**:
   - Make sure `actions/actions.py` is properly configured
   - Check `endpoints.yml` configuration

4. **Web interface not loading**:
   - Check if Flask app is running on port 5050
   - Verify Rasa server is running on port 5005

### Logs
- Check terminal output for error messages
- Rasa logs: Look for error messages in terminal
- Flask logs: Check app.py output

## Development

### Training the Model
```bash
rasa train
```

### Testing
```bash
rasa shell
```

### Adding New Features
1. Update `domain.yml` with new intents/entities
2. Add training examples in `data/nlu.yml`
3. Create stories in `data/stories.yml`
4. Implement actions in `actions/actions.py`
5. Retrain: `rasa train`

## License

This project is for educational purposes.

## Support

For issues and questions, please check the troubleshooting section or create an issue in the repository. 