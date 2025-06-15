# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# - [ATRiAN Integration Rules](../.windsurfrules_atrian_section)
# - [ATRiAN Implementation Plan](./ATRiAN_Implementation_Plan.md)
# - [EGOS Global Rules](../global_rules.md)
# --- 

import os
import json
import logging
from datetime import datetime
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("atrian_demo")

# Mock Windsurf operation types
class MockOperationType(Enum):
    FILE_CREATION = "file_creation"
    CODE_GENERATION = "code_generation"
    AUTHENTICATION = "authentication"
    SYSTEM_CONFIG = "system_config"

# Mock ATRiAN components
class MockEthicalCompass:
    """Simplified mock of the EthicalCompass class."""
    
    def evaluate_action(self, action_description, context=None):
        """Evaluate an action from an ethical perspective."""
        logger.info(f"Ethical evaluation for: {action_description}")
        
        # Check for privacy concerns
        privacy_keywords = ["personal", "sensitive", "password", "private"]
        contains_private = False
        
        if context:
            context_str = json.dumps(context).lower()
            for keyword in privacy_keywords:
                if keyword in context_str:
                    contains_private = True
                    break
        
        # Simple demonstration logic
        if "scrape" in action_description.lower() and "without consent" in action_description.lower():
            return {
                "allowed": False,
                "warnings": ["Ethical concern: Operating without user consent violates Sacred Privacy principles"],
                "guidance": "Consider obtaining explicit consent before collecting user data"
            }
        elif contains_private:
            return {
                "allowed": True,
                "warnings": ["Privacy-sensitive operation detected. Ensure proper data handling."],
                "guidance": "Implement data minimization and secure storage for sensitive information"
            }
        else:
            return {
                "allowed": True,
                "warnings": [],
                "guidance": "No specific ethical concerns detected"
            }

class MockTrustWeaver:
    """Simplified mock of the WeaverOfTrust class."""
    
    def __init__(self):
        self.trust_scores = {
            "DefaultUser": 0.7,
            "LowTrustUser": 0.3,
            "HighTrustUser": 0.9
        }
    
    def get_trust_score(self, agent_id):
        """Get the trust score for an agent."""
        return self.trust_scores.get(agent_id, 0.5)
    
    def update_trust_score(self, agent_id, event_type, outcome, magnitude, reason=None):
        """Update the trust score for an agent."""
        current_score = self.get_trust_score(agent_id)
        
        if outcome == "positive":
            new_score = min(1.0, current_score + magnitude)
        else:
            new_score = max(0.0, current_score - magnitude)
        
        self.trust_scores[agent_id] = new_score
        logger.info(f"Updated trust score for {agent_id}: {current_score:.2f} -> {new_score:.2f} ({reason})")

class MockWindsurfAdapter:
    """Simplified mock of the ATRiANWindsurfAdapter class."""
    
    def __init__(self):
        self.ethical_compass = MockEthicalCompass()
        self.trust_weaver = MockTrustWeaver()
        self.operations = {}
        self.notifications = []
    
    def evaluate_operation(self, operation_type, context, user_id="DefaultUser"):
        """Evaluate a Windsurf operation using ATRiAN components."""
        # Generate operation ID
        operation_id = f"{operation_type.value}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Map operation type to action description
        action_descriptions = {
            MockOperationType.FILE_CREATION: f"Creating file with potential {context.get('content_type', 'unknown')} content",
            MockOperationType.CODE_GENERATION: f"Generating code for {context.get('purpose', 'unknown purpose')}",
            MockOperationType.AUTHENTICATION: f"Performing authentication operation: {context.get('operation', 'unknown')}",
            MockOperationType.SYSTEM_CONFIG: f"Modifying system configuration: {context.get('component', 'unknown')}"
        }
        
        action_description = action_descriptions.get(operation_type, "Performing unknown operation")
        
        # Get ethical evaluation
        ethical_eval = self.ethical_compass.evaluate_action(action_description, context)
        
        # Get trust score
        trust_score = self.trust_weaver.get_trust_score(user_id)
        
        # Determine if notification is needed
        should_notify = (
            not ethical_eval.get("allowed", True) or
            len(ethical_eval.get("warnings", [])) > 0 or
            trust_score < 0.4
        )
        
        # Check for privacy concerns
        privacy_keywords = ["personal", "sensitive", "password", "private"]
        context_str = json.dumps(context).lower()
        detected_keywords = [kw for kw in privacy_keywords if kw in context_str]
        contains_sensitive_data = len(detected_keywords) > 0
        
        # Create operation record
        result = {
            "operation_id": operation_id,
            "user_id": user_id,
            "operation_type": operation_type.value,
            "timestamp": datetime.now().isoformat(),
            "allowed": ethical_eval.get("allowed", True) and trust_score >= 0.4,
            "ethical_evaluation": ethical_eval,
            "trust_score": trust_score,
            "should_notify": should_notify,
            "contains_sensitive_data": contains_sensitive_data,
            "detected_keywords": detected_keywords
        }
        
        # Store operation
        self.operations[operation_id] = result
        
        # Update trust based on operation
        if contains_sensitive_data and ethical_eval.get("allowed", True):
            self.trust_weaver.update_trust_score(
                user_id,
                "privacy_sensitive_operation",
                "positive" if ethical_eval.get("allowed", True) else "negative",
                0.05,
                "Proper handling of sensitive data" if ethical_eval.get("allowed", True) else "Privacy concern"
            )
        
        logger.info(f"Evaluated {operation_type.value} operation (ID: {operation_id})")
        logger.info(f"Result: allowed={result['allowed']}, should_notify={should_notify}")
        
        return result
    
    def generate_notification(self, operation_id):
        """Generate a notification for a previous operation."""
        if operation_id not in self.operations:
            return {"error": "Unknown operation ID"}
        
        operation = self.operations[operation_id]
        
        if not operation.get("should_notify", False):
            return {"notification_required": False}
        
        notification_type = "warning" if not operation.get("allowed", True) else "info"
        
        notification = {
            "notification_id": f"notification_{len(self.notifications) + 1}",
            "type": notification_type,
            "title": f"ATRiAN {notification_type.capitalize()}: {operation['operation_type']}",
            "message": operation["ethical_evaluation"].get("guidance", ""),
            "operation_id": operation_id,
            "timestamp": datetime.now().isoformat()
        }
        
        self.notifications.append(notification)
        logger.info(f"Generated {notification_type} notification for operation {operation_id}")
        
        return notification

