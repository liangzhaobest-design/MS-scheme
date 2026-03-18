from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from ms_scheme.ibms_ntru import aggregate, extract_user_key, partial_sign, setup, verify


def main() -> None:
    mkeys = setup()
    signers = ["alice@example.com", "bob@example.com", "carol@example.com"]
    msg = "Compare with my own design".encode()

    user_keys = [extract_user_key(mkeys, sid) for sid in signers]
    partials = [partial_sign(mkeys, uk, msg, signers) for uk in user_keys]
    msig = aggregate(partials, signers, mkeys.mpk.params.q)

    ok = verify(mkeys.mpk, msg, msig)
    print("verify:", ok)
    print("signature size elements:", len(msig.R) + len(msig.z))


if __name__ == "__main__":
    main()
