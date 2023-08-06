import manim as _m
import numpy as np
import random
import math

# The different particles
PROTON = 0
NEUTRON = 1
ELECTRON = 2
POSITRON = 3


class Particle(_m.Circle):
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
        if Particle._is_nucleon(type):
            return 1
        else:
            return 0.5
            
    def __init__(self, type, size_multiplier=0.3):
        self.charge = _get_charge(type)
        color = _colors_by_charge[self.charge]
        drawn_size = size_multiplier * _get_drawn_size(type)

        super().__init__(radius=drawn_size)
        
        self.set_stroke(color[0], opacity=1)
        self.set_fill(color[1], opacity=1)

class Nucleus(_m.VGroup):
    class Nucleon(Particle):
        """Represents a particle with its offset from the centre of the nucleus"""
        def __init__(self, type, size_multiplier, coords):
            super().__init__(type, size_multiplier)
            self.coords = coords

    def _generate_full_nucleus_pattern(number_of_particles, nucleon_separation, particle_num_difference):
        """Generate a list of positions that evenly spread `number_of_particles` particles
        This is done by drawing progressively larger concentric circles of particles
        """
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
        # For each of circles, generate particles evenly around the circle
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
    
    def __init__(self, num_protons, num_neutrons, nucleon_separation, particle_num_difference, nucleon_size_multiplier=0.3, seed=1):
        super().__init__()
        self.nucleons = []
        random.seed(seed)
    
        sq_nucleon_separation = nucleon_separation ** 2
    
        # Make a random list of neutrons and protons
        nucleon_types = [PROTON] * num_protons + [NEUTRON] * num_neutrons
        random.shuffle(nucleon_types)
    
        pattern = Nucleus._generate_full_nucleus_pattern(num_protons + num_neutrons, nucleon_separation, particle_num_difference)
        # shuffle the pattern as well to introduce a random z-index to the nucleons (for more interesting overlapping)
        random.shuffle(pattern)
    
        for nucleon_type, position in zip(nucleon_types, pattern):
            x, y = position
            nucleon = Nucleus.Nucleon(nucleon_type, nucleon_size_multiplier, position)
            nucleon.shift(x * _m.RIGHT, y * _m.UP)
            self.add(nucleon)
            self.nucleons.append(nucleon)

    def create_anims(self):
        return map(lambda nucleon: _m.Create(nucleon), self.nucleons)
