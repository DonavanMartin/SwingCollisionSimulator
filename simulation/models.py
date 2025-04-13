# simulation/models.py
from enum import Enum


class RiskLevel(Enum):
    IMPROBABLE = 1
    POSSIBLE = 2
    PROBABLE = 3
    TRES_PROBABLE = 4

    @property
    def display_name(self):
        return {
            1: "Improbable (faible)",
            2: "Possible (moyen)",
            3: "Probable (élevé)",
            4: "Très probable (extrême)"
        }[self.value]

    def __str__(self):
        return self.display_name