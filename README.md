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
    B. Ask user if our inferred intent is correct

if intent is accepted by the user:
    Send a prompt broadly asking "can you solve the error with 100% certainty, return 1 if yes, 0 if true only", along with the error text, Contents of Filename + intent
    
    Output: 1 (Good) or 0 (Bad)
    
    if 1:
        Call the API again with the same set of appended files but different prompt asking for the best solution possible.
        Return solution to user <in whatever form we decide on>
    if 0:
        This means the LLM has not got enough information to infer a solution to the problem.
        At this point, we need to add additional context. 
        One approach is to gradually append files from the TraceBack in reverse order to the prompt.
        This could naturally get quite big, so we'll need to implement constraints to ensure we are not using excessive calls.
        We could ask the user after each iteration if they want to add an additional file before we do it (including the filename)
        <this is likely to be the most complex element of the entire problem>
        Continue till 1. 

else: intent == 0:
  
    Discovering that the user does not agree with the perceived intent, send LLM a second prompt with the following:
        1) Failed Intent
        2) Filename + file content
        3) Prompt requesting clarifying questions (these can be fleshed out later)
    Output: Set of clarifying questions as before
    
    Send the above output to user, requesting answers to clarifying questions.
    
    Send another request to LLM containing above params plus the answers mentioned, asking it to generate a new perceived intention.
    Send THAT to the user and check if new intent is valid. 

    If valid, go to the intent/solve/more info loop
    If not valid:
        re-run the clarifying questions loop with additional context.


```


