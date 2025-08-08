# siglent-visa

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python library for controlling Siglent instruments via VISA interface. This package provides easy-to-use Python classes for managing Siglent function generators and other test equipment.

## 🚀 Features

### Supported Instruments
- **SDG1000 Series**: All models with full parameter control
- **SDG2000X Series**: Complete functionality including advanced features
- **Expandable Architecture**: Easy to add support for new instrument series

### Core Functionality
- **Basic Waveform Control**: Set/get waveform type, frequency, amplitude, offset, phase
- **Advanced Features**: Modulation, sweep, burst, arbitrary waveforms
- **Instrument Management**: Connection handling, device identification, error checking
- **Robust Communication**: Automatic retry logic and error recovery

### Developer Features
- **Clean API**: Intuitive Python interface following best practices
- **Type Hints**: Full type annotation support for better IDE integration
- **Comprehensive Testing**: Unit tests for all major functionality
- **Documentation**: Detailed API documentation and examples

## 📦 Installation

### From PyPI
```bash
pip install siglent-visa
```

### From Source
```bash
git clone https://github.com/tfblum/siglent-visa.git
cd siglent-visa
pip install -e .
```

## 🎯 Quick Start

### Basic Usage
```python
import pyvisa
from sdg2000x.sdg2000x_instrument import SDG2000X

# Connect to instrument
rm = pyvisa.ResourceManager()
resource = rm.open_resource("USB0::0xF4ED::0xEE3A::SDG2000X::INSTR")

# Create instrument instance
sdg = SDG2000X(resource)

# Set basic waveform parameters
sdg.set_waveform_type(1, "SINE")
sdg.set_frequency(1, 1000.0)  # 1 kHz
sdg.set_amplitude(1, 2.5)     # 2.5V
sdg.set_offset(1, 0.0)        # 0V offset
sdg.set_phase(1, 0.0)         # 0° phase

# Enable output
sdg.set_output_state(1, True)

# Get current settings
current_settings = sdg.get_waveform_parameters(1)
print(f"Current waveform: {current_settings}")
```

### SDG1000 Series Example
```python
from sdg1000.sdg1000_instrument import SDG1000

# Connect and configure SDG1000
sdg = SDG1000(resource)
sdg.set_basic_wave(1, "SQUARE", 2000.0, 3.3, 1.65, 90.0)
```

## 🔧 API Reference

### SDG2000X Class

#### Basic Waveform Control
```python
# Set waveform parameters
set_waveform_type(channel: int, waveform_type: str)
set_frequency(channel: int, frequency: float)
set_amplitude(channel: int, amplitude: float)
set_offset(channel: int, offset: float)
set_phase(channel: int, phase: float)

# Get waveform parameters
get_waveform_parameters(channel: int) -> dict
get_frequency(channel: int) -> float
get_amplitude(channel: int) -> float
```

#### Output Control
```python
set_output_state(channel: int, state: bool)
get_output_state(channel: int) -> bool
```

#### Advanced Features
```python
# Modulation
set_modulation(channel: int, mod_type: str, **params)
get_modulation_parameters(channel: int) -> dict

# Sweep
configure_sweep(channel: int, start_freq: float, stop_freq: float, time: float)
start_sweep(channel: int)
stop_sweep(channel: int)

# Burst
configure_burst(channel: int, mode: str, cycles: int)
trigger_burst(channel: int)
```

#### Utility Functions
```python
# Instrument identification
get_instrument_info() -> str
reset_instrument()
self_test() -> bool

# Error handling
get_error_queue() -> list
clear_errors()
```

### SDG1000 Class

#### Simplified Interface
```python
set_basic_wave(channel: int, waveform: str, frequency: float, 
               amplitude: float, offset: float, phase: float)
get_basic_wave(channel: int) -> dict
```

## 🧪 Testing

### Run Tests
```bash
# All tests
pytest

# Specific instrument tests
pytest test_sdg2000x.py
pytest test_sdg1000.py

# Hardware tests (requires connected instrument)
pytest -m hardware
```

### Mock Testing
The library includes comprehensive mock support for testing without hardware:

```python
from unittest.mock import MagicMock

# Mock resource for testing
mock_resource = MagicMock()
mock_resource.query.return_value = "SIGLENT,SDG2042X,123456,1.0.0"

sdg = SDG2000X(mock_resource)
# Test functionality without hardware
```

## 📚 Supported SCPI Commands

### Basic Waveform Commands
- `C1:BSWV WVTP,<type>` - Set waveform type
- `C1:BSWV FRQ,<freq>` - Set frequency
- `C1:BSWV AMP,<amp>` - Set amplitude
- `C1:BSWV OFST,<offset>` - Set offset
- `C1:BSWV PHSE,<phase>` - Set phase

### Output Control
- `C1:OUTP ON|OFF` - Enable/disable output
- `C1:OUTP?` - Query output state

### Modulation Commands
- `C1:MDWV <type>` - Set modulation type
- `C1:MDWV?` - Query modulation parameters

### System Commands
- `*IDN?` - Get instrument identification
- `*RST` - Reset instrument
- `*TST?` - Self test
- `SYST:ERR?` - Get error queue

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-instrument`)
3. Add your changes with tests
4. Ensure all tests pass (`pytest`)
5. Submit a pull request

### Adding New Instruments
To add support for a new Siglent instrument:

1. Create a new directory: `sdgXXXX/`
2. Implement the instrument class following existing patterns
3. Add comprehensive tests
4. Update documentation

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Original Author**: Francesco Gramazio (gramazio.francesco@lab3841.it)
- **Enhanced By**: Thomas Blum (tfblum@icloud.com)
- **PyVISA Community**: Excellent instrument communication framework
- **Siglent Technologies**: Hardware documentation and support

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/tfblum/siglent-visa/issues)
- **Original Repository**: [GramazioFrancesco/siglent-visa](https://github.com/GramazioFrancesco/siglent-visa)

## 🔄 Version History

- **v0.2.0**: Enhanced packaging, improved API, comprehensive testing
- **v0.1.0**: Initial release with basic SDG2000X support