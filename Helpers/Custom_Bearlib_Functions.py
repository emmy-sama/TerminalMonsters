from time import sleep
from bearlibterminal import terminal


def setup_bearlib():
    terminal.open()
    # sprite setting
    terminal.set("window: size=88x25")
    terminal.set("0xE001: data/pngs/BackSprites.png, size=333x333, align=center")
    terminal.set("0xE305: data/pngs/FrontSprites.png, size=333x333, align=center")
    terminal.set("0xF8FF: data/pngs/Background.png")
    terminal.set("0xF8FD: data/pngs/Background2.png")
    terminal.set("0xF8FC: data/pngs/BlankBackground.png")
    terminal.set("0xF8FB: data/pngs/Random.png, align=center")
    terminal.set("0xF8FA: data/pngs/Sun.png, align=center")
    terminal.set("0xF8F9: data/pngs/Forest.png, align=center")
    terminal.set("0xF8F8: data/pngs/Cave.png, align=center")
    terminal.set("0xF8F7: data/pngs/Ocean.png, align=center")
    terminal.set("0xF8F6: data/pngs/City.png, align=center")
    terminal.set("0xF8F5: data/pngs/moon.png, align=center")
    terminal.set("0xF8F4: data/pngs/Pokeball.png, align=bottom-right")
    terminal.set("0xF8F3: data/pngs/Pokeball_Half_Open.png, align=bottom-right")
    terminal.set("0xF8F2: data/pngs/Pokeball_Open.png, align=bottom-right")
    terminal.set("0x2640: data/pngs/Female_symbol.png, align=center")
    terminal.set("0x2642: data/pngs/Male_symbol.png, align=center")
    terminal.set("font: data/pokemon.ttf, size=16")
    # base window setup
    terminal.put(0, 0, 0xF8FC)
    terminal.layer(1)
    terminal.refresh()


def print_txt(txt, delay=2):
    terminal.clear_area(1, 20, 85, 5)
    terminal.printf(1, 20, txt)
    terminal.refresh()
    sleep(delay)
