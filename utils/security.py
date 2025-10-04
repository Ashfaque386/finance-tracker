"""Security utilities for PIN/password protection."""
import hashlib
import os
from typing import Optional, Tuple


class Security:
    """Security utilities for app protection."""
    
    @staticmethod
    def hash_pin(pin: str) -> str:
        """Hash a PIN code using SHA-256."""
        return hashlib.sha256(pin.encode()).hexdigest()
    
    @staticmethod
    def verify_pin(pin: str, hashed_pin: str) -> bool:
        """Verify a PIN against a hashed PIN."""
        return Security.hash_pin(pin) == hashed_pin
    
    @staticmethod
    def generate_salt() -> str:
        """Generate a random salt for encryption."""
        return os.urandom(32).hex()
    
    @staticmethod
    def validate_pin_strength(pin: str) -> Tuple[bool, str]:
        """Validate PIN strength."""
        if not pin:
            return False, "PIN cannot be empty"
        
        if len(pin) < 4:
            return False, "PIN must be at least 4 digits"
        
        if not pin.isdigit():
            return False, "PIN must contain only numbers"
        
        # Check for simple patterns
        if pin == pin[0] * len(pin):
            return False, "PIN cannot be all same digits"
        
        # Check for sequential patterns
        is_sequential = all(
            int(pin[i]) == int(pin[i-1]) + 1 
            for i in range(1, len(pin))
        )
        if is_sequential:
            return False, "PIN cannot be sequential"
        
        return True, "PIN is valid"
    
    @staticmethod
    def encrypt_simple(data: str, key: str) -> str:
        """Simple XOR encryption for basic data protection."""
        encrypted = []
        key_length = len(key)
        
        for i, char in enumerate(data):
            key_char = key[i % key_length]
            encrypted_char = chr(ord(char) ^ ord(key_char))
            encrypted.append(encrypted_char)
        
        return ''.join(encrypted)
    
    @staticmethod
    def decrypt_simple(data: str, key: str) -> str:
        """Simple XOR decryption."""
        return Security.encrypt_simple(data, key)  # XOR is symmetric

