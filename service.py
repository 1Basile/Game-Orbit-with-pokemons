"""Service part of project"""
import os
import random
import pygame
from constants import *
from PIL import Image

# default windows size
WIN_WIDTH = 1200
WIN_HEIGHT = 800

screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT), pygame.RESIZABLE)
clock = pygame.time.Clock()


on_lvl = 'menu'
checkpoint = 'menu'
game_done = False
on_pause = False
to_interrupt_press = False
music_on_pause = False
lvl_number = 12

pygame.init()
pygame.mixer.init()
pygame.mixer.music.set_volume(0.015625)         # set default music volume


def resize_img(image):
    """Function resize an image, the way it fit window size. And save it in tmp file."""
    image = Image.open(image)
    new_image = image.resize((WIN_WIDTH, WIN_HEIGHT))
    new_image.save(os.path.join(img_folder, 'Backgrounds', f'tmp_bg_file.png'))


def set_background(image_name):
    """Function change background image. It returns Background obj with appropriate image."""
    resize_img(os.path.join(img_folder, 'Backgrounds', f'{image_name}.png'))  # background_2.png
    background_img = pygame.image.load(os.path.join(img_folder, 'Backgrounds', f'tmp_bg_file.png')).convert()
    return background_img


def delete_all_sprites():
    """It clean all planets and asteroids from level environment."""
    lvl_environment = [all_objects, all_planet, available_asteroids, all_buttons, all_lives_sprites, lvl_counters]
    for group in lvl_environment:
        group.empty()


game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'image')
music_folder = os.path.join(game_folder, 'music')

# loading images
sound_on_button_img = pygame.image.load(os.path.join(img_folder, 'Buttons', 'sound_on_button.png')).convert()
sound_off_button_img = pygame.image.load(os.path.join(img_folder, 'Buttons', 'sound_off_button.png')).convert()
open_planet_img = pygame.image.load(os.path.join(img_folder, 'Pokeballs', 'open_pokeball.png')).convert()
close_planet_img = pygame.image.load(os.path.join(img_folder, 'Pokeballs', 'close_pokeball.png')).convert()
repeling_planet_img = pygame.image.load(os.path.join(img_folder, 'Pokeballs', 'repeling_planet.png')).convert()
starting_game_button_img = pygame.image.load(os.path.join(img_folder, 'Buttons', 'starting_game_button.png')).convert()
next_lvl_button_img = pygame.image.load(os.path.join(img_folder, 'Buttons', 'next_lvl_button.png')).convert()
help_button_img = pygame.image.load(os.path.join(img_folder, 'Buttons', 'help_button.png')).convert()
back_to_menu_button_img = pygame.image.load(os.path.join(img_folder, 'Buttons', 'back_to_menu_button.png')).convert()
back_to_checkpoint_button_img = pygame.image.load(os.path.join(img_folder, 'Buttons',
                                                               'back_to_checkpoint_button.png')).convert()
life_img = pygame.image.load(os.path.join(img_folder, 'Buttons', 'pokecoin.png')).convert()
pointer_img = pygame.image.load(os.path.join(img_folder, 'Messages', 'pointer.png')).convert()
levels_img = [pygame.image.load(os.path.join(img_folder, 'Levels', f'{i}.png')).convert() for i in range(1, lvl_number)]
help_pages_img = [pygame.image.load(os.path.join(img_folder, 'Messages', f'{img}.png')).convert() for img in
                  help_massages]
prop_img = pygame.image.load(os.path.join(img_folder, 'Pokemons', f'prop.png')).convert()
checkpoint_img = pygame.image.load(os.path.join(img_folder, 'Messages', 'checkpoint.png')).convert()
next_page_pointer_img = pygame.image.load(os.path.join(img_folder, 'Buttons', 'next_help_page.png')).convert()
previous_page_pointer_img = pygame.image.load(os.path.join(img_folder, 'Buttons', 'previous_help_page.png')).convert()
icon_img = pygame.image.load(os.path.join(img_folder, 'Icons', 'crown.png'))

# lvl environment initialization
all_planet = pygame.sprite.Group()
all_objects = pygame.sprite.Group()
available_asteroids = pygame.sprite.Group()
unavailable_asteroids = pygame.sprite.Group()
all_buttons = pygame.sprite.Group()
all_lives_sprites = pygame.sprite.Group()
lvl_counters = pygame.sprite.Group()


def random_color():
    """Function give you random color (in range of colors in constants.py)."""
    # using function filed to not to repeat colors up to they end
    if not hasattr(random_color, '__colors') or random_color.__colors == []:
        random_color.__colors = list(colors.keys())
    color_name = random.choice(random_color.__colors)
    color = colors[color_name]
    random_color.__colors.remove(color_name)
    return color_name, color


def random_crash_eff():
    """Function give you random song (in range of crash_eff in constants.py)."""
    # using function filed to not to repeat crash effect up to they end
    if not hasattr(random_crash_eff, '__effects') or random_crash_eff.__effects == []:
        random_crash_eff.__effects = list(crash_lib)
    song_name = random.choice(random_crash_eff.__effects)
    random_crash_eff.__effects.remove(song_name)
    return song_name


def random_song():
    """Function give you random song (in range of music_lib in constants.py)."""
    # using function filed to not to repeat song up to they end
    if not hasattr(random_song, '__song') or random_song.__song == []:
        random_song.__song = list(music_lib)
    song_name = random.choice(random_song.__song)
    random_song.__song.remove(song_name)
    return song_name


def play_song(song):
    """Function start to play given song."""
    pygame.mixer.music.load(os.path.join(music_folder, f'{song}.wav'))
    pygame.mixer.music.play()


def fill_music_queue():
    """Function fill music queue and start it."""
    pygame.mixer.music.load(os.path.join(music_folder, f'{random_song()}.wav'))
    for _ in music_lib:
        pygame.mixer.music.queue(os.path.join(music_folder, f'{random_song()}.wav'))
    pygame.mixer_music.play(-1)


def asteroid_image(color):
    """Function give you a random img of asteroid with appropriate param: color."""
    img_name = random.choice(asteroids_by_color[color])
    asteroid_img = pygame.image.load(os.path.join(img_folder, 'Pokemons', f'{img_name}.png'))
    return asteroid_img


def set_window_header():
    """Method set icon and caption of a game window."""
    pygame.display.set_caption("Asteroids")
    icon_img.set_colorkey(colors["BLACK"])
    pygame.display.set_icon(icon_img)
