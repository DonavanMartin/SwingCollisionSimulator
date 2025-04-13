# simulation/models.py
from enum import Enum


class RiskLevel(Enum):
    """
    Enumération des niveaux de risque pour l'évaluation des dangers dans la simulation.
    Chaque niveau associe une valeur numérique à une description en français.
    """
    IMPROBABLE = (1, "Improbable (faible)")
    POSSIBLE = (2, "Possible (moyen)")
    PROBABLE = (3, "Probable (élevé)")
    TRES_PROBABLE = (4, "Très probable (extrême)")

    def __init__(self, value, display_name):
        self._value_ = value
        self._display_name = display_name

    @property
    def display_name(self):
        """Retourne la description lisible du niveau de risque."""
        return self._display_name

    def __str__(self):
        """Retourne la description pour l'affichage."""
        return self.display_name