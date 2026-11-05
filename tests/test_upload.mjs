import assert from 'node:assert/strict';
import {readCollection,uploadImage,uploadSubfolder,uploadSessionName,installUploadWidget} from '../web/upload.mjs';
assert.deepEqual(readCollection('["a.png","b.jpg"]'),['a.png','b.jpg']);
assert.deepEqual(readCollection('{"wrong":true}'),[]);
assert.deepEqual(readCollection('[null]'),[]);
let request;
const file=new Blob(['fixture'],{type:'image/png'}); file.name='example.png';
const api={async fetchApi(path,options){request={path,options};return {ok:true,json:async()=>({name:'example (1).png',subfolder:'prompt-atelier/test',type:'input'})};}};
assert.equal(await uploadImage(file,api,'prompt-atelier/test'),'prompt-atelier/test/example (1).png');
assert.equal(request.path,'/upload/image');
assert.equal(request.options.body.get('image').name,'example.png');
assert.equal(request.options.body.get('type'),'input');
assert.equal(request.options.body.get('subfolder'),'prompt-atelier/test');
assert.equal(request.options.body.has('overwrite'),false);
await assert.rejects(uploadImage(file,{fetchApi:async()=>({ok:false,status:413})},'test'),/413/);
await assert.rejects(uploadImage(file,{fetchApi:async()=>({ok:true,json:async()=>({name:'bad',type:'output'})})},'test'),/invalid upload result/);
console.log('Upload uses native endpoint, preserves renamed paths, avoids overwrite and reports failures.');
assert.equal(uploadSessionName({randomUUID:()=> 'test-id'}),'test-id');
assert.ok(uploadSessionName({}).length>8);
assert.equal(uploadSubfolder({webkitRelativePath:'references/scene/a.png'},'base'),'base/references/scene');
assert.throws(()=>uploadSubfolder({webkitRelativePath:'../a.png'},'base'),/Invalid selected folder/);
class Element {
    constructor(tag){this.tag=tag;this.children=[];this.dataset={};this.events={};this.attributes={};this.clicks=0;}
    append(...children){this.children.push(...children);}
    setAttribute(name,value){this.attributes[name]=value;}
    addEventListener(name,fn){this.events[name]=fn;}
    replaceChildren(){this.children=[];}
    click(){this.clicks++;this.events.click?.();}
}
const elements=[];globalThis.document={createElement(tag){const el=new Element(tag);elements.push(el);return el;}};
const manifest={name:'images',value:'[]'};
let unrelatedDrops=0;
const node={properties:{},widgets:[manifest],addDOMWidget(){return {};},setDirtyCanvas(){},onDragDrop(){unrelatedDrops++;return false;}};
let calls=0;
installUploadWidget(node,{apiURL:path=>path,async fetchApi(path,{body}){calls++;return {ok:true,json:async()=>({name:body.get('image').name,type:'input',subfolder:body.get('subfolder')})};}});
elements.find(el=>el.className==='mage-dropzone').click();
assert.equal(elements.find(el=>el.tag==='input'&&!('webkitdirectory' in el.attributes)).clicks,1);
elements.find(el=>el.textContent==='Choose folder').click();
assert.equal(elements.find(el=>el.tag==='input'&&'webkitdirectory' in el.attributes).clicks,1);
assert.equal(node.onDragOver({dataTransfer:{types:['Files']}}),true);
assert.equal(node.onDragOver({dataTransfer:{types:['text/plain']}}),false);
assert.equal(await node.onDragDrop({dataTransfer:{files:[file]}}),true);
assert.equal(calls,1);assert.equal(JSON.parse(manifest.value).length,1);
assert.equal(await node.onDragDrop({dataTransfer:{files:[{name:'workflow.json'}]}}),false);
assert.equal(unrelatedDrops,1);
console.log('Large drop area, local-folder picker, whole-node image drops and non-HTTPS upload IDs passed.');
