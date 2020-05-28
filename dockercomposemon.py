# -*- coding: utf-8 -*-
import os
import subprocess
import datetime
import sys
import time
import json


INTERVAL_SECONDS = 15.0

RED     = "\033[1;31m"
BLUE    = "\033[1;34m"
CYAN    = "\033[1;36m"
GREEN   = "\033[0;32m"
RESET   = "\033[0;0m"
BOLD    = "\033[;1m"
WHITE   = "\033[0;37m"
REVERSE = "\033[;7m"

UP = "\033[1;37m"
DOWN =  "\033[1;31m"
MISSING = u"\u001b[38;5;239m"

MaxW = [0]
MaxH = [0]

def all_containers():
    # -q makes docker-compose return a bunch of nonsense hashes for each of the
    # containers created by the docker-compose. Then we can use those hashes
    # to docker inspect
    try:
        s = subprocess.check_output(["docker-compose", "ps", "-q" ] , stderr=subprocess.DEVNULL )[:-1]
        return s.decode("utf-8").split('\n')
    except:
        return []

def check_docker():
    # this parses systemctl output to identify if the docker service is enabled
    try:
        s = subprocess.check_output(["systemctl", "show", "--property", "ActiveState", "docker"])[:-1]
        return (s.decode("utf-8") == 'ActiveState=active')
    except:
        return False

def do_it():
    if not check_docker():
        os.system('clear')
        print(DOWN + "docker" + RESET)
        return
        
    containers = all_containers()
    command = ["docker", "inspect"] + containers
    j = subprocess.check_output(command)
    # docker inspect returns a json, and that's really convenient
    js = json.loads(j)
    
    found = dict()
    used = set()
    to_print = []

    for x in js:
        n = str(x['Name'])
        if n not in used:
            if n.startswith("/"):
                n = n[1:]
            MaxW[0] = max(MaxW[0], len(n))
            n += ' ' * ( MaxW[0] - len(n) )
            status = x['State']['Status']
            if status == 'running':
                if ('Health' in x['State']) and x['State']['Health']['Status'] == 'unhealthy':
                    s = DOWN + n + RESET
                else:
                    s = UP + n + RESET
            elif status == 'exited':
                s = MISSING + n + RESET
            else:
                s = DOWN + n + RESET
            to_print.append(s)

    MaxH[0] = max(MaxH[0], len(to_print) )
    if len(to_print)  < MaxH[0]:
        to_print += [ " " * MaxW[0] ] * (  MaxH[0] - len(to_print) )


    sys.stdout.write("\033[0;0H")
    print('\n'.join(to_print) )

os.system('clear')
while True:
    try:
        do_it()
    except e:
        print(e)
    time.sleep(INTERVAL_SECONDS)

