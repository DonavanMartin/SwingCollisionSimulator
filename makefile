# Makefile for swing.py project

# Variables
PYTHON = python3
VENV = venv
ACTIVATE = $(VENV)/bin/activate
PIP = $(VENV)/bin/pip
SCRIPT = swing.py
REQUIREMENTS = requirements.txt

# Default target
all: setup run

# Create and set up virtual environment
$(VENV):
	$(PYTHON) -m venv $(VENV)

# Install dependencies
setup: $(VENV)
	. $(ACTIVATE) && $(PIP) install --upgrade pip
	. $(ACTIVATE) && $(PIP) install -r $(REQUIREMENTS)

# Run the script
run: setup
	. $(ACTIVATE) && $(PYTHON) $(SCRIPT)

# Clean virtual environment
clean:
	rm -rf $(VENV)

# Phony targets
.PHONY: all setup run clean