#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""production_deployment.py

Production deployment configuration and security hardening for the
EGOS Diagnostic Tracking System, implementing best practices for secure
deployment in multi-user environments.

@references:
- Core References:
  - [MQP.md](mdc:../../MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP.md](mdc:../../ROADMAP.md) - Project roadmap and planning
- Security References:
  - [security_standards.md](mdc:../../docs/security/security_standards.md)
  - [ethik_validation.md](mdc:../../docs/frameworks/ethik_validation.md)
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import os
import sys
import argparse
import logging
import secrets
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
import hashlib
import uuid
import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("EGOS.Dashboard.ProductionDeployment")

# Default configuration
DEFAULT_CONFIG = {
    "server": {
        "host": "0.0.0.0",
        "port": 8501,
        "use_ssl": True,
        "ssl_cert_path": "./certificates/cert.pem",
        "ssl_key_path": "./certificates/key.pem",
        "enable_cors": False,
        "allowed_origins": [],
        "max_upload_size_mb": 50,
        "session_expiry_hours": 24,
        "rate_limit_requests": 100,
        "rate_limit_period_minutes": 5
    },
    "security": {
        "force_https": True,
        "content_security_policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;",
        "x_frame_options": "DENY",
        "strict_transport_security": "max-age=31536000; includeSubDomains",
        "password_min_length": 12,
        "password_requires_special": True,
        "password_requires_number": True,
        "password_requires_uppercase": True,
        "password_requires_lowercase": True,
        "failed_login_lockout_threshold": 5,
        "failed_login_lockout_minutes": 30,
        "session_idle_timeout_minutes": 30,
        "admin_email": "admin@egos.local"
    },
    "data": {
        "data_dir": "./data",
        "backup_dir": "./backups",
        "backup_frequency_hours": 12,
        "max_backups": 30,
        "encryption_enabled": True
    },
    "notifications": {
        "smtp_server": "smtp.example.com",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "smtp_username": "",
        "smtp_password": "",
        "from_email": "diagnostics@egos.local",
        "admin_notification_email": "admin@egos.local"
    },
    "mycelium": {
        "server_url": "nats://localhost:4222",
        "use_tls": True,
        "client_cert_path": "./certificates/client-cert.pem",
        "client_key_path": "./certificates/client-key.pem",
        "ca_cert_path": "./certificates/ca.pem",
        "max_reconnect": 10,
        "reconnect_wait_seconds": 2
    },
    "logging": {
        "log_dir": "./logs",
        "level": "INFO",
        "max_log_size_mb": 10,
        "backup_count": 5,
        "log_format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        "audit_logging": True
    }
}

def generate_secret_key() -> str:
    """Generate a secure random secret key.
    
    Returns:
        Random 32-byte hex string
    """
    return secrets.token_hex(32)

def create_ssl_certificates(cert_dir: Path) -> bool:
    """Create self-signed SSL certificates for development.
    
    Args:
        cert_dir: Directory to store certificates
        
    Returns:
        Success status
    """
    try:
        # Create certificate directory
        cert_dir.mkdir(parents=True, exist_ok=True)
        
        # Define paths
        key_path = cert_dir / "key.pem"
        cert_path = cert_dir / "cert.pem"
        
        # Check if certificates already exist
        if key_path.exists() and cert_path.exists():
            logger.info("SSL certificates already exist")
            return True
        
        # Generate self-signed certificate
        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:4096",
            "-keyout", str(key_path),
            "-out", str(cert_path),
            "-days", "365",
            "-nodes",
            "-subj", "/C=US/ST=State/L=City/O=EGOS/CN=egos.local"
        ], check=True)
        
        logger.info(f"Generated self-signed SSL certificates in {cert_dir}")
        return True
    except Exception as e:
        logger.error(f"Error creating SSL certificates: {e}")
        return False

