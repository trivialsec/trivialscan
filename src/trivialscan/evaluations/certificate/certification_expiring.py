from typing import Union
from datetime import datetime, timedelta
from ...transport import TLSTransport
from ...certificate import BaseCertificate
from .. import BaseEvaluationTask


class EvaluationTask(BaseEvaluationTask):
    def __init__(  # pylint: disable=useless-super-delegation
        self, transport: TLSTransport, metadata: dict, config: dict
    ) -> None:
        super().__init__(transport, metadata, config)

    def evaluate(self, certificate: BaseCertificate) -> Union[bool, None]:
        self.substitution_metadata["expiry_status"] = certificate.expiry_status
        risk = datetime.utcnow() + timedelta(days=3)
        return datetime.fromisoformat(certificate.not_after) < risk
