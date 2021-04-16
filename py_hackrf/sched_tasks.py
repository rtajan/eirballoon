import json
import os
import time 
from datetime import datetime
import json
import stat
from os import path
from inspect import getmembers, isfunction



#task name and task execname should be the same 


class Task:
        #defining attributes for the task class
        offset=0
        name=""
        ExecName=""
        TaskArgs=[]
        def initialize(self, ParsedName,  ParsedArgs, ParsedOffset):
            self.offset=int(ParsedOffset)
            self.name=ParsedName
            self.ExecName=ParsedName
            self.TaskArgs=ParsedArgs  
        
        def exec(self, args_dict):
            #args is a table of arguments parsed from the JSON
            
            fncs=getmembers(Task, isfunction)
            for taskexec in fncs:
                if taskexec[0]==self.ExecName:
                    taskexec[1](self, args_dict)

        #defining execs for each task 

        #########################################
        #### YOU CAN SIMPLY add a task exec below 
        # 
        # def task_exec(self, args_dict):
        # after this line !!!!#


        def create_pipe(self,args_dict):
            #mkfifo
            return
        def take_photo(self,args_dict):
            #prendre une photo
            
            
            filename=args_dict["MediaFilePath"]+"Image_N.jpeg"
            args_dict["LogFile"].write(datetime.now().strftime("%H:%M:%S")+": Taking photo"+"\n")
            

            

        def record(self, args_dict):
            #prendre une video
            # add
            filename=args_dict["MediaFilePath"]+"Vid_N.mp4"

            args_dict["LogFile"].write(datetime.now().strftime("%H:%M:%S")+": Taking video for "+str(args_dict["vid_sec"])+" seconds"+"\n")

            
            
        def start_aff3ct(self, args_dict):

            args_dict["LogFile"].write(datetime.now().strftime("%H:%M:%S")+": Starting Aff3ct"+"\n")

        
#if __name__ == "__main__":
    
