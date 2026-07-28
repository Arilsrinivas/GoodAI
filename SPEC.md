You are an expert AI Architect, Full Stack Engineer, Machine Learning Engineer, and Software Engineer.



Build a production-ready Universal AI Story-to-Video Generation Platform.



The platform should convert ANY long-form narrative into a fully cinematic, AI-generated video with synchronized narration while maintaining perfect character, location, object, camera, and scene continuity.



This is NOT a simple prompt generator.



This is an intelligent AI Director that understands stories exactly like a human director.



====================================================

PRIMARY OBJECTIVE

====================================================



Accept any input:



• PDF

• DOCX

• TXT

• EPUB

• Markdown

• HTML

• Movie Script

• Story

• Novel

• Biography

• Research Paper

• Historical Document

• User-written Story

• AI-generated Story



Automatically understand the content and generate:



• Narration

• Scene Breakdown

• Character Profiles

• Location Profiles

• Object Memory

• Timeline

• Emotional Flow

• Camera Plan

• Cinematic Prompts

• AI Videos

• Scene Continuity

• Final Movie



The system must work for ANY future story without modifications.



====================================================

ARCHITECTURE

====================================================



The system should be Agent-based.



Agents communicate using shared memory.



Create the following AI Agents:



1\. Document Parser Agent



Reads any document.



Extracts



Title



Chapters



Paragraphs



Timeline



Characters



Dialogue



Narration



Important events



Themes



Keywords



2\. Story Understanding Agent



Acts like a film director.



Understands



Main plot



Subplots



Character arcs



Relationships



Motivations



Emotions



Conflicts



Turning points



Scene transitions



Visual opportunities



Foreshadowing



Symbolism



3\. Character Memory Agent



Maintains perfect character consistency.



Store



Unique ID



Name



Aliases



Age



Gender



Face



Hair



Eyes



Skin



Body



Clothing



Accessories



Voice



Personality



Expressions



Movement style



Relationships



Character evolution



Never redesign characters unless the story explicitly changes them.



4\. Location Memory Agent



Store every location.



Architecture



Lighting



Weather



Season



Objects



Time of day



Camera mood



Visual references



Environment



Historical details



5\. Object Memory Agent



Remember



Books



Weapons



Vehicles



Furniture



Animals



Sacred objects



Jewelry



Clothing



Buildings



Everything appearing in previous scenes.



Objects should never randomly disappear.



6\. Timeline Agent



Create chronological memory.



Store



Years



Dates



Age progression



Location changes



Character development



Important events



Scene transitions



7\. Emotion Agent



Understand emotional progression.



Store



Hope



Fear



Joy



Sadness



Anger



Suspense



Mystery



Peace



Emotion intensity.



Emotion directly affects



Narration



Music



Lighting



Camera



Color grading



8\. Scene Planner Agent



Convert the story into cinematic scenes.



Do NOT simply split paragraphs.



Instead split based on



Action



Emotion



Camera transition



Location



Character interaction



Narration timing



Each scene should be approximately



8–15 seconds



9\. Cinematography Agent



Acts like Hollywood cinematographer.



Choose



Camera



Lens



Movement



Composition



Shot type



Depth of field



Lighting



Color grading



Frame composition



Visual style



10\. Prompt Engineering Agent



Generate the best possible prompts.



Each prompt should contain



Character Memory



Location Memory



Object Memory



Timeline Memory



Visual Memory



Current narration



Current emotion



Camera instructions



Negative prompt



Ending frame description



11\. Narration Agent



Generate cinematic narration.



Narration should always synchronize with scene duration.



Support multiple narration styles.



Documentary



Movie trailer



Storytelling



Educational



Podcast



Dramatic



12\. Video Generation Agent



Abstract interface.



Should support multiple providers.



The provider should be replaceable without changing the workflow.



13\. Continuity Agent



This is the most important component.



After every generated video



Extract the final frame.



Store



Camera position



Lighting



Character positions



Objects



Background



Environment



Generate the next scene beginning from that exact frame.



If the provider supports reference images



Use the previous last frame.



Otherwise



Use detailed scene memory.



The viewer should never notice scene boundaries.



14\. Quality Assurance Agent



Before every generation verify



Timeline consistency



Character consistency



Lighting continuity



Weather continuity



Object continuity



Camera continuity



Narration synchronization



Historical accuracy



Scene quality



====================================================

MEMORY SYSTEM

====================================================



Implement long-term structured memory.



Character Memory



Location Memory



Timeline Memory



Object Memory



Visual Memory



Emotion Memory



Scene Memory



Narration Memory



Each memory should be stored independently.



Every generation automatically loads all relevant memories.



====================================================

VISUAL MEMORY

====================================================



Store



