def update_line(file_path, line_num, new_line):
    with open(file_path, 'r+') as f:
        lines = f.readlines()
        lines[line_num-1] = new_line + '\n'
        f.seek(0)
        f.writelines(lines)
