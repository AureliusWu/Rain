define config.name = _("雨停之前")
define config.version = "0.1.0"
define config.window_title = "雨停之前 · AI Galgame"
define gui.show_name = True
define gui.about = _("一部关于雨夜、旧信与重新说出口的约定的短篇视觉小说。\n\n创作与工程：AureliusWu / AI 辅助\n引擎：Ren'Py 8.5.3\n\n当前版本为工程验证样片。")
define build.name = "BeforeTheRainStops"
define build.version = config.version
define build.destination = "dist"
define config.save_directory = "AureliusWu-BeforeTheRainStops-v1"
define config.has_sound = True
define config.has_music = True
define config.has_voice = True
define config.default_music_volume = 0.4
define config.default_sfx_volume = 0.3
define config.default_voice_volume = 0.8
define config.default_language = "schinese"
define config.default_text_cps = 32
define config.window = "auto"
define config.enter_transition = dissolve
define config.exit_transition = dissolve
define config.after_load_transition = None
define config.end_game_transition = dissolve
define config.window_icon = "gui/window_icon.png"

init python:
    # Explicit allow-list: authoring data, source assets and tools stay out of ZIP.
    build.classify("game/cache/**", None)
    build.classify("game/saves/**", None)
    build.classify("game/tests/**", None)
    build.classify("game/testcases.*", None)
    build.classify("game/data/**", None)
    build.classify("**~", None)
    build.classify("**.bak", None)
    build.classify("**.rpy", None)
    build.classify("game/**", "all")
    build.classify("README.md", "all")
    build.classify("CREDITS.md", "all")
    build.classify("LICENSE", "all")
    build.classify("licenses/**", "all")
    build.classify("**", None)
    build.documentation("README.md")
    build.documentation("CREDITS.md")
