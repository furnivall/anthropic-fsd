# FSD - Friendly Script Doctor

FSD is your helpful assistant for fixing Python bugs and errors. It utilizes language models to understand your code's purpose, ask clarifying questions, and even suggest fixes!

## Key Features

- Analyzes your Python script and runs it
- Captures stderr if the script exits with error
- Infers your code's purpose through conversational prompts
- Asks clarifying questions if initial purpose guess is wrong
- Determines if it can suggest a fix with available info
- Provides context-aware fix suggestions in Python code

## Usage

- Clone repo
- `alias fsd python3 main.py`
- run `fsd <your file path>`

FSD requires Python 3.6+ and a LangChain installation.
FSD was created by Frederico Wieser, Danny Furnivall and Soumya Kundu for the Anthropic Hackathon in London in November 2023. 
