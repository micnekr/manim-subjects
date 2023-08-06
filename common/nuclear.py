import manim as _m
import numpy as np
import math

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
    
# Generates a pattern of circles within circles
def _generate_full_nucleus_pattern(number_of_particles, nucleon_separation, particle_num_difference):
    # The pattern consists of n circles, each with a different number of particles
    # Let's see how many particles there are in each circle
    particle_nums = []
    particle_num_in_layer = 1
    while True:
        # If ran out of particles, add the remaining ones
        if number_of_particles <= particle_num_in_layer:
            particle_nums.append(number_of_particles)
            break
        # Reduce the number of available particles
        number_of_particles -= particle_num_in_layer
        particle_nums.append(particle_num_in_layer)
        
        
        particle_num_in_layer += particle_num_difference

    out = []
    # For each of circles, generate particles evenly around the circle, and then displace them
    for particle_num in particle_nums:
        # Pick the radius in such a way that the nucleon_separation is the distance between two consequtive nucleons
        # Arc length is nucleon_separation, and arc length = radius * angle
        # Each small angle is 2pi/particle_num
        radius = nucleon_separation / (2*np.pi) * particle_num
        for angle in np.linspace(0, 2*np.pi, particle_num, endpoint=False):
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            out.append((x, y))
    return out

def create_nucleus(num_protons, num_neutrons, nucleon_separation, particle_num_difference, nucleon_size_multiplier=0.3, seed=1):
    import random
    import math
    random.seed(seed)

    sq_nucleon_separation = nucleon_separation ** 2

    # Make a random list of neutrons and protons
    nucleon_types = [PROTON] * num_protons + [NEUTRON] * num_neutrons
    random.shuffle(nucleon_types)

    pattern = _generate_full_nucleus_pattern(num_protons + num_neutrons, nucleon_separation, particle_num_difference)
    # shuffle the pattern as well to introduce a random z-index to the nucleons (for more interesting overlapping)
    random.shuffle(pattern)

    out = _m.VGroup()
    for nucleon_type, position in zip(nucleon_types, pattern):
        x, y = position
        proton = create_particle(nucleon_type, nucleon_size_multiplier)
        proton.shift(x * _m.RIGHT, y * _m.UP)
        out.add(proton)
        
    return out
    