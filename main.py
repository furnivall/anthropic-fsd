import argparse
import subprocess
import sys
import re
from pprint import pprint
from typing import List
import xml.etree.ElementTree as ET
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


def iterate_infer_purpose(inference, questions_and_answers):
    pass

def get_user_answers(questions):
    q_and_a = []
    for q in questions:
        pprint(q)
        a = input('Answer: ')
        if a: q_and_a.append([q, a])


def get_user_decision_on_inference(inference):
    pprint(f"Initial inference: {inference}")
    pprint("Do you agree with this inference? (y/n)")
    user_input = input()
    if user_input == 'Y':
        return inference
    elif user_input == 'N':
        iterate_user_input()
    # todo do some validation here - might as well make it True/False for type safety
    return user_input


def get_clarifying_questions(file_path, content, error_message):
    questions_template = """You are a world class software developer. I will send you a filename, file content, error_message, and purpose and you should then infer some clarifying questions which would help someone to understand the intent of the given project. Under no circumstances provide any other information. Give me your best attempt. Provide the questions individually in structured XML format. An example of this format is... ```<questions><question id="1"><text>Why is x data in csv format?</text></question><question id="2"><text>What are you expecting as an output?</text></question><question id="3"><text>How does this algorithm work?</text></question></questions>```. Use as few questions as possible and do not ask simplistic questions, like 'What are you building?'"""
    human_template = "***{filename}*** \n ***{file_content}*** \n ***{error_message}***"
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", questions_template),
        ("human", human_template),
    ])
    chain = chat_prompt | ChatAnthropic(model="claude-2")
    input = {
        "filename": file_path,
        "file_content": content,
        "error_message": error_message, 
    }
    question_str = chain.invoke(input).content
    root = ET.fromstring(question_str)
    # Extract each <text> value into list 
    questions = []
    for q in root.findall('./question/text'):
        questions.append(q.text)
    return questions


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
            pprint(f"Error code: {exit_code}")
            # initial_inference = infer_purpose(file_path, content)
            # get_user_decision_on_inference(initial_inference)

            purpose_inf = infer_purpose(
                file_path,
                content
            )
            pprint(f"Initial inference: \n{purpose_inf}")
 
            questions: List[str] = get_clarifying_questions(
                file_path,
                content,
                stderr_output,
            )
            
            q_and_a = get_user_answers(questions)
            
            breakpoint()        
                
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
