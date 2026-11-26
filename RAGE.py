# RAGE.EXE - Edition complete pour NumWorks
# Versions 1 a 5 reunies :
# - plateformes, sauts et collisions (desormais aussi laterales)
# - pieges surprises : pics, sols fragiles, plateformes mobiles, ressorts
# - 20 niveaux progressifs et varies
# - menu, selection des niveaux (grille + records), compteur de morts et records
# - game feel : coyote time, jump buffer, vibration des plateformes fragiles,
#   flash rouge + message a la mort ("PIEGE !" / "CHUTE !")
#
# Commandes :
# Fleches gauche/droite : bouger
# OK : sauter / valider
# BACKSPACE : retour menu / quitter

from kandinsky import *
from ion import *
from time import sleep

W = 320
H = 222
HUD_H = 40

try:
    _KEY_BACK = KEY_BACK
except NameError:
    _KEY_BACK = KEY_HOME

BG = (14, 16, 25)
WHITE = (240, 240, 245)
RED = (240, 55, 65)
BLUE = (55, 155, 255)
CYAN = (90, 210, 235)
GREEN = (65, 225, 125)
YELLOW = (255, 205, 65)
GREY = (95, 105, 120)
DARK = (35, 40, 55)
PURPLE = (175, 100, 235)
ORANGE = (245, 145, 55)
PINK = (245, 85, 115)

# Types de plateformes :
# 0 = normale, 1 = fragile, 2 = qui tombe,
# 3 = mobile horizontale, 4 = invisible jusqu'a l'approche,
# 5 = mobile verticale, 6 = ressort (propulse plus haut).

# Modes de pieges :
# 0 = declenchement horizontal (player_x > x - 12)
# 1 = proximite verticale (joueur au-dessus du piege a moins de `param` px)
# 2 = compteur de trames (frame >= param)

LEVEL_COUNT = 20
LEVELS = []

COYOTE_FRAMES = 6
JUMP_BUFFER = 6
SPRING_V = -9.4

MENU_OPTIONS = ("JOUER", "CHOISIR UN NIVEAU", "RECOMMENCER", "QUITTER")


def prand(n, i, m):
    # Pseudo-aleatoire determinant : chaque niveau est toujours le meme.
    x = ((n + 7) * 2654435761 + (i + 13) * 40503) & 0x7FFFFFFF
    x = (x ^ (x >> 7)) * 1274126177 & 0x7FFFFFFF
    x = (x ^ (x >> 11)) & 0xFFFF
    return x % m


def make_level(n):
    # Hauteur de depart, largeurs et variations : tout varie selon n.
    plats = []
    spikes = []
    traps = []

    def rnd(i, a, b):
        return a + prand(n, i, b - a + 1)

    start_y = 195 - rnd(0, 0, 28)
    fw = 72 - n // 5
    if fw < 46:
        fw = 46
    plats.append([0, start_y, fw, 12, 0])

    n_mid = 4 + n % 3
    span = 286 - fw
    while n_mid > 3 and span // n_mid < 36:
        n_mid -= 1
    slot = span // n_mid

    # L'ordre d'apparition des types tourne avec n : plus de repetition.
    if n < 2:
        pool = (0, 0, 0, 1)
    elif n < 5:
        pool = (0, 0, 1, 2, 3)
    elif n < 8:
        pool = (0, 1, 2, 3, 3, 6)
    elif n < 12:
        pool = (0, 1, 2, 3, 4, 6)
    else:
        pool = (0, 1, 2, 3, 4, 5, 5, 6)

    x = fw
    y = start_y
    spring_up = False
    for i in range(n_mid):
        x += slot
        if spring_up:
            dy = -rnd(20 + i, 46, 62)
            spring_up = False
        else:
            dy = rnd(20 + i, -26, 20)
        ny = y + dy
        if ny > 196:
            ny = 196
        if ny < 108:
            ny = 108
        w = slot - rnd(3 + i, 6, 18) - n // 6
        if w < 24:
            w = 24
        if w > 44:
            w = 44
        if x + w > 280:
            w = 280 - x
            if w < 18:
                x += slot
                continue
        t = pool[(i + n) % len(pool)]
        if n < 2 and t not in (0, 1):
            t = 0
        amp = 0
        if t == 3:
            amp = rnd(40 + i, 12, 22)
        elif t == 5:
            amp = rnd(40 + i, 12, 22)
            if ny - amp < 98:
                ny += 98 - (ny - amp)
            if ny + amp > 202:
                amp = 202 - ny
            if amp < 6:
                t = 0
                amp = 0
        if t == 6 and w < 28:
            w = 28
        if t == 6:
            spring_up = True
        plats.append([x, ny, w, 10, t])

        # Pics visibles sur certaines plateformes normales.
        if t == 0 and w >= 30 and rnd(60 + i, 0, 9) < 2 + n // 4:
            sw = 12
            sxx = x + rnd(61 + i, 4, w - 4 - sw)
            spikes.append([sxx, ny, sw])

        # Pieges surprises, mode variable selon la difficulte.
        if n >= 3 and t == 0 and w >= 30 and rnd(70 + i, 0, 9) < (2 if n < 8 else 3):
            tw = 14
            tx = x + rnd(71 + i, 8, w - 8 - tw)
            if n < 6:
                m = 0
                par = 0
            elif n < 15:
                m = rnd(72 + i, 0, 1)
                par = 20 if m == 1 else 0
            else:
                m = (0, 1, 1, 2)[rnd(72 + i, 0, 3)]
                par = 20 if m == 1 else (rnd(73 + i, 50, 100) if m == 2 else 0)
            traps.append([tx, ny, tw, m, par, 0, 0])
        y = ny

    fy = 150 + rnd(80, 0, 42)
    plats.append([284, fy, 36, 12, 0])
    goal = [290, fy - 30, 18, 30]
    start = [8, start_y - 12]
    return {"platforms": plats, "spikes": spikes, "traps": traps,
            "goal": goal, "start": start}


