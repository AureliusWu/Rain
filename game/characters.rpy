define h = Character("许澄", color="#9fdbe5", image="heroine")
define p = Character("我", color="#c9d5e3")
default affection = 0
default trust = 0
default truth_known = False
default current_scene = ""
default current_chapter = ""
default visited_scenes = []
default last_ending = ""

init python:
    renpy.music.register_channel("ambient", mixer="sfx", loop=True)

transform heroine_position:
    xalign 0.68
    yalign 1.0
    yoffset 30

screen ending_card(ending_title):
    modal True
    add Solid("#091927dd")
    vbox:
        xalign 0.5
        yalign 0.47
        spacing 42
        text "雨停之前" size 63 color "#a9e1e9" xalign 0.5
        text ending_title size 42 xalign 0.5
        text "这一段路，已经走完。" size 30 color "#becdd7" xalign 0.5
        textbutton "回到主菜单" id "ending_return" xalign 0.5 action Return()
