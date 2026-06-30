# 3 Sum

- https://leetcode.com/problems/3sum/

```python

class Solution:
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        nums.sort()
        res = []

        for i in range(len(nums)):
            left = i + 1
            right = len(nums) - 1

            while left < right:
                total = nums[i] + nums[left] + nums[right]

                if total == 0:
                    triplet = [nums[i], nums[left], nums[right]]

                    if triplet not in res:
                        res.append(triplet)

                    left += 1
                    right -= 1

                elif total < 0:
                    left += 1
                else:
                    right -= 1

        return res

```