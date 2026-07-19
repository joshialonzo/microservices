# Google Server Min-max

For each contiguous group of Google server racks of length *x*, determine the minimum available disk capacity within that group. Then compute the maximum value among all group minima.

## Example 1

**Input:** `x = 2` (the segment length), `n = 4` (the number of server racks), `space = [8, 2, 4, 6]`

**Output:** `4`

**Explanation:** The contiguous groups of length 2 are [8, 2], [2, 4], and [4, 6]. The minimum values in each group are 2, 2, and 4, respectively. The maximum among the minima is 4.

## Example 2

**Input:** `x = 1`, `n = 5`, `space = [1, 2, 3, 1, 2]`

**Output:** `3`

**Explanation:** The groups of size x = 1 are [1], [2], [3], [1], and [2]. Each value is the minimum for the corresponding group.

## Constraints

- 1 ≤ *n* ≤ 10⁶
- 1 ≤ *x* ≤ *n*
- 1 ≤ *space[i]* ≤ 10⁹

## Test Case Input Format

The first line contains an integer, *x*, representing the rack group length.
The second line contains an integer, *n*, the size of the array *space*.
Each of the next *n* lines contains an integer, *space[i]*, representing available disk capacity for a rack.
