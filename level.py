"""Module with levels implementation."""
from pygame.locals import *
from service import *
from planets import *
from buttons import *
from sys import exit


class Level:
    """Class that include background image, number and location of planets and asteroids."""

    def __init__(self, background_, planets: dict, asteroids: dict, buttons: dict, lives: int,
                 is_checkpoint='', last_one=False, special_music=None, asteroid_to_create=True, special=False):
        self.is_last = last_one
        self.is_checkpoint = is_checkpoint
        self.not_allowed_to_cr_aster = not asteroid_to_create
        self.background = background_
        self.planets = []
        self.asteroids = []
        self.buttons = pygame.sprite.Group()
        self.buttons_name = tuple(buttons.values())
        self.lives = pygame.sprite.Group()
        self.force_vectors = {}
        self.special_music = special_music
        self.special_lvl = special
        i = 0
        x = 100
        y = WIN_HEIGHT - 50
        for elem in range(lives):
            self.lives.add(Life(x, y))
            x += 52
        for settings in planets.values():
            self.planets.append(f"Planet(**{settings})")
        for location, force_vect in asteroids.values():
            self.asteroids.append(f"Asteroid({location[0]}, {location[1]})")
            self.force_vectors.update({i: f"{force_vect}"})
            i += 1
        for button in buttons.values():
            self.buttons.add(button)
        if self.is_checkpoint:
            self.buttons.add(checkpoint_sign)

    def get_settings(self):
        """
        Method set level environment (changed background and set planets buttons and asteroids).
        And clear event list.
        """
        service.delete_all_sprites()
        pygame.event.clear()
        if self.is_checkpoint:
            service.checkpoint = self.is_checkpoint
        for planet in self.planets:
            planet_ = eval(planet)
            service.all_planet.add(planet_)
            service.all_objects.add(planet_)
            service.lvl_counters.add(SatellitesCounter(planet_))  #
        for i in range(len(self.asteroids)):
            asteroid = eval(self.asteroids[i])
            asteroid.starting_direction([float(i) for i in self.force_vectors[i][1:-1].split(", ")])
            service.all_objects.add(asteroid)  # to convert '(123, 321)' to [123, 321]
            service.available_asteroids.add(asteroid)
        for button in self.buttons:
            service.all_buttons.add(button)
        for life in self.lives:
            service.all_lives_sprites.add(life)
        background.image = self.background
        if not service.music_on_pause:
            if self.special_music == -1:
                play_song(random_crash_eff())
            elif self.special_music == 1:
                play_song(winning_lib[0])
            else:
                fill_music_queue()
        self.normalize()
        service.lvl_done = False
        service.to_interrupt_press = True

    def normalize(self):
        """Method move all appropriate obj to right places,
        after window resize."""
        buttons_loc = {next_lvl_button: 'service.WIN_WIDTH - 50, 50',
                       starting_game_button: 'service.WIN_WIDTH // 2, service.WIN_HEIGHT // 1.2',
                       back_to_menu_button: '50, 50',
                       back_to_checkpoint_button: 'service.WIN_WIDTH // 2, service.WIN_HEIGHT // 1.2',
                       help_button: 'service.WIN_WIDTH - 130, 50',
                       sound_button: 'service.WIN_WIDTH - 260, 50',
                       help_message: 'service.WIN_WIDTH // 2, service.WIN_HEIGHT // 2',
                       pointer_message: 'service.WIN_WIDTH - 110, 230',
                       checkpoint_sign: 'service.WIN_WIDTH - 200, 40'}

        for button in all_buttons:
            if not isinstance(button, (NextPageButton, PreviousPageButton)):
                button.rect.center = (eval(buttons_loc[button]))

        next_page_button.normalize_loc()
        previous_page_button.normalize_loc()

        x = 100
        y = service.WIN_HEIGHT - 50
        for life in self.lives:
            life.rect.center = (x, y)
            x += 52

    @staticmethod
    def game_over():
        """Function that ."""
        service.on_lvl = "game_over_lvl"

    def run(self):
        """Method set lvl environment, start level loop and serves it.."""
        still_in_lvl = True
        to_start_special_sound = True
        not_to_remove_life = False

        # set lvl environment
        self.get_settings()
        asteroid = Asteroid(starting_game_button.rect.center[0], WIN_HEIGHT + 50)  # to prevent crashes

        # lvl loop
        while still_in_lvl or service.on_pause:
            clock.tick(FPS)
            screen.fill(colors["BLACK"])
            screen.blit(background.image, background.rect)
            button_pressed = all_buttons.has(help_message)

            # define mouse position
            pos = pygame.mouse.get_pos()
            if service.to_interrupt_press:
                pressed = (0, 0, 0)
                service.to_interrupt_press = False
            else:
                pressed = pygame.mouse.get_pressed()

            # start to play music
            if not pygame.mixer.music.get_busy():
                fill_music_queue()

            for event in pygame.event.get():

                if event.type == QUIT:
                    pygame.quit()
                    exit()

                if event.type == VIDEORESIZE:
                    service.WIN_WIDTH, service.WIN_HEIGHT = event.size
                    service.screen = pygame.display.set_mode((service.WIN_WIDTH, service.WIN_HEIGHT), pygame.RESIZABLE)
                    background.image = self.background
                    self.normalize()

                for button in all_buttons:
                    if event.type == MOUSEBUTTONDOWN and event.button == 1 and button.is_pressed(pos):
                        still_in_lvl = not button.to_act(pos)  # depends on button
                        button_pressed = True
                        not_to_remove_life = True
                        asteroid = Prop(*pos)

                # creating asteroid if needed
                if not button_pressed and event.type == MOUSEBUTTONDOWN and event.button == 1:
                    if self.not_allowed_to_cr_aster:
                        asteroid = Prop(*pos)
                    else:
                        asteroid = Asteroid(*pos)
                    unavailable_asteroids.add(asteroid)

                if not button_pressed and event.type == MOUSEBUTTONUP and event.button == 1:
                    if self.special_lvl:
                        pass
                    elif not_to_remove_life or remove_life():  # no life`s left
                        self.game_over()
                        still_in_lvl = False
                    not_to_remove_life = False
                    asteroid.starting_direction(pos)
                    available_asteroids.add(asteroid)
                    all_objects.add(asteroid)
                    unavailable_asteroids.remove(asteroid)

                # changing music volume
                if not button_pressed and event.type == MOUSEBUTTONDOWN and event.button == 4:
                    pygame.mixer.music.set_volume(pygame.mixer.music.get_volume() + 0.01)
                elif not button_pressed and event.type == MOUSEBUTTONDOWN and event.button == 5:
                    pygame.mixer.music.set_volume(pygame.mixer.music.get_volume() - 0.01)

            # drawing asteroid force vector if needed
            if not button_pressed and pressed[0]:
                screen.fill(colors["BLACK"])
                all_objects.draw(screen)
                screen.blit(background.image, background.rect)

                pygame.draw.aaline(screen, asteroid.color, asteroid.rect.center, pos)
                pygame.draw.circle(screen, asteroid.color, pos, 3)
                asteroid.draw_trajectory(pos)

            # check whether lvl is complete
            if not button_pressed and lvl_completed():
                if self.is_last:
                    service.on_lvl = 'win_lvl'
                    still_in_lvl = False
                elif service.on_lvl == 'menu':
                    pass
                else:
                    all_buttons.add(next_lvl_button)
                    self.normalize()
                    if to_start_special_sound:
                        play_song(winning_lib[1])
                        to_start_special_sound = False

            # moving asteroids and check collisions
            if not button_pressed:
                move_with_gravity(all_objects)
                ask_satellites(available_asteroids)
                available_asteroids.update()
                close_nessesary_pokeballs()
                is_collide(all_planet, available_asteroids)

            # drawing lvl environment
            unavailable_asteroids.draw(screen)
            all_lives_sprites.draw(screen)
            all_planet.draw(screen)
            to_animate_objects(all_buttons)
            to_animate_objects(lvl_counters)
            available_asteroids.draw(screen)
            all_buttons.draw(screen)
            pygame.display.flip()