def create_directory_structure(base_dir: Path, config: Dict[str, Any]) -> bool:
    """Create the directory structure for production deployment.
    
    Args:
        base_dir: Base directory for deployment
        config: Configuration dictionary
        
    Returns:
        Success status
    """
    try:
        # Create required directories
        dirs_to_create = [
            Path(config["data"]["data_dir"]),
            Path(config["data"]["backup_dir"]),
            Path(config["logging"]["log_dir"]),
            Path(os.path.dirname(config["server"]["ssl_cert_path"]))
        ]
        
        for dir_path in dirs_to_create:
            # Convert to absolute path if relative
            if not dir_path.is_absolute():
                dir_path = base_dir / dir_path
            
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")
        
        logger.info("Created directory structure for production deployment")
        return True
    except Exception as e:
        logger.error(f"Error creating directory structure: {e}")
        return False

def create_environment_file(base_dir: Path, config: Dict[str, Any]) -> bool:
    """Create environment file with sensitive configuration.
    
    Args:
        base_dir: Base directory for deployment
        config: Configuration dictionary
        
    Returns:
        Success status
    """
    try:
        env_path = base_dir / ".env"
        
        with open(env_path, 'w') as f:
            # Add sensitive configuration
            f.write(f"SECRET_KEY={generate_secret_key()}\n")
            f.write(f"SMTP_USERNAME={config['notifications']['smtp_username']}\n")
            f.write(f"SMTP_PASSWORD={config['notifications']['smtp_password']}\n")
            
            # Add server configuration
            f.write(f"SERVER_HOST={config['server']['host']}\n")
            f.write(f"SERVER_PORT={config['server']['port']}\n")
            f.write(f"USE_SSL={str(config['server']['use_ssl']).lower()}\n")
            
            # Add mycelium configuration
            f.write(f"MYCELIUM_SERVER_URL={config['mycelium']['server_url']}\n")
            f.write(f"MYCELIUM_USE_TLS={str(config['mycelium']['use_tls']).lower()}\n")
            
            # Add admin email
            f.write(f"ADMIN_EMAIL={config['security']['admin_email']}\n")
        
        # Set restrictive permissions
        os.chmod(env_path, 0o600)
        
        logger.info(f"Created environment file: {env_path}")
        return True
    except Exception as e:
        logger.error(f"Error creating environment file: {e}")
        return False

def create_nginx_config(base_dir: Path, config: Dict[str, Any]) -> bool:
    """Create Nginx configuration for production deployment.
    
    Args:
        base_dir: Base directory for deployment
        config: Configuration dictionary
        
    Returns:
        Success status
    """
    try:
        nginx_config_path = base_dir / "nginx.conf"
        
        with open(nginx_config_path, 'w') as f:
            f.write(f"""
server {{
    listen 80;
    server_name _;
    
    # Redirect all HTTP traffic to HTTPS
    return 301 https://$host$request_uri;
}}

server {{
    listen 443 ssl;
    server_name _;
    
    # SSL configuration
    ssl_certificate {config['server']['ssl_cert_path']};
    ssl_certificate_key {config['server']['ssl_key_path']};
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305';
    
    # Security headers
    add_header Strict-Transport-Security "{config['security']['strict_transport_security']}";
    add_header X-Frame-Options "{config['security']['x_frame_options']}";
    add_header X-Content-Type-Options "nosniff";
    add_header Content-Security-Policy "{config['security']['content_security_policy']}";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    # Proxy settings
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=diagnostic_limit:10m rate=10r/s;
    limit_req zone=diagnostic_limit burst=20 nodelay;
    
    # File size limits
    client_max_body_size {config['server']['max_upload_size_mb']}m;
    
    # Proxy to Streamlit
    location / {{
        proxy_pass http://localhost:{config['server']['port']};
    }}
    
    # Static files (if needed)
    location /static/ {{
        alias {base_dir}/static/;
        expires 1d;
    }}
    
    # Logs
    access_log {config['logging']['log_dir']}/nginx_access.log;
    error_log {config['logging']['log_dir']}/nginx_error.log;
}}
            """)
        
        logger.info(f"Created Nginx configuration: {nginx_config_path}")
        return True
    except Exception as e:
        logger.error(f"Error creating Nginx configuration: {e}")
        return False

