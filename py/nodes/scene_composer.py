from ..dart.openai_assistant import execute_generation
import json
import re
from .base import BaseNode
from ..dart.local_assistant import local_models,load_local_clip
from ..dart.memory import offload_after
from ..dart.scene_variation import variation
from ..dart.appearance import override_instructions,check_appearance_wording,AppearanceMismatch
from ..dart.size_edit import edit_text
from ..dart.text_output import final_text

VISIBLE_EXPRESSIONS={
    'playful curiosity':'a slight head tilt and raised eyebrows',
    'quiet determination':'a steady gaze and a firm mouth',
    'suspenseful anticipation':'eyes directed toward the scene focal point, with lips slightly parted',
    'joyful surprise':'raised eyebrows and an open smile',
    'thoughtful solitude':'a lowered gaze and relaxed mouth',
    'restless energy':'an alert gaze and an asymmetrical stance',
    'dreamlike wonder':'wide eyes and a slightly lifted chin',
    'calm confidence':'a level chin, relaxed shoulders and a slight smile',
}

class PromptMageSceneComposer(BaseNode):
    CATEGORY='Prompt Mage/Assistants'
    DESCRIPTION='Invent varied scenes for your character. Empty concepts invents a scene; concepts/instructions guide it. Connect Appearance Overrides to retain character traits. Outputs prose directly, without a JSON-planning requirement.'
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{
            'concepts':('STRING',{'default':'','multiline':True,'tooltip':'Optional idea, location or concepts. Blank invents a new scene around your character using seeded creative directions.'}),
            'length':(['Short','Balanced','Detailed'],{'default':'Balanced','tooltip':'Short: 40–70 words; Balanced: 80–130; Detailed: 140–220. Add visible scene detail, not emotional narration or padding. Approximate targets.'}),
            'seed':('INT',{'default':0,'min':0,'max':2**32-1,'control_after_generate':'randomize','tooltip':'Randomize changes the seed for the next queued run. Fixed repeats the same creative directions and permits ComfyUI caching.'})},
            'optional':{
            'appearance':('ATELIER_APPEARANCE',{'tooltip':'Optional character recipe. Its trigger and selected traits take priority over creative directions.'}),
            'instructions':('STRING',{'default':'','multiline':True,'tooltip':'Guide the scene, aesthetic and writing. Explicit instructions take priority over random suggestions.'}),
            'local_model':(['Automatic']+local_models(),{'default':'Automatic','tooltip':'Uses an installed full generation-capable Qwen model. Automatic prefers a small general model; CLIP overrides it.'}),
            'clip':('CLIP',{'tooltip':'Optional full generation-capable encoder; overrides Local model.'}),
            'max_tokens':('INT',{'default':1024,'min':128,'max':8192,'step':128,'tooltip':'Maximum generated tokens for the prose response. Increase if a long scene is cut off; this does not force a word count.'}),
            'unload_after_generation':('BOOLEAN',{'default':False,'tooltip':'Offload this assistant after generation, including errors. Leave off to reuse it.'})}}
    RETURN_TYPES=('STRING',)*4
    RETURN_NAMES=('prompt','creative_directions','status','report')
    OUTPUT_TOOLTIPS=('Generated prose prompt, ready for text encoding.','Seeded suggestions used for this scene.','ok or warning; inspect the report for appearance mismatches.','JSON diagnostics including seed, directions and applied text edits.')
    FUNCTION='generate'
    OUTPUT_NODE=True
    def generate(self,concepts='',length='Balanced',seed=0,appearance=None,instructions='',local_model='Automatic',clip=None,max_tokens=1024,unload_after_generation=False,thinking=False,creative_directions=None):
        if length not in ('Short','Balanced','Detailed'):raise ValueError('Choose Short, Balanced or Detailed.')
        replacements,trigger=override_instructions(appearance)
        if creative_directions is None:
            directions=variation(seed,guided=bool(concepts.strip() or instructions.strip()))
            mood=directions.pop('mood')
            if not (appearance and appearance.get('enabled') and appearance.get('traits',{}).get('expression')):
                directions['visible_expression']=VISIBLE_EXPRESSIONS[mood]
        else:
            directions=dict(creative_directions)
        target={'Short':'40–70','Balanced':'80–130','Detailed':'140–220'}[length]
        system=('Write one imaginative, coherent image-generation prompt describing a single visible frame in plain factual prose. No JSON, headings, alternatives or explanations. '
                'Describe what an illustrator or camera can show, not a story or how the scene feels. '
                'Start with the subject and visible appearance, then specify one consistent body pose, hand positions and action, '
                'clothing/materials, objects and their placement, foreground/background, viewpoint/framing, and light direction/color. '
                'Not every sentence needs every category: choose concrete useful details and avoid contradictions such as standing and kneeling simultaneously. '
                'Show emotion only through visible facial expression or posture. No internal thoughts, memories, motivations, symbolism, '
                'sensations, sounds, smells, imagined past/future events, metaphors, similes, personification or purple prose. '
                'Use direct nouns and verbs. Do not write phrases such as the sea whispers, a secret longing, as if, or a sense of wonder. '
                'Spend the word budget on visible details; do not pad to reach a target. '
                'Keep one main adult subject unless the user requests otherwise. Use the exact character trigger when provided. '
                'Preserve selected character traits and invent setting, action, composition and light around them. '
                'Use seeded directions to avoid repeating the same meadow, glowing orb or golden-hour scene. Explicit concepts, instructions and appearance replacements take priority. '
                'Do not introduce sexual details absent a request. Do not invent named characters, artists, LoRA directives or ratings. '
                f'Aim for {target} useful words without padding. '+replacements)
        payload=json.dumps(dict(concepts=concepts or 'Invent a fresh scene for the specified character or one adult woman.',instructions=instructions,creative_directions=directions,seed=seed),ensure_ascii=False)
        encoder=load_local_clip(local_model,clip)
        generation={}
        with offload_after(encoder,unload_after_generation):
            output=execute_generation(clip=encoder,prompt=payload,max_length=max_tokens,sampling_mode={'sampling_mode':'on','temperature':0.95,'top_k':60,'top_p':0.95,'min_p':0.05,'repetition_penalty':1.08,'seed':seed},thinking=thinking,system_prompt=system,mtp='off')
            text=final_text(output,thinking,generation)
        text=re.sub(r'<think>.*?</think>','',text,flags=re.S).strip()
        if not text:raise ValueError('Scene Composer returned no text. Check the generation-capable model and token limit.')
        original=text
        trigger_added=bool(trigger and trigger not in text)
        if trigger and trigger not in text:text=trigger+', '+text
        text,edits=edit_text(text,appearance)
        issues=[]
        try:check_appearance_wording(text,appearance,'scene prompt')
        except AppearanceMismatch as error:issues=[item['message'] for item in error.issues]
        report=dict(status='warning' if issues else 'ok',issues=issues,seed=seed,directions=directions,generation=generation,writing_style='visible single-frame description',post_edits=edits,model_output=original,trigger_added=trigger_added,
                    note='Seed changes vary suggestions, not a guarantee of globally unique scenes. Appearance semantics remain model-guided.')
        return {'ui':{'text':[text],'mage_report':[report]},'result':(text,json.dumps(directions,ensure_ascii=False,indent=2),report['status'],json.dumps(report,ensure_ascii=False,indent=2))}
