import json
from flask import Flask, render_template, request, redirect, flash, url_for


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

competitions = loadCompetitions()
clubs = loadClubs()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['POST'])
def showSummary():
    club = next((club for club in clubs if club['email'] == request.form['email']), None)
    if club:
        return render_template('welcome.html', club=club, competitions=competitions)
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


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = next((c for c in competitions if c['name'] == request.form['competition']), None)
    club = next((c for c in clubs if c['name'] == request.form['club']), None)
    placesRequired = int(request.form['places'])

    if competition and club:
        if placesRequired <= 0:
            flash("Invalid number of places requested.")
        elif placesRequired > int(competition['numberOfPlaces']):
            flash(f"Only {competition['numberOfPlaces']} places available.")
        else:
            competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired
            flash('Great-booking complete!')
        return render_template('welcome.html', club=club, competitions=competitions)
    else:
        flash("Invalid club or competition.")
        return redirect(url_for('index'))


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
