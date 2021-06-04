"""Module with main game objects."""
import math
import time
import pygame
import service


class SpaceObject(pygame.sprite.Sprite):
    """
    Abstract class.
    """

    def __init__(self, x, y, mass, img):
        super().__init__()
        self.image = img
        self.image.set_colorkey(service.colors["BLACK"])
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.ax = 1
        self.ay = 1
        self.vx = 0
        self.vy = 0
        self.fx = 0
        self.fy = 0
        self.mass = mass

    def draw(self):
        """Method draw objects."""
        service.screen.blit(self.image, self.rect.center)

    def reset_forses(self):
        """
        Method reset values of self.f{x, y} and self.a{x, y}.
        """
        self.fx = 0
        self.fy = 0
        self.ax = 1
        self.ay = 1

    def gravitational_force(self, other):
        """
        Method calculate gravitational interaction of two objects and change
        .ax, .ay of those objects.
        """
        k = 2000  # gravitational constant
        dx = self.rect.x - other.rect.x  # calculate the distance between object centres
        dy = self.rect.y - other.rect.y
        r = math.sqrt(dx ** 2 + dy ** 2)
        if r < 1:
            r = 1

        # calculate the equivalent for this pair
        f = (k * self.mass * other.mass) / (r ** 2)
        fx = f * dx / r
        fy = f * dy / r

        self.fx -= fx  # first object`s force
        self.fy -= fy
        other.fx += fx  # second object`s force in opposite direction
        other.fy += fy

        self.ax = self.fx / self.mass
        self.ay = self.fy / self.mass
        other.ax = other.fx / other.mass
        other.ay = other.fy / other.mass


class Planet(SpaceObject):
    """
    Сlass for visible game objects with own size, gravitation, color and location.
    """

    def __init__(self, x, y, condition, mass=30):
        if mass < 0:
            super().__init__(x, y, mass, service.repeling_planet_img)
        else:
            super().__init__(x, y, mass, service.open_planet_img)
        self.__condition = condition
        self.__satellites = pygame.sprite.Group()
        self.__time_open = None  # atr. used to change icon

    def draw(self):
        """Method draw objects."""
        service.screen.blit(self.image, (self.rect.x, self.rect.y))

    @property
    def condition(self):
        """Method return how many satellites left."""
        num = self.__condition - len(self.__satellites)
        if num <= 0:
            num = 0
        return num

    @property
    def satellites(self):
        """
        Return satellites of planet.
        """
        return self.__satellites

    def add_satellite(self, asteroid: 'Asteroid'):
        """Add asteroid as a satellite of planet."""
        if asteroid not in self.__satellites:
            self.__satellites.add(asteroid)

    def passed(self):
        """Method returns whether enough satellites are moving round the planet."""
        return self.condition == 0

    def pokemon_cached(self):
        """
        Method change icon of planet to close one.
        Pokemons are interpretation of asteroids.
        """
        if self.mass < 0:
            pass
        else:
            self.image = service.close_planet_img
            self.image.set_colorkey(service.colors["BLACK"])
        self.__time_open = time.time()

    def to_close_pokeball(self):
        """
        Method change icon of planet to open one,
        if enough time passed.
        Pokeballs are interpretation of planets.
        """
        time_to_open = 1
        if self.mass > 0 and self.__time_open and (time.time() - self.__time_open) > time_to_open:
            self.image = service.open_planet_img
            self.image.set_colorkey(service.colors["BLACK"])

            self.__time_open = None

    def update(self, *args):
        """
        Method of changing object coordinates(it is required to working with groups)
        Planets do not move, so implementation is trivial.
        """
        pass


