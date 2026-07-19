# YouTube Channel Recommendations

Implement a prototype of a channel collaboration recommendation system for YouTube.

There are *n* channels indexed from 0 to *n−1*, and *m* collaborations are represented as a 2d array, *collaborations*, where the *iᵗʰ* collaboration is a connection between channels *collaborations[i][0]* and *collaborations[i][1]*.

A channel *x* is suggested as a collaborator to channel *y* if:

1. *x* and *y* are not already collaborators
2. *x* and *y* have the maximum number of common collaborators (collaborators that are connected to both *x* and *y*)
3. If multiple channels satisfy conditions 1 and 2, the channel with the minimum index is recommended

Given *n* and *collaborations*, for each of the *n* channels, find the index of the collaborator that should be recommended. If no recommendation is available, report -1.

## Example

Suppose `n = 5`, `m = 5`, and `connections = [[0, 1], [0, 2], [1, 3], [2, 3], [3, 4]]`

```
        2
      /   \
    0       3 --- 4
      \   /
        1
```

| Channel | Max Common Collaborators With | Recommendation |
|---------|-------------------------------|----------------|
| 0 | 3 (1, 2) | 3 |
| 1 | 2 (0, 3) | 2 |
| 2 | 1 (0, 3) | 1 |
| 3 | 0 (1, 2) | 0 |
| 4 | 2 (3), 1 (3) | 1 (minimum index) |

Hence the answer returned is `[3, 2, 1, 0, 1]`.

## Function Description

Complete the function `getRecommendedCollaborators` in the editor with the following parameters:

- `int n`: the number of YouTube channels
- `int collaborations[m][2]`: the collaborations between the YouTube channels

## Constraints

- 1 ≤ *n* ≤ 10⁵
- 0 ≤ *m* ≤ 2.5×10⁵
- 0 ≤ *collaborations[i][0]*, *collaborations[i][1]* < *n*
- There are no self-loops or multiple edges.
- Each channel has a maximum of 15 collaborators.
- The collaboration network might be disjoint.

## Input Format For Custom Testing

The first line contains an integer, *n*.
The next line contains an integer, *m*, the size of *collaborations*.
The next line contains a constant integer, 2, the size of *collaborations[i]*.
Each line *i* of the *m* subsequent lines contains two integers *collaborations[i][0]* and *collaborations[i][1]*.

## Sample Case 0

**Sample Input For Custom Testing**

```
STDIN       FUNCTION
-----       --------
3       →   n = 3
3       →   m = 3
2
0 1     →   collaborations = [[0, 1], [1, 2], [2, 0]]
1 2
2 0
```

**Sample Output**

```
-1
-1
-1
```

**Explanation:** All YouTube channels are connected to each other (triangle 0–1–2), so no recommendation can be made.

## Sample Case 1

**Sample Input For Custom Testing**

```
STDIN       FUNCTION
-----       --------
3       →   n = 3
2       →   m = 2
2
0 1     →   collaborations = [[0, 1], [0, 2]]
0 2
```

**Sample Output**

```
-1
2
1
```

**Explanation:** Since YouTube channel 0 is connected to both channels, no recommendation can be made for it. As common collaborators via channel 0, channels 1 and 2 can be recommended to each other.
