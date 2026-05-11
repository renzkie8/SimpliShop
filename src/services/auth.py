"""Authentication and password security utilities.

This module provides functions for secure password hashing and verification.
"""

import hashlib
import secrets
import string


def hash_password(password):
    """
    Hash a password using SHA-256.
    
    Args:
        password (str): The plain text password to hash
        
    Returns:
        str: The hashed password as a hexadecimal string
        
    Example:
        >>> hashed = hash_password("mypassword123")
        >>> print(len(hashed))
        64
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def verify_password(password, hashed_password):
    """
    Verify a password against its hash.
    
    Args:
        password (str): The plain text password to verify
        hashed_password (str): The hashed password to compare against
        
    Returns:
        bool: True if password matches, False otherwise
        
    Example:
        >>> hashed = hash_password("mypassword123")
        >>> verify_password("mypassword123", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    if not password or not hashed_password:
        return False
    
    return hash_password(password) == hashed_password


def generate_random_password(length=12):
    """
    Generate a random secure password.
    
    Args:
        length (int): Length of the password (default: 12)
        
    Returns:
        str: A randomly generated password
        
    Example:
        >>> password = generate_random_password(16)
        >>> print(len(password))
        16
    """
    if length < 8:
        raise ValueError("Password length must be at least 8 characters")
    
    # Define character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Combine all characters
    all_characters = lowercase + uppercase + digits + special
    
    # Ensure at least one character from each set
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        secrets.choice(special),
    ]
    
    # Fill the rest randomly
    password += [secrets.choice(all_characters) for _ in range(length - 4)]
    
    # Shuffle to avoid predictable patterns
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)


def validate_password_strength(password):
    """
    Validate password strength and return feedback.
    
    Args:
        password (str): The password to validate
        
    Returns:
        dict: Dictionary with 'valid' (bool) and 'message' (str) keys
        
    Example:
        >>> result = validate_password_strength("weak")
        >>> print(result['valid'])
        False
        >>> print(result['message'])
        Password must be at least 8 characters long
    """
    if not password:
        return {
            'valid': False,
            'message': 'Password cannot be empty'
        }
    
    if len(password) < 8:
        return {
            'valid': False,
            'message': 'Password must be at least 8 characters long'
        }
    
    has_lowercase = any(c.islower() for c in password)
    has_uppercase = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    if not has_lowercase:
        return {
            'valid': False,
            'message': 'Password must contain at least one lowercase letter'
        }
    
    if not has_uppercase:
        return {
            'valid': False,
            'message': 'Password must contain at least one uppercase letter'
        }
    
    if not has_digit:
        return {
            'valid': False,
            'message': 'Password must contain at least one number'
        }
    
    if not has_special:
        return {
            'valid': False,
            'message': 'Password must contain at least one special character'
        }
    
    return {
        'valid': True,
        'message': 'Password is strong'
    }


# For testing purposes
if __name__ == "__main__":
    # Test password hashing
    password = "MySecurePassword123!"
    hashed = hash_password(password)
    print(f"Original: {password}")
    print(f"Hashed: {hashed}")
    print(f"Verification: {verify_password(password, hashed)}")
    
    # Test random password generation
    random_pw = generate_random_password(16)
    print(f"\nGenerated password: {random_pw}")
    
    # Test password strength validation
    test_passwords = [
        "weak",
        "StrongPass1!",
        "NoSpecialChar1",
        "noupppercase1!",
    ]
    
    print("\nPassword strength tests:")
    for pw in test_passwords:
        result = validate_password_strength(pw)
        print(f"  {pw}: {result['message']}")


