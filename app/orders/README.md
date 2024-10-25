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
- Required inputs: customer_id, payment_id
- Returns jsonified dictionary with the information of the new order.
```
[POST] /orders
customer_id
payment_id
```
## Show order information
- Shows order information.
- Returns jsonified dictionary with the information of the order.
```
[GET] /orders/<order_id>
```
## Update order information
- Updates order entry.
- the new `payment_received` will be added or subtracted from the currently stored `payment_received`, depending on if it is positive or negative.
- `order_status` MUST be one of the following if not None: UNFINISHED, FINISHED
    - Will not update if no cookies exist in the cookie orders.
- `delivery_status` MUST be one of the following if not None: NOT_SENT, SENT, DELIVERED, DELAYED, PICKED_UP.
- Returns jsonified dictionary with the updated information of the order.
```
[PATCH] /orders/<order_id>
customer_id
payment_id
payment_received
order_status
delivery_status
```
## Delete order
- Deletes order.
- Returns confirmation or failure message.
```
[DELETE] /orders/<order_id>
```