"""Typed SDK failures."""


class RappSDKError(Exception):
    """Base class for SDK errors."""


class ValidationError(RappSDKError, ValueError):
    """Input or artifact validation failed."""


class CanonicalizationError(ValidationError):
    """A value is outside the RAPP/1 canonical JSON profile."""


class InventoryError(ValidationError):
    """The organism inventory is invalid."""


class SpecimenAccessError(ValidationError):
    """A specimen path is unsafe or unavailable."""


class TrustError(ValidationError):
    """Authenticated evidence was absent or invalid."""


class FrameValidationError(ValidationError):
    """A frame failed a specific ordered acceptance step."""

    def __init__(self, step: str, message: str):
        self.step = step
        super().__init__(f"frame step {step}: {message}")


class FrameStateError(FrameValidationError):
    """Persisted stream state refused rollback, fork, gap, or unauthorized reset."""


class EggValidationError(ValidationError):
    """An egg failed structural, integrity, or trust validation."""


class WireError(RappSDKError):
    """Base class for wire errors."""


class WireProtocolError(WireError):
    """The peer did not emit the exact RAPP/1 wire contract."""


class WireTransportError(WireError):
    """The HTTP exchange failed."""


class ResponseTooLarge(WireProtocolError):
    """A response exceeded the configured bound."""


class RappRefusal(WireError):
    """An exact HTTP 422 RAPP/1 refusal."""

    def __init__(self, code: str, step: str | None):
        self.code = code
        self.step = step
        super().__init__(f"RAPP/1 refusal: {code} (step={step!r})")


class StructuralRefusalOnly(WireError):
    """A refusal has exact wire shape but lacks authenticated error-code evidence."""

    def __init__(self, code: str, step: str | None):
        self.code = code
        self.step = step
        super().__init__(
            f"structural refusal only: {code} (step={step!r}); "
            "VerifiedRegistry proof required for conformant acceptance"
        )
