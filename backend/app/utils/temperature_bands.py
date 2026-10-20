from dataclasses import dataclass


@dataclass(frozen=True)
class TempBand:
    min_f: int | None
    max_f: int | None
    # category -> allowed subcategories (subset of CLOTHING_CATEGORIES[category])
    allow: dict[str, frozenset[str]]
    label: str  # for Outfit.reason


BANDS = (
    TempBand(
        None,
        39,
        {
            "top": frozenset(
                {"long_sleeve", "polo"}
            ),  # or whatever you prefer under a mid
            "bottom": frozenset({"jeans", "trousers", "leggings"}),
            "mid_layer": frozenset({"hoodie", "sweater", "fleece"}),
            "outer_layer": frozenset({"coat", "parka", "jacket"}),
            "shoes": frozenset({"boots", "sneakers"}),
        },
        "Cold — layers and covered legs",
    ),
    TempBand(
        40,
        54,
        {
            "top": frozenset({"long_sleeve", "polo"}),
            "bottom": frozenset({"jeans", "trousers", "leggings"}),
            "mid_layer": frozenset({"hoodie", "sweater", "cardigan", "fleece"}),
            "outer_layer": frozenset({"jacket", "coat"}),
            "shoes": frozenset({"boots", "sneakers"}),
        },
        "Chilly — mid layer recommended",
    ),
    TempBand(
        55,
        64,
        {
            "top": frozenset({"long_sleeve", "polo", "blouse"}),
            "bottom": frozenset({"jeans", "trousers", "leggings"}),
            "mid_layer": frozenset({"cardigan", "hoodie", "sweater"}),
            "shoes": frozenset({"sneakers", "dress_shoes"}),
        },
        "Mild — light mid layer",
    ),
    TempBand(
        65,
        74,
        {
            "top": frozenset({"t_shirt", "polo", "blouse"}),
            "bottom": frozenset({"jeans", "trousers", "shorts"}),
            "shoes": frozenset({"sneakers", "dress_shoes"}),
        },
        "Comfortable — light layers",
    ),
    TempBand(
        75,
        84,
        {
            "top": frozenset({"t_shirt", "tank_top", "polo"}),
            "bottom": frozenset({"shorts", "skirt"}),
            "shoes": frozenset({"sneakers", "sandals"}),
        },
        "Warm — short sleeves",
    ),
    TempBand(
        85,
        None,
        {
            "top": frozenset({"t_shirt", "tank_top"}),
            "bottom": frozenset({"shorts", "skirt"}),
            "shoes": frozenset({"sandals", "sneakers"}),
        },
        "Hot — minimal clothing",
    ),
)


def determine_temperature_band(temp_f: int) -> TempBand:
    for band in BANDS:
        lo = band.min_f if band.min_f is not None else float("-inf")
        hi = band.max_f if band.max_f is not None else float("inf")
        if lo <= temp_f <= hi:
            return band
    return BANDS[-1]