Camera



Lens



Lighting



Weather



Color grading



Time of day



Composition



Character positions



Object positions



Environment



Style



====================================================

SCENE MEMORY

====================================================



Every scene stores



Opening frame



Ending frame



Narration



Prompt



Duration



Objects



Characters



Environment



Camera



Transitions



====================================================

DIRECTOR LOGIC

====================================================



The AI should think like a film director.



Instead of asking



"What happened?"



Ask



"What should the audience see?"



Every narration sentence should have matching visuals.



Never show unrelated footage.



====================================================

CONTINUATION

====================================================



After every generated scene



Extract last frame.



Use it as reference for the next scene.



Maintain



Identity



Environment



Lighting



Perspective



Camera



Objects



Clothing



Expressions



Movement



The movie should feel continuous.



====================================================

VIDEO STYLE

====================================================



Support selectable styles



Photorealistic



Pixar



Anime



Studio Ghibli



Comic



Watercolor



Oil Painting



Vintage



3D Animation



Clay



Stop Motion



Documentary



Realistic Cinema



====================================================

NARRATION STYLES

====================================================



Support



Documentary



Historical



Inspirational



Educational



Storytelling



Movie Trailer



Fantasy



Adventure



====================================================

EXPORT

====================================================



Generate



Narration



Subtitles



JSON



Timeline



Prompt history



Character database



Location database



Scene database



Videos



Final stitched movie



Metadata



====================================================

TECH STACK

====================================================



Frontend



Next.js



React



TailwindCSS



TypeScript



Backend



Python



FastAPI



Workflow



LangGraph



LLM



AtlasCloud



Memory



SQLite initially



Support PostgreSQL



Storage



Filesystem



Video



FFmpeg



Image



OpenCV



Pillow



====================================================

SOFTWARE DESIGN

====================================================



Use Clean Architecture.



Use Repository Pattern.



Use Service Layer.



Use Dependency Injection.



Use Async Programming.



Use Typed Models.



Use Pydantic.



Use Comprehensive Logging.



Retry API failures.



Streaming progress updates.



Support future plugins.



Make every component independently replaceable.



====================================================

GOAL



Build this as a reusable AI Story Engine, not a project for one story.



The same pipeline should work equally well for:



• A 5-page biography

• A 500-page novel

• A children's story

• A documentary script

• A historical book

• A religious text

• A science article

• A movie screenplay

• A user-written story



without changing any code.

====================================================

AI PROJECT HANDOFF SYSTEM

====================================================



This project must be self-documenting.



Every time code is generated, modified, or refactored, the AI must automatically update the project documentation so another developer or AI agent can continue without losing context.



Maintain the following files automatically.



PROJECT\_STATUS.md



Contains



• Overall completion percentage

• Current milestone

• Current sprint

• Last updated timestamp

• Current branch

• Features completed

• Features in progress

• Blockers

• Next recommended tasks



\----------------------------------------------------



CHANGELOG.md



Automatically append every significant change.



Include



Date



Files modified



Reason



Summary



Impact



\----------------------------------------------------



DECISIONS.md



Whenever an architectural decision is made, record



Decision



Reason



Alternatives considered



Trade-offs



Future implications



\----------------------------------------------------



TODO.md



Automatically maintain



High priority tasks



Medium priority tasks



Low priority tasks



Completed tasks



Deferred tasks



\----------------------------------------------------



ARCHITECTURE.md



Update whenever



New services



New APIs



New workflows



Database changes



Memory changes



Agent changes



are introduced.



\----------------------------------------------------



API.md



Automatically update whenever



Endpoints



Schemas



Models



Authentication



Request/Response formats



change.



\----------------------------------------------------



DATABASE.md



Automatically update



ER diagrams



Tables



Columns



Relationships



Indexes



Migration history



\----------------------------------------------------



PROMPTS.md



Whenever prompts change



Record



Prompt purpose



Inputs



Outputs



Reason for modification



Version history



\----------------------------------------------------



MEMORY.md



Keep documentation of



Character Memory



Scene Memory



Timeline Memory



Object Memory



Visual Memory



Emotion Memory



How each memory is updated



How each memory is consumed



\----------------------------------------------------



WORKLOG.md



At the end of every coding session write



Today's accomplishments



Files changed



Problems encountered



Solutions



Remaining work



Estimated completion



\----------------------------------------------------



HANDOFF.md



This is the most important file.



Generate it automatically after every significant milestone.



Include



Project summary



Current architecture



Completed modules



Incomplete modules



Known bugs



Known limitations



Current environment



Dependencies



How to run the project



Where development should continue



Recommended next tasks



Estimated effort remaining



Important warnings



This file should allow a new engineer or AI agent to continue development without asking any questions.



