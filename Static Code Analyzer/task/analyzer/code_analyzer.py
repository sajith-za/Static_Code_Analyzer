# write your code here
import os
import sys
from error_functions import *


if __name__ == '__main__':

    args = sys.argv
    isFile = os.path.isfile(args[1])
    isDirectory = os.path.isdir(args[1])

    if isFile:
        ca = Error_Checker(args[1])
        ca.processing()
        ca.print_error_dict()

    elif isDirectory:
        for entry in os.listdir(args[1]):
            if os.path.isfile(os.path.join(args[1], entry)):
                if not entry.endswith('.html'):
                    ca = Error_Checker(os.path.join(args[1], entry))
                    ca.processing()
                    ca.print_error_dict()
