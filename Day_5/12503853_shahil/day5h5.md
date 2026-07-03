
# h5p2
# 643. Maximum Average Subarray 

**https://leetcode.com/problems/maximum-average-subarray-i/description/**


```python
class Solution:
    def findMaxAverage(self, nums: List[int], k: int):
        current_sum = sum(nums[:k])
        max_sum = current_sum
        for i in range(k, len(nums)):
            current_sum += nums[i] - nums[i-k]
            max_sum = max(max_sum, current_sum)
        return max_sum / k
```


#problem 1512

https://leetcode.com/problems/number-of-good-pairs/description/



```python
class Solution:
    def numIdenticalPairs(self, nums: List[int]) -> int:
        count = 0
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                if nums[i] == nums[j]:
                    count += 1
        return count
```

