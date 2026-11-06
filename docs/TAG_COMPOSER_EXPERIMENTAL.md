# Tag Composer development build

Search **Prompt Mage · Tag Composer (Experimental)**. Start with `1girl`, choose Invent, Short or Balanced, and an installed full Qwen generation model. No DART model or tokenizer is needed. `tags` is vocabulary-backed; `prompt` may additionally include a character trigger explicitly supplied by Appearance Overrides. Description and scene_json retain the richer scene; report shows additions, unmatched concepts, candidate count and source revision.

This development build is not a new public release. Existing nodes retain their public behavior. Data attribution and spelling limitations are in [the vocabulary README](../py/data/README.md).

Implemented: offline pinned vocabulary; exact/alias/lexical CPU lookup; two-stage local Qwen generation; per-concept candidate membership checks; one shared repair allowance; stable DART-style category ordering; exact input-tag pinning, exact Avoid-tag exclusion and simple recognizable no/without phrases; model offloading after all stages; preview, diagnostic outputs and drag suggestions.

Semantic correctness remains model-guided. Flat tags cannot bind all attributes to individual people. Faithful prose constraints and exclusions need broader evaluation. No model training, embedding retrieval, chat-server backend, arbitrary user literals, stage notifications or direct MOSS output is included yet.

Scene coverage: planning now explicitly inventories the scene it invents. A bounded dictionary scan of the description recovers literal details omitted from the plan as additional retrieval concepts. Unambiguous literal scenery/clothing matches can also be retained deterministically, with their origin recorded in literal_description_matches. Actions and appearance are not automatically emitted this way. Exact description matches are reserved during context trimming. Repairs preserve prior valid selections instead of replacing the entire list. Selection can use multiple supported tags per concept and the bounded repair addresses uncovered concepts. Short/Balanced/Detailed have soft tag-count targets, with no padding requirement. Automatic training-sheet and meme tags are excluded unless explicitly supplied as tags. Vocabulary membership and coverage are still not proof that each selected tag expresses the right meaning; inspect report.coverage and unmatched concepts.

Current candidate context is capped by count and serialized UTF-8 bytes, not measured model tokens. Generation limits are per call; at most three calls are permitted. A token-measured total budget remains a release prerequisite. No current-canonical/legacy spelling switch is exposed: this build explicitly uses dataset spelling.

Development checks: four new Python regression cases cover offline lookup, alias ambiguity, invalid IDs, bounded repair, explicit counts and sorting. A ten-case lexical development set reached 10/10 expected-tag presence after word-form fixes; it is not held-out evaluation. The initial real-model run selected an irrelevant valid meme tag, so automatic meme candidates were removed unless explicitly requested and selection was restricted to each concept's retrieval set. Further real-model review is required before public publication.

Do not treat a valid vocabulary tag as proof of a correct image description. Review report and description before sending the prompt to an image workflow.

Coverage follow-up: description-derived concepts now retain a context window. Initial native coverage increased from a sparse list to 25 tags, but exposed semantic distractors. Context guards reject tied-up-person tags for tied-up hair and rolling-action tags for rolling hills. These are narrowly scoped checks, not a general semantic guarantee. Broader quality evaluation remains pending.

Additional candidate guards: count-only seeds do not offer named character/copyright candidates; unrequested 69-position tags and unexplained franchise qualifiers are excluded. These guards cover observed failures, not an exhaustive sexual-content or semantic classifier. A native run before these final guards still produced incorrect tags, so public release remains blocked on broader semantic evaluation.

For seeded variation, empty ideas, Appearance Overrides, planner normalization and the simpler prose Scene Composer, see [Scene Composer](SCENE_COMPOSER.md). Fixed seed controls on saved nodes must be changed manually to randomize to vary each queued run.
