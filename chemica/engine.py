import chempy
import mendeleev
try:
    from .substance import Substance
    from .structure import Structure
    from .run import run_reaction, process_compositions
except ImportError:
    from substance import Substance
    from structure import Structure
    from run import run_reaction, process_compositions


def expected_reaction_type(A_composition: dict[int, int], B_composition: dict[int, int]) -> str:
    # TYPES OF REACTIONS:
    # Synthesis (Combination) [A + B -> C]
    # Decomposition [AB -> A + B] - Unsupported due to design NOTE
    # Single Replacement [A + BC -> AC + B]
    # Double Replacement [AB + CD -> BC + AD] - Not fully supported due to lack of support for polyatomic atoms NOTE
    # Combustion [CxHy + O2 -> CO2 + H2O]

    # if statements already works as length of A and B needs to be > 0
    # SYNTHESIS
    if len(A_composition) + len(B_composition) == 2:
        return "SYNTHESIS"

    # REDOX OR COMBUSTION
    elif len(A_composition) + len(B_composition) == 3:
        # IF COMBUSTION
        if (6 in A_composition and 1 in A_composition and list(B_composition.keys()) == [8] and B_composition[8] == 2) or (6 in B_composition and 1 in B_composition and list(A_composition.keys()) == [8] and A_composition[8] == 2):
            return "COMBUSTION"
        # ELSE REDOX
        return "REDOX"

    # METATHESIS
    elif len(A_composition) + len(B_composition) == 4 and len(A_composition) == 2:
        return "METATHESIS"
    return "UNKNOWN"


def reaction_equation(reac: dict[str, int], prod: dict[str, int]):
    full_equation_str = ""

    # Reactants
    for index, substance in enumerate(reac):
        # if not start
        if index != 0:
            full_equation_str += "+ "
        if reac[substance] != 1:
            full_equation_str += f"{reac[substance]} "
        full_equation_str += substance + " "

    full_equation_str += "→ "
    # Products
    for index, substance in enumerate(prod):
        # if not start
        if index != 0:
            full_equation_str += "+ "
        if prod[substance] != 1:
            full_equation_str += f"{prod[substance]} "
        full_equation_str += substance + " "

    return full_equation_str


def solve(A: str, B: str) -> None:
    first_substance = Substance.from_formula(A)
    second_substance = Substance.from_formula(B)

    first_substance_composition = first_substance.composition.copy()
    second_substance_composition = second_substance.composition.copy()

    # Don't show charge in composition
    if 0 in first_substance_composition:
        del first_substance_composition[0]
    if 0 in second_substance_composition:
        del second_substance_composition[0]

    reaction_type = expected_reaction_type(first_substance_composition, second_substance_composition)
    # Run respective reaction
    solved_products = run_reaction(reaction_type, first_substance.composition, second_substance.composition)
    if type(solved_products) == str:
        return solved_products

    reac, prod = chempy.chemistry.balance_stoichiometry(
        # Reactants
        set([Substance.dict_to_formula(reactant)
            for reactant in process_compositions(
                [first_substance.composition, second_substance.composition]
            )]),
        # Products
        set([Substance.dict_to_formula(solved_product) for solved_product in solved_products]))
    # Turn into reaction
    return reaction_equation(reac, prod), [reac, prod]


def test(default=False):
    if default:
        first_substance = "F2"
        print(f"First Substance: {first_substance}")
    else:
        first_substance = input("First Substance: ")

    print("+")

    if default:
        second_substance = "NaCl"
        print(f"Second Substance: {second_substance}")
    else:
        second_substance = input("Second Substance: ")

    print("->")
    print(solve(first_substance, second_substance))


if __name__ == "__main__":
    test()