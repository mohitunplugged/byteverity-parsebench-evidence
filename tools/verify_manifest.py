"""Dependency-free verifier for manifest.signed.json (bv.validity.handoff.v1): Ed25519 (RFC 8032) over the canonical
JSON of the manifest without its signature fields (keys sorted at every level, compact separators, raw UTF-8).
Also checks that every file listed in the manifest is present with the recorded SHA-256.

usage: python tools/verify_manifest.py manifest.signed.json [bundle_root]"""
import hashlib, json, os, sys

p = 2**255 - 19
L = 2**252 + 27742317777372353535851937790883648493
d = -121665 * pow(121666, p - 2, p) % p
I = pow(2, (p - 1) // 4, p)


def xrecover(y):
    xx = (y * y - 1) * pow(d * y * y + 1, p - 2, p)
    x = pow(xx, (p + 3) // 8, p)
    if (x * x - xx) % p != 0:
        x = x * I % p
    if x % 2 != 0:
        x = p - x
    return x


def add(P, Q):
    (x1, y1), (x2, y2) = P, Q
    x3 = (x1 * y2 + x2 * y1) * pow(1 + d * x1 * x2 * y1 * y2, p - 2, p)
    y3 = (y1 * y2 + x1 * x2) * pow(1 - d * x1 * x2 * y1 * y2, p - 2, p)
    return x3 % p, y3 % p


def mul(P, e):
    Q = (0, 1)
    while e:
        if e & 1:
            Q = add(Q, P)
        P, e = add(P, P), e >> 1
    return Q


By = 4 * pow(5, p - 2, p) % p
B = (xrecover(By), By)


def decode_point(s):
    y = int.from_bytes(s, "little") & ((1 << 255) - 1)
    x = xrecover(y)
    if (x & 1) != (s[31] >> 7):
        x = p - x
    P = (x, y)
    if (-x * x + y * y - 1 - d * x * x * y * y) % p != 0:
        raise ValueError("point not on curve")
    return P


def verify(pub: bytes, msg: bytes, sig: bytes) -> bool:
    if len(sig) != 64 or len(pub) != 32:
        return False
    R, A, S = decode_point(sig[:32]), decode_point(pub), int.from_bytes(sig[32:], "little")
    if S >= L:
        return False
    h = int.from_bytes(hashlib.sha512(sig[:32] + pub + msg).digest(), "little")
    return mul(B, S) == add(R, mul(A, h))


m = json.load(open(sys.argv[1]))
root = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(sys.argv[1]))
sig, pub = bytes.fromhex(m.pop("signature")), bytes.fromhex(m.pop("signer_pubkey"))
kid = m.pop("signer_keyid")
canon = json.dumps(m, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
ok_sig = verify(pub, canon, sig)
bad = [f for f, h in m["bundle_files"].items()
       if not os.path.exists(os.path.join(root, f)) or hashlib.sha256(open(os.path.join(root, f), "rb").read()).hexdigest() != h]
print(f"signature: {'VALID' if ok_sig else 'INVALID'} (keyid {kid[:16]}…)  files: {len(m['bundle_files']) - len(bad)}/{len(m['bundle_files'])} match")
sys.exit(0 if ok_sig and not bad else 1)
