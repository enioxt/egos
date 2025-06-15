"""TODO: Module docstring for models.py

@references: 
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

"""
@references:
- Core References:
  - [MQP.md](mdc:../../MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP.md](mdc:../../ROADMAP.md) - Project roadmap and planning





# EGOS Import Resilience: see docs/process/dynamic_import_resilience.md
import sys
from pathlib import Path
project_root = str(Path(__file__).resolve().parents[6])
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from pydantic import BaseModel, Field


class ContractClassification(BaseModel):
    category: str = Field(
        description="The classified category of the contract (e.g., 'License Agreement', 'Service', 'IP', etc.)"
    )
    reasoning: str = Field(
        description="A concise explanation (max 150 words) justifying why the contract was classified in this category"
    )