"""
Test suite for SDG1000 instrument implementation

Tests SDG1000-specific functionality including parameter validation,
model detection, and command generation.

@version: v0.1.0
@author: Function Generator UI Project
"""

import unittest
import sys
import os

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock pyvisa for testing
class MockInstrument:
    def __init__(self):
        self.write_termination = '\n'
        self.read_termination = '\n'
        self.query_delay = 0.1
        self.commands = []
        self.responses = {
            '*IDN?': 'Siglent Technologies,SDG1025,SDG1XXXXXXXX,1.01.01.33R5',
            'C1:OUTP?': 'C1:OUTP ON,LOAD,50,PLRT,NOR',
            'C1:BSWV?': 'C1:BSWV WVTP,SINE,FRQ,1000.0HZ,AMP,2.0V,OFST,0.0V,PHSE,0.0'
        }
    
    def write(self, command):
        self.commands.append(command)
    
    def query(self, command):
        return self.responses.get(command, 'OK')
    
    def close(self):
        pass

class MockResourceManager:
    def open_resource(self, address):
        return MockInstrument()

# Mock pyvisa module
class MockPyVisa:
    ResourceManager = MockResourceManager

sys.modules['pyvisa'] = MockPyVisa()

# Now import our classes
from sdg1000.sdg1000_instrument import SDG1000
from factory import SiglentInstrumentFactory, UnsupportedModelError