for i in range(LEVEL_COUNT):
    LEVELS.append(make_level(i + 1))

# Etat du jeu
scene = "title"
level_index = 0
level_unlocked = 1
deaths = 0
level_deaths = 0
records = [None] * LEVEL_COUNT  # Records de la session : essais par niveau

player_x = 8.0
player_y = 178.0
vx = 0.0
vy = 0.0
on_ground = False
standing = -1
coyote = 0
jump_buffer = 0
frame = 0

platforms = []
spikes = []
trap_zones = []
hud_cache = None

death_msg = ""
message_timer = 0
menu_choice = 0
sel_level = 0

prev_ok = False
prev_back = False
prev_up = False
prev_down = False
prev_left = False
prev_right = False


# --- Entrees : detection propre des nouveaux appuis -----------------------

def poll_keys():
    # Retourne les nouvelles pressions (fronts montants) de chaque touche.
    global prev_ok, prev_back, prev_up, prev_down, prev_left, prev_right
    now_ok = keydown(KEY_OK)
    now_back = keydown(_KEY_BACK)
    now_up = keydown(KEY_UP)
    now_down = keydown(KEY_DOWN)
    now_left = keydown(KEY_LEFT)
    now_right = keydown(KEY_RIGHT)
    edges = (now_ok and not prev_ok,
             now_back and not prev_back,
             now_up and not prev_up,
             now_down and not prev_down,
             now_left and not prev_left,
             now_right and not prev_right)
    prev_ok = now_ok
    prev_back = now_back
    prev_up = now_up
    prev_down = now_down
    prev_left = now_left
    prev_right = now_right
    return edges


# --- Affichage securise ---------------------------------------------------

def rect(x, y, w, h, color):
    x = int(x)
    y = int(y)
    w = int(w)
    h = int(h)
    if x < 0:
        w += x
        x = 0
    if y < 0:
        h += y
        y = 0
    if x + w > W:
        w = W - x
    if y + h > H:
        h = H - y
    if w > 0 and h > 0:
        fill_rect(x, y, w, h, color)


def safe_text(txt, x, y, color=WHITE, bg=BG):
    txt = str(txt)
    x = int(x)
    y = int(y)
    if x < 0:
        x = 0
    if y < 0:
        y = 0
    if x + 10 * len(txt) > W:
        x = W - 10 * len(txt)
    if y > H - 18:
        y = H - 18
    draw_string(txt, x, y, color, bg)


def fmt_rec(r):
    if r is None:
        return "--"
    return str(r)


# --- Chargement d'un niveau ----------------------------------------------

