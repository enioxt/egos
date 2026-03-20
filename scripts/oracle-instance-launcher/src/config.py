import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def _csv(name: str) -> list[str]:
    raw = os.getenv(name, "").strip()
    return [item.strip() for item in raw.split(",") if item.strip()] if raw else []


@dataclass(slots=True)
class AppConfig:
    auth_mode: str
    config_file: str
    profile: str
    region: str
    tenancy_id: str
    user_id: str
    fingerprint: str
    private_key_path: str
    private_key_passphrase: str
    compartment_id: str
    subnet_id: str
    image_id: str
    image_autodetect: bool
    image_os: str
    image_version: str
    ssh_public_key: str
    display_name: str
    hostname_label: str
    shape: str
    ocpus: int
    memory_gb: int
    boot_volume_gb: int
    assign_public_ip: bool
    ads: list[str]
    ad_strategy: str
    retry_seconds: int
    wait_for_running: bool
    stop_on_success: bool
    write_success_json: bool
    log_level: str


def load_config() -> AppConfig:
    load_dotenv()
    key_file = os.getenv("OCI_SSH_PUBLIC_KEY_FILE", "").strip()
    key_text = os.getenv("OCI_SSH_PUBLIC_KEY", "").strip()
    if key_file:
        key_text = Path(key_file).expanduser().read_text(encoding="utf-8").strip()
    cfg = AppConfig(
        auth_mode=os.getenv("OCI_AUTH_MODE", "api_key").strip(),
        config_file=os.getenv("OCI_CONFIG_FILE", "~/.oci/config").strip(),
        profile=os.getenv("OCI_PROFILE", "DEFAULT").strip(),
        region=os.getenv("OCI_REGION", "us-ashburn-1").strip(),
        tenancy_id=os.getenv("OCI_TENANCY_OCID", "").strip(),
        user_id=os.getenv("OCI_USER_OCID", "").strip(),
        fingerprint=os.getenv("OCI_FINGERPRINT", "").strip(),
        private_key_path=os.getenv("OCI_PRIVATE_KEY_PATH", "").strip(),
        private_key_passphrase=os.getenv("OCI_PRIVATE_KEY_PASSPHRASE", "").strip(),
        compartment_id=os.getenv("OCI_COMPARTMENT_ID", "").strip(),
        subnet_id=os.getenv("OCI_SUBNET_ID", "").strip(),
        image_id=os.getenv("OCI_IMAGE_ID", "").strip(), image_autodetect=_bool("OCI_IMAGE_AUTODETECT", True),
        image_os=os.getenv("OCI_IMAGE_OS", "Canonical Ubuntu").strip(), image_version=os.getenv("OCI_IMAGE_VERSION", "24.04").strip(),
        ssh_public_key=key_text, display_name=os.getenv("OCI_DISPLAY_NAME", "egos-a1-free").strip(),
        hostname_label=os.getenv("OCI_HOSTNAME_LABEL", "egos-a1-free").strip(), shape=os.getenv("OCI_SHAPE", "VM.Standard.A1.Flex").strip(),
        ocpus=int(os.getenv("OCI_OCPUS", "1")), memory_gb=int(os.getenv("OCI_MEMORY_GB", "6")), boot_volume_gb=int(os.getenv("OCI_BOOT_VOLUME_GB", "50")),
        assign_public_ip=_bool("OCI_ASSIGN_PUBLIC_IP", True), ads=_csv("OCI_ADS"), ad_strategy=os.getenv("OCI_AD_STRATEGY", "all").strip(),
        retry_seconds=int(os.getenv("OCI_RETRY_SECONDS", "300")), wait_for_running=_bool("OCI_WAIT_FOR_RUNNING", True),
        stop_on_success=_bool("OCI_STOP_ON_SUCCESS", True), write_success_json=_bool("OCI_WRITE_SUCCESS_JSON", True), log_level=os.getenv("OCI_LOG_LEVEL", "INFO").strip(),
    )
    required = [("OCI_COMPARTMENT_ID", cfg.compartment_id), ("OCI_SUBNET_ID", cfg.subnet_id), ("OCI_SSH_PUBLIC_KEY", cfg.ssh_public_key)]
    if cfg.auth_mode == "api_key" and not Path(cfg.config_file).expanduser().exists():
        required += [("OCI_TENANCY_OCID", cfg.tenancy_id), ("OCI_USER_OCID", cfg.user_id), ("OCI_FINGERPRINT", cfg.fingerprint), ("OCI_PRIVATE_KEY_PATH", cfg.private_key_path)]
    missing = [name for name, value in required if not value]
    if missing:
        raise ValueError(f"Missing required settings: {', '.join(missing)}")
    return cfg