def simulate_windsurf_integration():
    """Simulate the integration between Windsurf IDE and ATRiAN."""
    print("\n" + "="*50)
    print("ATRiAN Windsurf Integration Demonstration")
    print("="*50)
    
    # Create adapter
    adapter = MockWindsurfAdapter()
    
    # Scenario 1: Privacy-sensitive file creation
    print("\nScenario 1: Privacy-sensitive file creation")
    print("-" * 40)
    
    file_context = {
        "file_path": "/example/user_data.py",
        "content_type": "user data processing",
        "content": "def save_user_data(user_id, personal_info, password):\n    database.store(user_id, personal_info, password)",
    }
    
    result1 = adapter.evaluate_operation(MockOperationType.FILE_CREATION, file_context, "DefaultUser")
    
    print(f"Operation allowed: {result1['allowed']}")
    print(f"Should notify: {result1['should_notify']}")
    print(f"Contains sensitive data: {result1['contains_sensitive_data']}")
    print(f"Detected keywords: {result1['detected_keywords']}")
    
    if result1["should_notify"]:
        notification = adapter.generate_notification(result1["operation_id"])
        print(f"Notification: {notification['title']}")
        print(f"Message: {notification['message']}")
    
    # Scenario 2: Unethical code generation
    print("\nScenario 2: Unethical code generation")
    print("-" * 40)
    
    code_context = {
        "purpose": "scraping social media data without consent",
        "language": "python",
        "model": "data collection"
    }
    
    result2 = adapter.evaluate_operation(MockOperationType.CODE_GENERATION, code_context, "DefaultUser")
    
    print(f"Operation allowed: {result2['allowed']}")
    print(f"Should notify: {result2['should_notify']}")
    print(f"Ethical evaluation: {result2['ethical_evaluation']['guidance']}")
    
    if result2["should_notify"]:
        notification = adapter.generate_notification(result2["operation_id"])
        print(f"Notification: {notification['title']}")
        print(f"Message: {notification['message']}")
    
    # Scenario 3: Trust boundary testing
    print("\nScenario 3: Trust boundary testing")
    print("-" * 40)
    
    config_context = {
        "component": "security settings",
        "changes": {"disable_authentication": True},
        "reason": "testing"
    }
    
    result3 = adapter.evaluate_operation(MockOperationType.SYSTEM_CONFIG, config_context, "LowTrustUser")
    
    print(f"User trust score: {result3['trust_score']}")
    print(f"Operation allowed: {result3['allowed']}")
    print(f"Should notify: {result3['should_notify']}")
    
    if result3["should_notify"]:
        notification = adapter.generate_notification(result3["operation_id"])
        print(f"Notification: {notification['title']}")
        print(f"Message: {notification['message']}")
    
    print("\n" + "="*50)
    print("Integration Demonstration Complete")
    print("="*50)
    print("\n✧༺❀༻∞ EGOS ∞༺❀༻✧")

if __name__ == "__main__":
    simulate_windsurf_integration()