import pygame
import sys
import Simulator as game
import Database as database
import sqlite3 as sql

# Initialise database connection
conn = sql.connect("Planets.db")
c = conn.cursor()

# Initialise Pygame
pygame.init()

# Setting up display, fonts, and images
WIDTH, HEIGHT = 1200, 800
FONT = pygame.font.Font('nasalization-rg.otf', 25)
FONT_small = pygame.font.Font('nasalization-rg.otf', 17)
earth_png = pygame.image.load("earth.png")
name_png = pygame.image.load("name.png")

# Setting up colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
LIGHTBLUE = (30, 144, 255)
AQUA = (127, 255, 212)
NAVY = (0, 0, 128)
RED = (188, 39, 50)
DARK_GREY = (80, 78, 81)
PEARL_WHITE = (220, 220, 220)
YELLOWISH_BROWN = (150, 100, 0)
DARK_SPACE = (14, 36, 51)
LIGHT_SPACE = (114, 136, 151)
DARK_GREY = (52, 53, 59)
LIGHT_GREY = (81, 82, 92)

# Set up the display
def set_display():
    WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    return WIN

# Setting display as a variable
WIN = set_display()
# Set up the buttons
game_button_rect = pygame.Rect(0, HEIGHT // 2 - 25, 600, 65)
edit_button_rect = pygame.Rect(0, HEIGHT // 2 + 75, 550, 65)
exit_button_rect = pygame.Rect(0, HEIGHT // 2 + 175, 500, 65)
author_rect = pygame.Rect(0, HEIGHT - 50, 227, 30)

# Game loop
while True:
    #Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            text = None
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if game_button_rect.collidepoint(event.pos): # Checks if user clicked on start simulation
                    game.main() # Run the game file and refresh display
                    WIDTH, HEIGHT = WIN.get_size()
                    WIN = set_display()
                    pygame.init()
                if edit_button_rect.collidepoint(event.pos): # Checks if user clicked on edit planets
                    database.main(c) # Run the database file and refresh display
                    WIDTH, HEIGHT = WIN.get_size()
                    WIN = set_display()
                    pygame.init()
                if exit_button_rect.collidepoint(event.pos): # Checks if user clicked on exit
                    pygame.quit() # Terminates all pygame processes
                    sys.exit()
                    
        elif event.type == pygame.VIDEORESIZE:
            # Updates values after display resize
            WIDTH, HEIGHT = pygame.display.get_surface().get_size()
        elif event.type == pygame.MOUSEMOTION:
            pass


    # Draw the background
    WIN.fill(BLACK)
    WIN.blit(earth_png, (WIDTH - 1200, HEIGHT - 820))

    # Draw the name
    WIN.blit(name_png, (0, 0))

    # Draw the start simulation button
    pygame.draw.rect(WIN, DARK_SPACE, game_button_rect)
    text = FONT.render("Start Simulation", True, WHITE)
    text_rect = text.get_rect(center=((exit_button_rect.center)[0], game_button_rect.center[1]))
    WIN.blit(text, text_rect)

    # Draw the edit planet button
    pygame.draw.rect(WIN, DARK_SPACE, edit_button_rect)
    text = FONT.render("Edit Planets", True, WHITE)
    text_rect = text.get_rect(center=((exit_button_rect.center)[0], edit_button_rect.center[1]))
    WIN.blit(text, text_rect)

    # Draw the exit button
    pygame.draw.rect(WIN, DARK_SPACE, exit_button_rect)
    text = FONT.render("Exit", True, WHITE)
    text_rect = text.get_rect(center=exit_button_rect.center)
    WIN.blit(text, text_rect)

    # Draw the author
    pygame.draw.rect(WIN, DARK_SPACE, author_rect)
    text = FONT_small.render("Author: Ying Jin Liang", True, WHITE)
    text_rect = text.get_rect(center=author_rect.center)
    WIN.blit(text, text_rect)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(60)
pygame.quit()
