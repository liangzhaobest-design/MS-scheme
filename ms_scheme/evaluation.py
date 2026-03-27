from __future__ import annotations

import math
import statistics
import time
from dataclasses import dataclass
from typing import Callable, Iterable, List

from ms_scheme import cl_ntru_ms_irs, clsas_ntru, ibms_ntru, ni_ibms_pka
from ms_scheme.ibms_ntru import Params


@dataclass
class BenchmarkRecord:
    scheme: str
    n: int
    q: int
    signer_count: int
    rounds: int
    key_extract_ms_mean: float
    partial_sign_ms_mean: float
    aggregate_ms_mean: float
    verify_ms_mean: float
    verify_success_rate: float
    signature_size_bytes: int
    revoke_update_ms_mean: float
    revoke_check_ms_mean: float


def _measure_ms(fn: Callable[[], None]) -> float:
    t0 = time.perf_counter()
    fn()
    return (time.perf_counter() - t0) * 1000.0


def signature_size_bytes(n: int, q: int, signer_ids: Iterable[str], poly_count: int) -> int:
    coeff_bytes = math.ceil(math.log2(q) / 8)
    poly_bytes = n * coeff_bytes
    ids_bytes = sum(len(s.encode("utf-8")) for s in signer_ids)
    return poly_count * poly_bytes + ids_bytes


def _revocation_benchmark(scheme: str, signer_ids: list[str], rounds: int) -> tuple[float, float]:
    update_costs: list[float] = []
    check_costs: list[float] = []

    for r in range(rounds):
        revoked = signer_ids[r % len(signer_ids)]
        if scheme == "CLSAS-NTRU":
            # compressed revocation structure (set-like)
            status = {sid: False for sid in signer_ids}

            update_costs.append(_measure_ms(lambda: status.__setitem__(revoked, True)))
            check_costs.append(_measure_ms(lambda: all(not status[sid] for sid in signer_ids)))
        else:
            # classic CRL list style
            crl: list[str] = []

            update_costs.append(_measure_ms(lambda: crl.append(revoked)))
            check_costs.append(_measure_ms(lambda: all(sid not in crl for sid in signer_ids)))

    return statistics.mean(update_costs), statistics.mean(check_costs)


def _run_generic_benchmark(
    scheme: str,
    n: int,
    q: int,
    signer_count: int,
    rounds: int,
    poly_count: int,
    setup_fn,
    extract_fn,
    sign_fn,
    aggregate_fn,
    verify_fn,
    prepare_fn,
) -> BenchmarkRecord:
    params = Params(n=n, q=q)
    signer_ids = [f"user-{i:02d}@example.com" for i in range(signer_count)]

    key_extract_ms: List[float] = []
    partial_sign_ms: List[float] = []
    aggregate_ms: List[float] = []
    verify_ms: List[float] = []
    verify_ok = 0

    for r in range(rounds):
        mkeys = setup_fn(params)
        message = f"benchmark-message-round-{r}".encode()
        extra = prepare_fn(mkeys, signer_ids)

        user_keys = []
        for sid in signer_ids:
            key_extract_ms.append(_measure_ms(lambda s=sid: user_keys.append(extract_fn(mkeys, s))))

        partials = []
        for uk in user_keys:
            partial_sign_ms.append(_measure_ms(lambda k=uk: partials.append(sign_fn(mkeys, k, message, signer_ids, extra))))

        sig_holder = [None]
        aggregate_ms.append(_measure_ms(lambda: sig_holder.__setitem__(0, aggregate_fn(partials, signer_ids, extra, q))))

        verify_holder = [False]
        public_params = mkeys.mpk if hasattr(mkeys, "mpk") else mkeys.pp
        verify_ms.append(_measure_ms(lambda: verify_holder.__setitem__(0, verify_fn(public_params, message, sig_holder[0]))))
        verify_ok += 1 if verify_holder[0] else 0

    revoke_update, revoke_check = _revocation_benchmark(scheme, signer_ids, rounds)

    return BenchmarkRecord(
        scheme=scheme,
        n=n,
        q=q,
        signer_count=signer_count,
        rounds=rounds,
        key_extract_ms_mean=statistics.mean(key_extract_ms),
        partial_sign_ms_mean=statistics.mean(partial_sign_ms),
        aggregate_ms_mean=statistics.mean(aggregate_ms),
        verify_ms_mean=statistics.mean(verify_ms),
        verify_success_rate=verify_ok / rounds,
        signature_size_bytes=signature_size_bytes(n, q, signer_ids, poly_count=poly_count),
        revoke_update_ms_mean=revoke_update,
        revoke_check_ms_mean=revoke_check,
    )


