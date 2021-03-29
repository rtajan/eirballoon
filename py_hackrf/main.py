#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#

# Title: main.py

#programme de gestion des séquences on -> pause -> exec Tx.py -> aff3ct cesse d'écrire ds le tube -> kill Tx.py/off -> pause -> et on recommence 


#exec

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

import os
import time 

class amp:
    power = 0
    def amp_on(self):
        #mettre le bit à 1
        self.power = 1
        #pause 100us
        time.sleep(0.0100)
        print("ampli allumé")
        return 1

    def amp_off(self):
        #mettre le bit à 0
        self.power = 0
        #pause 130us
        time.sleep(0.0130)
        print("ampli éteint")
        return 1






class start:

    def __init__(self):
        #on retrouve le repertoire eirballoon
        path_tmp = os.path.dirname(os.path.abspath(__file__))
        abs_path = path_tmp.split("/")
        while abs_path[-1:][0]!="eirballoon":
            print(abs_path)
            abs_path.pop()
        print(abs_path)
        i = 0
        str_abs_path = ""
        for i in range(len(abs_path)):
            str_abs_path = "/" + abs_path[i]
        str_abs_path = str_abs_path + "/"
        print (str_abs_path)


    def tube_creator(path):
        os.mkfifo(path)
        return 1

    

    def take_a_photo(file_path):
        #prendre une photo
        print(photo)
        return 1 #return file_name

    def record_video(file_path):
        #prendre une video
        print(video)
        return 1 #return file_name

    def start_aff3ct(file_name):
        print(affect)
        #exec aff3ct(path)
        return 1









def main(): 
    print("démarrage")
    demarrage = start()
    ampli = amp()



main()

    #if __name__ == "__main__":
     #   print("Les chicots, c'est sacré ! Parce que si j'les lave pas maintenant, dans dix ans, c'est tout à la soupe. Et l'mec qui me fera manger de la soupe il est pas né !")
      #  main()
    #else:
     #   print('Du passé faisons table en marbre.')