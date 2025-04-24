Chatbot Application
This is a web-based chatbot application built with a FastAPI backend and React frontend. It supports chatting with an AI model via Open Router, uploading and searching PDFs, and performing web searches using SerpAPI or Google Search as a fallback. The application uses WebSocket for real-time communication.
Features

Chat: Interact with an AI model (google/gemini-2.0-flash-exp:free) for conversational responses.
PDF Upload and Search: Upload PDFs and search their content using search_pdf:<query>.
Web Search: Perform web searches using search_web:<query> and view results with titles, links, and summaries.
Responsive UI: A clean React interface with chat and web search inputs.

Prerequisites
Before setting up the application, ensure you have the following installed:

Python 3.8+: For the backend.
Node.js 16+ and npm: For the frontend.
Git: To clone the repository (optional).

You also need API keys for:

Open Router: To access AI models (required).
SerpAPI: For web search functionality (optional, fallback to Google Search if not provided).

Installation
1. Clone the Repository
git clone <repository-url>
cd chatbot

2. Set Up the Backend
The backend is built with FastAPI and requires Python dependencies.
a. Create a Virtual Environment
python -m venv venv
venv\Scripts\activate

b. Install Python Dependencies
pip install -r requirements.txt

c. Configure API Keys
Edit the chat.py file in the root directory to add your API keys:

Open chat.py in a text editor.
Find the following lines near the top:OPENROUTER_API_KEY = "your_openrouter_api_key"
SERPAPI_API_KEY = "your_serpapi_api_key" 


Replace your_openrouter_api_key with your Open Router API key.
Replace your_serpapi_api_key with your SerpAPI key (or leave as "" to use Google Search fallback).


Open Router API Key:
Sign up at Open Router.
Go to Settings > API Keys, create a key, and copy it.

SerpAPI Key (optional):
Sign up at SerpAPI.
Get your API key from the dashboard.
If not provided, web search will fall back to basic Google Search scraping.

Note: Storing API keys directly in code is not recommended for production due to security risks. For development, this is acceptable.
3. Set Up the Frontend
The frontend is a React application.
a. Navigate to the Frontend Directory
cd frontend

b. Install Node.js Dependencies
npm install

This installs required packages, including react, uuid, and others specified in package.json.
4. Run the Application
a. Start the Backend
In the backend directory (where chat.py is located):
python chat.py


The backend will run on http://localhost:8000.
You should see logs like:WebSocket connection attempted



b. Start the Frontend
In the chatbot directory:
npm start


The frontend will run on http://localhost:3000.
Open http://localhost:3000 in your browser to access the chat interface.

Usage
1. Chat with the AI
In the chat input box at the bottom of the interface, type a message (e.g., Hello) and press "Send" or Enter.
The AI (google/gemini-2.0-flash-exp:free) will respond.

2. Upload and Search PDFs
Use the PDF upload feature (if implemented in the UI) to upload a PDF file.
In the chat input, type search_pdf:<query> (e.g., search_pdf:test) and press "Send".
Results will show matching text from the PDF with page numbers.

3. Perform Web Searches
Using the Chat Input:
Type search_web:<query> (e.g., search_web:news) in the chat input and press "Send".
Results will display as a message with article titles, links, and summaries.

Using the Web Search Input (if implemented):
Enter a query (e.g., news) in the web search input box (above the chat input).
Click "Search Web".
Results will display as a formatted list with clickable links and summaries.

Troubleshooting
1. WebSocket Connection Fails
Symptom: No WebSocket connected log in browser console (F12 > Console).
Solution:
Check if backend is running (python chat.py).
Verify the WebSocket URL in App.js (ws://localhost:8000/ws/chat).
Check port conflicts:netstat -aon | findstr :8000 
If port 8000 is in use, change the port in chat.py and App.js:uvicorn.run(app, host="0.0.0.0", port=8001)
wsRef.current = new WebSocket('ws://localhost:8001/ws/chat');

2. Open Router Errors
Symptom: Errors like Open Router error: ... in the chat interface.
Common Issues:
Invalid API Key:
Verify OPENROUTER_API_KEY in chat.py.
Test with:curl -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer your_openrouter_key" \
  -H "Content-Type: application/json" \
  -d '{"model": "google/gemini-2.0-flash-exp:free", "messages": [{"role": "user", "content": "Hello"}], "stream": false}'
If 401 Unauthorized, generate a new key at Open Router.
Quota Exceeded:
Free accounts are limited to ~2666 tokens. Use free models like google/gemini-2.0-flash-exp:free.
Upgrade to a paid account at Open Router if needed.


3. Web Search Fails
Symptom: search_web:news returns No articles found or no summaries.
Solution:
Verify SERPAPI_API_KEY in chat.py.
Test SerpAPI:curl -X GET "https://serpapi.com/search?api_key=your_serpapi_key&q=news&num=3"
If invalid, get a new key at SerpAPI.
If no SerpAPI key, the app falls back to Google Search scraping, which may return limited results.

4. Other Errors
Backend Logs: Check terminal for logs like Open Router error, Search error, or WebSocket error.
Frontend Logs: Check browser console (F12 > Console) for WebSocket or rendering issues.
Dependencies: Ensure all Python (pip list) and Node.js (npm list) dependencies are installed.
Python Version: Run python --version to confirm Python 3.8+.
Node.js Version: Run node --version to confirm Node.js 16+.

Contributing
Report issues or suggest features by creating an issue in the repository.
To contribute, fork the repository, make changes, and submit a pull request.

License
This project is licensed under the MIT License.
