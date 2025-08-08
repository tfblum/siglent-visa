"""
Siglent Function Generator Factory

Provides automatic model detection and instantiation of appropriate instrument classes
based on SCPI *IDN? response.

@version: v0.2.0
@author: Gramazio Francesco, Thomas Blum (tfblum)
@reference: Siglent API Reference, Device Documentation
"""

import re
from typing import Union, Optional

# Import instrument classes
from sdg2000x.sdg2000x_instrument import SDG2000X
from sdg1000.sdg1000_instrument import SDG1000


class UnsupportedModelError(Exception):
    """Raised when an unsupported Siglent model is detected"""
    pass


class SiglentInstrumentFactory:
    """
    Factory class for creating appropriate Siglent instrument instances
    based on automatic model detection
    """
    
    # Model detection patterns (case-insensitive)
    SDG1000_PATTERNS = [
        r'SDG1\d{3}[A-Z]*',  # SDG1025, SDG1025X, etc.
        r'SDG10\d{2}[A-Z]*'  # SDG1032, etc.
    ]
    
    SDG2000X_PATTERNS = [
        r'SDG2\d{3}X[A-Z]*',  # SDG2042X, SDG2122X, etc.
        r'SDG20\d{2}X[A-Z]*'  # SDG2042X, etc.
    ]
    
    # Future model patterns (for extensibility)
    SDG6000X_PATTERNS = [
        r'SDG6\d{3}X[A-Z]*',  # SDG6032X, etc.
        r'SDG60\d{2}X[A-Z]*'
    ]
    
    @classmethod
    def detect_model_from_idn(cls, idn_response: str) -> str:
        """
        Detect Siglent model from *IDN? response
        
        Args:
            idn_response: Response from *IDN? query
            
        Returns:
            str: Model family ('SDG1000', 'SDG2000X', 'SDG6000X')
            
        Raises:
            UnsupportedModelError: If model is not supported
            
        Example:
            >>> factory = SiglentInstrumentFactory()
            >>> model = factory.detect_model_from_idn("Siglent Technologies,SDG1025,SDG1XXXXXXXX,1.01.01.33R5")
            >>> print(model)  # 'SDG1000'
        """
        if not idn_response:
            raise UnsupportedModelError("Empty or invalid *IDN? response")
        
        # Extract model name from IDN response
        # Expected format: "Manufacturer,Model,SerialNumber,FirmwareVersion"
        parts = idn_response.strip().split(',')
        if len(parts) < 2:
            raise UnsupportedModelError(f"Invalid *IDN? format: {idn_response}")
        
        model_name = parts[1].strip()
        
        # Check against known patterns
        for pattern in cls.SDG1000_PATTERNS:
            if re.search(pattern, model_name, re.IGNORECASE):
                return 'SDG1000'
        
        for pattern in cls.SDG2000X_PATTERNS:
            if re.search(pattern, model_name, re.IGNORECASE):
                return 'SDG2000X'
        
        for pattern in cls.SDG6000X_PATTERNS:
            if re.search(pattern, model_name, re.IGNORECASE):
                return 'SDG6000X'
        
        # Model not recognized
        raise UnsupportedModelError(f"Unsupported model detected: {model_name}")
    
    @classmethod
    def create_instrument(cls, address: str, model_hint: Optional[str] = None) -> Union[SDG1000, SDG2000X]:
        """
        Create appropriate instrument instance with automatic model detection
        
        Args:
            address: VISA resource address
            model_hint: Optional model family hint ('SDG1000', 'SDG2000X') to skip detection
            
        Returns:
            Union[SDG1000, SDG2000X]: Appropriate instrument instance
            
        Raises:
            UnsupportedModelError: If model is not supported
            pyvisa.Error: If connection fails
            
        Example:
            >>> instrument = SiglentInstrumentFactory.create_instrument("USB0::0xF4EC::0x1000::XXXXXXXX::INSTR")
            >>> print(type(instrument))  # <class 'sdg1000_instrument.SDG1000'>
        """
        if model_hint:
            # Use provided hint without detection
            if model_hint == 'SDG1000':
                return SDG1000(address)
            elif model_hint == 'SDG2000X':
                return SDG2000X(address)
            elif model_hint == 'SDG6000X':
                raise UnsupportedModelError("SDG6000X not yet implemented")
            else:
                raise UnsupportedModelError(f"Unknown model hint: {model_hint}")
        
        # Auto-detect model by connecting and querying *IDN?
        # We'll use a temporary SDG2000X instance for the detection query
        # since the base VisaInstruments class handles *IDN? uniformly
        temp_instrument = None
        try:
            # Create temporary instance for detection
            temp_instrument = SDG2000X(address)
            idn_response = temp_instrument.instr.query('*IDN?')
            
            # Detect model family
            model_family = cls.detect_model_from_idn(idn_response)
            
            # Close temporary connection
            temp_instrument.instr.close()
            temp_instrument = None
            
            # Create appropriate instrument instance
            if model_family == 'SDG1000':
                return SDG1000(address)
            elif model_family == 'SDG2000X':
                return SDG2000X(address)
            elif model_family == 'SDG6000X':
                raise UnsupportedModelError("SDG6000X not yet implemented")
            else:
                raise UnsupportedModelError(f"Detected model family '{model_family}' not implemented")
                
        except Exception as e:
            # Clean up temporary connection if it exists
            if temp_instrument and hasattr(temp_instrument, 'instr'):
                try:
                    temp_instrument.instr.close()
                except:
                    pass
            
            # Re-raise the exception
            if isinstance(e, UnsupportedModelError):
                raise
            else:
                raise UnsupportedModelError(f"Failed to detect model: {str(e)}")
    
    @classmethod
    def get_supported_models(cls) -> list:
        """
        Get list of supported model families
        
        Returns:
            list: List of supported model families
        """
        return ['SDG1000', 'SDG2000X']
    
    @classmethod
    def get_model_patterns(cls, model_family: str) -> list:
        """
        Get regex patterns for a specific model family
        
        Args:
            model_family: Model family name
            
        Returns:
            list: List of regex patterns for the model family
        """
        if model_family == 'SDG1000':
            return cls.SDG1000_PATTERNS
        elif model_family == 'SDG2000X':
            return cls.SDG2000X_PATTERNS
        elif model_family == 'SDG6000X':
            return cls.SDG6000X_PATTERNS
        else:
            return []
    
    @classmethod
    def validate_model_name(cls, model_name: str) -> tuple:
        """
        Validate and classify a model name
        
        Args:
            model_name: Model name to validate
            
        Returns:
            tuple: (is_supported, model_family, matched_pattern)
        """
        all_patterns = [
            ('SDG1000', cls.SDG1000_PATTERNS),
            ('SDG2000X', cls.SDG2000X_PATTERNS),
            ('SDG6000X', cls.SDG6000X_PATTERNS)
        ]
        
        for family, patterns in all_patterns:
            for pattern in patterns:
                if re.search(pattern, model_name, re.IGNORECASE):
                    return (True, family, pattern)
        
        return (False, None, None)


