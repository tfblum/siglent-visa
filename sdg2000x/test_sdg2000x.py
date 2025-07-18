'''
Class to test SDG2000X instrument

@version: v0.1.0

@author: Francesco Gramazio
@contact: francesco.gramazio@lab3841.it
'''

import unittest
from sdg2000x.sdg2000x_instrument import *

class testsdg2000x(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.device = SDG2000X('TCPIP0::192.168.38.153::inst0::INSTR')

    def test_get_info(self):
        response = self.device.get_info()
        self.assertIn('device_id', response)

    def test_get_store_list(self):
        response = self.device.get_store_list()
        self.assertIn(10, response)

    def test_get_output_state(self):
        for channel in [SDG2000X.CHANNEL1, SDG2000X.CHANNEL2]:
            response = self.device.get_output_state(channel)
            self.assertIn('state', response)

    def test_get_arb_wave_type(self):
        for channel in [SDG2000X.CHANNEL1, SDG2000X.CHANNEL2]:
            response = self.device.get_arb_wave_type(channel)
            self.assertIn('index', response)

    def test_reset(self):
        for channel in [SDG2000X.CHANNEL1, SDG2000X.CHANNEL2]:
            self.device.set_waveform(channel, SDG2000X.WAVEFORM_PULSE)
            self.device.set_wave_frequency(channel, 1430)

        self.device.reset()

        for channel in [SDG2000X.CHANNEL1, SDG2000X.CHANNEL2]:
            response = self.device.get_wave_info(channel)
            self.assertEqual(response['type'], 'SINE')
            self.assertEqual(response['frequency'], 1000)

    def test_self_test(self):
        response = self.device.self_test()
        self.assertEqual(response, True)

    def test_set_waveform(self):
        for type in [SDG2000X.WAVEFORM_NOISE, SDG2000X.WAVEFORM_SQUARE, SDG2000X.WAVEFORM_RAMP, SDG2000X.WAVEFORM_PULSE, SDG2000X.WAVEFORM_NOISE, SDG2000X.WAVEFORM_DC, SDG2000X.WAVEFORM_ARB]:
            for channel in [SDG2000X.CHANNEL1, SDG2000X.CHANNEL2]:
                self.device.set_waveform(channel, type)
                response = self.device.get_wave_info(channel)
                self.assertEqual(response['type'], type)

    def test_set_wave_frequency(self):
        for channel in [SDG2000X.CHANNEL1, SDG2000X.CHANNEL2]:
            self.device.set_waveform(channel, SDG2000X.WAVEFORM_SINE)
            frequency = 100
            self.device.set_wave_frequency(channel, frequency)
            response = self.device.get_wave_info(channel)
            self.assertEqual(response['frequency'], frequency)

    def test_set_wave_period(self):
        for channel in [SDG2000X.CHANNEL1, SDG2000X.CHANNEL2]:
            self.device.set_waveform(channel, SDG2000X.WAVEFORM_SINE)
            period = 0.1
            self.device.set_wave_period(channel, period)
            response = self.device.get_wave_info(channel)
            self.assertEqual(response['period'], period)
    
    def test_set_wave_amplitude(self):
        for channel in [SDG2000X.CHANNEL1, SDG2000X.CHANNEL2]:
            self.device.set_waveform(channel, SDG2000X.WAVEFORM_SINE)
            amplitude = 10
            self.device.set_wave_amplitude(channel, amplitude)
            response = self.device.get_wave_info(channel)
            self.assertEqual(response['amplitude'], amplitude)
    
    def test_set_wave_offset(self):
        for channel in [SDG2000X.CHANNEL1, SDG2000X.CHANNEL2]:
            self.device.set_waveform(channel, SDG2000X.WAVEFORM_SINE)
            offset = 2.5
            self.device.set_wave_offset(channel, offset)
            response = self.device.get_wave_info(channel)
            self.assertEqual(response['offset'], offset)
    
    def test_set_wave_symmetry(self):
        for channel in [SDG2000X.CHANNEL1, SDG2000X.CHANNEL2]:
            self.device.set_waveform(channel, SDG2000X.WAVEFORM_RAMP)
            symmetry = 50
            self.device.set_wave_symmetry(channel, symmetry)
            response = self.device.get_wave_info(channel)
            self.assertEqual(response['symmetry'], symmetry)

    def test_set_wave_duty(self):
        for type in [SDG2000X.WAVEFORM_SQUARE, SDG2000X.WAVEFORM_PULSE]:
            for channel in [SDG2000X.CHANNEL1, SDG2000X.CHANNEL2]:
                self.device.set_waveform(channel, type)
                duty = 50
                self.device.set_wave_duty(channel, duty)
                response = self.device.get_wave_info(channel)
                self.assertEqual(response['duty'], duty)

    def test_set_wave_phase(self):
            for channel in [SDG2000X.CHANNEL1, SDG2000X.CHANNEL2]:
                self.device.set_waveform(channel, SDG2000X.WAVEFORM_SINE)
                phase = 50
                self.device.set_wave_phase(channel, phase)
                response = self.device.get_wave_info(channel)
                self.assertEqual(response['phase'], phase)

    def test_set_wave_stdev(self):
            for channel in [SDG2000X.CHANNEL1, SDG2000X.CHANNEL2]:
                self.device.set_waveform(channel, SDG2000X.WAVEFORM_NOISE)
                stdev = 0.5
                self.device.set_wave_stdev(channel, stdev)
                response = self.device.get_wave_info(channel)
                self.assertEqual(response['stdev'], stdev)

    def test_set_wave_mean(self):
            for channel in [SDG2000X.CHANNEL1, SDG2000X.CHANNEL2]:
                self.device.set_waveform(channel, SDG2000X.WAVEFORM_NOISE)
                mean = 3
                self.device.set_wave_mean(channel, mean)
                response = self.device.get_wave_info(channel)
                self.assertEqual(response['mean'], mean)

    def test_set_wave_width(self):
            for channel in [SDG2000X.CHANNEL1, SDG2000X.CHANNEL2]:
                self.device.set_waveform(channel, SDG2000X.WAVEFORM_PULSE)
                width = 0.009
                self.device.set_wave_width(channel, width)
                response = self.device.get_wave_info(channel)
                self.assertEqual(response['width'], width)

    def test_set_wave_rise(self):
            for channel in [SDG2000X.CHANNEL1, SDG2000X.CHANNEL2]:
                self.device.set_waveform(channel, SDG2000X.WAVEFORM_PULSE)
                frequency = 10
                delay = 0
                width = 0.001
                rise = 0.0001
                self.device.set_wave_frequency(channel, frequency)     
                self.device.set_wave_delay(channel, delay)
                self.device.set_wave_width(channel, width)
                self.device.set_wave_rise(channel, rise)
                response = self.device.get_wave_info(channel)
                self.assertEqual(response['rise'], rise)   

    def test_set_wave_fall(self):
            for channel in [SDG2000X.CHANNEL1, SDG2000X.CHANNEL2]:
                self.device.set_waveform(channel, SDG2000X.WAVEFORM_PULSE)
                fall = 0.001
                frequency = 100
                width = 0.001
                self.device.set_wave_frequency(channel, frequency)
                self.device.set_wave_width(channel, width)
                self.device.set_wave_fall(channel, fall)
                response = self.device.get_wave_info(channel)
                self.assertEqual(response['fall'], fall)

    def test_set_wave_delay(self):
            for channel in [SDG2000X.CHANNEL1, SDG2000X.CHANNEL2]:
                self.device.set_waveform(channel, SDG2000X.WAVEFORM_PULSE)
                delay = 0.001
                frequency = 100
                width = 0.001
                self.device.set_wave_frequency(channel, frequency)
                self.device.set_wave_width(channel, width)
                self.device.set_wave_delay(channel, delay)
                response = self.device.get_wave_info(channel)
                self.assertEqual(response['delay'], delay)

    def test_set_wave_high_level(self):
            for channel in [SDG2000X.CHANNEL1, SDG2000X.CHANNEL2]:
                self.device.set_waveform(channel, SDG2000X.WAVEFORM_SINE)
                high_level = 6
                self.device.set_wave_high_level(channel, high_level)
                response = self.device.get_wave_info(channel)
                self.assertEqual(response['high_level'], high_level) 

    def test_set_wave_low_level(self):
        for channel in [SDG2000X.CHANNEL1, SDG2000X.CHANNEL2]:
            self.device.set_waveform(channel, SDG2000X.WAVEFORM_SINE)
            low_level = 4
            self.device.set_wave_low_level(channel, low_level)
            response = self.device.get_wave_info(channel)
            self.assertEqual(response['low_level'], low_level)

    def test_set_output_state(self):
        for channel in [SDG2000X.CHANNEL1, SDG2000X.CHANNEL2]:
            for state in [SDG2000X.OUTPUT_OFF, SDG2000X.OUTPUT_ON]:
                self.device.set_output_state(channel, state)
                response = self.device.get_output_state(channel)
                self.assertEqual(response['state'], state)

    def test_set_output_load(self):
        for channel in [SDG2000X.CHANNEL1, SDG2000X.CHANNEL2]:
            for state in [SDG2000X.HIGH_IMPEDANCE, 1000]:
                self.device.set_output_load(channel, state)
                response = self.device.get_output_state(channel)
                self.assertEqual(response['load'], state)

    def test_set_output_polarity(self):
        for channel in [SDG2000X.CHANNEL1, SDG2000X.CHANNEL2]:
            for state in [SDG2000X.POLARITY_INVERTED, SDG2000X.POLARITY_NORMAL]:
                self.device.set_output_polarity(channel, state)
                response = self.device.get_output_state(channel)
                self.assertEqual(response['polarity'], state)

    def test_set_arb_wave_type(self):
        for channel in [SDG2000X.CHANNEL1, SDG2000X.CHANNEL2]:
            self.device.set_arb_wave_type(channel, 4)
            response = self.device.get_arb_wave_type(channel)
            self.assertEqual(response['index'], 4)
     
if __name__ == '__main__':
    unittest.main()