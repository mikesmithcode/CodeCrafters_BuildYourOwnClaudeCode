import argparse

from app.ai import Agent


def main(debug=False):   
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()
    
    ai=Agent(debug=debug)
    ai.prompt(args)    
    

    
    


if __name__ == "__main__":
    debug=False
    main(debug)