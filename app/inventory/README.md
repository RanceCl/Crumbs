# Inventory
## List current user inventory
Returns a list of the inventory of every cookie for the currently logged in user.
```
[GET] /users/inventory
```
## Change current user's cookie name inventory entry
Changes the logged in user's inventory for a cookie. Inventory is the new value for the quantity.
```
[POST, PATCH] /users/inventory
cookie_name
inventory
```
## Delete current user's coookie name inventory entry
Deletes the inventory entry for the cookie_name given for the logged in user.
```
[DELETE] /users/inventory
cookie_name
```