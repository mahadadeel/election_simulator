import random
import math

import json
from pathlib import Path

from models.party import Party
from core.map_generator import MapGenerator
from render.graph_renderer import GraphRenderer

# Main Election Game Class
class ElectionGame:

    # Max turn
    TURN_MAX = 20

    # Starting Voteshare
    STARTING_VOTESHARE = [14.7, 35.2, 39.6, 10.5]

    # Target end voteshare
    _TARGET_END_VOTESHARE = [35.0, 15.0, 25.0, 25.0]

    # Karma cap
    _KARMA_CAP = 6.0

    # File handling
    _CORE_DIR = Path(__file__).resolve().parent
    _PROJECT_DIR = _CORE_DIR.parent

    _GAME_SCRIPT_DIR = _PROJECT_DIR / "game_script"

    _TURN_DATA_PATH = _GAME_SCRIPT_DIR / "turn_data.json"
    _OUTCOMES_PATH = _GAME_SCRIPT_DIR / "possible_outcomes.json"

    # Margins when counting results
    _COUNTING_MARGINS = [
        35,
        30,
        27,
        23,
        20,
        17,
        15,
        12,
        10,
        8,
        7,
        6,
        5,
        4,
        3,
        2.5,
        2,
        1.5,
        1,
        0.5,
        0
    ]

    # Turn data
    with open(_TURN_DATA_PATH, "r", encoding="utf-8") as f:
        _TURN_DATA = json.load(f)["turns"]

    # Possible outcomes
    with open(_OUTCOMES_PATH, "r", encoding="utf-8") as f:
        _POSSIBLE_OUTCOMES = json.load(f)

    # Initialisation
    def __init__(
        self,
        total_seats=650
    ):

        # Set total seats in game
        self.total_seats = total_seats

        # New game variables
        self.new_game()

        # Graph renderer
        self.renderer = GraphRenderer(self)

        # Lambda to get turn data
        self.get_turn_data = lambda : self._TURN_DATA[self.turn - 1]
    
    # Function to define all variables for a new (or restarted) game
    def new_game(self):

        # Define turn
        self.turn = 1

        # Copy starting voteshare to current and record

        self.current_voteshare = self.STARTING_VOTESHARE.copy()

        self.voteshare_record = [
            self.STARTING_VOTESHARE.copy()
        ]

        # Define karma (rewards/subtracts voteshare depending on policy decisions)
        self._karma = [0.0, 0.0, 0.0, 0.0]

        # Define other empty variables
        self.final_results = []
        
        # Define starting seats
        self.starting_seats = None
        
        # Define election count step
        self.election_count_step = 0

        # Define majority announced
        self.majority_announced = False

        # Define majority threshold
        self.majority_threshold = math.ceil(self.total_seats / 2)

        # Define parties
        self.parties = self._create_parties()

        # Define seat total
        self.seat_total = None

        # Define seats
        self.seats = MapGenerator(
            total_seats = self.total_seats
        ).generate()
    
    # Function to create the parties for this election
    def _create_parties(self):
        far_right = Party(
            name="Alternative Party",
            colour="#00c7c0",
            poll = 0,
            tactical_vote = 5,
            base_support = -0.3,
            weights = {
            "urban": -0.9,
            "industry": 0.6,
            "wealth": -0.2,
            "education": -0.6
            }
        )

        centre_right = Party(
            name="Conservative Party",
            colour="#0062ff",
            poll = 0,
            tactical_vote = 10,
            base_support = 0.5,
            weights = {
                "urban": -0.5,
                "industry": -0.3,
                "wealth": 0.8,
                "education": 0.2
            }
        )

        centre_left = Party(
            name="Liberal Party",
            colour="#dc0000",
            poll = 0,
            tactical_vote = 20,
            base_support = 0.3,
            weights = {
                "urban": 0.6,
                "industry": 0.2,
                "wealth": -0.5,
                "education": 0.4
            }
        )

        far_left = Party(
            name="Green Party",
            colour="#21bc3e",
            poll = 0,
            tactical_vote = 15,
            base_support = -0.5,
            weights = {
                "urban": 0.4,
                "industry": -0.2,
                "wealth": -0.5,
                "education": 0.8
            }
        )

        return [far_right, centre_right, centre_left, far_left]

    # Public function to run next election step
    def next_election_step(self):

        # Add one to turn
        self.turn += 1

        # Check if final turn
        if self.turn > self.TURN_MAX:

            # Set final results
            self.final_results = self.current_voteshare.copy()

            # Run election
            self.run_election()

            # return True for election complete
            return True
        
        # Step voteshare
        self._step_voteshare()

        # Apply karma
        self._apply_karma()

        # Append to record
        self.voteshare_record.append(self.current_voteshare.copy())

        # return False for continue election
        return False

    # Function to run an election
    def run_election(self):

        # Empty seat totals
        self.seat_total = {
            p.name: 0 for p in self.parties
        }

        # Set poll numbers for parties
        for i in range(len(self.parties)):
            self.parties[i].poll = self.current_voteshare[i]

        # Run elections in every seat
        for seat in self.seats:
            # Predict result for seat
            results = seat.predict(self.parties)

            # Get winner
            winner = max(results, key=results.get)

            # Add to seat total
            self.seat_total[winner] += 1
        
        # Return 1 for success
        return 1

    # Method for stepping voteshare from start to end
    # Following pseudo-deterministic underlying trend
    def _step_voteshare(self):

        # Define profiles for voteshare changing
        profiles = [
            {"midpoint": 10,   "steepness": 0.7},  # Alternative
            {"midpoint": 7.5,  "steepness": 1.4},  # Conservative
            {"midpoint": 5,   "steepness": 0.3},  # Liberal
            {"midpoint": 13, "steepness": 1.3}   # Green
        ]

        # Initialise values
        values = []

        # Zip together voteshare trend and profiles
        # Then iterate
        for start, target, profile in zip(
            self.STARTING_VOTESHARE,
            self._TARGET_END_VOTESHARE,
            profiles
        ):

            progress = self._scaled_logistic(
                profile["midpoint"],
                profile["steepness"]
            )

            base = start + (target - start) * progress

            # Polling volatility
            noise_strength = max(0.3, 1.5 - self.turn / 20)
            noise = random.uniform(-noise_strength, noise_strength)

            values.append(base + noise)

        # Update current voteshare to values
        self.current_voteshare = values

        # Normalise
        self._normalise_vote()
    
    # Function to rescale raw logistics between 1 and 15
    # By turn 15 the voteshare trend is mostly complete
    # This means 15 onwards is mostly volatile to player decisions
    def _scaled_logistic(
        self,
        midpoint,
        steepness
    ):

        # Define logistic progression
        logistic = lambda x : 1 / (1 + math.exp(-steepness * (x - midpoint)))

        # Find start, end, and current
        start = logistic(1)
        end = logistic(15)
        current = logistic(self.turn)

        # 
        return (current - start) / (end - start)

    # Method to normalise voteshare to sum of 100
    # Takes in list of four numbers -> converts to sum of 100
    # E.g. [5, 10, 15, 20] --> [10, 20, 30, 40]
    def _normalise_vote(self):

        # Shift voteshare if there are negatives so the minimum becomes 0
        min_val = min(self.current_voteshare)
        if min_val < 0:
            self.current_voteshare = [v - min_val for v in self.current_voteshare]

        # Compute total sum of votes
        total = sum(self.current_voteshare)

        # If everything is zero, set voteshare to equal split
        if total == 0:
            self.current_voteshare = [25.0, 25.0, 25.0, 25.0]

        # Scale votes to percentages (sum to 100)
        scaled = [v * 1000 / total for v in self.current_voteshare]  # working in tenths of a percent

        # Take integer part (floor) in tenths
        base = [int(x) for x in scaled]

        # Compute how many tenths are left to distribute to reach exactly 100.0
        remainder = int(round(1000 - sum(base)))

        # Compute fractional parts for prioritising largest remainders
        fractions = [x - b for x, b in zip(scaled, base)]

        # Distribute remaining tenths based on highest fractional parts
        for i in sorted(
            range(
                len(
                    self.current_voteshare
                )
            ),
            key=lambda i: fractions[i],
            reverse=True
        )[:remainder]:
            base[i] += 1

        # Set updated voteshare
        self.current_voteshare = [
            b / 10
            for b in base
        ]

    # Method to apply karma to political parties
    def _apply_karma(
        self,
        flat=0.8,
        exp=0.6,
        steep=1.6
    ):

        # Iterate over voteshare (indices)
        for i in range(len(self.current_voteshare)):

            # Get karma
            k = self._karma[i]

            # Apply linear effect
            linear = flat * k

            # Apply exponential effect
            exp_effect = exp * math.copysign(
                abs(k) ** steep,
                k
            )

            # Adjust voteshare
            self.current_voteshare[i] += linear + exp_effect

        # Normalise voteshare once complete
        self._normalise_vote()

    # Function to resolve ties when finding winning candidatees
    # More often picking candidate with higher voteshare
    def _resolve_party_tie(
        self,
        candidates
    ):

        if len(candidates) == 1:
            return candidates[0]

        party_order = [
            "Alternative Party",
            "Conservative Party",
            "Liberal Party",
            "Green Party"
        ]

        best_vote = max(
            self.final_results[party_order.index(p)]
            for p in candidates
        )

        vote_candidates = [
            p for p in candidates
            if self.final_results[party_order.index(p)] == best_vote
        ]

        if len(vote_candidates) == 1:
            return vote_candidates[0]

        return random.choice(vote_candidates)
    
    # Function to get the outcome text
    def get_outcome_text(self):

        majority_party = "None"

        # If majority is announced, set majority party and largest party
        if self.majority_announced:

            majority_party = max(self.seat_total, key=self.seat_total.get)
            largest_party = majority_party

        # Else, just pick largest party
        else:

            # Find largest seat count
            largest_seats = max(self.seat_total.values())

            # Get candidates for largest seats
            largest_candidates = [
                p
                for p, seats in self.seat_total.items()
                if seats == largest_seats
            ]

            # Resolve tie
            largest_party = self._resolve_party_tie(
                largest_candidates
            )

        # Find opposition
        opposition_pool = {
            p: seats
            for p, seats in self.seat_total.items()
            if p != largest_party
        }

        # Get opposition seats
        opposition_seats = max(opposition_pool.values())

        # Get opposition candidates
        opposition_candidates = [
            p
            for p, seats in opposition_pool.items()
            if seats == opposition_seats
        ]

        # Resolve tie
        opposition_party = self._resolve_party_tie(
            opposition_candidates
        )

        # Get outcome text
        outcome_text = (
            self._POSSIBLE_OUTCOMES
                .get(majority_party, {})
                .get(largest_party, {})
                .get(opposition_party)
        )

        # If no text, use rare case text
        if outcome_text is None:

            outcome_text = [
                "What did you do. Well. I'm completely stumped. Somehow you ended up with an outcome I absolutely did not intend. Did you hack the game? Or was this a legitimate result? Either way, I'm genuinely impressed. Let me know how you got this outcome! In the meanwhile, I'll just pretend parliament caught on fire and everyone died. That'll be a clean outcome."
            ]

        # Divide between title and text
        parts = outcome_text[0].split(".", 1) # Divide after first sentence

        title = parts[0].strip()
        text = parts[1].strip()

        return title, text

    # Function to get the current turn's map figure
    def get_turn_map_figure(self):
        # If first turn
        if self.turn == 1:
            # Set starting seats
            self.starting_seats = self.seat_total.copy()
            return self.renderer.plot_seats_results(map_title="")
        
        # Otherwise return projection
        return self.renderer.plot_seat_projection(map_title="")

    # Function to handle player choices, adding karma to parties
    def handle_choice(self, choice_index):
        # Get current turn data
        turn_data = self.get_turn_data()

        # Identify choice
        choice = turn_data["choices"][choice_index]

        # Get result
        result = choice["result"]

        # Update karma
        for i in range(len(result)):
            self._karma[i] += result[i]

            # Clamp to bounds
            self._karma[i] = max(
                -self._KARMA_CAP,
                min(
                    self._KARMA_CAP,
                    self._karma[i]
                )
            )

        # Get advisor feedback
        feedback = choice["response"]

        # Return
        return feedback

    # Function for counting the next step in an election
    def count_next_votes(self):

        # Add one step
        self.election_count_step = min(
            self.election_count_step + 1,
            len(self._COUNTING_MARGINS) - 1
        )

        # Current margin
        current_margin = self._COUNTING_MARGINS[self.election_count_step]

        # Get figure, chart, voteshare
        fig = self.renderer.plot_final_seats(
            map_title="",
            margin_tolerance=current_margin
        )

        chart, running_total, majority = self.renderer.results_parliament_graph(
            margin_tolerance=current_margin
        )

        voteshare = self.renderer.live_voteshare_graph(running_total)

        # Majority event handling
        # Return none unless first time a majority is announced
        majority_event = None

        # Handle if majority is first announced
        if majority and not self.majority_announced:
            self.majority_announced = True
            majority_event = majority
        
        # Boolean for finished
        finished = (
            self.election_count_step ==
            len(self._COUNTING_MARGINS) - 1
        )

    
        # If counting complete, set count percentage 100
        if finished:
            count_percentage = 100
        else:
            # If not finished, set count_percentage

            # Ease-out curve for voting progress
            t = self.election_count_step / (len(self._COUNTING_MARGINS) - 1)

            eased = 1 - math.pow(1 - t, 3)
            raw = 100 * eased
            count_percentage = round(100 * eased)

            # Switch formatting mode near end
            if raw >= 99.9:
                count_percentage = round(raw, 2)
                count_percentage = min(count_percentage, 99.99)
            elif raw >= 99:
                count_percentage = round(raw, 1)
                count_percentage = min(count_percentage, 99.9)
            else:
                count_percentage = round(raw)
                # Will always round up to 99% due to previous checks
        
        # Return dictionary of all results
        return {
            "finished": finished,
            "margin": current_margin,
            "count_percentage": count_percentage,
            "figure": fig.to_dict(),
            "parliament": chart.to_dict(),
            "voteshare": voteshare.to_dict(),
            "majority_event": majority_event
        }