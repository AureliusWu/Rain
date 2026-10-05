"""Recreate the native 1080p project-owned blue GUI primitives."""
import json
from PIL import Image, ImageDraw
from tools.story_model import ROOT
from tools.image_process.import_asset import import_image


def main():
    manifest = json.loads((ROOT / 'game/data/asset_manifest.json').read_text(encoding='utf-8'))
    by_file = {a['file']: a for a in manifest['assets']}

    def save(relative, image):
        source = ROOT / 'assets_source/ui/v3' / relative
        source.parent.mkdir(parents=True, exist_ok=True)
        if source.exists():
            with Image.open(source) as previous:
                previous.load()
                if previous.mode != image.mode or previous.size != image.size or previous.tobytes() != image.tobytes():
                    raise ValueError('Changed GUI pixels require a new source and asset version: ' + relative)
        else:
            image.save(source)
        entry = by_file['gui/' + relative]
        import_image(source=source.relative_to(ROOT).as_posix(), asset_id=entry['id'], kind='ui',
                     output=entry['file'], version=3, method='copy_png_v1',
                     source_label='Original procedural GUI; tools/image_process/create_ui.py', license_name='Project MIT')

    for name in ['main_menu', 'game_menu']:
        image = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 416, 1079), fill='#071622c9')
        draw.line((417, 0 if name == 'main_menu' else 180, 417, 1035), fill='#7ebbc8', width=3)
        save('overlay/' + name + '.png', image)
    sizes = {
        ('slider', 'horizontal', 'bar'): (525, 45), ('slider', 'horizontal', 'thumb'): (22, 45),
        ('slider', 'vertical', 'bar'): (45, 525), ('slider', 'vertical', 'thumb'): (45, 22),
        ('scrollbar', 'horizontal', 'bar'): (1050, 18), ('scrollbar', 'horizontal', 'thumb'): (1050, 18),
        ('scrollbar', 'vertical', 'bar'): (18, 1050), ('scrollbar', 'vertical', 'thumb'): (18, 1050),
    }
    for family in ['slider', 'scrollbar']:
        for orientation in ['horizontal', 'vertical']:
            for state in ['idle', 'hover']:
                for part in ['bar', 'thumb']:
                    color = ('#284b5d' if state == 'idle' else '#37697b') if part == 'bar' else ('#91d4e0' if state == 'idle' else '#d1f3fa')
                    save(f'{family}/{orientation}_{state}_{part}.png', Image.new('RGBA', sizes[family, orientation, part], color))
    for name in ['radio', 'check']:
        image = Image.new('RGBA', (38, 54), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        # Explicit rounded caps keep identical pixels across Pillow releases.
        for box in [(4, 10, 12, 43), (5, 9, 11, 44), (6, 8, 10, 45)]:
            draw.rectangle(box, fill='#91d4e0')
        save(f'button/{name}_selected_foreground.png', image)
    print('Imported 20 native 1080p GUI primitives with source assets and recipes.')


if __name__ == '__main__':
    main()
