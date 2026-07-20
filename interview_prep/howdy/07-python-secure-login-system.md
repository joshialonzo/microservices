# Python: Secure Login System

Implement a Python program using closures to create a secure login system. The closure should:

1. Store provided user credentials
2. Allow access only when the correct username and password are entered
3. Log each successful and failed login attempt

## Function Description

Complete the function `login_system` in the editor with the following parameters:

- `dict login_attempts`: a dictionary with 'success' and 'failed' as keys and their counts as the values

## Returns

- `function secure_login(string username, string password)`:
  - Manages the login process by checking the provided username and password against stored credentials.
  - Logs the attempt as either successful or failed.
  - Return Values:
    - If credentials are correct: `"Welcome, {username}!"`
    - If credentials are incorrect: `"Failed login attempt for {username}"`
- `function get_login_attempts()`:
  - This returns the `login_attempts` dictionary, which has keys 'success' and 'failed' to track the number of successful and failed login attempts.

## Constraints

- The number of users is less than or equal to 30.

## Input Format For Custom Testing

The integer in the first line denotes the number of users.
The following lines contain the {username}, {password} for each of the users.
The integer in the following line denotes the number of users trying to log in.
The following lines contain {username}, {password} for login attempts.

## Sample Case 0

**Sample Input For Custom Testing**

```
4
admin,3rTb9ZaYqF6vP2dQ8wKmXsNcRJ5tL7hP2MqU
user1,1aXc8YbOpR4eT9sD6uJnWqAcLJ3vK8eF1LpM
user2,5sFb4XnVqR2pT6dE9wKmSsNcZJ8tL5hP9MqU
user3,9aBc8YdOpR4eT9sD6uJnWqAcLJ3vK8eF1LpM
2
admin,3rTb9ZaYqF6vP2dQ8wKmXsNcRJ5tL7hP2MqU
user1,1aXc8YbOpR4eT9sD6uJnWqAcLJ3vK8eF1LpM
```

**Sample Output**

```
Welcome, admin!
Welcome, user1!
Login Attempts - Successful: 2 Failed: 0
```

**Explanation:** There are usernames and passwords for 4 users, and two login attempts. The credentials are correct for both users, so their welcome messages are displayed. Finally, the login attempt count is displayed.
