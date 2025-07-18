# siglent-visa
This package is a big project where I try to provide a library of functions that can be applied with siglent tools using the visa library. 
Is an expanding project, where for now a set of functions has been created for sdg2000x instrument, tips and requests are welcome!

## sdg2000x

sdg2000x is a part of package that can be used with sdg2000x instruments, it provides some basic function to manage the wave and in this part of package there is a class that provides some general function for visa instruments like get info, reset and self-test.
This project can be used as an initial basis, but in the future it may also be updated by implementing new functions

### Basic functionality

- set every basic parametry of wave
- get every basic parametry of wave
- get instrument info, reset, self-test
- get and set arbitrary wave type
- file with test for every function

# Installation

```bash
pip install siglent-visa
```