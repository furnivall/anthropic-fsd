import argparse
import subprocess
import sys
from langchain.chat_models import ChatAnthropic
from langchain.prompts.chat import (
    ChatPromptTemplate,
)


def infer_purpose(file_path, content):
    inference_template = """You are a world class software developer who reads in filename and file content. 
A user will pass in a file path, file content and you should
then infer what you believe the purpose of the file to be. 
Under no circumstances provide any other information. Give me your best attempt."""
    human_template = "***{filename}*** \n ***{file_content}***"
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", inference_template),
        ("human", human_template),
    ])
    chain = chat_prompt | ChatAnthropic(model="claude-2")
    input = {"filename": file_path, "file_content": content}
    return chain.invoke(input)




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
            initial_inference = infer_purpose(file_path, content)
            print(f"Initial inference: {initial_inference}")

            # For future development needs, stderr_output is stored in a variable
            # You can process stderr_output as needed here
            # This is where we could introduce our checks for other linked files


    except FileNotFoundError:
        print(f"The file {args.script} does not exist or is not a file.", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
