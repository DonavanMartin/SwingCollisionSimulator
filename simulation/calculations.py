# simulation/calculations.py
import math
from .constants import (
    G, COLLISION_TIME, LENGTH_SWING, LBS_TO_KG, ANTHROPOMETRIC_DATA
)
from .risk_assessment import (
    assess_decapitation_risk, assess_cervical_fracture_risk, assess_concussion_risk
)
from .models import RiskLevel

# Variables globales (à refactoriser si possible)
force = 0
velocity1_global = 0
velocity2_global = 0


def calculate_max_angle(height, length=LENGTH_SWING):
    if height > length:
        raise ValueError("La hauteur d’oscillation ne peut pas dépasser la longueur de la balançoire.")
    cos_theta = 1 - height / length
    return math.degrees(math.acos(cos_theta))


def calculate_velocity(theta_rad, length=LENGTH_SWING, initial_velocity=0):
    """Calcule la vitesse tangentielle à une position angulaire."""
    h = length * (1 - math.cos(theta_rad))
    velocity_from_height = math.sqrt(2 * G * h)
    return velocity_from_height + initial_velocity


def calculate_force(velocity, mass, collision_time=COLLISION_TIME):
    return (mass * velocity) / collision_time


def calculate_acceleration(level, head_mass_kg):
    return force / head_mass_kg


def calculate_neck_diameter(circumference_mm):
    return circumference_mm / math.pi


def calculate_impact_surface(age, impact_type):
    data = ANTHROPOMETRIC_DATA[age]
    neck_diameter_mm = calculate_neck_diameter(data["circumference_mm"])
    neck_height_mm = data["neck_height_mm"]
    impact_height_mm = neck_height_mm * (2 / 3)
    if impact_type == "frontal":
        surface_mm2 = neck_diameter_mm * impact_height_mm
    else:
        surface_mm2 = 20 * impact_height_mm
    return surface_mm2 / 100


def calculate_pressure(level, surface_cm2):
    surface_mm2 = surface_cm2 * 100
    return force / surface_mm2


def check_platform_collision(theta1, theta2, platform_width, pivot1_x=0, pivot1_y=LENGTH_SWING,
                             pivot2_x=0, pivot2_y=LENGTH_SWING, length=LENGTH_SWING, scale_factor=1.0):
    """Vérifie si les plateformes des balançoires se chevauchent."""
    x1 = pivot1_x + (length * scale_factor) * math.sin(theta1)
    y1 = pivot1_y - (length * scale_factor) * math.cos(theta1)
    x2 = pivot2_x + (length * scale_factor) * math.sin(theta2)
    y2 = pivot2_y - (length * scale_factor) * math.cos(theta2)
    platform1_x1 = x1 - platform_width * math.cos(theta1)
    platform1_y1 = y1 - platform_width * math.sin(theta1)
    platform1_x2 = x1 + platform_width * math.cos(theta1)
    platform1_y2 = y1 + platform_width * math.sin(theta1)
    platform2_x1 = x2 - platform_width * math.cos(theta2)
    platform2_y1 = y2 - platform_width * math.sin(theta2)
    platform2_x2 = x2 + platform_width * math.cos(theta2)
    platform2_y2 = y2 + platform_width * math.sin(theta2)
    def ccw(Ax, Ay, Bx, By, Cx, Cy):
        return (Cy - Ay) * (Bx - Ax) > (By - Ay) * (Cx - Ax)
    
    def intersect(x1, y1, x2, y2, x3, y3, x4, y4):
        return ccw(x1, y1, x3, y3, x4, y4) != ccw(x2, y2, x3, y3, x4, y4) and \
               ccw(x1, y1, x2, y2, x3, y3) != ccw(x1, y1, x2, y2, x4, y4)
    
    if intersect(platform1_x1, platform1_y1, platform1_x2, platform1_y2,
                 platform2_x1, platform2_y1, platform2_x2, platform2_y2):
        return True
    min_distance = min(
        math.sqrt((platform1_x1 - platform2_x1)**2 + (platform1_y1 - platform2_y1)**2),
        math.sqrt((platform1_x1 - platform2_x2)**2 + (platform1_y1 - platform2_y2)**2),
        math.sqrt((platform1_x2 - platform2_x1)**2 + (platform1_y2 - platform2_y1)**2),
        math.sqrt((platform1_x2 - platform2_x2)**2 + (platform1_y2 - platform2_y2)**2)
    )
    return min_distance < 0.01 * scale_factor


def calculate_pendulum_motion(max_angle_rad, v_init1, v_init2, mass1_kg, mass2_kg, target_angle_rad, platform_width,
                              pivot1_x=-2.0, pivot1_y=LENGTH_SWING, pivot2_x=2.0, pivot2_y=LENGTH_SWING,
                              scale_factor=1.0, dt=1.0/60.0):
    """Simule le mouvement pendulaire jusqu'à la collision des plateformes."""
    damping_coeff = 0.02
    theta1 = max_angle_rad
    theta2 = -max_angle_rad
    theta1_dot = v_init1 / LENGTH_SWING if v_init1 else 0
    theta2_dot = v_init2 / LENGTH_SWING if v_init2 else 0
    t = 0
    while True:
        accel1 = -(G / LENGTH_SWING) * math.sin(theta1) - (damping_coeff / mass1_kg) * theta1_dot
        accel2 = -(G / LENGTH_SWING) * math.sin(theta2) - (damping_coeff / mass2_kg) * theta2_dot
        theta1_dot += accel1 * dt
        theta2_dot += accel2 * dt
        theta1 += theta1_dot * dt
        theta2 += theta2_dot * dt
        t += dt
        if abs(theta1) >= target_angle_rad and check_platform_collision(
            theta1, theta2, platform_width, pivot1_x, pivot1_y, pivot2_x, pivot2_y, LENGTH_SWING, scale_factor
        ):
            return theta1, theta2, theta1_dot, theta2_dot
        if t > 10:
            return theta1, theta2, theta1_dot, theta2_dot
    return theta1, theta2, theta1_dot, theta2_dot


