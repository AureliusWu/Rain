# v0.7 背景精确请求 — station_exit_after_rain

生成方式：OpenAI 内置 imagegen；具体模型标识未暴露。原始参考图：assets_source/background/station_rain_v1.png（只用于画风与建筑材质）。

```text
Use case: illustration-story.
Asset type: original 16:9 visual novel background for Before the Rain Stops, a modern fictional Chinese town named Jiangcheng.
Input images: Image 1 is only the visual style and station architecture reference. Create a NEW location image, do not modify or reproduce the reference composition.
Style: detailed hand-painted anime environment, restrained realistic architecture and perspective, matching the reference's deep navy evening sky, muted blue-grey surfaces, weathered cream concrete, dark timber, gentle warm fluorescent and amber window lighting. Quiet and grounded; no fantasy, no dramatic romance symbols.
Composition: wide landscape, eye level. Reserve lower quarter as a simple unobtrusive area behind a dialogue box. The right central area will contain an adult character sprite, so keep background readable without an object blocking that region. One single background image, no panels or montage.
Constraints: original anonymous location; no people, figures, faces, trains, brands, logos, legible writing, watermarks, UI or borders. Opaque image.
Scene: 22:16–22:26. A street-facing view outside the same small weathered station shortly after rain has nearly stopped. The station exit and its corrugated canopy recede on the right, a narrow quiet road curves away on the left, ordinary low buildings, a distant warmly lit small shop at a street corner. Wet paving and a shallow puddle catch restrained amber lights. No visible falling rain; roof edges may still be damp and drip. Deep blue-grey clouded NIGHT sky, no dawn or sunset. Camera is on the sidewalk near the station exit, safely off the road, level horizon. A plain covered place where a player could put a cardboard box by their legs and wait for a taxi, but no luggage or taxi baked into the image. No station name or readable sign.
```

## 店招清理请求

上一步完整输出保存在 assets_source/background/station_exit_after_rain_base_v1.png。以下为在该图上的精确编辑请求：

```text
Use case: precise-object-edit. Asset type: visual novel station exit background. Edit target: Image 1. Change ONLY the small illuminated shop sign above the door of the shop on the far left: replace every letter, pseudo-letter and writing on that fascia with a completely blank unmarked warm-brown wooden panel. No text anywhere. Keep the shop, its window, lights, all architecture, columns, canopy, paving, street reflections, tree, night sky, image framing and painterly style exactly the same. Keep the canvas opaque. Do not add or remove people or any other object.
```
