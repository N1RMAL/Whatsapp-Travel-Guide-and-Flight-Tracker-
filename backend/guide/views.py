import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ObjectDoesNotExist

from .models import Destination, Place, Food, ChatLog

# LangChain Ollama imports
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
import json
import traceback

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


def set_cors_headers(response):
    """
    Adds CORS headers to the response object.
    """
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


@csrf_exempt
@require_http_methods(["POST"])
def chat_with_bot(request):
    print("chat_with_bot: Received request.")  # Debugging

    try:
        data = json.loads(request.body)
        print("chat_with_bot: Parsed data:", data)  # Debugging

        user_query = data.get('query', '').strip()
        print("chat_with_bot: User query:", user_query)  # Debugging

        if not user_query:
            print("chat_with_bot: No query provided.")  # Debugging
            return JsonResponse({'error': 'No query provided'}, status=400)

        # Initialize ChatOllama
        try:
            print("chat_with_bot: Initializing ChatOllama...")  # Debugging

            system_message = SystemMessage(content="""
                You are a travel guide chatbot. Your purpose is to provide information about destinations, places to visit, local cuisines, and best travel practices.

                You must:
                - Only respond to queries related to travel.
                - Politely decline to answer questions unrelated to travel.
                - Redirect the user to other resources if their query falls outside your scope.
            """)
            chatbot = ChatOllama(
                model="llama3.2:3b",
                host="http://localhost",
                port=11434,
                temperature=0
            )
            print("chat_with_bot: ChatOllama initialized successfully.")  # Debugging
        except Exception as e:
            print(f"chat_with_bot: Error initializing ChatOllama: {e}")  # Debugging
            return JsonResponse({'error': 'Failed to initialize chatbot', 'details': str(e)}, status=500)

        # Generate response
        try:
            print(f"chat_with_bot: Sending query to ChatOllama: {user_query}")  # Debugging
            response = chatbot([system_message, HumanMessage(content=user_query)])
            chatbot_response = response.content if response and response.content else "No response from chatbot"
            print(f"chat_with_bot: Response from ChatOllama: {chatbot_response}")  # Debugging
        except Exception as e:
            print(f"chat_with_bot: Error generating response: {e}")  # Debugging
            return JsonResponse({'error': 'Failed to generate response', 'details': str(e)}, status=500)

        # Save to database
        try:
            print("chat_with_bot: Saving chat log to database...")  # Debugging
            ChatLog.objects.create(user_query=user_query, chatbot_response=chatbot_response)
            print("chat_with_bot: Chat log saved successfully.")  # Debugging
        except Exception as e:
            print(f"chat_with_bot: Error saving chat log: {e}")  # Debugging
            return JsonResponse({'error': 'Failed to save chat log', 'details': str(e)}, status=500)

        print("chat_with_bot: Returning successful response.")  # Debugging
        return JsonResponse({'response': chatbot_response}, headers={'Access-Control-Allow-Origin': '*'}, status=200)

    except json.JSONDecodeError:
        print("chat_with_bot: Invalid JSON format.")  # Debugging
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except Exception as e:
        print(f"chat_with_bot: Unexpected error: {e}")  # Debugging
        return JsonResponse({'error': 'An unexpected error occurred', 'details': str(e)}, status=500)



@csrf_exempt
@require_http_methods(["GET", "POST", "OPTIONS"])
def get_destination_details(request, destination_id):
    print(f"get_destination_details: Received request for destination_id: {destination_id}")  # Debugging

    try:
        print("get_destination_details: Fetching destination from database...")  # Debugging
        destination = Destination.objects.get(id=destination_id)
        print(f"get_destination_details: Destination found: {destination.name}")  # Debugging

        print("get_destination_details: Fetching places and food for destination...")  # Debugging
        places = Place.objects.filter(destination=destination)\
       .exclude(name__iexact='unknown')\
       .exclude(description__isnull=True)\
       .values('name', 'description', 'category')
        
        food = Food.objects.filter(destination=destination)\
        .exclude(name__iexact='unknown')\
        .exclude(description__isnull=True)\
        .values('name', 'description', 'cuisine_type')

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
        print(f"get_destination_details: Response data prepared: {response_data}")  # Debugging
        return JsonResponse(response_data)

    except Destination.DoesNotExist:
        print("get_destination_details: Destination not found.")  # Debugging
        return JsonResponse({'error': 'Destination not found'}, status=404)
    except Exception as e:
        print(f"get_destination_details: Unexpected error: {e}")  # Debugging
        print(traceback.format_exc())  # Debugging
        return JsonResponse({'error': 'An unexpected error occurred', 'details': str(e)}, status=500)
