import tkinter as tk
from tkinter import ttk, messagebox
import math
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import threading
import time
from PIL import Image, ImageTk

from enum import Enum

# Define RiskLevel enum
class RiskLevel(Enum):
    IMPROBABLE = "Improbable (faible)"
    POSSIBLE = "Possible (moyen)"
    PROBABLE = "Probable (élevé)"
    TRES_PROBABLE = "Très probable (extrême))"

    def __str__(self):
        return self.value

# Constantes physiques
G = 9.81
COLLISION_TIME = 0.05
LENGTH_SWING = 2.25
LBS_TO_KG = 0.453592  # Conversion factor from lbs to kg

# Données anthropométriques
ANTHROPOMETRIC_DATA = {
    1: {"circumference_mm": 200, "neck_height_mm": 45, "vertebrae_strength_mpa": (4, 8), "head_mass_kg": 3.0},
    2: {"circumference_mm": 210, "neck_height_mm": 50, "vertebrae_strength_mpa": (4.5, 8.5), "head_mass_kg": 3.2},
    3: {"circumference_mm": 225, "neck_height_mm": 60, "vertebrae_strength_mpa": (5, 9), "head_mass_kg": 3.5},
    4: {"circumference_mm": 235, "neck_height_mm": 65, "vertebrae_strength_mpa": (5, 9.5), "head_mass_kg": 3.7},
    5: {"circumference_mm": 245, "neck_height_mm": 70, "vertebrae_strength_mpa": (5, 10), "head_mass_kg": 4.0}
}

DECAPITATION_THRESHOLD = (5, 10)
CERVICAL_FRACTURE_THRESHOLD = (3, 6)
CONCUSSION_ACCELERATION_THRESHOLD = 80  # g (approx. 784 m/s²)

# Variables globales
animation_running = False
animation_thread = None
target_angle = 0
max_angle = 0
toggle_button = None
force = 0
velocity1_global = 0
velocity2_global = 0

def calculate_max_angle(height, length=LENGTH_SWING):
    if height > length:
        raise ValueError("La hauteur d’oscillation ne peut pas dépasser la longueur de la balançoire.")
    cos_theta = 1 - height / length
    return math.degrees(math.acos(cos_theta))

def calculate_velocity(angle_degrees, max_height, initial_velocity=0):
    velocity_from_height = math.sqrt(2 * G * max_height)
    return math.sqrt(velocity_from_height**2 + initial_velocity**2)

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

def calculate_pressure(force, surface_cm2):
    surface_mm2 = surface_cm2 * 100
    return force / surface_mm2

def assess_decapitation_risk(pressure_mpa, age):
    vertebrae_strength = ANTHROPOMETRIC_DATA[age]["vertebrae_strength_mpa"]
    threshold_min, threshold_max = DECAPITATION_THRESHOLD
    if pressure_mpa < threshold_min:
        return RiskLevel.IMPROBABLE
    elif threshold_min <= pressure_mpa <= threshold_max:
        if pressure_mpa < vertebrae_strength[0]:
            return RiskLevel.IMPROBABLE
        elif pressure_mpa <= vertebrae_strength[1]:
            return RiskLevel.POSSIBLE
        else:
            return RiskLevel.PROBABLE
    else:
        return RiskLevel.TRES_PROBABLE

def assess_cervical_fracture_risk(pressure_mpa, age):
    vertebrae_strength = ANTHROPOMETRIC_DATA[age]["vertebrae_strength_mpa"]
    threshold_min, threshold_max = CERVICAL_FRACTURE_THRESHOLD
    if pressure_mpa < threshold_min:
        return RiskLevel.IMPROBABLE
    elif threshold_min <= pressure_mpa <= threshold_max:
        if pressure_mpa < vertebrae_strength[0]:
            return RiskLevel.IMPROBABLE
        elif pressure_mpa <= vertebrae_strength[1]:
            return RiskLevel.POSSIBLE
        else:
            return RiskLevel.PROBABLE
    else:
        return RiskLevel.TRES_PROBABLE

def assess_concussion_risk(acceleration_ms2, age):
    acceleration_g = acceleration_ms2 / 9.81
    if acceleration_g < CONCUSSION_ACCELERATION_THRESHOLD * 0.8:
        return RiskLevel.IMPROBABLE
    elif acceleration_g < CONCUSSION_ACCELERATION_THRESHOLD:
        return RiskLevel.POSSIBLE
    else:
        return RiskLevel.PROBABLE

