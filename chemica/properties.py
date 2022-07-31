import mendeleev

def metallicity(series_name: str) -> int:
    # Return:
    # 1 if metal
    # 0 if metalloid
    # -1 if non-metal
    if series_name.lower() == "metalloid":
        return 0
    elif "metal" in series_name.lower():
        return 1
    else:
        return -1


# ionic_radii: list[mendeleev.models.IonicRadius]
def charge_set(ionic_radii: list) -> set:
    return set([ionic_radius.charge for ionic_radius in ionic_radii])