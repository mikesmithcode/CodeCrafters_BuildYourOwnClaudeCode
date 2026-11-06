import argparse
import os

from app.ai import Agent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", required=True, help="Prompt for the agent")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    # Set the environment variable so decorators can read it globally
    if args.debug:
        os.environ["DEBUG"] = "true"
    else:
        os.environ.get("DEBUG", "false") # or leave it unset

    agent = Agent(debug=args.debug)
    msg = agent.prompt(args)
    print(msg)

if __name__ == "__main__":
    main()