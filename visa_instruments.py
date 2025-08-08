'''
Class to manage visa instruments

@version: v0.2.0

@requires: pip install pyvisa

@author: Francesco Gramazio, Thomas Blum (tfblum)
@contact: francesco.gramazio@lab3841.it
'''

import pyvisa

class VisaInstruments():
    def __init__(self, address: str):
        self.rm = pyvisa.ResourceManager()
        
        self.address = address
        self.instr = self.rm.open_resource(self.address)
        self.instr.write_termination = '\n'
        self.instr.read_termination = '\n'
        self.instr.query_delay = 0.1

    def get_info(self):
        ''' 
        Returns the instrument information
        '''
        response = self.instr.query('*IDN?')
        fields = response.strip().split(',')

        # creates a dictionary
        instrument_dict = {
        'device_id' : fields[0],
        'model' : fields[1], 
        'serial_number' : fields[2],
        'firmware_version' : fields[3]
        }
        
        return instrument_dict
    
    def reset(self):
        '''
        Resets the instrument
        '''
        self.instr.write('*RST')

    def self_test(self):
        '''
        Starts a self-test to finds errors
        '''
        response = self.instr.query('*TST?')

        if response == '0':
            return True
        else:
            return False
