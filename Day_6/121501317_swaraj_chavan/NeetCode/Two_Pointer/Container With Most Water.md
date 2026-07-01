# Container With Most Water 
- https://leetcode.com/problems/container-with-most-water/
``` python 
class Solution:
    def maxArea(self, height: List[int]) -> int:

        left = 0
        right = len(height) - 1

        ans = 0

        while left < right:

            width = right - left
            area = width * min(height[left], height[right])

            ans = max(ans, area)

            if height[left] < height[right]:
                left += 1
            else:
                right -= 1

        return ans
```