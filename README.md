⚠️ **AVERTISSEMENT**

> Ce projet, **SwingCollisionSimulator**, s’inspire d’observations de situations réelles impliquant des balançoires. Il est conçu exclusivement à des **fins éducatives, de simulation et d’analyse**. L’analyse a été réalisée par un **inspecteur certifié canadien des aires de jeux (CPSI)** conformément à la norme **CSA Z614:20**.  
>  
> **IL EST STRICTEMENT INTERDIT DE REPRODUIRE CE PROJET DANS LA RÉALITÉ.** Toute tentative pourrait entraîner des **blessures graves ou des accidents**. Toute reproduction est **fortement déconseillée** et se fait aux **risques et périls de l’utilisateur**.

# SwingCollisionSimulator

![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Description

**SwingCollisionSimulator** est une application Python qui simule la collision entre deux balançoires à plateforme, avec une analyse des risques de blessure pour un enfant (modélisé comme un bonhomme allumette). Le projet utilise `tkinter` pour une interface graphique interactive et `matplotlib` pour une animation visuelle des balançoires oscillant face à face. L’utilisateur peut sélectionner l’âge de l’enfant, l’angle d’impact, et le type d’impact (frontal ou concentré) pour calculer la force, la pression exercée sur le cou, et la probabilité d’une décapitation partielle par écrasement. Une image d’arrière-plan personnalisée peut être ajoutée, et un bonhomme allumette de 1 mètre est dessiné sur la balançoire pour représenter l’enfant.

### Caractéristiques principales

- Interface graphique interactive avec `tkinter` pour configurer les paramètres de la simulation.
- Animation réaliste des balançoires avec `matplotlib`, incluant un bonhomme allumette assis sur une balançoire.
- Calculs physiques détaillés : vitesse, force d’impact, pression, et analyse des risques basée sur des données anthropométriques.
- Support pour une image d’arrière-plan personnalisée dans la fenêtre d’animation.
- Visualisation claire des balançoires oscillant face à face, avec une détection de collision à l’angle spécifié.

## Prérequis

- **Python 3.x** (testé avec Python 3.13)
- Bibliothèques Python :
  - `tkinter` (généralement inclus avec Python, mais peut nécessiter une configuration sur macOS/Linux)
  - `matplotlib` (pour l’animation et la visualisation)
- Une image d’arrière-plan (par exemple, `background.jpg`) pour la visualisation (optionnel).

## Installation

1. **Clonez le dépôt** :
   ```bash
   git clone https://github.com/votre_nom/SwingCollisionSimulator.git
   cd SwingCollisionSimulator
   ```

### Installez les dépendances :

Assurez-vous que `matplotlib` est installé. Vous pouvez l’installer avec pip :

```bash
pip install matplotlib
```

### Configurer `tkinter` (si nécessaire) :

- **Sur Windows** : `tkinter` est généralement inclus avec Python.
- **Sur macOS** : Vous devrez peut-être installer Tcl/Tk :

```bash
brew install tcl-tk
```

Si `tkinter` ne fonctionne pas, réinstallez Python avec le support de Tcl/Tk (voir la section [Dépannage](#dépannage-troubleshooting)).

- **Sur Linux** : Installez `tkinter` avec :

```bash
sudo apt-get install python3-tk
```

---

## Ajouter une image d’arrière-plan (optionnel) :

Placez une image nommée `background.jpg` (ou modifiez le nom dans le code) dans le répertoire du projet pour l’utiliser comme arrière-plan de l’animation.

---

## Utilisation

### Exécutez le script :

```bash
python swing_collision_simulator.py
```

### Configurer les paramètres :

- **Âge de l’enfant** : Sélectionnez l’âge (1 à 5 ans) dans le menu déroulant.
- **Angle d’impact** : Entrez un angle entre 0° et 90° (par exemple, 30°).
- **Type d’impact** : Choisissez entre `Frontal` ou `Concentré (bord étroit)`.

### Lancer la simulation :

Cliquez sur **"Lancer la simulation"** pour calculer et afficher les résultats (vitesse, force, pression, probabilité de décapitation partielle).

### Lancer l’animation :

Cliquez sur **"Lancer l’animation"** pour voir les balançoires osciller avec un bonhomme allumette assis sur la balançoire de gauche.  
L’animation s’arrête lorsque l’angle d’impact est atteint.

---

## Exemple de résultats

- **Âge** : 3 ans
- **Angle** : 30°
- **Type d’impact** : Concentré
- **Vitesse** : 4,43 m/s
- **Force** : 3987 N
- **Surface d’impact** : 6 cm²
- **Pression** : 6,65 MPa
- **Probabilité de décapitation partielle** : _Possible_

---

## Captures d’écran

### Interface principale

<img src="screenshots/interface.png" alt="Interface principale" width="500">

### Animation des balançoires

![Animation](screenshots/animation.png)

---

## Structure du projet

- `swing_collision_simulator.py` : Script principal contenant le code de la simulation et de l’animation.
- `background.jpg` : Image d’arrière-plan (optionnelle, non incluse dans le dépôt).
- `screenshots/` : Dossier pour les captures d’écran (à créer).

---

## Dépannage (Troubleshooting)

### Problème avec `tkinter` sur macOS

Si vous obtenez une erreur comme :

```text
ModuleNotFoundError: No module named '_tkinter'
```

Suivez ces étapes :

1. Installez Tcl/Tk :

```bash
brew install tcl-tk
```

2. Réinstallez Python avec le support de Tcl/Tk :

- Téléchargez Python depuis [python.org](https://www.python.org) et installez-le.
- Ou réinstallez via Homebrew :

```bash
brew uninstall python@3.13
brew install python@3.13
```

3. Vérifiez que `tkinter` fonctionne :

```bash
python3 -c "import tkinter"
```

---

### Image d’arrière-plan non trouvée

Assurez-vous que l’image `background.jpg` est dans le répertoire du script.  
Vous pouvez également modifier le nom ou le chemin de l’image dans le code (dans la fonction `animate_swings`).

---

## Contribuer

Les contributions sont les bienvenues !  
Si vous souhaitez ajouter des fonctionnalités (par exemple, un deuxième bonhomme, des paramètres personnalisables pour la taille des balançoires, ou des effets visuels supplémentaires), suivez ces étapes :

1. **Forkez** le dépôt.
2. Créez une branche pour votre fonctionnalité :

```bash
git checkout -b ma-nouvelle-fonctionnalite
```

3. Faites vos modifications et **commitez** :

```bash
git commit -m "Ajout de ma nouvelle fonctionnalité"
```

4. **Poussez** votre branche :

```bash
git push origin ma-nouvelle-fonctionnalite
```

5. **Ouvrez une pull request** sur GitHub.

---

## Licence

Ce projet est sous licence MIT.  
Voir le fichier `LICENSE` pour plus de détails.

---

## Auteurs

- Donavan Martin, Ing., Inspecteur certifié CPSI - Créateur initial – [Votre Profil GitHub](https://github.com/)

```
