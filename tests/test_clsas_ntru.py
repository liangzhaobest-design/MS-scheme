from ms_scheme.clsas_ntru import extract_user_key, init_signature, setup, sign_step, verify


def _gen_signature(message: bytes):
    mkeys = setup()
    signers = ["id:alice", "id:bob", "id:carol"]
    uks = [extract_user_key(mkeys, sid) for sid in signers]
    sig = init_signature(mkeys.pp.params.n)
    for uk in uks:
        sig = sign_step(mkeys, uk, message, sig)
    return mkeys, sig


def test_clsas_valid() -> None:
    mkeys, sig = _gen_signature(b"hello")
    assert verify(mkeys.pp, b"hello", sig)


def test_clsas_tamper_message() -> None:
    mkeys, sig = _gen_signature(b"hello")
    assert not verify(mkeys.pp, b"HELLO", sig)
