from django.core.management.base import BaseCommand
from guide.models import Destination, Place, Food

class Command(BaseCommand):
    help = "Seeds the database with initial travel guide data."

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting database seeding...")

        # Seed destinations, places, and food
        self.seed_destinations()
        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))

    def seed_destinations(self):
        destinations_data = [
            {
                "name": "Paris",
                "description": "The capital city of France, known for its art, fashion, and culture.",
                "best_time_to_visit": "April to June, September to November",
                "places": [
                    {"name": "Eiffel Tower", "description": "Iconic landmark of Paris."},
                    {"name": "Louvre Museum", "description": "World's largest art museum."}
                ],
                "food": [
                    {"name": "Croissant", "description": "Buttery and flaky pastry."},
                    {"name": "Baguette", "description": "Traditional French bread."}
                ]
            },
            {
                "name": "New Delhi",
                "description": "Capital of India, a blend of history and modernity.",
                "best_time_to_visit": "October to March",
                "places": [
                    {"name": "India Gate", "description": "War memorial and iconic landmark."},
                    {"name": "Qutub Minar", "description": "Historic minaret and UNESCO site."}
                ],
                "food": [
                    {"name": "Butter Chicken", "description": "Famous North Indian dish."},
                    {"name": "Chaat", "description": "Popular street food snack."}
                ]
            }
        ]

        for data in destinations_data:
            destination, created = Destination.objects.get_or_create(
                name=data["name"],
                defaults={
                    "description": data["description"],
                    "best_time_to_visit": data["best_time_to_visit"]
                }
            )
            if created:
                self.stdout.write(f"Added destination: {destination.name}")
            else:
                self.stdout.write(f"Skipped existing destination: {destination.name}")

            # Seed places
            for place_data in data["places"]:
                place, created = Place.objects.get_or_create(
                    destination=destination,
                    name=place_data["name"],
                    defaults={"description": place_data["description"]}
                )
                if created:
                    self.stdout.write(f"  Added place: {place.name}")
                else:
                    self.stdout.write(f"  Skipped existing place: {place.name}")

            # Seed food
            for food_data in data["food"]:
                food, created = Food.objects.get_or_create(
                    destination=destination,
                    name=food_data["name"],
                    defaults={"description": food_data["description"]}
                )
                if created:
                    self.stdout.write(f"  Added food: {food.name}")
                else:
                    self.stdout.write(f"  Skipped existing food: {food.name}")