def load_level(index):
    global player_x, player_y, vx, vy, on_ground, standing, coyote, jump_buffer
    global platforms, spikes, trap_zones, frame, level_deaths
    level_deaths = 0
    frame = 0
    data = LEVELS[index]
    player_x, player_y = data["start"]
    player_x = float(player_x)
    player_y = float(player_y)
    vx = 0
    vy = 0
    on_ground = False
    standing = -1
    coyote = 0
    jump_buffer = 0
    platforms = []
    for p in data["platforms"]:
        # [x, y, w, h, type, active, timer, start_x, dir, amp, base_y]
        platforms.append([p[0], p[1], p[2], p[3], p[4], 1, 0,
                          float(p[0]), 1, 0, p[1]])
    for p in platforms:
        if p[4] == 3 or p[4] == 5:
            p[9] = 12 + prand(index, int(p[0]) % 97, 11)
        elif p[4] == 4:
            p[9] = 1
    spikes = [s[:] for s in data["spikes"]]
    trap_zones = [t[:] for t in data["traps"]]


def overlap(ax, ay, aw, ah, bx, by, bw, bh):
    return (ax < bx + bw and ax + aw > bx and
            ay < by + bh and ay + ah > by)


def die(msg):
    global deaths, level_deaths, death_msg, message_timer
    deaths += 1
    level_deaths += 1
    death_msg = msg
    message_timer = 34


# --- Simulation ------------------------------------------------------------

def update_platforms():
    global player_x, player_y
    for i in range(len(platforms)):
        p = platforms[i]
        if not p[5]:
            continue
        t = p[4]
        if t == 1:
            if p[6] > 0:
                p[6] -= 1
                if p[6] <= 0:
                    p[5] = 0
        elif t == 2:
            if p[6] > 0:
                dy = p[6]
                p[1] += dy
                p[6] = dy + 0.3
                if p[1] > H + 20:
                    p[5] = 0
                elif i == standing:
                    player_y += dy
        elif t == 3:
            nx = p[0] + p[8] * 1.1
            if nx < p[7] - p[9]:
                p[8] = 1
                nx = p[7] - p[9]
            elif nx > p[7] + p[9]:
                p[8] = -1
                nx = p[7] + p[9]
            if i == standing:
                player_x += nx - p[0]
            p[0] = nx
        elif t == 5:
            ny = p[1] + p[8]
            if ny < p[10] - p[9]:
                p[8] = 1
                ny = p[10] - p[9]
            elif ny > p[10] + p[9]:
                p[8] = -1
                ny = p[10] + p[9]
            if i == standing:
                player_y += ny - p[1]
            p[1] = ny


def update_traps():
    global frame
    frame += 1
    for t in trap_zones:
        if t[5]:
            if t[6] < 10:
                t[6] += 2
            continue
        m = t[3]
        if m == 0:
            if player_x + 9 > t[0] - 12:
                t[5] = 1
        elif m == 1:
            if (player_x + 9 > t[0] and player_x < t[0] + t[2] and
                    player_y + 12 >= t[1] - t[4] and player_y <= t[1]):
                t[5] = 1
        elif frame >= t[4]:
            t[5] = 1
        if t[5] and t[6] < 10:
            t[6] += 2


