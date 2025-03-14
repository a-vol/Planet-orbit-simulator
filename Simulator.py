import math
import pygame
from pygame.locals import *
from pygame.math import Vector2
import random
import threading
import sqlite3 as sql
import Database as database
import os

#Initialise pygame and music
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load('englishsunshine.mp3')

#Set up display
WIDTH, HEIGHT = 1200, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
WIN_CENTRE = Vector2(WIDTH // 2, HEIGHT // 2)
WCENTRE, HCENTRE = WIN_CENTRE

#Set up caption and icon
pygame.display.set_caption('PlanetOrbit')
icon = pygame.image.load('PlanetOrbit.ico')
pygame.display.set_icon(icon)

#Set up colours
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
}

#Set up font
FONT = pygame.font.SysFont('arial', 16)

#Set up variables
default = 1
details = False
show_orbit = True
show_stars = True
show_lebron = False



#Planet class
class Planet:
    #Physics constants
    AU = 149.6e6 *1000
    G = 6.67428e-11
    SCALE = 250 / AU  #arbritary scale
    TIMESTEP = 3600*24 / default# days per frame
                                # 1 = 1 day per frame = 60 days per second
                                # 30 = 1/30th of a day per frame = 2 days per second
                                # 60 = 1/60th of a day per frame = 1 day per second
    EarthRadius = 16 #Arbitrary radius of earth 
    pause = False

    def __init__(self, x, y, radiusScale, colour, mass, orbital_period, name, imagepath = None):
        self.x = x
        self.y = y
        #Radius of planet as a ratio of earth's radius
        self.radiusScale = radiusScale
        self.colour = colour
        self.mass = mass
        self.orbital_period = orbital_period
        self.name = name
        self.imagepath = imagepath

        self.orbit = []
        self.sun = False
        self.distance_to_sun = 0

        self.x_vel = 0
        self.y_vel = 0

        self.loop_counter = 0
    
    #Render the planet and orbit on the window
    def draw(self, win):
        x = self.x * self.SCALE + WCENTRE
        y = self.y * self.SCALE + HCENTRE
        radius = self.radiusScale * self.EarthRadius

        #Render orbit lines
        if len(self.orbit) > 2:
            updated_points = [(x * self.SCALE + WCENTRE, y * self.SCALE + HCENTRE) for x, y in self.orbit]
            if show_orbit:
                pygame.draw.lines(WIN, self.colour, False, updated_points, 1)
        pygame.draw.circle(win, self.colour, (x, y), radius)
        
        #Render distance to sun
        if not self.sun and details:
            distance_text = FONT.render(f"{round(self.distance_to_sun/1000, 1)} km", 1, colour_mapping['WHITE'])
            WIN.blit(distance_text, (x - distance_text.get_width(), y - distance_text.get_height()))


    #Calculate force of attraction using Newton's law of universal gravitation
    def attraction(self, other):
        #Calculate the difference between the two planets in x and y directions
        dx = other.x - self.x
        dy = other.y - self.y
        # Calculate distance using pythagoras theorem
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if other.sun:
            self.distance_to_sun = distance
        # Calculate force of attraction using Newton's law
        force = self.G * self.mass * other.mass / distance**2
        # Calculating angle between the two planets
        theta = math.atan2(dy, dx)
        # Calculate the x and y components of the force
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x, force_y
    
    #Update the position of the planet
    def update_position(self, planets):

        if Planet.pause:
            return
        # Calculates resultant force
        total_fx = 0
        total_fy = 0
        for planet in planets:
            if self == planet:
                continue
            if self.sun:
                return 

            fx, fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy

        # Converting force into components of velocity 
        # Updating velocities
        self.x_vel += total_fx / self.mass * self.TIMESTEP
        self.y_vel += total_fy / self.mass * self.TIMESTEP

        # Updating positions
        self.x += self.x_vel * self.TIMESTEP
        self.y += self.y_vel * self.TIMESTEP
        self.orbit.append((self.x, self.y))

    #Render information about the selected planet
    def render_planet_info(self, win, sun):
        if show_lebron:
            text = 'LEBRON'
            name_text = FONT.render(f"Name: {text}", 1, colour_mapping['YELLOW'])
            mass_text = FONT.render(f"Mass: {text} kg", 1, colour_mapping['YELLOW'])
            orbital_period_text = FONT.render(f"Orbital Period: {text} days", 1, colour_mapping['YELLOW'])
            distance_text = FONT.render(f"Distance from Sun: {text} km", 1, colour_mapping['YELLOW'])
            velocity = math.sqrt(self.x_vel**2 + self.y_vel**2)
            vel_text = FONT.render(f"Velocity: {text} km/s", 1, colour_mapping['YELLOW'])

        else:
            name_text = FONT.render(f"Name: {self.name}", 1, self.colour)
            mass_text = FONT.render(f"Mass: {self.mass:.5g} kg", 1, self.colour)
            orbital_period_text = FONT.render(f"Orbital Period: {round(self.orbital_period, 2)} days", 1, self.colour)
            distance_text = FONT.render(f"Distance from Sun: {round(self.distance_to_sun / 1000, 2):,} km", 1, self.colour)
            velocity = math.sqrt(self.x_vel**2 + self.y_vel**2)
            vel_text = FONT.render(f"Velocity: {round(velocity / 1000, 2):,} km/s", 1, self.colour)

        #Calculate the alignment of the text
        alignment = max(
            name_text.get_width(), mass_text.get_width(),
            orbital_period_text.get_width(), 
            distance_text.get_width(), vel_text.get_width()) + 15
        
        #Rendering text
        WIN.blit(name_text, (WIDTH - alignment, 15))
        WIN.blit(mass_text, (WIDTH - alignment, 35))
        WIN.blit(orbital_period_text, (WIDTH - alignment, 55))
        WIN.blit(distance_text, (WIDTH - alignment, 75))
        WIN.blit(vel_text, (WIDTH - alignment, 95))

        # Calculating the position of the planet
        x = self.x * self.SCALE + WCENTRE
        y = self.y * self.SCALE + HCENTRE
        planet_pos = x, y 
        sun_pos = WCENTRE, HCENTRE

        #Draws a line from the sun to the planet
        pygame.draw.lines( WIN, self.colour, False, [sun_pos, planet_pos], 2)
        if not self.sun:
            #Renders the distance from sun as text
            distance_text = FONT.render(f"{round(self.distance_to_sun/1000, 1)} km", 1, colour_mapping['WHITE'])
            WIN.blit(distance_text, (x - distance_text.get_width(), y - distance_text.get_height()))

    #Lebron function
    def lebron(self,):
        if self.name == 'Lebron':
            WIN.blit(self.imagepath, (WCENTRE - (80//2), HCENTRE - (75//2)))

#Main function
def main():
    #Globalise variables
    global WIN_CENTRE, WCENTRE, HCENTRE, WIDTH, HEIGHT, default, details, show_orbit, show_stars, show_lebron
    run = True
    pause = False
    drag = False
    drag_start = False

    # Set up database connection
    conn = sql.connect("Planets.db")
    c = conn.cursor()
    
    # Check if database exists if not, create one
    try: 
        c.execute('SELECT * FROM celestial_bodies') 
        exists = c.fetchone()
    except sql.OperationalError:
        exists = False
    if not exists:
        database.create_db()

    #Set up clock
    clock = pygame.time.Clock()

    #Fetching all the planetary data form database using SQL queries
    sun_x, sun_y, sun_radiusScale, sun_colour, sun_mass, sun_orbital_period, sun_name = c.execute("""
                                                                                                  SELECT position.x, 
                                                                                                         position.y, 
                                                                                                         physical_properties.radiusscale, 
                                                                                                         physical_properties.colour, 
                                                                                                         physical_properties.mass, 
                                                                                                         physical_properties.orbital_period, 
                                                                                                         celestial_bodies.name 
                                                                                                         FROM celestial_bodies JOIN position 
                                                                                                         ON celestial_bodies.id = position.celestial_body_id 
                                                                                                         JOIN physical_properties 
                                                                                                         ON celestial_bodies.id = physical_properties.celestial_body_id 
                                                                                                         WHERE celestial_bodies.name = 'Sun'
                                                                                                  """).fetchone()
    mercury_x, mercury_y, mercury_radiusScale, mercury_colour, mercury_mass, mercury_orbital_period, mercury_name = c.execute("SELECT position.x, position.y, physical_properties.radiusscale, physical_properties.colour, physical_properties.mass, physical_properties.orbital_period, celestial_bodies.name FROM celestial_bodies JOIN position ON celestial_bodies.id = position.celestial_body_id JOIN physical_properties ON celestial_bodies.id = physical_properties.celestial_body_id WHERE celestial_bodies.name = 'Mercury'").fetchone()
    venus_x, venus_y, venus_radiusScale, venus_colour, venus_mass, venus_orbital_period, venus_name = c.execute("SELECT position.x, position.y, physical_properties.radiusscale, physical_properties.colour, physical_properties.mass, physical_properties.orbital_period, celestial_bodies.name FROM celestial_bodies JOIN position ON celestial_bodies.id = position.celestial_body_id JOIN physical_properties ON celestial_bodies.id = physical_properties.celestial_body_id WHERE celestial_bodies.name = 'Venus'").fetchone()
    earth_x, earth_y, earth_radiusScale, earth_colour, earth_mass, earth_orbital_period, earth_name = c.execute("SELECT position.x, position.y, physical_properties.radiusscale, physical_properties.colour, physical_properties.mass, physical_properties.orbital_period, celestial_bodies.name FROM celestial_bodies JOIN position ON celestial_bodies.id = position.celestial_body_id JOIN physical_properties ON celestial_bodies.id = physical_properties.celestial_body_id WHERE celestial_bodies.name = 'Earth'").fetchone()
    mars_x, mars_y, mars_radiusScale, mars_colour, mars_mass, mars_orbital_period, mars_name = c.execute("SELECT position.x, position.y, physical_properties.radiusscale, physical_properties.colour, physical_properties.mass, physical_properties.orbital_period, celestial_bodies.name FROM celestial_bodies JOIN position ON celestial_bodies.id = position.celestial_body_id JOIN physical_properties ON celestial_bodies.id = physical_properties.celestial_body_id WHERE celestial_bodies.name = 'Mars'").fetchone()
    jupiter_x, jupiter_y, jupiter_radiusScale, jupiter_colour, jupiter_mass, jupiter_orbital_period, jupiter_name = c.execute("SELECT position.x, position.y, physical_properties.radiusscale, physical_properties.colour, physical_properties.mass, physical_properties.orbital_period, celestial_bodies.name FROM celestial_bodies JOIN position ON celestial_bodies.id = position.celestial_body_id JOIN physical_properties ON celestial_bodies.id = physical_properties.celestial_body_id WHERE celestial_bodies.name = 'Jupiter'").fetchone()
    saturn_x, saturn_y, saturn_radiusScale, saturn_colour, saturn_mass, saturn_orbital_period, saturn_name = c.execute("SELECT position.x, position.y, physical_properties.radiusscale, physical_properties.colour, physical_properties.mass, physical_properties.orbital_period, celestial_bodies.name FROM celestial_bodies JOIN position ON celestial_bodies.id = position.celestial_body_id JOIN physical_properties ON celestial_bodies.id = physical_properties.celestial_body_id WHERE celestial_bodies.name = 'Saturn'").fetchone()
    uranus_x, uranus_y, uranus_radiusScale, uranus_colour, uranus_mass, uranus_orbital_period, uranus_name = c.execute("SELECT position.x, position.y, physical_properties.radiusscale, physical_properties.colour, physical_properties.mass, physical_properties.orbital_period, celestial_bodies.name FROM celestial_bodies JOIN position ON celestial_bodies.id = position.celestial_body_id JOIN physical_properties ON celestial_bodies.id = physical_properties.celestial_body_id WHERE celestial_bodies.name = 'Uranus'").fetchone()
    neptune_x, neptune_y, neptune_radiusScale, neptune_colour, neptune_mass, neptune_orbital_period, neptune_name = c.execute("SELECT position.x, position.y, physical_properties.radiusscale, physical_properties.colour, physical_properties.mass, physical_properties.orbital_period, celestial_bodies.name FROM celestial_bodies JOIN position ON celestial_bodies.id = position.celestial_body_id JOIN physical_properties ON celestial_bodies.id = physical_properties.celestial_body_id WHERE celestial_bodies.name = 'Neptune'").fetchone()
    
    # Setting up planets objects
    sun = Planet(sun_x, sun_y, sun_radiusScale, colour_mapping[sun_colour], int(eval(sun_mass)), sun_orbital_period, sun_name)
    sun.sun = True

    mercury = Planet(mercury_x * Planet.AU, mercury_y, mercury_radiusScale, colour_mapping[mercury_colour], int(eval(mercury_mass)), mercury_orbital_period, mercury_name)
    mercury.y_vel = -47.4 * 1000

    venus = Planet(venus_x * Planet.AU, venus_y, venus_radiusScale, colour_mapping[venus_colour], int(eval(venus_mass)), venus_orbital_period, venus_name)
    venus.y_vel = -35.02 * 1000

    earth = Planet(earth_x * Planet.AU, earth_y, earth_radiusScale, colour_mapping[earth_colour], int(eval(earth_mass)), earth_orbital_period, earth_name)
    earth.y_vel = 29.783 * 1000 

    mars = Planet(mars_x * Planet.AU, mars_y, mars_radiusScale, colour_mapping[mars_colour], int(eval(mars_mass)), mars_orbital_period, mars_name)
    mars.y_vel = 24.077 * 1000

    jupiter = Planet(jupiter_x * Planet.AU, jupiter_y, jupiter_radiusScale, colour_mapping[jupiter_colour], int(eval(jupiter_mass)), jupiter_orbital_period, jupiter_name)
    jupiter.y_vel = -13.06 * 1000

    saturn = Planet(saturn_x * Planet.AU, saturn_y, saturn_radiusScale, colour_mapping[saturn_colour], int(eval(saturn_mass)), saturn_orbital_period, saturn_name)
    saturn.y_vel = -9.68 * 1000

    uranus = Planet(uranus_x * Planet.AU, uranus_y, uranus_radiusScale, colour_mapping[uranus_colour], int(eval(uranus_mass)), uranus_orbital_period, uranus_name)
    uranus.y_vel = -6.80 * 1000

    neptune = Planet(neptune_x * Planet.AU, neptune_y, neptune_radiusScale, colour_mapping[neptune_colour], int(eval(neptune_mass)), neptune_orbital_period, neptune_name)
    neptune.y_vel = -5.43 * 1000

    # Setting up lebron
    lebron_img = pygame.image.load('lebron.jpg')
    lebron_img = pygame.transform.scale(lebron_img, (120, 75))
    lebron_img = lebron_img.subsurface((20, 0, 80, 75))
    lebron_x, lebron_y, lebron_radiusScale, lebron_colour, lebron_mass, lebron_orbital_period, lebron_name = c.execute("SELECT position.x, position.y, physical_properties.radiusscale, physical_properties.colour, physical_properties.mass, physical_properties.orbital_period, celestial_bodies.name FROM celestial_bodies JOIN position ON celestial_bodies.id = position.celestial_body_id JOIN physical_properties ON celestial_bodies.id = physical_properties.celestial_body_id WHERE celestial_bodies.name = 'Lebron'").fetchone()
    lebron = Planet(lebron_x, lebron_y, lebron_radiusScale, colour_mapping[lebron_colour], int(eval(lebron_mass)), lebron_orbital_period, lebron_name, lebron_img)

    # Setting up list of planets
    planets = [sun, earth, mars, mercury, venus, jupiter, saturn, uranus, neptune ]
    #Selected planet is default to earth
    selected_planet = earth

    #Converts a position on the window to real universe coordinates
    def convert_to_real(pos):
        real_pos = Vector2(pos) - WIN_CENTRE
        real_pos.x /= Planet.SCALE
        real_pos.y /= -Planet.SCALE
        return real_pos
    
    #Render simulator information on the window
    def render_win_info():
        x, y = convert_to_real(pygame.mouse.get_pos())
        x_text = FONT.render(f"Position - x: {round(x // 1000):,}km", 1, colour_mapping['WHITE'])
        y_text = FONT.render(f"Position - y: {round(y // 1000):,}km", 1, colour_mapping['WHITE'])
        scale_text = FONT.render(f"Scale: km per pixel: {round(1 / Planet.SCALE) // 1000:,}km", 1, colour_mapping['WHITE'])
        dps = ((1/default) * clock.get_fps())
        fps_text = FONT.render(f"FPS: {round(float(clock.get_fps()), 4)}", 1, colour_mapping['WHITE'])
        time_scale_text = FONT.render(f"Time scale: {round(dps, 10)} days a second", 1, colour_mapping['WHITE'])
        author_text = FONT.render(f"Author: Ying Jin Liang", 1, colour_mapping['WHITE'])
        author_rect = author_text.get_rect(bottomright = (WIDTH - 5, HEIGHT - 5))

        WIN.blit(time_scale_text, (15, 15))
        WIN.blit(x_text, (15, 35))
        WIN.blit(y_text, (15, 55))
        WIN.blit(scale_text, (15, 75))
        WIN.blit(fps_text, (15, 95))
        WIN.blit(author_text, author_rect)

    #Render tips on the window
    def render_tips():
        tip1 = FONT.render("Show/Hide stars: S", 1, colour_mapping['WHITE'])
        tip2 = FONT.render("Select/Deselect planet: LMB/RMB", 1, colour_mapping['WHITE'])
        tip3 = FONT.render("Pause/Unpause: SPACE", 1, colour_mapping['WHITE'])
        tip4 = FONT.render("Show orbit: O", 1, colour_mapping['WHITE'])
        tip5 = FONT.render("Show/Hide distances: D", 1, colour_mapping['WHITE'])
        tip6 = FONT.render("Zoom +/- : UP/DOWN or Mouse Wheel", 1, colour_mapping['WHITE'])
        tip7 = FONT.render("Use mouse to adjust position", 1, colour_mapping['WHITE'])
        tip8 = FONT.render("Use slider to adjust time scale", 1, colour_mapping['WHITE'])
        tips = [tip1, tip2, tip3, tip4, tip5, tip6, tip7, tip8]

        # Calculates alignment and renders each tip
        for i, tip in enumerate(tips):
            displacement = (i+1) * 15
            WIN.blit(tip, (15, HEIGHT - tip.get_height() - displacement))

    #Generate random stars
    def generate_stars():
        WIDTH, HEIGHT = pygame.display.get_surface().get_size()
        stars = []
        for _ in range(WIDTH * HEIGHT // 10000):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            stars.append((x, y))

        return stars

    #Set up slider data
    slider_width = 200
    slider_height = 20
    slider_x = 15
    slider_y = 140
    slider_min = 1
    slider_max = 60
    slider_Dragging = False
    drag_offset = 0

    #Uses threads to draw orbits (faster for exe file)
    orbit_threads = [threading.Thread(target=planet.draw, args=(WIN,)) for planet in planets]
    for thread in orbit_threads:
        thread.start()

    # Generate random stars
    stars = generate_stars()

    #Main loop
    while run:
        # Initial setup
        clock.tick(60)
        WIN.fill(colour_mapping['BLACK'])
        WIDTH, HEIGHT = pygame.display.get_surface().get_size()
        
        #Draw slider
        pygame.draw.rect(WIN, colour_mapping['DARK_GREY'], (slider_x, slider_y, slider_width, slider_height))
        slider_percent = (default - slider_min) / (slider_max - slider_min)
        slider_fill_width = slider_percent * slider_width
        #Draw slider fill area
        pygame.draw.rect(WIN, colour_mapping['RED'], (slider_x, slider_y, slider_fill_width, slider_height))

        # Draw the exit button
        exit_button_rect = pygame.Rect(15, 175, 50, 20)
        exit_colour = colour_mapping['DARK_SPACE']
        pygame.draw.rect(WIN, exit_colour, exit_button_rect)
        text = FONT.render("Exit", True, colour_mapping['WHITE'])
        text_rect = text.get_rect(center=exit_button_rect.center)
        WIN.blit(text, text_rect)

        #Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Toggle pause/unpause if space is pressed
                    pause = not pause
                    Planet.pause = not Planet.pause
                    
                elif event.key == pygame.K_d:
                    # toggles details
                    details = not details

                elif event.key == pygame.K_o:
                    # toggles orbit paths
                    show_orbit = not show_orbit

                elif event.key == pygame.K_s:
                    # toggles stars
                    show_stars = not show_stars

                elif event.key == pygame.K_l:
                    # toggles easter egg
                    show_lebron = not show_lebron
                    selected_planet = sun
                    pygame.mixer.music.play()

            elif event.type == MOUSEBUTTONDOWN:
                #detects player scrolling up
                if event.button == 4:
                    for planet in planets:
                        Planet.SCALE += 1/Planet.AU  #Zoom in
                        Planet.EarthRadius += 0.05
                    planet.draw(WIN)

                elif event.button == 1:
                    #detects if player presses LMB
                    # returns to menu if player exits
                    if exit_button_rect.collidepoint(event.pos):
                        return 'menu'

                    # detects player clicking on slider
                    mouse_pos = pygame.mouse.get_pos()
                    if slider_x < mouse_pos[0] < slider_x + slider_width and slider_y < mouse_pos[1] < slider_y + slider_height:
                        slider_Dragging = True
                        drag_offset = mouse_pos[0] - slider_x -  slider_fill_width
                        break

                    # sets dragging flag to true and takes initial mouse position   
                    drag = True
                    drag_start = pygame.mouse.get_pos()
                    # detects if player clicks on a planet
                    for planet in planets:
                        x = planet.x * Planet.SCALE + WCENTRE
                        y = planet.y * Planet.SCALE + HCENTRE
                        planet_pos = Vector2(x, y)
                        if planet_pos.distance_to(pygame.mouse.get_pos()) < planet.radiusScale * Planet.EarthRadius * 2:
                            selected_planet = planet 
                            break
                # detects if player deslects planet
                elif event.button == 3:
                    for planet in planets:
                        x = planet.x * Planet.SCALE + WCENTRE
                        y = planet.y * Planet.SCALE + HCENTRE
                        planet_pos = Vector2(x, y)
                        if planet_pos.distance_to(pygame.mouse.get_pos()) < planet.radiusScale * Planet.EarthRadius * 2:
                            pass
                        else:
                            selected_planet = None

            # detects player scrolling down
            elif event.type == MOUSEBUTTONUP:
                if event.button == 5:
                    for planet in planets:
                        if Planet.SCALE <= 1.8401069518717394e-10:
                            continue
                        Planet.SCALE -= 1/Planet.AU #Zoom out
                        Planet.EarthRadius -= 0.05
                        planet.draw(WIN)

                # if player releases LMB, set dragging flag to false and reset initial mouse position
                elif event.button == 1:
                    slider_Dragging = False
                    drag = False
                    drag_start = None
            
            # Detects mouse motion
            elif event.type == MOUSEMOTION:
                
                #Whilst player is dragging their mouse and holding LMB...
                if drag:
                    # Calculate position of mouse relative to initial mouse position and adjust the centre of the window
                    WIN_CENTRE += Vector2(pygame.mouse.get_pos()) - drag_start
                    drag_start = pygame.mouse.get_pos()
                    WCENTRE, HCENTRE = WIN_CENTRE.x, WIN_CENTRE.y

                # if the player is dragging the slider...
                elif slider_Dragging:
                    # calculate offset
                    mouse_pos = pygame.mouse.get_pos()
                    slider_fill_width = mouse_pos[0] - slider_x - drag_offset
                    if slider_fill_width < 0:
                        slider_fill_width = 0
                    elif slider_fill_width > slider_width:
                        slider_fill_width = slider_width
                    # calculate new timestep
                    default = (slider_min + (slider_fill_width / slider_width) * (slider_max - slider_min))
                    Planet.TIMESTEP = 3600 * 24 / default

            # Detects window resizing, regenerates stars updates variables
            elif event.type == VIDEORESIZE:
                WIDTH, HEIGHT = pygame.display.get_surface().get_size()
                stars = generate_stars()

        # Calculates  new position of the planets and draws them
        for planet in planets:
            planet.update_position(planets)
            planet.draw(WIN)

        # only draws stars if they are enabled
        if show_stars:
            for star in stars:
                # random module is used to simulate shimmering stars
                pygame.draw.line(WIN, colour_mapping['WHITE'], (star[0], star[1]), (star[0] + random.randint(-1, 1), star[1] + random.randint(-1, 1)), 1) 
        
        # easter egg
        if show_lebron:
            lebron.lebron()
        else:
            pygame.mixer.music.pause()

        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[K_UP]:
            for planet in planets:
                
                Planet.SCALE += 1/Planet.AU  # Zoom in

                Planet.EarthRadius += 0.05
                planet.draw(WIN)
        elif keys_pressed[K_DOWN]:
            for planet in planets:
                if Planet.SCALE <= 1.8401069518717394e-10:
                     continue
                Planet.SCALE -= 1/Planet.AU  # Zoom out
                Planet.EarthRadius -= 0.05
                planet.draw(WIN)

        # Renders simulator information and tips
        render_win_info()
        render_tips()
        # Renders planet information for selected planet
        selected_planet.render_planet_info(WIN, sun) if selected_planet else None

        pygame.display.update()
    pygame.quit()
    conn.commit
    conn.close()
    
if __name__ == '__main__':
    main()