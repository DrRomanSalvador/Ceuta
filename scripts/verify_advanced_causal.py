from __future__ import annotations

from backend.app.core.causal.advanced import (
    ActiveCausalLearning,
    ActiveCausalQuery,
    CausalModel,
    CausalModelEnsemble,
    ConfoundingAnalyzer,
    FeedbackAnalyzer,
)


def main() -> None:
    if ConfoundingAnalyzer.adjustment_status(["z"], []) != "unresolved_confounding":
        raise SystemExit("FAIL: unresolved confounding was not blocked")
    models = [
        CausalModel("m1", (("x", "y"),), ("consistency",), 0.5),
        CausalModel("m2", (("z", "y"),), ("consistency",), 0.5),
    ]
    if not CausalModelEnsemble.disagreement(models):
        raise SystemExit("FAIL: model disagreement was collapsed")
    try:
        FeedbackAnalyzer.assess(["x", "y"], 0.5, False)
    except ValueError:
        pass
    else:
        raise SystemExit("FAIL: instantaneous feedback was accepted")
    queries = [ActiveCausalQuery("a", "measure", "u", 2, 1, 1, "information")]
    if ActiveCausalLearning.rank(queries)[0].priority != 2:
        raise SystemExit("FAIL: active causal priority")
    print("PASS: advanced causal reasoning invariants")


if __name__ == "__main__":
    main()
