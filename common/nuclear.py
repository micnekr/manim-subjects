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
        self.type = type
        self.charge = Particle._get_charge(type)
        color = Particle._colors_by_charge[self.charge]
        drawn_size = size_multiplier * Particle._get_drawn_size(type)

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
        # Reverse the layer order to allow the central atoms to cover other atoms if no shuffling has been enabled
        # This happens because central atoms are added last
        for particle_num in reversed(particle_nums):
            # Pick the radius in such a way that the nucleon_separation is the distance between two consequtive nucleons
            # Arc length is nucleon_separation, and arc length = radius * angle
            # Each small angle is 2pi/particle_num
            radius = nucleon_separation / (2*np.pi) * particle_num
            for angle in np.linspace(0, 2*np.pi, particle_num, endpoint=False):
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
                out.append((x, y))
        return out
    
    def __init__(self):
        super().__init__()
        self.nucleons = []

    def init_from_nums(self, num_protons, num_neutrons, nucleon_separation, particle_num_difference, nucleon_size_multiplier=0.3, seed=1):
        random.seed(seed)
        self.nucleon_separation = nucleon_separation
        self.particle_num_difference = particle_num_difference
        self.nucleon_size_multiplier = nucleon_size_multiplier
    
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
        return self

    def init_from_nucleons(self, new_nucleons, nucleon_separation, particle_num_difference, shuffle, seed=1,  nucleon_size_multiplier=0.3):
        self.nucleon_separation = nucleon_separation
        self.particle_num_difference = particle_num_difference
        self.nucleon_size_multiplier = nucleon_size_multiplier
        
        pattern = Nucleus._generate_full_nucleus_pattern(len(new_nucleons), nucleon_separation, particle_num_difference)
        if shuffle:
            random.seed(seed)
            random.shuffle(pattern)
        for nucleon, position in zip(new_nucleons, pattern):
            x, y = position
            nucleon = Nucleus.Nucleon(nucleon.type, nucleon_size_multiplier, position)
            nucleon.shift(x * _m.RIGHT, y * _m.UP)
            self.add(nucleon)
            self.nucleons.append(nucleon)
        return self

    def _enforce_init(self):
        if len(self.nucleons) == 0:
            raise Exception("Please initialise the nucleus before using it")
    
    def create_anims(self):
        self._enforce_init()
        return map(lambda nucleon: _m.Create(nucleon), self.nucleons)

    def _sq_dist(c1, c2):
        x1, y1 = c1
        x2, y2 = c2
        return (x1 - x2) ** 2 + (y1 - y2) ** 2
    
    def decay(self, num_protons, num_neutrons, start_position, shuffle1=True, shuffle2=True, seed=1):
        """Returns two daughter nuclei, one of which has the specified number of protons and neutrons, with Transform animations to get from one to another"""
        # Sort the nuclei by distance to the start position
        # Note: using squared distance to save computing power
        indices_sorted_by_distance = sorted(range(len(self.nucleons)), key=lambda i: Nucleus._sq_dist(start_position, self.nucleons[i].coords))

        # Collect the indices into the first daughter nucleus by a quota
        neutrons_left = num_neutrons
        protons_left = num_protons
        daughter1_nucleon_indices = []
        daughter2_nucleon_indices = []
        for i in indices_sorted_by_distance:
            type = self.nucleons[i].type
            nucleon = self.nucleons[i]
            if type == PROTON and protons_left > 0:
                protons_left -=1
                daughter1_nucleon_indices.append(i)
            elif type == NEUTRON and neutrons_left > 0:
                neutrons_left -=1
                daughter1_nucleon_indices.append(i)
            else:
                # If the quota has already been met, add it to the other daughter nucleus
                daughter2_nucleon_indices.append(i)
        # Sort each list so that nucleons do not change position too much
        daughter1_nucleon_indices.sort()
        daughter2_nucleon_indices.sort()
        
        daughter1_nucleons = [self.nucleons[i] for i in daughter1_nucleon_indices]
        daughter2_nucleons = [self.nucleons[i] for i in daughter2_nucleon_indices]
        
        daughter1 = Nucleus().init_from_nucleons(
            daughter1_nucleons, self.nucleon_separation, self.particle_num_difference, shuffle1, seed, self.nucleon_size_multiplier)
        daughter2 = Nucleus().init_from_nucleons(
            daughter2_nucleons, self.nucleon_separation, self.particle_num_difference, shuffle2, seed, self.nucleon_size_multiplier)

        daughter1_pairs = []
        daughter2_pairs = []
        # Go through each original nucleon and find the daughter nucleon it ended up being
        for i, nucleon in enumerate(self.nucleons):
            if i in daughter1_nucleon_indices:
                new_nucleon = daughter1.nucleons[daughter1_nucleon_indices.index(i)]
                daughter1_pairs.append((nucleon, new_nucleon))
            else:
                new_nucleon = daughter2.nucleons[daughter2_nucleon_indices.index(i)]
                daughter2_pairs.append((nucleon, new_nucleon))
                
        return (daughter1, daughter2, daughter1_pairs, daughter2_pairs)
