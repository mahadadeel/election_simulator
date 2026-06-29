from dataclasses import dataclass, field

# Basic model for the political party
@dataclass
class Party:
    name: str # Party name
    colour: str # Party brand colour (for map)

    # Current national polling (%)
    poll: float = 0.0
    # How much of the party is willing to tactically vote (percentage)
    tactical_vote: float = 0.0
    # Inherent structural support (-1 = strongly disadvantaged, 1 = strongly advantaged)
    base_support: float = 0.0

    # Demographic preferences
    # -1 = strongly dislikes, 0 = neutral, 1 = strongly likes
    weights: dict[str, float] = field(default_factory=lambda: {
        "urban": 0.0,
        "industry": 0.0,
        "wealth": 0.0,
        "education": 0.0
    })
