"""Module with game buttons and messages."""
import pygame.sprite
import service


class Button(pygame.sprite.Sprite):
    """
    Abstract class for visible game objects, that case some change, when pressed.
    """

    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.image.set_colorkey(service.colors["BLACK"])
        self.rect = self.image.get_rect()
        self.rect.center = (float(x), float(y))
        self.is_last = False

    def is_pressed(self, pos: tuple):
        """
        Method check if pos in button rectangle.
        Param pos: mouse position or tuple of (x, y) coordinates.
        """
        return self.rect.collidepoint(pos)

    def draw(self):
        """Method draw objects."""
        service.screen.blit(self.image, (self.rect.x, self.rect.y))

    def to_act(self, pos):
        """
        Method define what happened if button is pressed.
        Par: pos define, where exactly button was pressed.
        (it`s not so important in most cases.)
        """
        pass


class StartingGameButton(Button):
    """Button that start first level."""

    def __init__(self, x, y):
        super().__init__(x, y, service.starting_game_button_img)

    def to_act(self, pos=(0, 0)):
        """Method start first level loop."""
        service.on_lvl = 'lvl_1'
        return True

    def draw(self):
        """Method draw objects."""
        service.screen.blit(self.image, (self.rect.x, self.rect.y))


class BackToMenuButton(Button):
    """Button that return game to main menu."""

    def __init__(self, x, y):
        super().__init__(x, y, service.back_to_menu_button_img)

    def to_act(self, pos=(0, 0)):
        """Method return game to main menu."""
        service.on_lvl = 'menu'
        return True


class NextLevelButton(Button):
    """Button that start next level."""

    def __init__(self, x, y):
        super().__init__(x, y, service.next_lvl_button_img)

    def to_act(self, pos=(0, 0)):
        """Method start next level."""
        service.on_lvl = "lvl_" + str(int(service.on_lvl[4:]) + 1)
        return True


class BackToCheckpointButton(Button):
    """Button that back game to last checkpoint."""

    def __init__(self, x, y):
        super().__init__(x, y, service.back_to_checkpoint_button_img)

    def to_act(self, pos=(0, 0)):
        """Method start last checkpoint level."""
        service.on_lvl = service.checkpoint
        return True


class HelpButton(Button):
    """Button that show player help message."""

    def __init__(self, x, y):
        super().__init__(x, y, service.help_button_img)

    def to_act(self, pos=(0, 0)):
        """
        Method add help message to lvl environment and set game setting the way
        almost all game process pause and help message appears.
        """
        for button in (help_message, next_page_button, previous_page_button):
            button.normalize_loc()
        service.all_buttons.add(help_message, next_page_button, previous_page_button)
        service.on_pause = True
        if not service.music_on_pause:
            sound_button.to_act()
        return True


class SoundButton(Button):
    """Button that interrupt or continue playing music."""

    def __init__(self, x, y):
        super().__init__(x, y, service.sound_off_button_img)

    def to_act(self, pos=(0, 0)):
        """
        Method interrupt or continue playing music.
        """
        if not service.music_on_pause:
            change_img(self, service.sound_on_button_img)
            service.music_on_pause = True
            pygame.mixer.music.pause()
        else:
            change_img(self, service.sound_off_button_img)
            service.music_on_pause = False
            pygame.mixer.music.unpause()
        return False


class Background(pygame.sprite.Sprite):
    """Game background image"""

    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = [0, 0]

    @property
    def image(self):
        """Returns background image."""
        return self.__image

    @image.setter
    def image(self, image):
        self.__image = service.set_background(image)


class Life(Button):
    """Visible game object, that show player`s attempts."""

    def __init__(self, x, y):
        super().__init__(x, y, service.life_img)


class Pointer(Button):
    """Visible game object, that disappears if help_button was pressed."""

    def __init__(self, x, y):
        super().__init__(x, y, service.pointer_img)
        self.shift = 10
        self.shifted = 1
        self.step = 1

    def shake(self):
        """Method change obj location a bit,
        to make a swing illusion."""
        if abs(self.shifted) > self.shift:
            self.step = -self.step
        self.rect.y += self.step
        self.shifted += self.step

    def draw(self):
        """Method shake and draw object."""
        self.shake()
        service.screen.blit(self.image, (self.rect.x, self.rect.y))


