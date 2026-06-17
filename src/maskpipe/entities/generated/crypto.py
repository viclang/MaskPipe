"""Entity generated from presidio_analyzer.predefined_recognizers.generic.crypto_recognizer.CryptoRecognizer."""
from hashlib import sha256
from spacy.tokens import Span
from maskpipe.entities.entity import Entity

def _decode_base58(bc: bytes) -> bytes:
    digits58 = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    origlen = len(bc)
    bc = bc.lstrip(digits58[0:1])
    n = 0
    for char in bc:
        n = n * 58 + digits58.index(char)
    return n.to_bytes(origlen - len(bc) + (n.bit_length() + 7) // 8, 'big')

def _bech32_hrp_expand(hrp):
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]

def _bech32_polymod(values):
    generator = [996825010, 642813549, 513874426, 1027748829, 705979059]
    chk = 1
    for value in values:
        top = chk >> 25
        chk = (chk & 33554431) << 5 ^ value
        for i in range(5):
            chk ^= generator[i] if top >> i & 1 else 0
    return chk

def _bech32_verify_checksum(hrp, data):
    const = _bech32_polymod(_bech32_hrp_expand(hrp) + data)
    if const == 1:
        return 1
    if const == 734539939:
        return 2
    return None

def _bech32_decode(bech):
    if any((ord(x) < 33 or ord(x) > 126 for x in bech)) or (bech.lower() != bech and bech.upper() != bech):
        return (None, None, None)
    bech = bech.lower()
    pos = bech.rfind('1')
    if pos < 1 or pos + 7 > len(bech) or len(bech) > 90:
        return (None, None, None)
    if not all((x in 'qpzry9x8gf2tvdw0s3jn54khce6mua7l' for x in bech[pos + 1:])):
        return (None, None, None)
    hrp = bech[:pos]
    data = ['qpzry9x8gf2tvdw0s3jn54khce6mua7l'.find(x) for x in bech[pos + 1:]]
    spec = _bech32_verify_checksum(hrp, data)
    if spec is None:
        return (None, None, None)
    return (hrp, data[:-6], spec)

def _validate_bech32_address(address):
    hrp, data, spec = _bech32_decode(address)
    if hrp is not None and data is not None:
        return (True, spec)
    return (False, None)

def _validator(span: Span) -> bool:
    pattern_text = span.text
    if pattern_text.startswith('1') or pattern_text.startswith('3'):
        try:
            bcbytes = _decode_base58(str.encode(pattern_text))
            checksum = sha256(sha256(bcbytes[:-4]).digest()).digest()[:4]
            return bcbytes[-4:] == checksum
        except ValueError:
            return False
    elif pattern_text.startswith('bc1'):
        if _validate_bech32_address(pattern_text)[0]:
            return True
    return False

CRYPTO = Entity(
    label="CRYPTO",
    patterns=[
        {"score": 0.5, "pattern": [{"TEXT": {"REGEX": "(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,59}"}}]},
    ],
    validator=_validator,
    context_patterns=[
        {"pattern": [{"LEMMA": {"IN": ["wallet", "btc", "bitcoin", "crypto"]}}], "score": 0.35},
    ],
)
