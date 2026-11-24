import time

BLU = "\033[94m"
YEL = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"


def ts():
    return time.strftime("%H:%M:%S")


def stampaInfo(message: str):
    print(f"{BLU}{ts()} Info: {message}{RESET}", flush=True)


def stampaWarning(message: str):
    print(f"{YEL}{ts()} Warning: {message}{RESET}", flush=True)


def stampaAllarme(message: str):
    print(f"{RED}{ts()} Error: {message}{RESET}", flush=True)