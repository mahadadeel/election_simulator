from dataclasses import dataclass, field
from typing import Optional, Dict
import random

# Basic model for each Seat
@dataclass
class Seat:
    name: str # Seat name
    x: int # X-position of Seat on graph
    y: int # Y-position of Seat on graph

    # Store election results and current winner
    election_results: Dict[str, float] = field(default_factory=dict)
    winner: str | None = None

    # Colour of winner for colour-coding by party
    winner_colour: str | None = None

    # Neighbours for map layout
    neighbours: Dict[str, Optional["Seat"]] = field(default_factory=lambda: {
        "up": None,
        "up-left": None,
        "up-right": None,
        "bottom": None,
        "bottom-left": None,
        "bottom-right": None
    })

    # Demographics (valued -1 to 1)
    urban: float = 0.0 # -1 = strongly rural, 0 = suburban, 1 = strongly urban
    industry: float = 0.0 # -1 = strongly non-industrial, 0 = average industry, 1 = strongly industrial
    wealth: float = 0.0 # -1 = very poor, 0 = average wealth, 1 = very wealthy
    education: float = 0.0 # -1 = very uneducated, 0 = average education, 1 = very educated

    # Seat Bias Profile (how well each party performs inherently in the seat)
    bias: dict[str, float] = field(default_factory=dict)

    # Predict who would win the seat
    # Input is all the parties
    def predict(self, parties, gamma=1.3):
        # Dictionary to store the scores of each party
        scores = {}

        for party in parties:
            # Calculate the local effects of the local demographics + how the party performs based on them
            local_effect = (
                self.urban * party.weights["urban"] +
                self.industry * party.weights["industry"] +
                self.wealth * party.weights["wealth"] +
                self.education * party.weights["education"]
            )

            # Get seat and party structural bias
            seat_bias = self.bias.get(party.name, 0.0)
            party_base = party.base_support

            # Get raw score for how well party performs (poll + local effect + structural bias + random noise)
            raw_score = max(
                0.01,
                party.poll
                + (local_effect * 10)
                + (seat_bias * 5)
                + (party_base * 3)
                + random.gauss(0, 2)
            )

            # Add party score to dictionary of score
            # Power by gamma so parties in the lead have more of a stated lead (creates illusion of 'safe' districts)
            scores[party.name] = raw_score ** gamma

        # Next we transfer the score into a popular vote
        # Get total of scores
        total = sum(scores.values())

        # Find popular vote by dividing score by total and storing as percentages
        # Compile dictionary of party names and results
        results = {
            name: score / total * 100
            for name, score in scores.items()
        }

        # Apply tactical voting
        results = self._apply_tactical_voting(results, parties)

        # Store election results
        self.election_results = results

        # determine winner
        self.winner = max(results, key=results.get)

        # Store winner's colour
        winner_party = next(p for p in parties if p.name == self.winner)
        self.winner_colour = winner_party.colour

        # Return results
        return results

    # Private Function to calculate tactical voting
    def _apply_tactical_voting(self, results, parties, margin_threshold=10):
        # Quick dictionary to look up parties
        party_lookup = {p.name: p for p in parties}

        # Also store names of party separately for convenience
        FR = "Alternative Party"
        CR = "Conservative Party"
        CL = "Liberal Party"
        FL = "Green Party"

        # Helper function to check if margin is close
        def margin_is_close():
            # Sort values
            sorted_vals = sorted(results.values(), reverse=True)
            # Check if leading two parties are below margin threshold for tactical voting
            return (sorted_vals[0] - sorted_vals[1]) < margin_threshold

        # Check if margin is not close (i.e. <10%)
        # If not, return results
        if not margin_is_close():
            return results

        # If margin is close, get winner
        winner = max(results, key=results.get)

        # Helper function to shift votes from one party to another party
        def shift(from_party, to_party):
            # Lookup amount of votes that would transfer
            amount = results[from_party] * (party_lookup[from_party].tactical_vote / 100)
            # Subtract from donor party, add to recipient party
            results[from_party] -= amount
            results[to_party] += amount

        # Get 'blocs' of parties
        right_bloc = [FR, CR]
        left_bloc = [CL, FL]
        centre_bloc = [CR, CL]

        # Get sums for each bloc
        right_total = sum(results[p] for p in right_bloc)
        left_total = sum(results[p] for p in left_bloc)
        centre_total = sum(results[p] for p in centre_bloc)

        # Rule 1:
        # Left-leaning party winning
        # But Right vote combined is greater
        # Shift within right bloc

        if winner in left_bloc:

            if right_total > results[winner]:
                donor = FR if results[FR] < results[CR] else CR
                receiver = CR if donor == FR else FR

                shift(donor, receiver)

        # Rule 2:
        # Right-leaning party winning
        # But Left vote combined is greater
        # Shift within right bloc

        elif winner in right_bloc:

            if left_total > results[winner]:
                donor = FL if results[FL] < results[CL] else CL
                receiver = CL if donor == FL else FL

                shift(donor, receiver)

        # Rule 3:
        # Far-left or far-right party winning
        # But Centrist vote combined is greater
        # Shift within centrist bloc

        if winner == FR:

            if centre_total > results[FR]:
                donor = CL if results[CL] < results[CR] else CR
                receiver = CR if donor == CL else CL

                shift(donor, receiver)

        elif winner == FL:

            if centre_total > results[FL]:
                donor = CL if results[CL] < results[CR] else CR
                receiver = CR if donor == CL else CL

                shift(donor, receiver)

        return results
