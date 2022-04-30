from dataclasses import dataclass, field

__module__ = "trivialscan.metadata"


@dataclass
class Metadata:
    host: str = field(default_factory=str)
    certificate_root_ca: bool = field(default_factory=bool)
    certificate_intermediate_ca: bool = field(default_factory=bool)
    certificate_private_key_pem: bytes = field(default_factory=bytes)
    certificate_public_key_type: str = field(default_factory=str)
    certificate_public_key_curve: str = field(default_factory=str)
    certificate_public_key_exponent: int = field(default_factory=int)
    certificate_public_key_size: int = field(default_factory=int)
    certificate_serial_number: str = field(default_factory=str)
    certificate_serial_number_decimal: int = field(default_factory=int)
    certificate_serial_number_hex: str = field(default_factory=str)
    certificate_version: int = field(default_factory=int)
    certificate_subject: str = field(default_factory=str)
    certificate_issuer: str = field(default_factory=str)
    certificate_issuer_country: str = field(default_factory=str)
    certificate_signature_algorithm: str = field(default_factory=str)
    certificate_sha256_fingerprint: str = field(default_factory=str)
    certificate_sha1_fingerprint: str = field(default_factory=str)
    certificate_md5_fingerprint: str = field(default_factory=str)
    certificate_spki_fingerprint: str = field(default_factory=str)
    certificate_not_before: str = field(default_factory=str)
    certificate_not_after: str = field(default_factory=str)
    certificate_expired: bool = field(default_factory=bool)
    certificate_common_name: str = field(default_factory=str)
    certificate_san: list = field(default_factory=list)
    certificate_subject_key_identifier: str = field(default_factory=str)
    certificate_authority_key_identifier: str = field(default_factory=str)
    certificate_extensions: list = field(default_factory=list)
    certificate_is_self_signed: bool = field(default_factory=bool)
    client_certificate_expected: bool = field(default_factory=bool)
    certificate_validation_type: str = field(default_factory=str)
    certificate_validation_oid: str = field(default_factory=str)
    certification_authority_authorization: bool = field(default_factory=bool)
    certificate_known_compromised: bool = field(default_factory=bool)
    certificate_key_compromised: bool = field(default_factory=bool)
    revocation_ocsp_stapling: bool = field(default_factory=bool)
    revocation_ocsp_must_staple: bool = field(default_factory=bool)
    revocation_ocsp_status: str = field(default_factory=str)
    revocation_ocsp_response: str = field(default_factory=str)
    revocation_ocsp_reason: str = field(default_factory=str)
    revocation_ocsp_time: str = field(default_factory=str)
    revocation_crlite: bool = field(default_factory=bool)
    sni_support: bool = field(default_factory=bool)
    negotiated_protocol: str = field(default_factory=str)
    offered_tls_versions: list = field(default_factory=list)
    negotiated_cipher: str = field(default_factory=str)
    negotiated_cipher_bits: int = field(default_factory=int)
    weak_cipher: bool = field(default_factory=bool)
    strong_cipher: bool = field(default_factory=bool)
    forward_anonymity: bool = field(default_factory=bool)
    offered_ciphers: list = field(default_factory=list)
    session_resumption_caching: bool = field(default_factory=bool)
    session_resumption_tickets: bool = field(default_factory=bool)
    session_resumption_ticket_hint: bool = field(default_factory=bool)
    client_renegotiation: bool = field(default_factory=bool)
    tlsa: bool = field(default_factory=bool)
    dnssec: bool = field(default_factory=bool)
    dnssec_algorithm: str = field(default_factory=str)
    scsv: bool = field(default_factory=bool)
    preferred_protocol: str = field(default_factory=str)
    compression_support: bool = field(default_factory=bool)
    tls_version_intolerance: bool = field(default_factory=bool)
    tls_version_intolerance_versions: list = field(default_factory=list)
    tls_version_interference: bool = field(default_factory=bool)
    tls_version_interference_versions: list = field(default_factory=list)
    tls_long_handshake_intolerance: bool = field(default_factory=bool)
    peer_address: str = field(default_factory=str)
    http_expect_ct_report_uri: bool = field(default_factory=bool)
    http_hsts: bool = field(default_factory=bool)
    http_xfo: bool = field(default_factory=bool)
    http_csp: bool = field(default_factory=bool)
    http_coep: bool = field(default_factory=bool)
    http_coop: bool = field(default_factory=bool)
    http_corp: bool = field(default_factory=bool)
    http_nosniff: bool = field(default_factory=bool)
    http_unsafe_referrer: bool = field(default_factory=bool)
    http_xss_protection: bool = field(default_factory=bool)
    http_status_code: int = field(default_factory=int)
    http1_support: bool = field(default_factory=bool)
    http1_1_support: bool = field(default_factory=bool)
    http2_support: bool = field(default_factory=bool)
    http2_cleartext_support: bool = field(default_factory=bool)
    port: int = 443
    possible_phish_or_malicious: bool = field(default_factory=bool)
    trust_ccadb: bool = field(default_factory=bool)
    trust_ccadb_status: str = field(default_factory=str)
    trust_java: bool = field(default_factory=bool)
    trust_java_status: str = field(default_factory=str)
    trust_android: bool = field(default_factory=bool)
    trust_android_status: str = field(default_factory=str)
    trust_linux: bool = field(default_factory=bool)
    trust_linux_status: str = field(default_factory=str)
    trust_russia: bool = field(default_factory=bool)
    trust_russia_status: str = field(default_factory=str)
    trust_rustls: bool = field(default_factory=bool)
    trust_rustls_status: str = field(default_factory=str)
    trust_certifi: bool = field(default_factory=bool)
    trust_certifi_status: str = field(default_factory=str)
    trust_go: bool = field(default_factory=bool)
    trust_go_status: str = field(default_factory=str)
    trust_ruby: bool = field(default_factory=bool)
    trust_ruby_status: str = field(default_factory=str)
    trust_node: bool = field(default_factory=bool)
    trust_node_status: str = field(default_factory=str)
    trust_erlang: bool = field(default_factory=bool)
    trust_erlang_status: str = field(default_factory=str)
