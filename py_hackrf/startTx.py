#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, './py_aff3ct/build/lib') #always bind the path to the aff3ct library

import Mytools
import os
import signal
import subprocess
import argparse
import time

if __name__ == "__main__":
    # Definition des argument
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test", help="emision/reception without Hackrf",action="store_true")
    parser.add_argument("-d", "--debug", help="debug",action="store_true")
    args = parser.parse_args()

    # Gestion de du CTRL+c
    process = None
    def sig_handler(signalNumber, frame):
        process.send_signal(signal.SIGINT)
    signal.signal(signal.SIGINT, sig_handler)

    # Declaration de variable
    configPath = Mytools.Config.createConfigBin() # Creation d'un fichier de configuration binaire a partir du config.jdon
    AbsPath = Mytools.getEirbollonPath()
    conf = Mytools.Config.read()
    pipname = conf['pip']['Aff3ct2Tx']

    # création de la commande  à exécuter
    if args.test:
        print("test option")
        if conf['pip']['Aff3ct2Tx'] != conf['pip']['Rx2Aff3ct']:
            print("erreur config.json")
            print(conf['pip'])
            print("Aff3ct2Tx !=  Rx2Aff3ct")
            exit(0)
        mypipe = AbsPath +"/radio_logicielle/mypipe"
        prog1 = AbsPath + "/build/bin/emetteur -f " + configPath
        prog2 = AbsPath + "/build/bin/recepteur -f " + configPath
        bashCommand = " ".join([mypipe,pipname,prog1,"/",prog2])
    elif args.debug:
        prog1 = AbsPath + "/build/bin/emetteur -d -f " + configPath
        bashCommand = " ".join([prog1])
    else:
        mypipe = AbsPath +"/radio_logicielle/mypipe"
        prog1 = AbsPath + "/build/bin/emetteur -f " + configPath
        prog2 = AbsPath + "/radio_logicielle/Tx.py"
        bashCommand = " ".join([mypipe,pipname,prog1,"/",prog2])


    # https://stackoverflow.com/questions/4256107/running-bash-commands-in-python
    # print(bashCommand)
    # os.system(bashCommand)
    process = subprocess.Popen(bashCommand.split())
    process.wait()
