# -*- coding: utf-8 -*-
import pytest
from server import app, loadClubs

# Fixture client : fournit un client de test pour simuler les requêtes HTTP
@pytest.fixture
def client():
    """Active le mode test et crée un client Flask."""
    app.testing = True
    with app.test_client() as client:
        yield client

# 1. Test : Afficher le résumé avec un email valide
def test_show_summary_valid_email(client):
    """Test /showSummary avec un email valide."""
    clubs = loadClubs()
    valid_email = clubs[0]['email']  # Email du 1er club

    response = client.post(
        '/showSummary', data={'email': valid_email}
    )

    assert response.status_code == 200
    assert 'Bienvenue'.encode('utf-8') in response.data

# 2. Test : Afficher le résumé avec un email invalide
def test_show_summary_invalid_email(client):
    """Test /showSummary avec un email invalide."""
    response = client.post(
        '/showSummary',
        data={'email': 'invalid@example.com'},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert 'Email non trouvé'.encode('utf-8') in response.data

# 3. Test : Afficher le résumé avec un email vide
def test_show_summary_empty_email(client):
    """Test /showSummary avec un email vide."""
    response = client.post(
        '/showSummary',
        data={'email': ''},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert 'Email non trouvé'.encode('utf-8') in response.data

# 4. Test : Accéder à la page d'accueil
def test_home_page(client):
    """Test d'accès à la page d'accueil."""
    response = client.get('/')

    assert response.status_code == 200
    assert (
        b"Bienvenue sur le portail d'inscription GUDLFT !"
        in response.data
    )

# 5. Test : Affichage du tableau public des points
def test_public_points_table(client):
    """Test d'affichage du tableau public des points."""
    response = client.get('/public_points')

    assert response.status_code == 200
    assert b'Public Clubs Points Table' in response.data

# 6. Test : Déconnexion et redirection vers la page d'accueil
def test_logout_redirect(client):
    """Test de la déconnexion et de la redirection."""
    response = client.get('/logout', follow_redirects=True)

    assert response.status_code == 200
    assert (
        b"Bienvenue sur le portail d'inscription GUDLFT !"
        in response.data
    )
