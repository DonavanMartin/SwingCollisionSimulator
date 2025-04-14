# rendering/animation.py
import math
import threading
import time
from PIL import Image, ImageTk
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from simulation.constants import G, LENGTH_SWING, LBS_TO_KG, ANTHROPOMETRIC_DATA, PLATFORM_WIDTH
from simulation.calculations import (
    calculate_max_angle, check_platform_collision, calculate_force,
    calculate_impact_surface, calculate_pressure, calculate_acceleration,
    calculate_collision
)
from simulation.risk_assessment import (
    assess_decapitation_risk, assess_cervical_fracture_risk, assess_concussion_risk
)
from .opengl_utils import load_texture, draw_swing, draw_pivot, draw_grid, render_fps, render_text


def animate_swings_thread(surface, animation_label, root, toggle_button, is_running, update_results,
                         max_angle, target_angle, age, mass1_lbs, mass2_lbs, v_init1, v_init2,
                         angle_horizontal, max_height, impact_type):
    pygame.init()  # Ensure Pygame is initialized
    window_width, window_height = 800, 600
    pygame.display.set_mode((window_width, window_height), DOUBLEBUF | OPENGL | HIDDEN)
    gluOrtho2D(-5 , 5 , -2 , 5 )
    glClearColor(0.0, 1.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    background_texture = load_texture("animation/background.jpg")
    if background_texture is None:
        print("Failed to load background texture; rendering with fallback color.")
    clock = pygame.time.Clock()
    pivot1_x = -2.0 
    pivot2_x = 2.0 
    pivot1_y = pivot2_y = LENGTH_SWING
    frame_count = 0
    last_time = time.time()
    fps_count = 0
    fps = 0.0
    mass1_kg = mass1_lbs * LBS_TO_KG
    mass2_kg = mass2_lbs * LBS_TO_KG
    damping_coeff = 0.02
    e = 0.5
    max_angle_rad = math.radians(max_angle)
    target_angle_rad = math.radians(target_angle)
    theta1 = -max_angle_rad
    theta2 = max_angle_rad
    theta1_dot = v_init1 / LENGTH_SWING if v_init1 else 0
    theta2_dot = -v_init2 / LENGTH_SWING if v_init2 else 0
    collision_occurred = False
    flash_time = 0
    t = 0
    dt = 1.0 / 60.0
    
    final_v1 = 0
    final_v2 = 0
    
    while is_running.get():
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Set up projection and modelview matrices each frame
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(-5 , 5 , -2 , 5 )
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Save OpenGL state
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glPushMatrix()
        
        # Render background
        if background_texture:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, background_texture)
            glDisable(GL_DEPTH_TEST)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(-5 , -2 )
            glTexCoord2f(1, 0); glVertex2f(5 , -2 )
            glTexCoord2f(1, 1); glVertex2f(5 , 5 )
            glTexCoord2f(0, 1); glVertex2f(-5 , 5 )
            glEnd()
            glDisable(GL_TEXTURE_2D)
            glEnable(GL_DEPTH_TEST)
        else:
            # Fallback quad to prevent black background
            glBegin(GL_QUADS)
            glColor3f(0.0, 0.5, 0.0)  # Dark green
            glVertex2f(-5 , -2 )
            glVertex2f(5 , -2 )
            glVertex2f(5 , 5 )
            glVertex2f(-5 , 5 )
            glEnd()
        
        glPopMatrix()
        draw_grid()
        current_time = time.time()
        fps_count += 1
        elapsed_time = current_time - last_time
        if elapsed_time >= 1.0:
            fps = fps_count / elapsed_time
            fps_count = 0
            last_time = current_time
        if is_running.get():
            accel1 = -(G / LENGTH_SWING) * math.sin(theta1) - (damping_coeff / mass1_kg) * theta1_dot
            accel2 = -(G / LENGTH_SWING) * math.sin(theta2) - (damping_coeff / mass2_kg) * theta2_dot
            theta1_dot += accel1 * dt
            theta2_dot += accel2 * dt
            theta1 += theta1_dot * dt
            theta2 += theta2_dot * dt
            t += dt
            frame_count += 1
            
            if abs(theta1) >= target_angle_rad and check_platform_collision(
                theta1, theta2, pivot1_x, pivot1_y, pivot2_x, pivot2_y,
                LENGTH_SWING
            ) and not collision_occurred:
                v1 = theta1_dot * LENGTH_SWING
                v2 = theta2_dot * LENGTH_SWING
                final_v1 = v1
                final_v2 = v2
                v1_prime, v2_prime = calculate_collision(theta1_dot, theta2_dot, mass1_kg, mass2_kg, e)
                theta1_dot = v1_prime / LENGTH_SWING
                theta2_dot = v2_prime / LENGTH_SWING
                collision_occurred = True
                flash_time = current_time
                # Calculer le rapport
                velocity1 = v1
                velocity2 = v2
                relative_velocity = abs(velocity1) + abs(velocity2)
                reduced_mass = (mass1_kg * mass2_kg) / (mass1_kg + mass2_kg) if (mass1_kg + mass2_kg) != 0 else mass1_kg
                force = calculate_force(relative_velocity, reduced_mass)
                surface_cm2 = calculate_impact_surface(age, impact_type)
                pressure_mpa = calculate_pressure(force, surface_cm2)
                head_mass = ANTHROPOMETRIC_DATA[age]["head_mass_kg"]
                acceleration_ms2 = calculate_acceleration(force, head_mass)
                decapitation_risk = assess_decapitation_risk(pressure_mpa, age)
                cervical_fracture_risk = assess_cervical_fracture_risk(pressure_mpa, age)
                concussion_risk = assess_concussion_risk(acceleration_ms2, age)
                results = {
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
                    "decapitation_risk": decapitation_risk.display_name,
                    "cervical_fracture_risk": cervical_fracture_risk.display_name,
                    "concussion_risk": concussion_risk.display_name
                }
                root.after(0, lambda: update_results(results))
            if collision_occurred and current_time - flash_time < 0.1:
                color1 = (1, 0, 0) if impact_type == "frontal" else (1, 0.5, 0)
                color2 = (1, 0, 0) if impact_type == "frontal" else (1, 0.5, 0)
            else:
                color1 = (0, 0, 1)
                color2 = (1, 0, 0)
                if collision_occurred:
                    is_running.set(False)
                    root.after(0, lambda: toggle_button.config(text="Démarrer", state="normal"))
        else:
            theta1 = 0
            theta2 = 0
            theta1_dot = 0
            theta2_dot = 0
            color1 = (0, 0, 1)
            color2 = (1, 0, 0)
        
        draw_swing(pivot1_x, pivot1_y, theta1, LENGTH_SWING , color1)
        draw_swing(pivot2_x, pivot2_y, theta2, LENGTH_SWING , color2)
        draw_pivot(pivot1_x, pivot1_y)
        draw_pivot(pivot2_x, pivot2_y)
        
        # Render angle labels
        angle1_deg = math.degrees(theta1)
        angle2_deg = math.degrees(theta2)
        render_text(f"Angle 1: {angle1_deg:.1f}°", pivot1_x - 0.5, pivot1_y + 0.5)
        render_text(f"Angle 2: {angle2_deg:.1f}°", pivot2_x - 0.5, pivot2_y + 0.5)
        
        # Calculate and render speed labels
        
        if collision_occurred:
            speed1_ms = abs(theta1_dot * LENGTH_SWING)  # Speed in m/s for Swing 1
            speed2_ms = abs(theta2_dot * LENGTH_SWING)  # Speed in m/s for Swing 2
            render_text(f"Vitesse 1: {final_v1:.2f} m/s", pivot1_x - 0.5, pivot1_y+0.8)  # Below angle label
            render_text(f"Vitesse 2: {final_v2:.2f} m/s", pivot2_x - 0.5, pivot2_y+0.8)  # Below angle label
        else:
            speed1_ms = abs(theta1_dot * LENGTH_SWING)  # Speed in m/s for Swing 1
            speed2_ms = abs(theta2_dot * LENGTH_SWING)  # Speed in m/s for Swing 2
            render_text(f"Vitesse 1: {speed1_ms:.2f} m/s", pivot1_x - 0.5, pivot1_y+0.8)  # Below angle label
            render_text(f"Vitesse 2: {speed2_ms:.2f} m/s", pivot2_x - 0.5, pivot2_y+0.8)  # Below angle label
            
        
        render_fps(fps)
        
        glPopAttrib()
        
        # Capture buffer
        glFinish()
        data = glReadPixels(0, 0, window_width, window_height, GL_RGB, GL_UNSIGNED_BYTE)
        if not data:
            print("glReadPixels returned empty data")
            continue
        image = Image.frombytes("RGB", (window_width, window_height), data)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        photo = ImageTk.PhotoImage(image)
        root.after(0, lambda: animation_label.configure(image=photo))
        root.after(0, lambda: setattr(animation_label, 'image', photo))
        
        clock.tick(60)
    
    # Cleanup
    if background_texture:
        try:
            glDeleteTextures([background_texture])
            print("Texture deleted")
        except Exception as e:
            print(f"Error deleting texture: {e}")
    pygame.quit()  # Proper cleanup