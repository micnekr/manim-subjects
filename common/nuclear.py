import manim as _m
import numpy as np
import random
import math

from common import util

# The different particles
PROTON = 0
NEUTRON = 1
ELECTRON = 2
POSITRON = 3
NEUTRINO = 4

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
        if type in [PROTON, POSITRON]:
            return 1
        elif type in [ELECTRON]:
            return -1
        else:
            return 0
    
    def _get_drawn_size(type):
        if Particle._is_nucleon(type):
            return 1
        else:
            return 0.5
    
    def __init__(self, type, size_multiplier, **kwargs): 
        super().__init__(radius=1, **kwargs)

        self.size_multiplier = size_multiplier
        
        self.set_particle_type(type)

    def set_particle_type(self, type):
        # Change the radius
        new_radius = Particle._get_drawn_size(type) * self.size_multiplier
        self.scale(new_radius / self.radius)
        self.radius = new_radius
        
        self.type = type
        self.charge = Particle._get_charge(type)
        color = Particle._colors_by_charge[self.charge]
        self.set_stroke(color[0], opacity=1)
        self.set_fill(color[1], opacity=1)

class ParticleLabel(_m.MathTex):
    
    def _get_label_tex(type):
        if type == ELECTRON:
            return r"e^-"
        elif type == POSITRON:
            return r"e^+"
        elif type == PROTON:
            return r"p^+"
        elif type == NEUTRON:
            return r"n"
        else:
            return ""
        
    def __init__(self, particle, font_size, label_override=None, **kwargs):
        if label_override is not None:
            label_tex = label_override
        else:
            label_tex = ParticleLabel._get_label_tex(particle.type)
        super().__init__(label_tex, font_size=font_size, z_index=particle.z_index + 1, **kwargs)
        self.move_to(particle)
        self.add_updater(lambda x: x.move_to(particle))

