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
