from ...exceptions import EvaluationNotRelevant
from ...transport import TLSTransport
from .. import BaseEvaluationTask


class EvaluationTask(BaseEvaluationTask):
    def __init__(  # pylint: disable=useless-super-delegation
        self, transport: TLSTransport, metadata: dict, config: dict
    ) -> None:
        super().__init__(transport, metadata, config)

    def evaluate(self) -> bool:
        if (
            self.transport.store.tls_state.certificate_mtls_expected
            or len(self.transport.expected_client_subjects) > 0
        ):
            return True
        raise EvaluationNotRelevant
