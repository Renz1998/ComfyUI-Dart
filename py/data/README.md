# Offline Tag Composer vocabulary

`tag_vocabulary.json.z85` is a zlib-compressed UTF-8 JSON vocabulary encoded as ASCII Base85, decoded by Python standard-library modules. It contains no images, model weights or executable code. Generation does not download data.

Source: [Mexes/danbooru-tag-taxonomy](https://huggingface.co/datasets/Mexes/danbooru-tag-taxonomy), revision `60652e06f1b50af7ab3ab0f13c63e7082fdfd9e3`, snapshot October 2, 2026; 112,570 rows. Credit **Mexes** for the classification and **Danbooru** for tag names, aliases and counts. Classification is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). See the source card's license and attribution section.

Transformation: keep tag, Danbooru category, semantic slot, post count and aliases; serialize compactly and compress. Internal IDs refer to this pinned row order only. The embedded manifest records source revision and CSV SHA-256. Do not carry IDs across vocabulary revisions.

Primary spellings are the dataset's spellings, including historically preserved names. They are not asserted to be current Danbooru canonical names. Semantic slots are provider annotations, not definitive contradiction rules. Alias collisions retain all matching candidates. No artist tags are included by the source.
