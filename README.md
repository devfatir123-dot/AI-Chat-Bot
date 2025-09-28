# AI ChatBot

A complete AI chatbot application built in Python that can answer questions and have conversations like ChatGPT (but simpler). The chatbot includes multiple interfaces and can work with or without API keys.

## Features

🤖 **Multiple Response Methods:**
- Built-in knowledge base with common topics
- Groq AI integration (fast AI responses)
- Hugging Face API integration (optional)
- Free AI responses for basic queries
- Intelligent fallback system

💬 **Multiple Interfaces:**
- Command-line interface with colored output
- Beautiful web interface
- Conversation history saving
- Personalized responses

🧠 **Smart Features:**
- Natural language processing
- Context-aware responses
- Math calculations
- Programming help
- Science and general knowledge

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Chatbot

**Command Line Interface:**
```bash
python chatbot.py
```

**Web Interface:**
```bash
python web_app.py
```
Then open http://localhost:5000 in your browser.

### 3. Optional: Add API Keys
Edit the `.env` file and add your API keys for enhanced AI responses:
```
GROQ_API_KEY=your_groq_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
```

## Usage Examples

The chatbot can help with:

- **General Questions:** "What is artificial intelligence?"
- **Math:** "Calculate 25 * 4 + 10"
- **Programming:** "How do I create a function in Python?"
- **Science:** "Explain photosynthesis"
- **Casual Chat:** "Hello, how are you?"

## File Structure

```
Chat bot/
├── chatbot.py          # Main command-line interface
├── web_app.py          # Web interface with Flask
├── knowledge_base.py   # Built-in knowledge and responses
├── ai_service.py       # AI API integrations
├── requirements.txt    # Python dependencies
├── .env               # API keys configuration
└── README.md          # This file
```

## How It Works

1. **User Input Processing:** The chatbot processes your input using natural language techniques
2. **Response Priority:** 
   - First tries Groq API (if configured)
   - Then tries Hugging Face API (if configured)  
   - Falls back to free AI responses
   - Finally uses built-in knowledge base
3. **Smart Responses:** Provides contextual answers based on detected topics

## Customization

### Adding New Knowledge
Edit `knowledge_base.py` to add new topics and responses:

```python
"new_topic": {
    "patterns": ["keyword1", "keyword2"],
    "responses": [
        "Response 1",
        "Response 2"
    ]
}
```

### Modifying the Web Interface
Edit the HTML template in `web_app.py` to customize the appearance.

## Requirements

- Python 3.7+
- Internet connection (for AI APIs, optional)
- Modern web browser (for web interface)

## API Keys (Optional)

### Groq API
1. Sign up at https://console.groq.com/
2. Generate an API key
3. Add to `.env` file

**Note:** The chatbot works without API keys using the built-in knowledge base!

## Troubleshooting

### NLTK Data Issues
If you get NLTK-related errors, run:
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
```

### Package Installation Issues
Make sure you're using Python 3.7+ and try:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Port Already in Use (Web Interface)
If port 5000 is busy, edit `web_app.py` and change the port:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

## Contributing

Feel free to:
- Add new knowledge topics
- Improve response quality
- Enhance the user interface
- Add new features
- Fix bugs

## License

This project is open source and available under the MIT License.

## Future Enhancements

- [ ] Voice input/output
- [ ] Chat rooms and user sessions
- [ ] Database integration
- [ ] More AI service integrations
- [ ] Mobile app version
- [ ] Sentiment analysis
- [ ] Multi-language support

---

**Enjoy chatting with your AI assistant! 🤖✨**