def create_systemd_service(base_dir: Path, config: Dict[str, Any]) -> bool:
    """Create systemd service for production deployment.
    
    Args:
        base_dir: Base directory for deployment
        config: Configuration dictionary
        
    Returns:
        Success status
    """
    try:
        service_path = base_dir / "egos-diagnostic.service"
        
        with open(service_path, 'w') as f:
            f.write(f"""
[Unit]
Description=EGOS Diagnostic Tracking System
After=network.target

[Service]
User=egos
WorkingDirectory={base_dir}
Environment="PATH={base_dir}/venv/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile={base_dir}/.env
ExecStart={base_dir}/venv/bin/streamlit run diagnostic_launcher.py --server.port={config['server']['port']} --server.address={config['server']['host']} --server.maxUploadSize={config['server']['max_upload_size_mb']}
Restart=always
RestartSec=5
StartLimitInterval=0

# Security hardening
CapabilityBoundingSet=
PrivateTmp=true
PrivateDevices=true
ProtectSystem=full
ProtectHome=true
NoNewPrivileges=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
LockPersonality=true
SystemCallFilter=@system-service
SystemCallErrorNumber=EPERM

[Install]
WantedBy=multi-user.target
            """)
        
        logger.info(f"Created systemd service file: {service_path}")
        return True
    except Exception as e:
        logger.error(f"Error creating systemd service file: {e}")
        return False

def create_backup_script(base_dir: Path, config: Dict[str, Any]) -> bool:
    """Create backup script for production deployment.
    
    Args:
        base_dir: Base directory for deployment
        config: Configuration dictionary
        
    Returns:
        Success status
    """
    try:
        backup_script_path = base_dir / "backup.py"
        
        with open(backup_script_path, 'w') as f:
            f.write(f"""#!/usr/bin/env python
# -*- coding: utf-8 -*-

\"\"\"
EGOS Diagnostic Tracking System Backup Script

This script creates automatic backups of the diagnostic tracking data,
ensuring data is preserved and can be restored in case of failure.
\"\"\"

import os
import sys
import shutil
import datetime
import logging
import json
import glob
from pathlib import Path
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("EGOS.Dashboard.BackupScript")

def create_backup(data_dir="{config['data']['data_dir']}", 
                 backup_dir="{config['data']['backup_dir']}",
                 max_backups={config['data']['max_backups']}):
    \"\"\"Create a backup of the diagnostic tracking data.\"\"\"
    try:
        # Ensure backup directory exists
        Path(backup_dir).mkdir(parents=True, exist_ok=True)
        
        # Create timestamp for backup
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = Path(backup_dir) / f"diagnostic_backup_{timestamp}.zip"
        
        # Create zip archive
        shutil.make_archive(
            str(backup_path).replace('.zip', ''),
            'zip',
            data_dir
        )
        
        logger.info(f"Created backup: {backup_path}")
        
        # Clean up old backups
        backup_files = sorted(glob.glob(str(Path(backup_dir) / "diagnostic_backup_*.zip")))
        if len(backup_files) > max_backups:
            # Remove oldest backups
            for old_backup in backup_files[:-max_backups]:
                os.remove(old_backup)
                logger.info(f"Removed old backup: {old_backup}")
        
        return True
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        return False

def restore_backup(backup_path, data_dir="{config['data']['data_dir']}"):
    \"\"\"Restore data from a backup.\"\"\"
    try:
        if not os.path.exists(backup_path):
            logger.error(f"Backup file not found: {backup_path}")
            return False
        
        # Create backup of current data before restoration
        create_backup(data_dir, "{config['data']['backup_dir']}", {config['data']['max_backups']})
        
        # Clear current data directory
        for item in os.listdir(data_dir):
            item_path = os.path.join(data_dir, item)
            if os.path.isfile(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        
        # Extract backup
        shutil.unpack_archive(backup_path, data_dir)
        
        logger.info(f"Restored backup from: {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Error restoring backup: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EGOS Diagnostic Tracking System Backup Utility")
    parser.add_argument("action", choices=["backup", "restore"], help="Action to perform")
    parser.add_argument("--backup-path", help="Path to backup file (for restore)")
    
    args = parser.parse_args()
    
    if args.action == "backup":
        success = create_backup()
        sys.exit(0 if success else 1)
    elif args.action == "restore":
        if not args.backup_path:
            parser.error("--backup-path is required for restore action")
        
        success = restore_backup(args.backup_path)
        sys.exit(0 if success else 1)
            """)
        
        # Make script executable
        os.chmod(backup_script_path, 0o755)
        
        logger.info(f"Created backup script: {backup_script_path}")
        return True
    except Exception as e:
        logger.error(f"Error creating backup script: {e}")
        return False

