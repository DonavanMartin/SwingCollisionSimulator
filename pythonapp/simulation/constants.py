# simulation/constants.py
# Constantes physiques
G = 9.81
COLLISION_TIME = 0.05
LENGTH_SWING = 2.25
LBS_TO_KG = 0.453592
FLASH_TIME = 1
REEL_PLATFORM_WIDTH = 1
PLATFORM_WIDTH = REEL_PLATFORM_WIDTH /2

# Données anthropométriques
ANTHROPOMETRIC_DATA = {
    1: {"circumference_mm": 200, "neck_height_mm": 45, "vertebrae_strength_mpa": (4, 8), "head_mass_kg": 3.0},
    2: {"circumference_mm": 210, "neck_height_mm": 50, "vertebrae_strength_mpa": (4.5, 8.5), "head_mass_kg": 3.2},
    3: {"circumference_mm": 225, "neck_height_mm": 60, "vertebrae_strength_mpa": (5, 9), "head_mass_kg": 3.5},
    4: {"circumference_mm": 235, "neck_height_mm": 65, "vertebrae_strength_mpa": (5, 9.5), "head_mass_kg": 3.7},
    5: {"circumference_mm": 245, "neck_height_mm": 70, "vertebrae_strength_mpa": (5, 10), "head_mass_kg": 4.0}
}

# Seuils de risque
DECAPITATION_THRESHOLD = (5, 10)
CERVICAL_FRACTURE_THRESHOLD = (3, 6)
CONCUSSION_ACCELERATION_THRESHOLD = 80  # g (approx. 784 m/s²)