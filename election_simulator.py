from flask import Flask, render_template, jsonify, request
import plotly.io as pio

import logging
import webbrowser
from threading import Timer

from core.election_game import ElectionGame

# Define game
election_game = ElectionGame()

# Define app
app = Flask(__name__)

# Home page
@app.route("/")
def index():

    return render_template(
        "index.html"
    )

# Main game loop
@app.route("/game")
def game():
    
    # Run election
    election_game.run_election()

    # Get map figure for current turn
    fig = election_game.get_turn_map_figure()

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
    voteshare_html = election_game.renderer.render_voteshare_html()
    trend_fig = election_game.renderer.create_voteshare_trend_graph()

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
    fig_parliament = election_game.renderer.create_parliament_graph(
        margin_tolerance = 5 if election_game.turn > 1 else 0
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
    archetype_key_html = election_game.renderer.render_archetype_key()

    # Turn data
    turn_data = election_game.get_turn_data()

    # Return all
    return render_template(
        "game.html",
        plot=graph_html,
        voteshare=voteshare_html,
        trend_plot=trend_html,
        parliament=parliament_html,
        archetype_key=archetype_key_html,
        turn=election_game.turn,
        max_turn=election_game.TURN_MAX,
        turn_data=turn_data
    )

# Choice handling
@app.route("/submit_choice", methods=["POST"])
def submit_choice():

    # Get data
    data = request.json
    choice = data["choice"]

    # Handle choice and get advisor response
    advisor_feedback = election_game.handle_choice(choice)

    # Return
    return jsonify({
        "success": True,
        "advisor_feedback": advisor_feedback
    })

# Stepping voteshare
@app.route("/step", methods=["POST"])
def step():
    # Move to next election step
    done = election_game.next_election_step()

    # Return
    return jsonify({
        "done": done,
        "turn": election_game.turn,
        "max_turn": election_game.TURN_MAX,
        "voteshare": election_game.current_voteshare
    })

# Election page
@app.route("/election")
def election():

    # Parliament figure
    fig = election_game.renderer.plot_final_seats(
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
    chart, running_total, _ = election_game.renderer.results_parliament_graph(
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

    voteshare = election_game.renderer.live_voteshare_graph(running_total)

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
    # Count votes
    return jsonify(
        election_game.count_next_votes()
    )

# Conclusion page
@app.route("/conclusion")
def conclusion():
    # Seats figure
    fig_seats = election_game.renderer.plot_seats_results(map_title="")

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
    fig_parliament = election_game.renderer.create_parliament_graph(
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
    table_html = election_game.renderer.render_results_table_html()

    # Outcome title and text
    title, text = election_game.get_outcome_text()

    # Archetype key
    archetype_key_html = election_game.renderer.render_archetype_key()

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
    election_game.new_game()

    return jsonify({
        "success": True
    })

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

def open_browser():
    webbrowser.open("http://127.0.0.1:5000/")

# Initiate software
if __name__ == "__main__":
    Timer(1, open_browser).start()
    app.run(
        debug=False,
        host="0.0.0.0",
        port=5000
    )
