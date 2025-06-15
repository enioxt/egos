# @references:
#   - ATRIAN/templates/tests/test_constitution_validator.py
# 
import sys
from pathlib import Path
# Adiciona o diretório raiz do projeto (C:\EGOS) ao sys.path
# para permitir importações de 'ATRIAN' como um pacote de nível superior
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import unittest
import os
import yaml
import json
import logging
import shutil
from datetime import datetime

# --- Configure enhanced verbose logging for tests ---
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('validator_test_debug.log', mode='a', encoding='utf-8')
    ]
)
logger = logging.getLogger('TestRunner')
logger.debug('Logging configured for Constitution Validator tests with enhanced diagnostics')

# Add a custom test result class for better error reporting
class DetailedTestResult(unittest.TextTestResult):
    def addError(self, test, err):
        super().addError(test, err)
        self._log_test_failure(test, err, "ERROR")
        
    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._log_test_failure(test, err, "FAILURE")
        
    def _log_test_failure(self, test, err, failure_type):
        import traceback
        err_type, err_value, err_traceback = err
        logger.error(f"\n{'='*80}\n{failure_type} in {test.id()}\n{'='*80}")
        logger.error(f"Error type: {err_type.__name__}")
        logger.error(f"Error message: {err_value}")
        
        # Get the traceback as a string
        tb_str = ''.join(traceback.format_tb(err_traceback))
        logger.error(f"Traceback:\n{tb_str}")
        
        # Add context information if available
        if hasattr(test, 'validator'):
            logger.error(f"Test validator configuration: {test.validator.__dict__}")
        
        logger.error(f"{'='*80}\nEnd of {failure_type} report\n{'='*80}\n")

# Import the validator module
from ATRIAN.templates.constitution_validator import EthicalConstitutionValidator, ConstitutionValidationResult, generate_validation_report, ValidationLogLevel
from ATRIAN.templates.base.ethical_constitution_schema import EthicalRule, SeverityLevel # Import for direct testing
# Note: The Pydantic models like EthicalRule, EthicalPrinciple are imported by EthicalConstitutionValidator itself.

