**Instructions:**
1. The LLM must adhere strictly to the schema provided.

**Schema:**
```json
{
  "user_input": {
    "type": "string",
    "description": "The original prompt or request provided by the user"
  },
  "enhanced_prompt": {
    "type": "string",
    "description": "The optimized and refined version of the user's prompt for better LLM interaction"
  },
  "explanation": {
    "type": "string",
    "description": "Detailed explanation of the enhancements made to the original prompt, including reasoning and strategies used"
  },
  "additional_info": {
    "type": "object",
    "properties": {
      "context_added": {
        "type": "string",
        "description": "Additional context or assumptions introduced to enhance the prompt's effectiveness"
      },
      "specificity_increased": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "List of areas where the prompt was made more specific to reduce vagueness"
      },
      "ambiguities_reduced": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "List of ambiguities in the original prompt that were clarified or resolved"
      },
      "examples_provided": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Examples or illustrative details added to make the prompt clearer and more actionable"
      },
      "tone_adjustments": {
        "type": "string",
        "description": "Any changes to the tone of the prompt to match the intended audience or context"
      }
    },
    "description": "Additional information about the enhancement process, including specific adjustments and justifications"
  }
}
