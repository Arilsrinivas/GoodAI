# Memory

The current implementation creates memory records inside the story plan. Dedicated memory tables are planned.

## Character Memory

Current update path: `CharacterMemoryAgent` extracts likely names from source text.

Current consumption path: prompts include up to five character names.

## Location Memory

Current update path: `LocationMemoryAgent` extracts location-like phrases.

Current consumption path: prompts include up to three locations and scene environment uses the first location.

## Object Memory

Current update path: `ObjectMemoryAgent` detects a small set of continuity-critical object words.

Current consumption path: prompts list detected objects and scenes store object names.

## Timeline Memory

Current update path: `TimelineAgent` converts paragraphs into ordered story beats.

Current consumption path: stored in the story plan for later scene planning and QA expansion.

## Visual Memory

Current update path: `CinematographyAgent` creates camera, lens, lighting, color grade, composition, and style per scene.

Current consumption path: prompts and scene records consume visual memory.

## Emotion Memory

Current update path: `EmotionAgent` assigns a simple primary emotion and intensity per scene.

Current consumption path: cinematography uses emotion to influence camera, lighting, and color.

## Scene Memory

Current update path: `ScenePlannerAgent`, `NarrationAgent`, `PromptEngineeringAgent`, and `ContinuityAgent` create full scene memory records.

Current consumption path: scenes are persisted in the story plan and returned through the API.

## Narration Memory

Current update path: `NarrationAgent` creates duration-aware narration per scene.

Current consumption path: prompt generation and scene records.

