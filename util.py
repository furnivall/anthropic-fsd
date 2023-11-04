import re

def stack_trace_to_files(traceback: str):
    file_regex = r'File "(?P<file>.+)", line'
    files = []
    for line in traceback.split('\n'):
        match = re.search(file_regex, line)
        if match:
            file = match.group('file')
            files.append(file)
    return files