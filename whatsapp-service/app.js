//http://localhost:8000/chat-with-bot/
const { create } = require('@open-wa/wa-automate');
const express = require('express');
const axios = require('axios');

const app = express();
app.use(express.json());

let client;

// Chatbot API URL
const CHATBOT_API_URL = 'http://localhost:7000/api/chat/'; // Replace with your backend's URL

// Test Chatbot API Reachability
const testChatbotAPI = async () => {
    try {
        const testResponse = await axios.get(`${CHATBOT_API_URL}health-check/`);
        console.log('✅ Chatbot API is reachable:', testResponse.data);
    } catch (error) {
        console.error('❌ Unable to reach Chatbot API:', error.message);
    }
};

testChatbotAPI();

// Initialize WhatsApp Client
create()
    .then((waClient) => {
        client = waClient;
        console.log('✅ WhatsApp Client Initialized');

        // Listen for incoming WhatsApp messages
        waClient.onMessage(async (message) => {
            console.log('📥 Incoming message:', message.body); // Log the received message
            console.log('👤 From:', message.from); // Log the sender's number

            // Only respond to text messages
            if (message.type !== 'chat') {
                console.log('⚠️ Non-text message received. Skipping.');
                return;
            }

            const userMessage = message.body;

            try {
                console.log('⏳ Sending user query to chatbot API...');
                const response = await axios.post(CHATBOT_API_URL, {
                    query: userMessage,
                });

                const botResponse = response.data.response || 'No response from chatbot.';
                console.log('✅ Response from chatbot API:', botResponse);

                // Send the bot's response back to the user
                await waClient.sendText(message.from, botResponse);
                console.log('📤 Sent response to user:', botResponse);
            } catch (error) {
                console.error('❌ Error communicating with chatbot API:', error.message);
                console.error('❌ Full error details:', error.response?.data || error);

                await waClient.sendText(
                    message.from,
                    'Sorry, there was an issue processing your request. Please try again later.'
                );
            }
        });
    })
    .catch((error) => {
        console.error('❌ Failed to initialize WhatsApp Client:', error.message);
    });

// Endpoint to test if the service is running
app.get('/', (req, res) => {
    console.log('✅ Health check hit.');
    res.send('WhatsApp Bot is running.');
});

// Start the Express server
const PORT = 3001;
app.listen(PORT, () => {
    console.log(`🚀 WhatsApp service running on http://localhost:${PORT}`);
});