def update_game(ok_now):
    global player_x, player_y, vx, vy, on_ground, standing, coyote, jump_buffer
    global scene, level_unlocked

    # Deplacement horizontal + collisions laterales (murs epais / mobiles).
    vx = 0
    if keydown(KEY_LEFT):
        vx = -2.4
    if keydown(KEY_RIGHT):
        vx = 2.4
    prev_x = player_x
    player_x += vx
    if player_x < 0:
        player_x = 0
    if player_x > 311:
        player_x = 311
    for p in platforms:
        if not p[5]:
            continue
        if player_y + 12 > p[1] + 3 and player_y < p[1] + p[3]:
            if vx > 0 and prev_x + 9 <= p[0] + 0.01 and player_x + 9 > p[0]:
                player_x = p[0] - 9
            elif vx < 0 and prev_x >= p[0] + p[2] - 0.01 and player_x < p[0] + p[2]:
                player_x = p[0] + p[2]

    # Saut : nouvel appui + jump buffer + coyote time.
    if jump_buffer > 0:
        jump_buffer -= 1
    if ok_now:
        jump_buffer = JUMP_BUFFER
    if jump_buffer > 0 and (on_ground or coyote > 0):
        vy = -7.4
        on_ground = False
        coyote = 0
        jump_buffer = 0
        standing = -1

    # Gravite + collision avec le dessus des plateformes.
    old_y = player_y
    vy += 0.42
    if vy > 8:
        vy = 8
    player_y += vy
    on_ground = False
    standing = -1
    for i in range(len(platforms)):
        p = platforms[i]
        if not p[5]:
            continue
        if (player_x + 9 > p[0] and player_x < p[0] + p[2] and
                old_y + 12 <= p[1] + 0.01 and player_y + 12 >= p[1] and vy >= 0):
            player_y = p[1] - 12
            if p[4] == 6:
                vy = SPRING_V
            else:
                vy = 0
                on_ground = True
                standing = i
                if p[4] == 1 and p[6] == 0:
                    p[6] = 12
                elif p[4] == 2 and p[6] == 0:
                    p[6] = 1
            break

    # Coyote time : quelques trames apres avoir quitte un appui.
    if on_ground:
        coyote = COYOTE_FRAMES
    elif coyote > 0:
        coyote -= 1

    update_traps()

    # Pics fixes.
    for s in spikes:
        if overlap(player_x, player_y, 9, 12, s[0], s[1] - 7, s[2], 8):
            die("PIEGE !")
            return

    # Pics surprises declenches.
    for t in trap_zones:
        if t[6] > 0 and overlap(player_x, player_y, 9, 12,
                                t[0], t[1] - t[6], t[2], t[6]):
            die("PIEGE !")
            return

    # Chute hors de l'ecran.
    if player_y > H:
        die("CHUTE !")
        return

    # Arrivee : record = essais (morts) du niveau courant.
    g = LEVELS[level_index]["goal"]
    if overlap(player_x, player_y, 9, 12, g[0], g[1], g[2], g[3]):
        if records[level_index] is None or level_deaths < records[level_index]:
            records[level_index] = level_deaths
        if level_index + 1 < LEVEL_COUNT:
            if level_index + 2 > level_unlocked:
                level_unlocked = level_index + 2
        scene = "win"


# --- Dessin ----------------------------------------------------------------

def draw_spikes(x, y, w, color=RED, h=7):
    h = int(h)
    if h <= 0:
        return
    if h >= 2:
        rect(x, y - 2, w, 2, color)
    if h >= 4:
        rect(x + 2, y - 4, w - 4, 2, color)
    if h >= 6:
        rect(x + 4, y - 6, w - 8, 2, color)
    if h >= 8:
        rect(x + 6, y - 8, w - 12, 2, color)
    if h >= 10:
        rect(x + 8, y - h, w - 16, 2, color)


def draw_player():
    rect(player_x, player_y, 9, 12, BLUE)
    rect(player_x + 2, player_y + 3, 2, 2, WHITE)
    rect(player_x + 6, player_y + 3, 2, 2, WHITE)
    rect(player_x + 2, player_y + 9, 5, 2, (25, 75, 145))


def draw_world():
    global hud_cache
    # Effacement du monde seul : la barre de score n'est repeinte
    # que si ses valeurs changent (moins d'appels graphiques).
    rect(0, HUD_H, W, H - HUD_H, BG)
    key = (level_index, deaths, level_deaths, records[level_index])
    if key != hud_cache or player_y < 48:
        rect(0, 0, W, HUD_H, DARK)
        safe_text("RAGE.EXE", 6, 3, RED, DARK)
        safe_text("Niv " + str(level_index + 1) + "/20", 226, 3, WHITE, DARK)
        hud = ("Morts " + str(deaths) + "   Essais " + str(level_deaths) +
               "   Rec " + fmt_rec(records[level_index]))
        safe_text(hud, 6, 20, YELLOW, DARK)
        hud_cache = key

    # Plateformes.
    for p in platforms:
        if not p[5]:
            continue
        t = p[4]
        x = p[0]
        # Plateforme fragile : elle tremble avant de ceder.
        if t == 1 and p[6] > 0:
            x += 1 if (frame >> 2) & 1 else -1
        if t == 4:
            if abs(player_x - p[0]) > 44:
                continue
            color = (75, 125, 165)
        elif t == 1:
            color = YELLOW
        elif t == 2:
            color = ORANGE
        elif t == 3:
            color = PURPLE
        elif t == 5:
            color = CYAN
        elif t == 6:
            color = PINK
        else:
            color = GREY
        rect(x, p[1], p[2], p[3], color)
        rect(x, p[1], p[2], 2, WHITE)

    # Pics fixes.
    for s in spikes:
        draw_spikes(s[0], s[1], s[2])

    # Pics surprises (invisibles jusqu'au declenchement).
    for t in trap_zones:
        if t[6] > 0:
            draw_spikes(t[0], t[1], t[2], RED, t[6])

    # Sortie.
    g = LEVELS[level_index]["goal"]
    rect(g[0], g[1], g[2], g[3], GREEN)
    rect(g[0] + 4, g[1] + 5, 10, 25, BG)
    rect(g[0] + 11, g[1] + 16, 2, 2, YELLOW)

    draw_player()