def run_simulation():
    try:
        age = int(age_var.get())
        angle_horizontal = float(angle_entry.get())
        mass1_lbs = float(mass1_entry.get())
        mass2_lbs = float(mass2_entry.get())
        v_init1 = float(v_init1_entry.get())
        v_init2 = float(v_init2_entry.get())
        # Convert angle from horizontal to vertical
        angle = 90 - angle_horizontal
        if angle < 0:
            messagebox.showerror("Erreur", "L’angle par rapport à l’horizontal doit être entre 0 et 90 degrés.")
            return
        max_height = float(height_entry.get())
        impact_type = impact_var.get()
        if max_height <= 0:
            messagebox.showerror("Erreur", "La hauteur d’oscillation doit être supérieure à 0.")
            return
        if max_height > LENGTH_SWING:
            messagebox.showerror("Erreur", f"La hauteur d’oscillation ne peut pas dépasser la longueur de la balançoire ({LENGTH_SWING} m).")
            return
        if mass1_lbs <= 0 or mass2_lbs <= 0:
            messagebox.showerror("Erreur", "La masse des balançoires doit être supérieure à 0.")
            return
        if v_init1 < 0 or v_init2 < 0:
            messagebox.showerror("Erreur", "Les vitesses initiales ne peuvent pas être négatives.")
            return
        max_angle = calculate_max_angle(max_height)
        if not 0 <= angle <= max_angle:
            messagebox.showerror("Erreur", f"L’angle (par rapport à la verticale) doit être entre 0 et {max_angle:.1f}°, soit entre {90-max_angle:.1f} et 90° par rapport à l’horizontal.")
            return
        # Convert masses to kg
        mass1_kg = mass1_lbs * LBS_TO_KG
        mass2_kg = mass2_lbs * LBS_TO_KG
        # Calculate velocities for both swings
        global velocity1_global, velocity2_global
        velocity1 = calculate_velocity(angle, max_height, v_init1)
        velocity2 = calculate_velocity(angle, max_height, v_init2)
        velocity1_global = velocity1
        velocity2_global = velocity2
        # Calculate relative velocity for collision
        relative_velocity = abs(velocity1 + velocity2)  # Head-on collision
        # Use reduced mass for force calculation
        reduced_mass = (mass1_kg * mass2_kg) / (mass1_kg + mass2_kg) if (mass1_kg + mass2_kg) != 0 else mass1_kg
        global force
        force = calculate_force(relative_velocity, reduced_mass)
        surface_cm2 = calculate_impact_surface(age, impact_type)
        pressure_mpa = calculate_pressure(force, surface_cm2)
        head_mass = ANTHROPOMETRIC_DATA[age]["head_mass_kg"]
        acceleration_ms2 = calculate_acceleration(force, head_mass)
        decapitation_risk = assess_decapitation_risk(pressure_mpa, age)
        cervical_fracture_risk = assess_cervical_fracture_risk(pressure_mpa, age)
        concussion_risk = assess_concussion_risk(acceleration_ms2, age)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Âge de l’enfant : {age} ans\n")
        result_text.insert(tk.END, f"Hauteur d’oscillation max : {max_height:.2f} m\n")
        result_text.insert(tk.END, f"Masse balançoire 1 : {mass1_lbs:.1f} lbs ({mass1_kg:.1f} kg)\n")
        result_text.insert(tk.END, f"Masse balançoire 2 : {mass2_lbs:.1f} lbs ({mass2_kg:.1f} kg)\n")
        result_text.insert(tk.END, f"Vitesse initiale balançoire 1 : {v_init1:.2f} m/s\n")
        result_text.insert(tk.END, f"Vitesse initiale balançoire 2 : {v_init2:.2f} m/s\n")
        result_text.insert(tk.END, f"Angle max (calculé, par rapport à la verticale) : {max_angle:.1f}°\n")
        result_text.insert(tk.END, f"Angle d’impact (par rapport à l’horizontal) : {angle_horizontal:.1f}°\n")
        result_text.insert(tk.END, f"Type d’impact : {impact_type}\n")
        result_text.insert(tk.END, f"Vitesse d’impact balançoire 1 : {velocity1:.2f} m/s\n")
        result_text.insert(tk.END, f"Vitesse d’impact balançoire 2 : {velocity2:.2f} m/s\n")
        result_text.insert(tk.END, f"Vitesse relative d’impact : {relative_velocity:.2f} m/s\n")
        result_text.insert(tk.END, f"Force d’impact : {force:.2f} N\n")
        result_text.insert(tk.END, f"Surface d’impact : {surface_cm2:.2f} cm²\n")
        result_text.insert(tk.END, f"Pression exercée : {pressure_mpa:.2f} MPa\n")
        result_text.insert(tk.END, f"Probabilité de décapitation partielle : {decapitation_risk}\n")
        result_text.insert(tk.END, f"Probabilité de fracture cervicale : {cervical_fracture_risk}\n")
        result_text.insert(tk.END, f"Probabilité de commotion cérébrale : {concussion_risk}\n")
    except ValueError:
        messagebox.showerror("Erreur", "Veuillez entrer des valeurs valides.")

