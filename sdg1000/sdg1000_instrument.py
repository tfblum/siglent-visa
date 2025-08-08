"""
Class to manage SDG1000 instrument

Based on the SDG2000X implementation but adapted for SDG1000 series specifications.
Key differences from SDG2000X:
- Frequency range: 1 μHz – 10 MHz (vs 40 MHz)
- Amplitude range: 2 mVpp minimum (vs 1 mVpp)
- ARB memory: 4k points, 12-bit (vs 16k points, 14-bit)
- Sweep: LINEAR only (no LOG mode)
- Load impedance: 50Ω or High-Z only (no variable impedance)
- Burst cycles: 1–50,000 (vs 1–65,535)

@version: v0.2.0
@author: Francesco Gramazio, Thomas Blum (tfblum)
@reference: SDG1000 Data Sheet DS02010-E08A, Siglent API Reference
"""

from typing import Union, Optional
from visa_instruments import VisaInstruments


class SDG1000(VisaInstruments):   
    """
    SDG1000 instrument class
    
    Inherits from VisaInstruments and provides SDG1000-specific functionality
    with parameter validation and model-specific constraints.
    """

    # Channel definitions (same as SDG2000X)
    CHANNEL1 = 'C1'
    CHANNEL2 = 'C2'
    
    # Waveform type definitions (same as SDG2000X)
    WAVEFORM_SINE = 'SINE'
    WAVEFORM_SQUARE = 'SQUARE'
    WAVEFORM_RAMP = 'RAMP'
    WAVEFORM_PULSE = 'PULSE'
    WAVEFORM_NOISE = 'NOISE'
    WAVEFORM_ARB = 'ARB'
    # Note: SDG1000 does not support DC waveform
    
    # Output state definitions (same as SDG2000X)
    OUTPUT_ON = 'ON'
    OUTPUT_OFF = 'OFF'
    
    # Load impedance definitions (SDG1000 specific - limited options)
    HIGH_IMPEDANCE = 0  # Represents HZ (High impedance)
    LOAD_50_OHM = 50    # Only 50Ω supported for low impedance
    
    # Polarity definitions (same as SDG2000X)
    POLARITY_INVERTED = 'INVT'
    POLARITY_NORMAL = 'NOR'
    
    # SDG1000-specific parameter limits
    FREQ_MIN = 1e-6      # 1 μHz
    FREQ_MAX = 10e6      # 10 MHz
    AMP_MIN = 0.002      # 2 mVpp
    AMP_MAX_50_OHM = 10.0    # 10 Vpp into 50Ω
    AMP_MAX_HIGH_Z = 20.0    # 20 Vpp into High-Z
    OFFSET_MAX_50_OHM = 5.0  # ±5 V into 50Ω
    OFFSET_MAX_HIGH_Z = 10.0 # ±10 V into High-Z
    
    # Waveform-specific frequency limits
    FREQ_MAX_RAMP = 200e3    # 200 kHz for ramp/triangle
    FREQ_MAX_PULSE = 5e6     # 5 MHz for pulse
    FREQ_MAX_NOISE = 5e6     # 5 MHz for noise
    FREQ_MAX_ARB = 5e6       # 5 MHz for arbitrary waveforms
    
    # Burst mode limits (SDG1000 specific)
    BURST_CYCLES_MIN = 1
    BURST_CYCLES_MAX = 50000  # vs 65535 for SDG2000X
    
    # ARB waveform limits (SDG1000 specific)
    ARB_POINTS_MAX = 4096     # 4k points vs 16k for SDG2000X
    ARB_RESOLUTION = 12       # 12-bit vs 14-bit for SDG2000X

    def __init__(self, address: str):
        """Initialize SDG1000 instrument"""
        super().__init__(address)
        self.model_name = "SDG1000"
        
    def _validate_frequency(self, frequency: float, waveform_type: Optional[str] = None) -> bool:
        """
        Validate frequency against SDG1000 specifications
        
        Args:
            frequency: Frequency in Hz
            waveform_type: Optional waveform type for type-specific limits
            
        Returns:
            bool: True if frequency is valid
            
        Raises:
            ValueError: If frequency is out of range
        """
        if frequency < self.FREQ_MIN or frequency > self.FREQ_MAX:
            raise ValueError(f"Frequency {frequency} Hz out of range "
                           f"({self.FREQ_MIN} Hz - {self.FREQ_MAX} Hz) for SDG1000")
        
        # Check waveform-specific limits
        if waveform_type == self.WAVEFORM_RAMP and frequency > self.FREQ_MAX_RAMP:
            raise ValueError(f"Frequency {frequency} Hz exceeds RAMP limit "
                           f"({self.FREQ_MAX_RAMP} Hz) for SDG1000")
        elif waveform_type == self.WAVEFORM_PULSE and frequency > self.FREQ_MAX_PULSE:
            raise ValueError(f"Frequency {frequency} Hz exceeds PULSE limit "
                           f"({self.FREQ_MAX_PULSE} Hz) for SDG1000")
        elif waveform_type == self.WAVEFORM_NOISE and frequency > self.FREQ_MAX_NOISE:
            raise ValueError(f"Frequency {frequency} Hz exceeds NOISE limit "
                           f"({self.FREQ_MAX_NOISE} Hz) for SDG1000")
        elif waveform_type == self.WAVEFORM_ARB and frequency > self.FREQ_MAX_ARB:
            raise ValueError(f"Frequency {frequency} Hz exceeds ARB limit "
                           f"({self.FREQ_MAX_ARB} Hz) for SDG1000")
        
        return True
    
    def _validate_amplitude(self, amplitude: float, load_impedance: Optional[int] = None) -> bool:
        """
        Validate amplitude against SDG1000 specifications
        
        Args:
            amplitude: Amplitude in Vpp
            load_impedance: Load impedance (50 or HIGH_IMPEDANCE)
            
        Returns:
            bool: True if amplitude is valid
            
        Raises:
            ValueError: If amplitude is out of range
        """
        if amplitude < self.AMP_MIN:
            raise ValueError(f"Amplitude {amplitude} V below minimum "
                           f"({self.AMP_MIN} V) for SDG1000")
        
        # Check load-dependent limits
        if load_impedance == self.LOAD_50_OHM:
            if amplitude > self.AMP_MAX_50_OHM:
                raise ValueError(f"Amplitude {amplitude} V exceeds 50Ω limit "
                               f"({self.AMP_MAX_50_OHM} V) for SDG1000")
        elif load_impedance == self.HIGH_IMPEDANCE:
            if amplitude > self.AMP_MAX_HIGH_Z:
                raise ValueError(f"Amplitude {amplitude} V exceeds High-Z limit "
                               f"({self.AMP_MAX_HIGH_Z} V) for SDG1000")
        else:
            # Default to more restrictive 50Ω limit if unknown
            if amplitude > self.AMP_MAX_50_OHM:
                raise ValueError(f"Amplitude {amplitude} V exceeds default limit "
                               f"({self.AMP_MAX_50_OHM} V) for SDG1000")
        
        return True
    
    def _validate_load_impedance(self, load: int) -> bool:
        """
        Validate load impedance against SDG1000 specifications
        
        Args:
            load: Load impedance value
            
        Returns:
            bool: True if load is valid
            
        Raises:
            ValueError: If load impedance is not supported
        """
        if load not in [self.LOAD_50_OHM, self.HIGH_IMPEDANCE]:
            raise ValueError(f"Load impedance {load} not supported by SDG1000. "
                           f"Supported values: {self.LOAD_50_OHM}Ω, High-Z")
        return True
    
    # Override methods with SDG1000-specific validation
    
    def get_output_state(self, channel: str):
        """
        Returns the output state, load and polarity parameters 
        value of the set channel (same as SDG2000X implementation)
        
        Args:
            channel: the set channel
        """
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
                    instrument_dict['load'] = SDG1000.HIGH_IMPEDANCE
                else:
                    instrument_dict['load'] = float(value)
            if key == 'POWERON_STATE':
                instrument_dict['poweron_state'] = float(value)
            if key == 'PLRT':
                instrument_dict['polarity'] = value

        return instrument_dict
    
    def get_wave_info(self, channel: str):
        """
        Returns wave information of the set channel (same as SDG2000X implementation)

        Args:
            channel: the set channel
        """
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
        """
        Used to read the stored wave data names (same as SDG2000X implementation)
        """
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
        """
        Return arb wave type of the set channel (same as SDG2000X implementation)

        Args:
            channel: the set channel (C1, C2)
        """
        query = f'{channel}:ARWV?'
        response = self.instr.query(query)

        if channel == SDG1000.CHANNEL1:
            fields = response.replace('C1:ARWV','').split(',')
        elif channel == SDG1000.CHANNEL2:
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

    # Setter methods with SDG1000-specific validation
    
    def set_waveform(self, channel: str, waveform_type: str):
        """
        Can set waveform of set channel (with SDG1000 validation)
        
        Args:
            channel: the set channel (C1, C2)
            waveform_type: type of waveform (SINE, SQUARE, RAMP, PULSE, NOISE, ARB)
            
        Raises:
            ValueError: If waveform type is not supported by SDG1000
        """
        supported_waveforms = [
            self.WAVEFORM_SINE, self.WAVEFORM_SQUARE, self.WAVEFORM_RAMP,
            self.WAVEFORM_PULSE, self.WAVEFORM_NOISE, self.WAVEFORM_ARB
        ]
        
        if waveform_type not in supported_waveforms:
            raise ValueError(f"Waveform type '{waveform_type}' not supported by SDG1000. "
                           f"Supported types: {supported_waveforms}")
        
        write = f'{channel}:BSWV WVTP,{waveform_type}'
        self.instr.write(write)

    def set_wave_frequency(self, channel: str, frequency: float):
        """
        Can set frequency of set channel (with SDG1000 validation)

        Args:
            channel: the set channel (C1, C2)
            frequency: wave frequency (Hz)
            
        Raises:
            ValueError: If frequency is out of SDG1000 range
        """
        # Get current waveform type for type-specific validation
        try:
            wave_info = self.get_wave_info(channel)
            waveform_type = wave_info.get('type')
        except:
            waveform_type = None
            
        self._validate_frequency(frequency, waveform_type)
        
        write = f'{channel}:BSWV FRQ,{frequency}'
        self.instr.write(write)

    def set_wave_period(self, channel: str, period: float):
        """
        Can set period of set channel (with SDG1000 validation)

        Args:
            channel: the set channel (C1, C2)
            period: wave period (s)
        """
        frequency = 1.0 / period if period > 0 else 0
        
        # Get current waveform type for type-specific validation
        try:
            wave_info = self.get_wave_info(channel)
            waveform_type = wave_info.get('type')
        except:
            waveform_type = None
            
        self._validate_frequency(frequency, waveform_type)
        
        write = f'{channel}:BSWV PERI,{period}'
        self.instr.write(write)

    def set_wave_amplitude(self, channel: str, amplitude: float):
        """
        Can set amplitude of set channel (with SDG1000 validation)

        Args:
            channel: the set channel (C1, C2)
            amplitude: wave amplitude (V)
        """
        # Get current load impedance for validation
        try:
            output_info = self.get_output_state(channel)
            load_impedance = output_info.get('load', self.LOAD_50_OHM)
        except:
            load_impedance = self.LOAD_50_OHM  # Default to more restrictive
            
        self._validate_amplitude(amplitude, load_impedance)
        
        write = f'{channel}:BSWV AMP,{amplitude}'
        self.instr.write(write)

    def set_wave_offset(self, channel: str, offset: float):
        """
        Can set offset of set channel (with SDG1000 validation)

        Args:
            channel: the set channel (C1, C2)
            offset: wave offset (V)
        """
        # Get current load impedance for validation
        try:
            output_info = self.get_output_state(channel)
            load_impedance = output_info.get('load', self.LOAD_50_OHM)
        except:
            load_impedance = self.LOAD_50_OHM  # Default to more restrictive
            
        max_offset = self.OFFSET_MAX_50_OHM if load_impedance == self.LOAD_50_OHM else self.OFFSET_MAX_HIGH_Z
        
        if abs(offset) > max_offset:
            raise ValueError(f"Offset {offset} V exceeds limit "
                           f"(±{max_offset} V) for SDG1000")
        
        write = f'{channel}:BSWV OFST,{offset}'
        self.instr.write(write)

    def set_output_load(self, channel: str, load: Union[str, int]):
        """
        Can set load output of set channel (with SDG1000 validation)

        Args:
            channel: the set channel (C1, C2)
            load: output load (50, HZ for SDG1000)
        """
        if isinstance(load, str) and load == 'HZ':
            load_value = self.HIGH_IMPEDANCE
        else:
            load_value = int(load)
            
        self._validate_load_impedance(load_value)
        
        if load_value == self.HIGH_IMPEDANCE:
            write = f'{channel}:OUTP LOAD,HZ'
        else:
            write = f'{channel}:OUTP LOAD,{load_value}'
        
        self.instr.write(write)

    # The following methods are identical to SDG2000X and don't need SDG1000-specific validation
    
    def set_wave_symmetry(self, channel: str, symmetry: float):
        """Can set symmetry of set channel (same as SDG2000X)"""
        write = f'{channel}:BSWV SYM,{symmetry}'
        self.instr.write(write)

    def set_wave_duty(self, channel: str, duty):
        """Can set duty of set channel (same as SDG2000X)"""
        write = f'{channel}:BSWV DUTY,{duty}'
        self.instr.write(write)

    def set_wave_phase(self, channel: str, phase: float):
        """Can set phase of set channel (same as SDG2000X)"""
        write = f'{channel}:BSWV PHSE,{phase}'
        self.instr.write(write)

    def set_wave_stdev(self, channel: str, stdev: float):
        """Can set stdev of set channel (same as SDG2000X)"""
        write = f'{channel}:BSWV STDEV,{stdev}'
        self.instr.write(write)

    def set_wave_mean(self, channel: str, mean: float):
        """Can set mean of set channel (same as SDG2000X)"""
        write = f'{channel}:BSWV MEAN,{mean}'
        self.instr.write(write)

    def set_wave_width(self, channel: str, width: float):
        """Can set width of set channel (same as SDG2000X)"""
        write = f'{channel}:BSWV WIDTH,{width}'
        self.instr.write(write)

    def set_wave_rise(self, channel: str, rise: float):
        """Can set rise of set channel (same as SDG2000X)"""
        write = f'{channel}:BSWV RISE,{rise}'
        self.instr.write(write)

    def set_wave_fall(self, channel: str, fall: float):
        """Can set fall of set channel (same as SDG2000X)"""
        write = f'{channel}:BSWV FALL,{fall}'
        self.instr.write(write)

    def set_wave_delay(self, channel: str, delay: float):
        """Can set delay of set channel (same as SDG2000X)"""
        write = f'{channel}:BSWV DLY,{delay}'
        self.instr.write(write)

    def set_wave_high_level(self, channel: str, high_level: float):
        """Can set high_level of set channel (same as SDG2000X)"""
        write = f'{channel}:BSWV HLEV,{high_level}'
        self.instr.write(write)

    def set_wave_low_level(self, channel: str, low_level: float):
        """Can set low_level of set channel (same as SDG2000X)"""
        write = f'{channel}:BSWV LLEV,{low_level}'
        self.instr.write(write)

    def set_output_state(self, channel: str, state: str):
        """Can set output state of set channel (same as SDG2000X)"""
        write = f'{channel}:OUTP {state}'
        self.instr.write(write)

    def set_output_polarity(self, channel: str, polarity: str):
        """Can set polarity output of set channel (same as SDG2000X)"""
        write = f'{channel}:OUTP PLRT,{polarity}'
        self.instr.write(write)

    def set_arb_wave_type(self, channel, index: int):
        """Can sets arbitrary wave type by name or index (same as SDG2000X)"""
        write = f'{channel}:ARWV INDEX,{index}'
        self.instr.write(write)

    # Advanced feature methods (adapted for SDG1000)
    
    def set_modulation(self, channel: str, state: str, mod_type: Optional[str] = None, 
                      frequency: Optional[float] = None, depth: Optional[float] = None):
        """
        Set modulation parameters (adapted for SDG1000)
        
        Args:
            channel: the set channel (C1, C2)
            state: modulation state (ON, OFF)
            mod_type: modulation type (AM, FM, PM, etc.)
            frequency: modulation frequency
            depth: modulation depth
        """
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
        """
        Get modulation settings for a channel (same as SDG2000X)
        
        Args:
            channel: the set channel (C1, C2)
        """
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

    def set_burst(self, channel: str, state: str, n_cycle: Optional[int] = None, 
                  period: Optional[float] = None, trigger_source: Optional[str] = None):
        """
        Set burst parameters (adapted for SDG1000)
        
        Args:
            channel: the set channel (C1, C2)
            state: burst state (ON, OFF)
            n_cycle: number of cycles (1-50000 for SDG1000)
            period: burst period
            trigger_source: trigger source (MAN, CH1, CH2, EXT)
        """
        # Validate burst cycles for SDG1000
        if n_cycle is not None:
            if not (self.BURST_CYCLES_MIN <= n_cycle <= self.BURST_CYCLES_MAX):
                raise ValueError(f"Burst cycles {n_cycle} out of range "
                               f"({self.BURST_CYCLES_MIN}-{self.BURST_CYCLES_MAX}) for SDG1000")
        
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
        """
        Get burst settings for a channel (same as SDG2000X)
        
        Args:
            channel: the set channel (C1, C2)
        """
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

    def set_sweep(self, channel: str, state: str, start_freq: Optional[float] = None,
                  stop_freq: Optional[float] = None, sweep_time: Optional[float] = None, 
                  sweep_type: Optional[str] = None):
        """
        Set frequency sweep parameters (adapted for SDG1000 - LINEAR only)
        
        Args:
            channel: the set channel (C1, C2)
            state: sweep state (ON, OFF)
            start_freq: start frequency
            stop_freq: stop frequency
            sweep_time: sweep time
            sweep_type: sweep type (LIN only for SDG1000)
        """
        # SDG1000 only supports LINEAR sweep
        if sweep_type and sweep_type.upper() != 'LIN':
            raise ValueError(f"SDG1000 only supports LINEAR sweep. Got: {sweep_type}")
        
        # Enable/disable sweep
        write = f'{channel}:SWWV STATE,{state}'
        self.instr.write(write)
        
        if state.upper() == 'ON':
            # Set sweep parameters
            if start_freq:
                self._validate_frequency(start_freq)
                write = f'{channel}:SWWV STFR,{start_freq}'
                self.instr.write(write)
            if stop_freq:
                self._validate_frequency(stop_freq)
                write = f'{channel}:SWWV SPFR,{stop_freq}'
                self.instr.write(write)
            if sweep_time:
                write = f'{channel}:SWWV TIME,{sweep_time}'
                self.instr.write(write)
            if sweep_type:
                write = f'{channel}:SWWV SWTP,{sweep_type}'
                self.instr.write(write)

    def get_sweep_settings(self, channel: str):
        """
        Get sweep settings for a channel (same as SDG2000X)
        
        Args:
            channel: the set channel (C1, C2)
        """
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

    # Arbitrary waveform methods (adapted for SDG1000 limits)
    
    def upload_arbitrary_waveform(self, channel: str, name: str, data: list, 
                                  sample_rate: Optional[float] = None):
        """
        Upload arbitrary waveform data (adapted for SDG1000 limits)
        
        Args:
            channel: the set channel (C1, C2)
            name: waveform name
            data: waveform data points (max 4096 for SDG1000)
            sample_rate: sample rate
        """
        # Validate data length for SDG1000
        if len(data) > self.ARB_POINTS_MAX:
            raise ValueError(f"Waveform data length {len(data)} exceeds SDG1000 limit "
                           f"({self.ARB_POINTS_MAX} points)")
        
        # Convert data to comma-separated string
        data_str = ','.join([str(point) for point in data])
        
        # Upload waveform data
        write = f'{channel}:WVDT WVNM,{name},{data_str}'
        self.instr.write(write)
        
        if sample_rate:
            write = f'{channel}:WVDT WVNM,{name},SMPL_RATE,{sample_rate}'
            self.instr.write(write)

    def select_arbitrary_waveform(self, channel: str, name: str):
        """
        Select an arbitrary waveform by name (same as SDG2000X)
        
        Args:
            channel: the set channel (C1, C2)
            name: waveform name
        """
        write = f'{channel}:ARWV NAME,{name}'
        self.instr.write(write)
    
    def delete_arbitrary_waveform(self, name: str):
        """
        Delete an arbitrary waveform (same as SDG2000X)
        
        Args:
            name: waveform name to delete
        """
        write = f'WVDT DL,{name}'
        self.instr.write(write)

    def list_arbitrary_waveforms(self):
        """
        List all stored arbitrary waveforms (same as SDG2000X)
        
        Returns:
            List of waveform names
        """
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
        self.instr.write(write)

    def set_wave_low_level(self, channel: str, low_level: float):
        """Can set low_level of set channel (same as SDG2000X)"""
        write = f'{channel}:BSWV LLEV,{low_level}'
        self.instr.write(write)

    def set_output_state(self, channel: str, state: str):
        """Can set output state of set channel (same as SDG2000X)"""
        write = f'{channel}:OUTP {state}'
        self.instr.write(write)

    def set_output_polarity(self, channel: str, polarity: str):
        """Can set polarity output of set channel (same as SDG2000X)"""
        write = f'{channel}:OUTP PLRT,{polarity}'
        self.instr.write(write)

    def set_arb_wave_type(self, channel, index: int):
        """Can sets arbitrary wave type by index (same as SDG2000X)"""
        write = f'{channel}:ARWV INDEX,{index}'
        self.instr.write(write)
