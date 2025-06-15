---
title: commit_skill_tagging_convention
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: project-wide
primary_entity_type: documentation
primary_entity_name: commit_skill_tagging_convention
tags: [documentation]
---
---
title: commit_skill_tagging_convention
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: 
primary_entity_type: 
primary_entity_name: 
tags: []
---

---
title: commit_skill_tagging_convention
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: 
primary_entity_type: 
primary_entity_name: 
tags: []
---

---
title: Commit Skill Tagging Convention
version: 1.0.0
status: Active
date: 2025-04-28
tags: [git, skills, workflow, convention]
@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

@references(level=1):
  - docs/governance/business/github_updates/CONTRIBUTING.md
  - docs/templates/reference_templates/action_skill_log_template.md






  - [MQP](../../core/MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP](../../governance/migrations/processed/pt/ROADMAP.md) - Project roadmap and planning
- Related Documents:
  - [action_skill_log_template](action_skill_log_template.md) - Template for logging skills
  - [CONTRIBUTING](../../governance/business/github_updates/CONTRIBUTING.md) - Contribution guidelines
  - docs/templates/reference_templates/commit_skill_tagging_convention.md

# 📝 Commit Skill Tagging Convention

**Document ID:** EGOS-STRAT-COMMIT-001  
**Version:** 1.0  
**Created:** 2025-04-28  
**Status:** ⚡ Active

## Purpose

This convention establishes a standardized approach for tagging Git commits with the skills they demonstrate or utilize. This practice serves multiple purposes:

1. Creates a traceable record of skill application throughout the project history
2. Helps identify patterns of strength and growth areas
3. Supports the creation of a skills portfolio with concrete evidence
4. Facilitates searching the commit history by skill type

## Skill Tagging Format

EGOS commits already follow the [Conventional Commits](https://www.conventionalcommits.org/) specification. Skill tagging extends this standard by adding a `Skills` section to the commit message body.

### Basic Format

```
<type>(<scope>): <description>

<body>

Skills: [Skill1, Skill2, Skill3]

<footer>
```

### Example Commit Messages

**Simple commit with skills:**

```
feat(nexus): add module dependency visualization

Implement D3-based visualization of module dependencies within the NEXUS subsystem.

Skills: [Visualization, JavaScript, SystemsThinking]

Closes #42
```

**More detailed commit with skills:**

```
refactor(ethik): optimize ethical validation pipeline

Refactored the core validation pipeline to improve performance and reduce memory usage:
- Implemented lazy evaluation for validators
- Added caching layer for common validation patterns
- Reduced cyclomatic complexity from 24 to 8

Skills: [CodeQuality, Optimization, SystemsThinking, Refactoring]

Part of #123
```

## Skill Categories Reference

When tagging commits, refer to these standard skill categories and specific skills to maintain consistency:

### Cognitive Skills
- **SystemsThinking**: Connecting components, seeing broader patterns
- **Metacognition**: Awareness of thought processes
- **CreativeProblemSolving**: Novel approaches to challenges
- **AnalyticalReasoning**: Breaking down complex problems

### Technical Skills
- **Architecture**: System or component design
- **CodeQuality**: Improving maintainability, readability
- **APIDesign**: Creating intuitive interfaces
- **Testing**: Test creation and validation strategies
- **Documentation**: Improving understanding through docs
- **Debugging**: Problem identification and resolution
- **Optimization**: Performance or resource improvements
- **Security**: Enhancing system security
- **Refactoring**: Restructuring code without changing behavior

### Domain-Specific Skills
- **Visualization**: Creating visual representations of data/systems
- **Python**: Python-specific implementations
- **JavaScript**: JavaScript-specific implementations
- **Database**: Database design or operations
- **AI**: Artificial intelligence implementations
- **WebDevelopment**: Web-related implementations
- **DevOps**: Deployment, CI/CD, infrastructure
- **DataAnalysis**: Working with data structures and analysis

### Meta-Work Skills
- **Organization**: Improving structure and processes
- **Documentation**: Creating explanatory materials
- **Automation**: Automating repetitive tasks
- **ProcessImprovement**: Enhancing workflows
- **KnowledgeTransfer**: Sharing understanding with others

## Usage Guidelines

1. **Be Specific But Concise**: List 1-4 primary skills demonstrated in the commit.
2. **Use Standard Terminology**: Stick to the skill names listed above when possible.
3. **Format Consistently**: Always use `Skills: [Skill1, Skill2]` format with brackets.
4. **Focus on Primary Skills**: Include only the most relevant skills demonstrated.
5. **Placement**: Add the skills list after the main body but before the footer (issue references, etc.).

## Integration with Other EGOS Processes

### With Action-Skill Logging

When making significant commits, consider also adding an entry to your Action-Skill Log with more detailed reflections on the skills used.

### With Case Studies

For particularly demonstrative work that spans multiple commits, reference the commit hashes in a Skill Demonstration Case Study to provide a comprehensive view of your applied skills.

### With Windsurf

When working in Windsurf, consider having your AI assistant suggest relevant skill tags for commits based on the changes made.

## Search and Analysis

Git commits tagged with skills can be searched and analyzed using commands like:

```bash
# Find all commits demonstrating Systems Thinking
git log --grep="Skills: \[.*SystemsThinking.*\]"

# Count commits by skill type
git log --format=%B | grep -o "Skills: \[.*\]" | sort | uniq -c | sort -nr
```

---

*This convention is designed to evolve with usage. Periodically review and refine the skill categories and examples as needed.*