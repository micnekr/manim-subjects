import sys
sys.path.append('../')

from manim import *
from common import nuclear
from importlib import reload
import random
import numpy as np

config.media_width = "75%"
config.media_embed = True

PARTICLE_SIZE_MULTIPLIER = 0.6
NUCLEON_SEPARATION = 1.0
PARTICLE_LABEL_FONT_SIZE = 30
HEADING_FONT_SIZE = 170

class TypesOfDecayScene(Scene):
    def construct(self):

        heading = Tex(r"$\alpha$ decay", font_size=HEADING_FONT_SIZE).shift(2.3 * UP)
        self.play(Write(heading))

        ## Prepare the scene
        nucleus = nuclear.Nucleus().init_from_nums(12, 12, NUCLEON_SEPARATION, 4, PARTICLE_SIZE_MULTIPLIER, seed=6)
        nucleus.shift(DOWN)

        # show the nucleus on screen
        self.play(*nucleus.create_anims(DrawBorderThenFill))

        self.wait()

        ## Alpha decay
        daughter1, daughter2, pairs1, pairs2 = nucleus.decay(2, 2, (2, -1), False, False, seed=1)

        # Move the bigger daughter nucleus to where we started to avoid weird shifts
        daughter2.move_to(nucleus)
        daughter1.shift(4 * RIGHT + 2 * DOWN)

        self.play(*map(lambda p: ReplacementTransform(p[0], p[1]), pairs1 + pairs2))

        self.wait()

        # Clean up
        self.play(*daughter1.create_anims(Uncreate))  # hide the alpha particle
        nucleus = daughter2

        ## Beta - decay
        self.beta_decay(False, nucleus, heading)

        self.wait()

        ## Beta + decay
        self.beta_decay(True, nucleus, heading)

        ## Gamma decay
        heading_gamma = Tex(r"$\gamma$ decay", font_size=HEADING_FONT_SIZE).move_to(heading)
        self.play(ReplacementTransform(heading, heading_gamma))
        new_nucleons = nucleus.get_nucleons_list()
        random.shuffle(new_nucleons)
        new_nucleus = nuclear.Nucleus().init_from_nucleons(new_nucleons, NUCLEON_SEPARATION, 4, PARTICLE_SIZE_MULTIPLIER, False)
        new_nucleus.move_to(nucleus)
        # Find some point on the edge of the nucleus

        gamma_init_coords = nucleus.find_closest_nucleon((0, 0)).get_center()
        initial_arrow = Arrow(start=gamma_init_coords, end=gamma_init_coords)
        final_arrow = Arrow(start=gamma_init_coords, end=(4 * RIGHT + 2 * UP))
        # Move the gamma particle with the arrow
        gamma_label = MathTex(r"\gamma", font_size=PARTICLE_LABEL_FONT_SIZE)
        gamma_label.move_to(initial_arrow)
        gamma_label.add_updater(lambda x: x.move_to(initial_arrow.point_from_proportion(0.7)).shift(0.3 * UP))
        self.add(initial_arrow, gamma_label)
        # Go from each original nucleon to the shuffled one
        self.play(ReplacementTransform(initial_arrow, final_arrow), 
                  *map(lambda n: ReplacementTransform(n[0], n[1]),
                       zip(new_nucleons, new_nucleus.get_nucleons_list())))
        self.wait(1)

    def beta_decay(self, is_plus, nucleus, heading):
        if is_plus:
            sign_letter = "+"
            nucleon_type = nuclear.PROTON
            new_nucleon_type = nuclear.NEUTRON
            beta_type = nuclear.POSITRON
            neutrino_label = r"\nu_e"
        else:
            sign_letter = "-"
            nucleon_type = nuclear.NEUTRON
            new_nucleon_type = nuclear.PROTON
            beta_type = nuclear.ELECTRON
            neutrino_label = r"\bar{\nu_e}"

        new_heading = Tex(f"$\\beta^{sign_letter}$ decay", font_size=HEADING_FONT_SIZE).move_to(heading)
        self.play(Transform(heading, new_heading))

        nucleon = nucleus.find_closest_nucleon((-2, 0), nucleon_type)

        beta = nuclear.Particle(beta_type, PARTICLE_SIZE_MULTIPLIER)
        beta.move_to(nucleon)

        beta_label1 = nuclear.ParticleLabel(beta, PARTICLE_LABEL_FONT_SIZE, f"\\beta^{sign_letter}")
        beta_label2 = nuclear.ParticleLabel(beta, PARTICLE_LABEL_FONT_SIZE)

        neutrino = nuclear.Particle(nuclear.NEUTRINO, PARTICLE_SIZE_MULTIPLIER)
        neutrino_label = nuclear.ParticleLabel(neutrino, PARTICLE_LABEL_FONT_SIZE, neutrino_label, color=DARK_GRAY)
        neutrino.move_to(nucleon)

        self.add(beta, beta_label1, neutrino, neutrino_label)
        self.play(nucleon.animate.set_particle_type(new_nucleon_type), beta.animate.shift(2 * LEFT + DOWN),
                  neutrino.animate.shift(2.5 * LEFT + UP), run_time=1)

        self.wait()

        self.play(ReplacementTransform(beta_label1, beta_label2))

        self.wait()

        # Clean up
        self.play(Uncreate(beta), Uncreate(beta_label2),
                  Uncreate(neutrino), Uncreate(neutrino_label))  # destroy the beta particle

