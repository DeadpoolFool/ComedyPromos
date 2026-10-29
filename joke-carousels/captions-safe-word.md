# Safe Word (`out/split_safe_word_1-2.jpg`)

Build: `python3 joke-carousels/split_posts.py joke-carousels/safe_word.json`, rename slide 2 to 3, then `python3 joke-carousels/list_slide.py <portrait still> joke-carousels/out/split_safe_word_2.jpg "No," "don't stop," ...`

Wording is the Notion Joke field plus the tags that land on tape (Structure notes, 2026-10-11): the safe word in one breath, "I'm enjoying this very much", and "you gotta say it in exactly the same order" as the button. Tape score 7.94 laughs/min (15 deliveries, #2 in the 10/7 rankings).

Background: The Stand NYC, 03/21/26 (`TheStand 03_21_26_ArtemMashkov.mov`, 1080p ProRes, locked-off camera), Artem's best Safe Word night (11.41/min). First carousel off the Broadway red curtain. Fixed crop (x 540, y 110, 920x573) so the STAND sign sits in the same spot on every photo, then AI super-resolution (EDSR x2) to 2160x1344.

v2 (Artem, 2026-10-29): the whole safe word sits on one slide as a list down the right side of a single photo, and the mic is up at his mouth in every shot.
- Slide 1: neutral 150.5 "The rest of the set will be spicy..." / smile 24.0 "The safe word is..."
- Slide 2: one photo (36.5, portrait crop) + the list, built with `list_slide.py`
- Slide 3: neutral 183.5 "You gotta say it..." / smile 219.5 "...in exactly the same order."
Stills are in `photos/stills-bank/thestand-2026-03-21/` (the portrait crop is in `portrait/`). 208 was dropped because the mic is down at his waist.

Caption options (one deadpan line, no punch hint):
- the rest of the set will be spicy
- we have a safe word now
- house rules
- establishing boundaries
- please memorize this
