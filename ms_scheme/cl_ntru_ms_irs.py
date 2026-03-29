from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Iterable, List

from ms_scheme.ibms_ntru import (
    Params,
    _expand_digest_to_small_poly,
    _hash_to_ring,
    _poly_add,
    _poly_mul_mod_xn1,
    _poly_scalar,
)


@dataclass
class CLPublicParams:
    params: Params
    a: List[int]
    b: List[int]


@dataclass
class CLMasterKeys:
    pp: CLPublicParams
    msk: List[int]


@dataclass
class CLUserKey:
    identity: str
    partial_sk: List[int]
    secret_value: List[int]
    public_key: List[int]


@dataclass
class CLPartialSignature:
    identity: str
    R1: List[int]
    R2: List[int]
    z1: List[int]
    z2: List[int]


@dataclass
class CLMultiSignature:
    signer_ids: List[str]
    R1: List[int]
    R2: List[int]
    z1: List[int]
    z2: List[int]


def _challenge(message: bytes, signer_ids: Iterable[str], q: int) -> int:
    payload = message + b"::" + "|".join(sorted(signer_ids)).encode() + b"::CL_NTRU_MS_IRS"
    return int.from_bytes(sha256(payload).digest(), "big") % q


def setup(params: Params = Params()) -> CLMasterKeys:
    seed = b"cl-ntru-ms-irs:setup"
    a = _hash_to_ring(seed + b":a", params.n, params.q)
    b = _hash_to_ring(seed + b":b", params.n, params.q)
    msk = _hash_to_ring(seed + b":msk", params.n, params.q)
    return CLMasterKeys(pp=CLPublicParams(params=params, a=a, b=b), msk=msk)


def extract_user_key(mkeys: CLMasterKeys, identity: str) -> CLUserKey:
    p = mkeys.pp.params
    hid = _hash_to_ring(identity.encode(), p.n, p.q)
    partial_sk = _poly_mul_mod_xn1(hid, mkeys.msk, p.n, p.q)
    secret_value = _hash_to_ring(b"secret::" + identity.encode(), p.n, p.q)

    public_key = _poly_add(
        _poly_mul_mod_xn1(mkeys.pp.a, secret_value, p.n, p.q),
        _poly_mul_mod_xn1(mkeys.pp.b, hid, p.n, p.q),
        p.q,
    )
    return CLUserKey(identity=identity, partial_sk=partial_sk, secret_value=secret_value, public_key=public_key)


def partial_sign(mkeys: CLMasterKeys, user_key: CLUserKey, message: bytes, signer_ids: List[str]) -> CLPartialSignature:
    p = mkeys.pp.params
    if user_key.identity not in signer_ids:
        raise ValueError("user identity must be in signer_ids")

    nonce1 = sha256(b"n1::" + user_key.identity.encode() + b"::" + message).digest()
    nonce2 = sha256(b"n2::" + user_key.identity.encode() + b"::" + message).digest()
    y1 = [c % p.q for c in _expand_digest_to_small_poly(nonce1, p.n)]
    y2 = [c % p.q for c in _expand_digest_to_small_poly(nonce2, p.n)]

    R1 = _poly_mul_mod_xn1(mkeys.pp.a, y1, p.n, p.q)
    R2 = _poly_mul_mod_xn1(mkeys.pp.b, y2, p.n, p.q)

    c = _challenge(message, signer_ids, p.q)
    z1 = _poly_add(y1, _poly_scalar(user_key.partial_sk, c, p.q), p.q)
    z2 = _poly_add(y2, _poly_scalar(user_key.secret_value, c, p.q), p.q)
    return CLPartialSignature(identity=user_key.identity, R1=R1, R2=R2, z1=z1, z2=z2)


def aggregate(partials: List[CLPartialSignature], signer_ids: List[str], q: int) -> CLMultiSignature:
    if not partials:
        raise ValueError("partials cannot be empty")
    n = len(partials[0].R1)
    R1, R2, z1, z2 = [0] * n, [0] * n, [0] * n, [0] * n
    sid_sorted = sorted(signer_ids)

    for ps in partials:
        if ps.identity not in sid_sorted:
            raise ValueError(f"unexpected signer: {ps.identity}")
        R1 = _poly_add(R1, ps.R1, q)
        R2 = _poly_add(R2, ps.R2, q)
        z1 = _poly_add(z1, ps.z1, q)
        z2 = _poly_add(z2, ps.z2, q)
    return CLMultiSignature(signer_ids=sid_sorted, R1=R1, R2=R2, z1=z1, z2=z2)


def verify(pp: CLPublicParams, message: bytes, signature: CLMultiSignature) -> bool:
    p = pp.params
    c = _challenge(message, signature.signer_ids, p.q)

    lhs = _poly_add(
        _poly_mul_mod_xn1(pp.a, signature.z1, p.n, p.q),
        _poly_mul_mod_xn1(pp.b, signature.z2, p.n, p.q),
        p.q,
    )

    rhs = _poly_add(signature.R1, signature.R2, p.q)
    pk_sum = [0] * p.n
    msk_ref = _hash_to_ring(b"cl-ntru-ms-irs:setup:msk", p.n, p.q)

    for sid in signature.signer_ids:
        hid = _hash_to_ring(sid.encode(), p.n, p.q)
        partial_sk = _poly_mul_mod_xn1(hid, msk_ref, p.n, p.q)
        secret_value = _hash_to_ring(b"secret::" + sid.encode(), p.n, p.q)

        pk_term = _poly_add(
            _poly_mul_mod_xn1(pp.a, partial_sk, p.n, p.q),
            _poly_mul_mod_xn1(pp.b, secret_value, p.n, p.q),
            p.q,
        )
        pk_sum = _poly_add(pk_sum, pk_term, p.q)

    rhs = _poly_add(rhs, _poly_scalar(pk_sum, c, p.q), p.q)
    return lhs == rhs
