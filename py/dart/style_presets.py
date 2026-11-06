"""Concrete style templates, independent of model weights and global random state."""
import random

STYLES = {
    'Photo · Amateur Instagram': ('An ordinary personal Instagram photo taken by a friend on a phone: casual everyday framing, available light, believable skin texture, everyday surroundings, slight handheld imperfections. No cinematic grading, dramatic rim lighting, professional retouching or exaggerated background blur.', 'everyday'),
    'Photo · Casual phone snapshot': ('A quick handheld smartphone snapshot, ordinary exposure and natural colors, informal composition, modest depth of field, believable everyday detail. Avoid staged cinematic lighting and film-poster framing.', 'everyday'),
    'Photo · Selfie': ('An informal front-camera phone selfie with plausible arm reach, close perspective and available light. Keep anatomy and camera placement consistent. No beauty-filter skin or cinematic grading.', 'everyday'),
    'Photo · Mirror selfie': ('A casual phone mirror selfie with physically consistent reflection, a visible phone, ordinary indoor light and everyday surroundings. Keep the subject and reflected camera placement coherent.', 'everyday'),
    'Photo · Direct flash': ('A spontaneous compact-camera or phone photo with direct on-camera flash, frontal highlights, a visible nearby cast shadow, abrupt light falloff and informal framing. No studio softbox look.', 'everyday'),
    'Photo · Disposable film': ('A casual disposable-camera photograph with modest fine grain, slightly uneven exposure, simple framing and restrained film color shifts. Do not turn it into a cinematic film still.', 'everyday'),
    'Photo · Instant film': ('An instant-film photograph with soft fine detail, gently faded colors and a straightforward snapshot composition. Do not add a physical border, date stamp or text unless requested.', 'everyday'),
    'Photo · Candid documentary': ('An observational documentary photograph: unstaged visible action, believable available light, environmental context, neutral color and practical eye-level framing.', 'everyday'),
    'Photo · Street photography': ('A candid street photograph with a clear visible moment, layered urban surroundings, practical natural light and grounded perspective. Avoid automatic neon, rain and cinematic grading.', 'everyday'),
    'Photo · Travel diary': ('An informal travel-diary photograph with a readable location, natural daylight, casual framing and realistic tourist-scale surroundings rather than a glossy tourism advertisement.', 'everyday'),
    'Photo · Studio portrait': ('A controlled studio portrait with a clear key light, restrained fill, clean backdrop, believable skin texture and deliberate portrait framing. Avoid unexplained dramatic effects.', None),
    'Photo · Editorial fashion': ('An editorial fashion photograph with clear garment construction and fabric texture, purposeful pose, coherent styling, controlled lighting and a readable fashion composition.', None),
    'Photo · Product catalog': ('A clean product photograph with a simple background, accurate material surfaces, readable object silhouette, grounded contact shadows and even controlled light. Describe the requested objects; do not add people unless requested.', None),
    'Photo · Food photography': ('An appetizing food photograph with readable ingredients, believable food texture, coherent plate and utensil placement, soft side light and a practical tabletop viewpoint. Do not add people unless requested.', None),
    'Photo · Architecture / interiors': ('An architectural or interior photograph with coherent room geometry, straight believable verticals, readable materials and practical window or interior light. Avoid impossible ultra-wide distortion.', None),
    'Photo · Cinematic film still': ('A deliberate cinematic film still with a clear focal subject, motivated directional lighting, controlled color palette, layered depth and coherent dramatic composition. No letterbox bars unless requested.', None),
    'Anime · Everyday slice of life': ('A slice-of-life anime illustration with clean linework, simple cel shading, readable expressions, ordinary everyday surroundings and a clear unforced composition.', 'everyday'),
    'Anime · Key visual': ('A polished anime key visual with crisp linework, coherent cel shading, a readable silhouette, deliberate color grouping and a clear focal hierarchy. Do not add titles or logos unless requested.', None),
    'Anime · Sci-fi': ('A science-fiction anime illustration with crisp linework, cel-shaded surfaces, coherent functional technology, readable mechanical detail and a clear subject silhouette. No automatic neon city or cinematic photo terminology.', 'scifi'),
    'Anime · Fantasy': ('A fantasy anime illustration with clear linework, cel shading, coherent costume materials and readable magical or architectural details. Keep effects subordinate to the subject silhouette.', 'fantasy'),
    'Manga · Black and white': ('A monochrome manga illustration with expressive ink linework, screentone, deliberate solid blacks and a readable single-frame composition. No panels, dialogue bubbles or lettering unless requested.', None),
    'Illustration · Sci-fi concept art': ('Science-fiction concept art with designed functional machinery, plausible scale cues, clearly organized forms, material separation and readable environment construction.', 'scifi'),
    'Illustration · Cyberpunk': ('A cyberpunk illustration with layered technology, worn urban materials, a controlled accent-color palette and readable subject separation. Use specific light sources instead of indiscriminate neon glow.', 'scifi'),
    'Illustration · Fantasy painting': ('A fantasy digital painting with coherent world details, readable silhouettes, deliberate brushwork, material variation and a clear focal hierarchy.', 'fantasy'),
    'Illustration · Watercolor': ('A watercolor illustration with transparent pigment washes, paper texture, selective soft edges and restrained detail around a clearly readable subject.', None),
    'Illustration · Oil painting': ('An oil painting with visible brushwork, layered opaque pigment, coherent light and shadow masses and purposeful edge control.', None),
    'Illustration · Children’s storybook': ('A friendly storybook illustration with simplified readable shapes, soft color grouping, expressive visible poses and clear environmental details. Do not add prose or lettering.', None),
    'Render · Stylized 3D': ('A stylized 3D render with simplified coherent geometry, tactile materials, controlled soft lighting and a readable silhouette. Avoid claiming photographic realism.', None),
    'Art · Pixel art': ('Pixel art with a consistent pixel scale, a limited intentional palette, crisp stepped edges and readable shapes. Avoid photographic lens effects and smooth painted gradients.', None),
    'Design · Graphic poster': ('A graphic poster composition with bold shape hierarchy, intentional negative space, limited colors and clean silhouettes. Only include exact visible wording explicitly requested by the user.', None),
}
STYLE_OPTIONS = ['None (model choice)', 'Random preset', 'Custom'] + list(STYLES)
WORLDS = {
    'everyday': [('a neighborhood cafe', 'pausing with a drink'), ('a lived-in apartment', 'taking a break beside a window'),
                 ('a local park', 'sitting on a bench'), ('a small grocery shop', 'browsing a shelf'),
                 ('a home kitchen', 'preparing a simple snack'), ('a familiar sidewalk', 'stopping beside a shop window')],
    'scifi': [('an orbital station concourse', 'checking a route display'), ('a spacecraft maintenance bay', 'inspecting a service panel'),
              ('a planetary research outpost', 'examining a sample container')],
    'fantasy': [('a stone courtyard garden', 'examining a carved object'), ('a small alchemist workshop', 'sorting glass vials'),
                ('a forest footbridge', 'studying a folded map')],
}


