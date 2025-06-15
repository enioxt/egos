# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# - [ATRiAN Implementation Plan](./ATRiAN_Implementation_Plan.md)
# - [EGOS Global Rules](../.windsurfrules)
# - [Master Quantum Prompt (MQP.md)](../MQP.md)
# --- 

import unittest
import os
import yaml
import logging
import shutil
from atrian_trust_weaver import WeaverOfTrust, DEFAULT_INITIAL_TRUST, TRUST_SCORE_MIN, TRUST_SCORE_MAX

# Define the logger name for the module under test
logger_name = "atrian_trust_weaver"

# Suppress logging output during tests unless specifically testing logging
# logging.disable(logging.CRITICAL) # This will be handled per test or setUp

class TestWeaverOfTrust(unittest.TestCase):
    """
    Unit tests for the WeaverOfTrust class.
    """
    ATRIAN_TEMP_TEST_CONFIGS_DIR = "./atrian_temp_test_configs_dir"
    VALID_CONFIG_PATH = os.path.join(ATRIAN_TEMP_TEST_CONFIGS_DIR, "valid_trust_layer.yaml")
    EMPTY_CONFIG_PATH = os.path.join(ATRIAN_TEMP_TEST_CONFIGS_DIR, "empty_trust_layer.yaml")
    MALFORMED_CONFIG_PATH = os.path.join(ATRIAN_TEMP_TEST_CONFIGS_DIR, "malformed_trust_layer.yaml")
    NO_RULES_CONFIG_PATH = os.path.join(ATRIAN_TEMP_TEST_CONFIGS_DIR, "no_rules_trust_layer.yaml")
    TRULY_EMPTY_CONFIG_PATH = os.path.join(ATRIAN_TEMP_TEST_CONFIGS_DIR, "truly_empty_trust_layer.yaml")
    TRUST_RULES_NOT_LIST_CONFIG_PATH = os.path.join(ATRIAN_TEMP_TEST_CONFIGS_DIR, "trust_rules_not_list.yaml")
    RULE_NOT_DICT_CONFIG_PATH = os.path.join(ATRIAN_TEMP_TEST_CONFIGS_DIR, "rule_not_dict.yaml")
    RULE_MISSING_AGENT_CONFIG_PATH = os.path.join(ATRIAN_TEMP_TEST_CONFIGS_DIR, "rule_missing_agent.yaml")
    RULE_INVALID_AGENT_ID_CONFIG_PATH = os.path.join(ATRIAN_TEMP_TEST_CONFIGS_DIR, "rule_invalid_agent_id.yaml")
    RULE_UNRECOGNIZED_LEVEL_CONFIG_PATH = os.path.join(ATRIAN_TEMP_TEST_CONFIGS_DIR, "rule_unrecognized_level.yaml")
    RULE_NO_LEVEL_CONFIG_PATH = os.path.join(ATRIAN_TEMP_TEST_CONFIGS_DIR, "rule_no_level.yaml")

    @classmethod
    def setUpClass(cls):
        if os.path.exists(cls.ATRIAN_TEMP_TEST_CONFIGS_DIR):
            shutil.rmtree(cls.ATRIAN_TEMP_TEST_CONFIGS_DIR)
        os.makedirs(cls.ATRIAN_TEMP_TEST_CONFIGS_DIR, exist_ok=True)

        # Create a valid config file
        valid_config_data = {
            'trust_rules': [
                {'agent': 'AgentA', 'level': 'high', 'delegation': 'full', 'can_delegate_to': ['*']},
                {'agent': 'AgentB', 'level': 'medium', 'delegation': 'partial', 'can_delegate_to': ['AgentC']},
                {'agent': 'AgentC', 'level': 'low', 'delegation': 'none'},
                {'agent': 'SystemCriticalAgent', 'level': 'system_critical', 'delegation': 'full'}
            ]
        }
        with open(cls.VALID_CONFIG_PATH, 'w') as f:
            yaml.dump(valid_config_data, f)

        # Create an empty config file (no trust_rules key)
        with open(cls.EMPTY_CONFIG_PATH, 'w') as f:
            yaml.dump({}, f)
            
        # Create a config file with no rules list
        with open(cls.NO_RULES_CONFIG_PATH, 'w') as f:
            yaml.dump({'trust_rules': []}, f)

        # Create a malformed YAML config file
        with open(cls.MALFORMED_CONFIG_PATH, 'w') as f:
            f.write("trust_rules: [agent: AgentD, level: high : extra_colon_makes_it_malformed]")

        # Create a truly empty YAML file
        with open(cls.TRULY_EMPTY_CONFIG_PATH, 'w') as f:
            pass # File is created empty

        # Create config where 'trust_rules' is not a list
        with open(cls.TRUST_RULES_NOT_LIST_CONFIG_PATH, 'w') as f:
            yaml.dump({'trust_rules': 'this_is_not_a_list'}, f)

        # Create config where a rule in 'trust_rules' is not a dictionary
        with open(cls.RULE_NOT_DICT_CONFIG_PATH, 'w') as f:
            yaml.dump({'trust_rules': ['not_a_dict', {'agent': 'AgentE', 'level': 'medium'}]}, f)

        # Create config where a rule is missing the 'agent' key
        with open(cls.RULE_MISSING_AGENT_CONFIG_PATH, 'w') as f:
            yaml.dump({'trust_rules': [{'level': 'high'}]}, f)

        # Create config where a rule has an invalid 'agent' ID (e.g., not a string, or empty)
        with open(cls.RULE_INVALID_AGENT_ID_CONFIG_PATH, 'w') as f:
            yaml.dump({'trust_rules': [{'agent': 123, 'level': 'high'}, {'agent': '  ', 'level': 'low'}]}, f)

        # Create config where a rule has an unrecognized 'level'
        with open(cls.RULE_UNRECOGNIZED_LEVEL_CONFIG_PATH, 'w') as f:
            yaml.dump({'trust_rules': [{'agent': 'AgentF', 'level': 'super_high_plus_plus'}]}, f)

        # Create config where a rule is missing the 'level' key
        with open(cls.RULE_NO_LEVEL_CONFIG_PATH, 'w') as f:
            yaml.dump({'trust_rules': [{'agent': 'AgentG'}]}, f)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.ATRIAN_TEMP_TEST_CONFIGS_DIR):
            shutil.rmtree(cls.ATRIAN_TEMP_TEST_CONFIGS_DIR)

    def setUp(self):
        # Reset logging to a known state for each test
        # This allows tests that specifically check logs to enable them temporarily
        logging.disable(logging.NOTSET) # Ensure logging is enabled
        
        # Initialize WeaverOfTrust with the valid config for all tests
        self.weaver = WeaverOfTrust(trust_config_filepath=self.VALID_CONFIG_PATH)
        
        # Ensure trust_event_log is cleared for each test
        self.weaver.trust_event_log.clear()

    def test_initialization_valid_config(self):
        weaver = WeaverOfTrust(trust_config_filepath=self.VALID_CONFIG_PATH)
        self.assertGreater(len(weaver.trust_baselines), 0)
        self.assertEqual(weaver.trust_baselines['AgentA']['level'], 'high')
        self.assertAlmostEqual(weaver.dynamic_trust_scores['AgentA'], 0.9)
        self.assertAlmostEqual(weaver.dynamic_trust_scores['AgentB'], 0.65)
        self.assertAlmostEqual(weaver.dynamic_trust_scores['AgentC'], 0.4)
        self.assertAlmostEqual(weaver.dynamic_trust_scores['SystemCriticalAgent'], 0.9)

    def test_initialization_missing_config(self):
        weaver = WeaverOfTrust(trust_config_filepath="./non_existent_config.yaml")
        self.assertEqual(len(weaver.trust_baselines), 0)
        self.assertEqual(len(weaver.dynamic_trust_scores), 0)

    def test_initialization_malformed_config(self):
        weaver = WeaverOfTrust(trust_config_filepath=self.MALFORMED_CONFIG_PATH)
        self.assertEqual(len(weaver.trust_baselines), 0)

    def test_initialization_empty_config(self):
        weaver = WeaverOfTrust(trust_config_filepath=self.EMPTY_CONFIG_PATH)
        self.assertEqual(len(weaver.trust_baselines), 0)
        
    def test_initialization_no_rules_config(self):
        weaver = WeaverOfTrust(trust_config_filepath=self.NO_RULES_CONFIG_PATH)
        self.assertEqual(len(weaver.trust_baselines), 0)
        self.assertEqual(len(weaver.dynamic_trust_scores), 0)

    def test_initialization_truly_empty_config(self):
        # Expects a warning log, baselines and scores should be empty
        weaver = WeaverOfTrust(trust_config_filepath=self.TRULY_EMPTY_CONFIG_PATH)
        self.assertEqual(len(weaver.trust_baselines), 0)
        self.assertEqual(len(weaver.dynamic_trust_scores), 0)

    def test_initialization_trust_rules_not_list(self):
        # Expects a warning log, baselines and scores should be empty
        weaver = WeaverOfTrust(trust_config_filepath=self.TRUST_RULES_NOT_LIST_CONFIG_PATH)
        self.assertEqual(len(weaver.trust_baselines), 0)
        self.assertEqual(len(weaver.dynamic_trust_scores), 0)

    def test_initialization_rule_not_dict(self):
        # Expects a warning for the invalid rule, but AgentE should load
        weaver = WeaverOfTrust(trust_config_filepath=self.RULE_NOT_DICT_CONFIG_PATH)
        self.assertEqual(len(weaver.trust_baselines), 1)
        self.assertIn('AgentE', weaver.trust_baselines)
        self.assertAlmostEqual(weaver.dynamic_trust_scores.get('AgentE'), 0.65)

    def test_initialization_rule_missing_agent(self):
        # Expects a warning, baselines and scores should be empty
        weaver = WeaverOfTrust(trust_config_filepath=self.RULE_MISSING_AGENT_CONFIG_PATH)
        self.assertEqual(len(weaver.trust_baselines), 0)
        self.assertEqual(len(weaver.dynamic_trust_scores), 0)

    def test_initialization_rule_invalid_agent_id(self):
        # Expects warnings for invalid agent IDs, baselines and scores should be empty
        weaver = WeaverOfTrust(trust_config_filepath=self.RULE_INVALID_AGENT_ID_CONFIG_PATH)
        self.assertEqual(len(weaver.trust_baselines), 0)
        self.assertEqual(len(weaver.dynamic_trust_scores), 0)

    def test_initialization_rule_unrecognized_level(self):
        # AgentF should load with DEFAULT_INITIAL_TRUST
        weaver = WeaverOfTrust(trust_config_filepath=self.RULE_UNRECOGNIZED_LEVEL_CONFIG_PATH)
        self.assertEqual(len(weaver.trust_baselines), 1)
        self.assertIn('AgentF', weaver.trust_baselines)
        self.assertAlmostEqual(weaver.dynamic_trust_scores.get('AgentF'), DEFAULT_INITIAL_TRUST)

    def test_initialization_rule_no_level(self):
        # AgentG should load with the score for 'medium' level (0.65) as per default in load_trust_baselines
        weaver = WeaverOfTrust(trust_config_filepath=self.RULE_NO_LEVEL_CONFIG_PATH)
        self.assertEqual(len(weaver.trust_baselines), 1)
        self.assertIn('AgentG', weaver.trust_baselines)
        self.assertAlmostEqual(weaver.dynamic_trust_scores.get('AgentG'), 0.65) # Default level 'medium' maps to 0.65

    def test_get_trust_score_known_agent(self):
        weaver = WeaverOfTrust(trust_config_filepath=self.VALID_CONFIG_PATH)
        self.assertAlmostEqual(weaver.get_trust_score('AgentA'), 0.9)

    def test_get_trust_score_unknown_agent(self):
        weaver = WeaverOfTrust(trust_config_filepath=self.VALID_CONFIG_PATH)
        self.assertAlmostEqual(weaver.get_trust_score('UnknownAgent'), DEFAULT_INITIAL_TRUST)

    def test_get_trust_score_invalid_agent_id(self):
        weaver = WeaverOfTrust(trust_config_filepath=self.VALID_CONFIG_PATH)
        self.assertAlmostEqual(weaver.get_trust_score(None), TRUST_SCORE_MIN) # type: ignore
        self.assertAlmostEqual(weaver.get_trust_score('  '), TRUST_SCORE_MIN)

    def test_update_trust_score_positive_event(self):
        agent_id = "AgentB"  # Exists, initial score 0.65
        initial_score = self.weaver.get_trust_score(agent_id)
        self.weaver.update_trust_score(agent_id, "success_event", "positive", 0.15, "Completed task successfully")
        expected_score = min(TRUST_SCORE_MAX, initial_score + 0.15)
        self.assertAlmostEqual(self.weaver.get_trust_score(agent_id), expected_score, places=4)
        self.assertEqual(len(self.weaver.trust_event_log), 1)
        log_entry = self.weaver.trust_event_log[0]
        self.assertEqual(log_entry['agent_id'], agent_id)
        self.assertEqual(log_entry['event_type'], "success_event")
        self.assertEqual(log_entry['outcome'], "positive")
        self.assertAlmostEqual(log_entry['original_score'], initial_score, places=4)
        self.assertAlmostEqual(log_entry['adjustment'], 0.15, places=4)
        self.assertAlmostEqual(log_entry['new_score'], expected_score, places=4)
        self.assertEqual(log_entry['reason'], "Completed task successfully")
        self.assertTrue(log_entry['success'])

    def test_update_trust_score_negative_event(self):
        agent_id = "AgentB" # Exists, initial score 0.65
        initial_score = self.weaver.get_trust_score(agent_id)
        self.weaver.update_trust_score(agent_id, "error_occurrence", "negative", 0.15, "Caused a minor error")
        expected_score = max(TRUST_SCORE_MIN, initial_score - 0.15)
        self.assertAlmostEqual(self.weaver.get_trust_score(agent_id), expected_score, places=4)
        self.assertEqual(len(self.weaver.trust_event_log), 1)
        log_entry = self.weaver.trust_event_log[0]
        self.assertEqual(log_entry['agent_id'], agent_id)
        self.assertEqual(log_entry['event_type'], "error_occurrence")
        self.assertEqual(log_entry['outcome'], "negative")
        self.assertAlmostEqual(log_entry['original_score'], initial_score, places=4)
        self.assertAlmostEqual(log_entry['adjustment'], -0.15, places=4)
        self.assertAlmostEqual(log_entry['new_score'], expected_score, places=4)
        self.assertEqual(log_entry['reason'], "Caused a minor error")
        self.assertTrue(log_entry['success'])

    def test_update_trust_score_bounds(self):
        agent_max = "AgentA" # Initial 0.9
        self.weaver.update_trust_score(agent_max, "max_test", "positive", 0.5, "Push to max")
        self.assertAlmostEqual(self.weaver.get_trust_score(agent_max), TRUST_SCORE_MAX, places=4)
        log_entry_max = self.weaver.trust_event_log[-1]
        self.assertAlmostEqual(log_entry_max['new_score'], TRUST_SCORE_MAX, places=4)

        agent_min = "AgentC" # Initial 0.4
        self.weaver.update_trust_score(agent_min, "min_test", "negative", 0.8, "Push to min")
        self.assertAlmostEqual(self.weaver.get_trust_score(agent_min), TRUST_SCORE_MIN, places=4)
        log_entry_min = self.weaver.trust_event_log[-1]
        self.assertAlmostEqual(log_entry_min['new_score'], TRUST_SCORE_MIN, places=4)

    def test_update_trust_score_invalid_agent_id(self):
        initial_log_len = len(self.weaver.trust_event_log)
        with self.assertLogs(logger_name, level='ERROR') as cm:
            self.weaver.update_trust_score("", "test_event", "positive", 0.1, "Invalid agent ID test")
        self.assertIn("Attempted to update trust score for invalid agent_id: ''", cm.output[0])
        self.assertEqual(len(self.weaver.trust_event_log), initial_log_len, "Log should not be created for invalid agent ID update attempt")

        with self.assertLogs(logger_name, level='ERROR') as cm:
            self.weaver.update_trust_score("   ", "test_event", "positive", 0.1, "Invalid agent ID test with spaces")
        self.assertIn("Attempted to update trust score for invalid agent_id: '   '", cm.output[0])
        self.assertEqual(len(self.weaver.trust_event_log), initial_log_len)

    def test_update_trust_score_unknown_agent(self):
        agent_id = "UnknownAgent"
        initial_log_len = len(self.weaver.trust_event_log) # Should be 0 due to setUp clearing log
        self.weaver.update_trust_score(agent_id, "test_event", "positive", 0.1, "Test event for unknown agent")
        expected_score = min(TRUST_SCORE_MAX, DEFAULT_INITIAL_TRUST + 0.1)
        self.assertAlmostEqual(self.weaver.get_trust_score(agent_id), expected_score, places=4)
        self.assertEqual(len(self.weaver.trust_event_log), initial_log_len + 1)
        log_entry = self.weaver.trust_event_log[-1]
        self.assertEqual(log_entry['agent_id'], agent_id)
        self.assertEqual(log_entry['event_type'], "test_event")
        self.assertEqual(log_entry['outcome'], "positive")
        self.assertAlmostEqual(log_entry['original_score'], DEFAULT_INITIAL_TRUST, places=4)
        self.assertAlmostEqual(log_entry['adjustment'], 0.1, places=4)
        self.assertAlmostEqual(log_entry['new_score'], expected_score, places=4)
        self.assertEqual(log_entry['reason'], "Test event for unknown agent")
        self.assertTrue(log_entry['success'])

    def test_update_trust_score_neutral_outcome(self):
        agent_id = "AgentA"
        initial_score = self.weaver.get_trust_score(agent_id)
        self.weaver.update_trust_score(agent_id, "observation", "neutral", 0.5, "Neutral event, magnitude ignored")
        self.assertAlmostEqual(self.weaver.get_trust_score(agent_id), initial_score, places=4, msg="Score should not change for neutral outcome")
        self.assertEqual(len(self.weaver.trust_event_log), 1)
        log_entry = self.weaver.trust_event_log[0]
        self.assertEqual(log_entry['agent_id'], agent_id)
        self.assertEqual(log_entry['outcome'], "neutral")
        self.assertAlmostEqual(log_entry['adjustment'], 0.0, places=4)
        self.assertAlmostEqual(log_entry['new_score'], initial_score, places=4)
        self.assertTrue(log_entry['success'])

    def test_update_trust_score_invalid_outcome(self):
        agent_id = "AgentB"
        initial_score = self.weaver.get_trust_score(agent_id)
        with self.assertLogs(logger_name, level='WARNING') as cm:
            self.weaver.update_trust_score(agent_id, "system_glitch", "unexpected_flux", 0.1, "Invalid outcome type")
        self.assertIn(f"Invalid outcome 'unexpected_flux' for agent '{agent_id}'. No score change applied.", cm.output[0])
        self.assertAlmostEqual(self.weaver.get_trust_score(agent_id), initial_score, places=4, msg="Score should not change for invalid outcome")
        self.assertEqual(len(self.weaver.trust_event_log), 1, "Event should still be logged as unsuccessful update")
        log_entry = self.weaver.trust_event_log[0]
        self.assertEqual(log_entry['agent_id'], agent_id)
        self.assertEqual(log_entry['outcome'], "unexpected_flux")
        self.assertFalse(log_entry['success'])
        self.assertEqual(log_entry['details'], "Invalid outcome provided")
        self.assertAlmostEqual(log_entry['new_score'], initial_score, places=4) # Score remains original

    def test_can_delegate_action_allowed(self):
        weaver = WeaverOfTrust(trust_config_filepath=self.VALID_CONFIG_PATH)
        # AgentA has 'full' delegation and can_delegate_to '*' and high trust
        # AgentB has medium trust (0.65), which is above default 0.6 threshold in stub
        self.assertTrue(weaver.can_delegate_action('AgentA', 'AgentB', {'type': 'some_action'}))

    def test_can_delegate_action_denied_delegator_no_baseline(self):
        weaver = WeaverOfTrust(trust_config_filepath=self.VALID_CONFIG_PATH)
        self.assertFalse(weaver.can_delegate_action('UnknownDelegator', 'AgentA', {'type': 'some_action'}))

    def test_can_delegate_action_denied_scope_none(self):
        weaver = WeaverOfTrust(trust_config_filepath=self.VALID_CONFIG_PATH)
        # AgentC has 'none' delegation scope
        self.assertFalse(weaver.can_delegate_action('AgentC', 'AgentA', {'type': 'some_action'}))

    def test_can_delegate_action_denied_not_in_can_delegate_to(self):
        weaver = WeaverOfTrust(trust_config_filepath=self.VALID_CONFIG_PATH)
        # AgentB can only delegate to AgentC by rule
        self.assertFalse(weaver.can_delegate_action('AgentB', 'AgentA', {'type': 'some_action'}))

    def test_can_delegate_action_denied_low_trust_delegatee(self):
        weaver = WeaverOfTrust(trust_config_filepath=self.VALID_CONFIG_PATH)
        weaver.dynamic_trust_scores['AgentC'] = 0.3 # Lower AgentC's trust below threshold (0.6 in stub)
        # AgentA can delegate to anyone, but AgentC's trust is too low
        self.assertFalse(weaver.can_delegate_action('AgentA', 'AgentC', {'type': 'some_action'}))

    def test_get_trust_log_empty(self):
        weaver = WeaverOfTrust(trust_config_filepath=self.VALID_CONFIG_PATH)
        self.assertEqual(len(weaver.get_trust_log()), 0)

    def test_get_trust_log_with_entries(self):
        weaver = WeaverOfTrust(trust_config_filepath=self.VALID_CONFIG_PATH)
        weaver.update_trust_score('AgentA', 'event1', 'positive', 0.1)
        weaver.update_trust_score('AgentB', 'event2', 'negative', 0.1)
        self.assertEqual(len(weaver.get_trust_log()), 2)

    def test_get_trust_log_filtered_agent(self):
        weaver = WeaverOfTrust(trust_config_filepath=self.VALID_CONFIG_PATH)
        weaver.update_trust_score('AgentA', 'event1', 'positive', 0.1)
        weaver.update_trust_score('AgentB', 'event2', 'negative', 0.1)
        weaver.update_trust_score('AgentA', 'event3', 'neutral', 0.0)
        agent_a_logs = weaver.get_trust_log(agent_id='AgentA')
        self.assertEqual(len(agent_a_logs), 2)
        for log in agent_a_logs:
            self.assertEqual(log['agent_id'], 'AgentA')

    def test_get_trust_log_last_n(self):
        weaver = WeaverOfTrust(trust_config_filepath=self.VALID_CONFIG_PATH)
        for i in range(5):
            weaver.update_trust_score(f'AgentX{i}', f'event{i}', 'positive', 0.01)
        last_3_logs = weaver.get_trust_log(last_n=3)
        self.assertEqual(len(last_3_logs), 3)
        self.assertEqual(last_3_logs[0]['agent_id'], 'AgentX2') # Assuming order is preserved
        self.assertEqual(last_3_logs[2]['agent_id'], 'AgentX4')

if __name__ == '__main__':
    unittest.main()