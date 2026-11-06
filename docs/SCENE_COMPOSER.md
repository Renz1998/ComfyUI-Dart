> Deprecated: use [Archmage](ARCHMAGE_BETA.md) for new workflows. Existing graphs remain supported.

# Scene Composer: varied scenes for a character

Add **Prompt Mage · Scene Composer** and connect **Appearance Overrides → appearance**. Leave **Concepts (blank = surprise me)** empty to invent a scene. Enter concepts or Scene instructions to guide it instead. Connect **prompt** directly to your image workflow's positive text encoder.

The **Variation seed** uses native **control after generate → randomize** for the next queued run. **Fixed** intentionally keeps the same creative directions and allows ComfyUI to reuse cached results. On older saved Tag Composer nodes, change a saved fixed control to randomize yourself; updates do not overwrite that preference. A changed seed produces different suggestions, not a guarantee of a globally unique result.

Writing now targets a concrete single visible frame: subject appearance, one consistent pose/action, hands, clothing/materials, objects and placement, foreground/background, camera framing and visible light. Mood suggestions become visible expression/posture cues (and are omitted when the recipe explicitly selects an expression). The prompt asks the model to avoid inner thoughts, sensory narration, imagined history, metaphors and poetic filler. Short/Balanced/Detailed target about 40–70/80–130/140–220 useful words, with no padding requirement. This is generation guidance, not an automatic prose-style classifier or guarantee of compliance.

Empty concepts selects a seeded setting/action pair plus framing, mood and lighting. Guided requests keep their requested setting and receive only optional mood/light/framing suggestions. Character traits and explicit instructions take priority. The model generates plain prose in one call, without a JSON-plan requirement. Short/Balanced/Detailed are approximate detail targets. All inference uses your installed local generation model.

Appearance Overrides is supported by both Scene Composer and experimental Tag Composer. Scene Composer retains the literal trigger, checks requested trait wording and reports discrepancies. If Apply exact breast-size wording edits text, the report records that edit and preserves the original model response. This does not edit image pixels or load a LoRA.

Tag Composer's `tags` output stays vocabulary-backed. Its `prompt` output may additionally contain the character trigger explicitly supplied by your recipe; that trigger is a user literal, not a verified booru tag. Some traits have no reliable tag mapping, so check the prose and report.

Tag Composer now splits overlong concept text instead of aborting at 160 characters, accepts recoverable string/missing-field concept forms with diagnostics, and sends the failed response/error to its single schema repair. Unrecoverable structured responses show a blocked report and block data outputs instead of a raw JSON traceback. Runtime/model failures still raise normally. Tag selection remains experimental and may return misleading valid tags; the prose Scene Composer is the simpler random-scene route.

Examples:

- [Random character scenes](../workflows/next/random_character_scenes.json): recipe → Scene Composer. Edit the example trigger and traits.
- [Random scene to tags](../workflows/next/random_scene_to_tags.json): the same scene feeds Tag Composer in Faithful mode, so it translates the developed scene instead of inventing another one.

Other messages in the reported log are separate: Image to Text needs a connected image; missing IPAdapterPlus belongs to Inspire Pack's dependency setup; the TAESD warning reports incompatible preview latent channels; user-interrupted diffusion runs are not text-generation exceptions. Those are not silently modified by this update.
