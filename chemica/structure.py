import mendeleev
import math
from math import sqrt, ceil, cos, sin, tan, atan, pi
from PIL import Image, ImageDraw, ImageFont
from chempy.util.parsing import formula_to_composition

class Bridge():
    def __init__(self, element_identifier):
        self.properties = mendeleev.element(element_identifier)
        self.connected_by = 0
        self.connections = []

        # Future Checking Purposes
        self.same = 0
        self.used_electrons = 0
        self.extra_others = 0


    def add_connection(self, bridge_symbol):
        new_bridge = bridge_symbol
        # If bridge_symbol is just an identifier, make it a bridge
        if type(bridge_symbol) != self.__class__:
            new_bridge = self.__class__(bridge_symbol)
        # Add same for future checking purposes
        if new_bridge.properties.atomic_number == self.properties.atomic_number:
            self.same += 1

        # STEP 3
        # Assign first a single bond
        new_bridge.connected_by = 1
        self.used_electrons += 1

        # STEP 4a
        # If central atom has negative left electrons, raise error
        if self.left_electrons < 0:
            return "Too many connections"
        # Count left electrons
        self.extra_others += new_bridge.left_electrons

        self.connections.append(new_bridge)
        return new_bridge


    @property
    def all_connections(self):
        # All things to show
        # Find Best - STEP 4b + 5
        if type(error_string := self.find_best()) == str:
            return error_string
        # Listify electrons to show
        electron_pair_lists = [[2] for _ in range(self.left_electrons // 2)]
        # if there's a last one
        if self.left_electrons % 2 == 1:
            electron_pair_lists.append([1])
        # if there are no more electrons left
        if len(electron_pair_lists) == 0:
            electron_pair_lists = [[]]

        # Add the elements to the electrons uniformly
        total_connections = len(self.connections)
        total_electron_pairs = len(electron_pair_lists)
        for index, element in enumerate(self.connections):
            # Case apples > basket || connections > electron_list
            if total_connections >= total_electron_pairs:
                # Identify which 'group' it will be placed in
                # How many apples can you place in a basket? Ex. 40 apples in 10 baskets = 4
                connections_per_group = total_connections // total_electron_pairs
                # After every maximum groups, move...
                electron_pair_lists[(index // connections_per_group) % total_electron_pairs] \
                    .insert(-1, element) # insert second to the last element
            # Else
            else:
                # Identify which 'group' it will be placed in
                # How many baskets can you assign to apples without overlap? Ex. 10 apples in 40 baskets = 4
                skip_by = total_electron_pairs // total_connections
                # Skip every skip_by...
                electron_pair_lists[(index * skip_by) % total_electron_pairs] \
                    .insert(-1, element) # insert second to the last element
        return electron_pair_lists


    def outward_lines(self):
        # Number of lines from self to all connections
        return sum([connection.connected_by for connection  in self.connections])


    def find_best(self):
        # Fix connections
        for connection in self.connections:
            # Only allow 2, 4, 6, 8
            needed = connection.needed if connection.needed <= 8 else 8
            lacking_electrons = needed - (2*connection.connected_by) - connection.left_electrons
            # Satisfy Needed
            if lacking_electrons != 0:
                # Add new bond
                connection.connected_by += lacking_electrons
                self.used_electrons += lacking_electrons
                # Remove the counted extra
                self.extra_others -= lacking_electrons
            # Remove the left_electrons which can no longer be used by central
            self.extra_others -= connection.left_electrons
            # No need to check for formal charge as that process maintains formal charge 0... In fact, I won't check for
            # it at all

        # Fix self
        # I think it's already fixed by doing above?
        if self.extra_others != 0:
            # Something went wrong
            return "Invalid Reagents"
        # lacking_electrons = self.needed - self.left_electrons - 2*self.outward_lines
        # # Satisfy Needed
        # if lacking_electrons != 0 and self.needed == 8:
        #     # How did this happen?
        #     # I don't know what to do


    @property
    def needed(self):
        # If can't reach 8 valence electrons or more than 8 valence electrons [exceptions to the octet rule]
        if self.properties.nvalence() <= 3 or self.properties.period >= 3:
            return self.properties.nvalence() * 2
        return 8


    @property
    def left_electrons(self):
        # Electrons not used in reactions
        return self.properties.nvalence() - self.connected_by - self.used_electrons


class Structure():
    def __init__(self, composition):
        # 5 steps to make a Lewis Dot Structure - Internet
        # 1 - Count total valence electrons [skipped, counted 'left electrons' instead]
        # 2 - Choose center (least electronegative, Carbon +1 priority, Hydrogen -1 priority)
        # 3 - Connect all by a single bond
        # 4 - [Count extra then] Distribute the extra electrons
        # 5 - Make sure everyone is happy
        self.composition = composition
        self._pil_canvas = Image.new("RGB", (500, 500), (255, 255, 255))
        self._font = ImageFont.truetype("./resources/fonts/quivira.regular.otf", 50)

        # STEP 2
        self.find_central_element()


    def find_central_element(self):
        def which(x):
            # Make H last
            if x.properties.atomic_number == 1:
                return 5
            # Make C first
            elif x.properties.atomic_number == 6:
                return -1
            return x.properties.en_pauling

        # Don't include charge
        mendeleev_elements = []
        for element_number in self.composition:
            if element_number != 0:
                # repeat inputting
                for _ in range(self.composition[element_number]):
                    mendeleev_elements.append(Bridge(element_number))
        # Sort in ascending electronegativity
        mendeleev_elements.sort(key=lambda x: which(x))

        self.central_element = mendeleev_elements[0]
        for element in mendeleev_elements[1:]:
            self.central_element.add_connection(element)


    @property
    def lewis(self):
        # NOTE: This tool can only show covalent bonding
        img = self._pil_canvas.copy()
        d = ImageDraw.Draw(img)
        # Guard, must only have at most 2 center
        if self.central_element.same > 2:
            # Double meaning to humans, 2 substances that have different centers or
            # a substance that has more than 2 centers
            d.text((250, 250), "Too many centers", fill='black', font=self._font, anchor='mm')
            return img

        # Height of font is 36 pixels (via trial and error)
        font_height = 36
        padding = 20
        # Smallest Radius of Extra Space
        # (36/2) = 18 => sqrt(a^2 + b^2) => sqrt(2a^2) => sqrt(2(18)^2) => 25.46 =ceil> 26
        smallest_radius = int(ceil(sqrt(2*(font_height / 2)**2)) * 1.5)
        line_length = 80

        center = (250, 250)
        # Make it align if there are only two elements
        if self.central_element.same == 1 or len(self.central_element.connections) == 1:
            center = (250 - (2*padding + line_length + 2*smallest_radius) // 2, 250)

        def draw_connections(current_bridge, location):
            # Connections + Lone Pairs
            all_bridge_connections = current_bridge.all_connections
            total_domains = sum([len(electron_sandwich) for electron_sandwich in all_bridge_connections])
            angle = (2*pi) / max(1, total_domains)

            # Draw self
            d.text(location, current_bridge.properties.symbol, fill='black', font=self._font, anchor='mm')

            connection_number = 0
            # Go in a circle adding lines and the element and the lone pairs
            for electron_sandwich in all_bridge_connections:
                for connection in electron_sandwich:
                    current_angle = angle * connection_number
                    adjacent = cos(current_angle)
                    opposite = sin(current_angle)
                    x_distance = padding + smallest_radius
                    y_distance = padding + smallest_radius

                    alpha = self.__class__.perpendicular_angle(current_angle)
                    line_shape = [(location[0] + adjacent * x_distance, location[1] + opposite * y_distance),
                                  (location[0] + adjacent * (x_distance + line_length), location[1] + opposite * (y_distance + line_length))]
                    new_location = (location[0] + adjacent * (2*x_distance + line_length),
                                    location[1] + opposite * (2*y_distance + line_length))

                    # Lone Pairs
                    if type(connection) == int:
                        electron_center = (location[0] + adjacent * smallest_radius, location[1] + opposite * smallest_radius)
                        radius = 5
                        center_borders = [(electron_center[0] - radius, electron_center[1] - radius), (electron_center[0] + radius, electron_center[1] + radius)]
                        # If only 1
                        if connection == 1:
                            d.ellipse(center_borders, fill='black')
                        # If 2
                        else:
                            distance_from_center = 7
                            adjacent = distance_from_center * cos(alpha)
                            opposite = distance_from_center * sin(alpha)
                            # Draw the two electrons
                            d.ellipse([(center_borders[0][0] - adjacent, center_borders[0][1] - opposite),
                                       (center_borders[1][0] - adjacent, center_borders[1][1] - opposite)], fill='black')
                            d.ellipse([(center_borders[0][0] + adjacent, center_borders[0][1] + opposite),
                                       (center_borders[1][0] + adjacent, center_borders[1][1] + opposite)], fill='black')

                    # Element
                    else:
                        # Draw line
                        distance_per_bond = 8
                        # [Last top, Last bottom]
                        last_location = [line_shape, line_shape]
                        even = False
                        # Odd case (with center)
                        if connection.connected_by % 2 == 1:
                            # Draw center
                            d.line(line_shape, fill='black', width=5)
                        # Even case (without center)
                        else:
                            even = True

                        # Draw the top or bottom
                        for _ in range(connection.connected_by // 2):
                            if even:
                                distance = distance_per_bond // 2
                                even = False
                            else:
                                distance = distance_per_bond

                            adjacent = distance * cos(alpha)
                            opposite = distance * sin(alpha)
                            # Update last top
                            last_location[0] = [(last_location[0][0][0] + adjacent, last_location[0][0][1] + opposite),
                                                (last_location[0][1][0] + adjacent, last_location[0][1][1] + opposite)]
                            # Top direction
                            d.line(last_location[0], fill='black', width=5)

                            # Update last bottom
                            last_location[1] = [(last_location[1][0][0] - adjacent, last_location[1][0][1] - opposite),
                                                (last_location[1][1][0] - adjacent, last_location[1][1][1] - opposite)]
                            # Bottom direction
                            d.line(last_location[1], fill='black', width=5)

                        # Draw next element and its connections
                        draw_connections(connection, new_location)
                    connection_number += 1


        # Draw compound recursively
        draw_connections(self.central_element, center)
        img.save("test.png")
        return img


    @classmethod
    def from_formula(cls, formula):
        return cls(formula_to_composition(formula))


    @staticmethod
    def perpendicular_angle(theta):
        # Turn to slope
        m = tan(theta)
        # Perpendicular slope
        if m != 0:
            # Non-zero slope
            m_perp = -m**-1
            # Turn back to angle
            return atan(m_perp)
        return pi/2



