import random
import re

import plotly.graph_objects as go

# Graph renderer
class GraphRenderer:

    # Various labels when describing demographics

    _URBAN_LABELS = {
        "high": "Urban",
        "middle": "Suburban",
        "low": "Rural"
    }

    _INDUSTRY_LABELS = {
        "high": "Industrial",
        "middle": "Average Industry",
        "low": "Non-Industrial"
    }

    _WEALTH_LABELS = {
        "high": "Wealthy",
        "middle": "Average Wealth",
        "low": "Poor"
    }

    _EDUCATION_LABELS = {
        "high": "Educated",
        "middle": "Average Education",
        "low": "Uneducated"
    }

    # Colours for the different archetypes
    _ARCHETYPE_COLOURS = {
        "Urban Industrial": "#981009",
        "Urban Educated": "#ff9900",
        "University Town": "#ffe600",
        "Post-Industrial Decline": "#ff6b6b",

        "Sub-Urban Affluent": "#08803c",
        "Sub-Urban Mixed": "#6cbd2e",
        "Sub-Urban Poor": "#aad578",

        "Rural Agricultural": "#8bfafe",
        "Rural Industrial": "#23a2c9",
        "Rural Deprived": "#0049d0"
    }

    # Initialise
    def __init__(
        self,
        game
    ):

        # Includes all game data for drawing graphs
        self.game = game

        # Define point size
        self._point_size = self._compute_point_size()

        # Define dictionary of parties and colours
        self._CORE_PARTY_COLOURS = {
            p.name: p.colour for p in self.game.parties
        }

        # List of party names
        self._PARTY_NAMES = [
            p.name for p in self.game.parties
        ]

    # Function to calculates how big the point size should be based on number of seats
    def _compute_point_size(self):

        # Use this basic size as a reference
        base_T = 120
        base_size = 30

        # Controls how fast points grow/shrink
        exponent = 0.6

        # Calculate new size by multiplying by T scale and then exponent
        size = base_size * (base_T / self.game.total_seats) ** exponent

        # Safety clamps: Can't be smaller than 4 or greater than 60
        return max(4, min(60, size))

    # Function to describe demographic labels
    def _describe_demographic(
        self, 
        value, 
        labels
    ):

        if value >= 0.8:
            return f"Very {labels['high']}"

        elif value >= 0.4:
            return labels["high"]

        elif value <= -0.8:
            return f"Very {labels['low']}"

        elif value <= -0.4:
            return labels["low"]

        else:
            return labels["middle"]

    # Function to create a graph showing election results
    def plot_seats_results(
        self,
        map_title="Election Results Map"
    ):
        
        # Data storage
        x_vals = []
        y_vals = []

        election_colours = []
        archetype_colours = []

        election_hover_texts = []
        archetype_hover_texts = []
        margin_hover_texts = []

        margin_colours = []

        # Margin colour scale (dark blue to light blue)

        def _margin_colour(margin):

            # closer races = darker (more intense)
            # map 0–50% into light->dark red/blue scale

            if margin < 1:
                return "#00042b"   # extremely tight (darkest)

            elif margin < 5:
                return "#0013b9"

            elif margin < 10:
                return "#4b5dff"

            else:
                return "#95a0ff"   # safe seat (light)

        # Build the data seat by seat
        for seat in self.game.seats:

            x_vals.append(seat.x)
            y_vals.append(seat.y)

            # Sort the results and extract winner, runner-up, and margin

            sorted_results = sorted(
                seat.election_results.items(),
                key=lambda item: item[1],
                reverse=True
            )

            winner_party, winner_vote = sorted_results[0]
            second_party, second_vote = sorted_results[1]

            margin = winner_vote - second_vote

            # Store margin colour
            margin_colours.append(_margin_colour(margin))

            # Election colour (winner)
            election_colours.append(seat.winner_colour)

            # Hover text for the election results

            results_str = "<br>".join(
                f"{party}: {vote:.2f}%"
                for party, vote in sorted_results
            )

            election_hover_text = (
                f"<b>{seat.name}</b><br>"
                f"Winner: {winner_party} ({winner_vote:.2f}%)<br>"
                f"{results_str}"
            )

            election_hover_texts.append(election_hover_text)

            # Hover text for archetypes/demographic data

            archetype = re.sub(r"\s+\d+$", "", seat.name)

            urban_desc = self._describe_demographic(seat.urban, self._URBAN_LABELS)
            industry_desc = self._describe_demographic(seat.industry, self._INDUSTRY_LABELS)
            wealth_desc = self._describe_demographic(seat.wealth, self._WEALTH_LABELS)
            education_desc = self._describe_demographic(seat.education, self._EDUCATION_LABELS)

            archetype_colours.append(
                self._ARCHETYPE_COLOURS.get(archetype, "#cccccc")
            )

            archetype_hover_text = (
                f"<b>{seat.name}</b><br>"
                f"Winner: {seat.winner}<br><br>"
                f"<b>Demographics</b><br>"
                f"Urbanisation: {urban_desc}<br>"
                f"Industry: {industry_desc}<br>"
                f"Wealth: {wealth_desc}<br>"
                f"Education: {education_desc}"
            )

            archetype_hover_texts.append(archetype_hover_text)

            # Hover text for margin of victory visualisation

            margin_hover_text = (
                f"<b>{seat.name}</b><br>"
                f"Winner: {seat.winner}, {winner_vote:.2f}%<br>"
                f"Runner-Up: {second_party}, {second_vote:.2f}%<br>"
                f"Margin: {margin:.2f}%"
            )

            margin_hover_texts.append(margin_hover_text)

        # Create figure

        fig = go.Figure()

        # Add election results trace

        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_vals,
                mode="markers",
                visible=True,

                marker=dict(
                    size=self._point_size,
                    color=election_colours,
                    line=dict(width=0)
                ),

                hoverinfo="text",
                hovertext=election_hover_texts,

                name="Election Results"
            )
        )

        # Add demographics trace

        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_vals,
                mode="markers",
                visible=False,

                marker=dict(
                    size=self._point_size,
                    color=archetype_colours,

                    line=dict(
                        color=election_colours,
                        width=0
                    )
                ),

                hoverinfo="text",
                hovertext=archetype_hover_texts,

                name="Demographics"
            )
        )

        # Add margin of victory trace

        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_vals,
                mode="markers",
                visible=False,

                marker=dict(
                    size=self._point_size,
                    color=margin_colours,
                    line=dict(width=0)
                ),

                hoverinfo="text",
                hovertext=margin_hover_texts,

                name="Margins"
            )
        )

        # Layout and toggles

        fig.update_layout(

            title=map_title,

            xaxis=dict(visible=False),
            yaxis=dict(visible=False),

            autosize=True,
            height=600,
            margin=dict(
                l=0,
                r=0,
                t=50,
                b=0
            ),

            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",

            dragmode=False,
            uirevision=True,

            updatemenus=[
                dict(
                    type="buttons",
                    direction="right",

                    buttons=[

                        dict(
                            label="Election Results",
                            method="update",
                            args=[{"visible": [True, False, False]}]
                        ),

                        dict(
                            label="Demographics",
                            method="update",
                            args=[{"visible": [False, True, False]}]
                        ),

                        dict(
                            label="Margins",
                            method="update",
                            args=[{"visible": [False, False, True]}]
                        ),
                    ],

                    x=0.5,
                    y=1.2,
                    xanchor="center"
                ),

                dict(
                    type="buttons",
                    direction="right",
                    showactive=False,

                    buttons=[
                        dict(
                            label="Outline: Off",
                            method="restyle",
                            args=[{"marker.line.width": 2}, [1]]
                        )
                    ],

                    x=0.5,
                    y=1.05,
                    xanchor="center",
                    visible=False
                )
            ]
        )

        fig.update_xaxes(
            visible=False,
            fixedrange=True,
            constrain="domain"
        )

        fig.update_yaxes(
            visible=False,
            fixedrange=True,
            scaleanchor="x",
            scaleratio=1
        )

        return fig

    # Function to create a graph showing projection of victory, not actual victory
    def plot_seat_projection(
        self,
        map_title="Projected Election Results"
    ):
        # Helper function to create a fade effect for the colours
        def fade(hex_colour, strength):
            """
            strength: 1.0 = full colour
                    0.5 = faded
            """
            hex_colour = hex_colour.lstrip("#")
            r = int(hex_colour[0:2], 16)
            g = int(hex_colour[2:4], 16)
            b = int(hex_colour[4:6], 16)

            r = int(255 - (255 - r) * strength)
            g = int(255 - (255 - g) * strength)
            b = int(255 - (255 - b) * strength)

            return f"#{r:02x}{g:02x}{b:02x}"

        # Helper function to classify projection based on margin of victory
        def classify_projection(margin):
            if margin > 15:
                return "Safe"
            elif margin > 10:
                return "Likely"
            elif margin > 5:
                return "Leaning"
            else:
                return "Tossup"

        # Storage

        x_vals = []
        y_vals = []

        proj_colours = []
        archetype_colours = []

        proj_hover = []
        archetype_hover = []

        # Build data

        for seat in self.game.seats:

            x_vals.append(seat.x)
            y_vals.append(seat.y)

            sorted_results = sorted(
                seat.election_results.items(),
                key=lambda x: x[1],
                reverse=True
            )

            top1_party, top1 = sorted_results[0]
            top2_party, top2 = sorted_results[1]

            margin = top1 - top2
            category = classify_projection(margin)

            base_colour = seat.winner_colour

            # Projection colour logic

            if category == "Safe":
                colour = base_colour

            elif category == "Likely":
                colour = fade(base_colour, 0.7)

            elif category == "Leaning":
                colour = fade(base_colour, 0.4)

            else:
                # Tossup = neutral yellow
                colour = "#ffcc00"

            proj_colours.append(colour)

            # Projection Hover Text

            if category == "Tossup":
                hover = (
                    f"<b>{seat.name}</b><br>"
                    f"<b>Tossup</b><br>"
                    f"Top contenders:<br>"
                    f"1. {top1_party}<br>"
                    f"2. {top2_party}"
                )
            else:
                hover = (
                    f"<b>{seat.name}</b><br>"
                    f"{category} {top1_party}"
                )

            proj_hover.append(hover)

            # Demographics hover text

            archetype = re.sub(r"\s+\d+$", "", seat.name)

            archetype_colours.append(
                self._ARCHETYPE_COLOURS.get(archetype, "#cccccc")
            )

            # Demographic labels
            urban_desc = self._describe_demographic(seat.urban, self._URBAN_LABELS)
            industry_desc = self._describe_demographic(seat.industry, self._INDUSTRY_LABELS)
            wealth_desc = self._describe_demographic(seat.wealth, self._WEALTH_LABELS)
            education_desc = self._describe_demographic(seat.education, self._EDUCATION_LABELS)

            # Projection classification

            if category == "Tossup":
                projection_text = (
                    f"<b>Tossup</b><br>"
                    f"Top 2: {top1_party} / {top2_party}"
                )
            else:
                projection_text = f"<b>{category} {top1_party}</b>"

            archetype_hover.append(
                f"<b>{seat.name}</b><br>"
                f"Archetype: {archetype}<br><br>"

                f"<b>Demographics</b><br>"
                f"Urbanisation: {urban_desc}<br>"
                f"Industry: {industry_desc}<br>"
                f"Wealth: {wealth_desc}<br>"
                f"Education: {education_desc}<br><br>"

                f"<b>Projection</b><br>"
                f"{projection_text}"
            )

        # Figure

        fig = go.Figure()

        # Add projection

        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_vals,
                mode="markers",
                visible=True,

                marker=dict(
                    size=self._point_size,
                    color=proj_colours,
                    line=dict(width=0)
                ),

                hoverinfo="text",
                hovertext=proj_hover,

                name="Projection"
            )
        )

        # Add demographics

        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_vals,
                mode="markers",
                visible=False,

                marker=dict(
                    size=self._point_size,
                    color=archetype_colours,

                    line=dict(
                        color=proj_colours,
                        width=2
                    )
                ),

                hoverinfo="text",
                hovertext=archetype_hover,

                name="Demographics"
            )
        )

        # Update layout

        fig.update_layout(

            title=map_title,

            xaxis=dict(visible=False),
            yaxis=dict(visible=False),

            autosize=True,
            height=600,
            margin=dict(
                l=0,
                r=0,
                t=50,
                b=0
            ),

            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",

            legend=dict(
                x=0,
                y=0,
                xanchor="right",
                yanchor="top"
            ),

            dragmode=False,
            uirevision=True,

            updatemenus=[

                dict(
                    type="buttons",
                    direction="right",

                    buttons=[

                        dict(
                            label="Projection",
                            method="update",
                            args=[{
                                "visible": [True, False]
                            }]
                        ),

                        dict(
                            label="Demographics",
                            method="update",
                            args=[{
                                "visible": [False, True]
                            }]
                        )
                    ],

                    x=0.5,
                    y=1.2,
                    xanchor="center"
                )
            ]
        )

        fig.update_xaxes(
            visible=False,
            fixedrange=True,
            constrain="domain"
        )

        fig.update_yaxes(
            visible=False,
            fixedrange=True,
            scaleanchor="x",
            scaleratio=1
        )

        return fig

    # Function to create a graph of final seats, but doesn't show results in seats with result less than margin tolerance
    def plot_final_seats(
        self, 
        map_title="Final Election Results", 
        margin_tolerance=0
    ):

        # Data storage
        x_vals = []
        y_vals = []

        election_colours = []

        election_hover_texts = []

        # Build the data seat by seat

        for seat in self.game.seats:

            x_vals.append(seat.x)
            y_vals.append(seat.y)

            # Sort the results and extract winner, runner-up, and margin

            sorted_results = sorted(
                seat.election_results.items(),
                key=lambda item: item[1],
                reverse=True
            )

            winner_party, winner_vote = sorted_results[0]
            second_vote = sorted_results[1][1]

            margin = winner_vote - second_vote

            # Check if margin is greater or lower than tolerance

            if margin > margin_tolerance:
                # Append winner colour
                election_colours.append(seat.winner_colour)

                # Hover text for the election results

                results_str = "<br>".join(
                    f"{party}: {vote:.2f}%"
                    for party, vote in sorted_results
                )

                election_hover_text = (
                    f"<b>{seat.name}</b><br>"
                    f"Winner: {winner_party} | Margin of Victory: ({margin:.2f}%)<br>"
                    f"{results_str}"
                )

            else:
                # If below tolerance, append grey

                election_colours.append("#989898")

                election_hover_text = (
                    f"<b>{seat.name}</b><br>"
                    "Election underway<br>"
                )

            election_hover_texts.append(election_hover_text)

        # Create figure

        fig = go.Figure()

        # Add election results trace

        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_vals,
                mode="markers",
                visible=True,

                marker=dict(
                    size=self._point_size,
                    color=election_colours,
                    line=dict(width=0)
                ),

                hoverinfo="text",
                hovertext=election_hover_texts,

                name="Election Results"
            )
        )

        # Layout and toggles

        fig.update_layout(

            title=map_title,

            xaxis=dict(visible=False),
            yaxis=dict(visible=False),

            autosize=True,
            height=500,

            margin=dict(
                l=0,
                r=0,
                t=0,
                b=0
            ),

            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",

            dragmode=False,
            uirevision=True,

        )

        fig.update_xaxes(
            visible=False,
            fixedrange=True,
            constrain="domain"
        )

        fig.update_yaxes(
            visible=False,
            fixedrange=True,
            scaleanchor="x",
            scaleratio=1
        )

        return fig

    # Function to create the voteshare trend graph for the HTML page
    def create_voteshare_trend_graph(self):

        # Get array of turns for displaying voteshare record
        turns = list(range(1, len(self.game.voteshare_record) + 1))

        fig = go.Figure()

        # Iterate through id and parties
        for idx, (party, colour) in enumerate(self._CORE_PARTY_COLOURS.items()):

            # Gather record
            y = [record[idx] for record in self.game.voteshare_record]

            # Add trace
            fig.add_trace(
                go.Scatter(
                    x=turns,
                    y=y,
                    mode="lines+markers",
                    name=party,
                    line=dict(
                        color=colour,
                        width=3
                    ),
                    marker=dict(
                        color=colour,
                        size=6
                    ),
                    hovertemplate="%{fullData.name}: %{y:.2f}%<extra></extra>"
                )
            )

        fig.update_layout(
            height=250,
            margin=dict(
                l=5,
                r=5,
                t=5,
                b=5
            ),

            showlegend=False,

            xaxis=dict(
                range=[1, 20],
                dtick=5,
                title=None
            ),

            yaxis=dict(
                range=[0,50],
                showticklabels=False,
                title=None
            )
        )

        return fig

    # Function to create parliament graph and hide seats with a margin less than tolerance as 'tossup'
    def create_parliament_graph(
        self,
        margin_tolerance=5
    ):

        # Copy party colours into local variable, and add tossup colour
        party_colours = self._CORE_PARTY_COLOURS.copy()
        party_colours["Tossup"] = "#ffd24d"

        # Copy counts data
        seat_counts = self.game.seat_total.copy()
        # Add tossups
        seat_counts["Tossup"] = 0

        # Add to tossups if there is a margin tolerance
        if margin_tolerance:
            # Iterate seats
            for seat in self.game.seats:
                # Get results
                results = seat.election_results

                # Sort results from highest to lowest
                sorted_results = sorted(
                    results.items(),
                    key=lambda x: x[1],
                    reverse=True
                )

                # Get top party and top two results
                top_party, top_val = sorted_results[0]
                second_val = sorted_results[1][1]

                # Get margin
                margin = top_val - second_val

                # If margin is less than tolerance, subtract from party and add to tossup
                if margin < margin_tolerance:
                    seat_counts[top_party] -= 1
                    seat_counts["Tossup"] += 1


        # Specify order of parties
        ordered_parties = [
            "Alternative Party",
            "Conservative Party",
            "Tossup",
            "Liberal Party",
            "Green Party"
        ]

        # Get values and colours
        values = [seat_counts[p] for p in ordered_parties]
        colors = [party_colours[p] for p in ordered_parties]

        # Create figure
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=ordered_parties,
                    values=values,

                    hole=0.55,

                    textinfo="none",
                    hoverinfo="label+value",
                    hovertemplate="<b>%{label}</b><br>Seats: %{value}<extra></extra>",

                    marker=dict(colors=colors),

                    sort=False,
                    direction="clockwise",
                    rotation=180
                )
            ]
        )

        fig.update_layout(
            showlegend=False,
            autosize=True,
            height=250,
            margin=dict(
                l=5,
                r=5,
                t=5,
                b=5
            )
        )

        return fig

    # Function to create parliament graph for results and hide seats below a certain tolerance
    def results_parliament_graph(
        self,
        margin_tolerance=0
    ):

        # Copy party colours and add 'Not Called'
        party_colours = self._CORE_PARTY_COLOURS.copy()
        party_colours["Not Called"] = "#989898"

        # Copy seat counts and add 'Not Called'
        running_total = self.game.seat_total.copy()
        running_total["Not Called"] = 0

        # If margin tolerance > 0
        if margin_tolerance:
            for seat in self.game.seats:

                results = seat.election_results

                sorted_results = sorted(
                    results.items(),
                    key=lambda x: x[1],
                    reverse=True
                )

                top_party, top_val = sorted_results[0]
                second_val = sorted_results[1][1]

                margin = top_val - second_val

                if margin <= margin_tolerance:
                    running_total[top_party] -= 1
                    running_total["Not Called"] += 1

        # Check for any majority party
        majority_party = next(
            (
                party
                for party, seats in running_total.items()
                if party != "Not Called"
                and seats >= self.game.majority_threshold
            ),
            None
        )

        ordered_parties = [
            "Alternative Party",
            "Conservative Party",
            "Not Called",
            "Liberal Party",
            "Green Party"
        ]

        values = [running_total[p] for p in ordered_parties]
        colors = [party_colours[p] for p in ordered_parties]

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=ordered_parties,
                    values=values,

                    hole=0.55,

                    textinfo="none",
                    hoverinfo="label+value",
                    hovertemplate="<b>%{label}</b><br>Seats: %{value}<extra></extra>",

                    marker=dict(colors=colors),

                    sort=False,
                    direction="clockwise",
                    rotation=180
                )
            ]
        )

        fig.update_layout(
            showlegend=False,

            autosize=True,
            height=275,

            margin=dict(
                l=10,
                r=10,
                t=5,
                b=5
            ),

            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        return fig, running_total, majority_party

    # Function to simulate a 'live voteshare' graph
    def live_voteshare_graph(
        self,
        running_total
    ):

        # Calculate how many seats are actually counted
        total_called = sum(
            v for k, v in running_total.items()
            if k != "Not Called"
        )

        called_ratio = total_called / self.game.total_seats

        # If no seats declared, set to 0
        
        if called_ratio == 0:
            apparent = [0, 0, 0, 0]
        
        else:
            # Get true seat share
            true_seat_share = [
                self.game.seat_total[p] / self.game.total_seats
                for p in self._PARTY_NAMES
            ]

            # Observed seat share so far
            observed_seat_share = [
                running_total[p] / total_called
                for p in self._PARTY_NAMES
            ]

            # Get bias of observed seats compared to actual outcome
            bias = [
                observed_seat_share[i] - true_seat_share[i]
                for i in range(len(self._PARTY_NAMES))
            ]

            # Construct apparent voteshare
            apparent = [
                self.game.final_results[i] * (1 + bias[i])
                for i in range(len(self._PARTY_NAMES))
            ]

            # Add noise if not all seats called
            if called_ratio < 1:
                uncertainty = 1 - called_ratio
                noise_strength = uncertainty ** 2

                for i in range(len(apparent)):
                    noise = random.gauss(0, 1)
                    base = apparent[i]
                    apparent[i] = base + (
                        noise * noise_strength
                    )

                # Quick normalisation to guarantee 100
                total = sum(apparent)
                apparent = [round(v * 100 / total, 1) for v in apparent]
                # Adjust final number so we guarantee 100
                apparent[-1] = round(100 - sum(apparent[:-1]), 1)

        # Build graph
        fig = go.Figure()

        for i, party in enumerate(self._PARTY_NAMES):

            fig.add_trace(
                go.Bar(
                    x=[party],
                    y=[apparent[i]],
                    width=1,
                    marker=dict(color=self._CORE_PARTY_COLOURS[party]),
                    hovertemplate=(
                        f"<b>{party}</b><br>"
                        "Apparent vote share: %{y:.1f}%<extra></extra>"
                    ),
                    showlegend=False
                )
            )
        
        fig.update_layout(
            autosize=True,
            height=250,

            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20
            ),

            xaxis=dict(
                visible=False
            ),

            dragmode=False,
            uirevision=True,

            yaxis=dict(
                visible=True,
                showticklabels=True,
                title=None,
                range=[0, 50]
            ),

            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",

            bargap = 0,

        )

        return fig

    # Function to return the HTML for the archetype key for demographic data
    def render_archetype_key(self):
        # Start html div
        html = '<div class="archetype-key">'

        # Add archetype colours
        for archetype, colour in self._ARCHETYPE_COLOURS.items():

            html += f"""
            <div class="archetype-item">
                <span class="archetype-swatch" style="background:{colour};"></span>
                <span class="archetype-label">{archetype}</span>
            </div>
            """

        # Close div
        html += "</div>"

        return html

    # Function to return HTML for voteshare
    def render_voteshare_html(self):

        # Pair parties and votes and sort by voteshare descending
        paired = list(zip(self._PARTY_NAMES.copy(), self.game.current_voteshare))
        paired.sort(key=lambda x: x[1], reverse=True)

        html = '<div class="voteshare-panel">'

        html += '<h3>Projected Voteshare</h3>'

        for party, value in paired:
            html += f"""
            <div class="vote-row">
                <div class="party-name">{party}</div>
                <div class="vote-value">{value:.1f}%</div>
            </div>
            """

        html += '</div>'

        return html

    # Function to render final results table in html
    def render_results_table_html(self):

        rows = []

        for i, party in enumerate(self._PARTY_NAMES):

            final_vote = self.game.final_results[i]
            start_vote = self.game.STARTING_VOTESHARE[i]
            vote_delta = final_vote - start_vote

            final_seats = self.game.seat_total.get(party, 0)
            start_seats = self.game.starting_seats.get(party, 0)
            seat_delta = final_seats - start_seats

            rows.append((
                party,
                final_vote,
                vote_delta,
                final_seats,
                seat_delta
            ))

        # sort by final seats (most meaningful "winner-first" ordering)
        rows.sort(key=lambda x: x[3], reverse=True)

        html = """
        <div class="results-table-container">
            <h3 style="text-align:center">Election Breakdown</h3>

            <table class="results-table">

                <thead>
                    <tr>
                        <th>Party</th>
                        <th>Vote Share</th>
                        <th>Change (Vote)</th>
                        <th>Seats</th>
                        <th>Change (Seats)</th>
                    </tr>
                </thead>

                <tbody>
        """

        for party, vote, vdelta, seats, sdelta in rows:

            # vote delta formatting
            if vdelta > 0:
                vdelta_str = f"+{vdelta:.1f}%"
                vclass = "delta-positive"
            elif vdelta < 0:
                vdelta_str = f"{vdelta:.1f}%"
                vclass = "delta-negative"
            else:
                vdelta_str = "0.0%"
                vclass = "delta-neutral"

            # seat delta formatting
            if sdelta > 0:
                sdelta_str = f"+{sdelta}"
                sclass = "delta-positive"
            elif sdelta < 0:
                sdelta_str = f"{sdelta}"
                sclass = "delta-negative"
            else:
                sdelta_str = "0"
                sclass = "delta-neutral"

            html += f"""
                <tr>
                    <td class="party-name">{party}</td>

                    <td>{vote:.1f}%</td>

                    <td class="{vclass}">{vdelta_str}</td>

                    <td>{seats}</td>

                    <td class="{sclass}">{sdelta_str}</td>
                </tr>
            """

        html += """
                </tbody>
            </table>
        </div>
        """

        return html