def calculate_collision(theta1_dot, theta2_dot, mass1_kg, mass2_kg, e=0.5):
    """Calcule les vitesses post-collision."""
    v1 = theta1_dot * LENGTH_SWING
    v2 = theta2_dot * LENGTH_SWING
    v1_prime = (mass1_kg * v1 + mass2_kg * v2 - mass2_kg * e * (v2 - v1)) / (mass1_kg + mass2_kg)
    v2_prime = (mass1_kg * v1 + mass2_kg * v2 + mass1_kg * e * (v2 - v1)) / (mass1_kg + mass2_kg)
    return v1_prime / LENGTH_SWING, v2_prime / LENGTH_SWING


def run_simulation(age, angle_horizontal, mass1_lbs, mass2_lbs, v_init1, v_init2, max_height, impact_type):
    """Effectue les calculs de la simulation avec une physique newtonienne."""
    global force, velocity1_global, velocity2_global
    try:
        angle = 90 - angle_horizontal
        if angle < 0:
            raise ValueError("L’angle par rapport à l’horizontal doit être entre 0 et 90 degrés.")
        if max_height <= 0:
            raise ValueError("La hauteur d’oscillation doit être supérieure à 0.")
        if max_height > LENGTH_SWING:
            raise ValueError(f"La hauteur d’oscillation ne peut pas dépasser la longueur de la balançoire ({LENGTH_SWING} m).")
        if mass1_lbs <= 0 or mass2_lbs <= 0:
            raise ValueError("La masse des balançoires doit être supérieure à 0.")
        if v_init1 < 0 or v_init2 < 0:
            raise ValueError("Les vitesses initiales ne peuvent pas être négatives.")
        max_angle = calculate_max_angle(max_height)
        if not 0 <= angle <= max_angle:
            raise ValueError(f"L’angle (par rapport à la verticale) doit être entre 0 et {max_angle:.1f}°.")
        
        mass1_kg = mass1_lbs * LBS_TO_KG
        mass2_kg = mass2_lbs * LBS_TO_KG
        max_angle_rad = math.radians(max_angle)
        target_angle_rad = math.radians(angle)
        platform_width = 0.6 * (ANTHROPOMETRIC_DATA[age]["neck_height_mm"] / 50.0)
        pivot1_x = -2.0
        pivot2_x = 2.0
        pivot1_y = pivot2_y = LENGTH_SWING
        scale_factor = 1.0
        
        theta1, theta2, theta1_dot, theta2_dot = calculate_pendulum_motion(
            max_angle_rad, v_init1, v_init2, mass1_kg, mass2_kg, target_angle_rad, platform_width,
            pivot1_x, pivot1_y, pivot2_x, pivot2_y, scale_factor
        )
        
        velocity1 = theta1_dot * LENGTH_SWING
        velocity2 = theta2_dot * LENGTH_SWING
        velocity1_global = velocity1
        velocity2_global = velocity2
        
        theta1_dot_prime, theta2_dot_prime = calculate_collision(theta1_dot, theta2_dot, mass1_kg, mass2_kg)
        relative_velocity = abs(theta1_dot_prime * LENGTH_SWING + theta2_dot_prime * LENGTH_SWING)
        
        reduced_mass = (mass1_kg * mass2_kg) / (mass1_kg + mass2_kg) if (mass1_kg + mass2_kg) != 0 else mass1_kg
        force = calculate_force(relative_velocity, reduced_mass)
        
        surface_cm2 = calculate_impact_surface(age, impact_type)
        pressure_mpa = calculate_pressure(force, surface_cm2)
        head_mass = ANTHROPOMETRIC_DATA[age]["head_mass_kg"]
        acceleration_ms2 = calculate_acceleration(force, head_mass)
        decapitation_risk = assess_decapitation_risk(pressure_mpa, age)
        cervical_fracture_risk = assess_cervical_fracture_risk(pressure_mpa, age)
        concussion_risk = assess_concussion_risk(acceleration_ms2, age)
        
        return {
            "age": age,
            "max_height": max_height,
            "mass1_lbs": mass1_lbs,
            "mass2_lbs": mass2_lbs,
            "mass1_kg": mass1_kg,
            "mass2_kg": mass2_kg,
            "v_init1": v_init1,
            "v_init2": v_init2,
            "max_angle": max_angle,
            "angle_horizontal": angle_horizontal,
            "impact_type": impact_type,
            "velocity1": velocity1,
            "velocity2": velocity2,
            "relative_velocity": relative_velocity,
            "force": force,
            "surface_cm2": surface_cm2,
            "pressure_mpa": pressure_mpa,
            "decapitation_risk": decapitation_risk,
            "cervical_fracture_risk": cervical_fracture_risk,
            "concussion_risk": concussion_risk
        }
    except ValueError as e:
        raise e