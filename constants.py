"""Constants of the game"""
FPS = 60
colors = {"BLACK": (0, 0, 0), "GRAY": (125, 125, 125), "LIGHT_BLUE": (64, 128, 255),
          "GREEN": (0, 200, 64), "YELLOW": (225, 225, 0), "PINK": (230, 50, 230), "ORANGE": (255, 150, 100),
          'PURPLE': (125, 38, 205, 255), "RED": (255, 0, 0, 255)}
asteroids_by_color = {"BLACK": ("musicbee",),
                      "GRAY": ("eevee", "pidgey"),
                      "LIGHT_BLUE": ("squirtle", "zubat", "dratini", "snorlax"),
                      "GREEN": ("bullbasaur", "caterpie", "incense"),
                      "YELLOW": ("bellsprout", "meowth", "pikachu"),
                      "PINK": ("jigglypuff", "mew", "mankey"),
                      "ORANGE": ("charmander", "abra", "psyduck", "weedle"),
                      "PURPLE": ("rattata", "venonat"),
                      "RED": ("desura",)}

music_lib = ('music_1', 'music_2', 'music_3', 'music_4')
crash_lib = ('smb_gameover', 'smb_mariodie', 'smb_warning')
winning_lib = ('smb_world_clear', 'smb_stage_clear')
help_massages = ('help_message_1', 'help_message_2', 'help_message_3')