from nacl.signing import VerifyKey


def verify_key(pk: str, body: bytes, signature: str, timestamp: str) -> bool:
    """
    Validate the following headers of an interaction request:
        - X-Signature-Ed25519
        - X-Signature-Timestamp

    https://discord.com/developers/docs/interactions/receiving-and-responding#security-and-authorization
    """

    key = VerifyKey(bytes.fromhex(pk))

    try:
        key.verify(f"{timestamp}{body}".encode(), bytes.fromhex(signature))
        return True
    except Exception as e:
        print(e)
    return False
