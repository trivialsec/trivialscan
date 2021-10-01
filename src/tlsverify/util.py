from dataclasses import dataclass
from binascii import hexlify
from datetime import datetime
from socket import socket, AF_INET, SOCK_STREAM
from cryptography import x509
from cryptography.x509 import Certificate, extensions
from OpenSSL.crypto import X509, X509Name, TYPE_RSA, TYPE_DSA, TYPE_DH, TYPE_EC
from OpenSSL import SSL
from certvalidator import CertificateValidator, ValidationContext
import certifi
import validators

__module__ = 'tlsverify.util'

X509_DATE_FMT = r'%Y%m%d%H%M%SZ'
WEAK_KEY_SIZE = {
    'RSA': 1024,
    'DSA': 2048,
    'EC': 160,
}
KNOWN_WEAK_KEYS = {
    'RSA': '2000: Factorization of a 512-bit RSA Modulus, essentially derive a private key knowing only the public key. Verified bt EFF in 2001. Later in 2009 factorization of up to 1024-bit keys',
    'DSA': '1999: HPL Laboratories demonstrated lattice attacks on DSA, a non-trivial example of the known message attack that is a total break and message forgery technique. 2010 Dimitrios Poulakis demonstrated a lattice reduction technique for single or multiple message forgery',
    'EC': '2010 Dimitrios Poulakis demonstrated a lattice reduction technique to attack ECDSA for single or multiple message forgery',
}
KNOWN_WEAK_SIGNATURE_ALGORITHMS = {
    'sha1WithRSAEncryption': 'Macquarie University Australia 2009: identified vulnerabilities to collision attacks, later in 2017 Marc Stevens demonstrated collision proofs',
    'md5WithRSAEncryption': 'Arjen Lenstra and Benne de Weger 2005: vulnerable to hash collision attacks',
    'md2WithRSAEncryption': 'Rogier, N. and Chauvaud, P. in 1995: vulnerable to collision, later preimage resistance, and second-preimage resistance attacks were demonstrated at BlackHat 2008 by Mark Twain',
}

@dataclass
class Metadata:
    host :str
    certificate_public_key_type :str = ''
    certificate_key_size :int = 0
    certificate_serial_number :str = ''
    certificate_subject :str = ''
    certificate_issuer :str = ''
    certificate_issuer_country :str = ''
    certificate_signature_algorithm :str = ''
    certificate_sha1_fingerprint :str = ''
    certificate_md5_fingerprint :str = ''
    certificate_not_before :str = ''
    certificate_not_after :str = ''
    certificate_common_name :str = ''
    certificate_san :list = []
    certificate_extensions :list = []
    certificate_is_self_signed : bool = False
    negotiated_cipher :str = ''
    negotiated_protocol :str = ''
    negotiated_protocol_version :str = ''
    revocation_ocsp_stapling :bool = False
    revocation_ocsp_must_staple :bool = False
    port :int = 443

def get_certificates(host :str, port :int = 443, cafiles :list = None) -> tuple[bytes,list,Metadata]:
    if cafiles is not None and not isinstance(cafiles, list):
        raise ValueError(f"provided an invalid type {type(cafiles)} for cafiles, expected list")
    if not isinstance(port, int):
        raise ValueError(f"provided an invalid type {type(port)} for port, expected int")
    if not validators.domain(host):
        raise ValueError(f"provided an invalid domain {host}")
    der = None
    certificate_chain = []
    metadata = Metadata(host=host, port=port)
    for method in [SSL.TLSv1_2_METHOD, SSL.TLSv1_1_METHOD, SSL.TLSv1_METHOD, SSL.SSLv23_METHOD]:
        certificate_chain = []
        context = SSL.Context(method=method)
        context.load_verify_locations(cafile=certifi.where())
        if isinstance(cafiles, list):
            for cafile in cafiles:
                context.load_verify_locations(cafile=cafile)
        sock = SSL.Connection(context=context, socket=socket(AF_INET, SOCK_STREAM))
        sock.settimeout(5)
        sock.set_tlsext_host_name(host.encode())
        try:
            sock.connect((host, port))
            der = sock.getpeercert(True)
            metadata.negotiated_cipher, metadata.negotiated_protocol, _ = sock.cipher()
            metadata.negotiated_protocol = sock.version() or metadata.negotiated_protocol
            sock.setblocking(1)
            sock.do_handshake()
            for (_, cert) in enumerate(sock.get_peer_cert_chain()):
                certificate_chain.append(cert)
            sock.shutdown()
            sock.close()
            break
        except Exception as ex:
            sock.shutdown()
            sock.close()
            raise ex

    return der, certificate_chain, metadata

