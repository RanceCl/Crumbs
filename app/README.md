# Crumbs Backend App
Application folder for the backend of the Crumbs application. 

## Models
### Users
| id | email | password_hash | first_name | last_name |
| --- | --- | --- | --- | --- |
| 12 | bestfrienddoggy@email.com | hashed_password | Best | Friend |

- Emails are set by the `set_email` method to ensure that emails are in the proper format before adding/changing.
- Passwords are set by `set_password`, which requires the same password to be provided for confirmation, as well as ensuring passwords follow the proper format.
- Passwords are not stored directly, but rather have a hash generated for them. This hash can be compared against a string to make sure they match.
- The user table also has the user mixin implemented, allowing for user login and management. 

### Cookies
| id | cookie_name | description | price | picture_url |
| --- | --- | --- | --- | --- |
| 2 | lemonaids | Long description text. | 6.00 | url_example |

### Payment_Types
| id | payment_type_name |
| --- | --- |
| 3 | PayPal |

### Customers
| id | first_name | last_name | user_id |
| --- | --- | --- | --- |
| 13 | Marley | Mittens | 12 |

### Orders
| id | customer_id | payment_id | notes | date_added | date_modified | order_status_stored | payment_status_stored | delivery_status_stored | 'total_cost' |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 32 | 13 | 4 | 17.00 | 10/10/2010 | 10/11/2010 | FINISHED | PAYMENT_INCOMPLETE | NOT_SENT | 42.00 |

- `order_status_stored` will always be one of the following: `UNFINISHED`, `FINISHED`
- `payment_status_stored` will always be one of the following: `PAYMENT_UNCONFIRMED`, `PAYMENT_COMPLETE`, `PAYMENT_INCOMPLETE`, `PAYMENT_INVALID`
- `delivery_status_stored` will always be one of the following: `NOT_SENT`, `SENT`, `DELIVERED`, `DELAYED`, `PICKED_UP`
- A total cost property is present, which is automatically calculated from the cookies attached to the order. 
- Payment status updates automatically depending on if a valid payment type has been selected as well as if the payment received meets the total cost.

### Cookie_Inventory
| user_id | cookie_id | inventory | 'projected_inventory' |
| --- | --- | --- | --- |
| 12 | 2 | 85 | 30 |

- Projected inventory adjusts automatically to represent what the current inventory would look like if all orders for the user were applied.

### Order_Cookies
| order_id | cookie_id | quantity | 'cost' |
| --- | --- | --- | --- |
| 32 | 2 | 4 | 24.00 |

- Cost property is automatically calculated based on the quantity of desired cookies and the cost of the desired cookie.


## List of Endpoints
All of the endpoints within the project are listed below. They are given and explained in more detail in the folders holding said routes.
### [Authentication](auth/)
- Register new user: `[GET, POST] /register`
- Login user: `[POST] /login`
- Logout current user: `[POST] /logout`
- Delete current user: `[DELETE] /delete_account`

### [Cookies](cookies/)
- List all cookies: `[GET] /cookies`
- Show single cookie: `[GET] /cookies/<cookie_name>`

### [Inventory](inventory/)
- List current user inventory: `[GET] /users/inventory`
- Change current user's cookie name inventory entry: `[POST, PATCH] /users/inventory`
- Delete current user's coookie name inventory entry: `[DELETE] /users/inventory`

### [Customers](customers/)
- List current user customers: `[GET] /customers`
- Create customer for current user: `[POST] /customers`
- Show customer information: `[GET] /customers/<customer_id>`
- Update customer information: `[PATCH] /customers/<customer_id>`
- Delete customer from current user: `[DELETE] /customers/<customer_id>`

### [Customer Orders](customers/)
- List customer's orders: `[GET] /customers/<customer_id>/orders`
- Add order to customer: `[POST] /customers/<customer_id>/orders`
- Show customer's order's information: `[GET] /customers/<customer_id>/orders/<order_id>`
- Update customer's order's information: `[PATCH] /customers/<customer_id>/orders/<order_id>`
- Delete customer's order: `[DELETE] /customers/<customer_id>/orders/<order_id>`

### [Orders](orders/) (All returned orders will include the cookies attached)
- List current user's orders: `[GET] /orders`
- Add order to customer: `[POST] /orders`
- Show order information: `[GET] /orders/<order_id>`
- Update order information: `[PATCH] /orders/<order_id>`
- Delete order: `[DELETE] /orders/<order_id>`

### [Order Cookies](order_cookies/)
- List order's cookies: `[GET] /orders/<order_id>/<cookie_id>`
- Add cookie to order: `[POST] /orders/<order_id>/<cookie_id>`
- Update order's cookie: `[PATCH] /orders/<order_id>/<cookie_id>`
- Delete cookie from order: `[DELETE] /orders/<order_id>/<cookie_id>`

### [User Info](users/)
- List current user's information: `[GET] /users`
- List current user's information: `[GET] /current-user`
- Change current user's email: `[GET, PATCH] /users/change_email`
- Change current user's password: `[GET, PATCH] /users/change_password`

### [Dev Tests](dev_tests/)
- Restart database: `[GET, POST] /dev_tests/init_db`
