from dataclasses import dataclass


@dataclass(slots=True)
class LaunchResult:
    success: bool
    message: str
    instance_id: str | None = None
    availability_domain: str | None = None
    lifecycle_state: str | None = None
