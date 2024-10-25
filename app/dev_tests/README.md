# Dev Tests
Endpoints regarding the initialization of the database and data to be stored within.

## Restart database
- Restarts the database and adds the following:
- All available cookie types.
- All available forms of payment.
- Four users.
     - The fourth will be replaced by a user given one if all of the following are met: 
        - email, password, password_confirm, first_name, and last_name are given.
        - Email address must be in a valid email format.
        - Passwords must:
            - Be between 8 and 20 characters long.
            - Contain at least one number.
            - Have at least one of the following characters: `! @ # $ % ^ & * _ ?`
        - Both passwords must match to confirm.
- For each user: 
    - A random number of cookies will be added to their inventories, with the type of cookie also being relatively random.
    - Three customers will be added. 
        - Each customer will have four orders attached to them.
            - Each order will have a random number of cookies of random types attached to them.
- **`WARNING: DELETES ALL PREVIOUS DATA!`**
```
[GET, POST] /dev_tests/init_db
(Entering a value for all of the following will add them to the database as the fourth user instead.)
email
password
password_confirm (same as password to work)
first_name
last_name
```




