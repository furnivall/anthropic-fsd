### Hackathon Application Plan

##### Objectives
We want to develop a CLI unix-esque application, where we can pipe the output of a python file into our application. 


The application will then first attempt to infer the *intent* of the code.
It will then check with the user that that we correctly determines the intent of the user.
If the intent is wrong, ask the user for some clarifying information.

If the intent appears to be correct, we can then make a suggestion on how to fix. 
For this, we should give the user two options:
1) Tell the user exactly what line to fix.
2) Give the user an entirely new version of the file (and write to x file)

#### Problems to solve

1) Infer filename from error text
2) Effective API usage - not wasting requests
3) Possible stretch idea - look at full codebases (or at least as much that we can fit in context window)
4) LLMs suck at maths. ensure the specific line is highlighted for the LLM's context as it cannot find relative line numbers.
5) Exclude standard libraries example sys

##### Extra ideas
- Diffing with colours
- Provide refactoring advice on code which already works (i.e. not appending output)

Potential Algo:
```
Input: Filename + Contents of Filename

Output: 
    A. Intent
    B. Ask user if Intent is 1 (Good) or 0 (Bad)

if intent == 1:
    Analyze: Error + Contents of Filename + intent
    Output: 1 (Good) or 0 (Bad)
    
    if 1: Re-call: with best solve
    if 0: [Not enough info] Recursion Re-call: with Filenames of Error. 
           Continue till 1. (APPLY CONSTRAINTS)

else: intent == 0:
  
    Recursive Re-call: with Focused questions from Intent + Contents of Filename
    Output: 1 (Good) or 0 (Bad)

    if 1: Procede to the case of intent == 1
    if 0: Continue Recursion
```


