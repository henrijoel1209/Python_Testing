# -*- coding: utf-8 -*-
import json
from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'something_special'


# Charger les clubs et compétitions une fois en mémoire
def loadClubs():
    with open('clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        return listOfCompetitions


# Initialiser les compétitions et les clubs
competitions = loadCompetitions()
clubs = loadClubs()

# Suivre le nombre de réservations par club et compétition
club_reservations = {club['name']: {} for club in clubs}

# Date minimale autorisée pour les compétitions : 1er octobre 2024
min_allowed_date = datetime(2024, 10, 1)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['POST'])
def showSummary():
    club = next(
        (club for club in clubs if club['email'] == request.form['email']),
        None
    )

    future_competitions = [
        comp for comp in competitions
        if datetime.strptime(comp['date'], '%Y-%m-%d %H:%M:%S') >= min_allowed_date
    ]

    if club:
        return render_template(
            'welcome.html',
            club=club,
            competitions=future_competitions,
            clubs=clubs
        )
    flash("Email non trouvé, veuillez réessayer.")
    return redirect(url_for('index'))


@app.route('/welcome')
def welcome():
    club = request.args.get('club')
    current_time = datetime.now()

    future_competitions = [
        comp for comp in competitions
        if datetime.strptime(comp['date'], "%Y-%m-%d %H:%M:%S") > current_time
    ]

    return render_template(
        'welcome.html',
        club=club,
        competitions=future_competitions
    )


@app.route('/book/<competition>/<club>', methods=['GET', 'POST'])
def book(competition, club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next(
        (c for c in competitions if c['name'] == competition),
        None
    )

    if not foundClub or not foundCompetition:
        flash("Club ou compétition invalide.")
        return redirect(url_for('showSummary'))

    competition_date = datetime.strptime(
        foundCompetition['date'], '%Y-%m-%d %H:%M:%S'
    )

    if competition_date < min_allowed_date:
        flash("Vous ne pouvez pas réserver pour des compétitions passées.")
        return redirect(url_for('showSummary'))

    return render_template(
        'booking.html',
        club=foundClub,
        competition=foundCompetition
    )


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = next(
        (c for c in competitions if c['name'] == request.form['competition']),
        None
    )

    club = next((c for c in clubs if c['name'] == request.form['club']), None)

    if not competition or not club:
        flash("Club ou compétition invalide.")
        return redirect(url_for('showSummary'))

    try:
        placesRequired = int(request.form['places'])
    except ValueError:
        flash("Entrée invalide pour le nombre de places.")
        return redirect(url_for('book', competition=competition['name'],
                                club=club['name']))

    competition_date = datetime.strptime(
        competition['date'], '%Y-%m-%d %H:%M:%S'
    )
    if competition_date < min_allowed_date:
        flash("Vous ne pouvez pas réserver pour des compétitions passées.")
        return redirect(url_for('showSummary'))

    club_reserved_places = club_reservations[club['name']].get(
        competition['name'], 0
    )

    if club_reserved_places + placesRequired > 12:
        message = (
            f"Vous ne pouvez pas réserver plus de 12 places. "
            f"Vous avez déjà réservé {club_reserved_places} places."
        )
        flash(message)

        future_competitions = [
            comp for comp in competitions
            if datetime.strptime(comp['date'], '%Y-%m-%d %H:%M:%S') >= min_allowed_date
        ]

        return render_template(
            'welcome.html',
            club=club,
            competitions=future_competitions,
            clubs=clubs
        )

    if placesRequired <= 0:
        flash("Nombre de places demandé invalide.")
        return redirect(url_for('book', competition=competition['name'],
                                club=club['name']))

    elif placesRequired > 12:
        flash("Vous ne pouvez pas réserver plus de 12 places.")
        return redirect(url_for('book', competition=competition['name'],
                                club=club['name']))

    elif placesRequired > int(competition['numberOfPlaces']):
        flash(f"Seulement {competition['numberOfPlaces']} places disponibles.")
        return redirect(url_for('book', competition=competition['name'],
                                club=club['name']))

    elif placesRequired > int(club['points']):
        flash(f"Vous n'avez que {club['points']} points disponibles.")
        return redirect(url_for('book', competition=competition['name'],
                                club=club['name']))

    else:
        available_places = int(competition['numberOfPlaces'])
        competition['numberOfPlaces'] = available_places - placesRequired
        club['points'] = int(club['points']) - placesRequired
        club_reservations[club['name']][competition['name']] = (
            club_reserved_places + placesRequired
        )

        flash('Super, réservation complétée !')

        future_competitions = [
            comp for comp in competitions
            if datetime.strptime(comp['date'], '%Y-%m-%d %H:%M:%S') >= min_allowed_date
        ]

        return render_template(
            'welcome.html',
            club=club,
            competitions=future_competitions,
            clubs=clubs
        )


@app.route('/public_points')
def publicPoints():
    return render_template('public_points.html', clubs=clubs)


@app.route('/logout')
def logout():
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
