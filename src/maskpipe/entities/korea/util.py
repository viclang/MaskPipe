def compute_checksum(rn: str) -> int:
    weights = [2, 3, 4, 5, 6, 7, 8, 9, 2, 3, 4, 5]
    return sum(int(rn[i]) * weights[i] for i in range(12))

def validate_region_code(region_code: int) -> bool:
    return 0 <= region_code <= 95
