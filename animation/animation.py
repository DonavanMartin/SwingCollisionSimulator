# rendering/animation.py
import math
import threading
import time
from PIL import Image, ImageTk
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from simulation.constants import FLASH_TIME, G, LENGTH_SWING, LBS_TO_KG, ANTHROPOMETRIC_DATA
from simulation.calculations import calculate_max_angle, check_platform_collision
from .opengl_utils import load_texture, draw_swing, draw_pivot, draw_grid, render_fps, render_text


def animate_swings_thread(surface, animation_label, root, toggle_button, is_running, max_angle, target_angle,
                         age, mass1_lbs, mass2_lbs, v_init1, v_init2, angle_horizontal, max_height, impact_type):
    pygame.init()  # Ensure Pygame is initialized
    window_width, window_height = 800, 600
    pygame.display.set_mode((window_width, window_height), DOUBLEBUF | OPENGL | HIDDEN)
    scale_factor = 1.0
    
    # Set clear color to green as fallback
    glClearColor(0.0, 1.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    
    # Load background texture
    background_texture = load_texture("background.jpg")
    if background_texture is None:
        print("Failed to load background texture; rendering with fallback color.")
    
    clock = pygame.time.Clock()
    pivot1_x = -2.0 * scale_factor
    pivot2_x = 2.0 * scale_factor
    pivot1_y = pivot2_y = LENGTH_SWING * scale_factor
    platform_width = 0.6 * (ANTHROPOMETRIC_DATA[age]["neck_height_mm"] / 50.0) * scale_factor
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
    theta2_dot = v_init2 / LENGTH_SWING if v_init2 else 0
    collision_occurred = False
    flash_time = 0
    t = 0
    dt = 1.0 / 60.0
    
    while is_running.get():
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Set up projection and modelview matrices each frame
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(-5 * scale_factor, 5 * scale_factor, -2 * scale_factor, 5 * scale_factor)
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
            glTexCoord2f(0, 0); glVertex2f(-5 * scale_factor, -2 * scale_factor)
            glTexCoord2f(1, 0); glVertex2f(5 * scale_factor, -2 * scale_factor)
            glTexCoord2f(1, 1); glVertex2f(5 * scale_factor, 5 * scale_factor)
            glTexCoord2f(0, 1); glVertex2f(-5 * scale_factor, 5 * scale_factor)
            glEnd()
            glDisable(GL_TEXTURE_2D)
            glEnable(GL_DEPTH_TEST)
        else:
            # Fallback quad to prevent black background
            glBegin(GL_QUADS)
            glColor3f(0.0, 0.5, 0.0)  # Dark green
            glVertex2f(-5 * scale_factor, -2 * scale_factor)
            glVertex2f(5 * scale_factor, -2 * scale_factor)
            glVertex2f(5 * scale_factor, 5 * scale_factor)
            glVertex2f(-5 * scale_factor, 5 * scale_factor)
            glEnd()
        
        glPopMatrix()
        
        # Draw other elements
        draw_grid()
        
        # FPS calculation
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
                theta1, theta2, platform_width / scale_factor, pivot1_x, pivot1_y, pivot2_x, pivot2_y,
                LENGTH_SWING, scale_factor
            ) and not collision_occurred:
                v1 = theta1_dot * LENGTH_SWING
                v2 = theta2_dot * LENGTH_SWING
                v1_prime = (mass1_kg * v1 + mass2_kg * v2 - mass2_kg * e * (v2 - v1)) / (mass1_kg + mass2_kg)
                v2_prime = (mass1_kg * v1 + mass2_kg * v2 + mass1_kg * e * (v2 - v1)) / (mass1_kg + mass2_kg)
                theta1_dot = v1_prime / LENGTH_SWING
                theta2_dot = v2_prime / LENGTH_SWING
                collision_occurred = True
                flash_time = current_time
            
            if collision_occurred and current_time - flash_time < 0.2:
                color1 = (1, 0, 0) if impact_type == "frontal" else (1, 0.5, 0)
                color2 = (1, 0, 0) if impact_type == "frontal" else (1, 0.5, 0)
            else:
                color1 = (0, 0, 1)
                color2 = (1, 0, 0)
                if collision_occurred:
                    is_running.set(False)
                    root.after(0, lambda: toggle_button.config(text="Start", state="normal"))
        else:
            theta1 = 0
            theta2 = 0
            theta1_dot = 0
            theta2_dot = 0
            color1 = (0, 0, 1)
            color2 = (1, 0, 0)
        
        draw_swing(pivot1_x, pivot1_y, theta1, LENGTH_SWING * scale_factor, color1, platform_width)
        draw_swing(pivot2_x, pivot2_y, theta2, LENGTH_SWING * scale_factor, color2, platform_width)
        draw_pivot(pivot1_x, pivot1_y)
        draw_pivot(pivot2_x, pivot2_y)
        angle1_deg = math.degrees(theta1)
        angle2_deg = math.degrees(theta2)
        render_text(f"Angle 1: {angle1_deg:.1f}°", pivot1_x - 0.5, pivot1_y + 0.3)
        render_text(f"Angle 2: {angle2_deg:.1f}°", pivot2_x - 0.5, pivot2_y + 0.3)
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