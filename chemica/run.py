import chempy
import mendeleev
from math import gcd
from typing import Union
try:
    from .substance import Substance
    from .properties import *
except ImportError:
    from substance import Substance
    from properties import *

# For redox
# NOTE
# I searched a bit and found this: https://www.quora.com/How-has-the-reactivity-series-or-activity-series-been-determined-in-chemistry-On-what-basis
# Maybe use it instead of a list (however, I don't think the dependencies I am currently using support it)
# HIGHEST TO LOWEST REACTIVITY
# Li, Rb, K, Ba, Ca, Na, Mg, Al, Mn, Zn, Cr, Fe, Ni, Sn, Pb, H, Cu, Hg, Ag, Pt, Au
METAL_ACTIVITY_SERIES = [3, 37, 19, 56, 20, 11, 12, 13, 30, 24, 26, 28, 50, 82, 1, 29, 80, 47, 78, 79]
# F, Cl, Br, I
NONMETAL_ACTIVITY_SERIES = [9, 17, 35, 53]
DIATOMIC_MOLECULES = [1, 7, 8, 9, 17, 35, 53]


def process_compositions(compositions: list[dict[int, int]]):
    clean_compositions = []
    for composition in compositions:
        # Diatomic molecule
        for key in composition:
            # If it's alone and 1 and diatomic
            if len(composition) == 1 and composition[key] == 1 and key in DIATOMIC_MOLECULES:
                composition[key] = 2
            # If we only need to know if it's 1, then we shouldn't check anymore
            break

        # Simplify
        # Find gcd of all
        composition_values = list(composition.values())
        common_factor = composition_values[0] if len(composition_values) != 1 else 1
        for value_index in range(1, len(composition_values)):
            common_factor = gcd(common_factor, composition_values[value_index])
        # Divide common factor
        for key in composition:
            composition[key] //= common_factor

        clean_compositions.append(composition)

    return clean_compositions


def process_molecule(X: dict[int, int], first: bool = False, second: bool = False) -> list[mendeleev.models.Element, int]:
    # If charge is given
    if len(X) == 2:
        charge = X[0]
        del X[0]
        # Get as mendeleev.element
        element = mendeleev.element(list(X.keys())[0])

    # Else if 1
    else:
        # Get as mendeleev.element
        element = mendeleev.element(list(X.keys())[0])
        charge = charge_set(element.ionic_radii)

    # NOTE
    # Might process which charge to return in metalloids? But for now, no, there aren't
    # that many reactions with metalloids (I think)
    returned_charge = list(charge)[0]
    # NOTE: bandaging method, will hopefully change in the future
    if first:
        for list_charge in list(charge):
            if list_charge > 0:
                returned_charge = list_charge
                break
    if second:
        for list_charge in list(charge):
            if list_charge < 0:
                returned_charge = list_charge
                break

    return [element, returned_charge]


def process_compound(X: dict[int, int]) -> list[list[mendeleev.models.Element, int], list[mendeleev.models.Element, int]]:
    metal_element = metal_charge = nonmetal_element = nonmetal_charge = None
    for index, molecule in enumerate([{mole: X[mole]} for mole in X if mole != 0]):
        # If metal
        if index == 0:
            processed_molecule = process_molecule(molecule, first=True)
        # If nonmetal
        else:
            processed_molecule = process_molecule(molecule, second=True)
        # metal charge
        if processed_molecule[1] > 0:
            metal_element, metal_charge = processed_molecule
        # nonmetal charge
        else:
            nonmetal_element, nonmetal_charge = processed_molecule

    # [metal+, nonmetal-]
    return [[metal_element, metal_charge], [nonmetal_element, nonmetal_charge]]


def synthesis(A: dict[int, int], B: dict[int, int]) -> list[dict]:
    A_element, A_charge = process_molecule(A)
    B_element, B_charge = process_molecule(B)

    # 1 should be + and the other is -
    if (A_charge < 0 and B_charge < 0) or (A_charge > 0 and B_charge > 0):
        return "Invalid reagents"

    positive = lambda x: -x if x < 0 else x
    # criss-cross
    composition = {
        A_element.atomic_number: positive(B_charge),
        B_element.atomic_number: positive(A_charge)
    }
    return process_compositions([composition])


