# Prompt Mage · Archmage (Beta)

The recommended unified assistant for new Prompt Mage scene, prose and MOSS workflows. Scene Composer, Text Assistant and Image to Text are deprecated but retain their existing IDs and behavior. Tag Composer remains a separate experimental tagging tool. Search **Prompt Mage** or **Archmage** after restarting ComfyUI and refreshing the browser. Archmage remains labeled Beta within the Prompt Mage pack; see [publishing status](../PUBLISHING.md) for the available Registry version.

## Start here

1. Add Archmage (Beta). Choose a full generation-capable local Qwen encoder, or connect CLIP. Image input requires a vision-capable encoder.
2. Leave Concepts blank for a seeded scene, or enter an idea. Connect Appearance Overrides to carry your trigger and selected traits into the generated text.
3. Choose Prose or MOSS JSON layout, a length and an aspect ratio. Custom uses Width/Height. These settings guide composition in **both** formats.
4. Optionally connect an image. It becomes the primary reference; Concepts and Instructions request changes to it. Appearance replacements change the caption, not the image pixels.
5. Connect **prompt** to your text encoder. For a separate tagger, use **description**, which stays prose even when prompt is JSON.

Default canvas is 1024×1024. Aspect presets choose fixed dimensions. **From image when connected** takes priority over these settings and uses the processed image size, aligned to multiples of 16. **Manual** keeps your canvas choice with a reference image. Connect Width/Height outputs to your latent node if you want the diffusion generation size to match; prompt context alone does not change latent size.

## Outputs

| Output | Meaning |
| --- | --- |
| prompt | Prose or validated native MOSS JSON, depending on Output format |
| description | Prose scene; MOSS reference mode uses summary.caption |
| moss_json | Native centered-pixel yxyx JSON; inactive in Prose mode |
| width / height | Resolved canvas dimensions |
| image | Resized reference pixels; inactive without a reference |
| status / report | ok, warning or blocked, with diagnostics and original generation details |

Inactive image/JSON outputs skip their downstream branches. They do not output a fake image or empty JSON. A failed layout conversion blocks prompt and moss_json while keeping any valid prose and diagnostics available. Genuine model/runtime failures still raise errors.

## Generation and controls

- Text Prose uses one scene generation. Text MOSS first writes a concrete scene, then converts it into a spatial layout, with at most one schema correction. It costs more inference time.
- Reference mode uses the existing grounded vision captioner and its bounded correction path. It prioritizes the image instead of random scene suggestions. The seed is for text scene invention; vision captioning is deterministic.
- Text-layout drafts use top-left pixel xyxy coordinates on the chosen canvas, wrapped in layout_draft or as a root summary/items draft without coordinate metadata. Native centered layouts require explicit abs_centralized/yxyx metadata. Draft conversion never guesses coordinate space from numeric values. Reference drafts use the vision captioner's normalized coordinate contract.
- Length targets are approximate: Short 40–70, Balanced 80–130, Detailed 140–220 useful words. Max tokens is a ceiling per stage, not a requested word count. Prefer 4096 for MOSS.
- Randomize changes the seed for the next queued run. Fixed repeats directions and permits ComfyUI caching. A seed cannot guarantee globally unique scenes.
- Direct / explicit requests precise supplied wording. Appearance Overrides supports exact size post-editing; the report records edits separately from model output. Other trait semantics remain model-guided and may need review.
- Unload assistant model offloads this encoder once the entire request finishes, including failures. It does not unload between the prose and layout stages.
- Upload Images can supply a list of differently sized images, processed individually by native list mapping. Connect filename to source_name; keep Image index at 0 for that list. A tensor IMAGE batch uses Image index to choose one image.

## Comparison workflows

- [Scene Composer beside Archmage](../workflows/next/archmage_beta_compare.json): shared appearance recipe and fixed seed; Archmage additionally receives portrait canvas context. Compare outputs, not word-for-word equality.
- [Text to MOSS](../workflows/next/archmage_beta_text_moss.json): landscape scene invention and spatial JSON.
- [Uploaded references to MOSS](../workflows/next/archmage_beta_reference_moss.json): add your own images to Upload Images after opening the workflow.

The beta does not perform vocabulary-validated Danbooru tagging. Feed description to a separate tagger when desired. Valid MOSS structure verifies schema and box bounds, not semantic correctness or exact diffusion placement.

## Thinking mode

Try the [thinking-enabled MOSS example](../workflows/next/archmage_beta_thinking_moss.json), which selects the locally tested Qwen3.5 9B filename. Choose an equivalent compatible model if your checkpoint has a different filename.

Thinking mode is optional and defaults to off, preserving older beta workflows. Turn it on to request native model thinking during scene writing, reference captioning and MOSS layout conversion. Archmage adds concrete composition checks for focal hierarchy, negative space, perspective, light and spatial relationships. Better aesthetics or instruction following are not guaranteed.

Use **Generation token limit = 8192** as a starting point; try **16384** for complex layouts. The ceiling includes thinking plus the final answer, per stage. Archmage does not silently increase your chosen budget. Thinking takes longer and may leave no final answer if the budget runs out. That condition blocks dependent prompt outputs and displays a message suggesting a larger budget or disabling thinking. Any already completed prose scene remains available if the layout stage exhausts its budget.

A compatible model and loader are required. In local checks, Qwen3-VL 4B did not return a separate thinking segment when requested. The installed Qwen3.5 loader explicitly handles the switch. The local Qwen3.5 9B heretic checkpoint returned separate thinking output in scene writing, MOSS conversion and reference captioning checks. The text-to-layout test took about 217 seconds; its cube/sphere positions were ordered correctly, but it also added an unrequested person. These checks do not establish an overall quality improvement. Check the report's thinking_requested and thinking_output_detected fields; a switch being on does not prove the model used thinking. If no separate thinking output is detected for a completed stage, the result continues with a visible warning rather than claiming thinking was confirmed.

Native thinking output is kept separate from final text. Prompt, description, JSON preview and reports do not contain the thinking trace; diagnostics record only whether a separate thinking output was detected. Existing Scene Composer and Image to Text nodes keep thinking off by default.

## Style / theme templates

Choose **Style / theme** to guide the visual treatment instead of relying on the model's cinematic defaults. The 30 presets include amateur Instagram, casual phone snapshots, selfies, mirror selfies, direct flash, disposable/instant film, documentary, street/travel photography, studio portrait, editorial fashion, product, food, interiors, cinematic film still, everyday anime, anime key visual, sci-fi/fantasy anime, monochrome manga, sci-fi concept art, cyberpunk, fantasy painting, watercolor, oil painting, storybook, stylized 3D, pixel art and graphic poster.

**None (model choice)** preserves previous behavior. **Random preset** chooses deterministically from the presets using the seed; randomize the seed to choose again. **Custom** requires Custom style notes. You can also use those notes to refine any preset, for example `cheap phone camera, flat afternoon light, no color grading`.

Active style templates remove competing random camera and lighting suggestions. Unguided casual-photo scenes use everyday locations/actions; sci-fi/fantasy presets use matching scene suggestions. Explicit concepts/instructions and selected appearance traits take priority. Templates guide model-generated text; they are not LoRAs or guaranteed rendering styles. Style names are not added as visible text or logos.

With a reference image, **Reference style → Preserve reference style** ignores the dropdown/notes and preserves the image's medium by default. Choose **Apply selected style** to restyle its generated caption while retaining subjects, layout and other unrequested details. This never edits reference pixels. It works for prose and MOSS layouts. The report records the selected/resolved style and whether it was applied.
