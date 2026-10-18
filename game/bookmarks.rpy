# Native persistent reading bookmarks. Authored JSON is excluded from player packages.
default rain_line_id = ""
default persistent.rain_bookmarks_v1 = {}

init python:
    import reading_bookmarks

    def rain_tag_history(entry):
        entry.rain_line_id = rain_line_id

    config.history_callbacks.append(rain_tag_history)

    def rain_merge_bookmarks(old, new, current):
        return reading_bookmarks.merge(old, new, RAIN_READING_CATALOG)

    renpy.register_persistent("rain_bookmarks_v1", rain_merge_bookmarks)

    def rain_history_identity(entry):
        return reading_bookmarks.identify(entry, RAIN_READING_CATALOG, rain_history_plain)

    def rain_is_bookmarked(identity):
        return identity in reading_bookmarks.clean_ids(persistent.rain_bookmarks_v1, RAIN_READING_CATALOG)

    def rain_toggle_bookmark(identity):
        persistent.rain_bookmarks_v1 = reading_bookmarks.toggle(persistent.rain_bookmarks_v1, identity, _history_list, RAIN_READING_CATALOG, rain_history_plain)
        renpy.save_persistent()
        renpy.restart_interaction()

    def rain_bookmark_rows(chapter=""):
        return reading_bookmarks.bookmark_rows(persistent.rain_bookmarks_v1, RAIN_READING_CATALOG, chapter)

screen rain_chapter_filter(variable):
    grid 3 3:
        spacing 8
        textbutton "全部章节":
            id (variable + "_all")
            style "history_filter_button"
            selected renpy.get_screen_variable(variable) == ""
            action [Stop("voice"), SetScreenVariable(variable, "")]
        for chapter_id, chapter_title in RAIN_READING_CHAPTERS:
            textbutton chapter_title:
                id (variable + "_" + chapter_id)
                style "history_filter_button"
                selected renpy.get_screen_variable(variable) == chapter_id
                action [Stop("voice"), SetScreenVariable(variable, chapter_id)]
        null
        null

screen rain_bookmarks():
    tag menu
    default bookmark_chapter = ""
    on "hide" action Stop("voice")
    on "replaced" action Stop("voice")
    use game_menu("已读收藏"):
        vbox:
            spacing 18
            use rain_chapter_filter("bookmark_chapter")
            text "收藏只保留已经读过的原文；查看和重听不会推进剧情。" size 24
            viewport:
                yfill True
                scrollbars "vertical"
                mousewheel True
                draggable True
                vbox:
                    spacing 18
                    for record in rain_bookmark_rows(bookmark_chapter):
                        frame:
                            xfill True
                            padding (18, 14)
                            vbox:
                                spacing 10
                                text (record["chapter_title"] + " / " + record["speaker"]) size 24
                                text record["text"] size 28 substitute False
                                hbox:
                                    spacing 16
                                    textbutton "移除收藏":
                                        id ("bookmark_remove_" + record["id"])
                                        action [Stop("voice"), Function(rain_toggle_bookmark, record["id"])]
                                    if record["voice"]:
                                        textbutton "重播语音":
                                            id ("bookmark_voice_" + record["id"])
                                            action PlayCharacterVoice(record["voice_tag"], record["voice"], selected=True)
                    if not rain_bookmark_rows(bookmark_chapter):
                        text "这一章还没有收藏。" size 28
