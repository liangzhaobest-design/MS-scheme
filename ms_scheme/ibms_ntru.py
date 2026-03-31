from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Iterable, List


@dataclass(frozen=True)
class Params:
    n: int = 107
    q: int = 2048


@dataclass
class PublicParams:
    params: Params
    a: List[int]


@dataclass
class MasterKeys:
    mpk: PublicParams
    msk: List[int]


@dataclass
class UserKey:
    identity: str
    sk: List[int]
    pk: List[int]


@dataclass
class PartialSignature:
    identity: str
    R: List[int]
    z: List[int]


@dataclass
class MultiSignature:
    signer_ids: List[str]
    R: List[int]
    z: List[int]


def _mod_q(x: int, q: int) -> int:
    return x % q


def _poly_add(a: List[int], b: List[int], q: int) -> List[int]:
    return [((x + y) % q) for x, y in zip(a, b)]


def _poly_scalar(a: List[int], c: int, q: int) -> List[int]:
    return [((x * c) % q) for x in a]


def _poly_mul_mod_xn1(a: List[int], b: List[int], n: int, q: int) -> List[int]:
    out = [0] * n
    for i in range(n):
        ai = a[i]
        if ai == 0:
            continue
        for j in range(n):
            v = ai * b[j]
            k = i + j
            if k < n:
                out[k] = (out[k] + v) % q
            else:
                # x^n == -1
                out[k - n] = (out[k - n] - v) % q
    return out


def _expand_digest_to_small_poly(seed: bytes, n: int) -> List[int]:
    # coeffs in {-1,0,1}
    coeffs: List[int] = []
    ctr = 0
    while len(coeffs) < n:
        h = sha256(seed + ctr.to_bytes(4, "big")).digest()
        for b in h:
            coeffs.append((b % 3) - 1)
            if len(coeffs) == n:
                break
        ctr += 1
    return coeffs


def _hash_to_ring(data: bytes, n: int, q: int) -> List[int]:
    small = _expand_digest_to_small_poly(data, n)
    return [c % q for c in small]


def _challenge(message: bytes, signer_ids: Iterable[str], q: int) -> int:
    ids_part = "|".join(sorted(signer_ids)).encode()
    digest = sha256(message + b"::" + ids_part).digest()
    return int.from_bytes(digest, "big") % q


def setup(params: Params = Params()) -> MasterKeys:
    seed = b"ms-scheme:setup"
    a = _hash_to_ring(seed + b":a", params.n, params.q)
    msk = _hash_to_ring(seed + b":msk", params.n, params.q)
    mpk = PublicParams(params=params, a=a)
    return MasterKeys(mpk=mpk, msk=msk)


def extract_user_key(mkeys: MasterKeys, identity: str) -> UserKey:
    p = mkeys.mpk.params
    hid = _hash_to_ring(identity.encode(), p.n, p.q)
    sk = _poly_mul_mod_xn1(hid, mkeys.msk, p.n, p.q)
    pk = _poly_mul_mod_xn1(mkeys.mpk.a, sk, p.n, p.q)
    return UserKey(identity=identity, sk=sk, pk=pk)


def partial_sign(
    mkeys: MasterKeys,
    user_key: UserKey,
    message: bytes,
    signer_ids: List[str],
) -> PartialSignature:
    p = mkeys.mpk.params
    if user_key.identity not in signer_ids:
        raise ValueError("user identity must be in signer_ids")

    nonce_seed = sha256(
        b"nonce::" + user_key.identity.encode() + b"::" + message + b"::" + "|".join(sorted(signer_ids)).encode()
    ).digest()
    y = _expand_digest_to_small_poly(nonce_seed, p.n)
    yq = [c % p.q for c in y]
    R = _poly_mul_mod_xn1(mkeys.mpk.a, yq, p.n, p.q)

    c = _challenge(message, signer_ids, p.q)
    z = _poly_add(yq, _poly_scalar(user_key.sk, c, p.q), p.q)
    return PartialSignature(identity=user_key.identity, R=R, z=z)


def aggregate(partials: List[PartialSignature], signer_ids: List[str], q: int) -> MultiSignature:
    if not partials:
        raise ValueError("partials cannot be empty")
    n = len(partials[0].R)
    R = [0] * n
    z = [0] * n
    sid_sorted = sorted(signer_ids)
    for ps in partials:
        if ps.identity not in sid_sorted:
            raise ValueError(f"unexpected signer: {ps.identity}")
        R = _poly_add(R, ps.R, q)
        z = _poly_add(z, ps.z, q)
    return MultiSignature(signer_ids=sid_sorted, R=R, z=z)


def verify(mpk: PublicParams, message: bytes, signature: MultiSignature) -> bool:
    p = mpk.params
    c = _challenge(message, signature.signer_ids, p.q)

    lhs = _poly_mul_mod_xn1(mpk.a, signature.z, p.n, p.q)

    rhs = signature.R.copy()
    pk_sum = [0] * p.n
    for sid in signature.signer_ids:
        hid = _hash_to_ring(sid.encode(), p.n, p.q)
        sk_derived = _poly_mul_mod_xn1(hid, _hash_to_ring(b"ms-scheme:setup:msk", p.n, p.q), p.n, p.q)
        pk = _poly_mul_mod_xn1(mpk.a, sk_derived, p.n, p.q)
        pk_sum = _poly_add(pk_sum, pk, p.q)

    rhs = _poly_add(rhs, _poly_scalar(pk_sum, c, p.q), p.q)
    return lhs == rhs
