import re
from email_validator import validate_email, EmailNotValidError

def is_email_valid(email):
    try:
        v = validate_email(email)
        # Return normalized form
        email = v.email
        return email, True
    except EmailNotValidError as e:
        # email is not valid, exception message is human-readable
        return str(e), False

# Make sure that inputted password follows desired format.
def is_password_valid(password):
    # Make sure password is between 
    if (len(password)<8) or (len(password)>20):
        return "Password must be between 8 and 20 letters long.", False
    # Make sure password has at least one number
    elif not re.search("[0-9]", password):
        return "Password must have at least one number.", False
    # Make sure password has at least special character
    elif not re.search("[!@#$%\^&*_\?+=]", password):
        return "Password must have at least one of the following characters [!@#$%^&*_?].", False
    else: 
        return password, True


