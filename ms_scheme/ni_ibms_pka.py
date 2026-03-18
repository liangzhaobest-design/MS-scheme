from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Iterable, List

from ms_scheme.ibms_ntru import (
    Params,
    _hash_to_ring,
    _poly_add,
    _poly_mul_mod_xn1,
    _poly_scalar,
)


@dataclass
class NIPublicParams:
    params: Params
    a: List[int]


@dataclass
class NIMasterKeys:
    pp: NIPublicParams
    msk: List[int]


@dataclass
class NIUserKey:
    identity: str
    sk_id: List[int]
    sk_u: List[int]
    pk_u: List[int]


@dataclass
class NIPartialSignature:
    identity: str
    z1: List[int]
    z2: List[int]


@dataclass
class NIMultiSignature:
    signer_ids: List[str]
    agg_pk: List[int]
    z1: List[int]
    z2: List[int]


def _challenge(message: bytes, signer_ids: Iterable[str], agg_pk: List[int], q: int) -> int:
    ids_part = "|".join(sorted(signer_ids)).encode()
    pk_part = ",".join(map(str, agg_pk)).encode()
    digest = sha256(b"NI-IBMS-PKA::" + message + b"::" + ids_part + b"::" + pk_part).digest()
    return int.from_bytes(digest, "big") % q


def setup(params: Params = Params()) -> NIMasterKeys:
    seed = b"ni-ibms-pka:setup"
    a = _hash_to_ring(seed + b":a", params.n, params.q)
    msk = _hash_to_ring(seed + b":msk", params.n, params.q)
    return NIMasterKeys(pp=NIPublicParams(params=params, a=a), msk=msk)


def extract_user_key(mkeys: NIMasterKeys, identity: str) -> NIUserKey:
    p = mkeys.pp.params
    hid = _hash_to_ring(identity.encode(), p.n, p.q)
    sk_id = _poly_mul_mod_xn1(hid, mkeys.msk, p.n, p.q)
    sk_u = _hash_to_ring(b"user-secret::" + identity.encode(), p.n, p.q)
    pk_u = _poly_mul_mod_xn1(mkeys.pp.a, sk_u, p.n, p.q)
    return NIUserKey(identity=identity, sk_id=sk_id, sk_u=sk_u, pk_u=pk_u)


def aggregate_public_keys(pp: NIPublicParams, signer_ids: List[str]) -> List[int]:
    p = pp.params
    agg = [0] * p.n
    for sid in sorted(signer_ids):
        sk_u = _hash_to_ring(b"user-secret::" + sid.encode(), p.n, p.q)
        pk_u = _poly_mul_mod_xn1(pp.a, sk_u, p.n, p.q)
        agg = _poly_add(agg, pk_u, p.q)
    return agg


def partial_sign(
    mkeys: NIMasterKeys,
    user_key: NIUserKey,
    message: bytes,
    signer_ids: List[str],
    agg_pk: List[int],
) -> NIPartialSignature:
    p = mkeys.pp.params
    if user_key.identity not in signer_ids:
        raise ValueError("user identity must be in signer_ids")

    y = [0] * p.n

    c = _challenge(message, signer_ids, agg_pk, p.q)
    z1 = _poly_add(y, _poly_scalar(user_key.sk_id, c, p.q), p.q)
    z2 = _poly_add(y, _poly_scalar(user_key.sk_u, c, p.q), p.q)
    return NIPartialSignature(identity=user_key.identity, z1=z1, z2=z2)


def aggregate(partials: List[NIPartialSignature], signer_ids: List[str], agg_pk: List[int], q: int) -> NIMultiSignature:
    if not partials:
        raise ValueError("partials cannot be empty")
    n = len(partials[0].z1)
    z1, z2 = [0] * n, [0] * n
    sid_sorted = sorted(signer_ids)

    for ps in partials:
        if ps.identity not in sid_sorted:
            raise ValueError(f"unexpected signer: {ps.identity}")
        z1 = _poly_add(z1, ps.z1, q)
        z2 = _poly_add(z2, ps.z2, q)

    return NIMultiSignature(signer_ids=sid_sorted, agg_pk=agg_pk, z1=z1, z2=z2)


def verify(pp: NIPublicParams, message: bytes, signature: NIMultiSignature) -> bool:
    p = pp.params
    c = _challenge(message, signature.signer_ids, signature.agg_pk, p.q)

    lhs = _poly_add(
        _poly_mul_mod_xn1(pp.a, signature.z1, p.n, p.q),
        _poly_mul_mod_xn1(pp.a, signature.z2, p.n, p.q),
        p.q,
    )

    msk_ref = _hash_to_ring(b"ni-ibms-pka:setup:msk", p.n, p.q)
    sk_id_sum = [0] * p.n
    for sid in signature.signer_ids:
        hid = _hash_to_ring(sid.encode(), p.n, p.q)
        sk_id = _poly_mul_mod_xn1(hid, msk_ref, p.n, p.q)
        sk_id_sum = _poly_add(sk_id_sum, sk_id, p.q)

    rhs = _poly_add(
        _poly_scalar(_poly_mul_mod_xn1(pp.a, sk_id_sum, p.n, p.q), c, p.q),
        _poly_scalar(signature.agg_pk, c, p.q),
        p.q,
    )
    return lhs == rhs
