# User Info
Endpoints that handle editing and retrieval of information about the currently logged in user. All routes require user login.

## List current user's information
- Retrieves the information on the currently logged in user.
- Returns jsonified dictionary with the information of the current user.
```
[GET] /users
```
## List current user's information
- Retrieves the information on the currently logged in user.
- Returns jsonified dictionary with the information of the current user.
```
[GET] /current-user
```
## Change current user's email
- Changes the email account of the logged in user.
- Required inputs: email, password
- Email address must be in a valid email format.
    - Returns information about incorrect formatting. ex: `Can only have one @.`
- Returns jsonified dictionary with the updated information of the current user.
```
[GET, PATCH] /users/change_email
new_email
password
```
## Change current user's password
- Changes the password of the logged in user. Requires a properly formatted "new_password", with the copied "new_password_confirm", and the current "password".
- Required inputs: password, new_password, new_password_confirm
- New passwords must:
    - Be between 8 and 20 characters long.
    - Contain at least one number.
    - Have at least one of the following characters: `! @ # $ % ^ & * _ ?`
    - Returns error about what specifications were missed.
- Both new passwords must match to confirm.
- Returns jsonified dictionary with the updated information of the current user.
```
[GET, PATCH] /users/change_password
password (old password)
new_password
new_password_confirm (copy of old password)
```