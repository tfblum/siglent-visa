"""
SDG1000 Series Function Generator Support

This package provides support for Siglent SDG1000 series function generators
through the siglent-visa library.

@version: v0.1.0
@author: Extended for SDG1000 support
"""

from .sdg1000_instrument import SDG1000

__all__ = ['SDG1000']
