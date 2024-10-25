# Customers
Endpoints that handle the addition of customers as well as handling information about them. All routes that attempt to access a customer require the id of the customer to belong to the user to be successful. All routes require user login.

## List current user customers
- Retrieves the list of customers belonging to the currently logged in user.
- Returns as a list within a dictionary.
```
[GET] /customers
```
## Create customer for current user
- Creates a new customer for the logged in user.
- Required inputs: first_name, last_name
- Returns confirmation message with the full name of the customer.
```
[POST] /customers
first_name
last_name
```
## Show customer information
- Retrieves the information of the customer with the given customer id.
- Returns jsonified dictionary with customer information.
```
[GET] /customers/<customer_id>
```
## Update customer information
- Updates the information of the customer with the given customer id.
- Required inputs: first_name, last_name
- Returns jsonified dictionary with new customer information.
```
[PATCH] /customers/<customer_id>
first_name
last_name
```
## Delete customer from current user
- Deletes customer entry. 
- Returns confirmation or failure message.
```
[DELETE] /customers/<customer_id>
```
# Customer Orders
Endpoints that handle the addition of orders to customers as well as handling information about them. All routes redirect to their corresponding order endpoints. All routes require user login. 

## List customer's orders
- Lists all of the orders belonging to the customer.
- Reroutes to the endpoint to retrieve all orders.
- Returns as a list within a dictionary.
```
[GET] /customers/<customer_id>/orders
```
## Add order to customer
- Adds an order to the customer with the id in the endpoint.
- Required inputs: payment_id
- Rerouts to orders endpoint to add an order to a customer, using the current customer's id.
- Returns jsonified dictionary with the information of the new order.
```
[POST] /customers/<customer_id>/orders
payment_id
```
## Show customer's order's information
- Lists the information on the order with the order_id belonging to the customer with the id in the endpoint. 
- Rerouts to orders endpoint to retrieve the information an order, using the current customer's id.
- Isn't limited to customers belonging to the logged in user, but IS limited to orders that belong to the customer.
- Returns jsonified dictionary with the information of the order.
```
[GET] /customers/<customer_id>/orders/<order_id>
```
## Update customer's order's information
- Updates the information on the order with the order_id belonging to the user with the id in the endpoint. 
- Only works for orders that belong to the customer.
- the new `payment_received` will be added or subtracted from the currently stored `payment_received`, depending on if it is positive or negative.
- `order_status` MUST be one of the following if not None: UNFINISHED, FINISHED
    - Will not update if no cookies exist in the cookie orders.
- `delivery_status` MUST be one of the following if not None: NOT_SENT, SENT, DELIVERED, DELAYED, PICKED_UP.
- Returns jsonified dictionary with the updated information of the order.
```
[PATCH] /customers/<customer_id>/orders/<order_id>
customer_id
payment_id
payment_received
order_status
delivery_status
```
## Delete customer's order
- Deletes the entry for the order with the order_id belonging to the user with the id in the endpoint. 
- Only works for orders that belong to the customer.
- Returns confirmation or failure message.
```
[DELETE] /customers/<customer_id>/orders/<order_id>
```