class TestSDG1000(unittest.TestCase):
    """Test SDG1000 instrument functionality"""
    
    def setUp(self):
        self.instrument = SDG1000("MOCK::ADDRESS")
    
    def test_model_constants(self):
        """Test SDG1000-specific constants"""
        self.assertEqual(self.instrument.FREQ_MIN, 1e-6)
        self.assertEqual(self.instrument.FREQ_MAX, 10e6)
        self.assertEqual(self.instrument.AMP_MIN, 0.002)
        self.assertEqual(self.instrument.BURST_CYCLES_MAX, 50000)
        self.assertEqual(self.instrument.ARB_POINTS_MAX, 4096)
        self.assertEqual(self.instrument.ARB_RESOLUTION, 12)
    
    def test_frequency_validation(self):
        """Test frequency validation against SDG1000 limits"""
        # Valid frequencies
        self.assertTrue(self.instrument._validate_frequency(1000))
        self.assertTrue(self.instrument._validate_frequency(1e6))
        self.assertTrue(self.instrument._validate_frequency(self.instrument.FREQ_MIN))
        self.assertTrue(self.instrument._validate_frequency(self.instrument.FREQ_MAX))
        
        # Invalid frequencies
        with self.assertRaises(ValueError):
            self.instrument._validate_frequency(0.5e-6)  # Too low
        
        with self.assertRaises(ValueError):
            self.instrument._validate_frequency(15e6)  # Too high
        
        # Waveform-specific limits
        with self.assertRaises(ValueError):
            self.instrument._validate_frequency(300e3, self.instrument.WAVEFORM_RAMP)  # RAMP max 200kHz
    
    def test_amplitude_validation(self):
        """Test amplitude validation against SDG1000 limits"""
        # Valid amplitudes
        self.assertTrue(self.instrument._validate_amplitude(2.0, self.instrument.LOAD_50_OHM))
        self.assertTrue(self.instrument._validate_amplitude(10.0, self.instrument.LOAD_50_OHM))
        self.assertTrue(self.instrument._validate_amplitude(20.0, self.instrument.HIGH_IMPEDANCE))
        
        # Invalid amplitudes
        with self.assertRaises(ValueError):
            self.instrument._validate_amplitude(0.001)  # Below minimum
        
        with self.assertRaises(ValueError):
            self.instrument._validate_amplitude(15.0, self.instrument.LOAD_50_OHM)  # Above 50Ω limit
        
        with self.assertRaises(ValueError):
            self.instrument._validate_amplitude(25.0, self.instrument.HIGH_IMPEDANCE)  # Above High-Z limit
    
    def test_load_impedance_validation(self):
        """Test load impedance validation for SDG1000"""
        # Valid loads
        self.assertTrue(self.instrument._validate_load_impedance(self.instrument.LOAD_50_OHM))
        self.assertTrue(self.instrument._validate_load_impedance(self.instrument.HIGH_IMPEDANCE))
        
        # Invalid loads
        with self.assertRaises(ValueError):
            self.instrument._validate_load_impedance(75)  # Not supported
        
        with self.assertRaises(ValueError):
            self.instrument._validate_load_impedance(1000)  # Not supported
    
    def test_set_frequency_with_validation(self):
        """Test set_wave_frequency with SDG1000 validation"""
        # Valid frequency
        self.instrument.set_wave_frequency('C1', 1000)
        self.assertIn('C1:BSWV FRQ,1000', self.instrument.instr.commands)
        
        # Invalid frequency should raise error
        with self.assertRaises(ValueError):
            self.instrument.set_wave_frequency('C1', 20e6)
    
    def test_set_amplitude_with_validation(self):
        """Test set_wave_amplitude with SDG1000 validation"""
        # Valid amplitude
        self.instrument.set_wave_amplitude('C1', 5.0)
        self.assertIn('C1:BSWV AMP,5.0', self.instrument.instr.commands)
        
        # Invalid amplitude should raise error
        with self.assertRaises(ValueError):
            self.instrument.set_wave_amplitude('C1', 0.001)
    
    def test_set_load_impedance_with_validation(self):
        """Test set_output_load with SDG1000 validation"""
        # Valid load impedances
        self.instrument.set_output_load('C1', 50)
        self.assertIn('C1:OUTP LOAD,50', self.instrument.instr.commands)
        
        self.instrument.set_output_load('C1', 'HZ')
        self.assertIn('C1:OUTP LOAD,HZ', self.instrument.instr.commands)
        
        # Invalid load impedance should raise error
        with self.assertRaises(ValueError):
            self.instrument.set_output_load('C1', 75)
    
    def test_waveform_type_validation(self):
        """Test waveform type validation"""
        # Valid waveform types
        valid_types = [
            self.instrument.WAVEFORM_SINE,
            self.instrument.WAVEFORM_SQUARE,
            self.instrument.WAVEFORM_RAMP,
            self.instrument.WAVEFORM_PULSE,
            self.instrument.WAVEFORM_NOISE,
            self.instrument.WAVEFORM_ARB
        ]
        
        for waveform_type in valid_types:
            self.instrument.set_waveform('C1', waveform_type)
            self.assertIn(f'C1:BSWV WVTP,{waveform_type}', self.instrument.instr.commands)
        
        # Invalid waveform type should raise error (if DC were supported)
        with self.assertRaises(ValueError):
            self.instrument.set_waveform('C1', 'DC')


