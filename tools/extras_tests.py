"""Native extras tests: real story unlocks, retained state and music controls."""
import json
from tools.story_model import ROOT, enumerate_routes, scene_lines
from tools.compile_story import quote

def render_extras_tests(story):
    assets = {a['id']:a['file'] for a in json.loads((ROOT/'game/data/asset_manifest.json').read_text())['assets']}
    route = next(r for r in enumerate_routes(story)['routes'] if r['ending']=='true')
    choices = {c['id']:c for n in story['nodes'] for c in n.get('choices', [])}
    first_voice = next(l['text'] for n in story['nodes'] for l in scene_lines(n) if l['id']=='s01_arrival_l005')
    lines = ['testcase extras_locked_no_spoilers:', '    run MainMenu(confirm=False)',
             '    click id "menu_extras"', '    assert screen "extras_images_room"',
             '    assert eval extras_gallery.Action("unsent_letter") is None',
             '    assert eval extras_gallery.Action("nearby_cafe") is None',
             '    assert eval "继续阅读后解锁" in renpy.get_widget("extras_images_room", "extras_locked_unsent_letter")._tts_all(False)',
             '    assert not id "extras_title_unsent_letter"',
             '    screenshot "native-extras-locked"',
             '    click id "extras_music_tab"', '    assert screen "extras_music_room_screen"',
             f'    assert eval not extras_music_room.is_unlocked({assets["unspoken_theme"]!r})',
             f'    assert eval not extras_music_room.is_unlocked({assets["next_message_theme"]!r})',
             '    assert not id "extras_music_unspoken_theme"',
             '    assert not id "extras_music_next_message_theme"',
             '    assert eval renpy.music.get_playing(channel="gallery_music") is None',
             '    screenshot "native-extras-music-locked"',
             '    click id "extras_images_tab"', '    $ renpy.set_physical_size((1280, 720))',
             '    pause until eval renpy.get_physical_size() == (1280, 720)',
             '    pause 0.3', '    screenshot "scaled-extras-locked"',
             '    click id "game_return"', '    assert screen "main_menu"', '',
             'testcase extras_unlock_and_music:']
    for identity in route['choices']:
        lines += ['    advance until screen "choice"', f'    click {quote(choices[identity]["text"])}']
    lines += ['    advance until screen "ending_card"', '    assert eval last_ending == "true"',
              '    click id "ending_return"', '    pause until screen "main_menu"',
              '    $ _test.extras_state = (affection, trust, truth_known, last_ending, list(visited_scenes))',
              '    $ _test.extras_volume = preferences.get_volume("music")',
              '    click id "menu_extras"',
              '    assert eval all(extras_gallery.Action(key) is not None for key, title, filename in extras_images)',
              '    assert eval extras_gallery.get_fraction(None) == "5/5"',
              '    screenshot "native-extras-unlocked"',
              '    click id "extras_image_unsent_letter"', '    pause until screen "extras_image_viewer"',
              '    assert id "extras_image_return"', '    screenshot "native-extras-cg"',
              '    click id "extras_image_return"', '    pause until screen "extras_images_room"',
              '    assert eval (affection, trust, truth_known, last_ending, list(visited_scenes)) == _test.extras_state',
              '    click id "extras_music_tab"',
              '    assert eval all(extras_music_room.is_unlocked(filename) for key, title, filename, duration in extras_music)',
              '    click id "extras_music_rain_theme"',
              f'    pause until eval renpy.music.get_playing(channel="gallery_music") == {assets["rain_theme"]!r}',
              '    click id "extras_next"',
              f'    pause until eval renpy.music.get_playing(channel="gallery_music") == {assets["unspoken_theme"]!r}',
              '    click id "extras_next"',
              f'    pause until eval renpy.music.get_playing(channel="gallery_music") == {assets["next_message_theme"]!r}',
              '    click id "extras_previous"',
              f'    pause until eval renpy.music.get_playing(channel="gallery_music") == {assets["unspoken_theme"]!r}',
              '    click id "extras_pause"', '    assert eval renpy.music.get_pause(channel="gallery_music")',
              '    click id "extras_pause"', '    assert eval not renpy.music.get_pause(channel="gallery_music")',
              '    click id "extras_volume" pos (0.25, 0.5)',
              '    $ print("Extras volume after real slider click:", preferences.get_volume("music"), MixerValue("music").get_mixer(), config.quadratic_volumes, config.volume_db_range)',
              '    assert eval abs(MixerValue("music").get_mixer() / (1.0 if config.quadratic_volumes else config.volume_db_range) - 0.25) < 0.06',
              '    click id "extras_mute"', '    assert eval preferences.mute["music"]',
              '    click id "extras_mute"', '    assert eval not preferences.mute["music"]',
              '    click id "extras_music_unspoken_theme"',
              f'    pause until eval renpy.music.get_playing(channel="gallery_music") == {assets["unspoken_theme"]!r}',
              '    screenshot "native-extras-music"',
              '    click id "extras_stop"', '    assert eval renpy.music.get_playing(channel="gallery_music") is None',
              '    click id "extras_music_next_message_theme"',
              f'    pause until eval renpy.music.get_playing(channel="gallery_music") == {assets["next_message_theme"]!r}',
              '    $ renpy.set_physical_size((1280, 720))',
              '    pause until eval renpy.get_physical_size() == (1280, 720)',
              '    pause 0.3', '    screenshot "scaled-extras-music"',
              '    click id "extras_images_tab"',
              '    assert eval renpy.music.get_playing(channel="gallery_music") is None',
              '    screenshot "scaled-extras-unlocked"',
              '    assert eval (affection, trust, truth_known, last_ending, list(visited_scenes)) == _test.extras_state',
              '    $ preferences.set_volume("music", _test.extras_volume)',
              '    click id "extras_music_tab"', '    click id "extras_music_rain_theme"',
              f'    pause until eval renpy.music.get_playing(channel="gallery_music") == {assets["rain_theme"]!r}',
              '    click id "menu_start"', f'    advance until {quote(first_voice)}',
              '    assert eval renpy.music.get_playing(channel="gallery_music") is None',
              f'    assert eval renpy.music.get_playing(channel="music") == {assets["rain_theme"]!r}',
              '    assert eval affection == 0 and trust == 0 and not truth_known', '']
    output = []
    for line in lines:
        if line.strip().startswith('screenshot '):
            output += ['    pause 0.3', '    pause until eval not any(renpy.get_ongoing_transition(layer) for layer in (None, "master", "screens"))']
        output.append(line)
    return output

def extras_persistence_assertions():
    return ['    assert eval all(extras_gallery.Action(key) is not None for key, title, filename in extras_images)',
            '    assert eval all(extras_music_room.is_unlocked(filename) for key, title, filename, duration in extras_music)',
            '    click id "menu_extras"', '    assert screen "extras_images_room"',
            '    screenshot "native-extras-persistent"', '    click id "game_return"',
            '    assert screen "main_menu"']
