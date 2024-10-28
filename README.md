# Crumbs Backend
Backend for data and route handling for the backend of the Crumbs application. 

## How to run
Running `python run.py` should begin to run the application for the backend. 

## Environment variables
In order to run, you must have a `.env` file with the following environment variables specified to the database you are using:
```
POSTRGRES_HOST=
POSTRGRES_DATABASE=
POSTRGRES_USER=
POSTRGRES_PASSWORD=
```

## List of Endpoints
All of the endpoints within the project are listed below. They are given and explained in more detail in the folders holding said routes.
### [Authentication](app/auth/)
#### Register new user
```
[GET, POST] /register
email
password
password_confirm (same as password to work)
first_name
last_name
```
#### Login user
```
[POST] /login
email
password
```
#### Logout current user
```
[POST] /logout
```
#### Delete current user
```
[DELETE] /delete_account
password
```

### [Cookies](app/cookies/)
#### List all cookies
```
[GET] /cookies
```
#### Show single cookie
```
[GET] /cookies/<cookie_name>
```

### [Inventory](app/inventory/)
#### List current user inventory
```
[GET] /users/inventory
```
#### Change current user's cookie name inventory entry
```
[POST, PATCH] /users/inventory
cookie_name
inventory
```
#### Delete current user's coookie name inventory entry
```
[DELETE] /users/inventory
cookie_name
```

### [Customers](app/customers/)
#### List current user customers
```
[GET] /customers
```
#### Create customer for current user
```
[POST] /customers
first_name
last_name
```
#### Show customer information
```
[GET] /customers/<customer_id>
```
#### Update customer information
```
[PATCH] /customers/<customer_id>
first_name
last_name
```
#### Delete customer from current user
```
[DELETE] /customers/<customer_id>
```

### [Customer Orders](app/customers/)
#### List customer's orders
```
[GET] /customers/<customer_id>/orders
```
#### Add order to customer
```
[POST] /customers/<customer_id>/orders
payment_id
notes
```
#### Show customer's order's information
```
[GET] /customers/<customer_id>/orders/<order_id>
```
#### Update customer's order's information
```
[PATCH] /customers/<customer_id>/orders/<order_id>
payment_id
notes
order_status [UNFINISHED, FINISHED]
payment_status [PAYMENT_UNCONFIRMED, PAYMENT_COMPLETE, PAYMENT_INCOMPLETE, PAYMENT_INVALID]
delivery_status [NOT_SENT, SENT, DELIVERED, DELAYED, PICKED_UP]
```
#### Delete customer's order
```
[DELETE] /customers/<customer_id>/orders/<order_id>
```

### [Orders](app/orders/) (All returned orders will include the cookies attached)
#### List current user's orders
```
[GET] /orders
```
#### Add order to customer
```
[POST] /orders
customer_id
payment_id
```
#### Show order information
```
[GET] /orders/<order_id>
```
#### Update order information
```
[PATCH] /orders/<order_id>
customer_id
payment_id
notes
order_status [UNFINISHED, FINISHED]
payment_status [PAYMENT_UNCONFIRMED, PAYMENT_COMPLETE, PAYMENT_INCOMPLETE, PAYMENT_INVALID]
delivery_status [NOT_SENT, SENT, DELIVERED, DELAYED, PICKED_UP]
```
#### Delete order
```
[DELETE] /orders/<order_id>
```

### [Order Cookies](app/order_cookies/)
#### List order's cookies
```
[GET] /orders/<order_id>/<cookie_id>
```
#### Add cookie to order
```
[POST] /orders/<order_id>/<cookie_id>
quantity (set to 0 if none given)
```
#### Update order's cookie
```
[PATCH] /orders/<order_id>/<cookie_id>
quantity (no change made if none given.)
```
#### Delete cookie from order
```
[DELETE] /orders/<order_id>/<cookie_id>
```

### [User Info](app/users/)
#### List current user's information
```
[GET] /users
```
#### List current user's information
#Use Flask-Login to get current user
```
[GET] /current-user
```
#### Change current user's email
```
[GET, PATCH] /users/change_email
new_email
password
```
#### Change current user's password
```
[GET, PATCH] /users/change_password
password (old password)
new_password
new_password_confirm (copy of old password)
```

### [Dev Tests](app/dev_tests/)
#### Restart database
```
[GET, POST] /dev_tests/init_db
(Entering a value for all of the following will add them to the database as the fourth user instead.)
email
password
password_confirm (same as password to work)
first_name
last_name
```