def load_texture(image_path):
    try:
        image = pygame.image.load(image_path)
        print(f"Image loaded: {image_path}, size: {image.get_size()}")
        image = image.convert_alpha()
        image_data = pygame.image.tostring(image, "RGBA", 1)
        width, height = image.get_size()
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
        print(f"Texture ID: {texture_id}")
        return texture_id
    except Exception as e:
        print(f"Erreur lors du chargement de la texture : {e}")
        return None

def draw_swing(x_pivot, y_pivot, angle_rad, length, color, platform_width):
    glDisable(GL_DEPTH_TEST)
    glColor3f(*color)
    glLineWidth(5.0)
    x_end = x_pivot + length * math.sin(angle_rad)
    y_end = y_pivot - length * math.cos(angle_rad)
    glBegin(GL_LINES)
    glVertex2f(x_pivot, y_pivot)
    glVertex2f(x_end, y_end)
    glEnd()
    platform_x1 = x_end - platform_width * math.cos(angle_rad)
    platform_y1 = y_end - platform_width * math.sin(angle_rad)
    platform_x2 = x_end + platform_width * math.cos(angle_rad)
    platform_y2 = y_end + platform_width * math.sin(angle_rad)
    glBegin(GL_LINES)
    glVertex2f(platform_x1, platform_y1)
    glVertex2f(platform_x2, platform_y2)
    glEnd()
    glEnable(GL_DEPTH_TEST)

def draw_pivot(x, y):
    glDisable(GL_DEPTH_TEST)
    glColor3f(0, 0, 0)
    glPointSize(10)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()
    glEnable(GL_DEPTH_TEST)

def draw_grid():
    glPushAttrib(GL_ENABLE_BIT | GL_COLOR_BUFFER_BIT)
    glPushMatrix()
    glDisable(GL_DEPTH_TEST)
    glColor3f(0.5, 0.5, 0.5)
    glLineWidth(1.0)
    glBegin(GL_LINES)
    for x in range(-5, 6, 1):
        glVertex2f(x, -2)
        glVertex2f(x, 5)
    for y in range(-2, 6, 1):
        glVertex2f(-5, y)
        glVertex2f(5, y)
    glEnd()
    try:
        font = pygame.font.SysFont("Arial", 12)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        for x in range(-5, 6, 1):
            if x != 0:
                text = font.render(str(x), True, (255, 255, 255))
                text_surface = pygame.image.tostring(text, "RGBA", True)
                glColor4f(0, 0, 0, 0.8)
                glBegin(GL_QUADS)
                glVertex2f(x - 0.15, -1.95)
                glVertex2f(x + 0.15, -1.95)
                glVertex2f(x + 0.15, -1.75)
                glVertex2f(x - 0.15, -1.75)
                glEnd()
                glRasterPos2f(x - 0.1, -1.9)
                glDrawPixels(text.get_width(), text.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_surface)
        for y in range(-2, 6, 1):
            if y != 0:
                text = font.render(str(y), True, (255, 255, 255))
                text_surface = pygame.image.tostring(text, "RGBA", True)
                glColor4f(0, 0, 0, 0.8)
                glBegin(GL_QUADS)
                glVertex2f(-4.95, y - 0.1)
                glVertex2f(-4.65, y - 0.1)
                glVertex2f(-4.65, y + 0.1)
                glVertex2f(-4.95, y + 0.1)
                glEnd()
                glRasterPos2f(-4.9, y - 0.05)
                glDrawPixels(text.get_width(), text.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_surface)
        glDisable(GL_BLEND)
    except Exception as e:
        print(f"Error rendering grid labels: {e}")
        glDisable(GL_BLEND)
    glPopMatrix()
    glPopAttrib()