def draw_death_screen():
    draw_world()
    rect(60, 84, 200, 56, (140, 30, 28))
    rect(64, 88, 192, 48, (26, 10, 10))
    safe_text(death_msg, (W - len(death_msg) * 10) // 2, 94, (255, 92, 88), (26, 10, 10))
    st = "Morts " + str(deaths) + "   Essais " + str(level_deaths)
    safe_text(st, (W - len(st) * 10) // 2, 114, WHITE, (26, 10, 10))


def draw_title():
    rect(0, 0, W, H, BG)
    safe_text("RAGE.EXE", 91, 38, RED)
    safe_text("LE JEU QUI VA TE FAIRE RAGER", 26, 72, WHITE)
    safe_text("20 niveaux - pieges surprises", 39, 101, YELLOW)
    safe_text("OK : JOUER", 108, 143, GREEN)
    safe_text("BACKSPACE : QUITTER", 70, 183, GREY)


def draw_menu():
    rect(0, 0, W, H, BG)
    safe_text("RAGE.EXE", 105, 24, RED)
    safe_text("MENU PRINCIPAL", 91, 54, WHITE)
    for i in range(len(MENU_OPTIONS)):
        color = YELLOW if i == menu_choice else WHITE
        prefix = "> " if i == menu_choice else "  "
        safe_text(prefix + MENU_OPTIONS[i], 65, 84 + i * 26, color)
    safe_text("HAUT/BAS : CHOISIR", 65, 186, GREY)
    safe_text("OK : VALIDER", 105, 202, GREY)


def draw_level_select(sel):
    rect(0, 0, W, H, BG)
    safe_text("CHOIX DU NIVEAU", 82, 6, YELLOW)
    for i in range(LEVEL_COUNT):
        col = i % 4
        row = i // 4
        x = 28 + col * 70
        y = 32 + row * 28
        unlocked = i + 1 <= level_unlocked
        if i == sel:
            rect(x - 7, y - 5, 46, 26, YELLOW)
        rect(x - 5, y - 3, 42, 22, DARK)
        if unlocked:
            color = YELLOW if i == sel else WHITE
            label = str(i + 1)
        else:
            color = GREY
            label = "--"
        safe_text(label, x - 5 + (42 - 10 * len(label)) // 2, y + 2, color, DARK)
    rec = records[sel]
    if rec is None:
        safe_text("Niveau " + str(sel + 1) + "   Record : --", 65, 176, GREEN)
    else:
        safe_text("Niveau " + str(sel + 1) + "   Record : " + str(rec), 55, 176, GREEN)
    safe_text("GAUCHE/DROITE/HAUT/BAS : NIVEAU", 20, 196, GREY)
    safe_text("OK : JOUER   BACK : MENU", 50, 214, WHITE)


def draw_win():
    rect(0, 0, W, H, BG)
    safe_text("NIVEAU TERMINE !", 75, 52, GREEN)
    safe_text("Essais (morts) : " + str(level_deaths), 80, 82, WHITE)
    safe_text("Record : " + fmt_rec(records[level_index]), 100, 108, YELLOW)
    safe_text("OK : NIVEAU SUIVANT", 65, 146, YELLOW)
    safe_text("BACKSPACE : MENU", 88, 172, GREY)


def draw_game_over():
    rect(0, 0, W, H, BG)
    safe_text("BRAVO !", 118, 43, GREEN)
    safe_text("TU AS TERMINE LES 20 NIVEAUX", 26, 79, WHITE)
    safe_text("Morts : " + str(deaths), 117, 111, YELLOW)
    safe_text("OK : REJOUER", 103, 158, GREEN)
    safe_text("BACKSPACE : MENU", 88, 187, GREY)


# --- Boucle principale ------------------------------------------------------

def reset_game():
    global level_index, deaths, level_deaths
    level_index = 0
    deaths = 0
    level_deaths = 0
    load_level(0)


def main():
    global scene, level_index, menu_choice, sel_level, last_drawn
    global message_timer, hud_cache
    menu_choice = 0
    sel_level = 0
    last_drawn = ""
    running = True
    while running:
        ok_now, back_now, up_now, down_now, left_now, right_now = poll_keys()

        # On ne repeint les ecrans statiques qu'au changement de scene.
        if scene != last_drawn:
            if scene == "title":
                draw_title()
            elif scene == "menu":
                draw_menu()
            elif scene == "select":
                draw_level_select(sel_level)
            elif scene == "game":
                draw_world()
            elif scene == "win":
                draw_win()
            elif scene == "complete":
                draw_game_over()
            last_drawn = scene

        if scene == "title":
            if ok_now:
                scene = "menu"
                last_drawn = ""
            elif back_now:
                running = False

        elif scene == "menu":
            moved = False
            if up_now:
                menu_choice = (menu_choice - 1) % len(MENU_OPTIONS)
                moved = True
            if down_now:
                menu_choice = (menu_choice + 1) % len(MENU_OPTIONS)
                moved = True
            if moved:
                draw_menu()
            if ok_now and not moved:
                if menu_choice == 0:
                    # JOUER : demarre ou reprend au niveau courant.
                    if level_index >= LEVEL_COUNT:
                        level_index = 0
                    load_level(level_index)
                    scene = "game"
                elif menu_choice == 1:
                    sel_level = min(level_index, level_unlocked - 1)
                    scene = "select"
                elif menu_choice == 2:
                    # RECOMMENCER : remise a zero complete de la session.
                    reset_game()
                    scene = "game"
                else:
                    running = False
                last_drawn = ""
            elif back_now:
                scene = "title"
                last_drawn = ""
            if running and scene == "menu":
                sleep(0.06)

        elif scene == "select":
            mx = level_unlocked - 1
            if right_now and sel_level < mx:
                sel_level += 1
                draw_level_select(sel_level)
            if left_now and sel_level > 0:
                sel_level -= 1
                draw_level_select(sel_level)
            if down_now and sel_level < mx:
                sel_level = min(mx, sel_level + 4)
                draw_level_select(sel_level)
            if up_now and sel_level > 0:
                sel_level = max(0, sel_level - 4)
                draw_level_select(sel_level)
            if ok_now:
                level_index = sel_level
                load_level(sel_level)
                scene = "game"
                last_drawn = ""
            elif back_now:
                scene = "menu"
                last_drawn = ""
            if scene == "select":
                sleep(0.06)

        elif scene == "game":
            if message_timer > 0:
                if message_timer > 30:
                    rect(0, 0, W, H, (150, 20, 22))
                elif message_timer == 30:
                    draw_death_screen()
                message_timer -= 1
                if message_timer <= 0:
                    load_level(level_index)
                    draw_world()
                sleep(0.02)
            else:
                update_game(ok_now)
                if scene == "game":
                    draw_world()
                    sleep(0.022)

        elif scene == "win":
            if ok_now:
                if level_index + 1 >= LEVEL_COUNT:
                    scene = "complete"
                else:
                    level_index += 1
                    load_level(level_index)
                    scene = "game"
                last_drawn = ""
            elif back_now:
                scene = "menu"
                last_drawn = ""
            if scene == "win":
                sleep(0.06)

        elif scene == "complete":
            if ok_now:
                reset_game()
                scene = "game"
                last_drawn = ""
            elif back_now:
                scene = "menu"
                last_drawn = ""
            if scene == "complete":
                sleep(0.06)

    rect(0, 0, W, H, BG)
    safe_text("A BIENTOT !", 105, 100, WHITE)


load_level(0)

if __name__ == "__main__":
    main()
