# -*- coding: utf-8 -*-
import pytest
from server import app

@pytest.fixture
def client():
    """Configure l'application Flask pour les tests."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_index_page(client):
    """Test d'accès à la page d'accueil."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Bienvenue" in response.data


def test_show_summary_valid_email(client):
    """Test avec un email valide."""
    response = client.post('/showSummary', data={
        'email': 'john@simplylift.co'  # Modifiez avec un email valide
    })
    assert response.status_code == 200
    assert b"Simply Lift" in response.data


def test_show_summary_invalid_email(client):
    """Test avec un email invalide."""
    response = client.post('/showSummary', data={
        'email': 'invalid@email.com'
    })
    assert response.status_code == 302  # Redirection
    assert "Email non trouvé" not in response.data.decode('utf-8')


def test_booking_page(client):
    """Test d'accès à la page de réservation."""
    response = client.get('/book/Fall%20Classic/Simply%20Lift')
    assert response.status_code == 200
    assert "Réserver des places pour la compétition" not in response.data.decode('utf-8')

def test_logout(client):
    """Test de déconnexion."""
    response = client.get('/logout')
    assert response.status_code == 302  # Redirection vers l'index