\----------------------------------------------------



PROGRESS.json



Maintain machine-readable progress.



Example



{

&#x20; "completion": 47,

&#x20; "current\_phase": "Scene Continuity Engine",

&#x20; "completed\_modules": \[

&#x20;   "Parser",

&#x20;   "Story Analyzer",

&#x20;   "Character Memory"

&#x20; ],

&#x20; "remaining\_modules": \[

&#x20;   "Video Generator",

&#x20;   "QA Agent"

&#x20; ],

&#x20; "last\_updated": "...",

&#x20; "next\_task": "Implement Frame Continuity"

}



\----------------------------------------------------



SESSION\_SUMMARY.md



At the end of every coding session generate a concise summary of



What changed



Why



How to continue



Open issues



Testing status



This should be readable in under five minutes.



====================================================



RULES



Never leave the documentation outdated.



Documentation updates are mandatory whenever the code changes.



The project should always be recoverable by another developer or AI using only the repository contents.



Before starting any new coding session, first read:



README.md

PROJECT\_STATUS.md

HANDOFF.md

WORKLOG.md

TODO.md

ARCHITECTURE.md

DECISIONS.md



and use them to reconstruct project context before making changes.

====================================================

AI PROJECT HANDOFF SYSTEM

====================================================



This project must be self-documenting.



Every time code is generated, modified, or refactored, the AI must automatically update the project documentation so another developer or AI agent can continue without losing context.



Maintain the following files automatically.



PROJECT\_STATUS.md



Contains



• Overall completion percentage

• Current milestone

• Current sprint

• Last updated timestamp

• Current branch

• Features completed

• Features in progress

• Blockers

• Next recommended tasks



\----------------------------------------------------



CHANGELOG.md



Automatically append every significant change.



Include



Date



Files modified



Reason



Summary



Impact



\----------------------------------------------------



DECISIONS.md



Whenever an architectural decision is made, record



Decision



Reason



Alternatives considered



Trade-offs



Future implications



\----------------------------------------------------



TODO.md



Automatically maintain



High priority tasks



Medium priority tasks



Low priority tasks



Completed tasks



Deferred tasks



\----------------------------------------------------



ARCHITECTURE.md



Update whenever



New services



New APIs



New workflows



Database changes



Memory changes



Agent changes



are introduced.



\----------------------------------------------------



API.md



Automatically update whenever



Endpoints



Schemas



Models



Authentication



Request/Response formats



change.



\----------------------------------------------------



DATABASE.md



Automatically update



ER diagrams



Tables



Columns



Relationships



Indexes



Migration history



\----------------------------------------------------



PROMPTS.md



Whenever prompts change



Record



Prompt purpose



Inputs



Outputs



Reason for modification



Version history



\----------------------------------------------------



MEMORY.md



Keep documentation of



Character Memory



Scene Memory



Timeline Memory



Object Memory



Visual Memory



Emotion Memory



How each memory is updated



How each memory is consumed



\----------------------------------------------------



WORKLOG.md



At the end of every coding session write



Today's accomplishments



Files changed



Problems encountered



Solutions



Remaining work



Estimated completion



\----------------------------------------------------



HANDOFF.md



This is the most important file.



Generate it automatically after every significant milestone.



Include



Project summary



Current architecture



Completed modules



Incomplete modules



Known bugs



Known limitations



Current environment



Dependencies



How to run the project



Where development should continue



Recommended next tasks



Estimated effort remaining



Important warnings



This file should allow a new engineer or AI agent to continue development without asking any questions.



\----------------------------------------------------



PROGRESS.json



Maintain machine-readable progress.



Example



{

&#x20; "completion": 47,

&#x20; "current\_phase": "Scene Continuity Engine",

&#x20; "completed\_modules": \[

&#x20;   "Parser",

&#x20;   "Story Analyzer",

&#x20;   "Character Memory"

&#x20; ],

&#x20; "remaining\_modules": \[

&#x20;   "Video Generator",

&#x20;   "QA Agent"

&#x20; ],

&#x20; "last\_updated": "...",

&#x20; "next\_task": "Implement Frame Continuity"

}



\----------------------------------------------------



SESSION\_SUMMARY.md



At the end of every coding session generate a concise summary of



What changed



Why



How to continue



Open issues



Testing status



This should be readable in under five minutes.



====================================================



RULES



Never leave the documentation outdated.



Documentation updates are mandatory whenever the code changes.



The project should always be recoverable by another developer or AI using only the repository contents.



Before starting any new coding session, first read:



README.md

PROJECT\_STATUS.md

HANDOFF.md

WORKLOG.md

TODO.md

ARCHITECTURE.md

DECISIONS.md



and use them to reconstruct project context before making changes.