class Nucleus(_m.VGroup):
    class Nucleon(Particle):
        """Represents a particle with its offset from the centre of the nucleus"""
        def __init__(self, type, size_multiplier, coords, **kwargs):
            super().__init__(type, size_multiplier, **kwargs)
            self.coords = coords
            x, y = coords
            self.shift(x * _m.RIGHT, y * _m.UP)

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
            # Place the central nucleon in the center
            if particle_num == 1:
                radius = 0
            layer = []
            for angle in np.linspace(0, 2*np.pi, particle_num, endpoint=False):
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
                layer.append((x, y))
            out.append(layer)
        return out
    
    def __init__(self):
        super().__init__()
        self.nucleons = []

    def init_from_nums(self, num_protons, num_neutrons, nucleon_separation, particle_num_difference, nucleon_size_multiplier, shuffle=True, seed=1):
        random.seed(seed)
        self.nucleon_separation = nucleon_separation
        self.particle_num_difference = particle_num_difference
        self.nucleon_size_multiplier = nucleon_size_multiplier
    
        # Make a random list of neutrons and protons
        nucleon_types = [PROTON] * num_protons + [NEUTRON] * num_neutrons
        random.shuffle(nucleon_types)
    
        pattern = Nucleus._generate_full_nucleus_pattern(num_protons + num_neutrons, nucleon_separation, particle_num_difference)

        if shuffle:
            # Give random z indices to have a varying overlapping structure
            z_indices = [random.randint(0, 10) for _ in range(len(nucleon_types))]
        else:
            # Otherwise, have the z-indices of 0
            z_indices = [0] * len(nucleon_types)
        
        self._init_from_pattern(pattern, nucleon_types, z_indices, nucleon_size_multiplier)
        
        return self

    def _init_from_pattern(self, pattern, nucleon_types, z_indices, nucleon_size_multiplier):
        i = 0
        for positions_in_layer in pattern:
            nucleons_in_layer = []
            for position in positions_in_layer:
                nucleon_type = nucleon_types[i]
                nucleon = Nucleus.Nucleon(nucleon_type, nucleon_size_multiplier, position, z_index=z_indices[i])
                self.add(nucleon)
                nucleons_in_layer.append(nucleon)
                i += 1
            self.nucleons.append(nucleons_in_layer)

    def init_from_nucleons(self, nucleons_list, nucleon_separation, particle_num_difference, nucleon_size_multiplier, shuffle, seed=1):
        random.seed(seed)
        self.nucleon_separation = nucleon_separation
        self.particle_num_difference = particle_num_difference
        self.nucleon_size_multiplier = nucleon_size_multiplier
        
        pattern = Nucleus._generate_full_nucleus_pattern(len(nucleons_list), nucleon_separation, particle_num_difference)

        nucleon_types = list(map(lambda n: n.type, nucleons_list))

        if shuffle:
            # Give random z indices to have a varying overlapping structure
            z_indices = [random.randint(0, 10) for _ in range(len(nucleon_types))]
        else:
            # Otherwise, preserve the z-indices
            z_indices = list(map(lambda n: n.z_index, nucleons_list))
        
        self._init_from_pattern(pattern, nucleon_types, z_indices, nucleon_size_multiplier)
        
        return self

    def _enforce_init(self):
        if len(self.nucleons) == 0:
            raise Exception("Please initialise the nucleus before using it")
    
    def create_anims(self, anim):
        self._enforce_init()
        return map(lambda nucleon: anim(nucleon), self.get_nucleons_list())

    def _sq_dist(c1, c2):
        x1, y1 = c1
        x2, y2 = c2
        return (x1 - x2) ** 2 + (y1 - y2) ** 2

    def get_nucleons_list(self):
        return util.flatMap(self.nucleons)
    
    def decay(self, num_protons, num_neutrons, start_position, shuffle1=True, shuffle2=True, seed=1):
        """Returns two daughter nuclei, one of which has the specified number of protons and neutrons, with Transform animations to get from one to another"""
        # Sort the nuclei by distance to the start position
        # Note: using squared distance to save computing power
        nucleons_list = self.get_nucleons_list()
        indices_sorted_by_distance = sorted(range(len(nucleons_list)), key=lambda i: Nucleus._sq_dist(start_position, nucleons_list[i].coords))

        # Collect the indices into the first daughter nucleus by a quota
        neutrons_left = num_neutrons
        protons_left = num_protons
        daughter1_nucleon_indices = []
        daughter2_nucleon_indices = []
        for i in indices_sorted_by_distance:
            nucleon = nucleons_list[i]
            type = nucleon.type
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
        
        daughter1_nucleons = [nucleons_list[i] for i in daughter1_nucleon_indices]
        daughter2_nucleons = [nucleons_list[i] for i in daughter2_nucleon_indices]
        
        daughter1 = Nucleus().init_from_nucleons(
            daughter1_nucleons, self.nucleon_separation, self.particle_num_difference, self.nucleon_size_multiplier, shuffle1, seed)
        daughter2 = Nucleus().init_from_nucleons(
            daughter2_nucleons, self.nucleon_separation, self.particle_num_difference, self.nucleon_size_multiplier, shuffle2, seed)

        daughter1_nucleons = daughter1.get_nucleons_list()
        daughter2_nucleons = daughter2.get_nucleons_list()

        
        daughter1_pairs = []
        daughter2_pairs = []
        # Go through each original nucleon and find the daughter nucleon it ended up being
        for i, nucleon in enumerate(nucleons_list):
            if i in daughter1_nucleon_indices:
                new_nucleon = daughter1_nucleons[daughter1_nucleon_indices.index(i)]
                daughter1_pairs.append((nucleon, new_nucleon))
            else:
                new_nucleon = daughter2_nucleons[daughter2_nucleon_indices.index(i)]
                daughter2_pairs.append((nucleon, new_nucleon))

        return (daughter1, daughter2, daughter1_pairs, daughter2_pairs)

    def find_closest_nucleon(self, position, filter_type=None):
        nucleons = self.get_nucleons_list()
        if filter_type is not None:
            nucleons = filter(lambda n: n.type == filter_type, nucleons)
        return min(nucleons, key=lambda n: Nucleus._sq_dist(n.coords, position))
