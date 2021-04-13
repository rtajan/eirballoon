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
import time 
from datetime import datetime
import json
import stat
from os import path

def isfifo(self,fn):
    #check if the pipe already exists
            return stat.S_ISFIFO(os.stat(fn).st_mode)

class amp:
    #complete this class!!!
    power = 0
    def amp_on(self):
        #mettre le bit à 1
        self.power = 1
        #pause 100us
        time.sleep(0.0100)
        print("ampli allumé")

    def amp_off(self):
        #mettre le bit à 0
        self.power = 0
        #pause 130us
        time.sleep(0.0130)
        print("ampli éteint")

class Start:
    '''Main class in scheduler '''

    def initialize(self):
        
        #defining global attributes
        self.photos_counter=0
        self.video_counter=0
        self.videos_ttl=0  #total length
        self.currentTaskNumber=""
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

        self.mediaFilePath=self.path+"py_hackrf/media"
        self.pipe_path=self.path+"py_hackrf/py_pipe"
        self.path_log=self.path+"py_hackrf/log_tasks.txt"

       #creating log file
        self.fichier_log=open(self.path_log, "w")
        self.fichier_log.write(datetime.now().strftime("%H:%M:%S")+" Starting Task Scheduling Log "+"\n")
        print("selfpath "+self.path)
       

 
    def tube_creator(self):

        #if pipe exists delete pipe
        try:
            os.mkfifo(self.pipe_path)
        except FileExistsError:
            os.remove(self.pipe_path)
            os.mkfifo(self.pipe_path)
            self.fichier_log.write(datetime.now().strftime("%H:%M:%S")+": Creating a named pipe in "+self.pipe_path+"\n")
   
    def take_a_photo(self):
        #prendre une photo

        filename=self.mediaFilePath+str(self.photos_counter)
        self.fichier_log.write(datetime.now().strftime("%H:%M:%S")+": Taking photo"+"\n")
        self.photos_counter+=1

    def record_video(self, vid_sec):
        #prendre une video

        filename=self.mediaFilePath+str(self.video_counter)

        self.fichier_log.write(datetime.now().strftime("%H:%M:%S")+": Taking video for "+str(vid_sec)+" seconds"+"\n")

        self.video_counter+=1
        self.videos_ttl+=vid_sec

    def start_aff3ct(self):

        self.ficher_log.write(datetime.now().strftime("%H:%M:%S")+": Starting Aff3ct"+"\n")


if __name__ == "__main__":
    #initializing Start class
    StartObj=Start() 
    #initializing path vars and
    StartObj.initialize()
   
    with open(StartObj.path+'py_hackrf/tasks.json') as json_file:
        data = json.load(json_file)
        '''
        from now on the only tasks executed are the tasks on the JSON file
            - each task has a name task_name
            - each task has a number task_number
            - each task has a list of task args task_args for example: below record has an argument of 4 seconds 
            - each task has a time offset task_offset: the exec sleeps for a number of seconds before exec the next step
        feel free to add/modify the task structures in the JSON file

        '''
        for all_tasks in data.values():
                task=all_tasks[0] # --> task_n
                StartObj.currentTaskName=task["task_name"]

                #switch 
                if StartObj.currentTaskName=="take_photo":
                    StartObj.take_a_photo()
                    StartObj.photos_counter+=1
                    time.sleep(int(task["task_offset"]))
                elif StartObj.currentTaskName=="record":
                    StartObj.record_video(int(task['task_args'][0]['arg_1']))
                    time.sleep(int(task["task_offset"]))
                elif StartObj.currentTaskName=="create_pipe":
                    StartObj.tube_creator()
                    time.sleep(int(task["task_offset"]))
                else:
                    print("NONE")

        StartObj.fichier_log.close()


# main()