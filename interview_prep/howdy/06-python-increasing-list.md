# Python: Increasing List

Create a Python class called `IncreasingList` that maintains a list of elements in non-decreasing order. This class should implement the following three methods:

1. `append(self, val)`: This method removes all elements from the list that are greater than *val*, starting from the end of the list. Once all greater elements are removed, it appends *val* to the end of the list.
2. `pop(self)`: This method removes the last element from the list if the list is not empty. If the list is empty, it does nothing.
3. `len(self)`: This method returns the number of elements currently in the list.

Additional methods can be added as needed, but the three specified methods must be implemented. The list is guaranteed to be in non-decreasing order at all times due to the behavior of the *append* and *pop* methods.

The implemented methods will be tested using a provided code stub on multiple input files. Each input file contains several operations of the following types:

- `append val`: Calls `append(val)` on the IncreasingList instance.
- `pop`: Calls `pop()` on the IncreasingList instance.
- `size`: Calls `len(obj)` on the IncreasingList instance and prints the returned value.

## Example

Suppose operations are `"size"`, `"append 2"`, `"append 4"`, `"append 5"`, `"size"`, `"append 2"`, `"size"`, `"pop"`, and `"size"`

**Output:**

```
0
3
2
1
```

Explanation of each operation. Start with an empty list called `lst[]`:

1. Return the size of the list, and 0 is printed to the output.
2. Append 2 to the list. Since there are no elements greater than 2 in the list, no elements are removed, and 2 is appended: `lst = [2]`.
3. Append 4 to the list. There are no elements greater than 4, so no elements are removed, and 4 is appended: `lst = [2, 4]`.
4. Append 5 to the list. There are no elements greater than 5, so no elements are removed, and 5 is appended: `lst = [2, 4, 5]`.
5. Return the size of the list, and 3 is printed to the output.
6. Append 2 to the list. There are two elements greater than 2, so they are removed first, starting from the end. After they are removed, 2 is appended: `lst = [2, 2]`.
7. Return the size of the list, and 2 is printed to the output.
8. Pop removes the last element from the list: `lst = [2]`.
9. Return the size of the list, and 1 is printed to the output.

## Constraints

- 1 ≤ number of operations in one test file ≤ 10⁵
- If *val* is a parameter of operation, then *val* is an integer and 1 ≤ *val* ≤ 10⁵
- It is guaranteed that there is at least one operation of type *size* in every test file.

## Test Case Input Format

In the first line, there is a single integer, *q*, the number of queries.
Then, *q* lines follow. In the *iᵗʰ* of them, there is a string that denotes an operation and, optionally, an integer that denotes the parameter of the operation.
