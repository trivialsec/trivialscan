from dataclasses import dataclass, field

__module__ = 'tlsverify.metadata'

@dataclass
class Metadata:
    host :str = field(default_factory=str)
    certificate_root_ca :bool = field(default_factory=bool)
    certificate_intermediate_ca :bool = field(default_factory=bool)
    certificate_private_key_pem :bytes = field(default_factory=bytes)
    certificate_public_key_type :str = field(default_factory=str)
    certificate_key_size :int = field(default_factory=int)
    certificate_serial_number :str = field(default_factory=str)
    certificate_serial_number_decimal :int = field(default_factory=int)
    certificate_serial_number_hex :str = field(default_factory=str)
    certificate_subject :str = field(default_factory=str)
    certificate_issuer :str = field(default_factory=str)
    certificate_issuer_country :str = field(default_factory=str)
    certificate_signature_algorithm :str = field(default_factory=str)
    certificate_pin_sha256 :str = field(default_factory=str)
    certificate_sha256_fingerprint :str = field(default_factory=str)
    certificate_sha1_fingerprint :str = field(default_factory=str)
    certificate_md5_fingerprint :str = field(default_factory=str)
    certificate_not_before :str = field(default_factory=str)
    certificate_not_after :str = field(default_factory=str)
    certificate_common_name :str = field(default_factory=str)
    certificate_san :list = field(default_factory=list)
    certificate_subject_key_identifier :str = field(default_factory=str)
    certificate_authority_key_identifier :str = field(default_factory=str)
    certificate_extensions :list = field(default_factory=list)
    certificate_is_self_signed :bool = field(default_factory=bool)
    certificate_client_authentication :bool = field(default_factory=bool)
    certificate_valid_tls_usage :bool = field(default_factory=bool)
    client_certificate_expected :bool = field(default_factory=bool)
    certificate_validation_type :str = field(default_factory=str) # None, DNS, Extended, Organisation
    certification_authority_authorization :bool = field(default_factory=bool)
    revocation_ocsp_stapling :bool = field(default_factory=bool)
    revocation_ocsp_must_staple :bool = field(default_factory=bool)
    revocation_ocsp_status :str = field(default_factory=str)
    revocation_ocsp_response :str = field(default_factory=str)
    revocation_ocsp_reason :str = field(default_factory=str)
    revocation_ocsp_time :str = field(default_factory=str)
    sni_support :bool = field(default_factory=bool)
    negotiated_protocol :str = field(default_factory=str)
    negotiated_cipher :str = field(default_factory=str)
    weak_cipher :bool = field(default_factory=bool)
    strong_cipher :bool = field(default_factory=bool)
    forward_anonymity :bool = field(default_factory=bool)
    offered_ciphers :list = field(default_factory=list)
    session_resumption_caching :bool = field(default_factory=bool)
    session_resumption_tickets :bool = field(default_factory=bool)
    session_resumption_ticket_hint :bool = field(default_factory=bool)
    client_renegotiation :bool = field(default_factory=bool)
    dnssec :bool = field(default_factory=bool)
    scsv_support :bool = field(default_factory=bool)
    compression_support :bool = field(default_factory=bool)
    peer_address :str = field(default_factory=str)
    http_expect_ct_report_uri :bool = field(default_factory=bool)
    http_hsts :bool = field(default_factory=bool)
    http_xfo :bool = field(default_factory=bool)
    http_csp :bool = field(default_factory=bool)
    http_coep :bool = field(default_factory=bool)
    http_coop :bool = field(default_factory=bool)
    http_corp :bool = field(default_factory=bool)
    http_nosniff :bool = field(default_factory=bool)
    http_unsafe_referrer :bool = field(default_factory=bool)
    http_xss_protection :bool = field(default_factory=bool)
    http_status_code :int = field(default_factory=int)
    http1_support :bool = field(default_factory=bool)
    http1_1_support :bool = field(default_factory=bool)
    http2_support :bool = field(default_factory=bool)
    http2_cleartext_support :bool = field(default_factory=bool)
    port :int = 443
