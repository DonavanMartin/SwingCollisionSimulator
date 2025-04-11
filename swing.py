import tkinter as tk
from tkinter import ttk, messagebox
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.image as mpimg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
ani = None
fig = None
canvas = None

def calculate_max_angle(height, length=LENGTH_SWING):
    """Calcule l’angle maximum à partir de la hauteur d’oscillation."""
    if height > length:
        raise ValueError("La hauteur d’oscillation ne peut pas dépasser la longueur de la balançoire.")
    cos_theta = 1 - height / length
    return math.degrees(math.acos(cos_theta))

def calculate_velocity(angle_degrees, max_height):
    """Calcule la vitesse de la balançoire à un angle donné."""
    angle_rad = math.radians(angle_degrees)
    # La hauteur effective à l’angle donné est h = max_height * (1 - cos(angle)) / (1 - cos(max_angle))
    velocity = math.sqrt(2 * G * max_height)
    return velocity

def calculate_force(velocity, mass=MASS_SWING, collision_time=COLLISION_TIME):
    """Calcule la force d’impact."""
    return (mass * velocity) / collision_time

def calculate_neck_diameter(circumference_mm):
    """Calcule le diamètre du cou à partir de la circonférence."""
    return circumference_mm / math.pi

def calculate_impact_surface(age, impact_type):
    """Calcule la surface d’impact sur le cou."""
    data = ANTHROPOMETRIC_DATA[age]
    neck_diameter_mm = calculate_neck_diameter(data["circumference_mm"])
    neck_height_mm = data["neck_height_mm"]
    impact_height_mm = neck_height_mm * (2 / 3)  # 2/3 de la hauteur du cou

    if impact_type == "frontal":
        surface_mm2 = neck_diameter_mm * impact_height_mm
    else:
        surface_mm2 = 20 * impact_height_mm

    return surface_mm2 / 100  # Convertir en cm²

def calculate_pressure(force, surface_cm2):
    """Calcule la pression exercée (MPa)."""
    surface_mm2 = surface_cm2 * 100  # Convertir cm² en mm²
    pressure_mpa = force / surface_mm2  # N/mm² = MPa
    return pressure_mpa

def assess_decapitation_risk(pressure_mpa, age):
    """Évalue la probabilité de décapitation partielle."""
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
    """Lance la simulation et affiche les résultats."""
    try:
        age = int(age_var.get())
        angle = float(angle_entry.get())
        max_height = float(height_entry.get())
        impact_type = impact_var.get()

        # Valider les entrées
        if max_height <= 0:
            messagebox.showerror("Erreur", "La hauteur d’oscillation doit être supérieure à 0.")
            return
        if max_height > LENGTH_SWING:
            messagebox.showerror("Erreur", f"La hauteur d’oscillation ne peut pas dépasser la longueur de la balançoire ({LENGTH_SWING} m).")
            return
        max_angle = calculate_max_angle(max_height)
        if not 0 <= angle <= max_angle:
            messagebox.showerror("Erreur", f"L’angle doit être entre 0 et {max_angle:.1f} degrés (défini par la hauteur).")
            return

        velocity = calculate_velocity(angle, max_height)
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
        messagebox.showerror("Erreur", "Veuillez entrer des valeurs valides pour l’angle et la hauteur (nombres).")

