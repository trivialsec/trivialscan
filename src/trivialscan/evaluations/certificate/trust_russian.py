import logging
from typing import Union

from tlstrust import TrustStore, context, stores
from ...exceptions import EvaluationNotRelevant, NoLogEvaluation
from ...transport import TLSTransport
from ...certificate import BaseCertificate, RootCertificate
from .. import BaseEvaluationTask

logger = logging.getLogger(__name__)


class EvaluationTask(BaseEvaluationTask):
    def __init__(  # pylint: disable=useless-super-delegation
        self, transport: TLSTransport, metadata: dict, config: dict
    ) -> None:
        super().__init__(transport, metadata, config)

    def evaluate(self, certificate: BaseCertificate) -> Union[bool, None]:
        if not isinstance(certificate, RootCertificate):
            raise EvaluationNotRelevant
        if not certificate.subject_key_identifier:
            reason = f"Missing SKI RootCertificate {certificate.issuer_common_name}"
            logger.warning(reason)
            self.substitution_metadata["reason"] = reason
            raise NoLogEvaluation

        store = TrustStore(certificate.subject_key_identifier)
        self.substitution_metadata["root_store_name"] = context.MINTSIFRY_ROSSII
        self.substitution_metadata["store_version"] = stores.mintsifry_rossii.__version__
        self.substitution_metadata["store_description"] = stores.mintsifry_rossii.__description__
        self.substitution_metadata["short_name"] = context.SHORT_LOOKUP.get(context.MINTSIFRY_ROSSII, context.MINTSIFRY_ROSSII)
        try:
            self.substitution_metadata["exists_in_store"] = store.exists(context_type=context.SOURCE_RUSSIA)
            self.substitution_metadata["expired_in_store"] = store.expired_in_store(context_type=context.SOURCE_RUSSIA)
        except FileExistsError:
            self.substitution_metadata["exists_in_store"] = False
        return store.check_trust(
            context_type=context.SOURCE_RUSSIA
        )
