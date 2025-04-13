# rendering/opengl_utils.py
import math
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

from simulation.constants import PLATFORM_WIDTH


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


def draw_swing(x_pivot, y_pivot, angle_rad, length, color):
    glDisable(GL_DEPTH_TEST)
    glColor3f(*color)
    glLineWidth(5.0)
    x_end = x_pivot + length * math.sin(angle_rad)
    y_end = y_pivot - length * math.cos(angle_rad)
    glBegin(GL_LINES)
    glVertex2f(x_pivot, y_pivot)
    glVertex2f(x_end, y_end)
    glEnd()
    platform_x1 = x_end - PLATFORM_WIDTH * math.cos(angle_rad)
    platform_y1 = y_end - PLATFORM_WIDTH * math.sin(angle_rad)
    platform_x2 = x_end + PLATFORM_WIDTH * math.cos(angle_rad)
    platform_y2 = y_end + PLATFORM_WIDTH * math.sin(angle_rad)
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
        x_pos = -4.25
        y_pos = 4.5
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


def render_text(text, x, y, font_size=16):
    """Rend une chaîne de texte à la position (x, y) en mètres."""
    glDisable(GL_DEPTH_TEST)
    try:
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        font = pygame.font.SysFont("Arial", font_size)
        text_surface = font.render(text, True, (255, 255, 255))
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        text_width = text_surface.get_width()
        text_height = text_surface.get_height()
        pixel_to_gl_x = 10.0 / 800
        pixel_to_gl_y = 7.0 / 600
        gl_text_width = text_width * pixel_to_gl_x
        gl_text_height = text_height * pixel_to_gl_y
        padding_x = 0.1
        padding_y = 0.05
        glColor4f(0, 0, 0, 0.8)
        glBegin(GL_QUADS)
        glVertex2f(x - padding_x, y + padding_y)
        glVertex2f(x + gl_text_width + padding_x, y + padding_y)
        glVertex2f(x + gl_text_width + padding_x, y - gl_text_height - padding_y)
        glVertex2f(x - padding_x, y - gl_text_height - padding_y)
        glEnd()
        glRasterPos2f(x, y - gl_text_height)
        glDrawPixels(text_width, text_height, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        glDisable(GL_BLEND)
    except Exception as e:
        print(f"Error rendering text: {e}")
    glEnable(GL_DEPTH_TEST)