def create_cron_jobs(base_dir: Path, config: Dict[str, Any]) -> bool:
    """Create cron jobs for production deployment.
    
    Args:
        base_dir: Base directory for deployment
        config: Configuration dictionary
        
    Returns:
        Success status
    """
    try:
        cron_path = base_dir / "crontab"
        
        with open(cron_path, 'w') as f:
            f.write(f"""# EGOS Diagnostic Tracking System Cron Jobs
# Automatic backups every {config['data']['backup_frequency_hours']} hours
0 */{config['data']['backup_frequency_hours']} * * * {base_dir}/venv/bin/python {base_dir}/backup.py backup >> {config['logging']['log_dir']}/backup.log 2>&1

# Log rotation daily
0 0 * * * find {config['logging']['log_dir']} -name "*.log" -size +{config['logging']['max_log_size_mb']}M -exec gzip {{}} \;

# Health check every 5 minutes
*/5 * * * * curl -s -o /dev/null -w "%{{http_code}}" https://localhost:{config['server']['port']}/healthz | grep 200 || systemctl restart egos-diagnostic.service
            """)
        
        logger.info(f"Created cron jobs file: {cron_path}")
        return True
    except Exception as e:
        logger.error(f"Error creating cron jobs file: {e}")
        return False

def create_deployment_script(base_dir: Path) -> bool:
    """Create deployment script.
    
    Args:
        base_dir: Base directory for deployment
        
    Returns:
        Success status
    """
    try:
        script_path = base_dir / "deploy.sh"
        
        with open(script_path, 'w') as f:
            f.write("""#!/bin/bash

# EGOS Diagnostic Tracking System Deployment Script

set -e

# Check for root privileges
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

# Configuration
APP_USER="egos"
APP_DIR=$(pwd)

echo "=== EGOS Diagnostic Tracking System Deployment ==="
echo "Deploying to: $APP_DIR"

# Create user if it doesn't exist
if ! id -u $APP_USER >/dev/null 2>&1; then
    echo "Creating user: $APP_USER"
    useradd -m -s /bin/bash $APP_USER
fi

# Install required packages
echo "Installing required packages..."
apt-get update
apt-get install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx

# Set up virtual environment
echo "Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -U pip
pip install -r requirements.txt

# Create directory structure
echo "Creating directory structure..."
python production_deployment.py --create-dirs

# Set up SSL certificates
echo "Setting up SSL certificates..."
python production_deployment.py --create-ssl

# Install systemd service
echo "Installing systemd service..."
cp egos-diagnostic.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable egos-diagnostic.service

# Install nginx configuration
echo "Installing nginx configuration..."
cp nginx.conf /etc/nginx/sites-available/egos-diagnostic
ln -sf /etc/nginx/sites-available/egos-diagnostic /etc/nginx/sites-enabled/
nginx -t && systemctl restart nginx

# Install cron jobs
echo "Installing cron jobs..."
crontab -u $APP_USER crontab

# Set correct permissions
echo "Setting permissions..."
chown -R $APP_USER:$APP_USER $APP_DIR
chmod 600 $APP_DIR/.env
chmod 755 $APP_DIR/backup.py

# Start the service
echo "Starting the service..."
systemctl start egos-diagnostic.service

echo "=== Deployment completed successfully ==="
echo "EGOS Diagnostic Tracking System is now running"
echo "Access the dashboard at: https://localhost"
            """)
        
        # Make script executable
        os.chmod(script_path, 0o755)
        
        logger.info(f"Created deployment script: {script_path}")
        return True
    except Exception as e:
        logger.error(f"Error creating deployment script: {e}")
        return False

