# Contributing

## Releases

Follow SemVer:

- major releases are discussed with all maintainers and all deprecations in previous releases will be finalized
- minor releases should be backwards compatible so any deprecations must be indicated to end-users, and this may require a wrapper function for the deprecated function using the old name that holds the deprecation warning OR supporting both deprecated and new functionality using a flag for the new and default to the old
- patch releases must be completely backwards compatible, so only add functionality, do not delete anything. if a change is made consider minor release instead. Of course a patch may be used to restore broken functionality so ensure the broken version is yanked once patched

## Merge Checklist

- Version bump in `cli/__main__.py`
- Check dependencies; ensure all are latest (with compatibility to other dependencies as the only exception)
- All `make test` tests pass
- Update the README and `pyproject.toml` features lists

## Project non-goals

One main rule here, no rewriting logic that is provided via existing python packages in the ecosystem where possible, it is not hard to literally search the code Github and if it is compatible with the license, or better it is on PyPi, integrate it directly or fork it.

Currently we utilise:

- `pyOpenSSL` Python bindings for OpenSSL
- `certifi` is self-explanatory
- `cryptography` is a powerful tool that can be used for this purpose
- `certvalidator` was intended to be used for this exact purpose [but is limited](https://github.com/wbond/certvalidator/issues/36)

Less of a rule, just good advice. If the functionality you want to add is significantly large, complex, or niche - consider making it a separate library and then integrate it here. [tlstrust](https://pypi.org/project/tlstrust/) is an example where it was both large and complex enough to be best suited in it's own package but still fully integrated into this tool.

## What to contribute?

Anything you want, or one of these:

⌛⌛ Idea List ⌛⌛

- jarm fingerprint hash
- HSTS Preloading
- Handshake Simulations
- More impersonation detections
- More C2 (command and control) detections
- Known RSA/DSA private keys: https://www.hdm.io/tools/debian-openssl/
- Common DH primes and public server param (Ys) reuse - logjam
- Logjam: similar to the FREAK attack but except that Logjam attacks the 512-bit DH export key exchange instead of the RSA key exchange. disable support for all DHE_EXPORT cipher suites
- ECDH public server param (Ys) reuse - Racoon
- TLS extension intolerance
- TLS extensions
  - nameConstraints [oid 2.5.29.30](https://www.alvestrand.no/objectid/2.5.29.30.html) [rfc5280](https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.10) [ref1](https://netflixtechblog.com/bettertls-c9915cd255c0#8498) [ref2](https://docs.aws.amazon.com/acm-pca/latest/userguide/name_constraints.html)
  - OCSPNonce reuse
- Expected Issuer public key match (If the server is owned or operated by you, a Zero-trust requirement)
- if HPKP is still present and expected, validate per the policy
- Incorrect SNI alerts
- Scanner proxy support
- Scanner Authentication
  - proxy auth
  - custom authenticator (i.e. pass the request object to modify with bespoke signers, custom headers, query string params, etc.)
- Informational Outputs
  - deep link https://crt.sh/?sha1=
- POODLE; CBC Padding Oracle Vulnerability; SSLv3 or CBC (GOLDENDOODLE, Zombie POODLE, Sleeping POODLE, POODLE BITES, POODLE 2.0, CVE-2015-4458, CVE-2016-2107, and Invalid Mac 0-length record CVE-2019-1559)
- HEARTBLEED: CVE-2014-0160 OpenSSL Vulnerability allowing attackers to access random server memory that could potentially disclose any sensitive data the server is storing
- CCS Injection: CVE-2014-0224 TLS feature providing MitM attackers opertunity to leverage
- FREAK: weak export cipher suites, RSA of moduli of less than 512 bits, trivial to factor https://tools.keycdn.com/freak
- Logjam: similar to the FREAK attack but except that Logjam attacks the 512-bit DH export key exchange instead of the RSA key exchange. disable support for all DHE_EXPORT cipher suites
- LUCKY13
- SWEET32
- DROWN
- HEARTBLEED: Heartbeat extension RFC6520 is leveraged for HEARTBLEED vulnerability
- Ticketbleed
- CDN detection
- tls_long_handshake_intolerance
- Change-Cipher-Specs allowing the use of attacker preferred ciphers that are available and potentially offer an exploit path
- EMS: Extended Master Secret extension provides additional security to SSL sessions and prevents certain MitM attacks
- EC_POINT_FORMAT TLS extension, RFC 8422 5.1.2: uncompressed point format is obsolete so it is perfectly fine for a client to not include this extension, if included it must have exactly the value 0 (Uncompressed) Point Format for NIST Curves

### Cert validation levels:

1. common validation

```py
def common_validation(self, trust_context: int = SOURCE_CCADB) -> bool:
    return True
```

Most browsers (and software generally) check only:

- common name exists
- common name well formed
- hostname match common name or SAN
- leaf not expired
- root CA exists in trust stores

2. TLS as a whole is RFC ccompliant

```py
def rfc_ccompliant(self, trust_context: int = SOURCE_CCADB) -> bool:
```

Proper RFC defined MUST validations:

- common_validation
- intermediates common_validation
- root common_validation
- no revocations

3. best practices / hardening standards

```py
def hardened_tls(self, trust_context: int = SOURCE_CCADB) -> bool:
```

RFC defined SHOULD validations and heavily scruitinised, yet still valid, best practices:

- is_valid
- no deprecated protocols, signatures, or ciphers
- all certificates issued in past tense
- server not sending useless certificates
- CAA
- Not DV
- TLS1.3
- Only PFS
- HSTS
- SCSV
- Secure Renegotiation
- No known vulnerabilities

4. FIPS 140-2 (NIST SP800-131A transition mode)

```py
def fips_valid(self, trust_context: int = SOURCE_CCADB) -> bool:
```

5. NIST SP800-131A strict mode (superset of NIST SP800-52 R2)

```py
def nist_validation(
    self, transition_mode: bool = False, trust_context: int = SOURCE_CCADB
) -> bool:
```

6. PCI

```py
def pci_validation(self, trust_context: int = SOURCE_CCADB) -> bool:
```

- No known vulnerabilities
- All the certificates provided by the server are trusted
- No known weak ciphers, protocols, keys, signatures, elliptic curves

7. HIPAA/HITECH requires NIST SP800

```py
def hipaa_valid(self, trust_context: int = SOURCE_CCADB) -> bool:
```

- All the X509 certificates provided by the server are in version 3
- supports OCSP stapling
- No known weak ciphers, protocols, keys, signatures, elliptic curves
- Support Extended Master Secret (EMS) extension for TLS versions ≤1.2
- Supports the Uncompressed Point Format for NIST Curves, or; no EC_POINT_FORMAT TLS extension

# Local Development Environment

## Interpreter/s

1. Obtain an openssl version still supporting SSL; For the sake of documentation just what the [drwetter/testssl.sh](https://testssl.sh/openssl-1.0.2k-chacha.pm.ipv6.Linux+FreeBSD.201705.tar.gz) project distributes, you should compile it directly which is also what I prefer.

2. Install multiple versions of python from version 3.9 onwards; currently `3.9.13`, `3.10.6`, `3.11.0rc1`

```sh
wget https://www.python.org/ftp/python/3.9.13/Python-3.9.13.tgz
tar xzvf Python-3.9.13.tgz
cd Python-3.9.13
./configure --with-openssl=/usr/src/openssl-1.0.2o --enable-optimizations --with-ensurepip=install
make -j4
make altinstall
```

**Note**: you may first need to install; `libssl-dev` `openssl` `g++` and possibly more (every distro and distro version is different)

Check the openssl version:

```py
import ssl
ssl.OPENSSL_VERSION
```

3. Ensure each version has Pip and [venv](https://virtualenv.pypa.io/en/latest/cli_interface.html) modules;

- Use `python -m ensurepip --default-pip` (replace `python` with version specific binaries; i.e. `python3.9`) which will provide `pip` for each version
- Make sure it is the latest; `python -m pip install --disable-pip-version-check -U pip wheel virtualenv` (for each version)

4. Activating each version:

Create the virtual environments:

```sh
python3.9 -m venv .venv3.9
python3.10 -m venv .venv3.10
python3.11 -m venv .venv3.11
```

Activate one at a time as needed for testing:

```sh
deactivate
source .venv3.9/bin/activate
```
