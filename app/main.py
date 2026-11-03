import argparse

from app.ai import Agent


def main():   
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()
    
    ai=Agent()
    ai.prompt(args)    
    

    
    


if __name__ == "__main__":
    main()