def create_healthcheck_endpoint(base_dir: Path) -> bool:
    """Create healthcheck endpoint for production deployment.
    
    Args:
        base_dir: Base directory for deployment
        
    Returns:
        Success status
    """
    try:
        healthcheck_path = base_dir / "healthcheck.py"
        
        with open(healthcheck_path, 'w') as f:
            f.write("""#!/usr/bin/env python
# -*- coding: utf-8 -*-

\"\"\"
EGOS Diagnostic Tracking System Healthcheck Endpoint

This module provides a healthcheck endpoint for monitoring and
automatic recovery of the diagnostic tracking system.
\"\"\"

import streamlit as st
import json
import time
import datetime
import sys
import os
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def check_database():
    \"\"\"Check if tracking database is accessible.\"\"\"
    try:
        from dashboard.diagnostic_tracking import get_all_issues
        issues = get_all_issues()
        return True
    except Exception:
        return False

def check_mycelium():
    \"\"\"Check if MYCELIUM connection is active.\"\"\"
    try:
        import asyncio
        from dashboard.diagnostic_mycelium import DiagnosticCollaborationManager
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def test_connection():
            manager = DiagnosticCollaborationManager()
            connected = await manager.initialize()
            if connected:
                await manager.shutdown()
            return connected
        
        return loop.run_until_complete(test_connection())
    except Exception:
        return False

def main():
    # Remove default Streamlit styling
    hide_streamlit_style = \"\"\"
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    \"\"\"
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    # Check if path is /healthz
    if st.experimental_get_query_params().get("check") == ["health"]:
        status = {
            "status": "ok",
            "timestamp": datetime.datetime.now().isoformat(),
            "checks": {
                "database": check_database(),
                "mycelium": check_mycelium()
            }
        }
        
        # Set overall status
        if not all(status["checks"].values()):
            status["status"] = "degraded"
        
        # Return JSON response
        st.json(status)
    else:
        st.error("Access denied")

if __name__ == "__main__":
    main()
            """)
        
        logger.info(f"Created healthcheck endpoint: {healthcheck_path}")
        return True
    except Exception as e:
        logger.error(f"Error creating healthcheck endpoint: {e}")
        return False

def main():
    """Main function for production deployment."""
    parser = argparse.ArgumentParser(description="EGOS Diagnostic Tracking System Production Deployment")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--output-dir", help="Output directory for deployment files")
    parser.add_argument("--create-dirs", action="store_true", help="Create directory structure")
    parser.add_argument("--create-ssl", action="store_true", help="Create SSL certificates")
    parser.add_argument("--interactive", action="store_true", help="Interactive configuration")
    
    args = parser.parse_args()
    
    # Determine base directory
    if args.output_dir:
        base_dir = Path(args.output_dir)
    else:
        base_dir = Path(__file__).resolve().parent
    
    # Load configuration
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
    else:
        config = DEFAULT_CONFIG
    
    logger.info(f"Starting production deployment to {base_dir}")
    
    # Interactive configuration
    if args.interactive:
        # TODO: Implement interactive configuration
        pass
    
    # Create components
    create_directory_structure(base_dir, config)
    
    if args.create_ssl:
        create_ssl_certificates(base_dir / Path(os.path.dirname(config["server"]["ssl_cert_path"])))
    
    create_environment_file(base_dir, config)
    create_nginx_config(base_dir, config)
    create_systemd_service(base_dir, config)
    create_backup_script(base_dir, config)
    create_cron_jobs(base_dir, config)
    create_deployment_script(base_dir)
    create_healthcheck_endpoint(base_dir)
    
    logger.info("Production deployment configuration completed successfully")
    logger.info(f"Run the deployment script to complete the deployment: {base_dir / 'deploy.sh'}")

if __name__ == "__main__":
    main()