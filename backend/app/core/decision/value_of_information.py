"""Decision-specific expected value of information (EVSI) primitive.

The calculation requires an explicit likelihood model for each prospective
signal. It therefore replaces the previous placeholder VoI=0 interface
without pretending that information has value independently of a decision.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping, Sequence


@dataclass(frozen=True, slots=True)
class SignalLikelihood:
    signal: str
    prior_probability: float
    option_likelihoods: Mapping[str, float]

    def __post_init__(self) -> None:
        if not self.signal or not 0.0 <= self.prior_probability <= 1.0:
            raise ValueError("invalid signal prior")
        if not self.option_likelihoods:
            raise ValueError("option_likelihoods must not be empty")
        if any(not isfinite(v) or not 0.0 <= v <= 1.0 for v in self.option_likelihoods.values()):
            raise ValueError("likelihoods must be in [0,1]")


@dataclass(frozen=True, slots=True)
class ValueOfInformation:
    expected_value_with_information: float
    expected_value_without_information: float
    gross_value: float
    acquisition_cost: float
    net_value: float
    method: str


class ValueOfInformationEngine:
    """Computes expected value of a prospective signal under explicit posteriors."""

    @staticmethod
    def expected_utility(probabilities: Mapping[str, float], utilities: Mapping[str, float]) -> float:
        if not probabilities or set(probabilities) != set(utilities):
            raise ValueError("probabilities and utilities must contain the same options")
        total = sum(probabilities.values())
        if not 0.999999 <= total <= 1.000001:
            raise ValueError("probabilities must sum to 1")
        return sum(probabilities[key] * utilities[key] for key in probabilities)

    def compute(
        self,
        *,
        prior_option_probabilities: Mapping[str, float],
        utilities: Mapping[str, float],
        posterior_option_probabilities_by_signal: Mapping[str, Mapping[str, float]],
        signal_probabilities: Mapping[str, float],
        acquisition_cost: float = 0.0,
    ) -> ValueOfInformation:
        if not prior_option_probabilities or set(prior_option_probabilities) != set(utilities):
            raise ValueError("prior probabilities and utilities must contain the same options")
        if any(not isfinite(v) or v < 0 for v in prior_option_probabilities.values()):
            raise ValueError("prior probabilities must be non-negative and finite")
        if not 0.999999 <= sum(prior_option_probabilities.values()) <= 1.000001:
            raise ValueError("prior option probabilities must sum to 1")
        if acquisition_cost < 0 or not isfinite(acquisition_cost):
            raise ValueError("acquisition_cost must be finite and non-negative")
        if set(posterior_option_probabilities_by_signal) != set(signal_probabilities):
            raise ValueError("posterior signals and signal probabilities must match")
        if not 0.999999 <= sum(signal_probabilities.values()) <= 1.000001:
            raise ValueError("signal probabilities must sum to 1")

        without_information = max(utilities.values())
        with_information = 0.0
        for signal, signal_probability in signal_probabilities.items():
            posterior = posterior_option_probabilities_by_signal[signal]
            if set(posterior) != set(utilities):
                raise ValueError("each posterior must cover every option")
            if any(not isfinite(v) or v < 0 for v in posterior.values()):
                raise ValueError("posterior probabilities must be non-negative and finite")
            if not 0.999999 <= sum(posterior.values()) <= 1.000001:
                raise ValueError("each posterior must sum to 1")
            with_information += signal_probability * max(utilities[option] for option in posterior)

        gross = with_information - without_information
        return ValueOfInformation(
            expected_value_with_information=with_information,
            expected_value_without_information=without_information,
            gross_value=gross,
            acquisition_cost=acquisition_cost,
            net_value=gross - acquisition_cost,
            method="expected_value_of_sample_information",
        )
