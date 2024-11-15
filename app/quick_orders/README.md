# Quick Orders
Endpoints that handle the addition of orders quickly. All routes that return order information will also return all of the cookies that are attached to an order when returned. All routes require user login.

## Add order to user quickly.
Adds order for a customer.
- Required inputs: payment_type_name, cookies
- `payment_type_name` uses one of the following: Cash, Credit, Venmo, PayPal.
- `cookies` is a list of dictionaries that hold the id and the quantity of each cookie that should be added.
- Returns jsonified dictionary with the information of the new order.
```
[POST] /quick_orders
payment_type_name
notes
cookies = [
    {"id": [cookie_id], "quantity": [quantity]},
    {"id": [cookie_id], "quantity": [quantity]},
    {"id": [cookie_id], "quantity": [quantity]}
]