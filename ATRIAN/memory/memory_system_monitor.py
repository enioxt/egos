#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATRiAN Memory System Monitor

This module provides monitoring capabilities for the ATRiAN memory system,
including usage analytics, privacy compliance checks, and diagnostic utilities.

It aligns with EGOS principles such as Systemic Cartography (SC) for
understanding system state, and Evolutionary Preservation (EP) by providing
tools to maintain system health over time.
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

# Assuming WindsurfMemoryAdapter is in the same directory or accessible in PYTHONPATH
# If not, adjust the import path accordingly.
# from .windsurf_memory_adapter import WindsurfMemoryAdapter, MemoryBackendInterface

# Placeholder for actual adapter import - this will need to be resolved
# based on the final project structure.
# For now, we'll define a mock adapter for development if direct import is problematic.

# EGOS Standards
EGOS_VERSION = "1.0.0"
EGOS_AUTHOR = "EGOS Team (AI: Cascade)"
EGOS_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MemorySystemMonitor:
    """
    Monitors the ATRiAN memory system, providing analytics, compliance checks,
    and diagnostic utilities.
    """

    def __init__(self, memory_adapter: Any, config: Optional[Dict[str, Any]] = None):
        """
        Initializes the MemorySystemMonitor.

        Args:
            memory_adapter: An instance of WindsurfMemoryAdapter or a compatible
                            memory backend interface.
            config: Optional configuration dictionary for the monitor.
        """
        self.memory_adapter = memory_adapter
        self.config = config if config else self._load_default_config()
        self.last_report_time: Optional[datetime] = None
        logger.info("MemorySystemMonitor initialized.")

    def _load_default_config(self) -> Dict[str, Any]:
        """
        Loads default configuration for the monitor.
        """
        # In a real scenario, this might load from a file or environment variables
        return {
            "report_interval_hours": 24,
            "storage_usage_threshold_gb": 10,
            "privacy_compliance_check_interval_days": 7,
            "log_retention_days": 30,
            "anonymization_effectiveness_threshold": 0.95
        }

    def get_status(self) -> Dict[str, Any]:
        """
        Returns the current status of the memory monitor.
        """
        return {
            "status": "Operational",
            "last_report_time": self.last_report_time.isoformat() if self.last_report_time else "N/A",
            "config": self.config,
            "adapter_type": type(self.memory_adapter).__name__
        }

    # --- Memory Usage Analytics --- #

    def get_total_storage_size(self, unit: str = 'bytes') -> float:
        """
        Calculates the total size of data managed by the memory adapter.

        Args:
            unit: The unit for the returned size ('bytes', 'kb', 'mb', 'gb').

        Returns:
            Total storage size in the specified unit.
        """
        total_size_bytes = 0
        try:
            all_items = self.memory_adapter._get_all_data_items()
            for item in all_items:
                total_size_bytes += item.get('size_bytes', 0)
        except AttributeError:
            logger.warning("_get_all_data_items method not found on adapter. Cannot calculate total storage size.")
            return 0.0
        except Exception as e:
            logger.error(f"Error calculating total storage size: {e}")
            return 0.0

        if unit.lower() == 'kb':
            return total_size_bytes / 1024
        elif unit.lower() == 'mb':
            return total_size_bytes / (1024 ** 2)
        elif unit.lower() == 'gb':
            return total_size_bytes / (1024 ** 3)
        return float(total_size_bytes)

    def get_storage_size_by_user(self, unit: str = 'bytes') -> Dict[str, float]:
        """
        Calculates storage size per user.

        Args:
            unit: The unit for the returned sizes ('bytes', 'kb', 'mb', 'gb').

        Returns:
            A dictionary mapping user_id to storage size in the specified unit.
        """
        size_by_user: Dict[str, int] = {}
        try:
            users = self.memory_adapter.get_all_users()
            for user_id in users:
                user_data = self.memory_adapter.get_all_data_for_user(user_id)
                user_size_bytes = sum(item.get('size_bytes', 0) for item in user_data)
                size_by_user[user_id] = user_size_bytes
        except AttributeError:
            logger.warning("Adapter missing required methods (get_all_users, get_all_data_for_user). Cannot get size by user.")
            return {}
        except Exception as e:
            logger.error(f"Error calculating storage size by user: {e}")
            return {}

        result_by_user: Dict[str, float] = {}
        for user, size_bytes in size_by_user.items():
            if unit.lower() == 'kb':
                result_by_user[user] = size_bytes / 1024
            elif unit.lower() == 'mb':
                result_by_user[user] = size_bytes / (1024 ** 2)
            elif unit.lower() == 'gb':
                result_by_user[user] = size_bytes / (1024 ** 3)
            else:
                result_by_user[user] = float(size_bytes)
        return result_by_user

    def get_item_count_by_operation_type(self) -> Dict[str, int]:
        """
        Counts the number of memory items by operation type.

        Returns:
            A dictionary mapping operation_type to item count.
        """
        count_by_op_type: Dict[str, int] = {}
        try:
            all_items = self.memory_adapter._get_all_data_items()
            for item in all_items:
                op_type = item.get('operation_type', 'unknown')
                count_by_op_type[op_type] = count_by_op_type.get(op_type, 0) + 1
        except AttributeError:
            logger.warning("_get_all_data_items method not found on adapter. Cannot count items by operation type.")
            return {}
        except Exception as e:
            logger.error(f"Error counting items by operation type: {e}")
            return {}
        return count_by_op_type

    def get_item_count_by_sensitivity(self) -> Dict[str, int]:
        """
        Counts items by their declared sensitivity level from metadata.

        Returns:
            A dictionary mapping sensitivity_level to item count.
        """
        count_by_sensitivity: Dict[str, int] = {}
        try:
            all_items = self.memory_adapter._get_all_data_items()
            for item in all_items:
                metadata = item.get('_metadata', {})
                sensitivity = metadata.get('sensitivity_level', 'UNKNOWN')
                count_by_sensitivity[sensitivity] = count_by_sensitivity.get(sensitivity, 0) + 1
        except AttributeError:
            logger.warning("_get_all_data_items method not found on adapter. Cannot count items by sensitivity.")
            return {}
        except Exception as e:
            logger.error(f"Error counting items by sensitivity: {e}")
            return {}
        return count_by_sensitivity

    def generate_memory_usage_report_section(self) -> str:
        """
        Generates a report section summarizing memory usage analytics.

        Returns:
            A string containing the formatted memory usage report section.
        """
        report_data = {
            "total_storage_size_gb": f"{self.get_total_storage_size(unit='gb'):.4f} GB",
            "total_storage_size_mb": f"{self.get_total_storage_size(unit='mb'):.2f} MB",
            "item_count_by_operation_type": json.dumps(self.get_item_count_by_operation_type(), indent=2),
            "item_count_by_sensitivity_level": json.dumps(self.get_item_count_by_sensitivity(), indent=2),
            "storage_size_by_user_mb": json.dumps({k: f"{v:.2f} MB" for k, v in self.get_storage_size_by_user(unit='mb').items()}, indent=2)
        }
        return self._format_report_section("Memory Usage Analytics", report_data)


    # --- Privacy Compliance Monitoring --- #

    def check_retention_policy_compliance(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Identifies items that may have violated retention policies.
        Checks if items are older than their specified retention period.

        Returns:
            A dictionary containing a list of potentially non-compliant items
            and a summary count.
        """
        non_compliant_items: List[Dict[str, Any]] = []
        summary = {"total_items_checked": 0, "potentially_overdue_items": 0}
        now = datetime.now().astimezone()

        try:
            all_items = self.memory_adapter._get_all_data_items()
            summary["total_items_checked"] = len(all_items)

            for item in all_items:
                metadata = item.get('_metadata', {})
                item_timestamp_str = item.get('timestamp')
                retention_days = metadata.get('retention_days')

                if item_timestamp_str and retention_days is not None:
                    try:
                        item_timestamp = datetime.fromisoformat(item_timestamp_str)
                        # Ensure item_timestamp is offset-aware if now is offset-aware
                        if now.tzinfo is not None and item_timestamp.tzinfo is None:
                            item_timestamp = item_timestamp.replace(tzinfo=now.tzinfo) # Assume same timezone if not specified
                        
                        expiration_date = item_timestamp + timedelta(days=int(retention_days))
                        if now > expiration_date:
                            non_compliant_items.append({
                                'user_id': item.get('user_id', 'unknown'), # Assuming user_id is part of the item
                                'context_id': item.get('_context_id', 'unknown'),
                                'timestamp': item_timestamp_str,
                                'retention_days': retention_days,
                                'expiration_date': expiration_date.isoformat(),
                                'days_overdue': (now - expiration_date).days
                            })
                            summary["potentially_overdue_items"] += 1
                    except ValueError:
                        logger.warning(f"Invalid timestamp format for item {item.get('_context_id', 'unknown')}: {item_timestamp_str}")
                    except TypeError:
                        logger.warning(f"Invalid retention_days format for item {item.get('_context_id', 'unknown')}: {retention_days}")
        except AttributeError:
            logger.warning("_get_all_data_items method not found on adapter. Cannot check retention policy compliance.")
            return {"summary": summary, "overdue_items_details": []}
        except Exception as e:
            logger.error(f"Error checking retention policy compliance: {e}")
            return {"summary": summary, "overdue_items_details": []}
        
        return {"summary": summary, "overdue_items_details": non_compliant_items}

    def get_anonymization_effectiveness(self) -> Dict[str, Any]:
        """
        Placeholder for assessing anonymization effectiveness.
        This is a simplified check: counts items marked as high/critical sensitivity
        that still report a non-zero number of sensitive terms found.
        A more sophisticated check would involve comparing original vs. anonymized data.

        Returns:
            A dictionary with a summary of the check.
        """
        high_sensitivity_with_terms = 0
        total_high_sensitivity_items = 0
        effectiveness_score = 1.0 # Default to 100% effective if no relevant items

        try:
            all_items = self.memory_adapter._get_all_data_items()
            for item in all_items:
                metadata = item.get('_metadata', {})
                sensitivity = metadata.get('sensitivity_level', '').upper()
                sensitive_terms_found = item.get('sensitive_terms_found', 0)

                if sensitivity in ['HIGH', 'CRITICAL']:
                    total_high_sensitivity_items += 1
                    if sensitive_terms_found > 0:
                        high_sensitivity_with_terms += 1
            
            if total_high_sensitivity_items > 0:
                effectiveness_score = 1.0 - (high_sensitivity_with_terms / total_high_sensitivity_items)
            else:
                effectiveness_score = 1.0 # No high/critical items to check against

        except AttributeError:
            logger.warning("_get_all_data_items method not found on adapter. Cannot assess anonymization effectiveness.")
            return {"status": "Error", "message": "Adapter method missing"}
        except Exception as e:
            logger.error(f"Error assessing anonymization effectiveness: {e}")
            return {"status": "Error", "message": str(e)}

        return {
            "total_high_critical_sensitivity_items_checked": total_high_sensitivity_items,
            "items_with_remaining_sensitive_terms": high_sensitivity_with_terms,
            "anonymization_effectiveness_score": f"{effectiveness_score:.2%}",
            "target_effectiveness_threshold": f"{self.config.get('anonymization_effectiveness_threshold', 0.95):.2%}",
            "passes_threshold": effectiveness_score >= self.config.get('anonymization_effectiveness_threshold', 0.95)
        }

    def get_items_with_missing_metadata(self) -> Dict[str, List[str]]:
        """
        Finds items lacking crucial metadata fields like 'sensitivity_level' or 'retention_days'.

        Returns:
            A dictionary mapping metadata_field_name to a list of context_ids with missing data.
        """
        missing_data: Dict[str, List[str]] = {
            'missing_sensitivity_level': [],
            'missing_retention_days': []
        }
        checked_items = 0
        try:
            all_items = self.memory_adapter._get_all_data_items()
            checked_items = len(all_items)
            for item in all_items:
                context_id = item.get('_context_id', 'unknown_context_id')
                metadata = item.get('_metadata', {})
                if not metadata.get('sensitivity_level'):
                    missing_data['missing_sensitivity_level'].append(context_id)
                if metadata.get('retention_days') is None: # Check for None specifically
                    missing_data['missing_retention_days'].append(context_id)
        except AttributeError:
            logger.warning("_get_all_data_items method not found on adapter. Cannot check for missing metadata.")
            return {"error": "Adapter method missing", "checked_items": 0}
        except Exception as e:
            logger.error(f"Error checking for missing metadata: {e}")
            return {"error": str(e), "checked_items": 0}
        
        return {
            "summary": {
                "total_items_checked": checked_items,
                "items_missing_sensitivity_level": len(missing_data['missing_sensitivity_level']),
                "items_missing_retention_days": len(missing_data['missing_retention_days'])
            },
            "details": missing_data # Optionally, can truncate details if too long for report
        }

    def generate_privacy_compliance_report_section(self) -> str:
        """
        Generates a report section summarizing privacy compliance checks.

        Returns:
            A string containing the formatted privacy compliance report section.
        """
        retention_check = self.check_retention_policy_compliance()
        anonymization_check = self.get_anonymization_effectiveness()
        missing_metadata_check = self.get_items_with_missing_metadata()

        report_data = {
            "retention_policy_compliance_summary": json.dumps(retention_check.get('summary', {}), indent=2),
            "potentially_overdue_item_count": retention_check.get('summary', {}).get('potentially_overdue_items', 0),
            # Optionally include details of overdue items if not too many
            # "overdue_items_sample": json.dumps(retention_check.get('overdue_items_details', [])[:5], indent=2),
            "anonymization_effectiveness": json.dumps(anonymization_check, indent=2),
            "missing_metadata_summary": json.dumps(missing_metadata_check.get('summary', {}), indent=2),
            # Optionally include details of items with missing metadata
            # "items_missing_sensitivity_sample": json.dumps(missing_metadata_check.get('details', {}).get('missing_sensitivity_level', [])[:5], indent=2)
        }
        return self._format_report_section("Privacy Compliance Monitoring", report_data)


    # --- Diagnostic Utilities --- #

    def check_adapter_connectivity(self) -> bool:
        """
        Performs a basic check to see if the memory adapter is responsive.
        Tries to call a simple, low-impact method on the adapter.

        Returns:
            True if the adapter appears responsive, False otherwise.
        """
        try:
            # Attempt to call a lightweight method, e.g., listing users or a dedicated status method
            # For the mock adapter, get_all_users is suitable.
            # A real adapter might have a specific health check endpoint or method.
            self.memory_adapter.get_all_users() 
            logger.info("Memory adapter connectivity check: PASSED")
            return True
        except AttributeError:
            logger.warning("Adapter does not have 'get_all_users' method for connectivity check.")
            # Try another common method if one exists, or assume failure for this basic check
            return False # Or raise an error, or try another method
        except Exception as e:
            logger.error(f"Memory adapter connectivity check: FAILED. Error: {e}")
            return False

    def get_data_store_age_span(self) -> Dict[str, Optional[str]]:
        """
        Finds the timestamps of the oldest and newest items in the memory store.

        Returns:
            A dictionary with 'oldest_item_timestamp' and 'newest_item_timestamp'.
            Timestamps are in ISO format. Returns None if no items or timestamps found.
        """
        oldest_ts: Optional[datetime] = None
        newest_ts: Optional[datetime] = None
        items_processed = 0

        try:
            all_items = self.memory_adapter._get_all_data_items()
            if not all_items:
                return {"oldest_item_timestamp": None, "newest_item_timestamp": None, "items_processed": 0}

            for item in all_items:
                items_processed +=1
                item_timestamp_str = item.get('timestamp')
                if item_timestamp_str:
                    try:
                        current_item_ts = datetime.fromisoformat(item_timestamp_str)
                        # Ensure tz-aware comparison if one is tz-aware
                        if oldest_ts and oldest_ts.tzinfo and not current_item_ts.tzinfo:
                            current_item_ts = current_item_ts.replace(tzinfo=oldest_ts.tzinfo)
                        elif newest_ts and newest_ts.tzinfo and not current_item_ts.tzinfo:
                             current_item_ts = current_item_ts.replace(tzinfo=newest_ts.tzinfo)

                        if oldest_ts is None or current_item_ts < oldest_ts:
                            oldest_ts = current_item_ts
                        if newest_ts is None or current_item_ts > newest_ts:
                            newest_ts = current_item_ts
                    except ValueError:
                        logger.warning(f"Could not parse timestamp '{item_timestamp_str}' for item {item.get('_context_id', 'unknown')}.")
        except AttributeError:
            logger.warning("_get_all_data_items method not found on adapter. Cannot determine data store age span.")
            return {"oldest_item_timestamp": None, "newest_item_timestamp": None, "items_processed": 0, "error": "Adapter method missing"}
        except Exception as e:
            logger.error(f"Error determining data store age span: {e}")
            return {"oldest_item_timestamp": None, "newest_item_timestamp": None, "items_processed": 0, "error": str(e)}

        return {
            "oldest_item_timestamp": oldest_ts.isoformat() if oldest_ts else None,
            "newest_item_timestamp": newest_ts.isoformat() if newest_ts else None,
            "items_processed": items_processed
        }

    def perform_basic_health_check(self) -> Dict[str, Any]:
        """
        Performs a basic health check of the memory system.
        This can be expanded with more specific checks.

        Returns:
            A dictionary containing health check results.
        """
        health_status: Dict[str, Any] = {}
        health_status['adapter_connectivity'] = self.check_adapter_connectivity()
        
        total_size_gb = self.get_total_storage_size(unit='gb')
        health_status['total_storage_size_gb'] = f"{total_size_gb:.4f}"
        
        storage_threshold_gb = self.config.get('storage_usage_threshold_gb', 10)
        health_status['storage_usage_threshold_gb'] = storage_threshold_gb
        health_status['storage_within_threshold'] = total_size_gb < storage_threshold_gb

        age_span = self.get_data_store_age_span()
        health_status['data_store_age_span'] = age_span

        # Overall status based on checks
        if health_status['adapter_connectivity'] and health_status['storage_within_threshold']:
            health_status['overall_status'] = 'HEALTHY'
        else:
            health_status['overall_status'] = 'WARNING' # Or 'UNHEALTHY' if critical failures
            issues = []
            if not health_status['adapter_connectivity']: issues.append("Adapter connectivity failed.")
            if not health_status['storage_within_threshold']: issues.append("Storage usage exceeds threshold.")
            health_status['issues_detected'] = issues

        return health_status

    def generate_diagnostic_report_section(self) -> str:
        """
        Generates a report section summarizing diagnostic checks.

        Returns:
            A string containing the formatted diagnostic report section.
        """
        health_check_results = self.perform_basic_health_check()
        report_data = {
            "overall_health_status": health_check_results.get('overall_status', 'UNKNOWN'),
            "adapter_connectivity": health_check_results.get('adapter_connectivity', False),
            "total_storage_size_gb": health_check_results.get('total_storage_size_gb', 'N/A'),
            "storage_usage_threshold_gb": health_check_results.get('storage_usage_threshold_gb', 'N/A'),
            "storage_within_threshold": health_check_results.get('storage_within_threshold', False),
            "data_store_age_span": json.dumps(health_check_results.get('data_store_age_span', {}), indent=2),
        }
        if 'issues_detected' in health_check_results:
            report_data['issues_detected'] = ", ".join(health_check_results['issues_detected'])
            
        return self._format_report_section("Diagnostic Utilities", report_data)


    # --- Reporting --- #

    def generate_full_system_report(self) -> str:
        """
        Generates a comprehensive system health report by combining all sections.

        Returns:
            A string containing the full system report.
        """
        report_content = self._generate_report_header("ATRiAN Memory System Full Report")
        
        report_content += self.generate_memory_usage_report_section()
        report_content += "\n" + "-" * 50 + "\n" # Separator
        
        report_content += self.generate_privacy_compliance_report_section()
        report_content += "\n" + "-" * 50 + "\n" # Separator
        
        report_content += self.generate_diagnostic_report_section()
        
        self.last_report_time = datetime.now().astimezone()
        logger.info("Full system report generated.")
        return report_content

    def schedule_periodic_report(self):
        """
        Placeholder for scheduling periodic report generation.
        In a real system, this might use a cron job, a scheduler library (like APScheduler),
        or be triggered by an external system.
        """
        logger.info("Periodic report scheduling is a placeholder. Call generate_full_system_report() manually or integrate with a scheduler.")
        # Example: print(f"Next report would be due around: {datetime.now() + timedelta(hours=self.config.get('report_interval_hours', 24))}")


    def _generate_report_header(self, report_title: str) -> str:
        """
        Generates a standardized report header.
        """
        now = datetime.now().astimezone()
        header = f"""\
        # {report_title}
        --------------------------------------------------
        Report Generated: {now.strftime(EGOS_TIMESTAMP_FORMAT)}
        Monitor Version: {EGOS_VERSION}
        --------------------------------------------------
        """
        return header

    def _format_report_section(self, title: str, data: Dict[str, Any]) -> str:
        """
        Formats a section of a report.
        """
        section_content = f"\n## {title}\n"
        if not data:
            section_content += "No data available for this section.\n"
        else:
            for key, value in data.items():
                section_content += f"- {key.replace('_', ' ').title()}: {value}\n"
        return section_content


if __name__ == '__main__':
    # This section is for demonstration and basic testing.
    # In a real deployment, the monitor would be integrated into the ATRiAN system.

    logger.info(f"ATRiAN Memory System Monitor - Version {EGOS_VERSION}")
    logger.info(f"Authored by: {EGOS_AUTHOR}")

    # --- Mocking dependencies for standalone execution --- #
    class MockMemoryAdapter:
        def __init__(self):
            self._storage: Dict[str, Dict[str, Any]] = {}
            self._metadata_storage: Dict[str, Dict[str, Any]] = {}
            logger.info("MockMemoryAdapter initialized for testing.")

        def list_contexts(self, user_id: str) -> List[str]:
            return list(self._storage.get(user_id, {}).keys())

        def get_context_metadata(self, user_id: str, context_id: str) -> Optional[Dict[str, Any]]:
            return self._metadata_storage.get(user_id, {}).get(context_id)

        def get_all_users(self) -> List[str]:
            return list(self._storage.keys())

        def get_all_data_for_user(self, user_id: str) -> List[Dict[str, Any]]:
            user_data = []
            if user_id in self._storage:
                for context_id, data_item in self._storage[user_id].items():
                    metadata = self.get_context_metadata(user_id, context_id) or {}
                    item_with_metadata = {**data_item, "_metadata": metadata, "_context_id": context_id}
                    user_data.append(item_with_metadata)
            return user_data

        def _get_all_data_items(self) -> List[Dict[str, Any]]:
            all_items = []
            for user_id in self.get_all_users():
                all_items.extend(self.get_all_data_for_user(user_id))
            return all_items

    # Example usage (requires a memory adapter instance)
    mock_adapter = MockMemoryAdapter()

    # Simulate some data in the mock adapter
    mock_adapter._storage['user123'] = {
        'context_alpha': {'operation_type': 'file_edit', 'timestamp': (datetime.now() - timedelta(days=1)).isoformat(), 'size_bytes': 1024, 'sensitive_terms_found': 2},
        'context_beta': {'operation_type': 'search', 'timestamp': (datetime.now() - timedelta(days=2)).isoformat(), 'size_bytes': 512, 'sensitive_terms_found': 0}
    }
    mock_adapter._metadata_storage['user123'] = {
        'context_alpha': {'sensitivity_level': 'HIGH', 'retention_days': 30},
        'context_beta': {'sensitivity_level': 'LOW', 'retention_days': 365}
    }
    mock_adapter._storage['user456'] = {
        'context_gamma': {'operation_type': 'file_read', 'timestamp': (datetime.now() - timedelta(days=5)).isoformat(), 'size_bytes': 2048, 'sensitive_terms_found': 1}
    }
    mock_adapter._metadata_storage['user456'] = {
        'context_gamma': {'sensitivity_level': 'MEDIUM', 'retention_days': 90}
    }

    monitor = MemorySystemMonitor(memory_adapter=mock_adapter)

    print("\n--- Monitor Status ---")
    status = monitor.get_status()
    for k, v in status.items():
        print(f"{k}: {v}")

    print("\n--- Generating Full System Report ---")
    try:
        full_report = monitor.generate_full_system_report()
        print(full_report)

        # Example of saving the report to a file
        report_filename = f"ATRiAN_Memory_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        # Ensure reports directory exists (basic example, consider proper path management)
        reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        report_filepath = os.path.join(reports_dir, report_filename)
        
        with open(report_filepath, 'w', encoding='utf-8') as f:
            f.write(full_report)
        logger.info(f"Full system report saved to: {report_filepath}")

    except Exception as e:
        logger.error(f"Error during full report generation or saving: {e}", exc_info=True)

    monitor.schedule_periodic_report() # Demonstrate placeholder

    logger.info("MemorySystemMonitor demonstration finished.")