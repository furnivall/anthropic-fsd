import argparse
import subprocess
import sys
import re
from pprint import pprint
from typing import List
import xml.etree.ElementTree as ET
from langchain.chat_models import ChatAnthropic
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter
from langchain.prompts.chat import ChatPromptTemplate


def infer_purpose(file_path, content):
    inference_template = """
    You are a world class software developer. 
    I am going to send in a filename of a python file and the file's content. 
    I want you to then infer what you believe the developer's overall intentions for the file's purpose.
    You must ONLY return your assessment of the developer's intentions at a high level. 
    You must not mention any mistakes or flaws or criticise the code in any way. 
    Use the heading 'Purpose' to indicate your answer.
    Give me your best attempt.
    """
    
    human_template = "***{filename}*** \n ***{file_content}***"
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", inference_template),
        ("human", human_template),
    ])
    chain = chat_prompt | ChatAnthropic(model="claude-2", temperature=0)
    input = {"filename": file_path, "file_content": content}
    return chain.invoke(input)


def infer_purpose_w_questions(file_path, content, q_and_a: List):
    inference_template = """
    You are a world class software developer. 
    I am going to send in a filename of a python file and the file's content. 
    I want you to then infer what you believe the developer's overall intentions for the file's purpose.
    You must ONLY return your assessment of the developer's intentions at a high level. 
    You must not mention any mistakes or flaws or criticise the code in any way. 
    Use the heading 'Purpose' to indicate your answer.
    Give me your best attempt.
    """
    
    human_template = "***Filename:*** {filename} \n ***File Content:*** {file_content} \n"
    
    for i, q in enumerate(q_and_a):
        human_template = f"{human_template} ***Question_{i+1}:*** {q[0]} \n ***Answer_{i+1}:*** {q[1]} \n"
    
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", inference_template),
        ("human", human_template),
    ])
    chain = chat_prompt | ChatAnthropic(model="claude-2", temperature=0)
    input = {"filename": file_path, "file_content": content}
    return chain.invoke(input)


def get_user_answers(questions):
    q_and_a = []
    for q in questions:
        print(f"Question: {q}")
        a = input('Answer: ')
        if a: q_and_a.append([q, a])
    return q_and_a


def get_user_decision_on_inference(inference, file_path, content):
    user_input = 'fuck you claude'
    print(inference.content)
    while user_input not in ['y', 'n']:
        user_input = input("Do you agree with this inference? (y/n)").lower()
    if user_input == 'y':
        return inference
    else:
        questions: List[str] = get_clarifying_questions(
            file_path,
            content,
            inference,
        )
        q_and_a = get_user_answers(questions)
        new_inference = infer_purpose_w_questions(file_path, content, q_and_a)
        return get_user_decision_on_inference(new_inference, file_path, content)


def get_clarifying_questions(file_path, content, inference):
    print("Understood. I'm now generating some questions to clarify the inference of the purpose.")
    questions_template = """You are a world class software developer. 
    I will send you a filename, file content, and purpose. 
    You should then infer some clarifying questions which would help someone to understand the intent of the given project. 
    Under no circumstances provide any other information. Give me your best attempt. 
    Provide the questions individually in structured XML format. 
    An example of this format is... 
    ```
    <questions><question id="1">
    <text>Why is x data in csv format?</text>
    </question>
    <question id="2"><text>What are you expecting as an output?</text></question>
    <question id="3"><text>How does this algorithm work?</text></question></questions>```. 
    Use as few questions as possible and do not ask simplistic questions, like 'What are you building?'"""
    human_template = "***{filename}*** \n ***{file_content}*** \n ***{purpose}***"
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", questions_template),
        ("human", human_template),
    ])
    chain = chat_prompt | ChatAnthropic(model="claude-2")
    input = {
        "filename": file_path,
        "file_content": content,
        "purpose": inference,
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


def can_you_fix(file_path, content, error_message, purpose):
    solvability_template = """
    You are a world-class software developer. I am planning to send you the following information:
    1. A piece of python code
    2. The full stderror content produced by running the code
    3. The developer's confirmed intent for the given output.
    4. Filename of the python code
    Consider whether you are able to provide a solution that resolves the error with only the information contained above.
    Important: You must ONLY respond with either the integers 1 or 0. 1 means you can fix the error, 0 means you cannot.
    Provide the questions individually in structured XML format. 
        An example of this format is... 
        ```<bool>1</bool>```
    """
    human_template = "***{filename}*** \n ***{file_content}*** \n ***{error_message}*** \n ***{purpose}***"
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", solvability_template),
        ("human", human_template),
    ])
    chain = chat_prompt | ChatAnthropic(model="claude-2", temperature=0)
    our_data = {"filename": file_path, "file_content": content, "error_message": error_message, "purpose": purpose}
    bool_regex = r"<bool>(0|1)</bool>"
    llm_output = ""
    while llm_output not in ["0", "1"]:
        llm_output = chain.invoke(our_data).content
        llm_output = re.findall(bool_regex, llm_output)[0]
    return int(llm_output)


