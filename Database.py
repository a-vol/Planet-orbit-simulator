import pygame
from pygame.locals import *
import sys
import sqlite3 as sql

# Initialise Pygame display and variables
pygame.init()
WIDTH, HEIGHT = 1200, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
FONT = pygame.font.Font('nasalization-rg.otf', 17)
FONT_large = pygame.font.Font('nasalization-rg.otf', 40)

# Initialise database connection
conn = sql.connect("Planets.db")
c = conn.cursor()
# Initialise colours
colour_mapping = {
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'YELLOW': (255, 255, 0),
    'LIGHT_BLUE': (30, 144, 255),
    'AQUA': (127, 255, 212),
    'NAVY': (0, 0, 128),
    'RED': (188, 39, 50),
    'DARK_GREY': (80, 78, 81),
    'PEARL_WHITE': (220, 220, 220),
    'YELLOWISH_BROWN': (150, 100, 0),
    'DARK_SPACE': (14, 36, 51),
    'LIGHT_SPACE': (114, 136, 151),
    'BLUE': (0, 0, 255),
    'GREEN': (0, 255, 0),
}

# creating database function
def create_db():
    # creating celestial body table
    c.execute("""
    CREATE TABLE IF NOT EXISTS celestial_bodies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
            )
            """)
    # creating position table
    c.execute("""
    CREATE TABLE IF NOT EXISTS position (

            celestial_body_id INTEGER,
            x REAL,
            y REAL,
            FOREIGN KEY(celestial_body_id) REFERENCES celestial_bodies(id)
            )
            """)
    # creating physical properties table
    c.execute("""
    CREATE TABLE IF NOT EXISTS physical_properties (

            celestial_body_id INTEGER,
            radiusscale REAL,
            colour TEXT,
            mass TEXT,
            orbital_period REAL,
            FOREIGN KEY(celestial_body_id) REFERENCES celestial_bodies(id)
            )
            """)
    # inserting names
    c.execute("""
            INSERT INTO celestial_bodies (name) 
            VALUES ('Sun'), ('Mercury'), ('Venus'), ('Earth'), ('Mars'), ('Jupiter'), ('Saturn'), ('Uranus'), ('Neptune'), ('Lebron')
            """)
    # inserting coordinates
    c.execute("""
            INSERT INTO position (celestial_body_id, x, y)
            VALUES (1, 0, 0), (2, 0.387, 0), (3, 0.723, 0), (4, -1, 0), (5, -1.524, 0), (6, 5.203, 0), (7, 9.537, 0), (8, 19.191, 0), (9, 30.069, 0), (10, 0.000, 0)
            """)
    # inserting radius scale, colour, mass, orbital_period
    c.execute("""
            INSERT INTO physical_properties (celestial_body_id, radiusscale, colour, mass, orbital_period)
            VALUES (1, 2, "YELLOW", "1.98840 * 10**30", 0), 
                    (2, 0.38, "DARK_GREY", "3.30110 * 10**23", 87.969), 
                    (3, 0.95, "WHITE", "4.8673 * 10**24", 224.701),
                    (4, 1, "LIGHT_BLUE", "5.9722 * 10**24", 365.2),
                    (5, 0.53, "RED", "6.4169 * 10**23", 686.98),
                    (6, 1.8, "PEARL_WHITE", "1.89813 * 10**27", 4332.59),
                    (7, 1.65, "YELLOWISH_BROWN", "5.688 * 10**26", 10759.22),
                    (8, 1.35, "AQUA", "8.6811 * 10**25", 30688.5),
                    (9, 1.25, "NAVY", "1.02409 * 10**26", 60190.0),
                    (10, 2, "YELLOW", "1.98840 * 10**30", 0)
    """)
    conn.commit()

# resetting database
def reset_db():
    try:
        # deleting existing tables
        c.execute("DROP TABLE IF EXISTS celestial_bodies")
        c.execute("DROP TABLE IF EXISTS position")
        c.execute("DROP TABLE IF EXISTS physical_properties")
        # recreates them
        create_db()
        conn.commit()
        return True
    except sql.Error as e:
        return e

# fetching data
def fetch_data():
    conn = sql.connect('Planets.db')
    c = conn.cursor()

    c.execute("""
        SELECT celestial_bodies.name, position.x, physical_properties.radiusscale, physical_properties.mass
        FROM celestial_bodies
        JOIN position ON celestial_bodies.id = position.celestial_body_id
        JOIN physical_properties ON celestial_bodies.id = physical_properties.celestial_body_id
    """)
    
    data = c.fetchall()
    conn.close()
    return data