def remove_life():
    """
    Function decrees number of your attempts to pass lvl and return True.
    If attempts end return True.
    """
    if len(service.all_lives_sprites.sprites()) == 0:
        return True
    else:
        service.all_lives_sprites.remove(service.all_lives_sprites.sprites()[-1])
        return False


# levels initializing
menu = Level(background_="starting_menu_background",
             planets={1: {'x': service.WIN_WIDTH // 5.21, 'y': service.WIN_HEIGHT // 4.3, 'condition': 1}},
             asteroids={1: ((service.WIN_WIDTH // 10.4347, service.WIN_HEIGHT // 4.14507),
                            (service.WIN_WIDTH // 11.320754, service.WIN_HEIGHT // 2.64900))},
             buttons={1: starting_game_button, 2: help_button, 3: sound_button, 4: pointer_message},
             lives=0, special=True)

lvl_1 = Level(background_="background_1",
              planets={1: {'x': service.WIN_WIDTH // 2, 'y': service.WIN_HEIGHT // 2, 'condition': 2}},
              asteroids={1: ((service.WIN_WIDTH // 2, service.WIN_WIDTH // 2),  # i know
                             (service.WIN_WIDTH // 2 - 135, service.WIN_HEIGHT // 2 + 134))},
              buttons={1: back_to_menu_button, 2: help_button, 3: sound_button},
              lives=6,
              is_checkpoint='lvl_1')

lvl_2 = Level(background_="background_2",
              planets={1: {'x': service.WIN_WIDTH // 2 - 200, "y": service.WIN_HEIGHT // 2, 'condition': 1},
                       2: {'x': service.WIN_WIDTH // 2 + 200, "y": service.WIN_HEIGHT // 2, 'condition': 1}},
              asteroids={},
              buttons={1: back_to_menu_button, 2: help_button, 3: sound_button},
              lives=4)

lvl_3 = Level(background_="background_3",
              planets={1: {'x': service.WIN_WIDTH // 2 - 50, "y": service.WIN_HEIGHT // 2 - 50, 'condition': 1},
                       2: {'x': service.WIN_WIDTH // 2 + 50, "y": service.WIN_HEIGHT // 2 - 50, 'condition': 1},
                       3: {'x': service.WIN_WIDTH // 2 + 50, "y": service.WIN_HEIGHT // 2 + 50, 'condition': 1},
                       4: {'x': service.WIN_WIDTH // 2 - 50, "y": service.WIN_HEIGHT // 2 + 50, 'condition': 1}},
              asteroids={1: ((service.WIN_WIDTH // 2, service.WIN_WIDTH // 2),  # i know
                             (service.WIN_WIDTH // 2 - 135, service.WIN_HEIGHT // 2 + 134))},
              buttons={1: back_to_menu_button, 2: help_button, 3: sound_button},
              lives=6,
              is_checkpoint='lvl_3')

lvl_4 = Level(background_="background_4",
              planets={1: {'x': service.WIN_WIDTH // 2 - 200, "y": service.WIN_HEIGHT // 2 - 200, 'condition': 0,
                           'mass': -10},
                       2: {'x': service.WIN_WIDTH // 2 + 200, "y": service.WIN_HEIGHT // 2 - 200, 'condition': 0,
                           'mass': -10},
                       3: {'x': service.WIN_WIDTH // 2 + 200, "y": service.WIN_HEIGHT // 2 + 200, 'condition': 0,
                           'mass': -10},
                       4: {'x': service.WIN_WIDTH // 2 - 200, "y": service.WIN_HEIGHT // 2 + 200, 'condition': 0,
                           'mass': -10},
                       5: {'x': service.WIN_WIDTH // 2 - 200, "y": service.WIN_HEIGHT // 2, 'condition': 0,
                           'mass': -10},
                       6: {'x': service.WIN_WIDTH // 2 + 200, "y": service.WIN_HEIGHT // 2, 'condition': 0,
                           'mass': -10},
                       7: {'x': service.WIN_WIDTH // 2, "y": service.WIN_HEIGHT // 2 + 200, 'condition': 0,
                           'mass': -10},
                       8: {'x': service.WIN_WIDTH // 2, "y": service.WIN_HEIGHT // 2 - 200, 'condition': 0,
                           'mass': -10},
                       9: {'x': service.WIN_WIDTH // 2, "y": service.WIN_HEIGHT // 2, 'condition': 1,
                           'mass': 1}},

              asteroids={},
              buttons={1: back_to_menu_button, 2: help_button, 3: sound_button},
              lives=4,
              last_one=True)

game_over_lvl = Level(background_="game_over_background",
                      planets={1: {'x': service.WIN_WIDTH // 2, "y": service.WIN_HEIGHT // 0.2, 'condition': 0}},
                      asteroids={},
                      buttons={1: back_to_menu_button, 2: back_to_checkpoint_button, 3: help_button, 4: sound_button},
                      lives=0, special_music=-1, asteroid_to_create=False, special=True)

win_lvl = Level(background_="winning_background",
                planets={1: {'x': service.WIN_WIDTH // 2, "y": service.WIN_HEIGHT // 0.2, 'condition': 0}},
                asteroids={},
                buttons={1: back_to_menu_button, 3: help_button, 4: sound_button},
                lives=0, special_music=1, asteroid_to_create=False, special=True)
