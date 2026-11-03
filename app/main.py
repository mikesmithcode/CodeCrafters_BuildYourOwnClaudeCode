import argparse
import os
import sys

from app.ai import Conversation


def main():   
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()
    
    ai=Conversation(clear_cache=True)
    chat = ai.prompt(args)    
    

    
    


if __name__ == "__main__":
    main()