from hashlib import sha256
from typing import List, Tuple

from spacy.tokens import Doc, Span

from .entity import Entity

# Constants for Bech32/Bech32m address validation
CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
BECH32M_CONST = 0x2BC830A3


def _bech32_polymod(values: List[int]) -> int:
    """Compute the Bech32 checksum."""
    generator = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]
    chk = 1
    for value in values:
        top = chk >> 25
        chk = (chk & 0x1FFFFFF) << 5 ^ value
        for i in range(5):
            chk ^= generator[i] if ((top >> i) & 1) else 0
    return chk


def _bech32_hrp_expand(hrp: str) -> List[int]:
    """Expand the HRP into values for checksum computation."""
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]


def _bech32_verify_checksum(hrp: str, data: List[int]) -> int | None:
    """Verify a checksum given HRP and converted data characters."""
    const = _bech32_polymod(_bech32_hrp_expand(hrp) + data)
    if const == 1:
        return 1  # BECH32
    if const == BECH32M_CONST:
        return 2  # BECH32M
    return None


def _bech32_decode(bech: str) -> tuple:
    """Validate a Bech32/Bech32m string, and determine HRP and data."""
    if (any(ord(x) < 33 or ord(x) > 126 for x in bech)) or (
        bech.lower() != bech and bech.upper() != bech
    ):
        return (None, None, None)
    bech = bech.lower()
    pos = bech.rfind("1")
    if pos < 1 or pos + 7 > len(bech) or len(bech) > 90:
        return (None, None, None)
    if not all(x in CHARSET for x in bech[pos + 1 :]):
        return (None, None, None)
    hrp = bech[:pos]
    data = [CHARSET.find(x) for x in bech[pos + 1 :]]
    spec = _bech32_verify_checksum(hrp, data)
    if spec is None:
        return (None, None, None)
    return (hrp, data[:-6], spec)


def _decode_base58(bc: bytes) -> bytes:
    """Decode Base58 encoded Bitcoin address."""
    digits58 = b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    origlen = len(bc)
    bc = bc.lstrip(digits58[0:1])

    n = 0
    for char in bc:
        n = n * 58 + digits58.index(char)
    return n.to_bytes(origlen - len(bc) + (n.bit_length() + 7) // 8, "big")


def _valid_crypto(span: Span) -> bool:
    """
    Validate a Bitcoin/crypto address using checksum.

    Supports:
    - P2PKH (starts with 1): Base58 + SHA256 checksum
    - P2SH (starts with 3): Base58 + SHA256 checksum
    - Bech32/Bech32m (starts with bc1): Bech32 checksum
    """
    addr = span.text.strip()

    if addr.startswith("1") or addr.startswith("3"):
        # P2PKH or P2SH address validation
        try:
            bcbytes = _decode_base58(addr.encode("ascii"))
            checksum = sha256(sha256(bcbytes[:-4]).digest()).digest()[:4]
            return bcbytes[-4:] == checksum
        except (ValueError, UnicodeEncodeError):
            return False
    elif addr.startswith("bc1"):
        # Bech32 or Bech32m address validation
        try:
            hrp, data, spec = _bech32_decode(addr)
            return hrp is not None and data is not None
        except Exception:
            return False
    return False


class CryptoMatcher:
    """Matcher for crypto wallet addresses using regex."""

    def __call__(self, doc: Doc) -> List[Tuple[int, int, float]]:
        """Find crypto addresses in the document."""
        import re

        matches = []
        # Match P2PKH (1...), P2SH (3...), and Bech32 (bc1...) addresses
        pattern = r"(?:bc1|[13])[a-zA-HJ-NP-Z0-9]{25,59}"
        for match in re.finditer(pattern, doc.text):
            span = doc.char_span(match.start(), match.end())
            if span:
                matches.append((span.start, span.end, 0.5))
        return matches


CRYPTO = Entity(
    label="CRYPTO",
    custom_matcher=CryptoMatcher(),
    validator=_valid_crypto,
    context_patterns=[
        {"pattern": [{"LOWER": {"FUZZY": "wallet"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "btc"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "bitcoin"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "crypto"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "address"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "blockchain"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "ethereum"}}]},
        {"pattern": [{"LOWER": {"FUZZY": "eth"}}]},
    ],
)
