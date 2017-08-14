"""
Hashing utilities for account security.

The purpose of applying sha512 before bcrypt is to allow arbitrarily long
passwords without loss of entropy or DDoS vulnerability. See
https://blogs.dropbox.com/tech/2016/09/how-dropbox-securely-stores-your-passwords/
for more info.

TODO: Investigate using a pepper and hashing on separate machines than the
ones running the API. This would protect the pepper in case the API is
compromised, and allow hashing on machines suitable for a compute heavy
workload.
"""
from passlib.hash import bcrypt
from passlib.hash import hex_sha512

def hash_pw(pw):
    # type: (str) -> bytes
    """
    :param pw: The password to hash.
    :returns: The hashed password.
    """
    return bcrypt.using(rounds=13).hash(hex_sha512.hash(pw))

def verify_pw(hashed_pw, pw):
    # type (bytes, str) -> bool
    """
    :param: hashed_pw. The hashed password. 
    :param: pw. The password.

    >>> verify_pw(hash_pw('hunter2'), 'hunter2')
    True
    >>> verify_pw(hash_pw('hunter2'), 'hunter1')
    False
    >>> verify_pw(b'garbage', 'hunter1')
    False
    """
    try:
        return bcrypt.verify(hex_sha512.hash(pw), hashed_pw)
    except ValueError:
        return False