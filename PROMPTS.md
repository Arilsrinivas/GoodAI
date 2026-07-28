# Prompts

Prompt generation is currently deterministic and implemented in `PromptEngineeringAgent`.

## Version 0.1.0

Purpose: Create a cinematic scene prompt that includes narration, character memory, location memory, object memory, camera, lighting, color grading, and continuity instructions.

Inputs:

- Story request style fields.
- Current narration.
- Visual memory.
- Character memory.
- Location memory.
- Object memory.

Outputs:

- Positive cinematic prompt.
- Negative prompt.
- Ending frame description.

Reason for modification:

- Initial bootstrap from `SPEC.md`.

Version history:

- 2026-07-16: Added initial prompt construction contract.

Planned improvements:

- Add AtlasCloud prompt templates.
- Add strict JSON output schemas.
- Add prompt regression tests.

