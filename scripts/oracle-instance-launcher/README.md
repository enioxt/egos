# Oracle Instance Launcher

Python utility to retry creation of an Oracle Cloud `VM.Standard.A1.Flex`
instance until capacity is available.

## Features

- API key or instance principal auth
- Retry across multiple Availability Domains
- Capacity-aware retry handling
- Optional image autodiscovery for Ubuntu ARM
- `success.json` guard to stop after first success
- Rotating logs in `logs/app.log`
- `--dry-run` and `--verbose`
- systemd-friendly runner

## Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill `.env` with your OCI values.

## Run

```bash
bash ./scripts/run.sh --dry-run
bash ./scripts/run.sh --verbose
```

The launcher exits immediately if `success.json` already exists and
`OCI_STOP_ON_SUCCESS=true`.

## Auth modes

- `api_key`: uses `OCI_CONFIG_FILE` + `OCI_PROFILE` when present, with env
  fallback for tenancy, user, fingerprint, and private key.
- `instance_principal`: uses OCI instance principal signer.

## Output

- `logs/app.log`
- `success.json`

## systemd

```bash
bash ./scripts/install_service.sh
sudo systemctl start oracle-instance-launcher.service
sudo systemctl status oracle-instance-launcher.service
```

## Notes

- Oracle Always Free compute is only available in the tenancy home region.
- If OCI returns `Out of host capacity`, the launcher advances to the next AD.
- For autodiscovery of ADs, provide `OCI_TENANCY_OCID`.
