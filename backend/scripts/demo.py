"""Interactive console entrypoint for the EchoCity demo.

Provides an immersive, guided CLI experience showing players how to navigate,
interrogate NPCs, collect evidence, and submit verdicts to the Court.
"""

import sys
import os
import argparse

# Add backend directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.bootstrap.game_factory import GameFactory
from app.shell.shell import Shell

_BANNER_LOGO = """
================================================================
 _____      _         _____ _ _       
|  ___|    | |       /  __ \ (_)      
| |__  ___| |__   ___| /  \/ |_ _   _ 
|  __|/ __| '_ \ / _ \ |   | | | | | |
| |___\__ \ | | | (_) | \__/\ | | |_| |
\____/|___/_| |_|\___/ \____/_|_|\__, |
                                  __/ |
                                 |___/ 
            AI CIVILIZATION RUNTIME - DEMO CONSOLE
================================================================
"""

def main() -> None:
    """Build the game and run the interactive command loop."""
    parser = argparse.ArgumentParser(description="EchoCity Interactive Demo Shell")
    parser.add_argument(
        "--prod",
        action="store_true",
        help="Run in production mode (connects to local SQLite database and Ollama AI engine)",
    )
    args = parser.parse_args()

    # Build the game graph
    game = GameFactory.build(demo=not args.prod)

    print(_BANNER_LOGO)
    
    if not args.prod:
        print("=" * 68)
        print("MODE: OFFLINE MOCK DEMO (No setup required)")
        print("MYSTERY: The Theft of Alice's Silver Necklace at the Cafe.")
        print("=" * 68)
        print("\nWALKTHROUGH FOR FIRST-TIME PLAYERS:")
        print("  1. Type 'cd cafe' to walk to the Cafe.")
        print("  2. Type 'observe' to see who is at the Cafe.")
        print("  3. Type 'question agent_3' (Carol) to interrogate the witness.")
        print("  4. Type 'collect agent_3 1' to extract Carol's witness clue.")
        print("  5. Type 'question agent_4' (Dave) to get corroborating hearsay evidence.")
        print("  6. Type 'collect agent_4 1' to extract Dave's hearsay clue.")
        print("  7. Type 'case' to inspect your compiled Case File.")
        print("  8. Type 'accuse agent_2' to point your finger at Bob.")
        print("  9. Type 'submit' to present the case and get the Court's verdict.")
        print("  10. Type 'court.exe' to stage the full courtroom trial dialogue.")
    else:
        print("=" * 68)
        print("MODE: PRODUCTION AI ENVIRONMENT")
        print("MYSTERY: The Theft of Victor's Silk fabric.")
        print("=" * 68)
        print("\nWALKTHROUGH FOR FIRST-TIME PLAYERS:")
        print("  1. Type 'cd cafe' and then 'observe' to list active NPCs.")
        print("  2. Type 'inspect sophia' (or question sophia) to interrogate Sophia Bennett.")
        print("  3. Type 'collect sophia 1' to harvest her testimony about Liam Carter.")
        print("  4. Type 'accuse liam' to identify Liam Carter as the suspect.")
        print("  5. Type 'submit' or run 'court.exe' to stage the trial and convict the suspect.")

    print("\nAvailable locations:")
    for location in game.location_manager.list_locations():
        print(f"  - {location.id} ({location.name})")
    print()
    print("Type 'help' to see command references, or 'exit' to quit.\n")

    try:
        _run_loop(game.shell)
    except KeyboardInterrupt:
        print("\nGoodbye.")


def _run_loop(shell: Shell) -> None:
    """Read, dispatch, and print commands until the player exits.

    Args:
        shell: The Shell instance to execute commands through.
    """
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break
            
        if not line:
            continue

        command = line.split()[0].lower()

        if command in {"exit", "quit"}:
            print("Goodbye.")
            return

        output = shell.execute_line(line)
        print(output)
        print()


if __name__ == "__main__":
    main()