def render_fps(fps):
    glDisable(GL_DEPTH_TEST)
    try:
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        font = pygame.font.SysFont("Arial", 24)
        text = font.render(f"FPS: {fps:.1f}", True, (255, 255, 255))
        text_surface = pygame.image.tostring(text, "RGBA", True)
        text_width = text.get_width()
        text_height = text.get_height()
        pixel_to_gl_x = 10.0 / 800
        pixel_to_gl_y = 7.0 / 600
        gl_text_width = text_width * pixel_to_gl_x
        gl_text_height = text_height * pixel_to_gl_y
        x_pos = -4.0
        y_pos = 4.0
        padding_x = 0.1
        padding_y = 0.05
        glColor4f(0, 0, 0, 0.8)
        glBegin(GL_QUADS)
        glVertex2f(x_pos - padding_x, y_pos + padding_y)
        glVertex2f(x_pos + gl_text_width + padding_x, y_pos + padding_y)
        glVertex2f(x_pos + gl_text_width + padding_x, y_pos - gl_text_height - padding_y)
        glVertex2f(x_pos - padding_x, y_pos - gl_text_height - padding_y)
        glEnd()
        glRasterPos2f(x_pos, y_pos - gl_text_height)
        glDrawPixels(text_width, text_height, GL_RGBA, GL_UNSIGNED_BYTE, text_surface)
        glDisable(GL_BLEND)
    except Exception as e:
        print(f"Error rendering FPS: {e}")
    glEnable(GL_DEPTH_TEST)

def animate_swings_thread(surface, animation_label):
    global animation_running, target_angle, max_angle, is_running
    pygame.init()
    window_width, window_height = 800, 600
    pygame.display.set_mode((window_width, window_height), DOUBLEBUF | OPENGL | HIDDEN)
    gluOrtho2D(-5, 5, -2, 5)
    glClearColor(0.0, 1.0, 0.0, 1.0)  # Green fallback for debugging
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    # Load background texture once
    background_texture = load_texture("background.jpg")
    if background_texture is None:
        print("Failed to load background texture; rendering with fallback color.")
    clock = pygame.time.Clock()
    omega = math.sqrt(G / LENGTH_SWING)
    pivot1_x, pivot1_y = -2, LENGTH_SWING
    pivot2_x, pivot2_y = 2, LENGTH_SWING
    platform_width = 0.6
    frame_count = 0
    last_time = time.time()
    fps_count = 0
    fps = 0.0
    while animation_running:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # Ensure clean OpenGL state
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glPushMatrix()  # Save current matrix
        # Render background texture first
        if background_texture:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, background_texture)
            glDisable(GL_DEPTH_TEST)
            # Apply horizontal flip transformation
            glTranslatef(0, 0, 0)  # Center at origin (optional, for clarity)
            glTranslatef(0, 0, 0)  # Reset translation
            glBegin(GL_QUADS)
            # Texture coordinates to prevent flipping
            glTexCoord2f(0, 0); glVertex2f(-5, -2)  # Bottom-left
            glTexCoord2f(1, 0); glVertex2f(5, -2)   # Bottom-right
            glTexCoord2f(1, 1); glVertex2f(5, 5)    # Top-right
            glTexCoord2f(0, 1); glVertex2f(-5, 5)   # Top-left
            glEnd()
            glDisable(GL_TEXTURE_2D)
            glEnable(GL_DEPTH_TEST)
        glPopMatrix()  # Restore matrix
        # Draw other elements
        draw_grid()
        current_time = time.time()
        fps_count += 1
        elapsed_time = current_time - last_time
        if elapsed_time >= 1.0:
            fps = fps_count / elapsed_time
            fps_count = 0
            last_time = current_time
        if is_running.get():
            t = frame_count / 60.0
            angle1 = max_angle * math.cos(omega * t)
            angle2 = -angle1
            frame_count += 1
            angle1_rad = math.radians(angle1)
            angle2_rad = math.radians(angle2)
            x1 = pivot1_x + LENGTH_SWING * math.sin(angle1_rad)
            if abs(angle1) >= target_angle and abs(x1 - pivot1_x) < 0.1:
                animation_running = False
                root.after(0, lambda: toggle_button.config(text="Start", state="normal"))
        else:
            angle1 = 0
            angle2 = 0
            angle1_rad = 0
            angle2_rad = 0
        draw_swing(pivot1_x, pivot1_y, angle1_rad, LENGTH_SWING, (0, 0, 1), platform_width)
        draw_swing(pivot2_x, pivot2_y, angle2_rad, LENGTH_SWING, (1, 0, 0), platform_width)
        draw_pivot(pivot1_x, pivot1_y)
        draw_pivot(pivot2_x, pivot2_y)
        render_fps(fps)
        glPopAttrib()  # Restore OpenGL state
        # Capture OpenGL buffer
        glFinish()
        data = glReadPixels(0, 0, window_width, window_height, GL_RGB, GL_UNSIGNED_BYTE)
        print("Frame rendered")  # Debug print
        image = Image.frombytes("RGB", (window_width, window_height), data)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        photo = ImageTk.PhotoImage(image)
        root.after(0, lambda: animation_label.configure(image=photo))
        root.after(0, lambda: setattr(animation_label, 'image', photo))
        clock.tick(60)
    # Clean up texture
    if background_texture:
        glDeleteTextures([background_texture])
        print("Texture deleted")
    pygame.quit()
    
