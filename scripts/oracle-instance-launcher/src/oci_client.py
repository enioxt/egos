from pathlib import Path
import oci
from oci.pagination import list_call_get_all_results
from src.config import AppConfig


def build_clients(cfg: AppConfig):
    if cfg.auth_mode == "instance_principal":
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        base = {"region": cfg.region}
        compute = oci.core.ComputeClient(base, signer=signer)
        identity = oci.identity.IdentityClient(base, signer=signer)
        return compute, identity

    config_path = Path(cfg.config_file).expanduser()
    if config_path.exists():
        base = oci.config.from_file(str(config_path), cfg.profile)
        cfg.region = base.get("region", cfg.region)
        cfg.tenancy_id = cfg.tenancy_id or base.get("tenancy", "")
    else:
        base = {
            "region": cfg.region,
            "tenancy": cfg.tenancy_id,
            "user": cfg.user_id,
            "fingerprint": cfg.fingerprint,
            "key_file": str(Path(cfg.private_key_path).expanduser()),
        }
        if cfg.private_key_passphrase:
            base["pass_phrase"] = cfg.private_key_passphrase
    return oci.core.ComputeClient(base), oci.identity.IdentityClient(base)


def discover_ads(cfg: AppConfig, identity) -> list[str]:
    if cfg.ads:
        return cfg.ads
    if not cfg.tenancy_id:
        raise ValueError("OCI_TENANCY_OCID is required for AD autodiscovery")
    response = identity.list_availability_domains(compartment_id=cfg.tenancy_id)
    return [item.name for item in response.data]


def discover_image_id(cfg: AppConfig, compute) -> str:
    if cfg.image_id:
        return cfg.image_id
    if not cfg.image_autodetect:
        raise ValueError("OCI_IMAGE_ID is required when autodetect is disabled")
    items = list_call_get_all_results(
        compute.list_images,
        compartment_id=cfg.compartment_id,
        operating_system=cfg.image_os,
        shape=cfg.shape,
        sort_by="TIMECREATED",
        sort_order="DESC",
    ).data
    if cfg.image_version:
        items = [item for item in items if cfg.image_version in (item.operating_system_version or "")]
    if not items:
        raise ValueError("No matching OCI image found for autodiscovery")
    return items[0].id


def wait_for_running(compute, instance_id: str):
    response = compute.get_instance(instance_id)
    return oci.wait_until(compute, response, "lifecycle_state", "RUNNING")


def is_capacity_error(exc: Exception) -> bool:
    if not isinstance(exc, oci.exceptions.ServiceError):
        return False
    message = f"{exc.code} {exc.message}".lower()
    return "out of host capacity" in message or "capacity" in message
