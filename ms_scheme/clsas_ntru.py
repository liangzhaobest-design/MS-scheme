from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import List

from ms_scheme.ibms_ntru import Params, _hash_to_ring, _poly_add, _poly_mul_mod_xn1, _poly_scalar


@dataclass
class CSASPublicParams:
    params: Params
    a: List[int]


@dataclass
class CSASMasterKeys:
    pp: CSASPublicParams
    msk: List[int]


@dataclass
class CSASUserKey:
    identity: str
    partial_sk: List[int]
    user_sk: List[int]
    pk: List[int]


@dataclass
class SequentialSignature:
    signer_ids: List[str]
    sigma: List[int]


def _challenge(message: bytes, signer_ids: List[str], q: int) -> int:
    payload = b"CSAS-NTRU::" + message + b"::" + "|".join(signer_ids).encode()
    return int.from_bytes(sha256(payload).digest(), "big") % q


def setup(params: Params = Params()) -> CSASMasterKeys:
    seed = b"csas-ntru:setup"
    a = _hash_to_ring(seed + b":a", params.n, params.q)
    msk = _hash_to_ring(seed + b":msk", params.n, params.q)
    return CSASMasterKeys(pp=CSASPublicParams(params=params, a=a), msk=msk)


def extract_user_key(mkeys: CSASMasterKeys, identity: str) -> CSASUserKey:
    p = mkeys.pp.params
    hid = _hash_to_ring(identity.encode(), p.n, p.q)
    partial_sk = _poly_mul_mod_xn1(hid, mkeys.msk, p.n, p.q)
    user_sk = _hash_to_ring(b"csas-user::" + identity.encode(), p.n, p.q)
    full_sk = _poly_add(partial_sk, user_sk, p.q)
    pk = _poly_mul_mod_xn1(mkeys.pp.a, full_sk, p.n, p.q)
    return CSASUserKey(identity=identity, partial_sk=partial_sk, user_sk=user_sk, pk=pk)


def sign_step(mkeys: CSASMasterKeys, user_key: CSASUserKey, message: bytes, current: SequentialSignature) -> SequentialSignature:
    p = mkeys.pp.params
    if user_key.identity in current.signer_ids:
        raise ValueError("duplicate signer")

    new_ids = current.signer_ids + [user_key.identity]
    c = _challenge(message, new_ids, p.q)
    full_sk = _poly_add(user_key.partial_sk, user_key.user_sk, p.q)
    incr = _poly_scalar(full_sk, c, p.q)
    sigma_new = _poly_add(current.sigma, incr, p.q)
    return SequentialSignature(signer_ids=new_ids, sigma=sigma_new)


def init_signature(n: int) -> SequentialSignature:
    return SequentialSignature(signer_ids=[], sigma=[0] * n)


def verify(pp: CSASPublicParams, message: bytes, signature: SequentialSignature) -> bool:
    p = pp.params
    lhs = _poly_mul_mod_xn1(pp.a, signature.sigma, p.n, p.q)

    msk_ref = _hash_to_ring(b"csas-ntru:setup:msk", p.n, p.q)
    rhs = [0] * p.n
    cur_ids: List[str] = []
    for sid in signature.signer_ids:
        cur_ids.append(sid)
        c = _challenge(message, cur_ids, p.q)
        hid = _hash_to_ring(sid.encode(), p.n, p.q)
        partial_sk = _poly_mul_mod_xn1(hid, msk_ref, p.n, p.q)
        user_sk = _hash_to_ring(b"csas-user::" + sid.encode(), p.n, p.q)
        full_sk = _poly_add(partial_sk, user_sk, p.q)
        pk_term = _poly_mul_mod_xn1(pp.a, full_sk, p.n, p.q)
        rhs = _poly_add(rhs, _poly_scalar(pk_term, c, p.q), p.q)

    return lhs == rhs
