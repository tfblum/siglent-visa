"""
Siglent VISA Library

A comprehensive library for controlling Siglent function generators via VISA interface.
Supports SDG1000, SDG2000X, and SDG6000X series instruments.

@version: v0.1.0
@author: Extended by Function Generator UI Project
"""

from visa_instruments import VisaInstruments
from sdg1000.sdg1000_instrument import SDG1000
from sdg2000x.sdg2000x_instrument import SDG2000X
from factory import SiglentInstrumentFactory, UnsupportedModelError, create_siglent_instrument, detect_siglent_model

__version__ = "0.1.0"
__all__ = [
    'VisaInstruments',
    'SDG1000', 
    'SDG2000X',
    'SiglentInstrumentFactory',
    'UnsupportedModelError',
    'create_siglent_instrument',
    'detect_siglent_model'
]
