init python:
    import replay_search

    def rain_history_plain(value):
        return renpy.filter_text_tags(value, allow=set())

    def rain_history_rows(history, query="", speaker=""):
        return replay_search.filter_history(history, query, speaker, rain_history_plain)

    def rain_history_speakers(history):
        return replay_search.history_speakers(history, rain_history_plain)

style history_search_input is input:
    size 30
    color "#e3edf1"
    xfill True

style history_filter_button is button:
    padding (12, 8)
    background Solid("#20404e")
    hover_background Solid("#315869")
    selected_background Solid("#386173")

style history_filter_button_text is button_text:
    size 26
    color "#c1d7e1"
    hover_color "#ffffff"
    selected_color "#ffffff"
