import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css';

interface Message {
  role: 'user' | 'bot';
  text: string;
  sources?: number[];
}

interface UploadedDoc {
  filename: string;
  sessionId: string;
}

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isChatting, setIsChatting] = useState(false);
  const [documents, setDocuments] = useState<UploadedDoc[]>([]);
  
  // Theme and toast
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
    setIsUploading(true);
    setErrorToast(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload`, formData);
      const newDoc: UploadedDoc = {
        filename: response.data.filename,
        sessionId: response.data.session_id
      };

      // Don't add duplicates (same hash = same file)
      setDocuments(prev => {
        const exists = prev.some(d => d.sessionId === newDoc.sessionId);
        if (exists) {
          setMessages(prev => [...prev, { 
            role: 'bot', 
            text: `"${selectedFile.name}" was already loaded (cached). Ready to chat!` 
          }]);
          return prev;
        }
        setMessages(prev => [...prev, { 
          role: 'bot', 
          text: `Successfully processed "${selectedFile.name}". ${prev.length === 0 ? 'Ask me anything!' : 'Added to your library.'}` 
        }]);
        return [...prev, newDoc];
      });
    } catch (error: any) {
      console.error('Upload error:', error);
      setErrorToast(error.response?.data?.detail || 'Failed to upload and process the PDF.');
    } finally {
      setIsUploading(false);
      // Reset input so same file can be re-selected
      e.target.value = '';
    }
  };

  const removeDocument = (sessionId: string) => {
    setDocuments(prev => prev.filter(d => d.sessionId !== sessionId));
  };

  const handleSendMessage = async () => {
    if (!input.trim() || documents.length === 0 || isChatting) return;

    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setIsChatting(true);
    setErrorToast(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        session_ids: documents.map(d => d.sessionId),
        question: userMsg
      });

      setMessages(prev => [...prev, { 
        role: 'bot', 
        text: response.data.answer, 
        sources: response.data.sources 
      }]);
    } catch (error: any) {
      console.error('Chat error:', error);
      setErrorToast(error.response?.data?.detail || 'Failed to get an answer.');
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
            {isUploading ? 'Processing...' : '+ Add PDF'}
            <input type="file" hidden accept=".pdf" onChange={handleFileUpload} disabled={isUploading} />
          </label>
        </div>

        {/* Document Library */}
        <div className="doc-library">
          <h3>📚 Library ({documents.length})</h3>
          {documents.length === 0 && (
            <p className="empty-library">No documents yet. Upload a PDF to start!</p>
          )}
          {documents.map((doc) => (
            <div key={doc.sessionId} className="doc-item">
              <span className="doc-name" title={doc.filename}>
                📄 {doc.filename.length > 22 ? doc.filename.substring(0, 22) + '...' : doc.filename}
              </span>
              <button 
                className="doc-remove" 
                onClick={() => removeDocument(doc.sessionId)}
                title="Remove from library"
              >
                ✕
              </button>
            </div>
          ))}
        </div>

        <div className="instructions">
          <h3>How to use:</h3>
          <ol>
            <li>Upload one or more PDFs</li>
            <li>Ask questions across all docs</li>
            <li>AI searches your entire library!</li>
          </ol>
        </div>
      </aside>

      <main className="chat-area">
        <div className="messages">
          {messages.length === 0 && documents.length === 0 && (
            <div className="welcome-msg">
              <h2>Welcome to PDF Brain 🧠</h2>
              <p>Upload your documents to build a searchable knowledge base.</p>
            </div>
          )}
          {messages.map((msg, idx) => {
            // Only show sources if it's a bot message, has sources, 
            // and the text doesn't contain the "I don't know" refusal.
            const isRefusal = msg.text.toLowerCase().includes("don't know") || 
                              msg.text.toLowerCase().includes("no information");
            const showSources = msg.role === 'bot' && msg.sources && msg.sources.length > 0 && !isRefusal;

            return (
              <div key={idx} className={`message ${msg.role === 'user' ? 'user-message' : 'bot-message'}`}>
                <div className="text">{msg.text}</div>
                {showSources && (
                  <div className="sources">
                    Sources: Page {msg.sources?.join(', ')}
                  </div>
                )}
              </div>
            );
          })}
          
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
              placeholder={documents.length > 0 ? `Ask across ${documents.length} document${documents.length > 1 ? 's' : ''}...` : "Upload a PDF first"} 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              disabled={documents.length === 0 || isChatting}
            />
            <button 
              className="send-btn" 
              onClick={handleSendMessage}
              disabled={documents.length === 0 || isChatting || !input.trim()}
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
