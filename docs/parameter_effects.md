# Generation Parameter Effects

This document explores how key generation parameters influence the quality and character of text produced by a large language model. Each parameter is demonstrated with a before-and-after example using the same base prompt.

Base prompt for all examples: **"Describe a sunset over the mountains."**

---

### Temperature

Temperature controls the randomness of the model's token selection. A lower temperature makes the model more deterministic, favoring high-probability tokens and producing safe, predictable prose. A higher temperature encourages the model to explore less likely tokens, leading to more creative and surprising output at the cost of occasional incoherence.

**Low temperature (0.2) -- conservative, predictable output:**

```
The sun dipped below the mountain peaks, casting a warm orange glow across the
sky. The clouds were tinged with pink and gold as the last light of day faded
slowly. Shadows crept across the valley floor, and the air grew cooler. It was
a peaceful evening, quiet and still, as the mountains stood tall against the
darkening horizon. Birds returned to their nests, and the world settled into
the familiar calm of dusk.
```

**High temperature (1.5) -- creative, unpredictable output:**

```
The sun bled into the granite teeth of the ridge like a wounded god retreating
from battle, its molten copper viscera smeared across a canvas of impossible
violet and crushed tangerine. Each peak wore a crown of liquid amber that
dripped and dissolved into the crevasses below. Somewhere between the scent of
pine resin and the electric taste of altitude, the sky forgot its own name and
became something older, something that remembered fire before humans had words
for warmth.
```

The low-temperature output reads like a competent weather report -- factually accurate, well-structured, but unremarkable. The high-temperature version takes risks with metaphor and personification, producing vivid and emotionally resonant prose. The tradeoff is that very high temperatures can occasionally produce fragments that feel disjointed or semantically unstable.

---

### Top P

Top P (nucleus sampling) determines the cumulative probability threshold for token selection. The model considers only the smallest set of tokens whose combined probability exceeds the top_p value. A low top_p restricts choices to the most probable tokens, while a high top_p allows the model to draw from a broader vocabulary.

**Low top_p (0.3) -- narrow vocabulary, repetitive structure:**

```
The sun set behind the mountains. The sky turned orange and red. The mountains
were dark against the bright sky. The light faded slowly. The air was cool and
quiet. The sun disappeared behind the peaks and the sky grew darker. The stars
began to appear one by one as night settled over the mountains.
```

**High top_p (0.95) -- diverse vocabulary, varied structure:**

```
Dusk arrived like a slow exhalation across the Cascades. The ridgeline carved a
jagged silhouette against bands of saffron and deepening rose, while cirrus
clouds high above caught the last ultraviolet frequencies and shimmered with an
almost phosphorescent lavender. Down in the alpine meadow, the wildflowers
closed their petals as if acknowledging the performance was over, and a lone
hawk traced lazy thermals on the cooling air, its wingspan gilded by the final
defiant rays.
```

The low top_p example is structurally monotonous -- nearly every sentence begins with "The" and uses simple subject-verb constructions. The high top_p version employs varied sentence openings, richer vocabulary ("saffron," "phosphorescent," "thermals"), and more sophisticated syntactic patterns. The difference is not just in word choice but in the fundamental texture of the prose.

---

### Repeat Penalty

Repeat penalty discourages the model from reusing tokens that have already appeared in the generated text. A low penalty (close to 1.0) places no restriction on repetition, while a higher penalty actively suppresses recently used words and phrases, forcing the model to find alternatives.

**Low repeat penalty (1.0) -- noticeable repetition:**

```
The sunset painted the mountains in shades of gold. The mountains glowed with
golden light as the sun set behind the mountains. The sky above the mountains
turned golden and orange, and the mountains cast long shadows across the
valley. The golden light reflected off the mountain lakes, and the mountains
looked beautiful in the golden evening light.
```

**High repeat penalty (1.3) -- forced lexical variety:**

```
Amber light spilled across the western ridgeline as day surrendered its hold.
The granite faces of the range caught fire briefly, each crag and precipice
illuminated in succession like candles on an altar. Above, the firmament cycled
through its twilight palette: peach dissolving into coral, then mauve, then a
deep indigo that carried the first faint pinpricks of starlight. Cool air
descended from the snowfields, carrying the mineral scent of ancient stone.
```

The low-penalty output is nearly unreadable in places, with "mountains," "golden," and "the mountains" repeating to the point of distraction. The high-penalty version is forced to reach for synonyms and alternative constructions, which produces more varied and engaging prose. However, setting repeat penalty too high can cause the model to use awkward or unusual substitutions simply to avoid repetition, so a moderate value typically produces the best results.