def extract_metadata(cert :X509, metadata :Metadata = None) -> Metadata:
    if metadata is None or not isinstance(metadata, Metadata):
        metadata = Metadata()
    public_key = cert.get_pubkey()
    if public_key.type() == TYPE_RSA:
        metadata.certificate_public_key_type = 'RSA'
    if public_key.type() == TYPE_DSA:
        metadata.certificate_public_key_type = 'DSA'
    if public_key.type() == TYPE_DH:
        metadata.certificate_public_key_type = 'DH'
    if public_key.type() == TYPE_EC:
        metadata.certificate_public_key_type = 'EC'
    metadata.certificate_key_size = public_key.bits()
    metadata.certificate_serial_number = str(cert.get_serial_number())
    subject = cert.get_subject()
    metadata.certificate_subject = "".join("/{0:s}={1:s}".format(name.decode(), value.decode()) for name, value in subject.get_components())
    issuer: X509Name = cert.get_issuer()
    metadata.certificate_issuer = issuer.commonName
    metadata.certificate_issuer_country = issuer.countryName
    metadata.certificate_signature_algorithm = cert.get_signature_algorithm().decode('ascii')
    metadata.certificate_sha1_fingerprint = cert.digest('sha1').decode('ascii')
    metadata.certificate_md5_fingerprint = cert.digest('md5').decode('ascii')
    metadata.certificate_san = cert.to_cryptography().extensions.get_extension_for_class(x509.SubjectAlternativeName).value.get_values_for_type(x509.DNSName)
    not_before = datetime.strptime(cert.get_notBefore().decode('ascii'), X509_DATE_FMT)
    not_after = datetime.strptime(cert.get_notAfter().decode('ascii'), X509_DATE_FMT)
    metadata.certificate_not_before = not_before.isoformat()
    metadata.certificate_not_after = not_after.isoformat()
    metadata.certificate_common_name = extract_certificate_common_name(cert.to_cryptography())
    for ext in metadata.certificate_extensions:
        if ext['name'] == 'TLSFeature' and 'rfc6066' in ext['features']:
            metadata.revocation_ocsp_stapling = True
            metadata.revocation_ocsp_must_staple = True

    return metadata

