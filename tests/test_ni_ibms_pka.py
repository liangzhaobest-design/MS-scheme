from ms_scheme.ni_ibms_pka import (
    aggregate,
    aggregate_public_keys,
    extract_user_key,
    partial_sign,
    setup,
    verify,
)


def _gen_signature(message: bytes):
    mkeys = setup()
    signers = ["id:alice", "id:bob", "id:carol"]
    agg_pk = aggregate_public_keys(mkeys.pp, signers)
    user_keys = [extract_user_key(mkeys, sid) for sid in signers]
    partials = [partial_sign(mkeys, uk, message, signers, agg_pk) for uk in user_keys]
    msig = aggregate(partials, signers, agg_pk, mkeys.pp.params.q)
    return mkeys, msig


def test_valid_multisignature_ni() -> None:
    mkeys, msig = _gen_signature(b"hello")
    assert verify(mkeys.pp, b"hello", msig)


def test_message_tamper_fails_ni() -> None:
    mkeys, msig = _gen_signature(b"hello")
    assert not verify(mkeys.pp, b"HELLO", msig)
