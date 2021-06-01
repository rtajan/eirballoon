# Eirballoon

This repository contains a student code for QPSK modulation and demodulation using py_aff3ct and Software Defined Radios (SDRs). 

## Pre-requisite

The first step is to fetch every submodule in this project.

	$ git submodule update --init --recursive

Then, compile `py_aff3ct` on Linux/MacOS/MinGW following [the README.md file](https://github.com/aff3ct/py_aff3ct/tree/d3a053a6180f303cbb55cbbf450aabc3bba202ec) of the `py_aff3ct` folder.

## Compile your code

Compile the code on Linux/MacOS/MinGW:

	$ mkdir build && cd build
	$ cmake .. -G"Unix Makefiles" -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS="-Wall -funroll-loops -march=native -fvisibility=hidden -fvisibility-inlines-hidden"
	$ make -j4