class ForcesHoldingNucleusTogetherScene(Scene):
    def construct(self):
        ## Prepare the scene
        nucleus = nuclear.Nucleus().init_from_nums(4, 3, NUCLEON_SEPARATION, 5, PARTICLE_SIZE_MULTIPLIER, seed=1)

        original_nucleus = nucleus.copy()

        # show the nucleus on screen
        self.play(*nucleus.create_anims(DrawBorderThenFill))

        ## Illustrate balance of forces
        # Draw attractive and repulsive forces to show the balance of forces
        proton = nucleus.find_closest_nucleon((-1, 0), nuclear.PROTON)
        proton_center = proton.get_center()
        attractive_arrow_length = ValueTracker(1.0)
        repulsive_arrow_length = ValueTracker(2.0)
        attractive_arrow = Arrow(buff=0, start=proton_center, end=proton_center + attractive_arrow_length.get_value() * RIGHT, color=GREEN_B, z_index=20)
        repulsive_arrow = Arrow(buff=0, start=proton_center, end=proton_center + repulsive_arrow_length.get_value() * LEFT, color=YELLOW, z_index=20)
        # Make the tip not disappear as well
        attractive_arrow.submobjects[0].z_index = 20

        self.play(GrowArrow(attractive_arrow))

        self.wait()

        self.play(GrowArrow(repulsive_arrow))

        # Make the arrows follow the proton
        attractive_arrow.add_updater(lambda a: a.put_start_and_end_on(proton.get_center(), proton.get_center() + attractive_arrow_length.get_value() * RIGHT))
        repulsive_arrow.add_updater(lambda a: a.put_start_and_end_on(proton.get_center(), proton.get_center() + repulsive_arrow_length.get_value() * LEFT))

        self.wait()

        # Move the nucleons apart, to show a decay
        expanded_nucleus = nuclear.Nucleus().init_from_nums(4, 3, 3 * NUCLEON_SEPARATION, 5, PARTICLE_SIZE_MULTIPLIER, seed=1)
        self.play(Transform(nucleus, expanded_nucleus))

        self.wait()

        # Move the nucleons back together
        self.play(Transform(nucleus, original_nucleus))

        # Show weakening of repulsive forces
        self.play(repulsive_arrow_length.animate.set_value(1.0))
        self.wait(0.3)
        # Reset the arrow
        self.play(repulsive_arrow_length.animate.set_value(2.0))
        # Show strengthening of attractive forces
        self.play(attractive_arrow_length.animate.set_value(2.0))

        self.wait(0.5)

        self.play(FadeOut(attractive_arrow), FadeOut(repulsive_arrow))

        # Decay the nucleus
        proton, new_nucleus, pairs1, pairs2 = nucleus.decay(1, 0, (-1, 0), False, False, seed=1)

        proton.shift(5 * LEFT)
        new_nucleus.move_to(nucleus)

        self.play(*map(lambda p: ReplacementTransform(p[0], p[1]), pairs1 + pairs2))

        self.wait()



# Coefficients for strong force graph
STRONG_FORCE_A = 2
STRONG_FORCE_B = -0.95
STRONG_FORCE_C = -7
EM_FORCE_A = 0.4

class CompareForces(Scene):

    def strong_force_calculation(x):
        # Do some shifting and scaling to the input
        x = STRONG_FORCE_A * x + STRONG_FORCE_B
        return STRONG_FORCE_C * x / np.exp(x)

    def em_force_calculation(x):
        # Do some shifting and scaling to the input
        return EM_FORCE_A * x ** -2

    def construct(self):
        ax = Axes(
            x_range=[0, 4.6, 0.5],
            x_length=6,
            y_length=4,
            x_axis_config={
                "numbers_to_include": [0.5, 1, 3],
            },
            y_axis_config={
                "numbers_to_include": [],
                "include_ticks": False,
            },
            tips=True,
        )
        y_label = ax.get_y_axis_label(
            Tex("Force strength").scale(0.65).rotate(90 * DEGREES),
            edge=LEFT,
            direction=LEFT,
            buff=0.3,
        )
        x_label = ax.get_x_axis_label(
            Tex("Distance").scale(0.65), edge=DOWN, direction=DOWN, buff=0.5
        )
        strong_force_graph = ax.plot(CompareForces.strong_force_calculation, color=GREEN_B, x_range=[0.3, 4, 0.05])
        em_force_graph = ax.plot(CompareForces.em_force_calculation, color=YELLOW, x_range=[0.3, 4, 0.05])
        axes_group = VGroup(y_label, x_label, ax)
        entire_graph = VGroup(axes_group, em_force_graph, strong_force_graph)

        entire_graph.shift(2 * LEFT)

        self.play(Write(axes_group))
        self.wait()
        self.play(Create(em_force_graph))
        self.wait()
        self.play(Create(strong_force_graph))

        self.wait(20)
