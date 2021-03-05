import os
import json
import struct
import ctypes
import sys
import numpy as np

def getEirbollonPath():
    """
    Return the  absolute path of Eirballoon folder
    """
    path_pip = os.path.dirname(os.path.abspath(__file__)) 
    tmp_path = path_pip.split("/")
    while tmp_path[-1:][0]!="eirballoon":
        tmp_path.pop()
    return "/".join(tmp_path)

def getPipPath(pipname):
    """
    Return the  absolute path of pip
    """
    eirbPath = getEirbollonPath()
    path_pip =  eirbPath+ "/build/bin/pip/"+pipname
    return path_pip

def getConfigBinPath():
    """
    Return the  absolute path of pip
    """
    eirbPath = getEirbollonPath()
    path =  eirbPath+ "/build/bin/conf"
    return path

def getConfigPath():
    """
    Return the  absolute path of config file
    """
    eirbPath = getEirbollonPath()
    path_pip =  eirbPath+ "/config.json"
    return path_pip

def getRecordDir():
    return getEirbollonPath() + "/record/"

def getHeaderPath():
    return getEirbollonPath() + "/header.csv"

class Config:

    def __init__(self):
        pass

    @staticmethod
    def read():
        with open(getConfigPath(),'r') as fd:
            res = json.loads(fd.read())
        return res

    @staticmethod
    def createConfigBin():
        "Create binary version of affect settings"
        "https://docs.python.org/3/library/struct.html"
        '''	
        const size_t n_threads ;// =                   1; // std::thread::hardware_concurrency();
        const int    n_frames  ;//=                   1;
        const int    K         ;//=                 128; // number of information bits
        const int    N         ;//=                 256; // codeword size
        const int    fe        ;//=                 100; // number of frame errors
        const int    seed      ;//=                   0; // PRNG seed for the AWGN channel
        const int    nb        ;//=                   2; // Number of bits per symbol (QPSK)
        const float  alpha     ;//=                0.40; // Roll-off of Root Raised Cosine
        const int    grp_delay ;//=                  20; // Group delay of Root Raised Cosine
        const int    osf       ;//=                   8; // Oversampling factor (Fse in labs at school)
        '''
        format = "Niiiiiifiiii"
        res = Config.read()["Aff3ct"]
        out = struct.pack(format,
            (np.uint8(res["n_threads" ])),
            (   int(res["n_frames"  ])),
            (   int(res["K"         ])),
            (   int(res["N"         ])),
            (   int(res["fe"        ])),
            (   int(res["seed"      ])),
            (   int(res["nb"        ])),
            (np.single(res["alpha"     ])),
            (   int(res["grp_delay" ])),
            (   int(res["osf"       ])),
            (   int(res["lenHeader"       ])),
            (   int(res["payloadSize"       ]))
            )
        path = getConfigBinPath()
        with open(path, 'w') as  fd:
            fd.buffer.write(out)
        return path



    @staticmethod
    def createDefaultFile():
        record_file = "record.bin" 
        hackrf_Tx = {
            "gain":"14",
            "IFgain":"47",
            "BBgain":"62"
        }
        hackrf_Rx = {
            "gain":"0",
            "IFgain":"30",
            "BBgain":"30"
        }

        hackrf = {
            "Fp":"869.475e6",
            "samp_rate":"4e6",
            "Tx":hackrf_Tx,
            "Rx":hackrf_Rx
        }
        pip = {
            "Aff3ct2Tx":"pip1",
            "Rx2Aff3ct":"pip1",
        }
        Aff3ct = {
            	"n_threads"     :"1"    ,
                "n_frames"      :"1"    ,#;//=                   1;
                "K"             :"128"  ,#;//=                 128; // number of information bits
                "N"             :"256"  ,#;//=                 256; // codeword size
                "fe"            :"100"  ,#;//=                 100; // number of frame errors
                "seed"          :"0"    ,#;//=                   0; // PRNG seed for the AWGN channel
                "nb"            :"2"    ,#;//=                   2; // Number of bits per symbol (QPSK)
                "alpha"         :"0.40" ,#;//=                0.40; // Roll-off of Root Raised Cosine
                "grp_delay"     :"20"   ,#;//=                  20; // Group delay of Root Raised Cosine
                "osf"           :"8"    ,#;//=                   8; // Oversampling factor (Fse in labs at school)
                "lenHeader"     :"64"   , 
                "payloadSize"   :"3328"
        }
        Config = {
            'record_name':record_file,
            'pip':pip,
            'Aff3ct':Aff3ct,
            'hackRF':hackrf
        }
        with open(getConfigPath(),'w') as fd:
            json.dump(Config,fd, indent=4)

if __name__ == "__main__":
    Config.createDefaultFile()