# Convenience functions for backward compatibility and ease of use

def create_siglent_instrument(address: str, model_hint: Optional[str] = None) -> Union[SDG1000, SDG2000X]:
    """
    Convenience function to create a Siglent instrument instance
    
    Args:
        address: VISA resource address
        model_hint: Optional model family hint
        
    Returns:
        Union[SDG1000, SDG2000X]: Appropriate instrument instance
    """
    return SiglentInstrumentFactory.create_instrument(address, model_hint)


def detect_siglent_model(address: str) -> str:
    """
    Convenience function to detect Siglent model without creating persistent connection
    
    Args:
        address: VISA resource address
        
    Returns:
        str: Detected model family
    """
    temp_instrument = None
    try:
        temp_instrument = SDG2000X(address)
        idn_response = temp_instrument.instr.query('*IDN?')
        return SiglentInstrumentFactory.detect_model_from_idn(idn_response)
    finally:
        if temp_instrument and hasattr(temp_instrument, 'instr'):
            try:
                temp_instrument.instr.close()
            except:
                pass


# Example usage and testing
if __name__ == "__main__":
    # Test model detection patterns
    test_idn_responses = [
        "Siglent Technologies,SDG1025,SDG1XXXXXXXX,1.01.01.33R5",
        "Siglent Technologies,SDG2042X,SDG2XXXXXXXX,2.01.01.35R2",
        "Siglent Technologies,SDG6032X,SDG6XXXXXXXX,3.01.01.10R1",
        "Unknown Manufacturer,MODEL123,SERIAL,1.0.0"
    ]
    
    factory = SiglentInstrumentFactory()
    
    for idn in test_idn_responses:
        try:
            model = factory.detect_model_from_idn(idn)
            print(f"✓ {idn} -> {model}")
        except UnsupportedModelError as e:
            print(f"✗ {idn} -> {e}")
    
    # Test model name validation
    test_models = ["SDG1025", "SDG2042X", "SDG6032X", "UNKNOWN123"]
    
    for model in test_models:
        supported, family, pattern = factory.validate_model_name(model)
        if supported:
            print(f"✓ {model} -> {family} (pattern: {pattern})")
        else:
            print(f"✗ {model} -> Not supported")
