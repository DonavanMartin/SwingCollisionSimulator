    # simulation/calculations.py
    import math
    from .constants import (
        G, COLLISION_TIME, LENGTH_SWING, LBS_TO_KG, ANTHROPOMETRIC_DATA, PLATFORM_WIDTH
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


    def calculate_acceleration(force, head_mass_kg):
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


    def calculate_pressure(force_newton, surface_cm2):
        """
        Calcule la pression exercée en mégapascals (MPa).

        Args:
            force_newton (float): Force en Newtons (N).
            surface_cm2 (float): Surface d'impact en centimètres carrés (cm²).

        Returns:
            float: Pression en mégapascals (MPa).

        Raises:
            ValueError: Si la surface est inférieure ou égale à zéro.
        """
        if surface_cm2 <= 0:
            raise ValueError("La surface d'impact doit être supérieure à zéro.")
        surface_mm2 = surface_cm2 * 100  # Convertir cm² en mm²
        return force_newton / surface_mm2  # Pression en N/mm² = MPa


    def check_platform_collision(theta1, theta2, # The `platform_width` variable in the
    # `check_platform_collision` function is used to
    # determine the width of the platforms attached to the
    # swings. It is a parameter that represents the width of
    # the platforms in the simulation. The function uses this
    # width to check if the platforms of the swings overlap
    # or collide during the swinging motion. By calculating
    # the positions of the platforms based on the swing
    # angles and dimensions, the function determines if there
    # is a collision between the platforms.
    pivot1_x=0, pivot1_y=LENGTH_SWING,
                                pivot2_x=0, pivot2_y=LENGTH_SWING, length=LENGTH_SWING):
        """Vérifie si les plateformes des balançoires se chevauchent."""
        x1 = pivot1_x + (length ) * math.sin(theta1)
        y1 = pivot1_y - (length ) * math.cos(theta1)
        x2 = pivot2_x + (length ) * math.sin(theta2)
        y2 = pivot2_y - (length ) * math.cos(theta2)
        platform1_x1 = x1 - PLATFORM_WIDTH * math.cos(theta1)
        platform1_y1 = y1 - PLATFORM_WIDTH * math.sin(theta1)
        platform1_x2 = x1 + PLATFORM_WIDTH * math.cos(theta1)
        platform1_y2 = y1 + PLATFORM_WIDTH * math.sin(theta1)
        platform2_x1 = x2 - PLATFORM_WIDTH * math.cos(theta2)
        platform2_y1 = y2 - PLATFORM_WIDTH * math.sin(theta2)
        platform2_x2 = x2 + PLATFORM_WIDTH * math.cos(theta2)
        platform2_y2 = y2 + PLATFORM_WIDTH * math.sin(theta2)
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
        return min_distance < 0.01 


    def calculate_pendulum_motion(max_angle_rad, v_init1, v_init2, mass1_kg, mass2_kg,
                                pivot1_x=-2.0, pivot1_y=LENGTH_SWING, pivot2_x=2.0, pivot2_y=LENGTH_SWING,
                                dt=1.0/60.0):
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
            if check_platform_collision(
                theta1, theta2, pivot1_x, pivot1_y, pivot2_x, pivot2_y, LENGTH_SWING
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