def redox(A: dict[int, int], B: dict[int, int]) -> list[dict]:
    def get_activity_series_position(atomic_number, is_metal):
        if is_metal:
            return METAL_ACTIVITY_SERIES.index(atomic_number)
        return NONMETAL_ACTIVITY_SERIES.index(atomic_number)

    # If B is compound
    if len(B) == 2 and not 0 in B:
        lone_element, lone_charge = process_molecule(A)
        metallic_element, nonmetallic_element = process_compound(B)
        metal_element, metal_charge = metallic_element
        nonmetal_element, nonmetal_charge = nonmetallic_element
        
    # If A is compound
    else:
        lone_element, lone_charge = process_molecule(B)
        metallic_element, nonmetallic_element = process_compound(A)
        metal_element, metal_charge = metallic_element
        nonmetal_element, nonmetal_charge = nonmetallic_element
    
    # NOTE
    # Covalent redox is currently unsupported
    # If something is None guard
    if metal_charge is None or nonmetal_charge is None:
        return "Invalid reagents"

    # Guards
    # If comparing metals
    if lone_charge > 0:
        # If chemical reaction will not happen
        # If element already paired is more reactive than lone
        if get_activity_series_position(lone_element.atomic_number, True) >= get_activity_series_position(metal_element.atomic_number, True):
            return "No reaction will occur"
    # If comparing nonmetals
    else:
        # If chemical reaction will not happen
        # If element already paired is more reactive than lone
        if get_activity_series_position(lone_element.atomic_number, False) >= get_activity_series_position(nonmetal_element.atomic_number, False):
            return "No reaction will occur"

    # A reaction will happen
    compositions = synthesis({lone_element.atomic_number: 1}, {metal_element.atomic_number: 1}) + [{nonmetal_element.atomic_number: 1}]
    return process_compositions(compositions)


def metathesis(A: dict[int, int], B: dict[int, int]) -> list[dict]:
    # A compound
    A_metallic_element, A_nonmetallic_element = process_compound(A)
    A_metal_element, A_metal_charge = A_metallic_element
    A_nonmetal_element, A_nonmetal_charge = A_nonmetallic_element
    # B compound
    B_metallic_element, B_nonmetallic_element = process_compound(B)
    B_metal_element, B_metal_charge = B_metallic_element
    B_nonmetal_element, B_nonmetal_charge = B_nonmetallic_element
    
    # NOTE
    # Covalent redox is currently unsupported
    # If something is None guard
    if A_metal_charge is None or A_nonmetal_charge is None or B_metal_charge is None or B_nonmetal_charge is None:
        return "Invalid reagents"

    # NOTE
    # Should only happen if a precipitate will occur, but due to lack of support for polyatomic atoms
    # it can't be done (or I don't know how it will be done)
    # Reaction
    compositions = synthesis(
                    # Switch Inner
                    {A_nonmetal_element.atomic_number: 1}, {B_metal_element.atomic_number: 1}
                    ) + synthesis(
                    # Switch Outer
                    {A_metal_element.atomic_number: 1}, {B_nonmetal_element.atomic_number: 1}
                    )
    return process_compositions(compositions)


def combustion(A: dict[int, int], B: dict[int, int]) -> list[dict]:
    return [
        # CO2
        {6: 1,
        8: 2},
        # H2O
        {1: 2,
        8: 1}
        ]


def run_reaction(reaction_type: str, A: dict[int, int], B: dict[int, int]) -> Union[list[dict], str]:
    if reaction_type == "UNKNOWN":
        return "Unknown reaction type"

    elif reaction_type == "SYNTHESIS":
        return synthesis(A, B)

    elif reaction_type == "REDOX":
        return redox(A, B)

    elif reaction_type == "METATHESIS":
        return metathesis(A, B)

    elif reaction_type == "COMBUSTION":
        return combustion(A, B)
