import json
from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'something_special'

# Load clubs and competitions once, and store in memory
def loadClubs():
    with open('clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs

def loadCompetitions():
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        return listOfCompetitions

# Load clubs and competitions into memory to avoid repeated file reads
competitions = loadCompetitions()
clubs = loadClubs()

# Track the number of places each club has already reserved for a competition
club_reservations = {club['name']: {} for club in clubs}

# Define the minimum competition date allowed for booking (01 Oct 2024)
min_allowed_date = datetime(2024, 10, 1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary', methods=['POST'])
def showSummary():
    # Retrieve the club based on the email provided
    club = next((club for club in clubs if club['email'] == request.form['email']), None)
    
    # Filter competitions to only show those in the future and after 01 Oct 2024
    future_competitions = [comp for comp in competitions 
                           if datetime.strptime(comp['date'], '%Y-%m-%d %H:%M:%S') >= min_allowed_date]
    
    if club:
        return render_template('welcome.html', club=club, competitions=future_competitions, clubs=clubs)
    else:
        flash("Email non trouvé, veuillez réessayer.")
        return redirect(url_for('index'))

@app.route('/welcome')
def welcome():
    club = request.args.get('club')  # Retrieve the club from the request
    # Filter the competitions to show only upcoming ones
    current_time = datetime.now()
    future_competitions = [
        comp for comp in competitions
        if datetime.strptime(comp['date'], "%Y-%m-%d %H:%M:%S") > current_time
    ]

    return render_template('welcome.html', club=club, competitions=future_competitions)

@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)
    
    if not foundClub or not foundCompetition:
        flash("Club ou compétition invalide.")
        return redirect(url_for('showSummary'))
    
    competition_date = datetime.strptime(foundCompetition['date'], '%Y-%m-%d %H:%M:%S')
    if competition_date < min_allowed_date:
        flash("Vous ne pouvez pas réserver pour des compétitions passées.")
        return redirect(url_for('showSummary'))
    
    return render_template('booking.html', club=foundClub, competition=foundCompetition)

@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = next((c for c in competitions if c['name'] == request.form['competition']), None)
    club = next((c for c in clubs if c['name'] == request.form['club']), None)
    
    if not competition or not club:
        flash("Club ou compétition invalide.")
        return redirect(url_for('showSummary'))

    try:
        placesRequired = int(request.form['places'])
    except ValueError:
        flash("Entrée invalide pour le nombre de places. Veuillez entrer un nombre valide.")
        return redirect(url_for('book', competition=competition['name'], club=club['name']))

    competition_date = datetime.strptime(competition['date'], '%Y-%m-%d %H:%M:%S')
    if competition_date < min_allowed_date:
        flash("Vous ne pouvez pas réserver pour des compétitions passées.")
        return redirect(url_for('showSummary'))

    club_reserved_places = club_reservations[club['name']].get(competition['name'], 0)
    
    if club_reserved_places + placesRequired > 12:
        flash(f"Vous ne pouvez pas réserver plus de 12 places pour cette compétition. "
              f"Vous avez déjà réservé {club_reserved_places} places.")
        # Redirect to welcome.html with the error message
        future_competitions = [comp for comp in competitions 
                               if datetime.strptime(comp['date'], '%Y-%m-%d %H:%M:%S') >= min_allowed_date]
        return render_template('welcome.html', club=club, competitions=future_competitions, clubs=clubs)
    
    if placesRequired <= 0:
        flash("Nombre de places demandé invalide. Veuillez entrer un nombre positif.")
        return redirect(url_for('book', competition=competition['name'], club=club['name']))
    elif placesRequired > 12:
        flash("Vous ne pouvez pas réserver plus de 12 places.")
        return redirect(url_for('book', competition=competition['name'], club=club['name']))
    elif placesRequired > int(competition['numberOfPlaces']):
        flash(f"Seulement {competition['numberOfPlaces']} places disponibles.")
        return redirect(url_for('book', competition=competition['name'], club=club['name']))
    elif placesRequired > int(club['points']):
        flash(f"Vous n'avez que {club['points']} points disponibles.")
        return redirect(url_for('book', competition=competition['name'], club=club['name']))
    else:
        # Update the number of reserved places
        competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired
        club['points'] = int(club['points']) - placesRequired  # Deduct points from the club
        
        club_reservations[club['name']][competition['name']] = club_reserved_places + placesRequired
        
        flash('Super, réservation complétée !')

        # Filter future competitions for redirection
        future_competitions = [comp for comp in competitions 
                               if datetime.strptime(comp['date'], '%Y-%m-%d %H:%M:%S') >= min_allowed_date]

        return render_template('welcome.html', club=club, competitions=future_competitions, clubs=clubs)

@app.route('/public_points.html')
def publicPoints():
    return render_template('public_points.html', clubs=clubs)

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
