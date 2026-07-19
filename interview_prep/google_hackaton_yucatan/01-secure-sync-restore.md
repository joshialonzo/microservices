# Secure Sync Restore

Google Secure Sync is being developed to provide end-to-end encryption for file synchronization across devices. As part of the system, a decryption function must run whenever an account signs in to the Google Secure Sync service.

The encryption method involves replacing each letter in a file with another letter shifted by a fixed number of positions down the alphabet. The shift value acts as the private key for each account. The decryption algorithm can be described as follows:

- *cipher* represents the encrypted content of the file (comprising lowercase or uppercase English letters without spaces)
- *key* indicates the fixed number of positions down the alphabet (the shift value)

Letters, whether lowercase or uppercase, are shifted left from their original positions, wrapping around the alphabet if necessary. For example, 'a' with a key of 1 becomes 'z', and 'A' with a key of 1 becomes 'Z'.

## Example

Given the *cipher* `'KcoTKQ'` and a *key* of `2`, the function should return `'IamRIO'`. The decryption process involves shifting each letter back from its original position by 2 positions:

```
'K' -> 'I'
'c' -> 'a'
'o' -> 'm'
'T' -> 'R'
'K' -> 'I'
'Q' -> 'O'
```

## Function Description

Complete the function `restore_sync` in the editor with the following parameter(s):

- `str cipher`: a string consisting of lowercase or uppercase English letters
- `int key`: the shift value

## Return

- `str`: the decrypted string

## Constraints

- 1 ≤ length of *cipher* ≤ 2×10⁵
- 0 ≤ *key* ≤ 10⁹

## Sample Case 0

**Sample Input For Custom Testing**

```
MPSZILEGOIVVERO
4
```

**Sample Output 0**

```
ILOVEHACKERRANK
```

**Explanation:** The decryption process involves shifting each letter back to its original position by 4 positions. For example, 'M' to 'I', 'P' to 'L', and so on.
