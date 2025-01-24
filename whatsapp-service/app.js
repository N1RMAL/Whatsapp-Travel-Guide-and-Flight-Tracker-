const { create } = require('@open-wa/wa-automate');
const express = require('express');
const axios = require('axios');

const app = express();
app.use(express.json());

let client;

// Chatbot API URL
const CHATBOT_API_URL = 'http://localhost:7000/api/chat/'; // Replace with your backend's URL

// Amadeus API Credentials
const AMADEUS_API_URL = 'https://test.api.amadeus.com/v1/security/oauth2/token';
const AMADEUS_CLIENT_ID = 'Vh0h1Htzha6m32KUT7jnBDtd5NO6PZgW';
const AMADEUS_CLIENT_SECRET = 'nP6qQVlG8sZAxVbp';

// Function to authenticate with Amadeus API
const getAmadeusToken = async () => {
    try {
        const response = await axios.post(AMADEUS_API_URL, {
            grant_type: 'client_credentials',
            client_id: AMADEUS_CLIENT_ID,
            client_secret: AMADEUS_CLIENT_SECRET,
        });
        return response.data.access_token;
    } catch (error) {
        console.error('❌ Error authenticating with Amadeus API:', error.message);
        throw new Error('Failed to authenticate with Amadeus API.');
    }
};

// Fetch flight offers from Amadeus API
const getFlights = async (origin, destination, departureDate) => {
    try {
        const token = await getAmadeusToken();
        const response = await axios.get('https://test.api.amadeus.com/v2/shopping/flight-offers', {
            headers: { Authorization: `Bearer ${token}` },
            params: {
                originLocationCode: origin,
                destinationLocationCode: destination,
                departureDate: departureDate,
                adults: 1,
            },
        });
        return response.data.data;
    } catch (error) {
        console.error('❌ Error fetching flights from Amadeus API:', error.message);
        throw new Error('Failed to fetch flights.');
    }
};

// Fetch hotel offers from Amadeus API
const getHotels = async (cityCode, checkInDate, checkOutDate) => {
    try {
        const token = await getAmadeusToken();
        const response = await axios.get('https://test.api.amadeus.com/v2/shopping/hotel-offers', {
            headers: { Authorization: `Bearer ${token}` },
            params: {
                cityCode: cityCode,
                checkInDate: checkInDate,
                checkOutDate: checkOutDate,
                adults: 1,
            },
        });
        return response.data.data;
    } catch (error) {
        console.error('❌ Error fetching hotels from Amadeus API:', error.message);
        throw new Error('Failed to fetch hotels.');
    }
};

// Initialize WhatsApp Client
create()
    .then((waClient) => {
        client = waClient;
        console.log('✅ WhatsApp Client Initialized');

        // Listen for incoming WhatsApp messages
        waClient.onMessage(async (message) => {
            console.log('📥 Incoming message:', message.body); // Log the received message
            console.log('👤 From:', message.from); // Log the sender's number

            if (message.isGroupMsg) {
                console.log('🚫 Ignoring message from group:', message.chat.name);
                return; // Ignore group messages
            }

            // Only respond to text messages
            if (message.type !== 'chat') {
                console.log('⚠️ Non-text message received. Skipping.');
                return;
            }

            const userMessage = message.body.toLowerCase();

            try {
                if (userMessage.startsWith('flight')) {
                    const [_, origin, destination, date] = userMessage.split(' ');
                    console.log('✈️ Fetching flight details...');
                    const flights = await getFlights(origin.toUpperCase(), destination.toUpperCase(), date);
                    const flightDetails = flights
                        .map((flight) => {
                            const departure = flight.itineraries[0].segments[0].departure.iataCode;
                            const arrival = flight.itineraries[0].segments[0].arrival.iataCode;
                            const price = flight.price.total;
                            return `From: ${departure}, To: ${arrival}, Price: $${price}`;
                        })
                        .join('\n');
                    await waClient.sendText(message.from, `Available flights:\n${flightDetails}`);
                } else if (userMessage.startsWith('hotel')) {
                    const [_, cityCode, checkIn, checkOut] = userMessage.split(' ');
                    console.log('🏨 Fetching hotel details...');
                    const hotels = await getHotels(cityCode.toUpperCase(), checkIn, checkOut);
                    const hotelDetails = hotels
                        .map((hotel) => {
                            const name = hotel.hotel.name;
                            const price = hotel.offers[0].price.total;
                            return `Hotel: ${name}, Price: $${price}`;
                        })
                        .join('\n');
                    await waClient.sendText(message.from, `Available hotels:\n${hotelDetails}`);
                } else {
                    console.log('💬 Sending query to chatbot API...');
                    const response = await axios.post(CHATBOT_API_URL, {
                        query: userMessage,
                    });

                    const botResponse = response.data.response || 'No response from chatbot.';
                    console.log('✅ Response from chatbot API:', botResponse);

                    // Send the bot's response back to the user
                    await waClient.sendText(message.from, botResponse);
                }
            } catch (error) {
                console.error('❌ Error processing user message:', error.message);
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