def toggle_animation():
    global animation_running, target_angle, max_angle, is_running
    if is_running.get():
        is_running.set(False)
        toggle_button.configure(text="Start")
    else:
        try:
            angle_horizontal = float(angle_entry.get())
            target_angle = 90 - angle_horizontal
            if target_angle < 0:
                messagebox.showerror("Erreur", "L’angle par rapport à l’horizontal doit être entre 0 et 90 degrés.")
                return
            max_height = float(height_entry.get())
            mass1_lbs = float(mass1_entry.get())
            mass2_lbs = float(mass2_entry.get())
            v_init1 = float(v_init1_entry.get())
            v_init2 = float(v_init2_entry.get())
            if max_height <= 0:
                messagebox.showerror("Erreur", "La hauteur doit être > 0.")
                return
            if max_height > LENGTH_SWING:
                messagebox.showerror("Erreur", f"La hauteur d’oscillation ne peut pas dépasser la longueur de la balançoire ({LENGTH_SWING} m).")
                return
            if mass1_lbs <= 0 or mass2_lbs <= 0:
                messagebox.showerror("Erreur", "La masse des balançoires doit être supérieure à 0.")
                return
            if v_init1 < 0 or v_init2 < 0:
                messagebox.showerror("Erreur", "Les vitesses initiales ne peuvent pas être négatives.")
                return
            global max_angle
            max_angle = calculate_max_angle(max_height)
            if not 0 <= target_angle <= max_angle:
                messagebox.showerror("Erreur", f"L’angle (par rapport à la verticale) doit être entre 0 et {max_angle:.1f}°, soit entre {90-max_angle:.1f} et 90° par rapport à l’horizontal.")
                return
            animation_running = True
            is_running.set(True)
            toggle_button.configure(text="Stop")
            threading.Thread(target=animate_swings_thread, args=(animation_surface, animation_label), daemon=True).start()
        except ValueError:
            messagebox.showerror("Erreur", "Valeurs invalides pour les paramètres.")

# Interface graphique
root = tk.Tk()
is_running = tk.BooleanVar(value=False)
root.title("Simulation de collision de balançoires")
root.geometry("1200x800")

style = ttk.Style()
style.configure("TFrame", background="#f0f0f0")
style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
style.configure("Title.TLabel", font=("Arial", 12, "bold"))
style.configure("TButton", font=("Arial", 10))
style.configure("TCombobox", font=("Arial", 10))
style.configure("TRadiobutton", background="#f0f0f0", font=("Arial", 10))

main_frame = ttk.Frame(root)
main_frame.pack(fill="both", expand=True, padx=20, pady=10)

left_frame = ttk.Frame(main_frame, relief="ridge", borderwidth=2)
left_frame.pack(side="left", fill="y", padx=(0, 10), pady=5)

input_frame = ttk.Frame(left_frame)
input_frame.pack(fill="x", padx=5, pady=5)

title_label = ttk.Label(input_frame, text="Paramètres de simulation", style="Title.TLabel")
title_label.pack(pady=(0, 10))