def animate_swings():
    """Crée une animation des balançoires jusqu’à l’angle d’impact."""
    global ani, fig, canvas

    try:
        target_angle = float(angle_entry.get())
        max_height = float(height_entry.get())
        if max_height <= 0:
            messagebox.showerror("Erreur", "La hauteur d’oscillation doit être supérieure à 0.")
            return
        if max_height > LENGTH_SWING:
            messagebox.showerror("Erreur", f"La hauteur d’oscillation ne peut pas dépasser la longueur de la balançoire ({LENGTH_SWING} m).")
            return
        max_angle = calculate_max_angle(max_height)
        if not 0 <= target_angle <= max_angle:
            messagebox.showerror("Erreur", f"L’angle doit être entre 0 et {max_angle:.1f} degrés (défini par la hauteur).")
            return

        # Créer une nouvelle fenêtre pour l’animation
        anim_window = tk.Toplevel(root)
        anim_window.title("Animation de la collision des balançoires")

        # Créer la figure et le canevas
        FIGHEIGHT = 7
        fig = plt.Figure(figsize=(FIGHEIGHT*1.33333, FIGHEIGHT))
        ax = fig.add_subplot(111)
        canvas = FigureCanvasTkAgg(fig, master=anim_window)
        canvas.get_tk_widget().pack()

        # Définir les limites des axes
        x_limits = (-5, 5)
        y_limits = (-2, 5)
        ax.set_xlim(x_limits)
        ax.set_ylim(y_limits)
        ax.set_xlabel("Position horizontale (m)")
        ax.set_ylabel("Position verticale (m)")
        ax.set_title("Collision des balançoires")
        ax.grid(True)
        ax.set_aspect('equal')

        # Charger et afficher l’image en arrière-plan
        try:
            img = mpimg.imread('background.jpg')
            ax.imshow(img, extent=[x_limits[0], x_limits[1], y_limits[0], y_limits[1]], aspect='auto', zorder=0)
        except FileNotFoundError:
            messagebox.showwarning("Avertissement", "Image 'background.jpg' non trouvée.")

        # Points de suspension des balançoires
        pivot1_x, pivot1_y = -2, LENGTH_SWING  # Balançoire 1
        pivot2_x, pivot2_y = 2, LENGTH_SWING   # Balançoire 2

        # Initialisation des lignes
        line1, = ax.plot([], [], 'b-', lw=2, label="Balançoire 1", zorder=2)
        line2, = ax.plot([], [], 'r-', lw=2, label="Balançoire 2", zorder=2)
        platform1, = ax.plot([], [], 'b-', lw=4, zorder=2)
        platform2, = ax.plot([], [], 'r-', lw=4, zorder=2)
        ax.plot(pivot1_x, pivot1_y, 'ko', zorder=2)
        ax.plot(pivot2_x, pivot2_y, 'ko', zorder=2)
        ax.legend()

        # Paramètres de l’oscillation
        omega = math.sqrt(G / LENGTH_SWING)
        platform_width = 0.6

        def init():
            line1.set_data([], [])
            line2.set_data([], [])
            platform1.set_data([], [])
            platform2.set_data([], [])
            return line1, line2, platform1, platform2

        def update(frame):
            t = frame / 100
            angle1 = -max_angle * math.cos(omega * t)
            angle2 = -angle1

            angle1_rad = math.radians(angle1)
            angle2_rad = math.radians(angle2)

            x1 = pivot1_x + LENGTH_SWING * math.sin(angle1_rad)
            y1 = LENGTH_SWING - LENGTH_SWING * math.cos(angle1_rad)
            x2 = pivot2_x + LENGTH_SWING * math.sin(angle2_rad)
            y2 = LENGTH_SWING - LENGTH_SWING * math.cos(angle2_rad)

            line1.set_data([pivot1_x, x1], [pivot1_y, y1])
            line2.set_data([pivot2_x, x2], [pivot2_y, y2])

            platform1_x = [x1 - platform_width * math.cos(angle1_rad), x1 + platform_width * math.cos(angle1_rad)]
            platform1_y = [y1 - platform_width * math.sin(angle1_rad), y1 + platform_width * math.sin(angle1_rad)]
            platform2_x = [x2 - platform_width * math.cos(angle2_rad), x2 + platform_width * math.cos(angle2_rad)]
            platform2_y = [y2 - platform_width * math.sin(angle2_rad), y2 + platform_width * math.sin(angle2_rad)]
            platform1.set_data(platform1_x, platform1_y)
            platform2.set_data(platform2_x, platform2_y)

            if x1 > pivot1_x and abs(angle1) >= target_angle:
                ani.event_source.stop()
                messagebox.showinfo("Collision", f"Collision détectée à un angle de {target_angle}° !")

            return line1, line2, platform1, platform2

        ani = animation.FuncAnimation(fig, update, init_func=init, frames=range(1000), interval=20, blit=True)
        canvas.draw()

    except ValueError:
        messagebox.showerror("Erreur", "Veuillez entrer des valeurs valides pour l’angle et la hauteur (nombres).")

# Créer l’interface graphique
root = tk.Tk()
root.title("Simulation de collision de balançoires")
root.geometry("400x650")

# Titre
title_label = tk.Label(root, text="Simulation de collision de balançoires", font=("Arial", 14, "bold"))
title_label.pack(pady=10)

# Sélection de l’âge
age_label = tk.Label(root, text="Âge de l’enfant (ans) :")
age_label.pack()
age_var = tk.StringVar(value="1")
age_menu = ttk.Combobox(root, textvariable=age_var, values=[1, 2, 3, 4, 5], state="readonly")
age_menu.pack()

# Entrée de la hauteur d’oscillation
height_label = tk.Label(root, text="Hauteur d’oscillation max (m) :")
height_label.pack()
height_entry = tk.Entry(root)
height_entry.pack()
height_entry.insert(0, "0.5")  # Valeur par défaut réaliste

# Entrée de l’angle
angle_label = tk.Label(root, text="Angle d’impact (degrés) :")
angle_label.pack()
angle_entry = tk.Entry(root)
angle_entry.pack()
angle_entry.insert(0, "30")

# Sélection du type d’impact
impact_label = tk.Label(root, text="Type d’impact :")
impact_label.pack()
impact_var = tk.StringVar(value="frontal")
impact_radio1 = tk.Radiobutton(root, text="Frontal", variable=impact_var, value="frontal")
impact_radio1.pack()
impact_radio2 = tk.Radiobutton(root, text="Concentré (bord étroit)", variable=impact_var, value="concentré")
impact_radio2.pack()

# Bouton pour lancer la simulation
simulate_button = tk.Button(root, text="Lancer la simulation", command=run_simulation)
simulate_button.pack(pady=10)

# Bouton pour lancer l’animation
animate_button = tk.Button(root, text="Lancer l’animation", command=animate_swings)
animate_button.pack(pady=5)

# Zone de texte pour les résultats
result_text = tk.Text(root, height=12, width=40)
result_text.pack(pady=10)

# Lancer l’interface
root.mainloop()