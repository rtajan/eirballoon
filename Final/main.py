
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#

# Title: main.py (Scheduler)

#programme de gestion des séquences on -> pause -> exec Tx.py -> aff3ct cesse d'écrire ds le tube -> kill Tx.py/off -> pause -> et on recommence 



#créer tube 
#trouver le chemin de aff3ct2py
#exécuter aff3ct2py
#traiter signal début aff3ct2py
#allumer émetteur
#aff3ct2py écrit dans le tube 
#tube -> buffer 
#buffer -> hackrf
#traiter signal fin aff3ct2py
#éteindre l'émetteur
import json
import os
# import sys
# sys.path.insert(1,'./classes/sched_tasks')
import time 
from datetime import datetime
import json
import stat
from inspect import getmembers, isfunction
from sched_tasks import Task
from os import path

# def isfifo(self,fn):
#     #check if the pipe already exists
#             return stat.S_ISFIFO(os.stat(fn).st_mode)

# class amp:
#     #complete this class!!!
#     power = 0
#     def amp_on(self):
#         #mettre le bit à 1
#         self.power = 1
#         #pause 100us
#         time.sleep(0.0100)
#         print("ampli allumé")

#     def amp_off(self):
#         #mettre le bit à 0
#         self.power = 0
#         #pause 130us
#         time.sleep(0.0130)
#         print("ampli éteint")

class Start:
    '''Main class in scheduler '''
    
    def initialize(self):
        
        #defining global attributes
        self.photos_counter=0
        self.video_counter=0
        self.videos_ttl=0  #total length
        self.currentTaskName=""

        ##############################################################################################
 
        #on retrouve le repertoire eirballoon
        abs_path = os.path.dirname(os.path.abspath(__file__)).split("/")
        while abs_path[-1:][0]!="eirballoon":
            abs_path.pop()
        str_abs_path = ""
        for i in range(1,len(abs_path)):
            str_abs_path = str_abs_path + "/" + abs_path[i]
        str_abs_path = str_abs_path + "/"
        self.path=str_abs_path
        ##############################################################################################

        self.mediaFilePath=self.path+"Final/media"
        self.pipe_path=self.path+"Final/py_pipe"
        self.path_log=self.path+"Final/log_tasks.txt"

       #creating log file
        self.fichier_log=open(self.path_log, "w")
        self.fichier_log.write(datetime.now().strftime("%H:%M:%S")+" Starting Task Scheduling Log "+"\n")
       

    def sched_sleep(self, secs):
        time.sleep(secs)
    def tube_creator(self):

        #if pipe exists delete pipe
        try:
            os.mkfifo(self.pipe_path)
        except FileExistsError:
            os.remove(self.pipe_path)
            os.mkfifo(self.pipe_path)
            self.fichier_log.write(datetime.now().strftime("%H:%M:%S")+": Creating a named pipe in "+self.pipe_path+"\n")
   





if __name__ == "__main__":
    #initializing Start class
    StartObj=Start() 
    #initializing path vars and
    StartObj.initialize()
    #dictionary containing global variables
    envvar={"MediaFilePath":StartObj.mediaFilePath, "LogFile":StartObj.fichier_log }

    with open(StartObj.path+'Final/tasks.json') as json_file:
        data = json.load(json_file)
        '''
        from now on the only tasks executed are the tasks on the JSON file
            - each task has a name task_name
            - each task has a list of task args task_args for example: below record has an argument of 4 seconds 
            - each task has a time offset task_offset: the exec sleeps for a number of seconds before exec the next step
        feel free to add/modify the task structures in the JSON file

        '''
        TaskObjs=[]
        while True :
            for all_tasks in data.values():
                task=all_tasks[0] # --> task_n
                #initialisation des objets Tas
                currentTask=Task()
                currentTask.initialize(task["task_name"], task['task_args'][0], task['task_offset'])
                #args reformatting
                currentTask.TaskArgs.update(envvar)
                #executing task routine
                currentTask.exec(currentTask.TaskArgs)
                StartObj.sched_sleep(currentTask.offset)
         
    StartObj.fichier_log.close()
