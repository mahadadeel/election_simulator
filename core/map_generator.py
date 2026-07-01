
import random
import math

from collections import deque

from models.seat import Seat

# Electoral map generation
class MapGenerator:

    # Distribution of archetypes in map
    _ARCHETYPE_PERCENTAGES = {
        "Urban Industrial": 9,
        "Urban Educated": 8,
        "Post-Industrial Decline":10,
        "University Town": 5,
        "Sub-Urban Affluent": 9,
        "Sub-Urban Mixed": 13,
        "Sub-Urban Poor": 7,
        "Rural Agricultural": 16,
        "Rural Industrial": 13,
        "Rural Deprived": 10
    }

    # Define Hex Directions for neighbours
    _HEX_DIRECTIONS = {
        "up": math.pi / 2,
        "up-right": math.pi / 6,
        "bottom-right": -math.pi / 6,
        "bottom": -math.pi / 2,
        "bottom-left": -5 * math.pi / 6,
        "up-left": 5 * math.pi / 6
    }

    # Define opposite directions
    _OPPOSITE = {
        "up": "bottom",
        "bottom": "up",
        "up-left": "bottom-right",
        "bottom-right": "up-left",
        "up-right": "bottom-left",
        "bottom-left": "up-right"
    }

    # Define hex offsets relative to directions
    _HEX_OFFSETS = {
        "up": (0, 1),
        "up-right": (1, 0),
        "bottom-right": (1, -1),
        "bottom": (0, -1),
        "bottom-left": (-1, 0),
        "up-left": (-1, 1)
    }

    # Define hex directions
    _HEX_NEIGHBOURS = [
        (1, 0),
        (1, -1),
        (0, -1),
        (-1, 0),
        (-1, 1),
        (0, 1)
    ]

    def __init__(
            self, 
            total_seats
        ):
        
        # How many seats the map has
        self.total_seats = total_seats

    # Generation function
    def generate(self):
        # Create electoral districts
        electoral_districts = self._create_electoral_districts()
        
        # Draw maps
        electoral_map = self._build_electoral_map(electoral_districts)

        # Return map
        return electoral_map

    # Method to create electoral districts
    def _create_electoral_districts(self):
        # Calculate how many seats based on archetypes
        archetype_seats = self._allocate_seats()

        # Generate seats
        seats = []
        
        # Urban Industrial
        for i in range(archetype_seats["Urban Industrial"]):
            seats.append(
                Seat(
                    name = f"Urban Industrial {i+1}",
                    x = 0,
                    y = 0,
                    urban = random.randint(6,10) / 10,
                    industry = random.randint(5,10) / 10,
                    wealth = random.randint(-6,0) / 10,
                    education = random.randint(-4,2)/10,

                    bias = {
                        "Alternative Party": 0.3,
                        "Conservative Party": -0.5,
                        "Liberal Party": 0.2,
                        "Green Party": 0
                    }
                )
            )

        # Urban Educated
        for i in range(archetype_seats["Urban Educated"]):
            seats.append(
                Seat(
                    name = f"Urban Educated {i+1}",
                    x = 0,
                    y = 0,
                    urban = random.randint(7,10) / 10,
                    industry = random.randint(-5,2) / 10,
                    wealth = random.randint(2,10) / 10,
                    education = random.randint(6,10)/10,

                    bias = {
                        "Alternative Party": -0.3,
                        "Conservative Party": -0.5,
                        "Liberal Party": 0.3,
                        "Green Party": 0.3
                    }
                )
            )
        
        # University Town
        for i in range(archetype_seats["University Town"]):
            seats.append(
                Seat(
                    name = f"University Town {i+1}",
                    x = 0,
                    y = 0,
                    urban = random.randint(3,8) / 10,
                    industry = random.randint(-6,2) / 10,
                    wealth = random.randint(-2,6) / 10,
                    education = random.randint(8,10)/10,

                    bias = {
                        "Alternative Party": -0.5,
                        "Conservative Party": -0.2,
                        "Liberal Party": 0.3,
                        "Green Party": 0.8
                    }
                )
            )
        
        # Suburban Affluent
        for i in range(archetype_seats["Sub-Urban Affluent"]):
            seats.append(
                Seat(
                    name = f"Sub-Urban Affluent {i+1}",
                    x = 0,
                    y = 0,
                    urban = random.randint(-4,3) / 10,
                    industry = random.randint(-3,2) / 10,
                    wealth = random.randint(5,10) / 10,
                    education = random.randint(2,8)/10,

                    bias = {
                        "Alternative Party": -0.4,
                        "Conservative Party": 0.5,
                        "Liberal Party": 0,
                        "Green Party": -0.2
                    }
                )
            )
        
        # Suburban Mixed
        for i in range(archetype_seats["Sub-Urban Mixed"]):
            seats.append(
                Seat(
                    name = f"Sub-Urban Mixed {i+1}",
                    x = 0,
                    y = 0,
                    urban = random.randint(-3,4) / 10,
                    industry = random.randint(-4,4) / 10,
                    wealth = random.randint(-2,6) / 10,
                    education = random.randint(-2,6)/10,

                    bias = {
                        "Alternative Party": 0,
                        "Conservative Party": 0.2,
                        "Liberal Party": 0.1,
                        "Green Party": 0
                    }
                )
            )
        
        # Suburban Poor
        for i in range(archetype_seats["Sub-Urban Poor"]):
            seats.append(
                Seat(
                    name = f"Sub-Urban Poor {i+1}",
                    x = 0,
                    y = 0,
                    urban = random.randint(-2,4) / 10,
                    industry = random.randint(-2,4) / 10,
                    wealth = random.randint(-8,-2) / 10,
                    education = random.randint(-6,1)/10,

                    bias = {
                        "Alternative Party": 0.2,
                        "Conservative Party": 0.3,
                        "Liberal Party": -0.4,
                        "Green Party": 0.2
                    }
                )
            )
        
        # Rural Industrial
        for i in range(archetype_seats["Rural Industrial"]):
            seats.append(
                Seat(
                    name = f"Rural Industrial {i+1}",
                    x = 0,
                    y = 0,
                    urban = random.randint(-10,-4) / 10,
                    industry = random.randint(4,10) / 10,
                    wealth = random.randint(-6,-1) / 10,
                    education = random.randint(-5,2)/10,

                    bias = {
                        "Alternative Party": 0.3,
                        "Conservative Party": 0.3,
                        "Liberal Party": -0.2,
                        "Green Party": -0.4
                    }
                )
            )
        
        # Rural Agricultural
        for i in range(archetype_seats["Rural Agricultural"]):
            seats.append(
                Seat(
                    name = f"Rural Agricultural {i+1}",
                    x = 0,
                    y = 0,
                    urban = random.randint(-10,-6) / 10,
                    industry = random.randint(-8,1) / 10,
                    wealth = random.randint(-4,4) / 10,
                    education = random.randint(-7,-2)/10,

                    bias = {
                        "Alternative Party": 0,
                        "Conservative Party": 0.5,
                        "Liberal Party": -0.3,
                        "Green Party": -0.8
                    }
                )
            )

        # Rural Deprived
        for i in range(archetype_seats["Rural Deprived"]):
            seats.append(
                Seat(
                    name = f"Rural Deprived {i+1}",
                    x = 0,
                    y = 0,
                    urban = random.randint(-10,-6) / 10,
                    industry = random.randint(-3,2) / 10,
                    wealth = random.randint(-10,-5) / 10,
                    education = random.randint(-7,-2)/10,

                    bias = {
                        "Alternative Party": 0.5,
                        "Conservative Party": 0.1,
                        "Liberal Party": -0.3,
                        "Green Party": -0.2
                    }
                )
            )
        
        # Post-Industrial Decline
        for i in range(archetype_seats["Post-Industrial Decline"]):
            seats.append(
                Seat(
                    name = f"Post-Industrial Decline {i+1}",
                    x = 0,
                    y = 0,
                    urban = random.randint(4,9) / 10,
                    industry = random.randint(2,8) / 10,
                    wealth = random.randint(-10,-4) / 10,
                    education = random.randint(-6,1)/10,

                    bias = {
                        "Alternative Party": 0.3,
                        "Conservative Party": -0.5,
                        "Liberal Party": -0.2,
                        "Green Party": 0.1
                    }
                )
            )
        
        return seats

    # Method to convert archetype percentages to actual seat counts
    def _allocate_seats(self):
        # Raw float allocations
        raw = {
            k: (v / 100) * self.total_seats
            for k, v in self._ARCHETYPE_PERCENTAGES.items()
        }

        # Floored values
        allocated = {
            k: int(v)
            for k, v in raw.items()
        }

        # Calculate remaining seats
        remaining = self.total_seats - sum(allocated.values())

        # Fractional remainders
        remainders = {
            k: raw[k] - allocated[k]
            for k in self._ARCHETYPE_PERCENTAGES
        }

        # Distribute remaining seats by largest remainer
        for k, _ in sorted(remainders.items(), key=lambda x: x[1], reverse=True):
            if remaining <= 0:
                break
            allocated[k] += 1
            remaining -= 1

        # Return seats
        return allocated

    # Function that adds spatial geometry to seats
    def _build_electoral_map(
        self, 
        seats
    ):

        # Define urban centres
        urban_centres = self._generate_urban_centres()

        # Assign position for every seat
        for seat in seats:
            seat = self._assign_city(seat, urban_centres)   # Assign city to a seat
            seat = self._spread_seat_from_city(seat)        # Push seat out from centre (rural = further away)
        
        # Push away seats to prevent overlap
        seats = self._relax_seat_positions(seats)

        # Get neighbours in hex-style formation
        seats = self._assign_hex_neighbours(seats)

        # Enforce mutual neighbours
        seats = self._enforce_mutual_neighbours(seats)

        # Filter out only mutual neighbours
        seats = self._filter_mutual_neighbours(seats)

        # Rebuild into hex grid using neighbour relations
        seats = self._rebuild_hex_grid(seats)

        return seats

    def _generate_urban_centres(
        self,
        separation_strength = 1.5
    ):

        # Get cluster count
        cluster_count = self._get_cluster_count()

        # Design clusters by circular radius (pushes them outwards)
        base_radius = 40 * (self.total_seats / 120) ** separation_strength # Separation strength sets stronger separation

        centres = []

        # Plot cluster points across circle with random noise
        for i in range(cluster_count):

            # Divide circle by number of circles
            # In effect this creates uniform shapes. E.g. triangles, squares, opposing lines...
            angle = (2 * math.pi * i) / cluster_count

            # Radial irregularity (breaks symmetry)
            radius_noise = random.uniform(0.85, 1.15)

            r = base_radius * radius_noise

            x = math.cos(angle) * r
            y = math.sin(angle) * r

            # Positional jitter
            x += random.uniform(-5, 5)
            y += random.uniform(-5, 5)

            centres.append((x, y))

        return centres
    
    # Calculate how many clusters there should be in map
    def _get_cluster_count(self):

        # Safety
        if self.total_seats <= 0:
            return 1

        # log2 growth: 30 → 1, 60 → 2, 120 → 3, etc.
        clusters = math.floor(math.log2(self.total_seats / 30)) + 1

        # Maximum of 5 clusters
        return max(1, min(5, clusters))
    
    # Function to assign a seat to a specific urban centre
    # No spatial generation yet but creates an anchor
    def _assign_city(
        self,
        seat, 
        urban_centres
    ):
        # Pick a random city's coordinates
        city_x, city_y = random.choice(urban_centres)
        # Set the seat's coordinates to the city's coordinates
        seat.x, seat.y = city_x, city_y

        return seat

    # Spreads a seat away from an urban centre
    # Urban = closer, rural = further
    def _spread_seat_from_city(
        self,
        seat
    ):
        
        # Helper function to classify archetype
        # Identifies if urban, suburban, or rural
        def classify_archetype(seat):
            if seat.name.startswith(
                (
                    "Urban Industrial",
                    "Urban Educated",
                    "University Town"
                )
            ):
                return "urban"

            elif seat.name.startswith(
                (
                    "Sub-Urban Affluent",
                    "Sub-Urban Mixed",
                    "Sub-Urban Poor"
                )
            ):
                return "suburban"

            else:
                return "rural"
    
        # Get seat archetype
        archetype = classify_archetype(seat)

        # Base distances per archetype
        if archetype == "urban":
            min_r, max_r = 0, 5 * (self.total_seats/30)
        elif archetype == "suburban":
            min_r, max_r = 5 * (self.total_seats/30), 15 * (self.total_seats/30)
        else:  # rural
            min_r, max_r = 15 * (self.total_seats/30), 35 * (self.total_seats/30)

        # Random angle within circle
        angle = random.uniform(0, 2 * math.pi)

        # Random radius within band
        radius = random.uniform(min_r, max_r)

        # Convert polar to cartesian offset
        dx = math.cos(angle) * radius
        dy = math.sin(angle) * radius

        # Apply offset to current city position
        seat.x += dx
        seat.y += dy

        return seat

    # Function that pushes seats apart to prevent overlap
    # Uses a simple repulsion-pass algorithm to spread seats apart
    def _relax_seat_positions(
        self,
        seats,
        iterations=3,
        min_distance=5,
        strength=0.1
    ):

        # Loop in iterations
        for _ in range(iterations):

            # Loop through seats, indexed
            for i in range(len(seats)):
                si = seats[i]

                dx_total = 0
                dy_total = 0

                for j in range(len(seats)):
                    if i == j:
                        continue

                    sj = seats[j]

                    dx = si.x - sj.x
                    dy = si.y - sj.y

                    dist_sq = dx * dx + dy * dy

                    # Avoid divide-by-zero
                    if dist_sq == 0:
                        dx_total += random.uniform(-1, 1)
                        dy_total += random.uniform(-1, 1)
                        continue

                    dist = math.sqrt(dist_sq)

                    # Only apply force if too close
                    if dist < min_distance:
                        force = strength * (min_distance - dist)

                        dx_total += (dx / dist) * force
                        dy_total += (dy / dist) * force

                si.x += dx_total
                si.y += dy_total

        return seats

    # Identifies neighbours in hex directions and assigns them to seat
    def _assign_hex_neighbours(
        self,
        seats
    ):
        
        # Lambda for angle between two points
        angle_between = lambda dx, dy : math.atan2(dy, dx)

        # Helper function for checking if angle is within a sector
        def in_sector(
            angle, 
            target_angle, 
            tolerance=math.pi / 6
        ):
            diff = abs(
                (
                    angle - target_angle + math.pi
                ) % (
                    2 * math.pi
                ) - math.pi
            )

            return diff < tolerance
        
        # Clear all neighbours first
        for seat in seats:
            for k in seat.neighbours:
                seat.neighbours[k] = None

        # Iterate by seat
        for seat in seats:

            # Identify candidates by direction
            candidates = {direction: None for direction in self._HEX_DIRECTIONS.keys()}
            
            # Track best distance, set as inf for start
            best_dist = {direction: float("inf") for direction in self._HEX_DIRECTIONS.keys()}

            # Iterate through seats to find one with lowest distance
            for other in seats:
                if other is seat:
                    continue

                # Find distance and angel between
                dx = other.x - seat.x
                dy = other.y - seat.y
                dist = math.sqrt(dx*dx + dy*dy)
                angle = angle_between(dx, dy)

                for direction, target_angle in self._HEX_DIRECTIONS.items():

                    # Check if angle is within a sector
                    if in_sector(angle, target_angle):

                        if dist < best_dist[direction]:
                            best_dist[direction] = dist
                            candidates[direction] = other

            # Assign best found per direction
            for direction, neighbour in candidates.items():
                seat.neighbours[direction] = neighbour

        return seats

    # Function to enforce seat neighbours are mutual
    # e.g. Seat A is up of Seat B, Seat B is down of Seat A
    def _enforce_mutual_neighbours(
        self,
        seats
    ):

        # Iterate seats
        for seat in seats:
            # Iterate directions and neighbours
            for direction, neighbour in seat.neighbours.items():
                # If no neighbour, skip
                if neighbour is None:
                    continue

                # Find opposite direction
                opposite = self._OPPOSITE[direction]

                # Check neighbour's for one-way directions and make them two-way
                if neighbour.neighbours[opposite] is None:
                    neighbour.neighbours[opposite] = seat

        return seats

    # Function to filter out only mutual neighbours
    def _filter_mutual_neighbours(
        self,
        seats
    ):

        # Iterate seats
        for seat in seats:
            # Iterate directions
            for direction, neighbour in list(seat.neighbours.items()):

                # Skip if no neighbour
                if neighbour is None:
                    continue

                # Find opposite
                opp = self._OPPOSITE[direction]

                # If reciprocal link doesn't exist, then remove it
                if neighbour.neighbours.get(opp) != seat:
                    seat.neighbours[direction] = None

        return seats

    # Function that builds the electoral map into the hex-shaped grid
    def _rebuild_hex_grid(
        self,
        seats
    ):

        # Record occupied and visited seats
        occupied = set()
        visited = set()

        # Get root seat
        root = seats[0]
        root.x, root.y = 0, 0

        # Interpret x,y as axial q,r internally
        root.q, root.r = 0, 0

        occupied.add((0, 0))
        visited.add(root.name)

        # Breadth First Search
        queue = deque([root])

        while queue:

            seat = queue.popleft()

            for direction, neighbour in seat.neighbours.items():

                if neighbour is None:
                    continue

                if neighbour.name in visited:
                    continue

                dq, dr = self._HEX_OFFSETS[direction]

                raw_q = seat.q + dq
                raw_r = seat.r + dr

                q, r = self._find_free_hex(raw_q, raw_r, occupied)

                neighbour.q = q
                neighbour.r = r

                # convert axial → display coords
                neighbour.x = q + (r / 2)
                neighbour.y = r * 0.866  # sin(60°)

                occupied.add((q, r))
                visited.add(neighbour.name)
                queue.append(neighbour)

        return seats

    # Method that finds the nearest free hex
    def _find_free_hex(
        self,
        q,
        r, 
        occupied
    ):

        # If the spot is not occupied, return it
        if (q, r) not in occupied:
            return (q, r)

        # Another breadth first search until we find an empty hex space
        visited = set()
        queue = deque([(q, r)])

        while queue:
            cq, cr = queue.popleft()

            for dq, dr in self._HEX_NEIGHBOURS:
                nq, nr = cq + dq, cr + dr

                if (nq, nr) in visited:
                    continue

                visited.add((nq, nr))

                if (nq, nr) not in occupied:
                    return (nq, nr)

                queue.append((nq, nr))
