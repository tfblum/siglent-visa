'''
Class to manage SDG2000X instrument

@version: v0.2.0

@author: Francesco Gramazio, Thomas Blum (tfblum)
@contact: francesco.gramazio@lab3841.it
'''

from typing import Union, Optional
from visa_instruments import VisaInstruments

class SDG2000X(VisaInstruments):   
    '''
    SDG2000X instrument
    '''

    CHANNEL1 = 'C1'
    CHANNEL2 = 'C2'
    WAVEFORM_SINE = 'SINE'
    WAVEFORM_SQUARE = 'SQUARE'
    WAVEFORM_RAMP = 'RAMP'
    WAVEFORM_PULSE = 'PULSE'
    WAVEFORM_NOISE = 'NOISE'
    WAVEFORM_DC = 'DC'
    WAVEFORM_ARB = 'ARB'
    OUTPUT_ON = 'ON'
    OUTPUT_OFF = 'OFF'
    HIGH_IMPEDANCE = 0
    POLARITY_INVERTED = 'INVT'
    POLARITY_NORMAL = 'NOR'
        
    def get_output_state(self, channel: str):
        '''
        Returns the output state, load and polarity parameters 
        value of the set channel
        
        Args:
        channel: the set channel
        '''

        query = f'{channel}:OUTP?'
        response = self.instr.query(query)
        fields = response.strip().split(',')       
        
        # creates a dictionary
        instrument_dict = {}
        first = fields[0].strip().split(' ')
        if len(first) == 2:
            key, value = first
        if key in ('C1:OUTP', 'C2:OUTP'):
            instrument_dict['state'] = value

        rest = fields[1:]       
        for i in range(0, len(rest) - 1, 2):
            key = rest[i].strip()
            value = rest[i + 1].strip()

            if key == 'LOAD':
                if value == 'HZ':
                    instrument_dict['load'] = SDG2000X.HIGH_IMPEDANCE
                else:
                    instrument_dict['load'] = float(value)
            if key == 'POWERON_STATE':
                instrument_dict['poweron_state'] = float(value)
            if key == 'PLRT':
                instrument_dict['polarity'] = value

        return instrument_dict
    
    def get_wave_info(self, channel: str):
        '''
        Returns wave information of the set channel

        Args:
        channel: the set channel
        '''
        query = f'{channel}:BSWV?'
        response = self.instr.query(query)
        fields = response.strip().split(',')

        # creates a dictionary
        instrument_dict = {}
        for i in range(0, len(fields), 2):
            key = fields[i].strip()
            value = fields[i + 1].strip()

            if key in ('C1:BSWV WVTP', 'C2:BSWV WVTP'):
                instrument_dict['type'] = value
            if key == 'FRQ':
                instrument_dict['frequency'] = float(value.replace('HZ', ''))
            if key == 'PERI':
                instrument_dict['period'] = float(value.replace('S', ''))
            if key == 'AMP':
                instrument_dict['amplitude'] = float(value.replace('V', ''))
            if key == 'AMPVRMS':
                instrument_dict['amp_vrms'] = float(value.replace('Vrms', ''))
            if key == 'AMPDBM':
                instrument_dict['amp_dbm'] = float(value.replace('dBm', ''))
            if key == 'MAX_OUTPUT_AMP':
                instrument_dict['max_output_amp'] = float(value.replace('V', ''))
            if key == 'OFST':
                instrument_dict['offset'] = float(value.replace('V', ''))
            if key == 'HLEV':
                instrument_dict['high_level'] = float(value.replace('V', ''))
            if key == 'LLEV':
                instrument_dict['low_level'] = float(value.replace('V', ''))
            if key == 'PHSE':
                instrument_dict['phase'] = float(value)
            if key == 'DUTY':
                instrument_dict['duty'] = float(value)
            if key == 'BANDSTATE':
                instrument_dict['bandstate'] = value
            if key == 'SYM':
                instrument_dict['symmetry'] = float(value)
            if key == 'WIDTH':
                instrument_dict['width'] = float(value)
            if key == 'RISE':
                instrument_dict['rise'] = float(value.replace('S', ''))
            if key == 'FALL':
                instrument_dict['fall'] = float(value.replace('S', ''))
            if key == 'DLY':
                instrument_dict['delay'] = float(value)
            if key == 'STDEV':
                instrument_dict['stdev'] = float(value.replace('V', ''))
            if key == 'MEAN':
                instrument_dict['mean'] = float(value.replace('V', ''))

        return instrument_dict
    
    def get_store_list(self):
        '''
        Used to read the stored wave data names
        '''
        query = 'STL?'
        response = self.instr.query(query)
        fields = response.replace('STL','').split(',')
        
        # creates a dictionary
        instrument_dict = {}
        counts = 0
        
        for i in range(0, len(fields) - 1, 2):
            counts += 1
            key = fields[i].strip()
            value = fields[i + 1].strip()
            instrument_dict[int(key.replace('M', ''))] = value

        return dict(sorted(instrument_dict.items()))
    
    def get_arb_wave_type(self, channel):
        '''
        Return arb wave type of the set channel

        Args:
        channel: the set channel (C1, C2)
        '''
        query = f'{channel}:ARWV?'
        response = self.instr.query(query)

        response = self.instr.query(query)
        if channel == SDG2000X.CHANNEL1:
            fields = response.replace('C1:ARWV','').split(',')
        elif channel == SDG2000X.CHANNEL2:
            fields = response.replace('C2:ARWV','').split(',')

        # creates a dictionary
        instrument_dict = {}
        for i in range(0, len(fields) - 1, 2):
            key = fields[i].strip()
            value = fields[i + 1].strip()

            if key == 'INDEX':
                instrument_dict['index'] = int(value)
            if key == 'NAME':
                instrument_dict['name'] = value

        return instrument_dict

    def set_waveform(self, channel: str, type):
        '''
        Can set waveform of set channel
        
        Args:
        channel: the set channel (C1, C2)
        type: type of waveform (SINE, SQUARE, RAMP, PULSE, NOISE, DC, ARB)
        '''
        write = f'{channel}:BSWV WVTP,{type}'
        self.instr.write(write)

    def set_wave_frequency(self, channel: str, frequency: float):
        '''
        Can set frequency of set channel

        Args:
        channel: the set channel (C1, C2)
        frequency: wave frequency (Hz)        
        '''
        write = f'{channel}:BSWV FRQ,{frequency}'
        self.instr.write(write)

    def set_wave_period(self, channel: str, period: float):
        '''
        Can set period of set channel

        Args:
        channel: the set channel (C1, C2)
        period: wave period (s)        
        '''
        write = f'{channel}:BSWV PERI,{period}'
        self.instr.write(write)

    def set_wave_amplitude(self, channel: str, amplitude: float):
        '''
        Can set amplitude of set channel

        Args:
        channel: the set channel (C1, C2)
        amplitude: wave amplitude (V)        
        '''
        write = f'{channel}:BSWV AMP,{amplitude}'
        self.instr.write(write)

    def set_wave_offset(self, channel: str, offset: float):
        '''
        Can set offset of set channel

        Args:
        channel: the set channel (C1, C2)
        offset: wave offset (V)        
        '''
        write = f'{channel}:BSWV OFST,{offset}'
        self.instr.write(write)

    def set_wave_symmetry(self, channel: str, symmetry: float):
        '''
        Can set symmetry of set channel

        Args:
        channel: the set channel (C1, C2)
        symmetry: wave symmetry (%)        
        '''
        write = f'{channel}:BSWV SYM,{symmetry}'
        self.instr.write(write)

    def set_wave_duty(self, channel: str, duty):
        '''
        Can set duty of set channel

        Args:
        channel: the set channel (C1, C2)
        duty: wave duty (%)        
        '''
        write = f'{channel}:BSWV DUTY,{duty}'
        self.instr.write(write)

    def set_wave_phase(self, channel: str, phase: float):
        '''
        Can set phase of set channel

        Args:
        channel: the set channel (C1, C2)
        phase: wave phase (°)        
        '''
        write = f'{channel}:BSWV PHSE,{phase}'
        self.instr.write(write)

    def set_wave_stdev(self, channel: str, stdev: float):
        '''
        Can set stdev of set channel

        Args:
        channel: the set channel (C1, C2)
        stdev: wave stdev (V)        
        '''
        write = f'{channel}:BSWV STDEV,{stdev}'
        self.instr.write(write)

    def set_wave_mean(self, channel: str, mean: float):
        '''
        Can set mean of set channel

        Args:
        channel: the set channel (C1, C2)
        mean: wave mean (V)                
        '''
        write = f'{channel}:BSWV MEAN,{mean}'
        self.instr.write(write)

    def set_wave_width(self, channel: str, width: float):
        '''
        Can set width of set channel

        Args:
        channel: the set channel (C1, C2)
        width: wave widht (Hz)        
        '''
        write = f'{channel}:BSWV WIDTH,{width}'
        self.instr.write(write)

    def set_wave_rise(self, channel: str, rise: float):
        '''
        Can set rise of set channel

        Args:
        channel: the set channel (C1, C2)
        rise: wave rise (s) 
        '''
        write = f'{channel}:BSWV RISE,{rise}'
        self.instr.write(write)

    def set_wave_fall(self, channel: str, fall: float):
        '''
        Can set fall of set channel

        Args:
        channel: the set channel (C1, C2)
        fall: wave fall (s) 
        '''
        write = f'{channel}:BSWV FALL,{fall}'
        self.instr.write(write)

    def set_wave_delay(self, channel: str, delay: float):
        '''
        Can set delay of set channel

        Args:
        channel: the set channel (C1, C2)
        delay: wave delay (s) 
        '''
        write = f'{channel}:BSWV DLY,{delay}'
        self.instr.write(write)

    def set_wave_high_level(self, channel: str, high_level: float):
        '''
        Can set high_level of set channel

        Args:
        channel: the set channel (C1, C2)
        high_level: wave high_level (V) 
        '''
        write = f'{channel}:BSWV HLEV,{high_level}'
        self.instr.write(write)

    def set_wave_low_level(self, channel: str, low_level: float):
        '''
        Can set low_level of set channel

        Args:
        channel: the set channel (C1, C2)
        low_level: wave low_level (V) 
        '''
        write = f'{channel}:BSWV LLEV,{low_level}'
        self.instr.write(write)

    def set_output_state(self, channel: str, state: str):
        '''
        Can set output state of set channel

        Args:
        channel: the set channel (C1, C2)
        state: output state (ON, OFF)
        '''
        write = f'{channel}:OUTP {state}'
        self.instr.write(write)

    def set_output_load(self, channel: str, load: Union[str, int]):
        '''
        Can set load output of set channel

        Args:
        channel: the set channel (C1, C2)
        load: output load (50~10000, HZ)
        '''
        if load == SDG2000X.HIGH_IMPEDANCE:
            write = f'{channel}:OUTP LOAD, HZ'
        else:
            write = f'{channel}:OUTP LOAD, {load}'
        
        self.instr.write(write)

    def set_output_polarity(self, channel: str, polarity: str):

        '''
        Can set polarity output of set channel

        Args:
        channel: the set channel (C1, C2)
        polarity: output polarity (INVT, NOR)
        '''
        write = f'{channel}:OUTP PLRT, {polarity}'
        self.instr.write(write)

    def set_arb_wave_type(self, channel, index: int):
        '''
        Can sets arbitrary wave type by name or index

        Args:
        channel: the set channel (C1, C2)
        index: index of arbitrary wave
        '''
        write = f'{channel}:ARWV INDEX, {index}'
        self.instr.write(write)
    
    # Advanced modulation methods
    def set_modulation(self, channel: str, state: str, mod_type: Optional[str] = None, 
                      frequency: Optional[float] = None, depth: Optional[float] = None):
        '''
        Set modulation parameters
        
        Args:
            channel: the set channel (C1, C2)
            state: modulation state (ON, OFF)
            mod_type: modulation type (AM, FM, PM, etc.)
            frequency: modulation frequency
            depth: modulation depth
        '''
        # Enable/disable modulation
        write = f'{channel}:MDWV STATE,{state}'
        self.instr.write(write)
        
        if state.upper() == 'ON' and mod_type:
            # Set modulation type and parameters
            if mod_type:
                write = f'{channel}:MDWV {mod_type}'
                if frequency:
                    write += f',FRQ,{frequency}'
                if depth:
                    if mod_type == 'AM':
                        write += f',DEPTH,{depth}'
                    elif mod_type == 'FM':
                        write += f',DEVI,{depth}'
                self.instr.write(write)
    
    def get_modulation_settings(self, channel: str):
        '''
        Get modulation settings for a channel
        
        Args:
            channel: the set channel (C1, C2)
        '''
        query = f'{channel}:MDWV?'
        response = self.instr.query(query)
        fields = response.strip().split(',')
        
        # Parse modulation settings
        instrument_dict = {}
        for i in range(0, len(fields), 2):
            if i + 1 < len(fields):
                key = fields[i].strip()
                value = fields[i + 1].strip()
                instrument_dict[key.lower()] = value
        
        return instrument_dict
    
    # Burst mode methods
    def set_burst(self, channel: str, state: str, n_cycle: Optional[int] = None, 
                  period: Optional[float] = None, trigger_source: Optional[str] = None):
        '''
        Set burst parameters
        
        Args:
            channel: the set channel (C1, C2)
            state: burst state (ON, OFF)
            n_cycle: number of cycles
            period: burst period
            trigger_source: trigger source (MAN, CH1, CH2, EXT)
        '''
        # Enable/disable burst
        write = f'{channel}:BTWV STATE,{state}'
        self.instr.write(write)
        
        if state.upper() == 'ON':
            # Set burst parameters
            if n_cycle:
                write = f'{channel}:BTWV GATE_NCYC,{n_cycle}'
                self.instr.write(write)
            if period:
                write = f'{channel}:BTWV PRD,{period}'
                self.instr.write(write)
            if trigger_source:
                write = f'{channel}:BTWV TRSR,{trigger_source}'
                self.instr.write(write)
    
    def get_burst_settings(self, channel: str):
        '''
        Get burst settings for a channel
        
        Args:
            channel: the set channel (C1, C2)
        '''
        query = f'{channel}:BTWV?'
        response = self.instr.query(query)
        fields = response.strip().split(',')
        
        # Parse burst settings
        instrument_dict = {}
        for i in range(0, len(fields), 2):
            if i + 1 < len(fields):
                key = fields[i].strip()
                value = fields[i + 1].strip()
                instrument_dict[key.lower()] = value
        
        return instrument_dict
    
    # Sweep methods
    def set_sweep(self, channel: str, state: str, start_freq: Optional[float] = None,
                  stop_freq: Optional[float] = None, sweep_time: Optional[float] = None, 
                  sweep_type: Optional[str] = None):
        '''
        Set frequency sweep parameters
        
        Args:
            channel: the set channel (C1, C2)
            state: sweep state (ON, OFF)
            start_freq: start frequency
            stop_freq: stop frequency
            sweep_time: sweep time
            sweep_type: sweep type (LIN, LOG)
        '''
        # Enable/disable sweep
        write = f'{channel}:SWWV STATE,{state}'
        self.instr.write(write)
        
        if state.upper() == 'ON':
            # Set sweep parameters
            if start_freq:
                write = f'{channel}:SWWV STFR,{start_freq}'
                self.instr.write(write)
            if stop_freq:
                write = f'{channel}:SWWV SPFR,{stop_freq}'
                self.instr.write(write)
            if sweep_time:
                write = f'{channel}:SWWV TIME,{sweep_time}'
                self.instr.write(write)
            if sweep_type:
                write = f'{channel}:SWWV SWTP,{sweep_type}'
                self.instr.write(write)
    
    def get_sweep_settings(self, channel: str):
        '''
        Get sweep settings for a channel
        
        Args:
            channel: the set channel (C1, C2)
        '''
        query = f'{channel}:SWWV?'
        response = self.instr.query(query)
        fields = response.strip().split(',')
        
        # Parse sweep settings
        instrument_dict = {}
        for i in range(0, len(fields), 2):
            if i + 1 < len(fields):
                key = fields[i].strip()
                value = fields[i + 1].strip()
                instrument_dict[key.lower()] = value
        
        return instrument_dict
    
    # Arbitrary waveform methods
    def upload_arbitrary_waveform(self, channel: str, name: str, data: list, 
                                  sample_rate: Optional[float] = None):
        '''
        Upload arbitrary waveform data
        
        Args:
            channel: the set channel (C1, C2)
            name: waveform name
            data: waveform data points (list of values)
            sample_rate: sample rate
        '''
        # Convert data to comma-separated string
        data_str = ','.join([str(point) for point in data])
        
        # Upload waveform data
        write = f'{channel}:WVDT WVNM,{name},{data_str}'
        self.instr.write(write)
        
        if sample_rate:
            write = f'{channel}:WVDT WVNM,{name},SMPL_RATE,{sample_rate}'
            self.instr.write(write)
    
    def select_arbitrary_waveform(self, channel: str, name: str):
        '''
        Select an arbitrary waveform by name
        
        Args:
            channel: the set channel (C1, C2)
            name: waveform name
        '''
        write = f'{channel}:ARWV NAME,{name}'
        self.instr.write(write)
    
    def delete_arbitrary_waveform(self, name: str):
        '''
        Delete an arbitrary waveform
        
        Args:
            name: waveform name to delete
        '''
        write = f'WVDT DL,{name}'
        self.instr.write(write)
    
    def list_arbitrary_waveforms(self):
        '''
        List all stored arbitrary waveforms
        
        Returns:
            List of waveform names
        '''
        response = self.instr.query('STL?')
        # Parse the response to extract waveform names
        waveforms = []
        if response:
            # STL response format: "STL M1,SINE,M2,USER,..."
            parts = response.replace('STL', '').strip().split(',')
            for i in range(1, len(parts), 2):  # Skip indices, get names
                if i < len(parts):
                    waveforms.append(parts[i].strip())
        return waveforms