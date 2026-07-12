"""Interactive console entrypoint for the EchoCity demo.

Thin CLI shell around GameFactory + Shell. Contains no gameplay logic —
every game command is delegated to Shell.execute_line(). This script
only handles the terminal loop, banner, and its own 'help' text.
"""

from app.bootstrap.game_factory import GameFactory
from app.shell.shell import Shell

_BANNER = """\
=================================
        EchoCity Demo
=================================
Solve the mystery.
Explore the city.
Question NPCs.
Collect evidence.
Build your case.
Accuse the culprit.

Type 'help' for available commands.

Suggested first steps:

  ls
  cd cafe
  observe

Type 'exit' to quit.
"""

_HELP_TEXT = """\
Navigation
  ls
  tree
  pwd
  cd <location>

Investigation
  observe
  question <agent>
  collect <agent> <index>

Case
  case
  remove <index>
  clear

Court
  accuse <agent>
  submit

Other
  help
  exit
  quit"""

_EXIT_COMMANDS = {"exit", "quit"}


def main() -> None:
    """Build the game and run the interactive command loop."""
    game = GameFactory.build()

    print(_BANNER)
    print()
    print("Locations:")
    for location in game.location_manager.list_locations():
        print(f"  - {location.id}")
    print()

    try:
        _run_loop(game.shell)
    except KeyboardInterrupt:
        print("\nGoodbye.")


def _run_loop(shell: Shell) -> None:
    """Read, dispatch, and print commands until the player exits.

    Args:
        shell: The Shell instance to execute non-local commands through.
    """
    while True:
        line = input("> ").strip()
        if not line:
            continue

        command = line.split()[0].lower()

        if command in _EXIT_COMMANDS:
            print("Goodbye.")
            return

        if command == "help":
            print(_HELP_TEXT)
            continue

        print(shell.execute_line(line))


if __name__ == "__main__":
    main()