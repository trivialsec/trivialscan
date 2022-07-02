from ...constants import SCT_GOOD, SCT_INSUFFICIENT, SCT_PRESENT
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
        self.substitution_metadata[
            "certificate_transparency_status"
        ] = certificate.transparency
        return certificate.transparency in [SCT_GOOD, SCT_INSUFFICIENT, SCT_PRESENT]
