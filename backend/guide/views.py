import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

from .models import Destination, Place, Food, ChatLog
import json
import traceback
import re

# Amadeus API credentials
AMADEUS_AUTH_URL = 'https://test.api.amadeus.com/v1/security/oauth2/token'
AMADEUS_FLIGHT_URL = 'https://test.api.amadeus.com/v2/shopping/flight-offers'
AMADEUS_HOTEL_URL = 'https://test.api.amadeus.com/v2/shopping/hotel-offers'
AMADEUS_CLIENT_ID = "Vh0h1Htzha6m32KUT7jnBDtd5NO6PZgW"
AMADEUS_CLIENT_SECRET = 'nP6qQVlG8sZAxVbp'

def get_amadeus_token():
    try:
        response = requests.post(AMADEUS_AUTH_URL, data={
            'grant_type': 'client_credentials',
            'client_id': AMADEUS_CLIENT_ID,
            'client_secret': AMADEUS_CLIENT_SECRET,
        })
        response.raise_for_status()
        print("✅ Amadeus Authentication Successful:", response.json())  # Debugging
        return response.json()['access_token']
    except requests.RequestException as e:
        print(f"❌ Amadeus Authentication Failed: {e}")
        print(f"❌ Response Content: {e.response.content if e.response else 'No response'}")
        raise Exception('Failed to authenticate with Amadeus API.')


