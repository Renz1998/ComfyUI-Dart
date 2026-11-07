# DART ideas → your character → Archmage

Connect **DART Generate.STRING → Archmage.source_tags** (shown as **DART tags (scene ideas)**). Connect **Appearance Overrides.appearance → Archmage.appearance**. Leave Scene idea blank for DART-led invention, or write your own idea to guide which suggestions fit.

Dragging from DART's text output suggests Archmage's tag socket first. Dragging backward from the tag socket suggests DART Generate and Decode nodes. Older Archmage nodes gain the new socket after refreshing; existing links keep their positions.

## What happens to the tags?

1. Underscores and common weighting syntax are normalized, and duplicates/control syntax/quality metadata are screened out.
2. **Scene ideas (protect character)** removes known random hair, eyes, body/skin/age traits and named characters/series. Selected replacements take their place through the appearance recipe. Poses, actions, clothing, objects, setting and camera ideas remain candidates.
3. A chosen style or reference image takes priority over source medium/rendering tags. A photograph preset can therefore use a fantasy prop without inheriting an anime or watercolor treatment.
4. Archmage chooses a coherent subset, combines it with your character and style, and writes prose or MOSS JSON. Your own Scene idea and Writing rules have higher priority than DART suggestions. No extra model call is added for filtering.

Example input:

```text
1girl, blue_hair, red_eyes, flat_chest, hatsune_miku, watercolor, sitting, cafe, holding_cup
```

With your character's black hair, blue eyes and selected body traits, plus a photo preset, the scene candidates become:

```text
1girl, sitting, cafe, holding cup
```

The appearance recipe supplies the character reference and selected replacements while Archmage develops the cafe scene. You can inspect **report.source_tags** for candidate tags, each removed tag's reason and requested character replacements. Candidates are suggestions; the report does not claim the model used every retained tag.

## Keep some random appearance

Choose **Keep unselected appearance** to allow DART traits you haven't overridden. Selected hair, eye, body, clothing or expression replacements still suppress known conflicts. **Trigger replaces identity details** continues to protect unselected identity traits in this mode. Disabled appearance recipes make no replacement requests.

With a reference image, tags alone do not request a new pose, person or setting. The reference remains the starting point; your explicit Scene idea/Writing rules can request changes.

## Practical limits

Screening uses a bundled tag vocabulary plus lexical rules. It does not know every tag or every trait associated with your trigger. Unknown tags remain optional candidates, and contextual relevance, custom replacements and final instruction following are model-guided. Check important outputs; image rendering is not guaranteed by tag filtering.

Appearance settings change generated text, not input pixels, model weights or LoRAs. The existing exact-size wording option and appearance reports remain active. The feature works with both local Qwen and OpenAI, subject to the selected model's capabilities and provider policies.

[DART → Archmage example](../workflows/start-here/06-dart-ideas-to-archmage.json) · [Archmage controls](ARCHMAGE_USABILITY.md)