# displaying data
def display_data(screen, data):
    screen.fill(colour_mapping['BLACK'])
    title_text = FONT_large.render("Celestial Body Database", True, colour_mapping['LIGHT_SPACE'])
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 20))
    
    # preparing headers
    headers = ["Name", "X Coord", "Radius Scale", "Mass"]
    header_x = WIDTH // 2 - len(headers) * 100
    header_y = 125
    spacing = 200
    
    header_height = 40
    pygame.draw.line(screen, colour_mapping['WHITE'], (header_x, header_y), (header_x + len(headers) * spacing, header_y),3)  # Top header line
    pygame.draw.line(screen, colour_mapping['WHITE'], (header_x, header_y + header_height), (header_x + len(headers) * spacing, header_y + header_height), 3)  # Bottom header line

    cell_positions = []

    # draws headers with the text
    for i, header in enumerate(headers):
        header_text = FONT.render(header, True, colour_mapping['WHITE'])
        text_width = header_text.get_width()
        text_height = header_text.get_height()
        screen.blit(header_text, (header_x + i * spacing + (spacing //2 - text_width //2), header_y + (header_height // 2 - text_height // 2)))
        pygame.draw.line(screen, colour_mapping['WHITE'], (header_x + i * spacing, header_y), (header_x + i * spacing, header_y + header_height), 3)

    pygame.draw.line(screen, colour_mapping['WHITE'], (header_x + len(headers) * spacing, header_y), (header_x + len(headers) * spacing, header_y + header_height), 3)

    # calculate row positions and renders data into a central position in each cell
    row_y = header_y + 40 
    row_height = 40
    for row in data:
        for i, value in enumerate(row):
            cell_text = FONT.render(str(value), True, colour_mapping['WHITE'])
            text_width = cell_text.get_width()
            text_height = cell_text.get_height()
            screen.blit(cell_text, (header_x + i * spacing + (spacing //2 - text_width // 2), row_y + (row_height // 2 - text_height // 2)))
            pygame.draw.line(screen, colour_mapping['WHITE'], (header_x + i * spacing, row_y), (header_x + i * spacing, row_y + row_height), 1)
        
            cell_positions.append((header_x + i * spacing, row_y, spacing, row_height))

        pygame.draw.line(screen, colour_mapping['WHITE'], (header_x, row_y), (header_x + len(headers) * spacing, row_y), 1)
        row_y += row_height  # Move down for the next row

    pygame.draw.line(screen, colour_mapping['WHITE'], (header_x, row_y), (header_x + len(headers) * spacing, row_y), 1)
    pygame.draw.line(screen, colour_mapping['WHITE'], (header_x + len(headers) * spacing, header_y), (header_x + len(headers) * spacing, row_y), 1)

    # returns the cell position of each cell in a list
    cell_positions = [cell_positions[i:i + 4] for i in range(0, len(cell_positions), 4)]
    return cell_positions

# finding which cell the user clicks on
def find_clicked_cell(cell_positions):
    #Set up variables and headers
    headers = ["Name", "X Coord", "Radius Scale", "Mass"]
    planet_id = 0
    field = 0
    rect = 0
    #iterate through each cell
    for x, cell in enumerate(cell_positions):
        #iterate through each item in that cell
        for y, value in enumerate(cell): 
            #detect if user mouse is in the cell's rectangle
            if pygame.Rect(cell_positions[x][y]).collidepoint(pygame.mouse.get_pos()):
                #assign the variables with values for that cell
                planet_id = x+1
                if y == 0:
                    break
                field = headers[y]
                rect = pygame.Rect(value)
    
    return planet_id, field, rect

# database status text
def status_text(text):
    if text == True:
        text = FONT.render('Value has been updated!', True, colour_mapping['GREEN'])
    elif text == 'Database Reset':
        text = FONT.render(text, True, colour_mapping['GREEN'])
    elif text == 'Value not in required form':
        text = FONT.render(text, True, colour_mapping['RED'])
    else:
        text = FONT.render(text, True, colour_mapping['RED'])
    WIN.blit(text, (200, 720))

#Validating user input for mass
def check_notation(value):
    #Removes whitespaces
    value = value.replace(" ", "")
    #Checks for *
    if "*" not in value:
        return False
    #Splits input at the first occuring *
    base_part, exp_part = value.split("*", 1)
    #Attempts to find 10 in the exponent
    if "10" not in exp_part:
        return False
    #Splits the expontent after the 10
    exp_split = exp_part.split("10", 1)
    #Checks for the expontentation after 10 in the exponent
    if len(exp_split) != 2 or not exp_split[1].startswith("**"):
        return 
    #Extract only the number in the exponent
    exponent = exp_split[1][2:]
    # Converts base and exponent form strings to numbers
    try:
        float(base_part) 
        int(exponent)   
    except ValueError:
        return False
    return True  

# takes in which planet and field to update, and the new value
def update(planet_id, field, value):
    if field == 'X Coord':
        try:
            #Validates input then updates database
            value = float(value)
            value += 0
            c.execute(""" UPDATE position
            SET x = ?
            WHERE celestial_body_id = ?""", (value, planet_id))
            conn.commit()
            return True
        except sql.Error as e:
            return "Error updating xcoord: {e}"
        except TypeError:
            return 'Value not a number'
        except ValueError:
            return 'Value not a number'
        
    elif field == 'Radius Scale':
        try:
            # Validates input then updates database
            value = float(value)
            value += 0
            c.execute(""" UPDATE physical_properties
            SET radiusscale = ?
            WHERE celestial_body_id = ?""", (value, planet_id))
            conn.commit()
            return True
        except sql.Error as e:
            return "Error updating radius: {e}"
        except TypeError:
            return 'Value not a number'
        except ValueError:
            return 'Value not a number'
        
    elif field == 'Mass':
        #Validates input using function before updating database
        check = check_notation(value)
        if check == False:
            return 'Value not in required form'
        else:
            try:
                c.execute(""" UPDATE physical_properties
                SET mass = ?
                WHERE celestial_body_id = ?""", (value, planet_id))
                conn.commit()
                return True
            except sql.Error as e:
                return "Error updating mass: {e}"
            except TypeError:
                return 'Value not a number'
            except ValueError:
                return 'Value not a number'

# displays help text
def display_tip(key):
    if key == 'xcoord':
        text = FONT.render("*X coord is a scale, 1 = 1AU = 149,597,870,700 km away from Sun", True, colour_mapping['WHITE'])
        WIN.blit(text, (200, 600))
    elif key == 'radius':
        text = FONT.render("*Radius is arbitrary, Earth is 16 pixels, and other values are a scale factor of Earth, 2 = 32 pixels", True, colour_mapping['WHITE'])
        WIN.blit(text, (200, 600))
    elif key == 'mass':
        text = FONT.render("*Mass is in kg, please write mass with standard form, e.g 1 * 10 ** 27", True, colour_mapping['WHITE'])
        WIN.blit(text, (200, 600))
    else:
        text = FONT.render("*Click on cell to update", True, colour_mapping['WHITE'])
        WIN.blit(text, (200, 600))

xcoord_Rect = pygame.Rect(400, 125, 200, 440)
radius_Rect = pygame.Rect(600, 125, 200, 440)
mass_Rect = pygame.Rect(800, 125, 200, 440)


def main(c):
    #Globalise variables
    global WIDTH, HEIGHT
    input_active = False
    input_text = ''
    status = ''

    # Attempts to display data
    try:
        display_data(screen, fetch_data())
    except sql.OperationalError:
        reset_db()
    # Main loop
    while True:
        WIDTH, HEIGHT = pygame.display.get_surface().get_size()
        screen.fill((0, 0, 0))
        #Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Checks if user clicked LMB
                if event.button == 1:
                    # Checks if user clicked exit back to menu
                    if exit_button_rect.collidepoint(event.pos):
                        return 'menu'
                    # Checks if user clicked on reset database
                    elif resetbutton.collidepoint(event.pos):
                        reset_status = reset_db()
                        if reset_status == True:
                            status = 'Database Reset'
                    else:
                        # Attempts to find which cell user clicked on
                        planet_id, field, input_rect = find_clicked_cell(display_data(screen, fetch_data()))
                        # Activates input box
                        if planet_id and input_rect:
                            input_active = True
                        if input_rect == 0:
                            input_active = False

            # Updates values after display resize
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = pygame.display.get_surface().get_size()
            elif event.type == pygame.MOUSEMOTION:
                pass
            elif event.type == pygame.KEYDOWN:
                # Takes in user text input
                if input_active:
                    if event.key == pygame.K_RETURN:
                        status = update(planet_id, field, input_text)
                        input_active = False
                        input_text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode
                    if event.key == pygame.K_ESCAPE:
                        input_active = False
                        input_text = ''

        # Displays data
        display_data(screen, fetch_data())

        # Renders exit btuton
        exit_button_rect = pygame.Rect(75, 135, 50, 20)
        exit_colour = colour_mapping['DARK_SPACE']
        pygame.draw.rect(WIN, exit_colour, exit_button_rect)
        text = FONT.render("Exit", True, colour_mapping['WHITE'])
        text_rect = text.get_rect(center=exit_button_rect.center)
        WIN.blit(text, text_rect)

        # Renders reset database button
        resetbutton = pygame.Rect(200, 630, 150, 25)
        reset_colour = colour_mapping['DARK_SPACE']
        pygame.draw.rect(WIN, reset_colour, resetbutton)
        text = FONT.render("Reset Database", True, colour_mapping['WHITE'])
        text_rect = text.get_rect(center=resetbutton.center)
        WIN.blit(text, text_rect)

        mouse_pos = pygame.mouse.get_pos()

        # Displays tip depending on where mouse is
        if xcoord_Rect.collidepoint(mouse_pos):
            display_tip('xcoord')
        elif radius_Rect.collidepoint(mouse_pos):
            display_tip('radius')
        elif mass_Rect.collidepoint(mouse_pos):
            display_tip('mass')
        else:
            display_tip(None)

        # Displays input box
        if input_active:
            pygame.draw.rect(WIN, colour_mapping['DARK_SPACE'], input_rect)
            text_surface = FONT.render(input_text, True, colour_mapping['WHITE'])
            WIN.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))

        # Displays status
        status_text(status)
        pygame.display.flip()
        pygame.time.Clock().tick(60)

if __name__ == '__main__':
    conn = sql.connect("Planets.db")
    c = conn.cursor()
    main(c)

    conn.commit()
    conn.close()
