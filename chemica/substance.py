import chempy
import mendeleev
try:
    from .properties import charge_set
except ImportError:
    from properties import charge_set

class Substance(chempy.chemistry.Substance):
    @property
    def nomenclature(self):
        # if _nomeclature is not an attribute of the class
        if not "_nomenclature" in self.__dir__():
            self._nomenclature = None

        if self._nomenclature is None:
            # Call static method name_substance
            self._nomenclature = self.__class__.name_substance(self.composition)
        return self._nomenclature


    @staticmethod
    def name_substance(composition: dict[int, int]) -> str:
        greek_prefixes = lambda x: ["mono", "di", "trio", "tetra", "penta", "hexa", "hepta", "octa", "nona", "deca"][x - 1]
        name = ""

        # Don't include charge
        mendeleev_elements = [mendeleev.element(element_number) for element_number in composition if element_number != 0]
        # Sort so that leftmost group is first
        mendeleev_elements.sort(key=lambda x: x.group_id)

        # NOTE
        # Identify type of compound?
        # Binary Acid
        # Oxoacids
        # Hydrates
        # Binary
        # Not for now...

        for index, element in enumerate(mendeleev_elements):
            prefix = greek_prefixes(composition[element.atomic_number])
            element_name = "oxide" if element.atomic_number == 8 else element.name.lower()

            # No prefix, if 1st element and only one of which
            if prefix == "mono" and index == 0:
                prefix = ""
            # Prefix combination rules
            elif (prefix[-1] == ["a"] and element_name[0] in ["a", "e", "i", "o", "u"]) or (prefix[-1] == element_name[0]):
                # Remove last letter of prefix
                prefix = prefix[0:-1]

            # If it's last element
            if index + 1 == len(mendeleev_elements):
                # Allow -ide to element name
                if element_name.endswith("gen"):
                    # Remove the last 4 letters
                    element_name = element_name[0:-4]
                elif element_name.endswith("ine"):
                    # Remove the last 3 letters
                    element_name = element_name[0:-3]
                elif element_name.endswith("on"):
                    # Remove the last 2 letters
                    element_name = element_name[0:-2]
                # Add -ide if last is not yet ide (i.e. oxide)
                if not element_name.endswith("ide"):
                    element_name = element_name + "ide"

            name += prefix + element_name + " "
        return name


    @staticmethod
    def dict_to_formula(composition: dict[int, int]) -> str:
        def which(list_charge: list[int]):
            # nonmetal
            for charge in list_charge:
                if charge < 0:
                    return 1
            return 0

        formula = ""
        # Don't include charge
        mendeleev_elements = [mendeleev.element(element_number) for element_number in composition if element_number != 0]
        # Sort so that leftmost group is first
        mendeleev_elements.sort(key=lambda x: which(list(charge_set(x.ionic_radii))))

        for mendeleev_element in mendeleev_elements:
            formula += mendeleev_element.symbol
            if composition[mendeleev_element.atomic_number] != 1:
                formula += f"{composition[mendeleev_element.atomic_number]}"
        return formula
