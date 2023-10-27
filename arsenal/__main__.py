# Copyright Orange CyberDefense

import argparse
import fcntl
import json
import os
import re
import sys
import termios
import time

from arsenal.cheat import Cheats
from arsenal.cheat import cheat_check
from arsenal.gui import Gui

from arsenal import __version__


BASEPATH = os.path.dirname(os.path.abspath(__file__))
DATAPATH = os.path.join(BASEPATH, 'cheats')
HOMEPATH = os.path.expanduser("~")
FORMATS = ["md", "rst", "yml"]
EXCLUDE_LIST = ["README.md", "README.rst", "index.rst"]

CHEATS_PATHS = [
    os.path.join(DATAPATH),
    #join(BASEPATH, "custom_cheats"),
    os.path.join(HOMEPATH, ".cheats")
]

messages_error_missing_arguments = 'Error missing arguments'

# set lower delay to use ESC key (in ms)
os.environ.setdefault('ESCDELAY', '25')
os.environ['TERM'] = 'xterm-256color'

savevarfile = os.path.join(HOMEPATH, ".arsenal.json")


#------------------------------------------------------------------------------
def parse_args():
    examples = '''examples:
    arsenal
    arsenal --copy
    arsenal --print

    You can manage global variables with:
    >set GLOBALVAR1=<value>
    >show
    >clear

    (cmd starting with '>' are internals cmd)
    '''

    parser = argparse.ArgumentParser(
        description='arsenal - Pentest command launcher',
        epilog='''
        Examples:
         arsenal
         arsenal --copy
         arsenal --print

        Manage global variables with:
         >set GLOBALVAR1=<value>
         >show
         >clear

        Prefix cmds with '>' for internal use.)''',
        formatter_class=argparse.RawTextHelpFormatter)

    group_out = parser.add_argument_group('output [default = prefill]')
    group_out.add_argument('-p', '--print', action='store_true', help='Print the result')
    group_out.add_argument('-o', '--outfile', action='store', help='Output to file')
    group_out.add_argument('-x', '--copy', action='store_true', help='Output to clipboard')
    group_out.add_argument('-e', '--exec', action='store_true', help='Execute cmd')
    group_out.add_argument('-t', '--tmux', action='store_true', help='Send command to tmux panel')
    group_out.add_argument('-c', '--check', action='store_true', help='Check the existing commands')

    parser.add_argument('-v', '--version',
                        action='version',
                        version=__version__,
                        help='''
                        Display the current version and exit.
                        ''')

    return parser.parse_args()


#------------------------------------------------------------------------------
def prefil_shell_cmd(cmd):
    stdin = 0
    # save TTY attribute for stdin
    oldattr = termios.tcgetattr(stdin)
    # create new attributes to fake input
    newattr = termios.tcgetattr(stdin)
    # disable echo in stdin -> only inject cmd in stdin queue (with TIOCSTI)
    newattr[3] &= ~termios.ECHO
    # enable non canonical mode -> ignore special editing characters
    newattr[3] &= ~termios.ICANON
    # use the new attributes
    termios.tcsetattr(stdin, termios.TCSANOW, newattr)
    # write the selected command in stdin queue
    for c in cmd.cmdline:
        fcntl.ioctl(stdin, termios.TIOCSTI, c)
    # restore TTY attribute for stdin
    termios.tcsetattr(stdin, termios.TCSADRAIN, oldattr)


#------------------------------------------------------------------------------
def main():
    args = parse_args()

    cheatsheets = Cheats().read_files(
        CHEATS_PATHS, FORMATS, EXCLUDE_LIST)

    if args.check:
        cheats_check(cheatsheets)
        return

    gui = Gui(savevarfile)
    while True:
        cmd = gui.run(cheatsheets)

        if cmd == None:
            exit(0)

        # Internal CMD
        elif cmd.cmdline[0] == '>':
            if cmd.cmdline == ">exit":
                break
            elif cmd.cmdline == ">show":
                if (os.path.exists(savevarfile)):
                    with open(savevarfile, 'r') as f:
                        arsenalGlobalVars = json.load(f)
                        for k, v in arsenalGlobalVars.items():
                            print(k + "=" + v)
                break
            elif cmd.cmdline == ">clear":
                with open(savevarfile, "w") as f:
                    f.write(json.dumps({}))
                run()
            elif re.match(r"^\>set( [^= ]+=[^= ]+)+$", cmd.cmdline):
                # Load previous global var
                if (os.path.exists(savevarfile)):
                    with open(savevarfile, 'r') as f:
                        arsenalGlobalVars = json.load(f)
                else:
                    arsenalGlobalVars = {}
                # Add new glovar var
                varlist = re.findall("([^= ]+)=([^= ]+)", cmd.cmdline)
                for v in varlist:
                    arsenalGlobalVars[v[0]] = v[1]
                with open(savevarfile, "w") as f:
                    f.write(json.dumps(arsenalGlobalVars))
            else:
                print("Arsenal: invalid internal command..")
                break

        # OPT: Copy CMD to clipboard
        elif args.copy:
            try:
                import pyperclip
                pyperclip.copy(cmd.cmdline)
            except ImportError:
                pass
            break

        # OPT: Only print CMD
        elif args.print:
            print(cmd.cmdline)
            break

        # OPT: Write in file
        elif args.outfile:
            with open(args.outfile, 'w') as f:
                f.write(cmd.cmdline)
            break

        # OPT: Exec
        elif args.exec and not args.tmux:
            os.system(cmd.cmdline)
            break

        elif args.tmux:
            try:
                import libtmux
                try:
                    server = libtmux.Server()
                    session = server.list_sessions()[-1]
                    window = session.attached_window
                    panes = window.panes
                    if len(panes) == 1:
                        # split window to get more pane
                        pane = window.split_window(attach=False)
                        time.sleep(0.3)
                    else:
                        pane = panes[-1]
                    # send command to other pane and switch pane
                    if args.exec:
                        pane.send_keys(cmd.cmdline)
                    else:
                        pane.send_keys(cmd.cmdline, enter=False)
                        pane.select_pane()
                except libtmux.exc.LibTmuxException:
                    prefil_shell_cmd(cmd)
                    break
            except ImportError:
                prefil_shell_cmd(cmd)
                break
        # DEFAULT: Prefill Shell CMD
        else:
            prefil_shell_cmd(cmd)
            break


if __name__ == "__main__":
    sys.exit(main())
