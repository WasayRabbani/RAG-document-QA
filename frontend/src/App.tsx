import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css';

interface Message {
  role: 'user' | 'bot';
  text: string;
  sources?: number[];
}

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isChatting, setIsChatting] = useState(false);
  const [processedFile, setProcessedFile] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  
  // New states for Phase 3
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [errorToast, setErrorToast] = useState<string | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isChatting]);

  // Auto-hide toast after 5 seconds
  useEffect(() => {
    if (errorToast) {
      const timer = setTimeout(() => setErrorToast(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [errorToast]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setIsUploading(true);
    setErrorToast(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload`, formData);
      setProcessedFile(response.data.filename);
      setSessionId(response.data.session_id);
      setMessages([{ role: 'bot', text: `Successfully processed "${selectedFile.name}". How can I help you with it?` }]);
    } catch (error: any) {
      console.error('Upload error:', error);
      setErrorToast(error.response?.data?.detail || 'Failed to upload and process the PDF. Ensure the backend is running.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim() || !sessionId || isChatting) return;

    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setIsChatting(true);
    setErrorToast(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        session_id: sessionId,
        question: userMsg
      });

      setMessages(prev => [...prev, { 
        role: 'bot', 
        text: response.data.answer, 
        sources: response.data.sources 
      }]);
    } catch (error: any) {
      console.error('Chat error:', error);
      setErrorToast(error.response?.data?.detail || 'Failed to get an answer. The server might be busy.');
    } finally {
      setIsChatting(false);
    }
  };

  return (
    <div className={`app-container ${theme}`}>
      {/* Toast Notification */}
      {errorToast && (
        <div className="toast-container">
          <div className="toast">
            ⚠️ {errorToast}
          </div>
        </div>
      )}

      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo-container">
            <h1>PDF Brain 🧠</h1>
          </div>
          <button className="theme-toggle" onClick={toggleTheme} aria-label="Toggle theme">
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
        </div>

        <div className="upload-section">
          <label className={`upload-btn ${isUploading ? 'processing' : ''}`}>
            {isUploading ? 'Processing...' : 'Upload PDF'}
            <input type="file" hidden accept=".pdf" onChange={handleFileUpload} disabled={isUploading} />
          </label>
          {file && (
            <div className="file-info">
              <p>📄 {file.name.length > 20 ? file.name.substring(0, 20) + '...' : file.name}</p>
              <span className={`status-badge ${sessionId ? 'status-online' : 'status-offline'}`}>
                {sessionId ? 'Ready' : 'Pending'}
              </span>
            </div>
          )}
        </div>

        <div className="instructions">
          <h3>How to use:</h3>
          <ol>
            <li>Upload a PDF document</li>
            <li>Wait for "Ready" status</li>
            <li>Ask questions about it!</li>
          </ol>
        </div>
      </aside>

      <main className="chat-area">
        <div className="messages">
          {messages.length === 0 && (
            <div className="welcome-msg" style={{ textAlign: 'center', color: 'var(--text-muted)', marginTop: '20vh' }}>
              <h2>Welcome! Upload a document to start chatting.</h2>
              <p>The AI will answer strictly based on the content of your PDF.</p>
            </div>
          )}
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role === 'user' ? 'user-message' : 'bot-message'}`}>
              <div className="text">{msg.text}</div>
              {msg.sources && msg.sources.length > 0 && (
                <div className="sources">
                  Sources: Page {msg.sources.join(', ')}
                </div>
              )}
            </div>
          ))}
          
          {/* Typing Indicator */}
          {isChatting && (
            <div className="message bot-message">
              <div className="typing-indicator">
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <div className="input-area">
          <div className="input-container">
            <input 
              type="text" 
              placeholder={sessionId ? "Ask a question..." : "Upload a PDF first"} 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              disabled={!sessionId || isChatting}
            />
            <button 
              className="send-btn" 
              onClick={handleSendMessage}
              disabled={!sessionId || isChatting || !input.trim()}
              title="Send Message"
            >
              {isChatting ? '...' : '➤'}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
