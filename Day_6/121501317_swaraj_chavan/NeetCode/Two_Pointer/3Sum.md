# 3Sum 
- https://leetcode.com/problems/3sum/description/
``` python 
class Solution:
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        nums.sort()
        res = []

        for i in range(len(nums)):

            # Skip duplicate first elements
            if i > 0 and nums[i] == nums[i - 1]:
                continue

            l = i + 1
            r = len(nums) - 1

            while l < r:

                total = nums[i] + nums[l] + nums[r]

                if total < 0:
                    l += 1

                elif total > 0:
                    r -= 1

                else:
                    res.append([nums[i], nums[l], nums[r]])

                    l += 1
                    r -= 1

                    # Skip duplicate second elements
                    while l < r and nums[l] == nums[l - 1]:
                        l += 1

                    # Skip duplicate third elements
                    while l < r and nums[r] == nums[r + 1]:
                        r -= 1

        return res
```