def gather_key_usages(cert :Certificate) -> tuple[list, list, list]:
    certificate_extensions = []
    validator_key_usage = []
    validator_extended_key_usage = []
    for ext in cert.extensions:
        data = {
            'critical': ext.critical,
            'name': ext.oid._name # pylint: disable=protected-access
        }
        if isinstance(ext.value, extensions.UnrecognizedExtension):
            continue
        if isinstance(ext.value, extensions.CRLNumber):
            data['crl_number'] = ext.value.crl_number
        if isinstance(ext.value, extensions.AuthorityKeyIdentifier):
            data['key_identifier'] = hexlify(ext.value.key_identifier).decode('utf-8')
            data['authority_cert_issuer'] = ', '.join([x.value for x in ext.value.authority_cert_issuer or []])
            data['authority_cert_serial_number'] = ext.value.authority_cert_serial_number
        if isinstance(ext.value, extensions.SubjectKeyIdentifier):
            data['digest'] = hexlify(ext.value.digest).decode('utf-8')
        if isinstance(ext.value, (extensions.AuthorityInformationAccess, extensions.SubjectInformationAccess)):
            data['descriptions'] = []
            for description in ext.value:
                data['descriptions'].append({
                    'access_location': description.access_location.value,
                    'access_method': description.access_method._name, # pylint: disable=protected-access
                })
        if isinstance(ext.value, extensions.BasicConstraints):
            data['ca'] = ext.value.ca
            data['path_length'] = ext.value.path_length
        if isinstance(ext.value, extensions.DeltaCRLIndicator):
            data['crl_number'] = ext.value.crl_number
        if isinstance(ext.value, (extensions.CRLDistributionPoints, extensions.FreshestCRL)):
            data['distribution_points'] = []
            for distribution_point in ext.value:
                data['distribution_points'].append({
                    'full_name': ', '.join([x.value for x in distribution_point.full_name or []]),
                    'relative_name': distribution_point.relative_name,
                    'reasons': distribution_point.reasons,
                    'crl_issuer': ', '.join([x.value for x in distribution_point.crl_issuer or []]),
                })
        if isinstance(ext.value, extensions.PolicyConstraints):
            data['policy_information'] = []
            data['user_notices'] = []
            for info in ext.value:
                if hasattr(info, 'require_explicit_policy'):
                    data['policy_information'].append({
                        'require_explicit_policy': info.require_explicit_policy,
                        'inhibit_policy_mapping': info.inhibit_policy_mapping,
                    })
                if hasattr(info, 'notice_reference'):
                    data['user_notices'].append({
                        'organization': info.notice_reference.organization,
                        'notice_numbers': info.notice_reference.notice_numbers,
                        'explicit_text': info.explicit_text,
                    })
        if isinstance(ext.value, extensions.ExtendedKeyUsage):
            data['key_usages'] = [x._name for x in ext.value or []] # pylint: disable=protected-access
            if 'serverAuth' in data['key_usages']:
                validator_extended_key_usage.append('server_auth')
        if isinstance(ext.value, extensions.TLSFeature):
            data['features'] = []
            for feature in ext.value:
                if feature.value == 5:
                    data['features'].append('OCSP Must-Staple (rfc6066)')
                    validator_extended_key_usage.append('ocsp_signing')
                if feature.value == 17:
                    data['features'].append('multiple OCSP responses (rfc6961)')
                    validator_extended_key_usage.append('ocsp_signing')
        if isinstance(ext.value, extensions.InhibitAnyPolicy):
            data['skip_certs'] = ext.value.skip_certs
        if isinstance(ext.value, extensions.KeyUsage):
            data['digital_signature'] = ext.value.digital_signature
            if ext.value.digital_signature:
                validator_key_usage.append('digital_signature')
            data['content_commitment'] = ext.value.content_commitment
            if ext.value.content_commitment:
                validator_key_usage.append('content_commitment')
            data['key_encipherment'] = ext.value.key_encipherment
            if ext.value.key_encipherment:
                validator_key_usage.append('key_encipherment')
            data['data_encipherment'] = ext.value.data_encipherment
            if ext.value.data_encipherment:
                validator_key_usage.append('data_encipherment')
            data['key_agreement'] = ext.value.key_agreement
            if ext.value.key_agreement:
                validator_key_usage.append('key_agreement')
                data['decipher_only'] = ext.value.decipher_only
                if ext.value.decipher_only:
                    validator_key_usage.append('decipher_only')
                data['encipher_only'] = ext.value.encipher_only
                if ext.value.encipher_only:
                    validator_key_usage.append('encipher_only')
            data['key_cert_sign'] = ext.value.key_cert_sign
            if ext.value.key_cert_sign:
                validator_key_usage.append('key_cert_sign')
            data['crl_sign'] = ext.value.crl_sign
            if ext.value.crl_sign:
                validator_key_usage.append('crl_sign')
        if isinstance(ext.value, extensions.NameConstraints):
            data['permitted_subtrees'] = [x.value for x in ext.value.permitted_subtrees or []]
            data['excluded_subtrees'] = [x.value for x in ext.value.excluded_subtrees or []]
        if isinstance(ext.value, extensions.SubjectAlternativeName):
            data['subject_alternative_names'] = [x.value for x in ext.value or []]
        if isinstance(ext.value, extensions.IssuerAlternativeName):
            data['issuer_alternative_names'] = [x.value for x in ext.value or []]
        if isinstance(ext.value, extensions.CertificateIssuer):
            data['certificate_issuers'] = [x.value for x in ext.value or []]
        if isinstance(ext.value, extensions.CRLReason):
            data['reason'] = ext.value.reason
        if isinstance(ext.value, extensions.InvalidityDate):
            data['invalidity_date'] = ext.value.invalidity_date
        if isinstance(ext.value, (extensions.PrecertificateSignedCertificateTimestamps, extensions.SignedCertificateTimestamps)):
            data['signed_certificate_timestamps'] = []
            for signed_cert_timestamp in ext.value:
                data['signed_certificate_timestamps'].append({
                    'version': signed_cert_timestamp.version.name,
                    'log_id': hexlify(signed_cert_timestamp.log_id).decode('utf-8'),
                    'timestamp': signed_cert_timestamp.timestamp,
                    'pre_certificate': signed_cert_timestamp.entry_type.value == 1,
                })
        if isinstance(ext.value, extensions.OCSPNonce):
            data['nonce'] = ext.value.nonce
        if isinstance(ext.value, extensions.IssuingDistributionPoint):
            data['full_name'] = ext.value.full_name
            data['relative_name'] = ext.value.relative_name
            data['only_contains_user_certs'] = ext.value.only_contains_user_certs
            data['only_contains_ca_certs'] = ext.value.only_contains_ca_certs
            data['only_some_reasons'] = ext.value.only_some_reasons
            data['indirect_crl'] = ext.value.indirect_crl
            data['only_contains_attribute_certs'] = ext.value.only_contains_attribute_certs
        certificate_extensions.append(data)
    return certificate_extensions, validator_key_usage, validator_extended_key_usage

