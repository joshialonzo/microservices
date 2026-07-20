# Repository Issue Resolution

You are given *n* repositories. For each repository *i*:

- *resolved[i]* — number of issues already fixed
- *required[i]* — number of issues needed for the repository to be considered maintained

You are also given:

- *k* — the total number of additional issues that can be fixed across all repositories

A repository is considered maintained if its total resolved issues are at least its required count.

You may distribute the *k* additional fixes across repositories in any way, but the total number of fixes used cannot exceed *k*.

Determine the maximum number of repositories that can be marked as maintained after optimally distributing the additional fixes.

## Example

```
n = 2
resolved = [2, 4]
required = [4, 5]
k = 1
```

It is optimal to fix the second repository (index = 1), since the number of additional issues the developer can fix is less than what is required for the first (index = 0). Only the issues of the second repo can be resolved with the given *k*.

Hence, the answer is 1.

## Constraints

- 1 ≤ *n* ≤ 10⁵
- 0 ≤ *resolved[i]*, *required[i]*, *k* ≤ 10⁹

## Input Format For Custom Testing

The first line contains an integer, *n*, the number of elements in *resolved*.
Each of the next *n* lines contains one integer, *resolved[i]*.
The next line contains the integer, *n*, the number of elements in *required*.
Each of the next *n* lines contains one integer, *required[i]*.
The next line contains an integer, *k*.

## Sample Case 0

**Sample Input For Custom Testing**

```
STDIN       FUNCTION
-----       --------
3       →   resolved[] size n = 3
24      →   resolved[] = [24, 27, 0]
27
0
3       →   required[] size n = 3
51      →   required[] = [51, 52, 100]
52
100
100     →   k = 100
```

**Sample Output**

```
2
```

**Explanation:** Here, *resolved* = [24, 27, 0] and *required* = [51, 52, 100], so needed resolutions are [27, 25, 100]. The optimal distribution of resolutions is 27 + 25 = 52 among the first two repositories. It would take all *k* = 100 additional resolutions to maintain the third repo.
