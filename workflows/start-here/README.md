# Start here

Drag one JSON file into ComfyUI. **01 and 02 make prompts; 03 generates images.**

| I want to… | Open | What to connect / change |
| --- | --- | --- |
| Write a scene for a character | [01 · Write a scene](01-write-a-scene.json) | Optional appearance settings → Archmage. Send **prompt** to your positive text encoder. |
| Describe my photos | [02 · Describe uploaded images](02-describe-uploaded-images.json) | Drop photos on Upload Images. Use **Run all images from first**; batch off runs the whole connected workflow per image. |
| Generate with MOSS | [03 · Full MOSS workflow](03-moss-full-workflow.json) | Select your installed MOSS diffusion model, compatible full Qwen encoder and Flux.2 VAE. Run. |
| Use random DART ideas with my character | [06 · DART ideas → Archmage](06-dart-ideas-to-archmage.json) | DART tags feed source_tags; Appearance Overrides and the selected style define the character/treatment. This example makes prompts, not images. |

In Archmage, **Scene idea = WHAT** (a mage in a red cloak taking a hotel mirror selfie). **Writing rules = HOW** (fully clothed, sharp focus throughout, no extra people). Either field can be empty. Style supplies the visual treatment; Bright lifestyle is the new default.

**Resolution** sends the same width/height to Archmage and the empty latent. Change its megapixels or aspect ratio once. It creates no latent itself, so you can use it with other generation models.

The full MOSS example uses base-model settings: 1 MP, 50 steps, Euler, shift 5, CFG 3. No private character LoRA or accelerator is included. Select your actual filenames; examples cannot install model weights for you. Archmage shares the loaded Qwen encoder. Thinking is off in this example to keep the first run shorter; new standalone Archmage nodes keep your requested thinking-on default. This graph is a starting point, not an exact copy of a distilled/LoRA workflow. [Official MOSS guide](https://github.com/OpenMOSS/MOSS-Image/blob/main/USERGUIDE.md).

## Compare prose and JSON fairly

Use [04 · Prose](04-compare-prose.json), then [05 · JSON](05-compare-json.json), with the **same model files**. Both use fixed scene/image seeds and identical generation settings. Only the Archmage output format changes. Its **description** output is the prose used to construct JSON; **moss_json** adds spatial boxes while retaining the full description in `summary.caption`.

JSON layout is experimental and can render worse than prose. Longer JSON does not imply sharper images. Keep whichever format works best with your checkpoint. A beach photo and an indoor mirror selfie also differ in light, framing and material detail, so that comparison alone cannot isolate format quality.

[Older / specialized examples](../next/README.md) · [Archmage controls](../../docs/ARCHMAGE_BETA.md)
