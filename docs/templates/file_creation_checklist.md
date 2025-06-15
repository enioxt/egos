@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

@references(level=1):
  - docs/governance/cross_reference_priority_list.md
  - docs/governance/development_standards.md
  - docs/governance/file_lifecycle_management.md






  - docs/templates/file_creation_checklist.md

# File Creation Checklist

## File Information

- **Filename**: [Filename with extension]
- **Path**: [Full path to file location]
- **Author**: [Author name]
- **Date Created**: [YYYY-MM-DD]
- **Related Issue/Task**: [Issue/Task ID and title]

## Pre-Creation Checklist

- [ ] **Purpose Defined**: Clear purpose and requirements are established
- [ ] **Duplicate Check**: Verified no existing file serves the same purpose
- [ ] **Location Appropriate**: File is placed in the correct directory structure
- [ ] **Naming Convention**: Filename follows EGOS naming conventions
- [ ] **Dependencies Identified**: Required dependencies are documented

## Creation Checklist

- [ ] **Header/Metadata**: File includes appropriate header and metadata
- [ ] **Documentation**: Purpose and functionality are clearly documented
- [ ] **Cross-References**: References to related files are included
- [ ] **Type Hints**: All functions include appropriate type hints (if applicable)
- [ ] **Docstrings**: All functions/classes have comprehensive docstrings
- [ ] **Error Handling**: Proper error handling is implemented
- [ ] **Logging**: Appropriate logging is implemented
- [ ] **Configuration**: Any configurable parameters are properly documented

## Quality Assurance Checklist

- [ ] **Linting**: Code passes all linting checks
- [ ] **Unit Tests**: Tests are implemented with adequate coverage
- [ ] **Integration Tests**: Integration with other components is tested
- [ ] **Documentation Tests**: Examples in documentation are tested
- [ ] **Security Review**: Security implications have been considered
- [ ] **Performance Check**: Performance implications have been considered

## Review Checklist

- [ ] **Self-Review**: Code has been self-reviewed for quality and clarity
- [ ] **Peer Review**: At least one other developer has reviewed the file
- [ ] **Feedback Addressed**: All review feedback has been addressed
- [ ] **Final Verification**: Final verification of all checklist items

## Post-Creation Checklist

- [ ] **Committed**: File is committed to version control with appropriate message
- [ ] **Documentation Updated**: Related documentation is updated
- [ ] **Cross-References Verified**: All cross-references are verified
- [ ] **Announcement**: Team is notified of the new file if appropriate

## Notes

[Any additional notes, considerations, or explanations]

---

*This checklist implements the File Management Golden Rule from the [EGOS Development Standards](../governance/development_standards.md) and [File Lifecycle Management](../governance/file_lifecycle_management.md) guidelines.*

## Related Documents

- [MQP.md](../MQP.md) - Master Quantum Prompt defining EGOS principles
- [ROADMAP.md](../ROADMAP.md) - Project roadmap and planning
- [Development Standards](../governance/development_standards.md) - Core development standards including Golden Rule
- [File Lifecycle Management](../governance/file_lifecycle_management.md) - Detailed guidelines for file management
- [Cross-Reference Priority List](../governance/cross_reference_priority_list.md) - Files needing cross-reference attention