class Asteroid(SpaceObject):
    """
    Сlass for visible game objects with own size, gravitation and color. It moves under the influence of planets
    and other asteroids gravitation. If asteroid collide with whatever planet it disappears.
    """

    def __init__(self, x: int, y: int, mass=10):
        self.color_name, self.color = service.random_color()
        super().__init__(x, y, mass, service.asteroid_image(self.color_name))
        self.end_of_line = 0
        self.__pos_count_angle = self.rect.center
        self.__nearest_planet = self.nearest_planet()
        self.__upper_left_point = list(self.rect.center)
        self.__lower_right_point = list(self.rect.center)

    def update(self):
        """Method of changing object coordinates. If object coordinates are out of screen,
        method remove this object."""
        self.__to_kill()
        dt = 1 / 9
        self.vx += self.ax
        self.vy += self.ay

        self.rect.x += self.vx * dt
        self.rect.y += self.vy * dt

    def starting_direction(self, end_of_line):
        """
        Method set line segment(that are moving from parameter: end_of_line to asteroid spot)
        as a vector of asteroid moving.
        """
        dt = 1 / 2
        self.vx = (self.rect.x - end_of_line[0]) * dt
        self.vy = (self.rect.y - end_of_line[1]) * dt

    def nearest_planet(self) -> Planet:
        """Method returns nearest to asteroid planet."""
        all_planets = list(service.all_planet)
        distance_to_planets = [
            (planet, math.sqrt((self.rect.x - planet.rect.x) ** 2 + (self.rect.y - planet.rect.y)
                               ** 2)) for planet in all_planets]  # [(planet, distance_to_it), ...]
        distance_to_planets.sort(reverse=False, key=lambda x: x[1])
        return distance_to_planets[0][0]

    def __find_extreme_points(self):
        """Method searching whether asteroid pos is most upper-left or lower-right."""
        if self.rect.x < self.__upper_left_point[0]:
            self.__upper_left_point[0] = self.rect.x
        if self.rect.x > self.__lower_right_point[0]:
            self.__lower_right_point[0] = self.rect.x
        if self.rect.y < self.__upper_left_point[1]:
            self.__upper_left_point[1] = self.rect.y
        if self.rect.y > self.__lower_right_point[1]:
            self.__lower_right_point[1] = self.rect.y

    def is_satellite_of(self) -> list:
        """
        Method check whether asteroid is a satellite of any planet.
        Return list of planets(whose satellite asteroid is).
        """
        list_of_planets = []
        cos = find_cos_angle(*self.__pos_count_angle, *self.__nearest_planet.rect.center,
                             *self.rect.center)
        self.__find_extreme_points()
        # some debug code

        # pygame.draw.circle(service.screen, service.colors["LIGHT_BLUE"], self.__lower_right_point, 4, 4)
        # pygame.draw.circle(service.screen, service.colors["PURPLE"], self.__upper_left_point, 4, 4)

        if cos < -0.999:
            list_of_planets = planets_in_rectangle(created_rect(self.__lower_right_point, self.__upper_left_point))
            # some debug code

            # pygame.draw.rect(service.screen, service.colors["LIGHT_BLUE"],
            # created_rect(self.__lower_right_point, self.__upper_left_point))
        return list_of_planets

    def __to_kill(self):
        """Method check whether object is out of screen. If it`s so it remove it."""
        if self.rect.x < 0 or self.rect.x > service.WIN_WIDTH:
            self.kill()
        if 0 > self.rect.y or self.rect.y > service.WIN_HEIGHT:
            self.kill()

    def draw_trajectory(self, end_of_line):
        """Method draw trajectory of asteroid movement."""
        AsteroidTrajectory(self, end_of_line).to_draw_traectory()


class AsteroidTrajectory(SpaceObject):
    """Class that help assteroid to draw trajectory of its movement."""

    def __init__(self, asteroid_copy: Asteroid, end_of_line):
        super().__init__(*asteroid_copy.rect.center, asteroid_copy.mass, asteroid_copy.image)
        self.color = asteroid_copy.color
        self.starting_direction(end_of_line)
        self.is_props = isinstance(asteroid_copy, Prop)

    def if_to_kill(self):
        """Method check whether trajectory if out of screen."""
        res = 0
        if self.rect.x < 0 or self.rect.x > service.WIN_WIDTH:
            res = 1
        if 0 > self.rect.y or self.rect.y > service.WIN_HEIGHT:
            res = 1
        if pygame.sprite.spritecollide(self, service.all_planet, dokill=False):
            res = 1
        return res

    def starting_direction(self, end_of_line):
        """
        Method set line segment(that are moving from parameter: end_of_line to asteroid spot)
        as a vector of asteroid moving.
        """
        dt = 1 / 2
        self.vx = (self.rect.x - end_of_line[0]) * dt
        self.vy = (self.rect.y - end_of_line[1]) * dt

    def update(self):
        """Method move trajectory point."""
        dt = 1 / 9
        self.vx += self.ax
        self.vy += self.ay

        self.rect.x += self.vx * dt
        self.rect.y += self.vy * dt

    def to_draw_traectory(self):
        """Method draw trajectory of asteroid movement"""
        if self.is_props:
            pass
        else:
            coordinate_list = [(self.rect.x + 18, self.rect.y + 18),
                               (self.rect.x + 19, self.rect.y + 19)]  # to prevent crashes
            service.all_objects.add(self)
            while not self.if_to_kill() and len(coordinate_list) < 200:
                coordinate_list.append(self.rect.center)
                move_with_gravity(service.all_objects)
                self.update()
            pygame.draw.aalines(service.screen, self.color, False, coordinate_list)
        self.kill()