def get_fix_code(file_path, content, error_message, purpose):
    solvability_template = """
    You are a world-class software developer who only responds in code and not english. I will send you the following information:
    1. A piece of python code
    2. The full error trace content produced by running the code
    3. The developer's confirmed intent for the given output.
    4. Filename of the python code

    Return a python code that fixes the error below. don't include any explanations in your responses.

    Assistant: {{list code in markdown}}
    """
    human_template = "Filename: ***{filename}*** \n File Content: ***{file_content}*** \n Error Message: ***{error_message}*** \n Purpose: ***{purpose}***"
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", solvability_template),
        ("human", human_template),
    ])
    chain = chat_prompt | ChatAnthropic(model="claude-2", temperature=0, max_tokens=100000)
    our_data = {"filename": file_path, "file_content": content, "error_message": error_message, "purpose": purpose}
    llm_output = chain.invoke(our_data).content
    return llm_output

def extract_code_from_markdown(markdown_text):
    # Regex to find fenced code blocks
    code_blocks = re.findall(r'```(?:.*\n)?((?:.|\n)*?)```', markdown_text + ' ``` ')
    if len(code_blocks) == 0:
        return markdown_text
    return code_blocks[0]

def diff(new_file, old_file, intent):
    inference_template = """
    You are a world class software developer. 
    Explian the difference between the two python files based on the intention of building them.
    """
    
    human_template = "***{new_file}*** \n ***{old_file}*** \n ***{intent}***"
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", inference_template),
        ("human", human_template),
    ])
    chain = chat_prompt | ChatAnthropic(model="claude-2", temperature=0)
    input = {"new_file": new_file, "old_file": old_file, "intent": intent}
    return chain.invoke(input)

def code_to_markdown(text):
    """Convert Python code blocks to Markdown format"""
    
    pattern = r"`{3}python\n(.*?)\n`{3}"
    repl = '```python\n\\1\n```'
    return re.sub(pattern, repl, text, flags=re.DOTALL)

def main():
    parser = argparse.ArgumentParser(description="Run a Python script and capture its exit code.")
    parser.add_argument('script', type=str, help="Path to the Python script to run.")
    args = parser.parse_args()

    try:
        exit_code, stderr_output, file_path = run_script(args.script)
        content = read_file_content(file_path)
        if exit_code != 0:
            print(f"Code confirmed flawed. Continuing.")
            
            # Initial guess at purpose of program.
            purpose_inf = infer_purpose(file_path, content)
            
            # If we need to we get a better purpose.
            purpose_inf = get_user_decision_on_inference(purpose_inf, file_path, content)

            can_fix = False
            while not can_fix:
                can_fix = can_you_fix(
                    file_path,
                    content,
                    stderr_output,
                    purpose_inf.content
                )
            
            code = get_fix_code(
                file_path,
                content,
                stderr_output,
                purpose_inf.content
            )

            code = extract_code_from_markdown(code)
            print(code)
            # Adjust code width according to terminal size
            print("\nCongratulations, you have fixed the code! Here is your solution:")
            pretty_code = highlight(code, PythonLexer(), TerminalFormatter())
            print(pretty_code)

            diff_output = diff(content, code, purpose_inf.content)
            final_diff = code_to_markdown(diff_output.content)
            print(final_diff)

    except FileNotFoundError:
        print(f"The file {args.script} does not exist or is not a file.", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
