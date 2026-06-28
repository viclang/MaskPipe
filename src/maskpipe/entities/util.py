from typing import List, Tuple

def sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
    for search_string, replacement_string in replacement_pairs:
        text = text.replace(search_string, replacement_string)
    return text

def luhn_checksum(digits: str) -> bool:
    nums = [int(d) for d in digits]
    odd_digits = nums[-1::-2]
    even_digits = nums[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(int(dig) for dig in str(d * 2))
    return checksum % 10 == 0

def is_verhoeff_number(input_number: int) -> bool:
    __d__ = [[0,1,2,3,4,5,6,7,8,9],[1,2,3,4,0,6,7,8,9,5],[2,3,4,0,1,7,8,9,5,6],[3,4,0,1,2,8,9,5,6,7],[4,0,1,2,3,9,5,6,7,8],[5,9,8,7,6,0,4,3,2,1],[6,5,9,8,7,1,0,4,3,2],[7,6,5,9,8,2,1,0,4,3],[8,7,6,5,9,3,2,1,0,4],[9,8,7,6,5,4,3,2,1,0]]
    __p__ = [[0,1,2,3,4,5,6,7,8,9],[1,5,7,6,2,8,3,0,9,4],[5,8,0,3,7,9,6,1,4,2],[8,9,1,6,0,4,3,5,2,7],[9,4,5,3,1,2,6,8,7,0],[4,2,8,6,5,7,3,9,0,1],[2,7,9,3,8,0,6,4,1,5],[7,0,4,6,9,1,3,2,5,8]]
    __inv__ = [0,4,3,2,1,5,6,7,8,9]
    c = 0
    inverted_number = list(map(int, reversed(str(input_number))))
    for i in range(len(inverted_number)):
        c = __d__[c][__p__[i % 8][inverted_number[i]]]
    return __inv__[c] == 0
