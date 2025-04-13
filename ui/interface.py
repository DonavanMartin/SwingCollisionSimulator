# ui/interface.py
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from PIL import Image, ImageTk
import pygame
from simulation.calculations import (
    calculate_max_angle, run_simulation
)
from simulation.constants import LBS_TO_KG, LENGTH_SWING, ANTHROPOMETRIC_DATA
from animation.animation import animate_swings_thread


class SwingSimulationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulation de collision de balançoires")
        self.root.geometry("1200x800")
        self.is_running = tk.BooleanVar(value=False)
        self.target_angle = 0
        self.max_angle = 0
        self.force = 0
        self.velocity1_global = 0
        self.velocity2_global = 0
        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        style.configure("Title.TLabel", font=("Arial", 12, "bold"))
        style.configure("TButton", font=("Arial", 10))
        style.configure("TCombobox", font=("Arial", 10))
        style.configure("TRadiobutton", background="#f0f0f0", font=("Arial", 10))

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Left panel: Input and Results
        left_frame = ttk.Frame(main_frame, relief="ridge", borderwidth=2)
        left_frame.pack(side="left", fill="y", padx=(0, 10), pady=5)

        # Input section
        input_frame = ttk.Frame(left_frame)
        input_frame.pack(fill="x", padx=5, pady=5)

        title_label = ttk.Label(input_frame, text="Paramètres de simulation", style="Title.TLabel")
        title_label.pack(pady=(0, 10))

        age_label = ttk.Label(input_frame, text="Âge de l’enfant (ans) :")
        age_label.pack(anchor="w", padx=5)
        self.age_var = tk.StringVar(value="1")
        age_menu = ttk.Combobox(input_frame, textvariable=self.age_var, values=[1, 2, 3, 4, 5], state="readonly", width=10)
        age_menu.pack(anchor="w", padx=5, pady=2)

        height_label = ttk.Label(input_frame, text="Hauteur d’oscillation max (m) :")
        height_label.pack(anchor="w", padx=5)
        self.height_entry = ttk.Entry(input_frame, width=10)
        self.height_entry.pack(anchor="w", padx=5, pady=2)
        self.height_entry.insert(0, "1")

        mass1_label = ttk.Label(input_frame, text="Masse balançoire 1 (lbs) :")
        mass1_label.pack(anchor="w", padx=5)
        self.mass1_entry = ttk.Entry(input_frame, width=10)
        self.mass1_entry.pack(anchor="w", padx=5, pady=2)
        self.mass1_entry.insert(0, "100")

        mass2_label = ttk.Label(input_frame, text="Masse balançoire 2 (lbs) :")
        mass2_label.pack(anchor="w", padx=5)
        self.mass2_entry = ttk.Entry(input_frame, width=10)
        self.mass2_entry.pack(anchor="w", padx=5, pady=2)
        self.mass2_entry.insert(0, "100")

        v_init1_label = ttk.Label(input_frame, text="Vitesse initiale balançoire 1 (m/s) :")
        v_init1_label.pack(anchor="w", padx=5)
        self.v_init1_entry = ttk.Entry(input_frame, width=10)
        self.v_init1_entry.pack(anchor="w", padx=5, pady=2)
        self.v_init1_entry.insert(0, "0")

        v_init2_label = ttk.Label(input_frame, text="Vitesse initiale balançoire 2 (m/s) :")
        v_init2_label.pack(anchor="w", padx=5)
        self.v_init2_entry = ttk.Entry(input_frame, width=10)
        self.v_init2_entry.pack(anchor="w", padx=5, pady=2)
        self.v_init2_entry.insert(0, "0")

        angle_label = ttk.Label(input_frame, text="Angle d’impact (degrés, par rapport à l’horizontal) :")
        angle_label.pack(anchor="w", padx=5)
        self.angle_entry = ttk.Entry(input_frame, width=10)
        self.angle_entry.pack(anchor="w", padx=5, pady=2)
        self.angle_entry.insert(0, "45")

        impact_label = ttk.Label(input_frame, text="Type d’impact :")
        impact_label.pack(anchor="w", padx=5)
        self.impact_var = tk.StringVar(value="frontal")
        impact_radio1 = ttk.Radiobutton(input_frame, text="Frontal", variable=self.impact_var, value="frontal")
        impact_radio1.pack(anchor="w", padx=5)
        impact_radio2 = ttk.Radiobutton(input_frame, text="Concentré (bord étroit)", variable=self.impact_var, value="concentré")
        impact_radio2.pack(anchor="w", padx=5)

        simulate_button = ttk.Button(input_frame, text="Lancer la simulation", command=self.run_simulation)
        simulate_button.pack(pady=10)

        # Result section
        result_frame = ttk.Frame(left_frame)
        result_frame.pack(fill="x", padx=5, pady=5)
        result_title = ttk.Label(result_frame, text="Résultats de la simulation", style="Title.TLabel")
        result_title.pack()
        self.result_text = tk.Text(result_frame, height=20, width=55, font=("Arial", 10))
        self.result_text.pack(pady=5)

        # Right panel: Animation
        animation_frame = ttk.Frame(main_frame, relief="ridge", borderwidth=2)
        animation_frame.pack(side="right", fill="both", expand=True)

        animation_title = ttk.Label(animation_frame, text="Animation des balançoires", style="Title.TLabel")
        animation_title.pack(pady=(0, 5))

        control_frame = ttk.Frame(animation_frame)
        control_frame.pack(fill="x", pady=5)
        self.toggle_button = ttk.Button(control_frame, text="Start", command=self.toggle_animation)
        self.toggle_button.pack(side="left", padx=5)

        self.animation_surface = pygame.Surface((800, 600))
        self.animation_surface.fill((200, 200, 200))
        self.animation_label = ttk.Label(animation_frame)
        self.animation_label.pack(pady=5)
        initial_image = Image.frombytes("RGB", (800, 600), pygame.image.tostring(self.animation_surface, "RGB"))
        initial_photo = ImageTk.PhotoImage(initial_image)
        self.animation_label.configure(image=initial_photo)
        self.animation_label.image = initial_photo

    def update_results(self, results):
        """Met à jour la fenêtre de résultats avec un dictionnaire de résultats."""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Âge de l’enfant : {results['age']} ans\n")
        self.result_text.insert(tk.END, f"Hauteur d’oscillation max : {results['max_height']:.2f} m\n")
        self.result_text.insert(tk.END, f"Masse balançoire 1 : {results['mass1_lbs']:.1f} lbs ({results['mass1_kg']:.1f} kg)\n")
        self.result_text.insert(tk.END, f"Masse balançoire 2 : {results['mass2_lbs']:.1f} lbs ({results['mass2_kg']:.1f} kg)\n")
        self.result_text.insert(tk.END, f"Vitesse initiale balançoire 1 : {results['v_init1']:.2f} m/s\n")
        self.result_text.insert(tk.END, f"Vitesse initiale balançoire 2 : {results['v_init2']:.2f} m/s\n")
        self.result_text.insert(tk.END, f"Angle max (calculé, par rapport à la verticale) : {results['max_angle']:.1f}°\n")
        self.result_text.insert(tk.END, f"Angle d’impact (par rapport à l’horizontal) : {results['angle_horizontal']:.1f}°\n")
        self.result_text.insert(tk.END, f"Type d’impact : {results['impact_type']}\n")
        self.result_text.insert(tk.END, f"Vitesse d’impact balançoire 1 : {results['velocity1']:.2f} m/s\n")
        self.result_text.insert(tk.END, f"Vitesse d’impact balançoire 2 : {results['velocity2']:.2f} m/s\n")
        self.result_text.insert(tk.END, f"Vitesse relative d’impact : {results['relative_velocity']:.2f} m/s\n")
        self.result_text.insert(tk.END, f"Force d’impact : {results['force']:.2f} N\n")
        self.result_text.insert(tk.END, f"Surface d’impact : {results['surface_cm2']:.2f} cm²\n")
        self.result_text.insert(tk.END, f"Pression exercée : {results['pressure_mpa']:.2f} MPa\n")
        self.result_text.insert(tk.END, f"Probabilité de décapitation partielle : {results['decapitation_risk']}\n")
        self.result_text.insert(tk.END, f"Probabilité de fracture cervicale : {results['cervical_fracture_risk']}\n")
        self.result_text.insert(tk.END, f"Probabilité de commotion cérébrale : {results['concussion_risk']}\n")

    def run_simulation(self):
        try:
            age = int(self.age_var.get())
            angle_horizontal = float(self.angle_entry.get())
            mass1_lbs = float(self.mass1_entry.get())
            mass2_lbs = float(self.mass2_entry.get())
            v_init1 = float(self.v_init1_entry.get())
            v_init2 = float(self.v_init2_entry.get())
            max_height = float(self.height_entry.get())
            impact_type = self.impact_var.get()
            
            results = run_simulation(
                age, angle_horizontal, mass1_lbs, mass2_lbs, v_init1, v_init2, max_height, impact_type
            )
            
            self.force = results["force"]
            self.velocity1_global = results["velocity1"]
            self.velocity2_global = results["velocity2"]
            self.max_angle = results["max_angle"]
            self.update_results(results)
        except ValueError as e:
            messagebox.showerror("Erreur", str(e))

    def toggle_animation(self):
        if self.is_running.get():
            self.is_running.set(False)
            self.toggle_button.configure(text="Start")
        else:
            try:
                age = int(self.age_var.get())
                angle_horizontal = float(self.angle_entry.get())
                mass1_lbs = float(self.mass1_entry.get())
                mass2_lbs = float(self.mass2_entry.get())
                v_init1 = float(self.v_init1_entry.get())
                v_init2 = float(self.v_init2_entry.get())
                max_height = float(self.height_entry.get())
                impact_type = self.impact_var.get()
                self.target_angle = 90 - angle_horizontal
                if self.target_angle < 0:
                    messagebox.showerror("Erreur", "L’angle par rapport à l’horizontal doit être entre 0 et 90 degrés.")
                    return
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
                self.max_angle = calculate_max_angle(max_height)
                if not 0 <= self.target_angle <= self.max_angle:
                    messagebox.showerror("Erreur", f"L’angle (par rapport à la verticale) doit être entre 0 et {self.max_angle:.1f}°, soit entre {90-self.max_angle:.1f} et 90° par rapport à l’horizontal.")
                    return
                self.is_running.set(True)
                self.toggle_button.configure(text="Stop")
                threading.Thread(
                    target=animate_swings_thread,
                    args=(self.animation_surface, self.animation_label, self.root, self.toggle_button, self.is_running,
                          self.update_results, self.max_angle, self.target_angle, age, mass1_lbs, mass2_lbs,
                          v_init1, v_init2, angle_horizontal, max_height, impact_type),
                    daemon=True
                ).start()
            except ValueError:
                messagebox.showerror("Erreur", "Valeurs invalides pour les paramètres.")


def create_application():
    root = tk.Tk()
    app = SwingSimulationApp(root)
    root.mainloop()