def resolve_style(selection, notes, seed):
    if selection not in STYLE_OPTIONS:
        raise ValueError('Choose a supported style preset.')
    if selection == 'Custom' and not notes.strip():
        raise ValueError('Enter Custom style notes, or choose a preset.')
    resolved = random.Random(f'prompt-mage-style:{int(seed)}').choice(list(STYLES)) if selection == 'Random preset' else selection
    guidance = STYLES.get(resolved, ('', None))[0]
    if notes.strip():
        guidance += '\nCustom style notes: ' + notes.strip()
    if guidance:
        guidance = ('Style template: ' + resolved + '. ' + guidance +
                    '\nThis is a visual style preference, not visible writing. Explicit scene instructions, subject counts and selected appearance replacements take priority. '
                    'Do not add human subjects to an objects-only concept. Do not add cinematic treatment unless the selected style or user instructions request it. ')
    return resolved, guidance


def style_directions(directions, resolved, seed, guided, active):
    result = dict(directions)
    if active:
        # Presets describe their own camera/light treatment; remove conflicting seeded suggestions.
        result.pop('lighting', None)
        result.pop('framing', None)
        world = STYLES.get(resolved, ('', None))[1]
        if world and not guided:
            place, action = random.Random(f'prompt-mage-world:{int(seed)}').choice(WORLDS[world])
            result.update(setting=place, action=action)
        elif not guided and resolved.startswith('Photo ·') and resolved != 'Photo · Cinematic film still':
            result.pop('setting', None)
            result.pop('action', None)
    return result
