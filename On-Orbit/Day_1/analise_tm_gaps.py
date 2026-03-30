import os
import sys
from datetime import date, datetime
from datetime import timedelta
import logging
from idlelib.colorizer import prog

def main(args: str):
    ret = 0
    fname = None
    process = True
    outpath = os.path.abspath(os.curdir)
    config: {}


def usage(prog: str):
    t1 = datetime.today()
    t1 = t1 + timedelta(days=1 - t1.day)
print(f"Usage: {prog} start_date stop_dateconfig_file\n")
print("xxxxxxxxxxxxxxxxxx")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if (sys.argv[1] == "-h" or sys.argv[1] == "--help" or sys.argv[1] == "/?"):
            usage(sys.argv[0])
            # get_any_input()
            sys.exit()
        sys.exit(main(sys.argv[1:]))
    else:
        usage(sys.argv[0])
        # get_any_input()
        sys.exit(0)



































