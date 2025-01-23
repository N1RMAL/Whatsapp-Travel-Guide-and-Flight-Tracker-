import React, { useState } from 'react';
import ChatBot from './components/ChatBot';
import './App.css';
import axios from 'axios';

function App() {
    const [recipient, setRecipient] = useState('');
    const [message, setMessage] = useState('');
    const [status, setStatus] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const sendMessage = async (e) => {
        e.preventDefault();

        // Validate input
        if (!recipient || !message) {
            setStatus('Recipient and message cannot be empty!');
            return;
        }

        setIsLoading(true);
        setStatus(''); // Clear previous status

        try {
            const response = await axios.post('http://localhost:7000/api/send-message/', {
                recipient,
                message,
            });

            if (response.status === 200) {
                setStatus('Message sent successfully!');
            } else {
                setStatus('Failed to send message. Please try again.');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            setStatus('Failed to send message. Please check the server.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="app-container">
            <header className="app-header">
                <h1>🌍 Travel Companion AI</h1>
                <p>Your personal AI guide for exploring the world. Ask me anything!</p>
            </header>

            <div className="content-container">
                <div className="chatbot-section">
                    <h2 className="chatbot-title">Chat with Your AI Guide</h2>
                    <p className="chatbot-subtitle">Ask about destinations, tips, or local cuisines!</p>
                    <ChatBot />
                </div>

                <div className="whatsapp-section">
                    <h2>Send WhatsApp Message</h2>
                    <form onSubmit={sendMessage}>
                        <label>
                            Recipient Number (with country code):
                            <input
                                type="text"
                                value={recipient}
                                onChange={(e) => setRecipient(e.target.value)}
                                placeholder="e.g., 1234567890"
                            />
                        </label>
                        <br />
                        <label>
                            Message:
                            <textarea
                                value={message}
                                onChange={(e) => setMessage(e.target.value)}
                                placeholder="Enter your message here"
                            />
                        </label>
                        <br />
                        <button type="submit" disabled={isLoading}>
                            {isLoading ? 'Sending...' : 'Send Message'}
                        </button>
                    </form>
                    {status && <p className="status-message">{status}</p>}
                </div>
            </div>

            <footer className="app-footer">
                <p>✨ Powered by Travel Companion AI | Explore the world with confidence. ✈️</p>
            </footer>
        </div>
    );
}

export default App;
