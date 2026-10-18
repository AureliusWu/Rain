init python:
    import replay_search

    def rain_history_plain(value):
        return renpy.filter_text_tags(value, allow=set())

    def rain_history_rows(history, query="", speaker=""):
        return replay_search.filter_history(history, query, speaker, rain_history_plain)

    def rain_history_speakers(history):
        return replay_search.history_speakers(history, rain_history_plain)

    def rain_history_session_token():
        # A panel lifetime must not consume the rollback-aware story RNG.
        return __import__("uuid").uuid4().hex

    def rain_set_history_query(value, session):
        """Apply native/HTML input only to its original live history panel."""
        screen = renpy.get_screen("history")
        if not isinstance(value, str) or screen is None:
            return False
        if screen.scope.get("history_session") != session:
            return False
        value = value[:80]
        if screen.scope.get("history_query", "") != value:
            renpy.music.stop(channel="voice")
            renpy.set_screen_variable("history_query", value, screen="history")
            renpy.restart_interaction()
        return True

    def rain_clear_history_filters(session):
        """A screen Function action must return None to keep its menu open."""
        if rain_set_history_query("", session):
            renpy.set_screen_variable("history_speaker", "", screen="history")
            renpy.set_screen_variable("history_chapter", "", screen="history")
            renpy.restart_interaction()

    class RainHistoryInputValue(InputValue):
        def __init__(self, session):
            self.session = session

        def get_text(self):
            screen = renpy.get_screen("history")
            if screen is None or screen.scope.get("history_session") != self.session:
                return ""
            return screen.scope.get("history_query", "")

        def set_text(self, value):
            rain_set_history_query(value, self.session)

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
