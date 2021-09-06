def read_files(files_arg):
    if len(files_arg) == 1 and files_arg[0].endswith(".txt"):
        files = []
        with open(files_arg[0]) as fp:
            for line in fp.readlines():
                files.append(line.rstrip())
    else:
        files = files_arg
    return files