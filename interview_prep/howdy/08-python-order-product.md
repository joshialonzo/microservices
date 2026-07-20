# Python: Order Product

An online retail company processes customer orders if the requested quantity is in stock and the total cost does not exceed the customer's account balance. Implement the required functionality given a set of products, user balances, and orders.

The given class `Node` has two fields: `IProduct` and `int`.

Define the `Product` class to implement the `IProduct` interface available as an abstract class, with properties:

- *Id*
- *Name*
- *Price*
- *ShippingCost*

Include a constructor to initialize these properties.

Define the `User` class to implement the `IUser` interface available as an abstract class, with properties:

- *Id*
- *Name*
- *Balance*
- *Orders* (a list of Node objects)

Include a constructor to initialize the *Id*, *Name*, and *Balance* properties, and initialize *Orders* as an empty list.

Define the `Company` class to implement the `ICompany` interface available as an abstract class, with properties:

- *Products* (a list of Node objects)
- *Users* (a list of IUser objects)

Include a constructor to initialize these properties as empty lists.

Implement the `MakeOrder` method in the `Company` class to:

- Take a list of product orders and a user as input.
- Check if the requested quantities are available.
- Calculate the highest shipping cost among the items ordered.
- Determine the total cost (sum of unit prices multiplied by quantities plus the highest shipping cost).
- Verify if the user has sufficient funds.
- If conditions are met, update the user's balance, reduce the product quantities, and add the ordered products to the user's order list.

Implement the `AddProduct` method to:

- Take a product and quantity as inputs.
- Increase the quantity of the product if it already exists in the list, or add the new product to the list if it does not.

Implement the `AddUser` method to:

- Take a user as input.
- Add the user to the list of users.

## Example

There are 2 products and 1 user. This user orders 3 Laptops and 1 Phone with 100 funds in the account.

| Id | Name | Price | Shipping Cost | Quantity* |
|----|--------|-------|---------------|-----------|
| 1 | Laptop | 20 | 5 | 20 |
| 2 | Phone | 30 | 3 | 10 |

*Quantity will be used when adding products to the company.

| Id | Name | Balance |
|----|-------|---------|
| 1 | User1 | 100 |

There are more than 3 Laptops and 1 Phone available.
The higher shipping cost is 5.
Total cost is (3 × 20) + (1 × 30) + 5 = 95.
User1 has enough funds for the purchase so balances are updated.

The new quantities of products are 17 Laptops and 9 Phones. The provided code prints these values.

## Constraints

- Product IDs are distinct for each product.

## Input Format For Custom Testing

The first line contains an integer *n*, the number of products.
Each of the next *n* lines contains the (Id, Name, Price, ShippingCost, Quantity) of the product separated by commas.
The next line contains an integer *m*, the number of users.
Each of the next *m* lines contains the (Id, Name, Balance) of the user.
The next line contains an integer *k*, the number of orders.
Each of the next *k* lines contains the (UserId,ProductId|Quantity,ProductId|Quantity,...) of the order information. ("," to separate products, "|" to separate product and order quantity).

## Sample Case 0

**Sample Input**

```
2
1,product1,20,2,20
2,product2,30,1,10
1
1,user1,500
1
1,1|5,2|2
```

**Sample Output**

```
product1:15
product2:8
```

**Explanation:** Looking at the order, user1 orders 5 units of product1 and 2 units of product2. The higher price for shipping is 2 for product1. There are plenty of units on hand, 20 of product1 and 10 of product2. The total cost is (5 × 20) + (2 × 30) + 2 = 162. The user has plenty of funds, so the order is filled, and product quantities are updated.
