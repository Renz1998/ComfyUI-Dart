"""Seeded creative directions: no global RNG mutation or hidden execution nonce."""
import random

SCENES = [
 ('a rain-soaked night market','discovering an unusual handmade object'),
 ('an abandoned observatory','tracking a strange signal in the sky'),
 ('a coastal railway platform','waiting as an unexpected arrival approaches'),
 ('a glass-roofed botanical conservatory','examining a rare flowering plant'),
 ('a bustling rooftop festival','moving through lanterns and drifting confetti'),
 ('a snowbound mountain refuge','preparing for a journey outside'),
 ('a flooded palace courtyard','crossing reflective stepping stones'),
 ('a desert roadside diner','studying a weathered map'),
 ('an underground music venue','pausing backstage before a performance'),
 ('a sunlit ceramics studio','working on an intricate new piece'),
 ('a suspended bridge above a cloud forest','noticing something below the mist'),
 ('a neon-lit laundromat','waiting through an unexpected power flicker'),
 ('a floating archive of old books','searching for a misplaced volume'),
 ('a moss-covered stone amphitheater','rehearsing before an empty audience'),
 ('a windswept lighthouse stairway','carrying a message toward the top'),
 ('a crowded orbital transit terminal','recognizing a mysterious departure sign'),
 ('a warm attic workshop','repairing an elaborate mechanical instrument'),
 ('a quiet riverside tea stall','watching a paper boat arrive'),
 ('a luminous salt flat','following distant reflections'),
 ('a small aquarium after closing','observing a shifting school of fish'),
 ('a hillside vineyard','collecting a forgotten basket before a storm'),
 ('a retro arcade at dawn','trying one last machine'),
 ('a velvet-lined theater balcony','watching the curtains open'),
 ('a long-distance train dining car','reacting to a surprising landscape outside'),
]
LIGHT = ['hard side lighting','soft overcast light','warm practical lamps against cool ambient light','reflected light from below','a narrow shaft of daylight','backlighting with a delicate rim','colored signage reflected in glass','low winter sunlight']
FRAME = ['an intimate off-center portrait','a wide environmental composition','a low viewpoint with strong leading lines','a candid medium shot','a layered composition through a foreground object','a distant cinematic composition','a close view with a meaningful background detail']
MOOD = ['playful curiosity','quiet determination','suspenseful anticipation','joyful surprise','thoughtful solitude','restless energy','dreamlike wonder','calm confidence']

def variation(seed, guided=False):
    rng=random.Random(int(seed)); place,action=rng.choice(SCENES)
    result=dict(lighting=rng.choice(LIGHT),framing=rng.choice(FRAME),mood=rng.choice(MOOD))
    if not guided:result.update(setting=place,action=action)
    return result
