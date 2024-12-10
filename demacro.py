#!/usr/bin/python3

import sys
import re

class Command:
    def __init__(self, name, num_args, definition):
        self.name = name
        self.num_args = num_args
        self.definition = definition

    def apply(self, tex: str):
        while True:
            match = re.search(re.compile('\\%s\\s*{' % self.name), tex)
            if not match:
                break
            idx = match.start()

            if self.num_args == 0:
                end_index = tex.index('}', idx)
                repl = self.definition
                tex = tex[:idx] + repl + tex[end_index + 1 :]
            else:
                start_idx = idx
                args = []
                # extract arguments
                for arg in range(self.num_args):
                    arg_start = tex.index('{', start_idx) + 1
                    i = arg_start
                    depth = 0
                    while tex[i] != '}' or depth > 0:
                        if tex[i] == '{':
                            depth += 1
                        elif tex[i] == '}':
                            depth -= 1
                        i += 1
                    arg_end = i
                    args.append(tex[arg_start : arg_end])
                    start_idx = i

                # build replacement string
                repl = self.definition
                for ind, arg in enumerate(args, 1):
                    repl = repl.replace('#%s' % ind, arg)
                tex = tex[:idx] + repl + tex[i+1:]
        return tex

def parse_command(tex :str, idx :int) -> Command:
    cmd_name = None
    num_args = 0
    cmd_definition = None

    # extract command name
    cmd_name_start = tex.index('{', idx) + 1
    cmd_name_end = tex.index('}', idx)
    cmd_name = tex[cmd_name_start: cmd_name_end].strip()
    assert r'\newcommand{' == tex[idx:cmd_name_start].strip().replace(' ', '')

    # parse rest of command
    i = cmd_name_end + 1
    while tex[i].isspace():
        i += 1

    # command has args
    if tex[i] == '[':
        end_index = tex.index(']', i)
        num_args = int(tex[i + 1 : end_index].strip())
        i = end_index + 1

    # skip over whitespace
    while tex[i].isspace():
        i += 1

    # command definition
    assert tex[i] == '{'
    i += 1
    
    cmd_definition_start = i
    depth = 0
    while tex[i] != '}' or depth > 0:
        if tex[i] == '{':
            depth += 1
        elif tex[i] == '}':
            depth -= 1
        i += 1
    cmd_definition_end = i
    cmd_definition = tex[cmd_definition_start : cmd_definition_end]
    tex = tex[:idx].strip() + tex[cmd_definition_end + 1:].strip()
    tex = tex.strip()

    return Command(cmd_name, num_args, cmd_definition), tex

def extract_commands(tex) -> list[Command]:
    commands = []
    while True:
        idx = None
        try: idx = tex.index(r'\newcommand')
        except ValueError: break
        command, tex = parse_command(tex, idx)
        commands.append(command)
    return commands, tex

if __name__ == '__main__':
    with open(sys.argv[1]) as f:
        tex = f.read()

    commands, tex = extract_commands(tex)

    for command in commands:
        tex = command.apply(tex)

    print(tex)