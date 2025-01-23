from django.db import models
from django.utils import timezone

class Destination(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100, default="Unknown")  # Added field for city/region
    description = models.TextField()
    best_time_to_visit = models.CharField(max_length=50)
    tags = models.JSONField(null=True, blank=True)  # Optional tags for filtering/searching

    def __str__(self):
        return self.name


class Place(models.Model):
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='places')
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=50, null=True, blank=True)  # Optional category (e.g., "Park", "Museum")

    def __str__(self):
        return self.name


class Food(models.Model):
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='foods')
    name = models.CharField(max_length=100)
    description = models.TextField()
    cuisine_type = models.CharField(max_length=50, null=True, blank=True)  # Optional type (e.g., "South Indian")

    def __str__(self):
        return self.name


class ChatLog(models.Model):
    user_query = models.TextField()
    chatbot_response = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    context = models.JSONField(null=True, blank=True)  # Store additional context if needed

    def __str__(self):
        return f"Query: {self.user_query[:30]} - Response: {self.chatbot_response[:30]}"
