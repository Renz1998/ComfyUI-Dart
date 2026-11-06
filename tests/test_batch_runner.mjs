import assert from 'node:assert/strict';
import {planBatch, submitBatch, installBatchRunner} from '../web/batch_runner.mjs';

const names = ['first.png','second.png','third.png','fourth.png','fifth.png'];
const snapshot = {output: {
    '1': {class_type:'DanbooruTagsTransformerImageBatchUpload',inputs:{images:JSON.stringify(names),index:999,wrap_index:true,max_images:2,batch_mode:'One image per queued run'}},
    '2': {class_type:'ImageScale',inputs:{image:['1',0]}},
    '3': {class_type:'DanbooruTagsTransformerArchmageBeta',inputs:{image:['2',0],image_index:99,seed:123}},
    '4': {class_type:'SaveImage',inputs:{images:['2',0],filename_prefix:'test'}},
    '5': {class_type:'DanbooruTagsTransformerImageToText',inputs:{image:['6',0],image_index:3}},
    '6': {class_type:'LoadImage',inputs:{image:'unrelated.png'}}},
    workflow:{nodes:[{id:1,dart_widget_values:{index:999}},{id:3,dart_widget_values:{image_index:99}}]}};
const original = JSON.stringify(snapshot);
const plan = planBatch(snapshot,1,names,false,'run-a');
assert.equal(plan.length,5);
const jobs = [...plan];
for (const [i,job] of jobs.entries()) {
    assert.deepEqual(JSON.parse(job.output['1'].inputs.images),[names[i]]);
    assert.equal(job.output['1'].inputs.index,0);
    assert.equal(job.output['1'].inputs.max_images,1);
    assert.equal(job.output['1'].inputs.batch_mode,'One image per queued run');
    assert.equal(job.output['3'].inputs.image_index,0);
    assert.equal(job.output['5'].inputs.image_index,3);
    assert.equal(job.output['3'].inputs.seed,123);
    assert.equal(job.output['4'].class_type,'SaveImage');
    assert.equal(job.workflow.nodes[0].dart_widget_values.index,0);
    assert.equal(job.workflow.extra.prompt_mage_batch.position,i+1);
}
assert.equal(JSON.stringify(snapshot),original,'Never rewrite the live editor/template.');
assert.notEqual(jobs[0].output['1'].inputs.batch_run_id,[...planBatch(snapshot,1,names,false,'run-b')][0].output['1'].inputs.batch_run_id);
const list = [...planBatch(snapshot,1,names,true,'list')];
assert.equal(list.length,1);
assert.deepEqual(JSON.parse(list[0].output['1'].inputs.images),names);
assert.equal(list[0].output['1'].inputs.max_images,5,'Do not inherit a manual limit of 2.');
assert.equal(list[0].output['1'].inputs.batch_mode,'All selected images as list');
for (const count of [20,100,512]) {
    const many=Array.from({length:count},(_,i)=>`image-${i}.png`);
    assert.equal(planBatch(snapshot,1,many,false,'many').length,count);
    const [all]=planBatch(snapshot,1,many,true,'many');
    assert.equal(all.output['1'].inputs.max_images,count);
    assert.equal(JSON.parse(all.output['1'].inputs.images).length,count);
}
assert.throws(()=>planBatch(snapshot,1,[],false,'x'),/Upload/);
assert.throws(()=>planBatch(snapshot,7,names,false,'x'),/missing/);
assert.throws(()=>planBatch({output:{'1':snapshot.output['1']},workflow:{}},1,names,false,'x'),/Connect/);

let pending=0,maximum=0,calls=[];
const api={async queuePrompt(number,job){pending++;maximum=Math.max(maximum,pending);await Promise.resolve();calls.push({number,job});pending--;return {prompt_id:'job-'+calls.length};}};
assert.equal((await submitBatch(api,plan)).length,5);
assert.equal(maximum,1,'Submit in deterministic order, never parallel requests.');
assert.ok(calls.every(c=>c.number===0),'Append to native queue, not front/explicit job number.');
let done=0;
assert.equal((await submitBatch(api,plan,{stopped:()=>done>=2,progress:()=>done++})).length,2);
let attempts=0;
await assert.rejects(submitBatch({async queuePrompt(){attempts++;if(attempts===2)throw Error('connection lost');return {prompt_id:'one'};}},plan),/Confirmed 1\/5.*Check the native queue/);
assert.equal(attempts,2,'Never retry an ambiguously accepted request.');
let partial=0;
await assert.rejects(submitBatch({async queuePrompt(){partial++;return {prompt_id:'partial',node_errors:{'4':{errors:['missing model']}}};}},plan),/Confirmed 1\/5.*validation errors/);
assert.equal(partial,1,'Stop if the server accepts only a valid subset of the graph.');

class Element {
    constructor(tag){this.tag=tag;this.children=[];this.events={};this.attributes={};this.dataset={};}
    append(...xs){this.children.push(...xs);} setAttribute(k,v){this.attributes[k]=v;}
    addEventListener(k,f){this.events[k]=f;}
}
const elements=[];globalThis.document={createElement(tag){const e=new Element(tag);elements.push(e);return e;}};
const node={id:1,properties:{},widgets:[{name:'images',value:JSON.stringify(names)}],addDOMWidget(){return {};},graph:{change(){}}};
let captures=0,ids=[];
const uiApi={fetchApi:async()=>({ok:true,json:async()=>({'DanbooruTagsTransformerImageBatchUpload':{input:{optional:{batch_run_id:['STRING']}}}})}),
    queuePrompt:async(_,job)=>{ids.push(job);return {prompt_id:'ui-'+ids.length};}};
installBatchRunner(node,uiApi,{graphToPrompt:async()=>{captures++;return snapshot;}});
const start=elements.find(e=>e.tag==='button'&&e.textContent.includes('Run all'));
const toggle=elements.find(e=>e.tag==='input');
assert.equal(toggle.checked,false);
await start.events.click();assert.equal(ids.length,5);assert.equal(captures,1);
toggle.checked=true;toggle.events.change();assert.equal(node.properties.mage_batch_mode,true);
ids=[];await start.events.click();assert.equal(ids.length,1);assert.equal(JSON.parse(ids[0].output['1'].inputs.images).length,5);
assert.ok(elements.some(e=>e.textContent?.includes('Queued does not mean finished')));
console.log('Batch runner: five complete jobs vs one list job, fresh starts, immutable capture, scoped index reset, stop/error handling and UI toggle passed.');
