# Native Gallery / MusicRoom use the existing Ren'Py seen-image and seen-audio
# records. Merely visiting this screen must never mark a locked item as seen.
init python:
    renpy.music.register_channel("gallery_music", mixer="music", loop=True)
    extras_gallery = Gallery()
    extras_gallery.image_screen = "extras_image_viewer"
    extras_gallery.navigation = False
    for identity, title, filename in extras_images:
        extras_gallery.button(identity)
        extras_gallery.unlock_image(filename)

    extras_music_room = MusicRoom(channel="gallery_music", fadeout=0.0, fadein=0.3,
                                 single_track=True)
    for identity, title, filename, duration in extras_music:
        extras_music_room.add(filename)

screen extras_images_room():
    tag menu

    use game_menu("图片鉴赏"):
        vbox:
            spacing 18
            use extras_tabs("images")
            text "在故事中看过的画面，会在这里点亮。" size 27 color "#becdd7"
            text "已解锁 [extras_gallery.get_fraction(None)]" size 27 color "#9fdbe5"
            grid 3 2:
                spacing 24
                for identity, title, filename in extras_images:
                    vbox:
                        spacing 12
                        xsize 420
                        button:
                            id "extras_image_" + identity
                            style "extras_thumbnail"
                            action extras_gallery.Action(identity)
                            if extras_gallery.Action(identity) is not None:
                                add Transform(filename, xysize=(408, 230), fit="contain")
                            else:
                                fixed:
                                    xysize (408, 230)
                                    add Solid("#193444")
                                    text "未解锁" align (0.5, 0.5) size 30 color "#becdd7"
                        if extras_gallery.Action(identity) is not None:
                            text title size 28 xalign 0.5
                        else:
                            text "继续阅读后解锁" size 25 color "#8da9b8" xalign 0.5
                null width 420 height 275

screen extras_music_room_screen():
    tag menu
    # Handle both hiding the menu and replacement by settings/start/load.
    on "hide" action extras_music_room.Stop()
    on "replaced" action extras_music_room.Stop()

    use game_menu("音乐鉴赏"):
        vbox:
            spacing 28
            use extras_tabs("music")
            text "在故事中听过的音乐，可以在这里慢慢重听。" size 27 color "#becdd7"
            for identity, title, filename, duration in extras_music:
                frame:
                    background "#153342dd"
                    padding (24, 18)
                    xsize 1320
                    hbox:
                        spacing 30
                        if extras_music_room.is_unlocked(filename):
                            textbutton title:
                                id "extras_music_" + identity
                                style "extras_control"
                                xsize 900
                                action extras_music_room.Play(filename)
                            text "[duration] 秒" size 27 color "#becdd7" yalign 0.5
                        else:
                            text "未解锁音乐" size 30 color "#8da9b8" xsize 900
                            text "继续阅读后解锁" size 25 color "#8da9b8" yalign 0.5
            hbox:
                spacing 20
                textbutton "上一曲" id "extras_previous" style "extras_control" action extras_music_room.Previous()
                textbutton "下一曲" id "extras_next" style "extras_control" action extras_music_room.Next()
                textbutton "暂停 / 继续" id "extras_pause" style "extras_control" action extras_music_room.TogglePause()
                textbutton "停止" id "extras_stop" style "extras_control" action extras_music_room.Stop()
            hbox:
                spacing 30
                text "音乐音量" size 30 yalign 0.5
                bar id "extras_volume" value Preference("music volume") xsize 620 yalign 0.5
                textbutton "音乐静音" id "extras_mute" style "extras_control" action Preference("music mute", "toggle")
            text "返回或切换页面时停止播放。音量与游戏设置共用。" size 26 color "#becdd7"

screen extras_tabs(selected):
    hbox:
        spacing 24
        textbutton "图片鉴赏" id "extras_images_tab" style "extras_control" selected selected == "images" action ShowMenu("extras_images_room")
        textbutton "音乐鉴赏" id "extras_music_tab" style "extras_control" selected selected == "music" action ShowMenu("extras_music_room_screen")

screen extras_image_viewer(locked, displayables, index, count, gallery, **properties):
    modal True
    add Solid("#07131c")
    if not locked:
        for displayable in displayables:
            add displayable
    frame:
        background "#091927dd"
        padding (28, 14)
        xalign 1.0
        yalign 1.0
        textbutton "返回鉴赏室" id "extras_image_return" style "extras_control" action gallery.Return()
    key "game_menu" action gallery.Return()

style extras_thumbnail is button:
    padding (6, 6)
    background "#274754"
    hover_background "#9fdbe5"
    insensitive_background "#193444"

style extras_control is button:
    padding (20, 10)
    background "#153342dd"
    hover_background "#2b5261"
    selected_background "#285063"

style extras_control_text is button_text:
    size 30
    color "#becdd7"
    hover_color "#ffffff"
    selected_color "#a9e1e9"
    insensitive_color "#8da9b8"
