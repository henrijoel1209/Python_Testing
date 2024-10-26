import random
from locust import HttpUser, TaskSet, between, task
from datetime import datetime

# Liste des clubs avec leurs emails
clubs = [
    {"name": "Simply Lift", "email": "john@simplylift.co"},
    {"name": "Iron Temple", "email": "admin@irontemple.com"},
    {"name": "She Lifts", "email": "kate@shelifts.co.uk"},
]

# Liste des compétitions
competitions = [
    {"name": "Spring Festival", "date": "2024-11-01 10:00:00"},
    {"name": "Fall Classic", "date": "2024-12-05 13:30:00"},
]

class UserBehavior(TaskSet):
    """Définit le comportement d'un utilisateur pour le test."""

    def on_start(self):
        """Simule la connexion avec un email aléatoire."""
        self.club = random.choice(clubs)
        response = self.client.post("/showSummary", data={
            "email": self.club["email"]
        })
        if response.status_code == 200:
            print(f"Connexion réussie pour {self.club['name']}")
        else:
            print(f"Erreur de connexion : {response.text}")

    @task(1)
    def load_competitions(self):
        """Charge la page des compétitions."""
        response = self.client.post("/showSummary", data={
            "email": self.club["email"]
        })
        if response.status_code == 200:
            print(f"Compétitions chargées pour {self.club['name']}")
        else:
            print(f"Erreur chargement compétitions : {response.text}")

    @task(1)
    def load_points(self):
        """Charge la page des points publics."""
        response = self.client.get("/public_points")
        if response.status_code == 200:
            print(f"Points chargés pour {self.club['name']}")
        else:
            print(f"Erreur chargement points : {response.text}")

    @task(1)
    def book_places(self):
        """Réserve un nombre aléatoire de places dans une compétition."""
        future_competitions = [
            comp for comp in competitions
            if datetime.strptime(comp['date'], "%Y-%m-%d %H:%M:%S") >= datetime.now()
        ]

        if not future_competitions:
            print("Aucune compétition disponible pour réservation.")
            return

        competition = random.choice(future_competitions)
        places_to_book = random.randint(1, 5)

        response = self.client.post(
            "/purchasePlaces",
            data={
                "competition": competition['name'],
                "club": self.club['name'],
                "places": places_to_book
            }
        )
        if response.status_code == 200:
            print(f"Réservation de {places_to_book} places pour {competition['name']} réussie.")
        else:
            print(f"Erreur lors de la réservation : {response.text}")


class WebsiteUser(HttpUser):
    """Utilisateur qui va exécuter les tâches définies."""
    tasks = [UserBehavior]
    wait_time = between(1, 5)
