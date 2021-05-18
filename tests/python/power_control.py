import RPi.GPIO as GPIO
import sys
import numpy as np
sys.path.insert(0, '../../build/lib')
from py_aff3ct.module.py_module import Py_Module


class power_control(Py_Module):

    def on(self): #off
        GPIO.output(switch, GPIO.HIGH)
        self.state=1
        return 0

    
    def off(self): # off
        GPIO.output(switch, GPIO.LOW)
        self.state=0
        return 0

    def change_state(self,out):
        if self.state==1:
            self.off()
        else:
            self.on()
        out = self.state
        return 0

    def __init__(self):
        # init
        Py_Module.__init__(self)
        self.name = "power_control"
        
        switch = 18 #physical pin num attached to the switch
        GPIO.setmode(GPIO.BOARD)   
        GPIO.setup(switch, GPIO.OUT) 
        self.state=0

        swtch = self.create_task('change_state')
        sin_change_state = self.create_socket_in(swtch, "X_N", 1, np.int32)  # send 1 to change state 
        sout_state = self.create_socket_out(swtch, "Y_N", 1, np.int32)   #current state of switch

        # properties
        self.create_codelet(swtch, lambda slf, lsk,
                            fid: self.change_state(lsk[sin_change_state], lsk[sout_state]))





