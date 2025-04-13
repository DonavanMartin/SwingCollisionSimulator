import tkinter as tk
from tkinter import ttk, messagebox
import math
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import threading
import time

# Constantes physiques
G = 9.81  # Accélération gravitationnelle (m/s²)
MASS_SWING = 45  # Masse de chaque balançoire (kg, incluant l'enfant)
COLLISION_TIME = 0.05  # Temps de collision (s)
LENGTH_SWING = 2.25  # Longueur de la balançoire (m, du pivot au siège)

# Données anthropométriques et résistance des tissus par âge
ANTHROPOMETRIC_DATA = {
    1: {"circumference_mm": 200, "neck_height_mm": 45, "vertebrae_strength_mpa": (4, 8)},
    2: {"circumference_mm": 210, "neck_height_mm": 50, "vertebrae_strength_mpa": (4.5, 8.5)},
    3: {"circumference_mm": 225, "neck_height_mm": 60, "vertebrae_strength_mpa": (5, 9)},
    4: {"circumference_mm": 235, "neck_height_mm": 65, "vertebrae_strength_mpa": (5, 9.5)},
    5: {"circumference_mm": 245, "neck_height_mm": 70, "vertebrae_strength_mpa": (5, 10)}
}

# Seuil pour une décapitation partielle (MPa)
DECAPITATION_THRESHOLD = (5, 10)

# Variables globales pour l’animation
animation_running = False
animation_thread = None
pygame_window = None
target_angle = 0
max_angle = 0

def calculate_max_angle(height, length=LENGTH_SWING):
    if height > length:
        raise ValueError("La hauteur d’oscillation ne peut pas dépasser la longueur de la v.")
    cos_theta = 1 - height / length
    return math.degrees(math.acos(cos_theta))

def calculate_velocity(angle_degrees, max_height):
    return math.sqrt(2 * G * max_height)

def calculate_force(velocity, mass=MASS_SWING, collision_time=COLLISION_TIME):
    return (mass * velocity) / collision_time

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
        return "Improbable"
    elif threshold_min <= pressure_mpa <= threshold_max:
        if pressure_mpa < vertebrae_strength[0]:
            return "Improbable"
        elif pressure_mpa <= vertebrae_strength[1]:
            return "Possible"
        else:
            return "Probable"
    else:
        return "Très probable"

def run_simulation():
    try:
        age = int(age_var.get())
        angle = float(angle_entry.get())
        max_height = float(height_entry.get())
        impact_type = impact_var.get()
        if max_height <= 0:
            messagebox.showerror("Erreur", "La hauteur d’oscillation doit être supérieure à 0.")
            return
        if max_height > LENGTH_SWING:
            messagebox.showerror("Erreur", f"La hauteur d’oscillation ne peut pas dépasser la longueur de la balançoire ({LENGTH_SWING} m).")
            return
        max_angle = calculate_max_angle(max_height)
        if not 0 <= angle <= max_angle:
            messagebox.showerror("Erreur", f"L’angle doit être entre 0 et {max_angle:.1f} degrés.")
            return
        velocity = calculate_velocity(angle, max_height)
        global force
        force = calculate_force(velocity)
        surface_cm2 = calculate_impact_surface(age, impact_type)
        pressure_mpa = calculate_pressure(force, surface_cm2)
        risk = assess_decapitation_risk(pressure_mpa, age)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Âge de l’enfant : {age} ans\n")
        result_text.insert(tk.END, f"Hauteur d’oscillation max : {max_height:.2f} m\n")
        result_text.insert(tk.END, f"Angle max (calculé) : {max_angle:.1f}°\n")
        result_text.insert(tk.END, f"Angle d’impact : {angle}°\n")
        result_text.insert(tk.END, f"Type d’impact : {impact_type}\n")
        result_text.insert(tk.END, f"Vitesse de la balançoire : {velocity:.2f} m/s\n")
        result_text.insert(tk.END, f"Force d’impact : {force:.2f} N\n")
        result_text.insert(tk.END, f"Surface d’impact : {surface_cm2:.2f} cm²\n")
        result_text.insert(tk.END, f"Pression exercée : {pressure_mpa:.2f} MPa\n")
        result_text.insert(tk.END, f"Probabilité de décapitation partielle : {risk}\n")
    except ValueError:
        messagebox.showerror("Erreur", "Veuillez entrer des valeurs valides.")

def load_texture(image_path):
    try:
        image = pygame.image.load(image_path)
        image_data = pygame.image.tostring(image, "RGBA", 1)
        width, height = image.get_size()
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
        return texture_id
    except Exception as e:
        print(f"Erreur lors du chargement de la texture : {e}")
        return None

def draw_swing(x_pivot, y_pivot, angle_rad, length, color, platform_width):
    glColor3f(*color)
    glLineWidth(3.0)
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

def draw_pivot(x, y):
    glColor3f(0, 0, 0)
    glPointSize(5)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()

