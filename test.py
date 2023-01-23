from vbml import Patcher, Pattern

pattern = Pattern('<word1> <word2> <word3>', lazy=False)
print(pattern.parse('раз два три четыре'))
print(pattern.dict())
