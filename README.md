This project uses AI to help fix Python code. It takes a Python file with errors, analyzes the code and errors, asks clarifying questions, and generates suggested fixes.

Getting Started
These instructions will help you run the code fixer on your machine.

Prerequisites
You will need:

Python 3.6 or higher
The following Python packages:
langchain
pygments
Using the Code Fixer
Save the Python file you want to fix in the same folder as code_fixer.py
Run the code fixer on your file:
Copy code

python code_fixer.py your_file.py
The code fixer will run your code, capture any errors, and ask you clarifying questions about what you were trying to accomplish.
It will then suggest fixes to your code. If the suggestions don't seem right, you can ask more clarifying questions.
When you're happy with the suggested fix, it will print out the fixed code for you to use.
Authors
Your name - Initial work
Acknowledgments
This project was created as a demo for how AI can help fix coding errors.
It uses the LangChain library to generate the suggestions.