@csrf_exempt
@require_http_methods(["GET"])
def get_flights(request):
    """
    Fetch flight offers using the Amadeus API.
    """
    origin = request.GET.get('origin')
    destination = request.GET.get('destination')
    departure_date = request.GET.get('departure_date')

    if not (origin and destination and departure_date):
        return JsonResponse({'error': 'Missing required parameters (origin, destination, departure_date)'}, status=400)

    try:
        # Step 1: Authenticate with Amadeus and get access token
        token = get_amadeus_token()

        # Step 2: Fetch flight data
        response = requests.get(
            AMADEUS_FLIGHT_URL,
            headers={'Authorization': f'Bearer {token}'},
            params={
                'originLocationCode': origin,
                'destinationLocationCode': destination,
                'departureDate': departure_date,
                'adults': 1,  # Example: Fetch for 1 adult
            },
        )
        response.raise_for_status()
        flights = response.json()
        return JsonResponse(flights, safe=False)  # Return raw Amadeus API response
    except requests.RequestException as e:
        print(f"get_flights: Error fetching flights: {e}")
        return JsonResponse({'error': 'Failed to fetch flights', 'details': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_hotels(request):
    """
    Fetch hotel offers using the Amadeus API.
    """
    city_code = request.GET.get('city_code')
    check_in_date = request.GET.get('check_in_date')
    check_out_date = request.GET.get('check_out_date')

    if not (city_code and check_in_date and check_out_date):
        return JsonResponse({'error': 'Missing required parameters (city_code, check_in_date, check_out_date)'}, status=400)

    try:
        token = get_amadeus_token()
        response = requests.get(AMADEUS_HOTEL_URL, headers={
            'Authorization': f'Bearer {token}'
        }, params={
            'cityCode': city_code,
            'checkInDate': check_in_date,
            'checkOutDate': check_out_date,
            'adults': 1,
        })
        response.raise_for_status()
        hotels = response.json()
        return JsonResponse(hotels, safe=False)
    except requests.RequestException as e:
        print(f"get_hotels: Error fetching hotels: {e}")
        return JsonResponse({'error': 'Failed to fetch hotels', 'details': str(e)}, status=500)

@api_view(['POST'])
def send_whatsapp_message(request):
    """
    Sends a WhatsApp message using a Node.js WhatsApp service.
    """
    data = request.data
    recipient = data.get('recipient')  # WhatsApp number
    message = data.get('message')     # Message to send

    print("send_whatsapp_message: Request received")  # Debugging
    print(f"Recipient: {recipient}, Message: {message}")  # Debugging

    if not recipient or not message:
        print("send_whatsapp_message: Missing recipient or message")  # Debugging
        return Response({'error': 'Recipient and message are required'}, status=400)

    try:
        # Make a POST request to the Node.js service
        response = requests.post(
            'http://localhost:3001/send-message',  # Replace with Node.js service URL
            json={'recipient': recipient, 'message': message}
        )
        print("send_whatsapp_message: Node.js service response:", response.json())  # Debugging
        return Response(response.json(), status=response.status_code)
    except requests.exceptions.RequestException as e:
        print(f"send_whatsapp_message: Error communicating with Node.js service: {e}")  # Debugging
        return Response({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def chat_with_bot(request):
    try:
        data = json.loads(request.body)
        user_query = data.get('query', '').strip()

        if not user_query:
            return JsonResponse({'error': 'No query provided'}, status=400)

        # Detect flight-related queries
        if 'flight' in user_query.lower():
            origin, destination, departure_date = extract_flight_details(user_query)
            if not (origin and destination and departure_date):
                return JsonResponse({'error': 'Invalid flight query. Provide origin, destination, and date.'}, status=400)

            # Fetch flight data
            try:
                token = get_amadeus_token()
                response = requests.get(
                    AMADEUS_FLIGHT_URL,
                    headers={'Authorization': f'Bearer {token}'},
                    params={
                        'originLocationCode': origin,
                        'destinationLocationCode': destination,
                        'departureDate': departure_date,
                        'adults': 1,
                    },
                )
                response.raise_for_status()
                flight_data = response.json()

                # Format response for chatbot
                flight_responses = [
                    f"Flight: {flight['itineraries'][0]['segments'][0]['departure']['iataCode']} to {flight['itineraries'][0]['segments'][0]['arrival']['iataCode']}, Price: ${flight['price']['total']}"
                    for flight in flight_data.get('data', [])
                ]
                chatbot_response = "\n".join(flight_responses) if flight_responses else "No flights found."
            except Exception as e:
                chatbot_response = f"Error fetching flight details: {str(e)}"

            return JsonResponse({'response': chatbot_response}, status=200)

        # Handle general queries
        chatbot = ChatOllama(
            model="llama3.2:3b",
            host="http://localhost",
            port=11434,
            temperature=0
        )
        response = chatbot([
            SystemMessage(content="You are a travel guide chatbot."),
            HumanMessage(content=user_query)
        ])
        chatbot_response = response.content if response and response.content else "No response from chatbot"

        return JsonResponse({'response': chatbot_response}, status=200)

    except Exception as e:
        return JsonResponse({'error': 'Failed to process request', 'details': str(e)}, status=500)




import re

def extract_flight_details(query):
    """
    Extract flight details (origin, destination, and departure date) from user query.
    Example query: "Find flights from DEL to NYC on 2025-01-30"
    """
    origin_match = re.search(r'from (\w{3})', query, re.IGNORECASE)
    destination_match = re.search(r'to (\w{3})', query, re.IGNORECASE)
    date_match = re.search(r'on (\d{4}-\d{2}-\d{2})', query, re.IGNORECASE)

    origin = origin_match.group(1).upper() if origin_match else None
    destination = destination_match.group(1).upper() if destination_match else None
    departure_date = date_match.group(1) if date_match else None

    return origin, destination, departure_date


@csrf_exempt
@require_http_methods(["GET", "POST", "OPTIONS"])
def get_destination_details(request, destination_id):
    """
    Fetch details about a destination.
    """
    try:
        destination = Destination.objects.get(id=destination_id)
        places = Place.objects.filter(destination=destination).exclude(name__iexact='unknown').exclude(description__isnull=True).values('name', 'description', 'category')
        food = Food.objects.filter(destination=destination).exclude(name__iexact='unknown').exclude(description__isnull=True).values('name', 'description', 'cuisine_type')

        response_data = {
            'destination': {
                'name': destination.name,
                'city': destination.city,
                'description': destination.description,
                'best_time_to_visit': destination.best_time_to_visit,
                'tags': destination.tags or []
            },
            'places': list(places),
            'food': list(food)
        }
        return JsonResponse(response_data)

    except Destination.DoesNotExist:
        return JsonResponse({'error': 'Destination not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred', 'details': str(e)}, status=500)
