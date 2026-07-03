#count vowels and consonants in Python 


```python
word = input()

vowels = "aeiou"
v = 0

for letter in word:
    if letter in vowels:
        v = v + 1

print("Vowels =", v)
print("Consonants =", len(word) - v)
```