class Prop(Asteroid):
    """Almost invisible game object, that imitate asteroid implementation."""

    def __init__(self, x, y):
        Asteroid.__init__(self, x, y)
        self.color = (255, 255, 255)
        self.image = service.prop_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        """It`s immovable obj. It`ll be killed just after its creation."""
        self.kill()

    def draw(self):
        """Method draw objects."""
        pass


def ask_satellites(asteroids: pygame.sprite.Group):
    """
    Function check whether asteroids are moving around of planets,
    if it`s so, add asteroid as a satellite of appropriate planet.
    """
    for asteroid in asteroids:
        planets = asteroid.is_satellite_of()
        for planet in planets:
            planet.add_satellite(asteroid)


def move_with_gravity(asteroids: pygame.sprite.Group):
    """
    Function takes tuple of planets(asteroids) calculate their gravitational
    interaction.
    """
    asteroids = tuple(asteroids)
    for asteroid in asteroids:
        asteroid.reset_forses()
    for asteroid_i in asteroids:
        for asteroid_j in asteroids:
            # In order for not to do the same action twice
            if asteroids.index(asteroid_i) < asteroids.index(asteroid_j):
                asteroid_i.gravitational_force(asteroid_j)


def is_collide(planet_group: pygame.sprite.Group, asteroid_group: pygame.sprite.Group):
    """
    Function check whether asteroid collides with planet. If it is so, it kill asteroid.
    And replace image of appropriate planet.
    """
    collided_planets = pygame.sprite.groupcollide(planet_group, asteroid_group, dokilla=False, dokillb=True)
    for planet in collided_planets.keys():
        if isinstance(planet, Planet):
            planet.pokemon_cached()


def find_cos_angle(ax, ay, bx, by, cx, cy):
    """Function returns cos of angle abc."""
    if ax == cx and ay == cy:
        cos_angle = 0
    else:
        ab = [bx - ax, by - ay]
        bc = [cx - bx, cy - by]
        a_b = ab[0] * bc[0] + ab[1] * bc[1]
        mod_ab = math.sqrt(ab[0] ** 2 + ab[1] ** 2)
        mod_bc = math.sqrt(bc[0] ** 2 + bc[1] ** 2)
        cos_angle = a_b / (mod_ab * mod_bc)
        # some debug code

        # pygame.draw.aaline(service.screen, service.colors["RED"], [ax, ay], [bx, by])
        # pygame.draw.aaline(service.screen, service.colors["RED"], [bx, by], [cx, cy])
    return cos_angle


def planets_in_rectangle(rect: pygame.Rect):
    """
    Method return list of planets in given rectangle.
    """
    all_planets = service.all_planet
    planet_in_rectangle = [planet for planet in all_planets if rect.collidepoint(*planet.rect.center)]
    return planet_in_rectangle


def created_rect(p_1: (tuple or list), p_2: (tuple or list)):
    """
    Function take upper-left and lower-right points(par: p_1, p_2), calculate width, height.
    Return created Rect(left, top, width, height).
    """
    width_ = math.fabs(p_1[0] - p_2[0])
    height_ = math.fabs(p_1[1] - p_2[1])
    # some debug code

    # rect = pygame.Rect(*p_2, width_, height_)
    # pygame.draw.rect(service.screen, service.colors["LIGHT_BLUE"], rect)
    return pygame.Rect(*p_2, width_, height_)


def to_animate_objects(group_of_obj: pygame.sprite.Group):
    """
    Method draw animated objects of given group.
    (par: group_of_obj).
    """
    for obj in group_of_obj:
        obj.draw()


def close_nessesary_pokeballs():
    """
    Function check whether pokeballs(interpretation of planets) are closed and open them
    if enough time has passed.
    """
    for planet in service.all_planet:
        planet.to_close_pokeball()


def lvl_completed():
    """
    Function check whether each planet has enough number of satellites.
    """
    return all([planet.passed() for planet in service.all_planet])