def draw_grid():
    glColor3f(0.5, 0.5, 0.5)  # Gray color for grid lines
    glLineWidth(1.0)  # Thin lines for the grid
    glBegin(GL_LINES)
    # Vertical lines
    for x in range(-5, 6, 1):  # From x=-5 to x=5, step=1
        glVertex2f(x, -2)
        glVertex2f(x, 5)
    # Horizontal lines
    for y in range(-2, 6, 1):  # From y=-2 to y=5, step=1
        glVertex2f(-5, y)
        glVertex2f(5, y)
    glEnd()

    # Enable blending for text rendering
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Add labels for grid lines
    try:
        font = pygame.font.SysFont("Arial", 12)  # Small font for labels
        # Labels for vertical lines (X-axis)
        for x in range(-5, 6, 1):
            if x != 0:  # Skip label at x=0 to avoid overlap
                text = font.render(str(x), True, (255, 255, 255))  # White text
                text_surface = pygame.image.tostring(text, "RGBA", True)
                # Draw background rectangle
                glColor4f(0, 0, 0, 0.8)  # Black, semi-transparent
                glBegin(GL_QUADS)
                glVertex2f(x - 0.15, -1.95)
                glVertex2f(x + 0.15, -1.95)
                glVertex2f(x + 0.15, -1.75)
                glVertex2f(x - 0.15, -1.75)
                glEnd()
                # Draw text
                glRasterPos2f(x - 0.1, -1.9)  # Position just below X-axis
                glDrawPixels(text.get_width(), text.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_surface)
        # Labels for horizontal lines (Y-axis)
        for y in range(-2, 6, 1):
            if y != 0:  # Skip label at y=0 to avoid overlap
                text = font.render(str(y), True, (255, 255, 255))  # White text
                text_surface = pygame.image.tostring(text, "RGBA", True)
                # Draw background rectangle
                glColor4f(0, 0, 0, 0.80)  # Black, semi-transparent
                glBegin(GL_QUADS)
                glVertex2f(-4.95, y - 0.1)
                glVertex2f(-4.65, y - 0.1)
                glVertex2f(-4.65, y + 0.1)
                glVertex2f(-4.95, y + 0.1)
                glEnd()
                # Draw text
                glRasterPos2f(-4.9, y - 0.05)  # Position just left of Y-axis
                glDrawPixels(text.get_width(), text.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_surface)
    except Exception as e:
        print(f"Error rendering grid labels: {e}")

    # Disable blending to avoid affecting other rendering
    glDisable(GL_BLEND)
def render_fps(fps):
    try:
        # Enable blending for text rendering
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        font = pygame.font.SysFont("Arial", 24)  # Font for FPS
        text = font.render(f"FPS: {fps:.1f}", True, (255, 255, 255))  # White text
        text_surface = pygame.image.tostring(text, "RGBA", True)

        # Calculate text size in OpenGL coordinates
        text_width = text.get_width()
        text_height = text.get_height()
        # Assuming viewport is 800x600 pixels mapped to (-5,5,-2,5)
        pixel_to_gl_x = 10.0 / 800  # 10 units (-5 to 5) over 800 pixels
        pixel_to_gl_y = 7.0 / 600   # 7 units (-2 to 5) over 600 pixels
        gl_text_width = text_width * pixel_to_gl_x
        gl_text_height = text_height * pixel_to_gl_y

        # Position settings
        x_pos = -4.0  # Base position (top-left corner of rectangle without padding)
        y_pos = 4.0
        padding_x = 0.1  # Padding around text in GL units
        padding_y = 0.05

        # Draw background rectangle
        glColor4f(0, 0, 0, 0.8)  # Black, semi-transparent
        glBegin(GL_QUADS)
        glVertex2f(x_pos - padding_x, y_pos + padding_y)  # Top-left
        glVertex2f(x_pos + gl_text_width + padding_x, y_pos + padding_y)  # Top-right
        glVertex2f(x_pos + gl_text_width + padding_x, y_pos - gl_text_height - padding_y)  # Bottom-right
        glVertex2f(x_pos - padding_x, y_pos - gl_text_height - padding_y)  # Bottom-left
        glEnd()

        # Draw text, centered in the rectangle
        text_x = x_pos  # Shift right by half padding
        text_y = y_pos - gl_text_height  # Shift down to center vertically
        glRasterPos2f(text_x, text_y)
        glDrawPixels(text_width, text_height, GL_RGBA, GL_UNSIGNED_BYTE, text_surface)

        # Disable blending to avoid affecting other rendering
        glDisable(GL_BLEND)
    except Exception as e:
        print(f"Error rendering FPS: {e}")
        
