# Security Grouping - Google

A Google Cloud project has *n* services where *riskLevel[i]* represents the risk score of the *iᵗʰ* Cloud service. All services in a service tier must have the same risk score, and the number of services in any two service tiers should not differ by more than 1.

Find the minimum number of service tiers needed to organize the project resources within Google Cloud.

## Example

For `n = 6`, `riskLevel = [2, 3, 3, 3, 2, 1]`:

The services need to be grouped into 4 service tiers: `[2, 2], [3, 3], [3], [1]`

## Function Description

Complete the function `getMinimumTiers` in the editor with the following parameters:

- `int riskLevel[n]`: the risk scores of the services

## Returns

- `int`: the minimum number of tiers required

## Constraints

- 1 ≤ *n* ≤ 10⁵
- 1 ≤ *riskLevel[i]* ≤ 10⁵

## Sample Case 0

**Sample Input For Custom Testing**

```
STDIN       FUNCTION
-----       --------
5       →   n = 5
1       →   riskLevel = [1, 7, 7, 7, 1]
7
7
7
1
```

**Sample Output**

```
2
```

**Explanation:**

- Tier 1: 3 Google Cloud services of risk score 7
- Tier 2: 2 Google Cloud services of risk score 1
