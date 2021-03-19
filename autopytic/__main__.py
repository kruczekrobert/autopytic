import sys, os
from pathlib import Path  # Python 3.6
from dotenv import load_dotenv
from .tools.wrapper import bcolors

env_path = Path(".") / ".pytic"
load_dotenv(dotenv_path=env_path)


def _check_file_coverage(f, lines):
    def_count = 0
    wrapper_count = 0
    for i, line in enumerate(lines):
        if "def" in line.strip():
            def_count += 1
            if "@Wrapper.register_event" not in lines[i-1] or "#" in lines[i-1].strip()[:15]:
                print(f'{bcolors.FAIL}[FAIL] {bcolors.ENDC}{f} line:{i} {line.strip()[:-1].replace("def ", "")} does not have event registration')
            else:
                print(f'{bcolors.OKGREEN}[PASS] {bcolors.ENDC}{f} line:{i} {line.strip()[:-1].replace("def ", "")}')
                wrapper_count +=1

    return round((wrapper_count / def_count) * 100, 2)


def _check_code_coverate():
    files = [os.path.join(path, name) for path, subdirs, files in os.walk(".") for name in files]
    file_cov = []
    for f in files:
        if os.environ.get("EXCLUDE_VENV") not in f and f[-3:] == ".py":
            with open(f, 'r') as cov_file:
                lines = cov_file.readlines()
                fc = _check_file_coverage(f, lines)
                if fc == 100.0:
                    file_cov.append(f'{f} {bcolors.OKGREEN}{fc}% {bcolors.ENDC}')
                else:
                    file_cov.append(f'{f} {bcolors.FAIL}{fc}% {bcolors.ENDC}')

    for fc in file_cov:
        print(fc)

if __name__ == "__main__":
    if "coverage" in sys.argv:
        print(f'{bcolors.WARNING}Checking autopytic code coverage...{bcolors.ENDC}')
        _check_code_coverate()
                
