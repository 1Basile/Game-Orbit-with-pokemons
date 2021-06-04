"""Main game loop."""
import service
import level


def main():
    """Main game script."""
    service.set_window_header()
    while not service.game_done:
        exec(f"level.{service.on_lvl}.run()")


if __name__ == "__main__":
    main()
