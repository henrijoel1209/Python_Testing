# -*- coding: utf-8 -*-
import pytest
from server import app, loadClubs


def utf8(data):
    """Encode une chaîne en UTF-8 pour éviter les erreurs
    de comparaison d'octets."""
    return data.encode('utf-8')


@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client


def test_show_summary_valid_email(client):
    clubs = loadClubs()
    valid_email = clubs[0]['email']
    response = client.post('/showSummary', data={'email': valid_email})

    assert response.status_code == 200
    assert utf8('Bienvenue') in response.data


def test_show_summary_invalid_email(client):
    response = client.post(
        '/showSummary', data={'email': 'invalid@example.com'},
        follow_redirects=True)

    assert response.status_code == 200
    assert utf8('Email non trouvé, veuillez réessayer.') in response.data


def test_show_summary_empty_email(client):
    response = client.post(
        '/showSummary', data={'email': ''}, follow_redirects=True)

    assert response.status_code == 200
    assert utf8('Email non trouvé, veuillez réessayer.') in response.data


def test_home_page(client):
    response = client.get('/')  # Accéder à la route d'accueil

    assert response.status_code == 200
    assert utf8(
        "Bienvenue sur le portail d'inscription GUDLFT !") in response.data


def test_public_points_table(client):
    # Accéder à la route des points publics
    response = client.get('/public_points')

    assert response.status_code == 200
    # Vérification du tableau
    assert utf8('Public Clubs Points Table') in response.data


def test_logout_redirect(client):
    response = client.get('/logout', follow_redirects=True)

    assert response.status_code == 200
    assert utf8(
        "Bienvenue sur le portail d'inscription GUDLFT !") in response.data
