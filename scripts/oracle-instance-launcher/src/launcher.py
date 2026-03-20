import json
import oci
from pathlib import Path
from src.models import LaunchResult
from src.oci_client import discover_ads, discover_image_id, is_capacity_error, wait_for_running


def _details(cfg, ad: str, image_id: str):
    return oci.core.models.LaunchInstanceDetails(
        availability_domain=ad,
        compartment_id=cfg.compartment_id,
        display_name=cfg.display_name,
        shape=cfg.shape,
        shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(ocpus=cfg.ocpus, memory_in_gbs=cfg.memory_gb),
        source_details=oci.core.models.InstanceSourceViaImageDetails(source_type="image", image_id=image_id, boot_volume_size_in_gbs=cfg.boot_volume_gb),
        create_vnic_details=oci.core.models.CreateVnicDetails(assign_public_ip=cfg.assign_public_ip, subnet_id=cfg.subnet_id, hostname_label=cfg.hostname_label),
        metadata={"ssh_authorized_keys": cfg.ssh_public_key},
    )


def _write_success(result: LaunchResult):
    payload = {
        "instance_id": result.instance_id,
        "availability_domain": result.availability_domain,
        "lifecycle_state": result.lifecycle_state,
        "message": result.message,
    }
    Path("success.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def launch_cycle(cfg, compute, identity, logger) -> LaunchResult:
    ads = discover_ads(cfg, identity)
    image_id = discover_image_id(cfg, compute)
    logger.info("Attempting launch across %s using image %s", ads, image_id)
    for ad in ads:
        try:
            response = compute.launch_instance(_details(cfg, ad, image_id))
            instance = response.data
            if cfg.wait_for_running:
                instance = wait_for_running(compute, instance.id).data
            result = LaunchResult(True, "Instance launched successfully", instance.id, ad, instance.lifecycle_state)
            if cfg.write_success_json:
                _write_success(result)
            return result
        except Exception as exc:
            if is_capacity_error(exc):
                logger.warning("Capacity unavailable in %s: %s", ad, exc)
                continue
            logger.exception("Launch failed in %s", ad)
    return LaunchResult(False, f"No AD succeeded; retrying in {cfg.retry_seconds}s")
