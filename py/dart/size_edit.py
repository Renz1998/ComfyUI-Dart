"""Explicit user-selected size-phrase editing, separate from model generation."""
from copy import deepcopy
import re

from .appearance import person_items, target_person_items, _words, TRAITS

SIZE = re.compile(r"\b(?:an?\s+)?(?:(?:very|extremely|exceptionally|moderately)\s+)?"
                  r"(?:small|medium|large|big|huge|massive|gigantic|enormous|ample|full|flat)\s+(?:breasts?|bust|chest)\b",re.I)
PERSON = re.compile(r"\b(?:woman|man|person|girl|boy|female|male|character|subject)\b",re.I)
MULTIPLE = re.compile(r"\b(?:women|men|people|girls|boys|characters|another|second)\b",re.I)


def enabled(settings):
    return bool(settings and settings.get("enabled") and settings.get("apply_size_wording", False) and
                settings.get("traits", {}).get("breast_size"))


def _edit(text, settings, location):
    phrase = settings["traits"]["breast_size"]
    # Do not rewrite explicit refusals into a purported successful caption.
    if re.match(r"\s*(?:I (?:cannot|can't|won't)|I'm sorry|I am sorry)",text,re.I): return text, []
    protected = [(m.start(),m.end()) for m in re.finditer(r'"[^"\n]*"',text)]
    old = []
    literal = phrase.lower() if phrase in TRAITS["breast_size"] else phrase
    replacement = "a " + literal if _words(phrase) == "flat chest" else literal
    def replace(match):
        if any(start <= match.start() < end for start,end in protected): return match.group()
        current = re.sub(r"^an?\s+", "", match.group(),flags=re.I)
        if _words(current) == _words(phrase): return match.group()
        old.append(match.group())
        return replacement
    result = SIZE.sub(replace,text)
    action = "replaced size wording"
    if not re.search(r"\b"+re.escape(_words(phrase))+r"\b",_words(result)):
        reference = settings.get("trigger") or "The selected subject"
        result = result.rstrip().rstrip(".") + ". " + reference + " has " + replacement + "."
        action = "added selected size phrase"
    if result == text: return text, []
    return result, [{"location":location,"trait":"breast_size","selected":phrase,"action":action,"replaced":old}]


def edit_text(text, settings, location="description", single_person=False):
    if not enabled(settings): return text, []
    subject = settings.get("subject", "Main subject")
    if subject == "All people": return _edit(text,settings,location)
    if subject == "Main subject" and (single_person or (PERSON.search(text) and not MULTIPLE.search(text))):
        return _edit(text,settings,location)
    # In multi-person/custom scenes, edit only an unambiguous sentence naming the target.
    reference = settings.get("trigger") or (subject if subject not in ("Main subject","All people") else "")
    if not reference: return text, []
    parts = re.split(r"(?<=[.!?])\s+",text)
    edits = []
    for index,part in enumerate(parts):
        if reference in part and not MULTIPLE.search(part):
            parts[index],changes = _edit(part,settings,location)
            edits.extend(changes)
    return " ".join(parts), edits


def edit_layout(layout, settings):
    if not enabled(settings): return layout, []
    result = deepcopy(layout)
    people = person_items(result,settings)
    result["summary"]["caption"], edits = edit_text(result["summary"]["caption"],settings,"MOSS summary.caption",len(people)==1)
    for index,item in target_person_items(result,settings):
        item["caption"],changes = edit_text(item["caption"],settings,f"MOSS items[{index}].caption",len(people)==1)
        edits.extend(changes)
    return result,edits


def edit_scene(scene, settings, target):
    if not enabled(settings): return scene, []
    result = deepcopy(scene)
    result["description"], edits = edit_text(result["description"],settings)
    if target in ("DART tags","Anima hybrid") and edits:
        # Tag-only edits are safe only when the associated description identified the target.
        phrase = settings["traits"]["breast_size"]
        result["tags"] = [tag for tag in result["tags"] if not SIZE.search(_words(tag))] + [phrase.lower() if phrase in TRAITS["breast_size"] else phrase]
        edits.append({"location":"tags","trait":"breast_size","selected":phrase,"action":"set size tag","replaced":[]})
    return result,edits


def edit_structured(value, settings):
    if not enabled(settings): return value, []
    result = deepcopy(value)
    result["description"],edits = edit_text(result["description"],settings,single_person=len(result["subjects"])==1)
    for index,text in enumerate(result["subjects"]):
        result["subjects"][index],changes = edit_text(text,settings,f"subjects[{index}]",len(result["subjects"])==1)
        edits.extend(changes)
    return result,edits
