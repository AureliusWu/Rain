"""Upgrade v0.8 imports from preserved sources; repeated runs keep the same versions."""
import json
import shutil
from tools.story_model import ROOT
from tools.image_process.create_ui import main as create_ui
from tools.image_process.import_asset import import_image


def main():
    create_ui()
    manifest = json.loads((ROOT / 'game/data/asset_manifest.json').read_text(encoding='utf-8'))
    for entry in manifest['assets']:
        kind = entry['type']
        if kind not in {'sprite', 'background', 'cg', 'ui'}:
            continue
        method = entry.get('image_recipe', {}).get('method')
        if kind == 'sprite':
            target_method = 'sprite_bottom_center_810x1050_v1'
        elif kind in {'background', 'cg'} or entry['id'] == 'gui_main_menu':
            target_method = 'fit_1920x1080_v1'
        elif method == 'copy_png_v1':
            continue
        else:
            source = ROOT / 'assets_source/ui/legacy720' / entry['file'].removeprefix('gui/')
            if not source.exists():
                source.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / 'game' / entry['file'], source)
            entry['source_file'] = source.relative_to(ROOT).as_posix()
            target_method = 'copy_png_v1' if entry['id'] == 'gui_window_icon' else 'scale_150percent_v1'
        import_image(source=entry['source_file'], asset_id=entry['id'], kind=kind,
                     output=entry['file'], version=entry['version'] + (method != target_method), method=target_method,
                     prompt=entry.get('prompt'), expression=entry.get('expression', 'normal'),
                     reference_source=entry.get('reference_source_file'), prompt_components=entry.get('prompt_components'))
    print('Native 1080p migration complete; original AI requests and sources preserved.')


if __name__ == '__main__':
    main()
