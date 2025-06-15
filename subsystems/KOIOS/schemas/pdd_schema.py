# @references:
#   - subsystems/KOIOS/schemas/pdd_schema.py
# 
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class PddMetadata(BaseModel):
    author: Optional[str] = None
    created_date: Optional[str] = None # Ideally, use datetime, but PDD standard shows string
    last_updated: Optional[str] = None # Ideally, use datetime
    tags: Optional[List[str]] = Field(default_factory=list)
    related_pdds: Optional[List[str]] = Field(default_factory=list)

class PddEthikGuidelines(BaseModel):
    pii_handling: Optional[str] = None
    bias_mitigation_ref: Optional[str] = None
    forbidden_topics: Optional[List[str]] = Field(default_factory=list)
    output_tone: Optional[str] = None

class PddSchema(BaseModel):
    id: str = Field(..., description="Unique identifier for the PDD, matching the filename (snake_case).")
    name: str = Field(..., description="Human-readable name for the prompt.")
    description: str = Field(..., description="Detailed description of the prompt's purpose, inputs, and expected outputs.")
    version: str = Field(..., description="Version of the PDD (e.g., '1.0.0', '0.2-alpha').")
    pdd_type: Optional[str] = Field(default="generic", description="Type of PDD, used for dispatching to specialized schemas (e.g., 'generic', 'specialized_handler').")
    parameters: List[str] = Field(default_factory=list, description="List of parameter names that should be substituted into the template.")
    template: str = Field(..., description="The prompt template string, often multi-line, with placeholders for parameters (e.g., {{parameter_name}}).")
    metadata: Optional[PddMetadata] = None
    ethik_guidelines: Optional[PddEthikGuidelines] = None

    model_config = {"extra": "forbid"} # Forbid any extra fields not defined in the schema

# Schema for PDDs that use a specialized handler (e.g., a multi-agent crew)
class SpecializedHandlerPddSchema(PddSchema):
    handler_type: Optional[str] = Field(None, description="Identifier for the type of specialized handler required (e.g., 'specialized_crew').")
    handler_reference: Optional[str] = Field(None, description="Specific reference or name of the handler logic to be invoked.")
    # Using direct field name matching YAML key 'model_config' for this test
    model_config: Optional[Dict[str, Any]] = Field(
        None,
        description="Configuration parameters specific to the handler or models it uses."
    )
    response_format: Optional[Dict[str, Any]] = Field(
        None,
        description="Detailed schema or format description for the expected response from the handler."
    )

    # Explicitly define model_config, even if it's the same as the parent, to be absolutely clear for Pydantic
    model_config = {"extra": "forbid"}

# Example Usage (for testing or documentation):
if __name__ == "__main__":
    example_pdd_data = {
        "id": "example_prompt",
        "name": "Example Prompt",
        "description": "This is an example PDD for demonstration purposes.",
        "version": "1.0",
        "parameters": ["user_query", "context_document"],
        "template": "Answer the following query: {{user_query}}\nBased on this document: {{context_document}}",
        "metadata": {
            "author": "EGOS System",
            "tags": ["example", "demonstration"]
        },
        "ethik_guidelines": {
            "output_tone": "neutral and objective"
        }
    }

    try:
        pdd_instance = PddSchema(**example_pdd_data)
        print("PDD Instance Validated Successfully:")
        print(pdd_instance.model_dump_json(indent=2))
    except Exception as e:
        print(f"PDD Validation Error: {e}")