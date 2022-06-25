from ...constants import DEPRECATED_OCSP_ALGO
from ...exceptions import EvaluationNotRelevant
from ...transport import Transport
from ...certificate import BaseCertificate, LeafCertificate
from .. import BaseEvaluationTask


class EvaluationTask(BaseEvaluationTask):
    def __init__(  # pylint: disable=useless-super-delegation
        self, transport: Transport, metadata: dict, config: dict
    ) -> None:
        super().__init__(transport, metadata, config)

    def evaluate(self, certificate: BaseCertificate) -> bool | None:
        if not isinstance(certificate, LeafCertificate):
            raise EvaluationNotRelevant
        if not certificate.revocation_ocsp_hash_algorithm:
            return None
        return (
            certificate.revocation_ocsp_hash_algorithm.upper() in DEPRECATED_OCSP_ALGO
        )
