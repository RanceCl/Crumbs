# Orders
Endpoints that handle the addition of orders as well as handling information about them. All routes that return order information will also return all of the cookies that are attached to an order when returned. All routes require user login.

## List current user's orders
- Retrieve a list of the orders that are associated to the logged in user via their customers.
- Returns as a list within a dictionary.
```
[GET] /orders
```
## Add order to customer
Adds order for a customer.
- Required inputs: customer_id, payment_type_name
- `payment_type_name` uses one of the following: Cash, Credit, Venmo, PayPal.
- Returns jsonified dictionary with the information of the new order.
```
[POST] /orders
customer_id
payment_type_name
notes
```
## Show order information
- Shows order information.
- Returns jsonified dictionary with the information of the order.
```
[GET] /orders/<order_id>
```
## Update order information
- Updates order entry.
- `payment_type_name` uses one of the following: Cash, Credit, Venmo, PayPal.
- `payment_status` MUST be one of the following if not None: "Unconfirmed", "Complete", "Incomplete", "Invalid".
- `delivery_status` MUST be one of the following if not None: "Not Sent", "Mailed", "Delivered", "Delayed", "Picked Up".
- `order_status` MUST be one of the following if not None: "Incomplete", "Complete".
- Returns jsonified dictionary with the updated information of the order.
```
[PATCH] /orders/<order_id>
customer_id
payment_type_name
notes
payment_status
delivery_status
order_status
```
## Delete order
- Deletes order.
- Returns confirmation or failure message.
```
[DELETE] /orders/<order_id>
```