def extract_certificate_common_name(cert :Certificate):
    for fields in cert.subject:
        current = str(fields.oid)
        if "commonName" in current:
            return fields.value
    return None

def match_hostname(host :str, cert :Certificate) -> bool:
    if not validators.domain(host):
        raise ValueError(f"provided an invalid domain {host}")
    if not isinstance(cert, Certificate):
        raise ValueError("invalid Certificate provided")
    wildcard_hosts = set()
    domains = set()
    for fields in cert.subject:
        current = str(fields.oid)
        if "commonName" in current:
            certificate_common_name = fields.value
            if certificate_common_name.startswith('*.'):
                wildcard_hosts.add(certificate_common_name)
            else:
                domains.add(certificate_common_name)
    certificate_san = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value.get_values_for_type(x509.DNSName)
    for san in certificate_san:
        if san.startswith('*.'):
            wildcard_hosts.add(san)
        else:
            domains.add(san)
    matched_wildcard = False
    for wildcard in wildcard_hosts:
        check = wildcard.replace('*', '')
        if host.endswith(check):
            matched_wildcard = True
            break

    return certificate_common_name is not None and (matched_wildcard is True or host in domains)

def validate_certificate_chain(der :bytes, pem_certificate_chain :list, validator_key_usage :list, validator_extended_key_usage :list):
    # TODO perhaps remove certvalidator, consider once merged: https://github.com/pyca/cryptography/issues/2381
    ctx = ValidationContext(allow_fetching=True, revocation_mode='hard-fail', weak_hash_algos=set(["md2", "md5", "sha1"]))
    validator = CertificateValidator(der, validation_context=ctx, intermediate_certs=pem_certificate_chain)
    validator.validate_usage(
        key_usage=set(validator_key_usage),
        extended_key_usage=set(validator_extended_key_usage),
    )