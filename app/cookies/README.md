# Cookies
Endpoints handling the retrieval of information regarding cookies in the database.

## List all cookies
- Returns a list of all the cookies in the database in a JSON format.
```
[GET] /cookies
```
## Show single cookie
- Returns the information about a cookie with the "cookie_name" placed in the endpoint.
- Cookie must be in the database.
```
[GET] /cookies/<cookie_name>
```