import manim as _m

# The different particles
PROTON = 0
NEUTRON = 1
ELECTRON = 2
POSITRON = 3

_colors_by_charge = {
    # [oultine, fill]
    1: [_m.RED, "#ce1616"],
    0: [_m.WHITE, "#e8e8e8"],
    -1: [_m.BLUE, "#5d96ea"],
}

def _is_nucleon(type):
    return type in [PROTON, NEUTRON]

def _get_charge(type):
    if type in [NEUTRON]:
        return 0
    elif type in [ELECTRON]:
        return -1
    else:
        return 1

def _get_drawn_size(type):
    if _is_nucleon(type):
        return 1
    else:
        return 0.5
    
def create_particle(type, size_multiplier=0.3):
    charge = _get_charge(type)
    color = _colors_by_charge[charge]
    drawn_size = size_multiplier * _get_drawn_size(type)
    
    circle = _m.Circle(radius=drawn_size)
    circle.set_stroke(color[0], opacity=1)
    circle.set_fill(color[1], opacity=1)
    return circle

def create_nucleus(num_protons, num_neutrons, radius, nucleon_separation, num_tries=3, nucleon_size_multiplier=0.3, seed=1):
    import random
    import math
    random.seed(seed)

    sq_nucleon_separation = nucleon_separation ** 2

    # Make a random list of neutrons and protons
    nucleon_types = [PROTON] * num_protons + [NEUTRON] * num_neutrons
    random.shuffle(nucleon_types)

    # Now, generate the positions of nucleons
    # We are trying to generate new nucleons in positions that are the furthest from other nucleon positions
    
    # Generate an x and y somewhere in the atom
    def gen_position_candidate():
        distance = random.uniform(0, radius)
        rotation = random.uniform(0, 2 * math.pi)
        return (math.cos(rotation) * distance, math.sin(rotation) * distance)

    # Get the score of the distance between two points
    # NOTE: larger score is better
    def get_score(c1, c2):
        # We want the distance to be close to nucleon_separation
        x1, y1 = c1
        x2, y2 = c2
        squared_dist = (x1 - x2) ** 2 + (y1 - y2) ** 2
        # The score is the squared difference between the squared dist and squared nucleon separation
        # The value is negative because larger score is better
        return - (sq_nucleon_separation - squared_dist) ** 2
        
    # Get the combined score for all nucleons for a given coord
    # NOTE: larger score is better
    def get_combined_score(nucleon_coords, coords):
        total = 0
        for c in nucleon_coords:
            total += get_score(c, coords)
        return total

    # For each nucleon, try num_tries times to put it in a place, pick the place with the largest score
    out = _m.VGroup()
    positions = []
    
    for nucleon_type in nucleon_types:
        # Find the best scoring try
        position_candidates = [gen_position_candidate() for _ in range(num_tries)]
        scores = list(map(lambda c: get_combined_score(positions, c), position_candidates))
        best_score = max(scores)

        # Find the best scoring position
        position = position_candidates[scores.index(best_score)]

        positions.append(position)

        nucleon = create_particle(nucleon_type, size_multiplier=nucleon_size_multiplier)
        nucleon.shift(position[0] * _m.UP + position[1] * _m.RIGHT)
        out.add(nucleon)

    return out
    