from django.contrib import admin  # Add this import
from django.urls import path
from guide.views import get_destination_details, chat_with_bot, send_whatsapp_message

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/destination/<int:destination_id>/', get_destination_details, name='destination-details'),
    path('api/chat/', chat_with_bot, name='chat-with-bot'),
    path('send-whatsapp/', send_whatsapp_message, name='send_whatsapp_message'),
]
