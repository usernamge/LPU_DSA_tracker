# Two Sum II - Input Array is Sorted

- https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/description/

```python

class Solution:
    def twoSum(self, numbers: List[int], target: int) -> List[int]:
        indices = [0]*2
        start = 0
        end = len(numbers)-1
        while start<end:
            if numbers[start]+numbers[end]==target:
                indices[0]=start+1
                indices[1]=end+1
                return indices
            elif numbers[start]+numbers[end]>target:
                end-=1
            else:
                start+=1
        return indices

```