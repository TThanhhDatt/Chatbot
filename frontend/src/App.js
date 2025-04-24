import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sessionId] = useState(Date.now().toString());
  const wsRef = useRef(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    wsRef.current = new WebSocket('ws://localhost:8000/ws/chat');
    
    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages((prev) => {
        const lastMessage = prev[prev.length - 1];
        if (lastMessage?.role === 'assistant' && !lastMessage.content.endsWith('\n')) {
          return [
            ...prev.slice(0, -1),
            { role: 'assistant', content: lastMessage.content + data.response }
          ];
        }
        return [...prev, { role: 'assistant', content: data.response }];
      });
    };

    wsRef.current.onclose = () => console.log('WebSocket closed');

    return () => {
      wsRef.current?.close();
    };
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;
    
    setMessages((prev) => [...prev, { role: 'user', content: input }]);
    wsRef.current?.send(JSON.stringify({ message: input, session_id: sessionId }));
    setInput('');
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', sessionId);

    try {
      await axios.post('http://localhost:8000/upload_pdf', formData);
      alert('PDF uploaded successfully');
    } catch (error) {
      alert('Error uploading PDF');
    }
  };

  return (
    <div className="app">
      <h1>AI ChatBot</h1>
      <div className="chat-container">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <strong>{msg.role === 'user' ? 'You' : 'Bot'}:</strong> {msg.content}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div className="input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type your message..."
        />
        <button onClick={handleSend}>Send</button>
        <input type="file" accept=".pdf" onChange={handleFileUpload} />
      </div>
      <p>
        Use "search_pdf:query" to search in uploaded PDF or "search_web:query" to search for articles/blogs.
      </p>
    </div>
  );
}

export default App;