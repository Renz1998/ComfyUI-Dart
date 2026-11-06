import json
from .base import BaseNode
from ..dart.local_assistant import local_models,load_local_clip
from ..dart.memory import offload_after
from ..dart.tag_composer import compose,MODES,LENGTHS
from ..dart.vocabulary import vocabulary
from ..dart.appearance import override_instructions,check_appearance_wording,AppearanceMismatch

class PromptMageTagComposer(BaseNode):
    CATEGORY='Prompt Mage/Assistants'
    DESCRIPTION='Develop an idea into vocabulary-checked, sorted booru tags using local Qwen. No DART or training needed. Dataset spelling profile; valid tags do not guarantee semantic or image accuracy.'
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{
            'idea':('STRING',{'default':'1girl','multiline':True,'tooltip':'Seed tags or a rough idea. Invent develops unspecified details; explicit tags remain requirements.'}),
            'creativity':(MODES,{'default':'Invent','tooltip':'Invent develops a scene; Expand adds modest details; Faithful requests no inventions. Inspect notes: semantic fidelity remains model-guided.'}),
            'length':(LENGTHS,{'default':'Balanced','tooltip':'Useful detail target, not an instruction to pad with unrelated tags.'}),
            'seed':('INT',{'default':0,'min':0,'max':2**32-1,'control_after_generate':'randomize','tooltip':'Randomize changes the seed for the next queued run; fixed intentionally repeats the scene and allows caching.'}),
        },'optional':{
            'appearance':('ATELIER_APPEARANCE',{'tooltip':'Optional character recipe. Selected traits guide the scene; unavailable tag equivalents are reported rather than invented.'}),
            'local_model':(['Automatic']+local_models(),{'default':'Automatic'}),
            'clip':('CLIP',{'tooltip':'Optional generation-capable Qwen CLIP; overrides Local model.'}),
            'instructions':('STRING',{'default':'','multiline':True,'tooltip':'Creative directions. Cannot change the response schema or allow invented vocabulary IDs.'}),
            'avoid':('STRING',{'default':'','multiline':True,'tooltip':'Exclusions passed to planning/selection. Exact comma-separated vocabulary tags are also excluded by code; prose exclusions remain model-guided.'}),
            'max_tokens':('INT',{'default':2048,'min':512,'max':8192,'step':256,'tooltip':'Per-call generation ceiling. At most three calls, including one repair; this is not a word target.'}),
            'unload_after_generation':('BOOLEAN',{'default':False,'tooltip':'Offload this assistant after all stages, including on failure. Keep off to reuse the same encoder.'})}}
    RETURN_TYPES=('STRING',)*6
    RETURN_NAMES=('tags','prompt','description','scene_json','status','report')
    FUNCTION='generate'
    OUTPUT_NODE=True
    @classmethod
    def IS_CHANGED(cls,**kwargs):return vocabulary().digest
    def generate(self,idea,creativity='Invent',length='Balanced',seed=0,local_model='Automatic',clip=None,instructions='',avoid='',max_tokens=2048,unload_after_generation=False,appearance=None):
        replacements,trigger=override_instructions(appearance)
        if not idea.strip() and creativity!='Invent':raise ValueError('Use Invent for an empty idea, or enter concepts for Faithful/Expand.')
        effective_idea=idea.strip() or '1girl'
        instructions=instructions+replacements
        from comfy_extras.nodes_textgen import TextGenerate
        encoder=load_local_clip(local_model,clip)
        with offload_after(encoder,unload_after_generation):
            def invoke(system,payload,stage):
                sampling={'sampling_mode':'off'} if creativity=='Faithful' else {'sampling_mode':'on','temperature':0.7 if stage==1 else 0.25,'top_k':40,'top_p':0.9,'min_p':0.05,'repetition_penalty':1.05,'seed':seed+stage-1}
                return TextGenerate.execute(clip=encoder,prompt=payload,max_length=max_tokens,sampling_mode=sampling,thinking=False,system_prompt=system,mtp='off').args[0]
            try:tags,description,scene,report=compose(effective_idea,creativity,length,seed,instructions,avoid,invoke)
            except (ValueError,TypeError,KeyError) as error:
                tags='';description='';scene={}
                report=dict(status='blocked',issues=['The model could not produce a usable structured tag plan: '+str(error),'Try Short/Balanced or a stronger instruction model. Scene Composer provides prose without requiring planner JSON.'],seed=seed)
        if trigger and description and trigger not in description:description=trigger+', '+description
        if description:
            try:check_appearance_wording(description,appearance,'scene description')
            except AppearanceMismatch as error:
                report['issues'].extend(item['message'] for item in error.issues);report['status']='warning'
            scene['description']=description
        report['requested_idea']=idea
        report['character_trigger']=trigger
        status=report['status'];details=json.dumps(report,ensure_ascii=False,indent=2)
        prompt=trigger+', '+tags if trigger and tags and trigger not in tags.split(', ') else tags
        report['user_literals']=[trigger] if trigger else []
        details=json.dumps(report,ensure_ascii=False,indent=2)
        values=(tags,prompt,description,json.dumps(scene,ensure_ascii=False,indent=2),status,details)
        if status=='blocked':
            from comfy_execution.graph import ExecutionBlocker
            values=tuple(ExecutionBlocker(None) for _ in range(4))+(status,details)
        return {'ui':{'text':[tags], 'mage_report':[report]},'result':values}
