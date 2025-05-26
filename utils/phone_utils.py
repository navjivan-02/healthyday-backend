import phonenumbers

def validate_mobile(mobile: str) -> str:
    try:
        # Remove all non-digit characters
        cleaned = ''.join(filter(str.isdigit, mobile))

        # If user gave only 10 digits, assume Indian mobile
        if len(cleaned) == 10:
            cleaned = "+91" + cleaned
        elif not cleaned.startswith("91") and not cleaned.startswith("+"):
            raise ValueError("Please enter a valid 10-digit Indian mobile number")

        # Parse and validate
        number = phonenumbers.parse(cleaned, None)
        if not phonenumbers.is_valid_number(number):
            raise ValueError("Invalid mobile number")

        return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)

    except Exception as e:
        raise ValueError(f"Invalid mobile number: {e}")
