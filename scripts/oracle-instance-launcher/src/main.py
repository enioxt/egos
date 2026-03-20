import argparse
import time
from pathlib import Path
from src.config import load_config
from src.launcher import launch_cycle
from src.logger import build_logger
from src.oci_client import build_clients


def parse_args():
    parser = argparse.ArgumentParser(description="Oracle A1 instance launcher")
    parser.add_argument("--dry-run", action="store_true", help="Validate config without launching")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    return parser.parse_args()


def main():
    args = parse_args()
    cfg = load_config()
    logger = build_logger(cfg.log_level, args.verbose)

    if cfg.stop_on_success and Path("success.json").exists():
        logger.info("success.json already exists; exiting")
        return

    logger.info("Launcher ready for %s in %s", cfg.shape, cfg.region)
    if args.dry_run:
        logger.info("Dry-run complete; config validated")
        return

    compute, identity = build_clients(cfg)
    while True:
        result = launch_cycle(cfg, compute, identity, logger)
        if result.success:
            logger.info("Success in %s: %s", result.availability_domain, result.instance_id)
            return
        logger.warning(result.message)
        time.sleep(cfg.retry_seconds)


if __name__ == "__main__":
    main()