def run_benchmark_ibms(n: int, q: int, signer_count: int, rounds: int = 30) -> BenchmarkRecord:
    return _run_generic_benchmark(
        "IBMS-NTRU", n, q, signer_count, rounds, 2,
        ibms_ntru.setup,
        ibms_ntru.extract_user_key,
        lambda m, u, msg, sids, _: ibms_ntru.partial_sign(m, u, msg, sids),
        lambda ps, sids, _, qv: ibms_ntru.aggregate(ps, sids, qv),
        ibms_ntru.verify,
        lambda _m, _s: None,
    )


def run_benchmark_cl(n: int, q: int, signer_count: int, rounds: int = 30) -> BenchmarkRecord:
    return _run_generic_benchmark(
        "CL-NTRU-MS-IRS", n, q, signer_count, rounds, 1,
        cl_ntru_ms_irs.setup,
        cl_ntru_ms_irs.extract_user_key,
        lambda m, u, msg, sids, _: cl_ntru_ms_irs.partial_sign(m, u, msg, sids),
        lambda ps, sids, _, qv: cl_ntru_ms_irs.aggregate(ps, sids, qv),
        cl_ntru_ms_irs.verify,
        lambda _m, _s: None,
    )


def run_benchmark_ni(n: int, q: int, signer_count: int, rounds: int = 30) -> BenchmarkRecord:
    return _run_generic_benchmark(
        "NI-IBMS-PKA", n, q, signer_count, rounds, 3,
        ni_ibms_pka.setup,
        ni_ibms_pka.extract_user_key,
        lambda m, u, msg, sids, agg_pk: ni_ibms_pka.partial_sign(m, u, msg, sids, agg_pk),
        lambda ps, sids, agg_pk, qv: ni_ibms_pka.aggregate(ps, sids, agg_pk, qv),
        ni_ibms_pka.verify,
        lambda m, s: ni_ibms_pka.aggregate_public_keys(m.pp, s),
    )


def run_benchmark_csas(n: int, q: int, signer_count: int, rounds: int = 30) -> BenchmarkRecord:
    params = Params(n=n, q=q)
    signer_ids = [f"user-{i:02d}@example.com" for i in range(signer_count)]
    key_extract_ms: list[float] = []
    partial_sign_ms: list[float] = []
    verify_ms: list[float] = []
    verify_ok = 0

    for r in range(rounds):
        mkeys = clsas_ntru.setup(params)
        message = f"benchmark-message-round-{r}".encode()

        user_keys = []
        for sid in signer_ids:
            key_extract_ms.append(_measure_ms(lambda s=sid: user_keys.append(clsas_ntru.extract_user_key(mkeys, s))))

        sig = clsas_ntru.init_signature(params.n)
        for uk in user_keys:
            holder = [sig]
            partial_sign_ms.append(_measure_ms(lambda k=uk: holder.__setitem__(0, clsas_ntru.sign_step(mkeys, k, message, holder[0]))))
            sig = holder[0]

        verify_holder = [False]
        verify_ms.append(_measure_ms(lambda: verify_holder.__setitem__(0, clsas_ntru.verify(mkeys.pp, message, sig))))
        verify_ok += 1 if verify_holder[0] else 0

    revoke_update, revoke_check = _revocation_benchmark("CLSAS-NTRU", signer_ids, rounds)

    return BenchmarkRecord(
        scheme="CLSAS-NTRU",
        n=n,
        q=q,
        signer_count=signer_count,
        rounds=rounds,
        key_extract_ms_mean=statistics.mean(key_extract_ms),
        partial_sign_ms_mean=statistics.mean(partial_sign_ms),
        aggregate_ms_mean=0.0,
        verify_ms_mean=statistics.mean(verify_ms),
        verify_success_rate=verify_ok / rounds,
        signature_size_bytes=signature_size_bytes(n, q, signer_ids, poly_count=1),
        revoke_update_ms_mean=revoke_update,
        revoke_check_ms_mean=revoke_check,
    )
