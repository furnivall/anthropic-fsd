import argparse
import subprocess
import sys
from langchain.chat_models import ChatAnthropic
from langchain.output_parsers import CommaSeparatedListOutputParser
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import AIMessage, HumanMessage, SystemMessage, BaseOutputParser

template = """You are a helpful assistant who reads in error messages and file content and returns
a potential solution to the error. A user will pass in a file path and an error message, and you should
use the file content to generate a solution to the error. ONLY return a solution, and nothing more."""
human_template = "***{filename}*** \n ***{error}*** \n ***{file_content}***"

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", template),
    ("human", human_template),
])




def run_script(file_path):
    process = subprocess.run(
        [sys.executable, file_path],
        capture_output=True,
        text=True
    )
    return process.returncode, process.stderr, file_path

def read_file_content(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    return content

def main():
    parser = argparse.ArgumentParser(description="Run a Python script and capture its exit code.")
    parser.add_argument('script', type=str, help="Path to the Python script to run.")
    args = parser.parse_args()

    try:
        exit_code, stderr_output, file_path = run_script(args.script)
        content = read_file_content(file_path)
        if exit_code != 0:
            print(f"Error code: {exit_code}")
            # For future development needs, stderr_output is stored in a variable
            # You can process stderr_output as needed here
            # This is where we could introduce our checks for other linked files

            chain = chat_prompt | ChatAnthropic
            print(chain.invoke({"filename": file_path, "error": stderr_output, "file_content": content}))
            print('Running chain')



    except FileNotFoundError:
        print(f"The file {args.script} does not exist or is not a file.", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()




# CLI - handle piped input


# Check for error code 1 on piped input
