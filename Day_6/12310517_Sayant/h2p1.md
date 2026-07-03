# h2p1 Two Sum

https://leetcode.com/problems/two-sum?q=two+sum

```python

lass Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        temp=0
        ans=[]
        for i in range(len(nums)):
            for j in range(len(nums)):
                if i==j:
                    continue
                temp=nums[i]+nums[j]
                if temp==target:
                    ans.append(i)
                    ans.append(j)
                    return ans
                    
```