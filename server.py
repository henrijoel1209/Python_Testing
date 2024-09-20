import json
import time
from flask import Flask, render_template, request, redirect, flash, url_for

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


@app.route('/')
def index():
    return render_template('index.html')


# Measure the time taken to retrieve competitions list
@app.route('/showSummary', methods=['POST'])
def showSummary():
    start_time = time.time()  # Start time for performance measurement
    
    club = next((club for club in clubs if club['email'] == request.form['email']), None)
    if club:
        elapsed_time = time.time() - start_time  # Calculate elapsed time
        if elapsed_time > 5:  # Check if the operation exceeds 5 seconds
            flash(f"Loading competitions took too long ({elapsed_time:.2f} seconds).")
        return render_template('welcome.html', club=club, competitions=competitions, clubs=clubs)
    else:
        flash("Email not found, please try again.")
        return redirect(url_for('index'))


@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)
    if foundClub and foundCompetition:
        return render_template('booking.html', club=foundClub, competition=foundCompetition)
    else:
        flash("Something went wrong-please try again.")
        return redirect(url_for('showSummary'))


# Measure the time taken to update points and ensure it's under 2 seconds
@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    start_time = time.time()  # Start time for performance measurement
    
    competition = next((c for c in competitions if c['name'] == request.form['competition']), None)
    club = next((c for c in clubs if c['name'] == request.form['club']), None)
    placesRequired = int(request.form['places'])

    if competition and club:
        if placesRequired <= 0:
            flash("Invalid number of places requested.")
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
            
            elapsed_time = time.time() - start_time  # Calculate elapsed time
            if elapsed_time > 2:  # Check if the operation exceeds 2 seconds
                flash(f"Updating points took too long ({elapsed_time:.2f} seconds).")
            
            flash('Great, booking complete!')
            return render_template('welcome.html', club=club, competitions=competitions, clubs=clubs)
    else:
        flash("Invalid club or competition.")
        return redirect(url_for('index'))


# Route for public view of clubs' points
@app.route('/public_points.html')
def publicPoints():
    return render_template('public_points.html', clubs=clubs)

@app.route('/logout')
def logout():
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