def animate_swings_thread():
    global animation_running, pygame_window
    pygame.init()
    window_width, window_height = 800, 600
    pygame_window = pygame.display.set_mode((window_width, window_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Animation de la collision des balançoires")
    gluOrtho2D(-5, 5, -2, 5)
    glClearColor(0.8, 0.8, 1.0, 1.0)
    background_texture = load_texture("background.jpg")
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
        for event in pygame.event.get():
            if event.type == QUIT:
                animation_running = False
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        if background_texture:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, background_texture)
            glColor3f(1, 1, 1)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(-5, -2)
            glTexCoord2f(1, 0); glVertex2f(5, -2)
            glTexCoord2f(1, 1); glVertex2f(5, 5)
            glTexCoord2f(0, 1); glVertex2f(-5, 5)
            glEnd()
            glDisable(GL_TEXTURE_2D)
        draw_grid()  # Draw the grid after the background
        current_time = time.time()
        fps_count += 1
        elapsed_time = current_time - last_time
        if elapsed_time >= 1.0:
            fps = fps_count / elapsed_time
            fps_count = 0
            last_time = current_time
        if is_running.get():
            t = frame_count / 100
            angle1 = -max_angle * math.cos(omega * t)
            angle2 = -angle1
            frame_count += 1
            angle1_rad = math.radians(angle1)
            angle2_rad = math.radians(angle2)  # Compute angle2_rad
            x1 = pivot1_x + LENGTH_SWING * math.sin(angle1_rad)
            if x1 > pivot1_x and abs(angle1) >= target_angle:
                animation_running = False
                root.after(0, lambda: toggle_button.config(text="Start"))
                root.after(0, lambda: messagebox.showinfo("Collision", f"Collision à {target_angle}° !"))
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
        pygame.display.flip()
        clock.tick(60)
    if background_texture:
        glDeleteTextures([background_texture])
    pygame.quit()
    pygame_window = None
    
def animate_swings():
    global animation_running, animation_thread, target_angle, max_angle
    try:
        target_angle = float(angle_entry.get())
        max_height = float(height_entry.get())
        if max_height <= 0:
            messagebox.showerror("Erreur", "La hauteur doit être > 0.")
            return
        if max_height > LENGTH_SWING:
            messagebox.showerror("Erreur", f"La hauteur d’oscillation ne peut pas dépasser la longueur de la balançoire ({LENGTH_SWING} m).")
            return
        max_angle = calculate_max_angle(max_height)
        if not 0 <= target_angle <= max_angle:
            messagebox.showerror("Erreur", f"L’angle doit être entre 0 et {max_angle:.1f}°.")
            return
        anim_window = tk.Toplevel(root)
        anim_window.title("Contrôle de l’animation")
        button_frame = tk.Frame(anim_window)
        button_frame.pack(fill=tk.X, pady=5)
        def toggle_animation():
            global animation_running
            if is_running.get():
                is_running.set(False)
                toggle_button.config(text="Start")
            else:
                is_running.set(True)
                toggle_button.config(text="Stop")
        toggle_button = tk.Button(button_frame, text="Start", command=toggle_animation)
        toggle_button.pack()
        animation_running = True
        animation_thread = threading.Thread(target=animate_swings_thread, daemon=True)
        animation_thread.start()
    except ValueError:
        messagebox.showerror("Erreur", "Valeurs invalides pour l’angle ou la hauteur.")

# Interface graphique
root = tk.Tk()
is_running = tk.BooleanVar(value=False)
root.title("Simulation de collision de balançoires")
root.geometry("400x650")
title_label = tk.Label(root, text="Simulation de collision de balançoires", font=("Arial", 14, "bold"))
title_label.pack(pady=10)
age_label = tk.Label(root, text="Âge de l’enfant (ans) :")
age_label.pack()
age_var = tk.StringVar(value="1")
age_menu = ttk.Combobox(root, textvariable=age_var, values=[1, 2, 3, 4, 5], state="readonly")
age_menu.pack()
height_label = tk.Label(root, text="Hauteur d’oscillation max (m) :")
height_label.pack()
height_entry = tk.Entry(root)
height_entry.pack()
height_entry.insert(0, "0.5")
angle_label = tk.Label(root, text="Angle d’impact (degrés) :")
angle_label.pack()
angle_entry = tk.Entry(root)
angle_entry.pack()
angle_entry.insert(0, "30")
impact_label = tk.Label(root, text="Type d’impact :")
impact_label.pack()
impact_var = tk.StringVar(value="frontal")
impact_radio1 = tk.Radiobutton(root, text="Frontal", variable=impact_var, value="frontal")
impact_radio1.pack()
impact_radio2 = tk.Radiobutton(root, text="Concentré (bord étroit)", variable=impact_var, value="concentré")
impact_radio2.pack()
simulate_button = tk.Button(root, text="Lancer la simulation", command=run_simulation)
simulate_button.pack(pady=10)
animate_button = tk.Button(root, text="Lancer l’animation", command=animate_swings)
animate_button.pack(pady=5)
result_text = tk.Text(root, height=12, width=40)
result_text.pack(pady=10)
root.mainloop()