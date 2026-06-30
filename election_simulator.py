from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import plotly.io as pio

import os

from core.election_game import ElectionGame

import uuid

# Store games
games = {}

# Define game
election_game = ElectionGame()

# Define app
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "development-secret-key"
)

# Function to manage games
def _get_game():
    # If first visit
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    
    sid = session["session_id"]

    # Find sid in games
    if sid not in games:
        games[sid] = ElectionGame()
    
    return games[sid]

# Function to validate if user has finished game
def _validate_game(game):
    # Check turn
    # If less than or equal to max turn, then return False
    if game.turn <= game.TURN_MAX:
        return False
    return True

# Home page
@app.route("/")
def index():

    return render_template(
        "index.html"
    )

# Main game loop
@app.route("/game")
def game():

    game = _get_game()

    # Return user to 'election' page if they completed
    validation = _validate_game(game)
    
    # If player has completed game, redirect to game
    if validation:
        return redirect(url_for("election"))
    
    # Run election
    game.run_election()

    # Get map figure for current turn
    fig = game.get_turn_map_figure()

    # Convert graph to html
    graph_html = pio.to_html(
        fig,
        full_html=False,
        include_plotlyjs="cdn",
        config={
            "responsive": True,
            "displayModeBar": False
        }
    )

    # Render voteshare and trendline as html
    voteshare_html = game.renderer.render_voteshare_html()
    trend_fig = game.renderer.create_voteshare_trend_graph()

    # Convert trend to html
    trend_html = pio.to_html(
        trend_fig,
        full_html=False,
        include_plotlyjs=False,
        config={
            "responsive": True,
            "displayModeBar": False
        }
    )

    # Render parliament map
    fig_parliament = game.renderer.create_parliament_graph(
        margin_tolerance = 5 if game.turn > 1 else 0
    )

    # To HTML
    parliament_html = pio.to_html(
        fig_parliament,
        full_html=False,
        include_plotlyjs=False,
        config={
            "responsive": True,
            "displayModeBar": False
        }
    )

    # Archetype key
    archetype_key_html = game.renderer.render_archetype_key()

    # Turn data
    turn_data = game.get_turn_data()

    # Return all
    return render_template(
        "game.html",
        plot=graph_html,
        voteshare=voteshare_html,
        trend_plot=trend_html,
        parliament=parliament_html,
        archetype_key=archetype_key_html,
        turn=game.turn,
        max_turn=game.TURN_MAX,
        turn_data=turn_data
    )

# Choice handling
@app.route("/submit_choice", methods=["POST"])
def submit_choice():

    game = _get_game()

    # Get data
    data = request.json
    choice = data["choice"]

    # Handle choice and get advisor response
    advisor_feedback = game.handle_choice(choice)

    # Return
    return jsonify({
        "success": True,
        "advisor_feedback": advisor_feedback
    })

# Stepping voteshare
@app.route("/step", methods=["POST"])
def step():

    game = _get_game()

    # Move to next election step
    done = game.next_election_step()

    # Return
    return jsonify({
        "done": done,
        "turn": game.turn,
        "max_turn": game.TURN_MAX,
        "voteshare": game.current_voteshare
    })

# Election page
@app.route("/election")
def election():

    game = _get_game()

    # Return user to 'game' page if they haven't completed
    validation = _validate_game(game)
    
    # If player hasnt completed game, redirect to game
    if not validation:
        return redirect(url_for("game"))

    # Parliament figure
    fig = game.renderer.plot_final_seats(
        map_title="",
        margin_tolerance=999
    )

    # To HTML
    seat_map_html = pio.to_html(
        fig,
        full_html=False,
        include_plotlyjs="cdn",
        config={
            "responsive": True,
            "displayModeBar": False
        }
    )

    # Chart and running total
    chart, running_total, _ = game.renderer.results_parliament_graph(
        margin_tolerance=999
    )

    chart_html = pio.to_html(
        chart,
        full_html=False,
        include_plotlyjs=False,
        config={
            "responsive": True,
            "displayModeBar": False
        }
    )

    voteshare = game.renderer.live_voteshare_graph(running_total)

    voteshare_html = pio.to_html(
        voteshare,
        full_html=False,
        include_plotlyjs=False,
        config={
            "responsive": True,
            "displayModeBar": False
        }
    )

    return render_template(
        "results.html",
        plot=seat_map_html,
        parliament=chart_html,
        voteshare=voteshare_html
    )

# Counting votes in result page
@app.route("/count_votes", methods=["POST"])
def count_votes():

    game = _get_game()

    # Count votes
    return jsonify(
        game.count_next_votes()
    )

# Conclusion page
@app.route("/conclusion")
def conclusion():

    game = _get_game()

    # Return user to 'game' page if they haven't completed
    validation = _validate_game(game)
    
    # If player hasnt completed game, redirect to game
    if not validation:
        return redirect(url_for("game"))

    # Seats figure
    fig_seats = game.renderer.plot_seats_results(map_title="")

    # Convert to html
    seats_html = pio.to_html(
        fig_seats,
        full_html=False,
        include_plotlyjs="cdn",
        config={
            "responsive": True,
            'displayModeBar': False,
        }
    )

    # Parliament
    fig_parliament = game.renderer.create_parliament_graph(
        margin_tolerance=0
    )

    parliament_html = pio.to_html(
        fig_parliament,
        full_html=False,
        include_plotlyjs=False,
        config={
            "responsive": True,
            "displayModeBar": False
        }
    )

    # Table
    table_html = game.renderer.render_results_table_html()

    # Outcome title and text
    title, text = game.get_outcome_text()

    # Archetype key
    archetype_key_html = game.renderer.render_archetype_key()

    return render_template(
        "conclusion.html",
        seats=seats_html,
        parliament=parliament_html,
        results_table=table_html,
        outcome_title=title,
        outcome_text=text,
        archetype_key=archetype_key_html
    )

# Creating a new game
@app.route("/reset_game", methods=["POST"])
def reset_game():

    game = _get_game()

    game.new_game()

    return jsonify({
        "success": True
    })


# Initiate software
if __name__ == "__main__":
    app.run(
        debug=False,
        host="0.0.0.0",
        port=5000
    )
