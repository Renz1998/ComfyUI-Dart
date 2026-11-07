import assert from 'node:assert/strict';
import {bindWorkflowEncoders, arrangeArchmage} from '../web/archmage_ui.mjs';
const mage = () => ({class_type:'DanbooruTagsTransformerArchmageBeta', inputs:{local_model:'Automatic'}});
const loader = {class_type:'CLIPLoader',inputs:{clip_name:'qwen35ForMossImage_v10_int8.safetensors'}};
const encode = {class_type:'CLIPTextEncode',inputs:{clip:['2',0], text:['1',0]}};
let snapshot = {output:{1:mage(),2:loader,3:encode}};
bindWorkflowEncoders(snapshot);
assert.deepEqual(snapshot.output[1].inputs.clip,['2',0]);
// Explicit connection/filename wins. Two consumers with different encoders remain unbound.
for (const settings of [{local_model:'chosen.safetensors'}, {local_model:'Automatic',clip:['9',0]}]) {
    snapshot = {output:{1:{...mage(),inputs:settings},2:loader,3:encode}};
    bindWorkflowEncoders(snapshot); assert.deepEqual(snapshot.output[1].inputs,settings);
}
snapshot={output:{1:mage(),2:loader,3:encode,4:loader,5:{...encode,inputs:{clip:['4',0],text:['1',0]}}}};
bindWorkflowEncoders(snapshot);assert.equal(snapshot.output[1].inputs.clip,undefined);
snapshot={output:{1:{class_type:'DanbooruTagsTransformerArchmageBeta',inputs:{assistant_backend:'OpenAI API',clip:['2',0]}},2:loader,3:encode}};
bindWorkflowEncoders(snapshot);assert.equal(snapshot.output[1].inputs.clip,undefined);
snapshot={output:{1:mage(),2:{class_type:'LoraLoader',inputs:{clip:['4',0],model:['1',0]}},3:encode,4:loader}};
bindWorkflowEncoders(snapshot);assert.equal(snapshot.output[1].inputs.clip,undefined); // no dependency cycle
snapshot={output:{1:mage(),2:{...loader,inputs:{clip_name:'clip_l.safetensors'}},3:encode}};
bindWorkflowEncoders(snapshot);assert.equal(snapshot.output[1].inputs.clip,undefined);
// Visual reordering does not drop controls or produce duplicate sections on configure.
const node={type:'DanbooruTagsTransformerArchmageBeta',widgets:[{name:'concepts'},{name:'style_preset'},{name:'width'}],
 addCustomWidget(widget){this.widgets.push(widget);return widget;}};
arrangeArchmage(node); arrangeArchmage(node);
assert.equal(node.widgets[1].name,'style_preset');
assert.equal(new Set(node.widgets).size,node.widgets.length);
assert.equal(node.widgets[0].serialize,false);
assert.deepEqual(node.widgets[0].computeSize(),[0,30]);
const painted=[];
const ctx={save(){},restore(){},fillRect(...args){painted.push(args);},fillText(text,x,y){painted.push([text,x,y]);}};
node.widgets[0].draw(ctx,node,420,200,30);
assert.ok(painted.filter(x=>typeof x[0]==='number').every(([x,y,w,h])=>y>=200 && y+h<=230));
assert.equal(painted.at(-1)[2],215);
console.log('Automatic encoder sharing, ambiguity, cycle prevention and grouped controls passed.');
