from time import sleep
from os import system
from sys import stdout
from platform import system as plat


def custom_print(string, speed=0.05):
    for i, ch in enumerate(string):
        if i + 1 == len(string):
            print(ch)
        else:
            print(ch, end="")
            stdout.flush()
            sleep(speed)


def clear_screen():
    platform = plat()
    match platform:
        case "Linux" | "Darwin":
            system('clear')
        case "Windows":
            system('cls')
