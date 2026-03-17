from ms_scheme.ibms_ntru import aggregate, extract_user_key, partial_sign, setup, verify


def _gen_signature(message: bytes):
    mkeys = setup()
    signers = ["id:alice", "id:bob", "id:carol"]
    user_keys = [extract_user_key(mkeys, sid) for sid in signers]
    partials = [partial_sign(mkeys, uk, message, signers) for uk in user_keys]
    msig = aggregate(partials, signers, mkeys.mpk.params.q)
    return mkeys, msig, signers


def test_valid_multisignature():
    mkeys, msig, _ = _gen_signature(b"hello")
    assert verify(mkeys.mpk, b"hello", msig)


def test_message_tamper_fails():
    mkeys, msig, _ = _gen_signature(b"hello")
    assert not verify(mkeys.mpk, b"HELLO", msig)


def test_signer_set_tamper_fails():
    mkeys, msig, signers = _gen_signature(b"hello")
    msig.signer_ids = sorted(signers + ["id:eve"])
    assert not verify(mkeys.mpk, b"hello", msig)
