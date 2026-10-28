"""
Input validation utilities for user interface
"""
from typing import Tuple, Optional
import re

# Common Indian states for validation
INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
]

# Common employment statuses
EMPLOYMENT_STATUSES = [
    "Employed (Full-time)", "Employed (Part-time)", "Self-Employed",
    "Unemployed", "Student", "Retired", "Homemaker", "Daily Wage Worker", "Farmer"
]

# Education levels
EDUCATION_LEVELS = [
    "No Formal Education", "Primary School", "Secondary School",
    "Higher Secondary", "Graduate", "Post-Graduate", "Diploma/ITI", "Other"
]

# Social categories
SOCIAL_CATEGORIES = [
    "General", "OBC", "SC", "ST", "EWS", "Prefer not to say"
]


def validate_age(age_input: str) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Validates age input.
    
    Returns:
        (is_valid, age_value, error_message)
    """
    if not age_input:
        return False, None, "Age is required"
    
    try:
        age = int(age_input)
        if age < 0:
            return False, None, "Age cannot be negative"
        if age > 120:
            return False, None, "Please enter a valid age (0-120)"
        return True, age, None
    except ValueError:
        return False, None, "Please enter a valid number for age"


def validate_income(income_input: str) -> Tuple[bool, Optional[float], Optional[str]]:
    """
    Validates annual income input.
    
    Returns:
        (is_valid, income_value, error_message)
    """
    if not income_input:
        return False, None, "Income is required"
    
    # Remove commas and spaces
    income_str = income_input.replace(",", "").replace(" ", "")
    
    try:
        income = float(income_str)
        if income < 0:
            return False, None, "Income cannot be negative"
        if income > 100000000:  # 10 crore limit for sanity
            return False, None, "Please enter a reasonable income amount"
        return True, income, None
    except ValueError:
        return False, None, "Please enter a valid number for income"


def validate_location(location_input: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validates location/state input.
    
    Returns:
        (is_valid, location_value, error_message)
    """
    if not location_input:
        return False, None, "Location is required"
    
    location = location_input.strip()
    if len(location) < 2:
        return False, None, "Please enter a valid location"
    
    return True, location, None


def validate_family_size(family_input: str) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Validates family size input.
    
    Returns:
        (is_valid, family_size, error_message)
    """
    if not family_input:
        return False, None, "Family size is required"
    
    try:
        family_size = int(family_input)
        if family_size < 1:
            return False, None, "Family size must be at least 1"
        if family_size > 50:
            return False, None, "Please enter a reasonable family size"
        return True, family_size, None
    except ValueError:
        return False, None, "Please enter a valid number for family size"


def validate_scheme_name(scheme_input: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validates scheme name input.
    
    Returns:
        (is_valid, scheme_name, error_message)
    """
    if not scheme_input:
        return False, None, "Scheme name is required"
    
    scheme = scheme_input.strip()
    if len(scheme) < 3:
        return False, None, "Please enter a valid scheme name (at least 3 characters)"
    
    return True, scheme, None


def validate_policy_name(policy_input: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validates policy name input.
    
    Returns:
        (is_valid, policy_name, error_message)
    """
    if not policy_input:
        return False, None, "Policy name is required"
    
    policy = policy_input.strip()
    if len(policy) < 3:
        return False, None, "Please enter a valid policy name (at least 3 characters)"
    
    return True, policy, None


def format_currency(amount: float) -> str:
    """Format amount in Indian currency format."""
    return f"₹{amount:,.2f}"


def validate_required_field(field_value: str, field_name: str) -> Tuple[bool, Optional[str]]:
    """
    Generic required field validator.
    
    Returns:
        (is_valid, error_message)
    """
    if not field_value or not field_value.strip():
        return False, f"{field_name} is required"
    return True, None
