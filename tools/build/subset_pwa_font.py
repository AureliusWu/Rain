"""Regenerate the licensed browser-control font (optional fonttools[woff] dependency)."""
import hashlib
import json
from fontTools import subset
from fontTools.ttLib import TTFont
from tools.story_model import ROOT


def main():
    source = ROOT / 'game/fonts/SourceHanSansLite.ttf'
    output = ROOT / 'tools/build/pwa/ui-font.woff2'
    inputs = ['game/data/story.json', 'game/screens.rpy', 'tools/build/web.py', 'tools/build/pwa/client.js']
    text = ''.join((ROOT / name).read_text(encoding='utf-8') for name in inputs)
    with TTFont(source) as font:
        options = subset.Options(); options.flavor = 'woff2'
        builder = subset.Subsetter(options=options); builder.populate(text=text); builder.subset(font)
        for identity, value in [(1, 'Rain Interface Sans'), (4, 'Rain Interface Sans'), (6, 'RainInterfaceSans')]:
            font['name'].setName(value, identity, 3, 1, 0x409)
        font.flavor = 'woff2'; font.save(output)
    with TTFont(output) as font:
        missing = {ord(char) for char in text if '\u3400' <= char <= '\u9fff'} - set(font.getBestCmap())
        if missing: raise ValueError('Missing Chinese glyphs: ' + ''.join(map(chr, sorted(missing))))
    report = dict(source='game/fonts/SourceHanSansLite.ttf', source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  output='tools/build/pwa/ui-font.woff2', sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                  bytes=output.stat().st_size, inputs=inputs, text_sha256=hashlib.sha256(text.encode()).hexdigest(),
                  license='licenses/SourceHanSans-OFL.txt', cjk_coverage='complete for current controls and story')
    (ROOT / 'docs/production/PWA-INPUT-FONT.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__': main()
