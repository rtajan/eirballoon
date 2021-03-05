#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

sys.path.insert(0, "./python_src")
import Mytools
import os
import signal
import subprocess
import argparse
import time

if __name__ == "__main__":
    # Definition des argument
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--rec",type=int, help="record, usage -r [time in ms]")
    args = parser.parse_args()

    # Gestion de du CTRL+c
    process = None
    def sig_handler(signalNumber, frame):
        process.send_signal(signal.SIGINT)
    signal.signal(signal.SIGINT, sig_handler)

    # Declaration de variable
    configPath = Mytools.Config.createConfigBin() # Creation d'un fichier de configuration binaire a partir du config.json
    AbsPath = Mytools.getEirbollonPath()
    conf = Mytools.Config.read()    # lecture du fichier configuration binaire
    pipname = conf['pip']['Aff3ct2Tx']

    # création de la commande  à exécuter 
    if args.rec: # Si on enregistre
        if not os.path.exists('record'):
            os.makedirs('record')
        bashCommand = AbsPath + "/py_hackrf/Rx_fd.py -r " + str(args.rec)
        process = subprocess.Popen(bashCommand.split())
        process.wait()
        exit()
    else:
        print("ok")
        mypipe = AbsPath +"/py_hackrf/mypipe"
        prog1 = AbsPath + "/py_hackrf/Rx_fd.py"
        prog2 = AbsPath + "/build/bin/recepteur -f " + configPath
        bashCommand = " ".join([mypipe,pipname,prog1,"/",prog2])

    # https://stackoverflow.com/questions/4256107/running-bash-commands-in-python
    # print(bashCommand)
    # os.system(bashCommand)
    process = subprocess.Popen(bashCommand.split())
    process.wait()
