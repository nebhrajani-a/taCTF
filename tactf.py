#!/usr/bin/python3

import argparse
import sys
import re
import subprocess
import tempfile
from string import ascii_lowercase, ascii_uppercase, digits, punctuation

not_allowed_chars = ['"', "'", "(", ")", ">", "<", "`", "|", "\\",
                     "#", ";", "&"]
punctuation = list(punctuation.strip(" "))
for char in not_allowed_chars:
    punctuation.remove(char)
punctuation = ''.join(punctuation)


def make_bold(text, index):
    return text[:index] + '\033[1m' + text[index] + '\033[0m' + text[index+1:]


def get_charset(code):
    if code == 1:
        charset = ascii_lowercase + punctuation
    elif code == 2:
        charset = ascii_uppercase + punctuation
    elif code == 3:
        charset = ascii_lowercase + ascii_uppercase + punctuation
    elif code == 4:
        charset = ascii_lowercase + digits + punctuation
    else:
        charset = ascii_lowercase + ascii_uppercase + digits + punctuation
    return charset


def get_instruction_count(test_str, binary_filename):
    with tempfile.NamedTemporaryFile() as tmp:
        command = f'echo "{test_str}" | valgrind --tool=callgrind --callgrind-out-file={tmp.name}\
        {binary_filename}'
        try:
            with subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE) as valout:
                valout = valout.stderr.read()
                valout = int(re.findall('Collected : \d+',
                                        valout.decode())[0][12:])
                return valout
        except IndexError:
            pass


def find_char_at(test_str, location, binary_filename, verbose, charset_code):
    if verbose:
        print("Testing: ", make_bold(test_str, location), "at", location)
    charset = get_charset(charset_code)
    maximum = 0
    bestchoice = ""
    for char in charset:
        test = test_str[:location] + char + test_str[location+1:]
        val = get_instruction_count(test, binary_filename)
        if val is not None:
            if val > maximum:
                maximum = val
                bestchoice = test
        if verbose:
            print("    ", char, ":", val)
    return bestchoice


def find_length(binary_filename, maxlen, verbose):
    maximum = -1
    init_counts = get_instruction_count("a", binary_filename)
    length = -1
    for i in range(1, maxlen+1):
        val = get_instruction_count("a"*i, binary_filename)
        if verbose:
            print("a"*i, ":", val)
        if val is not None:
            if val > maximum:
                maximum = val
                length = i
    if init_counts != maximum:
        return length

def find_string(binary_filename, maxlen=35,
                verbose=False, reverse=False,
                lengthgiven=False, length=0,
                charset_code=0,
                flag_format=""):
    if not lengthgiven:
        length = find_length(binary_filename, maxlen, verbose)
        if length is None:
            print("[taCTF] I couldn't guess the length, sorry. Try -l LENGTH.")
            sys.exit()
    print("Length guess:", length)
    length_diff = length - len(flag_format)
    candidate = flag_format + 'a'*length_diff
    if not reverse:
        for i in range(len(flag_format), length):
            candidate = find_char_at(candidate, i, binary_filename, verbose,
                                     charset_code)
            print(candidate)
    else:
        for i in range(length-1, len(flag_format)-1, -1):
            candidate = find_char_at(candidate, i, binary_filename, verbose,
                                     charset_code)
            print(candidate)
    return candidate


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run an instruction counting based timing attack on a given binary.')
    parser.add_argument('filename', type=str,
                        help='The file to run taCTF against')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="Verbose mode, prints out what it's up to at every iteration")
    parser.add_argument('-r', '--reverse', action='store_true',
                        help='Try the timing attack starting at the end of the string.')
    parser.add_argument('-f', '--flag-format', type=str, default="",
                        help='Flag format: first N known characters in string.')
    parser.add_argument('-ml', '--max-length', type=int, default=35,
                        help='Maximum length to check strings till, if length unknown.')
    parser.add_argument('-l', '--length', type=int,
                        help='Length of string, if known.')
    parser.add_argument('-c', '--charset', type=int, default=0,
                        help='Set the charset code. Default is 0 (all chars).')
    args = parser.parse_args()

    lengthgivenbool = False
    if args.length is not None:
        lengthgivenbool = True
    find_string(args.filename, maxlen=args.max_length,
                verbose=args.verbose,
                reverse=args.reverse,
                lengthgiven=lengthgivenbool, length=args.length,
                charset_code=args.charset,
                flag_format=args.flag_format)
