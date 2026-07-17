# Two Integer Sum II 
- https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/

``` python 
class Solution:
    def twoSum(self, numbers: List[int], target: int) -> List[int]:
        for i in range(len(numbers)):
             for j in range (i +1, len(numbers)):
                if numbers[i]+ numbers[j]== target:
                    return [i+1,j+1]
        return[]       
```