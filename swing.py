# main.py
import pygame
from ui.interface import create_application


def main():
    pygame.init()
    create_application()
    pygame.quit()


if __name__ == "__main__":
    main()