class TestConstitutionValidator(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory and mock constitution files for testing."""
        self.test_dir = Path("temp_test_constitutions_validator") # Using Path object
        os.makedirs(self.test_dir, exist_ok=True)

        # --- Mock Constitution Files ---
        # IMPORTANT: The structure of this mock data (especially for rules) needs to
        # align with the Pydantic models defined in 'ethical_constitution_schema.py'
        # (e.g., EthicalRule uses 'id', 'principle_ids', 'trigger_keywords', 'recommendations' (list), 'severity_override')
        # and how 'EthicalConstitutionValidator._load_constitution' parses them.
        # Discrepancies here are a likely source of test errors/failures.

        # 1. Base Constitution
        self.base_constitution_path = self.test_dir / "base_test.yaml"
        self.base_data = {
            'id': 'base_test_v1',
            'name': 'BaseTestConstitution',
            'description': 'A base test constitution.',
            'metadata': { # Matches ConstitutionMetadata
                'version': '1.0',
                'created_date': datetime.now().isoformat(),
                'author': 'Test Author',
                'purpose': 'Testing base functionality',
                'applicable_domains': ['general_test'],
                'tags': ['base', 'test'],
                'parent_constitutions': [],
                'regulatory_alignment': []
            },
            'principles': [{ # Matches EthicalPrinciple
                'id': 'P001', 
                'name': 'Safety', 
                'description': 'Do no harm.', 
                'severity': 'high' 
            }],
            'rules': [{ # Needs to match EthicalRule
                'id': 'R001_Base', # Changed 'name' to 'id'
                'principle_ids': ['P001'],
                'description': 'Avoid harmful content.',
                'trigger_keywords': ['harm', 'danger'],
                'recommendations': ['Review for safety.'],
                'severity_override': 'medium' # Corresponds to 'type' used in validator logic
            }]
        }
        with open(self.base_constitution_path, 'w') as f:
            yaml.dump(self.base_data, f)

        # 2. Sectorial Constitution with a critical rule and inheritance
        self.sectorial_constitution_path = self.test_dir / "sectorial_test.yaml"
        self.sectorial_data = {
            'id': 'sectorial_test_v1',
            'name': 'SectorialTestConstitution',
            'description': 'A sectorial test constitution.',
            'metadata': { # Matches ConstitutionMetadata
                'version': '1.0',
                'created_date': datetime.now().isoformat(),
                'author': 'Test Author',
                'purpose': 'Testing sectorial functionality with inheritance',
                'applicable_domains': ['finance_test'],
                'tags': ['sectorial', 'test', 'finance'],
                'parent_constitutions': [str(self.base_constitution_path.resolve())], # 'extends' used in validator, schema uses 'parent_constitutions' in metadata
                'regulatory_alignment': ['FINRA_Test_Rule']
            },
            'extends': [str(self.base_constitution_path.resolve())], # The validator's _load_constitution uses 'extends'
            'principles': [{ # Matches EthicalPrinciple
                'id': 'P002', 
                'name': 'Confidentiality', 
                'description': 'Protect private info.', 
                'severity': 'critical'
            }],
            'rules': [{ # Needs to match EthicalRule
                'id': 'R002_Sectorial', # Changed 'name' to 'id'
                'principle_ids': ['P002'],
                'description': 'Do not request Personally Identifiable Information.',
                'trigger_keywords': ['password', 'social security number'],
                'recommendations': ['CRITICAL: Remove request for PII.'],
                'severity_override': 'critical' # Corresponds to 'type' used in validator logic
            }]
        }
        with open(self.sectorial_constitution_path, 'w') as f:
            yaml.dump(self.sectorial_data, f)
        
        self.validator = EthicalConstitutionValidator(constitutions_dir=str(self.test_dir))

        # ---- START ISOLATION TEST FOR EthicalRule ----
        sys.stderr.write("\nDEBUG: Attempting to create EthicalRule directly from mock data...\n")
        first_rule_data_base = self.base_data['rules'][0]
        sys.stderr.write(f"DEBUG: Mock rule data: {first_rule_data_base}\n")
        try:
            EthicalRule(**first_rule_data_base)
            sys.stderr.write("DEBUG: EthicalRule created successfully from base_data['rules'][0].\n")
        except Exception as e:
            sys.stderr.write(f"DEBUG: FAILED to create EthicalRule from base_data['rules'][0]. Error: {e}\n")
        # ---- END ISOLATION TEST ----

    def tearDown(self):
        """Remove the temporary directory and its contents after tests."""
        # Close all logging file handlers to release file locks before rmtree
        # This is crucial on Windows to prevent PermissionError
        # Iterate over handlers of the root logger, as basicConfig adds to it.
        log = logging.getLogger() # root logger
        for hdlr in log.handlers[:]: # Iterate over a copy
            if isinstance(hdlr, logging.FileHandler):
                try:
                    hdlr.close()
                    log.removeHandler(hdlr)
                except Exception as e:
                    # Log this minor error, but don't let it stop teardown
                    print(f"LOG_WARNING: Error closing/removing root logger handler in tearDown: {e}")
        
        # If the validator itself (or other components) added specific file handlers
        # to their own named loggers without relying on root propagation,
        # those would also need to be closed.
        if hasattr(self, 'validator') and self.validator and hasattr(self.validator, '__class__') and hasattr(self.validator.__class__, '__name__'):
            validator_specific_logger_name = self.validator.__class__.__name__
            validator_specific_logger = logging.getLogger(validator_specific_logger_name)
            for h in validator_specific_logger.handlers[:]:
                if isinstance(h, logging.FileHandler):
                    try:
                        h.close()
                        validator_specific_logger.removeHandler(h)
                    except Exception as e:
                        print(f"LOG_WARNING: Error closing/removing validator logger handler in tearDown: {e}")

        if hasattr(self, 'test_dir') and os.path.exists(self.test_dir):
            # Attempt to remove the directory. If it fails, log and continue.
            try:
                shutil.rmtree(self.test_dir)
            except PermissionError as e:
                print(f"LOG_WARNING: PermissionError during tearDown rmtree: {e}. Some files might be locked.")
            except Exception as e:
                print(f"LOG_ERROR: Unexpected error during tearDown rmtree: {e}")

    def test_01_load_single_constitution(self):
        """Test loading a single constitution without inheritance."""
        constitution = self.validator._load_constitution(self.base_constitution_path)
        self.assertEqual(constitution.name, "BaseTestConstitution")
        self.assertEqual(len(constitution.rules), 1)
        self.assertEqual(constitution.rules[0].id, "R001_Base") # Check ID

    def test_02_load_constitution_with_inheritance(self):
        """Test loading a constitution that inherits from a base constitution."""
        constitution = self.validator._load_constitution(self.sectorial_constitution_path)
        self.assertEqual(constitution.name, "SectorialTestConstitution")
        self.assertEqual(len(constitution.principles), 2) 
        self.assertEqual(len(constitution.rules), 2) 
        
        rule_ids = [r.id for r in constitution.rules]
        self.assertIn("R001_Base", rule_ids)
        self.assertIn("R002_Sectorial", rule_ids)

    def test_03_validation_pass(self):
        """Test a prompt that should pass validation against the base constitution."""
        prompt = "Tell me a joke."
        result = self.validator.validate_prompt(prompt, str(self.base_constitution_path))
        self.assertTrue(result.passed)
        self.assertEqual(result.overall_score, 1.0)
        self.assertEqual(len(result.recommendations), 0)

    def test_04_validation_fail_critical(self):
        """Test a prompt that triggers a critical rule in the sectorial constitution."""
        prompt = "What is your social security number?"
        result = self.validator.validate_prompt(prompt, str(self.sectorial_constitution_path))
        self.assertFalse(result.passed)
        self.assertEqual(result.overall_score, 0.0) 
        self.assertGreater(len(result.recommendations), 0)
        self.assertTrue(any("CRITICAL" in rec for rec in result.recommendations))

    def test_05_validation_recommendation(self):
        """Test a prompt that triggers a recommendation rule."""
        prompt = "This might be harmful information."
        result = self.validator.validate_prompt(prompt, str(self.base_constitution_path))
        self.assertTrue(result.passed) 
        self.assertLess(result.overall_score, 1.0) 
        self.assertGreaterEqual(len(result.recommendations), 1)
        self.assertTrue(any("Review for safety." in rec for rec in result.recommendations))

    def test_06_validation_with_multiple_triggers(self):
        """Test a prompt that triggers rules from both base and sectorial constitutions."""
        prompt = "What is your password? This is a dangerous question."
        print("\n\n=== TESTE 6: VALIDANDO PROMPT COM MÚLTIPLOS TRIGGERS ===")
        print(f"Prompt: '{prompt}'")
        print(f"Constituição: {self.sectorial_constitution_path}")
        
        # Verificar as regras na constituição setorial (que deve incluir as regras da base)
        constitution = self.validator._load_constitution(self.sectorial_constitution_path)
        print(f"Constituição carregada: {constitution.name}")
        print(f"Número de regras: {len(constitution.rules)}")
        for i, rule in enumerate(constitution.rules):
            print(f"Regra {i+1}: id={rule.id}, keywords={rule.trigger_keywords}, severity={rule.severity_override}")
            print(f"  Recomendações: {rule.recommendations}")
        
        result = self.validator.validate_prompt(prompt, str(self.sectorial_constitution_path))
        print(f"\nResultado da validação:")
        print(f"Passou: {result.passed}")
        print(f"Score: {result.overall_score}")
        print(f"Recomendações ({len(result.recommendations)}): {result.recommendations}")
        
        self.assertFalse(result.passed) 
        self.assertEqual(result.overall_score, 0.0) 
        
        self.assertGreaterEqual(len(result.recommendations), 2)
        self.assertTrue(any("CRITICAL" in rec for rec in result.recommendations))
        self.assertTrue(any("Review for safety" in rec for rec in result.recommendations))

#    def test_07_aggregate_results(self):
#        """Test the aggregation of multiple ConstitutionValidationResult objects."""
#        result1 = ConstitutionValidationResult(constitution_id="const1", constitution_name="Constitution 1")
#        result1.passed = True
#        result1.overall_score = 0.8
#        result1.recommendations = ['Rec 1']
#
#        result2 = ConstitutionValidationResult(constitution_id="const2", constitution_name="Constitution 2")
#        result2.passed = False
#        result2.overall_score = 0.0
#        result2.recommendations = ['Critical 2']
#        result2.critical_failures = ['Rule X']
#
#
#        result3 = ConstitutionValidationResult(constitution_id="const3", constitution_name="Constitution 3")
#        result3.passed = True
#        result3.overall_score = 0.9
#        result3.recommendations = ['Rec 3']
#
#        aggregated_dict = aggregate_results([result1, result2, result3])
#        
#        self.assertFalse(aggregated_dict['passed']) 
#        self.assertEqual(aggregated_dict['overall_score'], 0.0) 
#        
#        self.assertEqual(len(aggregated_dict['recommendations']), 3)
#        self.assertIn('Rec 1', aggregated_dict['recommendations'])
#        self.assertIn('Critical 2', aggregated_dict['recommendations'])
#        self.assertIn('Rec 3', aggregated_dict['recommendations'])
#        
#        self.assertIn("Constitution 1", aggregated_dict['details_by_constitution'])
#        self.assertEqual(aggregated_dict['details_by_constitution']["Constitution 1"]['overall_score'], 0.8)


    def test_08_empty_prompt(self):
        """Test that an empty prompt passes validation."""
        prompt = ""
        result = self.validator.validate_prompt(prompt, str(self.base_constitution_path))
        self.assertTrue(result.passed)
        self.assertEqual(result.overall_score, 1.0)
        
    def test_09_validate_prompts_multi_constitution(self):
        """Test validating a prompt against multiple constitutions."""
        prompt = "What is your password? This is a test."
        constitution_paths = [str(self.base_constitution_path), str(self.sectorial_constitution_path)]
        
        print("\n\n=== TEST 9: VALIDATING AGAINST MULTIPLE CONSTITUTIONS ===")
        print(f"Prompt: '{prompt}'")
        print(f"Constitutions: {constitution_paths}")
        
        # Test with standard logging level
        result_dict = self.validator.validate_prompts(prompt, constitution_paths, log_level=ValidationLogLevel.STANDARD)
        
        # Verify the structure and content of the result
        self.assertIn('validation_id', result_dict)
        self.assertIn('timestamp', result_dict)
        self.assertIn('passed', result_dict)
        self.assertIn('overall_score', result_dict)
        self.assertIn('combined_recommendations', result_dict)
        self.assertIn('combined_critical_failures', result_dict) # Updated key for multi-constitution results
        self.assertIn('constitution_results', result_dict)
        self.assertIn('metrics', result_dict)
        
        # Verify metrics
        self.assertEqual(result_dict['metrics']['total_constitutions'], 2)
        
        # Verify that we have results for both constitutions
        self.assertEqual(len(result_dict['constitution_results']), 2)
        
        # Verify that the password rule was triggered (from sectorial constitution)
        self.assertFalse(result_dict['passed'])
        self.assertEqual(result_dict['overall_score'], 0.0)
        self.assertTrue(any('pii' in rec.lower() for rec in result_dict['combined_recommendations'])) # Check for 'pii' in recommendation
        
        print(f"\nValidation Result Summary:")
        print(f"Passed: {result_dict['passed']}")
        print(f"Overall Score: {result_dict['overall_score']}")
        print(f"Total Constitutions: {result_dict['metrics']['total_constitutions']}")
        print(f"Total Rules Checked: {result_dict['metrics']['total_rules_checked']}")
        print(f"Rules Triggered: {result_dict['metrics']['rules_triggered_count']}")
        
    def test_10_validation_with_verbose_logging(self):
        """Test validation with different logging levels."""
        print("\n\n=== TEST 10: VALIDATION WITH VERBOSE LOGGING (DEBUGGING) ===")
        
        try:
            # Create a custom validator with a mock rule that will definitely trigger
            validator = EthicalConstitutionValidator(constitutions_dir=str(self.test_dir))
            print("✓ Created validator successfully")
            
            # Create a test prompt that will trigger the 'danger' keyword in our mock rule
            prompt = "This is a dangerous test."
            print(f"✓ Test prompt: '{prompt}'")
            
            # First, let's manually create a mock constitution with a rule that will trigger
            mock_const_path = self.test_dir / "verbose_test.yaml"
            mock_const_data = {
                'id': 'verbose_test_v1',
                'name': 'VerboseTestConstitution',
                'description': 'A test constitution for verbose logging.',
                'metadata': {
                    'version': '1.0',
                    'created_date': datetime.now(),
                    'author': 'Test Author',
                    'purpose': 'Testing verbose logging',
                    'applicable_domains': ['test_domain'],
                    'tags': ['test', 'verbose'],
                    'parent_constitutions': [],
                    'regulatory_alignment': []
                },
                'principles': [{
                    'id': 'P001', 
                    'name': 'Safety', 
                    'description': 'Do no harm.', 
                    'severity': 'high'
                }],
                'rules': [{
                    'id': 'R001_Verbose',
                    'principle_ids': ['P001'],
                    'description': 'Detects dangerous content.',
                    'trigger_keywords': ['danger'],
                    'recommendations': ['Avoid dangerous content.'],
                    'severity_override': 'medium'
                }]
            }
            
            with open(mock_const_path, 'w') as f:
                yaml.dump(mock_const_data, f)
            print(f"✓ Created mock constitution at {mock_const_path}")
            
            # Test with VERBOSE logging
            print("Now calling validate_prompt()...")
            result = validator.validate_prompt(
                prompt, 
                str(mock_const_path), 
                log_level=ValidationLogLevel.VERBOSE
            )
            print("✓ Validation completed successfully")
            
            # Print detailed result info for diagnostics
            print(f"\nDETAILED RESULT DIAGNOSTICS:")
            print(f"Result type: {type(result)}")
            print(f"Result passed: {result.passed} (type: {type(result.passed)})")
            print(f"Overall score: {result.overall_score}")
            print(f"Recommendations: {result.recommendations}")
            print(f"Rules triggered count: {result.rules_triggered_count}")
            print(f"Total rules checked: {result.total_rules_checked}")
            
            # Basic validation checks - the prompt should trigger the rule
            # For a non-critical trigger:
            self.assertTrue(result.passed, "Validation should pass for a non-critical trigger")
            self.assertEqual(result.rules_triggered_count, 1, "One rule should be triggered")
            self.assertLess(result.overall_score, 1.0, "Score should be reduced when rule is triggered")
            self.assertGreater(len(result.recommendations), 0, "There should be recommendations when rule is triggered")
            
            # Check that metrics were properly recorded
            self.assertTrue(hasattr(result, 'total_rules_checked'), "Result should have total_rules_checked attribute")
            self.assertTrue(hasattr(result, 'rules_triggered_count'), "Result should have rules_triggered_count attribute")
            self.assertTrue(hasattr(result, 'processing_time_ms'), "Result should have processing_time_ms attribute")
            
        except Exception as e:
            print(f"\n❌ ERROR DURING TEST: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            raise  # Re-raise the exception
            
        print(f"\nValidation Result with VERBOSE logging:")
        print(f"Passed: {result.passed}")
        print(f"Overall Score: {result.overall_score}")
        print(f"Processing Time: {result.processing_time_ms:.2f}ms")
        print(f"Rules Checked: {result.total_rules_checked}")
        print(f"Rules Triggered: {result.rules_triggered_count}")
        
    def test_11_generate_validation_report(self):
        """Test generating validation reports in different formats."""
        # Create a sample validation result dictionary
        validation_result = {
            "validation_id": "test-validation-123",
            "timestamp": datetime.now().isoformat(),
            "passed": False,
            "overall_score": 0.7,
            "recommendations": ["Recommendation 1", "Recommendation 2"],
            "critical_failures": ["Critical issue 1"],
            "metrics": {
                "total_constitutions": 2,
                "total_rules_checked": 10,
                "rules_triggered_count": 3,
                "processing_time_ms": 150.5,
                "rules_by_severity": {
                    "critical": 1,
                    "high": 1,
                    "medium": 1,
                    "low": 0
                }
            },
            "constitution_results": [
                {
                    "constitution_id": "const1",
                    "constitution_name": "Constitution 1",
                    "passed": True,
                    "overall_score": 0.9,
                    "metrics": {
                        "total_rules_checked": 5,
                        "rules_triggered_count": 1
                    }
                },
                {
                    "constitution_id": "const2",
                    "constitution_name": "Constitution 2",
                    "passed": False,
                    "overall_score": 0.7,
                    "metrics": {
                        "total_rules_checked": 5,
                        "rules_triggered_count": 2
                    }
                }
            ]
        }
        
        print("\n\n=== TEST 11: GENERATE VALIDATION REPORTS ===")
        
        # Test markdown format
        markdown_report = generate_validation_report(validation_result, format="markdown")
        self.assertIsInstance(markdown_report, str)
        self.assertIn("# ATRiAN Ethical Constitution Validation Report", markdown_report)
        self.assertIn("**Validation ID**: `test-validation-123`", markdown_report)
        self.assertIn("## Summary", markdown_report)
        self.assertIn("## Rules by Severity", markdown_report)
        self.assertIn("## Recommendations", markdown_report)
        self.assertIn("## Critical Issues", markdown_report)
        self.assertIn("## Constitution Details", markdown_report)
        
        print("\nMarkdown Report (excerpt):")
        print("\n".join(markdown_report.split("\n")[:10]) + "\n[...]")
        
        # Test text format
        text_report = generate_validation_report(validation_result, format="text")
        self.assertIsInstance(text_report, str)
        self.assertIn("ATRiAN ETHICAL CONSTITUTION VALIDATION REPORT", text_report)
        self.assertIn("Validation ID: test-validation-123", text_report)
        self.assertIn("RECOMMENDATIONS:", text_report)
        self.assertIn("CRITICAL ISSUES:", text_report)
        self.assertIn("CONSTITUTION DETAILS:", text_report)
        
        print("\nText Report (excerpt):")
        print("\n".join(text_report.split("\n")[:10]) + "\n[...]")
        
        # Test JSON format
        json_report = generate_validation_report(validation_result, format="json")
        self.assertIsInstance(json_report, str)
        # Verify it's valid JSON
        parsed_json = json.loads(json_report)
        self.assertEqual(parsed_json["validation_id"], "test-validation-123")
        self.assertEqual(parsed_json["overall_score"], 0.7)
        
        print("\nJSON Report validated successfully.")
        
    def test_12_finalize_validation_result(self):
        """Test the finalize method of ConstitutionValidationResult."""
        # Create a properly initialized validation result with all required attributes
        result = ConstitutionValidationResult(constitution_id="test-const", constitution_name="Test Constitution")
        result.passed = True
        result.overall_score = 0.9
        result.recommendations = ["Sample recommendation"]
        result.critical_failures = []
        result.warnings = []
        result.rule_results = []
        result.critical_rule_triggered = False
        result.total_rules_checked = 0
        result.rules_triggered_count = 0
        result.rules_by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0, "unknown": 0}
        result.validation_id = "test-validation-id"
        result.timestamp = datetime.now()
        result.start_timestamp = datetime.now()
        
        # Test prompt text with sensitive content
        prompt_text = "This is a test prompt with sensitive information: password123"
        
        # Finalize the result
        finalized_result = result.finalize(prompt_text)
        
        # Verify that metrics were added
        self.assertTrue(hasattr(finalized_result, 'prompt_length'))
        self.assertEqual(finalized_result.prompt_length, len(prompt_text))
        
        self.assertTrue(hasattr(finalized_result, 'prompt_hash'))
        self.assertIsNotNone(finalized_result.prompt_hash)
        self.assertNotEqual(finalized_result.prompt_hash, "")
        
        self.assertTrue(hasattr(finalized_result, 'processing_time_ms'))
        self.assertGreaterEqual(finalized_result.processing_time_ms, 0)
        
        # Verify that the prompt text itself is not stored
        self.assertFalse(hasattr(finalized_result, 'prompt_text'))
        
        print("\n\n=== TEST 12: FINALIZE VALIDATION RESULT ===")
        print(f"Prompt Length: {finalized_result.prompt_length}")
        print(f"Prompt Hash: {finalized_result.prompt_hash}")
        print(f"Processing Time: {finalized_result.processing_time_ms:.2f}ms")
        
        # Test to_dict method with metrics
        result_dict = finalized_result.to_dict()
        self.assertIn('metrics', result_dict)
        self.assertIn('prompt_length', result_dict['metrics'])
        self.assertIn('prompt_hash', result_dict['metrics'])
        self.assertIn('processing_time_ms', result_dict['metrics'])
        
        print(f"\nResult Dictionary Metrics:")
        for key, value in result_dict['metrics'].items():
            print(f"  {key}: {value}")


if __name__ == '__main__':
    # Logging is already configured by basicConfig at the top of the file
    # to go to 'validator_test_debug.log' and sys.stdout.

    # We want the unittest runner's output (failures, errors) to also go to 'validator_test_debug.log'.
    root_logger = logging.getLogger()
    file_handler_path = None
    for handler in root_logger.handlers:
        if isinstance(handler, logging.FileHandler):
            # Ensure we're getting the handler that writes to validator_test_debug.log
            if 'validator_test_debug.log' in handler.baseFilename:
                file_handler_path = handler.baseFilename
                break
    
    if file_handler_path:
        print(f"Unittest runner output will be appended to: {file_handler_path}")
        # Open the log file in append mode, as the logger has already written to it (mode='w')
        with open(file_handler_path, 'a', encoding='utf-8') as log_file_stream:
            # Add a very clear separator with timestamp
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            separator = f"\n{'#'*30} UNITTEST RUNNER OUTPUT START - {current_time} {'#'*30}\n"
            log_file_stream.write(separator)
            print(separator) # Also print to console for clarity during run
            
            # Create a custom test runner with our enhanced result class
            class DetailedTextTestRunner(unittest.TextTestRunner):
                def _makeResult(self):
                    return DetailedTestResult(self.stream, self.descriptions, self.verbosity)
            
            # Use our enhanced test runner
            runner = DetailedTextTestRunner(stream=log_file_stream, verbosity=2)
            logger.info("Running tests with enhanced error reporting and diagnostics")
            
            # unittest.main discovers tests in the current module by default.
            # We pass the runner to unittest.main.
            # Using exit=False prevents unittest.main from calling sys.exit()
            test_program = unittest.main(testRunner=runner, argv=[sys.argv[0]], exit=False)
            
            # Log test run summary
            result = test_program.result
            logger.info(f"Test run completed: {result.testsRun} tests run, {len(result.errors)} errors, {len(result.failures)} failures")
            
            # Add detailed summary of test results
            if result.errors or result.failures:
                logger.error("\nTest run had errors or failures. See above for detailed reports.")
            
            end_separator = f"\n{'='*50}\nUNITTEST RUNNER OUTPUT END - {current_time}\n{'='*50}\n"
            log_file_stream.write(end_separator)
            print(end_separator)
        print(f"Detailed unittest runner output appended to: {file_handler_path}")
    else:
        print("Could not find logger's file handler for 'validator_test_debug.log'. Running tests with default runner.")
        unittest.main(argv=[sys.argv[0]], exit=False)