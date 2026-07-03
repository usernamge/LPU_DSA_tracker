# h2p2 Group Anagram

https://leetcode.com/problems/group-anagrams/description/

```python

class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        final=[]
        for i in strs:

            check = False
            for k in final:
                if i in k:
                    check=True         
            if check==True:
                continue

            temp=[]
            temp.append(i)
            for j in strs: 
                if i==j:
                    continue
                if Counter(i)==Counter(j):
                    temp.append(j)
            temp.sort()
            final.append(temp)
            
        final.sort(key=len)
        return final

```