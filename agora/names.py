import random

_NAMES = [
    "Orion",
    "Lyra",
    "Atlas",
    "Nova",
    "Cleo",
    "Zephyr",
    "Helios",
    "Iris",
    "Delphi",
    "Eos",
    "Hermes",
    "Selene",
    "Apollo",
    "Artemis",
    "Phaedra",
    "Castor",
    "Pollux",
    "Theron",
    "Nyx",
    "Aether",
    "Calyx",
    "Dione",
    "Eurus",
    "Fable",
    "Gale",
    "Haven",
    "Indra",
    "Juno",
    "Kairos",
    "Lumen",
    "Mira",
    "Nemo",
    "Oberon",
    "Pyxis",
    "Quirk",
    "Rune",
    "Sirius",
    "Telos",
    "Umbra",
    "Vega",
    "Wren",
    "Xero",
    "Yara",
    "Zara",
]


def generate_unique_name(taken: set[str]) -> str:
    """Pick a random fun name that is not in *taken*."""
    base = random.choice(_NAMES)

    if base not in taken:
        return base

    counter = 2
    while True:
        candidate = f"{base}-{counter}"
        if candidate not in taken:
            return candidate
        counter += 1
