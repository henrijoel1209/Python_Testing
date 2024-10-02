import json
from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import datetime

# Load clubs and competitions once, and store in memory
def loadClubs():
    with open('clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

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
    club = next((club for club in clubs if club['email'] == request.form['email']), None)
    
    # Filter competitions to only show those in the future and after 01 Oct 2024
    future_competitions = [comp for comp in competitions 
                           if datetime.strptime(comp['date'], '%Y-%m-%d %H:%M:%S') >= min_allowed_date]
    
    if club:
        return render_template('welcome.html', club=club, competitions=future_competitions, clubs=clubs)
    else:
        flash("Email not found, please try again.")
        return redirect(url_for('index'))


@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)
    
    # Check if club and competition exist
    if not foundClub or not foundCompetition:
        flash("Invalid club or competition.")
        return redirect(url_for('showSummary'))
    
    # Check if the competition date is in the future
    competition_date = datetime.strptime(foundCompetition['date'], '%Y-%m-%d %H:%M:%S')
    if competition_date < min_allowed_date:
        flash("You cannot book for past competitions.")
        return redirect(url_for('showSummary'))
    
    return render_template('booking.html', club=foundClub, competition=foundCompetition)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = next((c for c in competitions if c['name'] == request.form['competition']), None)
    club = next((c for c in clubs if c['name'] == request.form['club']), None)
    placesRequired = int(request.form['places'])
    
    # Check if club and competition exist
    if not competition or not club:
        flash("Invalid club or competition.")
        return redirect(url_for('showSummary'))
    
    # Check if the competition date is in the future
    competition_date = datetime.strptime(competition['date'], '%Y-%m-%d %H:%M:%S')
    if competition_date < min_allowed_date:
        flash("You cannot book for past competitions.")
        return redirect(url_for('showSummary'))

    club_reserved_places = club_reservations[club['name']].get(competition['name'], 0)
    
    # Check if the club is trying to reserve more than 12 places in total
    if club_reserved_places + placesRequired > 12:
        flash(f"You cannot reserve more than 12 places for this competition. "
              f"You have already reserved {club_reserved_places} places.")
        return redirect(url_for('book', competition=competition['name'], club=club['name']))
    
    if placesRequired <= 0:
        flash("Invalid number of places requested. Please enter a positive number.")
        return redirect(url_for('book', competition=competition['name'], club=club['name']))
    elif placesRequired > 12:
        flash("You cannot book more than 12 places.")
        return redirect(url_for('book', competition=competition['name'], club=club['name']))
    elif placesRequired > int(competition['numberOfPlaces']):
        flash(f"Only {competition['numberOfPlaces']} places available.")
        return redirect(url_for('book', competition=competition['name'], club=club['name']))
    elif placesRequired > int(club['points']):
        flash(f"You only have {club['points']} points available.")
        return redirect(url_for('book', competition=competition['name'], club=club['name']))
    else:
        competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired
        club['points'] = int(club['points']) - placesRequired  # Deduct points from the club
        
        # Update the number of places the club has reserved for this competition
        club_reservations[club['name']][competition['name']] = club_reserved_places + placesRequired
        
        flash('Great, booking complete!')
        return render_template('welcome.html', club=club, competitions=competitions, clubs=clubs)

# Route for public view of clubs' points
@app.route('/public_points.html')
def publicPoints():
    return render_template('public_points.html', clubs=clubs)

@app.route('/logout')
def logout():
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