age_label = ttk.Label(input_frame, text="Âge de l’enfant (ans) :")
age_label.pack(anchor="w", padx=5)
age_var = tk.StringVar(value="1")
age_menu = ttk.Combobox(input_frame, textvariable=age_var, values=[1, 2, 3, 4, 5], state="readonly", width=10)
age_menu.pack(anchor="w", padx=5, pady=2)

height_label = ttk.Label(input_frame, text="Hauteur d’oscillation max (m) :")
height_label.pack(anchor="w", padx=5)
height_entry = ttk.Entry(input_frame, width=10)
height_entry.pack(anchor="w", padx=5, pady=2)
height_entry.insert(0, "1")

mass1_label = ttk.Label(input_frame, text="Masse balançoire 1 (lbs) :")
mass1_label.pack(anchor="w", padx=5)
mass1_entry = ttk.Entry(input_frame, width=10)
mass1_entry.pack(anchor="w", padx=5, pady=2)
mass1_entry.insert(0, "100")

mass2_label = ttk.Label(input_frame, text="Masse balançoire 2 (lbs) :")
mass2_label.pack(anchor="w", padx=5)
mass2_entry = ttk.Entry(input_frame, width=10)
mass2_entry.pack(anchor="w", padx=5, pady=2)
mass2_entry.insert(0, "100")

v_init1_label = ttk.Label(input_frame, text="Vitesse initiale balançoire 1 (m/s) :")
v_init1_label.pack(anchor="w", padx=5)
v_init1_entry = ttk.Entry(input_frame, width=10)
v_init1_entry.pack(anchor="w", padx=5, pady=2)
v_init1_entry.insert(0, "0")

v_init2_label = ttk.Label(input_frame, text="Vitesse initiale balançoire 2 (m/s) :")
v_init2_label.pack(anchor="w", padx=5)
v_init2_entry = ttk.Entry(input_frame, width=10)
v_init2_entry.pack(anchor="w", padx=5, pady=2)
v_init2_entry.insert(0, "0")

angle_label = ttk.Label(input_frame, text="Angle d’impact (degrés, par rapport à l’horizontal) :")
angle_label.pack(anchor="w", padx=5)
angle_entry = ttk.Entry(input_frame, width=10)
angle_entry.pack(anchor="w", padx=5, pady=2)
angle_entry.insert(0, "45")

impact_label = ttk.Label(input_frame, text="Type d’impact :")
impact_label.pack(anchor="w", padx=5)
impact_var = tk.StringVar(value="frontal")
impact_radio1 = ttk.Radiobutton(input_frame, text="Frontal", variable=impact_var, value="frontal")
impact_radio1.pack(anchor="w", padx=5)
impact_radio2 = ttk.Radiobutton(input_frame, text="Concentré (bord étroit)", variable=impact_var, value="concentré")
impact_radio2.pack(anchor="w", padx=5)

simulate_button = ttk.Button(input_frame, text="Lancer la simulation", command=run_simulation)
simulate_button.pack(pady=10)

result_frame = ttk.Frame(left_frame)
result_frame.pack(fill="x", padx=5, pady=5)
result_title = ttk.Label(result_frame, text="Résultats de la simulation", style="Title.TLabel")
result_title.pack()
result_text = tk.Text(result_frame, height=20, width=55, font=("Arial", 10))
result_text.pack(pady=5)

animation_frame = ttk.Frame(main_frame, relief="ridge", borderwidth=2)
animation_frame.pack(side="right", fill="both", expand=True)

animation_title = ttk.Label(animation_frame, text="Animation des balançoires", style="Title.TLabel")
animation_title.pack(pady=(0, 5))

control_frame = ttk.Frame(animation_frame)
control_frame.pack(fill="x", pady=5)
toggle_button = ttk.Button(control_frame, text="Start", command=toggle_animation)
toggle_button.pack(side="left", padx=5)

animation_surface = pygame.Surface((800, 600))
animation_surface.fill((200, 200, 200))
animation_label = ttk.Label(animation_frame)
animation_label.pack(pady=5)
initial_image = Image.frombytes("RGB", (800, 600), pygame.image.tostring(animation_surface, "RGB"))
initial_photo = ImageTk.PhotoImage(initial_image)
animation_label.configure(image=initial_photo)
animation_label.image = initial_photo

pygame.init()
root.mainloop()