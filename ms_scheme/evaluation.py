from __future__ import annotations

import math
import statistics
import time
from dataclasses import dataclass
from typing import Callable, Iterable, List

from ms_scheme import cl_ntru_ms_irs, ibms_ntru
from ms_scheme.ibms_ntru import Params


@dataclass
class BenchmarkRecord:
    scheme: str
    n: int
    q: int
    signer_count: int
    rounds: int
    key_extract_ms_mean: float
    key_extract_ms_std: float
    partial_sign_ms_mean: float
    partial_sign_ms_std: float
    aggregate_ms_mean: float
    aggregate_ms_std: float
    verify_ms_mean: float
    verify_ms_std: float
    verify_success_rate: float
    signature_size_bytes: int


def _measure_ms(fn: Callable[[], None]) -> float:
    t0 = time.perf_counter()
    fn()
    return (time.perf_counter() - t0) * 1000.0


def signature_size_bytes(n: int, q: int, signer_ids: Iterable[str], poly_count: int) -> int:
    coeff_bytes = math.ceil(math.log2(q) / 8)
    poly_bytes = n * coeff_bytes
    ids_bytes = sum(len(s.encode("utf-8")) for s in signer_ids)
    return poly_count * poly_bytes + ids_bytes


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

        user_keys = []
        for sid in signer_ids:
            elapsed = _measure_ms(lambda s=sid: user_keys.append(extract_fn(mkeys, s)))
            key_extract_ms.append(elapsed)

        partials = []
        for uk in user_keys:
            elapsed = _measure_ms(lambda k=uk: partials.append(sign_fn(mkeys, k, message, signer_ids)))
            partial_sign_ms.append(elapsed)

        sig_holder = [None]
        aggregate_ms.append(_measure_ms(lambda: sig_holder.__setitem__(0, aggregate_fn(partials, signer_ids, q))))
        signature = sig_holder[0]

        verify_holder = [False]
        public_params = mkeys.mpk if hasattr(mkeys, "mpk") else mkeys.pp
        verify_ms.append(_measure_ms(lambda: verify_holder.__setitem__(0, verify_fn(public_params, message, signature))))
        verify_ok += 1 if verify_holder[0] else 0

    return BenchmarkRecord(
        scheme=scheme,
        n=n,
        q=q,
        signer_count=signer_count,
        rounds=rounds,
        key_extract_ms_mean=statistics.mean(key_extract_ms),
        key_extract_ms_std=statistics.pstdev(key_extract_ms),
        partial_sign_ms_mean=statistics.mean(partial_sign_ms),
        partial_sign_ms_std=statistics.pstdev(partial_sign_ms),
        aggregate_ms_mean=statistics.mean(aggregate_ms),
        aggregate_ms_std=statistics.pstdev(aggregate_ms),
        verify_ms_mean=statistics.mean(verify_ms),
        verify_ms_std=statistics.pstdev(verify_ms),
        verify_success_rate=verify_ok / rounds,
        signature_size_bytes=signature_size_bytes(n, q, signer_ids, poly_count=poly_count),
    )


def run_benchmark_ibms(n: int, q: int, signer_count: int, rounds: int = 30) -> BenchmarkRecord:
    return _run_generic_benchmark(
        scheme="IBMS-NTRU",
        n=n,
        q=q,
        signer_count=signer_count,
        rounds=rounds,
        poly_count=2,
        setup_fn=ibms_ntru.setup,
        extract_fn=ibms_ntru.extract_user_key,
        sign_fn=ibms_ntru.partial_sign,
        aggregate_fn=ibms_ntru.aggregate,
        verify_fn=ibms_ntru.verify,
    )


def run_benchmark_cl(n: int, q: int, signer_count: int, rounds: int = 30) -> BenchmarkRecord:
    return _run_generic_benchmark(
        scheme="CL-NTRU-MS-IRS",
        n=n,
        q=q,
        signer_count=signer_count,
        rounds=rounds,
        poly_count=4,
        setup_fn=cl_ntru_ms_irs.setup,
        extract_fn=cl_ntru_ms_irs.extract_user_key,
        sign_fn=cl_ntru_ms_irs.partial_sign,
        aggregate_fn=cl_ntru_ms_irs.aggregate,
        verify_fn=cl_ntru_ms_irs.verify,
    )
