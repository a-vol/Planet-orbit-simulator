import pygame
from pygame.locals import *
import math
from pygame.math import Vector2

pygame.init()

WIDTH, HEIGHT = 800, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
WIN_CENTER = Vector2(WIDTH // 2, HEIGHT // 2)
WCENTER, HCENTER = WIN_CENTER

pygame.display.set_caption('Planet Simulation')

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

FONT = pygame.font.SysFont('arial', 16)
default = 30
details = False



class Planet:
    AU = 149.6e6 *1000
    G = 6.67428e-11
    SCALE = 250 / AU # 1AU = 100 pixels
    TIMESTEP = 3600*24/default  # days per frame
                                # 1 = 1 day per frame = 60 days per second
                                # 30 = 1/30th of a day per frame = 2 days per second
                                # 60 = 1/60th of a day per frame = 1 day per second
    

    EarthRadius = 16
    pause = False

    def __init__(self, x, y, radiusScale, color, mass, orbital_period, name):
        self.x = x
        self.y = y
        self.radiusScale = radiusScale
        self.color = color
        self.mass = mass
        self.orbital_period = orbital_period
        self.name = name

        self.orbit = []
        self.sun = False
        self.distance_to_sun = 0

        self.x_vel = 0
        self.y_vel = 0
    
    def draw(self, win):
        x = self.x * self.SCALE + WCENTER
        y = self.y * self.SCALE + HCENTER
        radius = self.radiusScale * self.EarthRadius


        if len(self.orbit) > 2:
            updated_points = []
            point_count = 0
            for point in self.orbit:
                x, y = point
                x = x * self.SCALE + WCENTER
                y = y * self.SCALE + HCENTER
                updated_points.append((x, y))
                point_count += 1
            if len(updated_points) > 2:
                pygame.draw.lines(WIN, self.color, False, updated_points, 1)
        pygame.draw.circle(win, self.color, (x, y), radius)

        if not self.sun and details:

            distance_text = FONT.render(f"{round(self.distance_to_sun/1000, 1)} km", 1, WHITE)
            WIN.blit(distance_text, (x - distance_text.get_width(), y - distance_text.get_height()))






    def attraction(self, other):
        other_x, other_y = other.x, other.y
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

        if other.sun:
            self.distance_to_sun = distance

        force = self.G * self.mass * other.mass / distance**2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x, force_y
    

    def update_position(self, planets):
        if Planet.pause:
            return
        total_fx = total_fy = 0
        for planet in planets:
            if self == planet:
                continue
            if self.sun:
                return 

            fx, fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy

        self.x_vel += total_fx / self.mass * self.TIMESTEP
        self.y_vel += total_fy / self.mass * self.TIMESTEP

        self.x += self.x_vel * self.TIMESTEP
        self.y += self.y_vel * self.TIMESTEP
        self.orbit.append((self.x, self.y))

    def render_planet_info(self, win, sun):

        name_text = FONT.render(f"Name: {self.name}", 1, self.color)
        mass_text = FONT.render(f"Mass: {self.mass:.5g} kg", 1, self.color)
        orbital_period_text = FONT.render(f"Orbital Period: {round(self.orbital_period, 2)} days", 1, self.color)
        distance_text = FONT.render(f"Distance from Sun: {round(self.distance_to_sun / 1000, 2):,} km", 1, self.color)
        velocity = math.sqrt(self.x_vel**2 + self.y_vel**2)
        vel_text = FONT.render(f"Velocity: {round(velocity / 1000, 2):,} km/s", 1, self.color)

        alignment = max(
            name_text.get_width(), mass_text.get_width(),
            orbital_period_text.get_width(), 
            distance_text.get_width(), vel_text.get_width()
        ) + 15
        WIN.blit(name_text, (WIDTH - alignment, 15))
        WIN.blit(mass_text, (WIDTH - alignment, 35))
        WIN.blit(orbital_period_text, (WIDTH - alignment, 55))
        WIN.blit(distance_text, (WIDTH - alignment, 75))
        WIN.blit(vel_text, (WIDTH - alignment, 95))

        x = self.x * self.SCALE + WCENTER
        y = self.y * self.SCALE + HCENTER
        planet_pos = x, y 
        sun_pos = WCENTER, HCENTER
        pygame.draw.lines( WIN, self.color, False, [sun_pos, planet_pos], 2)
        if not self.sun:
            distance_text = FONT.render(f"{round(self.distance_to_sun/1000, 1)} km", 1, WHITE)
            WIN.blit(distance_text, (x - distance_text.get_width(), y - distance_text.get_height()))
       





def main():
    global WIN_CENTER, WCENTER, HCENTER, WIDTH, HEIGHT, default, details
    run = True
    pause = False
    drag = False
    drag_start = False

    clock = pygame.time.Clock()

    

    

    sun = Planet(0, 0, 2, YELLOW, 1.98840 * 10**30, 0, 'Sun')
    sun.sun = True

    mercury = Planet(0.387 * Planet.AU, 0, 0.38, DARK_GREY, 3.3010 * 10**23, 87.969, 'Mercury')
    mercury.y_vel = -47.4 * 1000

    venus = Planet(0.723 * Planet.AU, 0, 0.95, WHITE, 4.8673 * 10**24, 224.701, 'Venus')
    venus.y_vel = -35.02 * 1000

    earth = Planet(-1 * Planet.AU, 0, 1, LIGHTBLUE, 5.9722 * 10**24, 365.2, 'Earth')
    earth.y_vel = 29.783 * 1000 

    mars = Planet(-1.524 * Planet.AU, 0, 0.53, RED, 6.4169 * 10**23, 686.98, 'Mars')
    mars.y_vel = 24.077 * 1000

    jupiter = Planet(5.203 * Planet.AU, 0, 1.8, PEARL_WHITE, 1.89813 * 10**27, 4332.59, 'Jupiter')
    jupiter.y_vel = 13.06 * 1000

    saturn = Planet(9.537 * Planet.AU, 0, 1.65, YELLOWISH_BROWN, 5.688 * 10**26, 10759.22, 'Saturn')
    saturn.y_vel = 9.68 * 1000

    uranus = Planet(19.191 * Planet.AU, 0, 1.35, AQUA, 8.6811 * 10**25, 30688.5, 'Uranus')
    uranus.y_vel = 6.80 * 1000

    neptune = Planet(30.069 * Planet.AU, 0, 1.25, NAVY, 1.02409 * 10**26, 60190.0, 'Neptune')
    neptune.y_vel = 5.43 * 1000

    planets = [sun, earth, mars, mercury, venus, jupiter, saturn, uranus, neptune]
    selected_planet = earth

    slider_width = 200
    slider_height = 20
    slider_x = 15
    slider_y = 140
    slider_min = 1
    slider_max = 60
    default = 30

    slider_Dragging = False
    drag_offset = 0

    def convert_to_real(pos):
        real_pos = Vector2(pos) - WIN_CENTER
        real_pos.x /= Planet.SCALE
        real_pos.y /= -Planet.SCALE
        return real_pos
    
    def render_win_info():
        x, y = convert_to_real(pygame.mouse.get_pos())
        x_text = FONT.render(f"Position - x: {round(x):,}km", 1, WHITE)
        y_text = FONT.render(f"Position - y: {round(y):,}km", 1, WHITE)
        scale_text = FONT.render(f"Scale: km per pixel: {round(1 / Planet.SCALE):,}km", 1, WHITE)
        dps = (1/default)*60
        fps_text = FONT.render(f"FPS: {round(float(clock.get_fps()), 4)}", 1, WHITE)
        time_scale_text = FONT.render(f"Time scale: {round(dps, 3)} days a second", 1, WHITE)
        author_text = FONT.render(f"Author: Alan Liang", 1, WHITE)
        author_rect = author_text.get_rect(bottomright = (WIDTH - 5, HEIGHT - 5))

        WIN.blit(time_scale_text, (15, 15))
        WIN.blit(x_text, (15, 35))
        WIN.blit(y_text, (15, 55))
        WIN.blit(scale_text, (15, 75))
        WIN.blit(fps_text, (15, 95))
        WIN.blit(author_text, author_rect)

    def render_tips():
        tips1 = FONT.render("Pause/Unpause: SPACE", 1, WHITE)
        tips2 = FONT.render("Show distances: D", 1, WHITE)
        tips3 = FONT.render("Zoom +/- : UP/DOWN or Mouse Wheel", 1, WHITE)
        tips4 = FONT.render("Use mouse to adjust position", 1, WHITE)
        tips5 = FONT.render("Use slider to adjust time scale", 1, WHITE)
        tips6 = FONT.render("Select/Deselect planet: LMB/RMB", 1, WHITE)
        
        WIN.blit(tips6, (15, HEIGHT - tips6.get_height() - 5))
        WIN.blit(tips5, (15, HEIGHT - tips5.get_height() - 25))
        WIN.blit(tips4, (15, HEIGHT - tips4.get_height() - 45))
        WIN.blit(tips3, (15, HEIGHT - tips3.get_height() - 65))
        WIN.blit(tips2, (15, HEIGHT - tips2.get_height() - 85))
        WIN.blit(tips1, (15, HEIGHT - tips1.get_height() - 105))




    

    while run:
        clock.tick(60)
        WIN.fill(BLACK)

        pygame.draw.rect(WIN, DARK_GREY, (slider_x, slider_y, slider_width, slider_height))
        slider_percent = (default - slider_min) / (slider_max - slider_min)
        slider_fill_width = slider_percent * slider_width

        pygame.draw.rect(WIN, RED, (slider_x, slider_y, slider_fill_width, slider_height))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pause = not pause
                    Planet.pause = not Planet.pause
                elif event.key == pygame.K_d:
                    details = not details

            


            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 4:
                    for planet in planets:
                        
                        Planet.SCALE += 1/Planet.AU  # Zoom in

                        Planet.EarthRadius += 0.05
                        planet.draw(WIN)
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if slider_x < mouse_pos[0] < slider_x + slider_width and slider_y < mouse_pos[1] < slider_y + slider_height:
                        slider_Dragging = True
                        drag_offset = mouse_pos[0] - slider_x -  slider_fill_width
                        break

                    drag = True
                    drag_start = pygame.mouse.get_pos()

                    for planet in planets:
                        x = planet.x * Planet.SCALE + WCENTER
                        y = planet.y * Planet.SCALE + HCENTER
                        planet_pos = Vector2(x, y)
                        if planet_pos.distance_to(pygame.mouse.get_pos()) < planet.radiusScale * Planet.EarthRadius * 2:
                            selected_planet = planet
 
                            break
                elif event.button == 3:
                    for planet in planets:
                        x = planet.x * Planet.SCALE + WCENTER
                        y = planet.y * Planet.SCALE + HCENTER
                        planet_pos = Vector2(x, y)
                        if planet_pos.distance_to(pygame.mouse.get_pos()) < planet.radiusScale * Planet.EarthRadius * 2:
                            pass
 
                        else:
                            selected_planet = None

            elif event.type == MOUSEBUTTONUP:
                if event.button == 5:
                    for planet in planets:
                        print (Planet.SCALE)
                        if Planet.SCALE <= 1.8401069518717394e-10:
                            continue
                        Planet.SCALE -= 1/Planet.AU  # Zoom out
                        Planet.EarthRadius -= 0.05
                        planet.draw(WIN)

                if event.button == 1:
                    slider_Dragging = False
                    drag = False
                    drag_start = None
                    
            elif event.type == MOUSEMOTION:

                if drag:
                    WIN_CENTER += Vector2(pygame.mouse.get_pos()) - drag_start
                    drag_start = pygame.mouse.get_pos()
                    WCENTER, HCENTER = WIN_CENTER.x, WIN_CENTER.y

                elif slider_Dragging:
                    mouse_pos = pygame.mouse.get_pos()
                    slider_fill_width = mouse_pos[0] - slider_x - drag_offset
                    if slider_fill_width < 0:
                        slider_fill_width = 0
                    elif slider_fill_width > slider_width:
                        slider_fill_width = slider_width
                    default = (slider_min + (slider_fill_width / slider_width) * (slider_max - slider_min))
                    Planet.TIMESTEP = 3600 * 24 / default




            elif event.type == VIDEORESIZE:
                WIDTH, HEIGHT = pygame.display.get_surface().get_size()



        for planet in planets:
            planet.update_position(planets)
            planet.draw(WIN)
        




        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[K_UP]:
            for planet in planets:
                
                Planet.SCALE += 1/Planet.AU  # Zoom in

                Planet.EarthRadius += 0.05
                planet.draw(WIN)
        elif keys_pressed[K_DOWN]:
            for planet in planets:
                print (Planet.SCALE)
                if Planet.SCALE <= 1.8401069518717394e-10:
                     continue
                Planet.SCALE -= 1/Planet.AU  # Zoom out
                Planet.EarthRadius -= 0.05
                planet.draw(WIN)

            

        render_win_info()
        render_tips()
        selected_planet.render_planet_info(WIN, sun) if selected_planet else None
        if not pause:
            pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    main()