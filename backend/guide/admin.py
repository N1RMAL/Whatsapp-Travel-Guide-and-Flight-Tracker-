from django.contrib import admin
from .models import Destination, Place, Food, ChatLog

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'best_time_to_visit')
    search_fields = ('name', 'city', 'tags')


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'destination', 'category')
    search_fields = ('name', 'destination__name', 'category')


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'destination', 'cuisine_type')
    search_fields = ('name', 'destination__name', 'cuisine_type')


@admin.register(ChatLog)
class ChatLogAdmin(admin.ModelAdmin):
    list_display = ('user_query', 'chatbot_response', 'timestamp')
    search_fields = ('user_query', 'chatbot_response')