class TestSiglentInstrumentFactory(unittest.TestCase):
    """Test the Siglent instrument factory"""
    
    def test_model_detection_from_idn(self):
        """Test model detection from *IDN? responses"""
        factory = SiglentInstrumentFactory()
        
        # SDG1000 series
        idn_sdg1000 = "Siglent Technologies,SDG1025,SDG1XXXXXXXX,1.01.01.33R5"
        self.assertEqual(factory.detect_model_from_idn(idn_sdg1000), 'SDG1000')
        
        # SDG2000X series
        idn_sdg2000x = "Siglent Technologies,SDG2042X,SDG2XXXXXXXX,2.01.01.35R2"
        self.assertEqual(factory.detect_model_from_idn(idn_sdg2000x), 'SDG2000X')
        
        # Unsupported model
        idn_unknown = "Unknown Manufacturer,MODEL123,SERIAL,1.0.0"
        with self.assertRaises(UnsupportedModelError):
            factory.detect_model_from_idn(idn_unknown)
        
        # Invalid format
        with self.assertRaises(UnsupportedModelError):
            factory.detect_model_from_idn("InvalidFormat")
    
    def test_model_name_validation(self):
        """Test model name validation"""
        factory = SiglentInstrumentFactory()
        
        # Valid models
        supported, family, pattern = factory.validate_model_name("SDG1025")
        self.assertTrue(supported)
        self.assertEqual(family, 'SDG1000')
        
        supported, family, pattern = factory.validate_model_name("SDG2042X")
        self.assertTrue(supported)
        self.assertEqual(family, 'SDG2000X')
        
        # Invalid model
        supported, family, pattern = factory.validate_model_name("UNKNOWN123")
        self.assertFalse(supported)
        self.assertIsNone(family)
    
    def test_supported_models(self):
        """Test supported models list"""
        factory = SiglentInstrumentFactory()
        supported = factory.get_supported_models()
        self.assertIn('SDG1000', supported)
        self.assertIn('SDG2000X', supported)
    
    def test_model_patterns(self):
        """Test model pattern retrieval"""
        factory = SiglentInstrumentFactory()
        
        patterns_1000 = factory.get_model_patterns('SDG1000')
        self.assertTrue(len(patterns_1000) > 0)
        
        patterns_2000x = factory.get_model_patterns('SDG2000X')
        self.assertTrue(len(patterns_2000x) > 0)
        
        patterns_unknown = factory.get_model_patterns('UNKNOWN')
        self.assertEqual(len(patterns_unknown), 0)


class TestSDG1000VsSDG2000XDifferences(unittest.TestCase):
    """Test differences between SDG1000 and SDG2000X implementations"""
    
    def setUp(self):
        self.sdg1000 = SDG1000("MOCK::ADDRESS1")
        
        # We can't directly import SDG2000X here due to path issues,
        # but we can test the differences conceptually
    
    def test_frequency_range_differences(self):
        """Test that SDG1000 has more restrictive frequency range"""
        # SDG1000 max frequency (10 MHz)
        self.assertEqual(self.sdg1000.FREQ_MAX, 10e6)
        
        # SDG1000 should reject frequencies that SDG2000X would accept
        with self.assertRaises(ValueError):
            self.sdg1000._validate_frequency(20e6)  # SDG2000X can do 40MHz
    
    def test_amplitude_range_differences(self):
        """Test that SDG1000 has different amplitude specifications"""
        # SDG1000 minimum amplitude (2 mVpp vs 1 mVpp for SDG2000X)
        self.assertEqual(self.sdg1000.AMP_MIN, 0.002)
        
        # SDG1000 should reject amplitudes that SDG2000X would accept
        with self.assertRaises(ValueError):
            self.sdg1000._validate_amplitude(0.0015)  # Below SDG1000 minimum
    
    def test_load_impedance_differences(self):
        """Test that SDG1000 has limited load impedance options"""
        # SDG1000 only supports 50Ω and High-Z
        self.assertTrue(self.sdg1000._validate_load_impedance(50))
        self.assertTrue(self.sdg1000._validate_load_impedance(0))  # High-Z
        
        # SDG1000 should reject variable impedances that SDG2000X supports
        with self.assertRaises(ValueError):
            self.sdg1000._validate_load_impedance(75)
        
        with self.assertRaises(ValueError):
            self.sdg1000._validate_load_impedance(1000)
    
    def test_burst_cycles_differences(self):
        """Test that SDG1000 has different burst cycle limits"""
        # SDG1000 max burst cycles (50,000 vs 65,535 for SDG2000X)
        self.assertEqual(self.sdg1000.BURST_CYCLES_MAX, 50000)
    
    def test_arb_specifications_differences(self):
        """Test that SDG1000 has different arbitrary waveform specifications"""
        # SDG1000 ARB specs (4k points, 12-bit vs 16k points, 14-bit for SDG2000X)
        self.assertEqual(self.sdg1000.ARB_POINTS_MAX, 4096)
        self.assertEqual(self.sdg1000.ARB_RESOLUTION, 12)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
