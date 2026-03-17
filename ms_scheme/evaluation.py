from __future__ import annotations

import math
import statistics
import time
from dataclasses import dataclass
from typing import Iterable, List

from ms_scheme.ibms_ntru import (
    Params,
    aggregate,
    extract_user_key,
    partial_sign,
    setup,
    verify,
)


@dataclass
class BenchmarkRecord:
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


def _measure_ms(fn) -> float:
    t0 = time.perf_counter()
    fn()
    return (time.perf_counter() - t0) * 1000.0


def signature_size_bytes(n: int, q: int, signer_ids: Iterable[str]) -> int:
    coeff_bytes = math.ceil(math.log2(q) / 8)
    poly_bytes = n * coeff_bytes
    ids_bytes = sum(len(s.encode("utf-8")) for s in signer_ids)
    # signature includes R and z plus signer id list
    return 2 * poly_bytes + ids_bytes


def run_benchmark(n: int, q: int, signer_count: int, rounds: int = 30) -> BenchmarkRecord:
    params = Params(n=n, q=q)
    signer_ids = [f"user-{i:02d}@example.com" for i in range(signer_count)]

    key_extract_ms: List[float] = []
    partial_sign_ms: List[float] = []
    aggregate_ms: List[float] = []
    verify_ms: List[float] = []
    verify_ok = 0

    for r in range(rounds):
        mkeys = setup(params)
        message = f"benchmark-message-round-{r}".encode()

        user_keys = []
        for sid in signer_ids:
            elapsed = _measure_ms(lambda s=sid: user_keys.append(extract_user_key(mkeys, s)))
            key_extract_ms.append(elapsed)

        partials = []
        for uk in user_keys:
            elapsed = _measure_ms(lambda k=uk: partials.append(partial_sign(mkeys, k, message, signer_ids)))
            partial_sign_ms.append(elapsed)

        msig_holder = [None]
        aggregate_ms.append(_measure_ms(lambda: msig_holder.__setitem__(0, aggregate(partials, signer_ids, q))))
        msig = msig_holder[0]

        verify_result_holder = [False]
        verify_ms.append(_measure_ms(lambda: verify_result_holder.__setitem__(0, verify(mkeys.mpk, message, msig))))
        verify_ok += 1 if verify_result_holder[0] else 0

    return BenchmarkRecord(
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
        signature_size_bytes=signature_size_bytes(n, q, signer_ids),
    )
