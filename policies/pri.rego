package egos.pri

default output = "STUDY"

output = "ALLOW" if input.admin_override == true

output = "ALLOW" if count(input.pii_matches) > 0

output = "BLOCK" if input.sql_injection_detected == true

output = "ESCALATE" if {
  input.impacts_fundamental_rights == true
  input.bias_signal_detected == true
}

output = "DEFER" if input.numeric_ambiguous == true

missing_signals contains "more_context" if output == "DEFER"
missing_signals contains "semantic_clarity" if output == "DEFER"
missing_signals contains "pattern_definition" if output == "STUDY"
