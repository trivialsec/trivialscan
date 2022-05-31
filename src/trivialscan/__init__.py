import sys
from importlib import import_module
from rich.console import Console
from rich.table import Table
from .config import default_config
from .transport.insecure import InsecureTransport
from .transport.state import TransportState
from .evaluations import BaseEvaluationTask

__module__ = "trivialscan"

assert sys.version_info >= (3, 10), "Requires Python 3.10 or newer"
config = default_config()


def evaluate(
    hostname: str,
    port: int = 443,
    evaluations: list = config.get("evaluations"),
    skip_evaluations: list = [],
    skip_evaluation_groups: list = [],
    use_sni: bool = config["defaults"].get("use_sni"),
    cafiles: str = config["defaults"].get("cafiles"),
    client_certificate: str = None,
    console: Console = None,
    **kwargs,
) -> tuple[TransportState, list[dict]]:
    use_console = isinstance(console, Console)
    transport = InsecureTransport(hostname, port)
    if isinstance(client_certificate, str):
        transport.pre_client_authentication_check(client_pem_path=client_certificate)
    transport.connect_insecure(cafiles=cafiles, use_sni=use_sni)
    state = transport.get_state()
    evaluation_results = []
    for evaluation in evaluations:
        if any(
            [
                evaluation["group"] in skip_evaluation_groups,
                evaluation["key"] in skip_evaluations,
            ]
        ):
            continue
        _cls = getattr(
            import_module(
                f'.evaluations.{evaluation["group"]}.{evaluation["key"]}',
                package="trivialscan",
            ),
            "EvaluationTask",
        )
        cls: BaseEvaluationTask = _cls(transport, state, evaluation, config["defaults"])
        result = cls.evaluate()
        label_as = evaluation["label_as"]
        evaluation_value = "[cyan]SKIP![/cyan]"
        result_label = "Unknown"
        score = 0
        for anotatation in evaluation.get("anotate_results", []):
            if anotatation["value"] is result:
                evaluation_value = anotatation["evaluation_value"]
                result_label = anotatation["display_as"]
                score = anotatation["score"]
                break

        substitutions = {}
        for substitution in evaluation.get("substitutions", []):
            value = None
            if hasattr(state, substitution):
                value = getattr(state, substitution)
            if hasattr(transport, substitution):
                value = getattr(transport, substitution)
            if value:
                substitutions[substitution] = value
        if substitutions:
            label_as = label_as.format(**substitutions)
            evaluation_value = evaluation_value.format(**substitutions)
        if use_console:
            table = Table.grid(expand=True)
            table.add_column()
            table.add_column(justify="right")
            table.add_row(
                f"{evaluation_value} {label_as}", f"{state.hostname}:{state.port}"
            )
            console.print(table)
        evaluation_results.append(
            {
                "name": label_as,
                "key": evaluation["key"],
                "group": evaluation["group"],
                "cve": evaluation.get("cve", []),
                "cvss2": evaluation.get("cvss2", []),
                "cvss3": evaluation.get("cvss3", []),
                "result": result,
                "result_label": result_label,
                "score": score,
                "references": evaluation.get("references", []),
                "description": evaluation["issue"],
            }
        )

    return state, evaluation_results
