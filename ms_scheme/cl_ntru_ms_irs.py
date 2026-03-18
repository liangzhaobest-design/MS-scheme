from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Iterable, List

from ms_scheme.ibms_ntru import Params, _hash_to_ring, _poly_add, _poly_mul_mod_xn1, _poly_scalar


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
    compact_sk: List[int]
    public_key: List[int]


@dataclass
class CLPartialSignature:
    identity: str
    z: List[int]


@dataclass
class CLMultiSignature:
    signer_ids: List[str]
    z: List[int]


def _challenge(message: bytes, signer_ids: Iterable[str], q: int) -> int:
    payload = message + b"::" + "|".join(sorted(signer_ids)).encode() + b"::CL_NTRU_MS_IRS_COMPRESSED"
    return int.from_bytes(sha256(payload).digest(), "big") % q


def _combined_base(pp: CLPublicParams) -> List[int]:
    return _poly_add(pp.a, pp.b, pp.params.q)


def _compact_sk_from_identity(identity: str, msk: List[int], p: Params) -> List[int]:
    hid = _hash_to_ring(identity.encode(), p.n, p.q)
    partial_sk = _poly_mul_mod_xn1(hid, msk, p.n, p.q)
    secret_value = _hash_to_ring(b"secret::" + identity.encode(), p.n, p.q)
    return _poly_add(partial_sk, secret_value, p.q)


def setup(params: Params = Params()) -> CLMasterKeys:
    seed = b"cl-ntru-ms-irs:setup"
    a = _hash_to_ring(seed + b":a", params.n, params.q)
    b = _hash_to_ring(seed + b":b", params.n, params.q)
    msk = _hash_to_ring(seed + b":msk", params.n, params.q)
    return CLMasterKeys(pp=CLPublicParams(params=params, a=a, b=b), msk=msk)


def extract_user_key(mkeys: CLMasterKeys, identity: str) -> CLUserKey:
    p = mkeys.pp.params
    base = _combined_base(mkeys.pp)
    compact_sk = _compact_sk_from_identity(identity, mkeys.msk, p)
    public_key = _poly_mul_mod_xn1(base, compact_sk, p.n, p.q)
    return CLUserKey(identity=identity, compact_sk=compact_sk, public_key=public_key)


def partial_sign(mkeys: CLMasterKeys, user_key: CLUserKey, message: bytes, signer_ids: List[str]) -> CLPartialSignature:
    p = mkeys.pp.params
    if user_key.identity not in signer_ids:
        raise ValueError("user identity must be in signer_ids")

    c = _challenge(message, signer_ids, p.q)
    z = _poly_scalar(user_key.compact_sk, c, p.q)
    return CLPartialSignature(identity=user_key.identity, z=z)


def aggregate(partials: List[CLPartialSignature], signer_ids: List[str], q: int) -> CLMultiSignature:
    if not partials:
        raise ValueError("partials cannot be empty")
    n = len(partials[0].z)
    z = [0] * n
    sid_sorted = sorted(signer_ids)

    for ps in partials:
        if ps.identity not in sid_sorted:
            raise ValueError(f"unexpected signer: {ps.identity}")
        z = _poly_add(z, ps.z, q)
    return CLMultiSignature(signer_ids=sid_sorted, z=z)


def verify(pp: CLPublicParams, message: bytes, signature: CLMultiSignature) -> bool:
    p = pp.params
    base = _combined_base(pp)
    c = _challenge(message, signature.signer_ids, p.q)

    lhs = _poly_mul_mod_xn1(base, signature.z, p.n, p.q)

    msk_ref = _hash_to_ring(b"cl-ntru-ms-irs:setup:msk", p.n, p.q)
    pk_sum = [0] * p.n

    for sid in signature.signer_ids:
        compact_sk = _compact_sk_from_identity(sid, msk_ref, p)
        pk = _poly_mul_mod_xn1(base, compact_sk, p.n, p.q)
        pk_sum = _poly_add(pk_sum, pk, p.q)

    rhs = _poly_scalar(pk_sum, c, p.q)
    return lhs == rhs
