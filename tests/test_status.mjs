import assert from "node:assert/strict";
import { statusView, installStatusWidget, updateStatusWidget, finishedState, combineReports } from "../web/status.mjs";

const report = {status:"warning",has_appearance:true,message:"Output continues with unconfirmed overrides.",
    issues:[{location:"MOSS summary.caption",missing:["Gigantic breasts"],conflicts:["large bust"]}],
    next_step:"Use On override mismatch on this assistant to block downstream."};
assert.match(statusView(report).detail,/Missing: Gigantic breasts/);
assert.match(statusView(report).detail,/Model used: large bust/);
assert.match(statusView(report).title,/output continues/);
assert.equal(statusView({status:"unchecked",has_appearance:false}).visible,false);
const batch=combineReports([{...report,source:'image1.png'},{...report,status:'blocked',source:'image2.png'}]);
assert.match(batch.title,/2 images/);
assert.match(batch.issues[1].location,/image2.png/);
assert.equal(finishedState({atelierLastReport:batch}),'warning');
assert.equal(statusView(combineReports([{status:'unchecked'},{status:'unchecked'}])).visible,true);
assert.match(statusView({...report,status:"blocked"}).title,/downstream blocked/);

class Element {
    constructor(tag){this.tagName=tag;this.dataset={};this.children=[];this.events={};this.hidden=false;this.open=false;}
    setAttribute(name,value){this[name]=value;}
    append(...children){this.children.push(...children);}
    addEventListener(name,callback){this.events[name]=callback;}
}
globalThis.document={createElement:tag=>new Element(tag)};
const widgets=[];
const node={size:[420,500],properties:{dart_design:false},
    addDOMWidget(name,type,element,options){const widget={name,type,element,options};widgets.push(widget);return widget;},
    computeSize(){return [420,500];},setSize(size){this.size=size;},setDirtyCanvas(){}};
installStatusWidget(node);
assert.equal(widgets[0].serialize,false);
assert.equal(widgets[0].hidden,true);
updateStatusWidget(node,report);
const root=widgets[0].element;
assert.equal(root.hidden,false); // Feedback remains visible with Mage designs disabled.
assert.equal(root.dataset.status,"warning");
assert.equal(root.open,true); // The cause is shown without needing another click.
assert.match(root.children[1].textContent,/Gigantic breasts/);
assert.equal(finishedState(node),"warning");
root.open=true;
root.events.toggle();
assert.equal(widgets[0].options.getMinHeight(),250);
updateStatusWidget(node,{...report,status:"blocked",message:"<script>example</script>"});
assert.match(root.children[1].textContent,/<script>example<\/script>/);
assert.equal(root.children[1].innerHTML,undefined); // Report text cannot inject markup.
assert.equal(finishedState(node),"blocked");
updateStatusWidget(node,{status:"ok",has_appearance:true,message:"Confirmed",issues:[]});
assert.equal(finishedState(node),"done");
assert.equal(root.children[1].textContent,"Confirmed"); // Previous warnings are cleared.
console.log("Status feedback distinguishes warnings/blocking, remains visible, and renders report text safely.");
