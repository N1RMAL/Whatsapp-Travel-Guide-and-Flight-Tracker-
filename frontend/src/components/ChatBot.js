import React, { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import './ChatBot.css';

const api = axios.create({
    baseURL: 'http://localhost:7000/api',  // Match your Django backend port
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
});

function ChatBot() {
    const [query, setQuery] = useState('');
    const [messages, setMessages] = useState([
        {
            id: 0,
            text: "Hello! I'm your AI Travel Assistant. Ask me anything about destinations, travel tips, attractions, or local experiences.",
            sender: 'bot'
        }
    ]);
    const [isLoading, setIsLoading] = useState(false);

    const handleQuery = async () => {
        if (!query.trim()) return;

        const userMessage = {
            id: Date.now(),
            text: query,
            sender: 'user'
        };

        setMessages(prevMessages => [...prevMessages, userMessage]);
        setIsLoading(true);

        try {
            const res = await api.post('/chat/', { query });

            const botMessage = {
                id: Date.now() + 1,
                text: res.data.response, // Backend returns Markdown-formatted response
                sender: 'bot'
            };

            setMessages(prevMessages => [...prevMessages, botMessage]);
            setQuery('');
        } catch (error) {
            console.error('Chat error:', error);

            const errorMessage = {
                id: Date.now() + 2,
                text: 'Something went wrong. Please try again.',
                sender: 'bot'
            };

            setMessages(prevMessages => [...prevMessages, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="chatbot-container">
            <div className="chat-messages">
                {messages.map(message => (
                    <div 
                        key={message.id} 
                        className={`message ${message.sender}`}
                    >
                        {message.sender === 'bot' ? (
                            <ReactMarkdown>{message.text}</ReactMarkdown>
                        ) : (
                            <p>{message.text}</p>
                        )}
                    </div>
                ))}
                {isLoading && (
                    <div className="message bot loading">
                        Generating response...
                    </div>
                )}
            </div>
            <div className="chatbot-input">
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleQuery()}
                    placeholder="Ask about any travel destination or experience"
                />
                <button onClick={handleQuery} disabled={isLoading}>
                    Send
                </button>
            </div>
        </div>
    );
}

export default ChatBot;
