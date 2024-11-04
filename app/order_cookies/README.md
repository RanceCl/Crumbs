# Order Cookies
Endpoints that handle the addition of cookies attached to orders as well as handling information about them. All routes require user login.

## List order's cookies
- Shows information for the cookie on the order.
- Returns jsonified dictionary with the information of the cookie entry for the order.
```
[GET] /order_cookies/<order_id>/<cookie_id>
```
## Add cookie to order
- Adds the cookie to the order.
- Desired quantity will be 0 if none is given.
- Returns jsonified dictionary with the information of the new cookie entry for the order.
```
[POST] /order_cookies/<order_id>/<cookie_id>
quantity (set to 0 if none given)
```
## Update order's cookie
- Updates order's cookie quantity. 
- Desired quantity will be unchanged if none is given.
- Returns jsonified dictionary with the updated information of the cookie entry for the order.
```
[PATCH] /order_cookies/<order_id>/<cookie_id>
quantity (no change made if none given.)
```
## Delete cookie from order
- Deletes order's cookie.
- Returns confirmation or failure message.
```
[DELETE] /order_cookies/<order_id>/<cookie_id>
```