class HelpMessage(Button):
    """Game object that give player useful information."""

    def __init__(self, x, y):
        self.__current_page = service.help_pages_img[0]
        super().__init__(x, y, self.__current_page)

    def turn_to_next_page(self):
        """Method that change image onto next page image(if it exist)."""
        if service.help_pages_img.index(self.__current_page) == len(service.help_pages_img) - 1:
            pass
        else:
            self.__current_page = service.help_pages_img[service.help_pages_img.index(self.__current_page) + 1]
            change_img(self, self.__current_page)

    def turn_to_previous_page(self):
        """Method that change image onto previous page image(if it exist)."""
        if service.help_pages_img.index(self.__current_page) == 0:
            pass
        else:
            self.__current_page = service.help_pages_img[service.help_pages_img.index(self.__current_page) - 1]
            change_img(self, self.__current_page)

    def to_act(self, pos):
        """Method that close message and set game setting to
        continue game."""
        if next_page_button.is_pressed(pos) or previous_page_button.is_pressed(pos):
            pass
        else:
            if pointer_message in service.all_buttons:
                pointer_message.kill()
            service.all_buttons.remove(next_page_button, previous_page_button)
            service.on_pause = False
            service.all_buttons.remove(self)
            sound_button.to_act()
            return False  # it normalize still_on_lvl to True

    def normalize_loc(self):
        """Method move obj to right places of canvas
        after window resize."""
        self.rect.center = (service.WIN_WIDTH//2, service.WIN_HEIGHT//2)


class NextPageButton(Button):
    """Button that change help page onto next one."""
    def __init__(self, help_canvas: HelpMessage):
        x, y = help_canvas.rect.midbottom
        x += 48 + 30
        y -= 48 + 13
        super().__init__(x, y, service.next_page_pointer_img)
        self.__help_message = help_canvas

    def to_act(self, pos=(0, 0)):
        """Method that change help page onto next one."""
        self.__help_message.turn_to_next_page()

    def normalize_loc(self):
        """Method move obj to right places of canvas
        after window resize."""
        x, y = self.__help_message.rect.midbottom
        x += 48 + 30
        y -= 48 + 13
        self.rect.center = (x, y)


class PreviousPageButton(Button):
    """Button that change help page onto previous one."""
    def __init__(self, help_canvas: HelpMessage):
        x, y = help_canvas.rect.midbottom
        x -= 48 + 30
        y -= 48 + 13
        super().__init__(x, y, service.previous_page_pointer_img)
        self.__help_message = help_canvas

    def to_act(self, pos=(0, 0)):
        """Method that change help page onto previous one."""
        self.__help_message.turn_to_previous_page()

    def normalize_loc(self):
        """Method move obj to right places of canvas
        after window resize."""
        x, y = self.__help_message.rect.midbottom
        x -= 48 + 30
        y -= 48 + 13
        self.rect.center = (x, y)


class CheckpointSign(Button):
    """Visible game object, that signal: this lvl is checkpoint."""

    def __init__(self, x, y):
        super().__init__(x, y, service.checkpoint_img)


class SatellitesCounter(Button):
    """Visible game object, that show how many satellites left to set to given planet. """

    def __init__(self, planet):
        shift = free_space_near(*planet.rect.center, 50, 50)
        super().__init__(planet.rect.x + shift[0], planet.rect.y + shift[1], service.levels_img[0])
        self.__planet_connceted_with = planet

    def draw(self):
        """Method draw objects."""
        if self.__planet_connceted_with.condition == 0:
            pass
        else:
            change_img(self, service.levels_img[self.__planet_connceted_with.condition - 1])
            service.screen.blit(self.image, (self.rect.x, self.rect.y))


def change_img(obj: pygame.sprite.Sprite, img):
    """Function change image of object."""
    obj.image = img
    obj.image.set_colorkey(service.colors["BLACK"])


def free_space_near(x, y, wight, hight):
    """
    Fuction find free space(where rect with given wight, hight do not collide with other obj)
    near point(par: x, y). It returns coordinates of rect.center
    """
    shear = [0, 50, -50, 100, -100, 150, -150, 200, -200, 250, -250]
    shifts = ((i, j) for i in shear for j in shear)
    res = (0, -50)
    for shift in shifts:
        rect_ = pygame.sprite.Sprite()
        rect_.rect = pygame.Rect(x + shift[0], y + shift[1], wight, hight)
        if not (pygame.sprite.spritecollide(rect_, service.all_buttons, dokill=False) or
                pygame.sprite.spritecollide(rect_, service.all_planet, dokill=False) or
                pygame.sprite.spritecollide(rect_, service.all_lives_sprites, dokill=False)):
            res = shift
            break
    return res


# initialize almost all possible buttons
background = Background("loading_image")
next_lvl_button = NextLevelButton(service.WIN_WIDTH - 50, 50)
starting_game_button = StartingGameButton(service.WIN_WIDTH // 2, service.WIN_HEIGHT // 1.2)
back_to_menu_button = BackToMenuButton(50, 50)
back_to_checkpoint_button = BackToCheckpointButton(service.WIN_WIDTH // 2, service.WIN_HEIGHT // 1.2)
help_button = HelpButton(service.WIN_WIDTH - 130, 50)
sound_button = SoundButton(service.WIN_WIDTH - 260, 50)
help_message = HelpMessage(service.WIN_WIDTH // 2, service.WIN_HEIGHT // 2)
pointer_message = Pointer(service.WIN_WIDTH - 110, 230)
checkpoint_sign = CheckpointSign(service.WIN_WIDTH - 200, 40)
next_page_button = NextPageButton(help_message)
previous_page_button = PreviousPageButton(help_message)
