"""Environment-backed configuration for the Bedrock AI Help provider."""

from __future__ import annotations

import os
from dataclasses import dataclass


DEFAULT_BEDROCK_MODEL_ID = "amazon.nova-lite-v1:0"
DEFAULT_BEDROCK_TIMEOUT_SECONDS = 10.0
MAX_BEDROCK_TIMEOUT_SECONDS = 30.0


class BedrockNotConfiguredError(ValueError):
    """Raised when the provider has not been configured for the deployment."""


@dataclass(frozen=True)
class BedrockConfig:
    region: str
    model_id: str = DEFAULT_BEDROCK_MODEL_ID
    timeout_seconds: float = DEFAULT_BEDROCK_TIMEOUT_SECONDS

    @classmethod
    def from_environment(cls) -> "BedrockConfig":
        region = (
            os.getenv("BEDROCK_AWS_REGION")
            or os.getenv("AWS_REGION")
            or os.getenv("AWS_DEFAULT_REGION")
        )
        if not region or not region.strip():
            raise BedrockNotConfiguredError(
                "AI Help provider is not configured"
            )

        model_id = os.getenv("BEDROCK_MODEL_ID", DEFAULT_BEDROCK_MODEL_ID)
        if not model_id.strip():
            raise BedrockNotConfiguredError(
                "AI Help provider is not configured"
            )

        timeout_value = os.getenv(
            "BEDROCK_TIMEOUT_SECONDS",
            str(DEFAULT_BEDROCK_TIMEOUT_SECONDS),
        )
        try:
            timeout_seconds = float(timeout_value)
        except ValueError as exc:
            raise BedrockNotConfiguredError(
                "AI Help provider is not configured"
            ) from exc
        if timeout_seconds <= 0 or timeout_seconds > MAX_BEDROCK_TIMEOUT_SECONDS:
            raise BedrockNotConfiguredError(
                "AI Help provider is not configured"
            )

        return cls(
            region=region.strip(),
            model_id=model_id.strip(),
            timeout_seconds=timeout_seconds,
        )
