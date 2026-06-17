"""
intro_dialog.py
──────────────────
Cutscene de diálogos pós-intro_chase com efeitos pesados de glitch/corrupção.
O sistema parece estar falhando: tela fragmenta, cores corrompem, texto
distorce — transmitindo que o vírus realmente comprometeu tudo.

USO:
    from intro_dialog import show_intro_dialog

    show_intro_chase(screen, clock)
    show_intro_dialog(screen, clock)   # ← linha nova
    run_game(screen, clock)
"""

import pygame
import sys
import math
import random

BLACK       = (0, 0, 0)
WHITE       = (255, 255, 255)
NEON_CYAN   = (0, 220, 220)
NEON_RED    = (220, 30, 30)
NEON_PURPLE = (160, 40, 200)
VIRUS_CORE  = (255, 0, 60)
GRID_LINE   = (10, 28, 28)


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS BASE (mesmos da intro_chase)
# ══════════════════════════════════════════════════════════════════════════════

def _draw_grid(surface, offset=0):
    w, h = surface.get_width(), surface.get_height()
    off = int(offset) % 40
    for x in range(-40 + off, w, 40):
        pygame.draw.line(surface, GRID_LINE, (x, 0), (x, h), 1)
    for y in range(0, h, 40):
        pygame.draw.line(surface, GRID_LINE, (0, y), (w, y), 1)


def _draw_scanlines(surface, alpha=30):
    w, h = surface.get_width(), surface.get_height()
    scan = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(0, h, 4):
        pygame.draw.line(scan, (0, 0, 0, alpha), (0, y), (w, y), 1)
    surface.blit(scan, (0, 0))


def _draw_virus_blob(surface, center, radius, tick, color=VIRUS_CORE):
    cx, cy  = center
    pulse   = (math.sin(tick * 0.18) + 1.0) / 2.0
    r       = radius + pulse * 6

    glow = pygame.Surface((int(r * 4), int(r * 4)), pygame.SRCALPHA)
    pygame.draw.circle(glow, (*color, 60),
                       (glow.get_width() // 2, glow.get_height() // 2), int(r * 1.8))
    surface.blit(glow, (cx - glow.get_width() // 2, cy - glow.get_height() // 2))

    points = []
    for i in range(10):
        angle  = (2 * math.pi * i) / 10
        jitter = math.sin(tick * 0.3 + i * 1.7) * (r * 0.25)
        rr     = r + jitter
        points.append((cx + math.cos(angle) * rr, cy + math.sin(angle) * rr))
    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, WHITE, points, 1)

    for i in range(5):
        angle  = tick * 0.05 + i * (2 * math.pi / 5)
        length = r * (1.3 + 0.3 * math.sin(tick * 0.2 + i))
        ex = cx + math.cos(angle) * length
        ey = cy + math.sin(angle) * length
        pygame.draw.line(surface, color, (cx, cy), (int(ex), int(ey)), 2)
        pygame.draw.circle(surface, (255, 80, 80), (int(ex), int(ey)), 3)

    core_r = int(r * 0.25 * (0.6 + 0.4 * pulse))
    pygame.draw.circle(surface, WHITE, (cx, cy), core_r)


# ══════════════════════════════════════════════════════════════════════════════
#  EFEITOS DE GLITCH / CORRUPÇÃO
# ══════════════════════════════════════════════════════════════════════════════

def _glitch_slice(surface, tick):
    """
    Fatias horizontais deslocadas lateralmente — efeito VHS.
    Dispara em rajadas irregulares para parecer falha real de sistema.
    """
    w, h = surface.get_width(), surface.get_height()
    cycle = tick % 48
    if cycle > 8:
        return

    intensity = 1.0 - cycle / 8.0
    n_slices  = random.randint(3, 9)
    for _ in range(n_slices):
        sy  = random.randint(0, h - 20)
        sh  = random.randint(4, 28)
        dx  = int(random.choice([-1, 1]) * random.randint(8, 48) * intensity)
        sh  = min(sh, h - sy)
        if sh <= 0:
            continue
        strip = surface.subsurface(pygame.Rect(0, sy, w, sh)).copy()
        surface.blit(strip, (dx, sy))


def _glitch_rgb_split(surface, tick):
    """
    Aberração cromática: separa canais R e B horizontalmente.
    """
    if tick % 35 not in range(0, 5):
        return

    w, h  = surface.get_width(), surface.get_height()
    shift = random.randint(4, 14)
    sy    = random.randint(0, h - 80)
    sh    = min(random.randint(30, 80), h - sy)
    if sh <= 0:
        return

    strip  = surface.subsurface(pygame.Rect(0, sy, w, sh)).copy()
    r_surf = pygame.Surface((w, sh), pygame.SRCALPHA)
    b_surf = pygame.Surface((w, sh), pygame.SRCALPHA)
    r_surf.blit(strip, (0, 0))
    b_surf.blit(strip, (0, 0))
    r_surf.fill((0, 255, 255, 80), special_flags=pygame.BLEND_RGBA_MULT)
    b_surf.fill((255, 255, 0,  80), special_flags=pygame.BLEND_RGBA_MULT)
    surface.blit(r_surf, ( shift, sy), special_flags=pygame.BLEND_ADD)
    surface.blit(b_surf, (-shift, sy), special_flags=pygame.BLEND_ADD)


def _glitch_static_blocks(surface, tick, intensity=1.0):
    """
    Blocos de estática colorida — corrupção de memória de vídeo.
    """
    w, h  = surface.get_width(), surface.get_height()
    count = int(random.randint(4, 10) * intensity)
    for _ in range(count):
        if random.random() < 0.4:
            continue
        bx  = random.randint(0, w - 120)
        by  = random.randint(0, h - 20)
        bw  = random.randint(20, 160)
        bh  = random.randint(2, 18)
        col = random.choice([NEON_RED, NEON_CYAN, NEON_PURPLE, WHITE,
                             (255, 255, 0), (0, 255, 80)])
        s   = pygame.Surface((bw, bh), pygame.SRCALPHA)
        s.fill((*col, random.randint(40, 120)))
        surface.blit(s, (bx, by))


def _glitch_screen_tear(surface, tick):
    """
    Rasgo vertical repentino: duplica faixa com deslocamento.
    """
    if tick % 90 not in range(0, 3):
        return
    w, h = surface.get_width(), surface.get_height()
    tx   = random.randint(w // 4, 3 * w // 4)
    tw   = random.randint(60, 200)
    dy   = random.randint(-30, 30)
    if tx + tw > w:
        tw = w - tx
    if tw <= 0:
        return
    strip = surface.subsurface(pygame.Rect(tx, 0, tw, h)).copy()
    surface.blit(strip, (tx, dy))


def _glitch_corrupt_text(font, text, tick, base_color):
    """
    Texto com caracteres aleatoriamente substituídos por lixo binário.
    """
    CORRUPT_CHARS = "█▓▒░▀▄■□▪▫◆◇○●"
    glitch_active = (tick % 40) < 6

    corrupted = ""
    for ch in text:
        if glitch_active and ch != " " and random.random() < 0.18:
            corrupted += random.choice(CORRUPT_CHARS)
        else:
            corrupted += ch

    if glitch_active and random.random() < 0.5:
        color = random.choice([NEON_RED, WHITE, NEON_PURPLE])
    else:
        color = base_color

    return font.render(corrupted, True, color)


def _draw_noise_overlay(surface, tick, alpha=18):
    """
    Ruído granular — degradação de sinal.
    """
    w, h   = surface.get_width(), surface.get_height()
    n_dots = int(w * h * 0.002)
    noise  = pygame.Surface((w, h), pygame.SRCALPHA)
    for _ in range(n_dots):
        nx  = random.randint(0, w - 1)
        ny  = random.randint(0, h - 1)
        val = random.randint(100, 255)
        noise.set_at((nx, ny), (val, val, val, random.randint(20, alpha)))
    surface.blit(noise, (0, 0))


def _flash_red_vignette(surface, tick):
    """
    Vinheta vermelha pulsante nas bordas — sinal de perigo.
    """
    w, h    = surface.get_width(), surface.get_height()
    pulse   = abs(math.sin(tick * 0.08))
    v_alpha = int(pulse * 80)
    if v_alpha < 5:
        return

    vign      = pygame.Surface((w, h), pygame.SRCALPHA)
    thickness = 120
    for i in range(0, thickness, 3):   # passo 3 para performar melhor
        ratio = (thickness - i) / thickness
        a     = int(v_alpha * ratio * ratio)
        pygame.draw.rect(vign, (*NEON_RED, a),
                         (i, i, w - i * 2, h - i * 2), 1)
    surface.blit(vign, (0, 0))


# ══════════════════════════════════════════════════════════════════════════════
#  BALÃO DE FALA GLITCHADO
# ══════════════════════════════════════════════════════════════════════════════

def _draw_speech_bubble(surface, rect, lines, border_color,
                        font_body, font_label, label, label_color,
                        alpha, tail_side, tail_tip_y, tick):
    bub = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

    # fundo
    pygame.draw.rect(bub, (0, 0, 0, int(210 * alpha / 255)),
                     (0, 0, rect.width, rect.height), border_radius=10)

    # borda — pode "falhar" de cor durante glitch
    brd_col = border_color
    if (tick % 45) < 4 and random.random() < 0.6:
        brd_col = random.choice([NEON_RED, WHITE, NEON_PURPLE])
    pygame.draw.rect(bub, (*brd_col, int(255 * alpha / 255)),
                     (0, 0, rect.width, rect.height), 2, border_radius=10)

    # sotaque topo
    pygame.draw.rect(bub, (*border_color, int(255 * alpha / 255)),
                     (8, 0, rect.width - 16, 3), border_radius=2)

    # label speaker (pode corromper)
    lbl_surf = _glitch_corrupt_text(font_label, f"[ {label} ]", tick, label_color)
    lbl_surf.set_alpha(int(255 * alpha / 255))
    bub.blit(lbl_surf, (14, 10))

    # separador
    sep_y = 10 + font_label.get_height() + 6
    pygame.draw.line(bub, (*border_color, int(100 * alpha / 255)),
                     (10, sep_y), (rect.width - 10, sep_y), 1)

    # linhas de texto
    y_text = sep_y + 10
    for line in lines:
        ts = _glitch_corrupt_text(font_body, line, tick + hash(line) % 20, WHITE)
        ts.set_alpha(int(255 * alpha / 255))
        dx = random.randint(-3, 3) if (tick % 48) < 8 else 0
        bub.blit(ts, (14 + dx, y_text))
        y_text += font_body.get_height() + 8

    surface.blit(bub, rect.topleft)

    # cauda triangular
    tail_size = 20
    if tail_side == "left":
        tip    = (rect.left - tail_size, tail_tip_y)
        base_a = (rect.left, rect.centery - 14)
        base_b = (rect.left, rect.centery + 14)
    else:
        tip    = (rect.right + tail_size, tail_tip_y)
        base_a = (rect.right, rect.centery - 14)
        base_b = (rect.right, rect.centery + 14)

    tail_s = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(tail_s, (0, 0, 0, int(210 * alpha / 255)),
                        [tip, base_a, base_b])
    pygame.draw.polygon(tail_s, (*border_color, int(255 * alpha / 255)),
                        [tip, base_a, base_b], 2)
    surface.blit(tail_s, (0, 0))


# ══════════════════════════════════════════════════════════════════════════════
#  CENA PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def show_intro_dialog(screen, clock, player_animator=None):
    """
    Exibe a cutscene de diálogos pós-perseguição com efeitos de glitch.

    Integração no main.py — dentro do bloco MOUSEBUTTONDOWN do main_menu():

        show_intro_chase(screen, clock)
        show_intro_dialog(screen, clock)   # ← linha nova
        run_game(screen, clock)
    """
    W, H = screen.get_width(), screen.get_height()

    font_med   = pygame.font.Font(None, 30)
    font_label = pygame.font.Font(None, 22)
    font_skip  = pygame.font.Font(None, 22)

    if player_animator is None:
        try:
            from main import PlayerAnimator
            player_animator = PlayerAnimator()
        except Exception:
            player_animator = None

    TUX_X   = int(W * 0.20)
    TUX_Y   = int(H * 0.62)
    VIRUS_X = int(W * 0.80)
    VIRUS_Y = int(H * 0.62)

    # ── Roteiro ──────────────────────────────────────────────────────────────
    dialogs = [
        (
            400, 3600,
            "VÍRUS",
            ["O vírus atacou o sistema", "e está trancando todas as saídas"],
            NEON_RED,
            "right",
        ),
        (
            4000, 7200,
            "TUX",
            ["Cumpra as missões", "para fugir."],
            NEON_CYAN,
            "left",
        ),
    ]
    total_duration_ms = 7800

    grid_offset = 0.0
    prev_frame  = pygame.Surface((W, H))
    prev_frame.fill(BLACK)

    tick        = 0
    start_ticks = pygame.time.get_ticks()
    running     = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                running = False

        elapsed = pygame.time.get_ticks() - start_ticks
        if elapsed >= total_duration_ms:
            break

        # ── Persistence / ghost CRT ───────────────────────────────────────
        ghost = prev_frame.copy()
        ghost.set_alpha(30)
        screen.fill(BLACK)
        screen.blit(ghost, (0, 0))

        # ── Fundo ─────────────────────────────────────────────────────────
        grid_offset -= 0.6
        _draw_grid(screen, grid_offset)

        _glitch_static_blocks(screen, tick, intensity=0.9)
        _draw_noise_overlay(screen, tick, alpha=22)

        # ── Vírus ─────────────────────────────────────────────────────────
        _draw_virus_blob(screen, (VIRUS_X, VIRUS_Y), 42, tick)

        # ── Tux ───────────────────────────────────────────────────────────
        if player_animator:
            player_animator.current_direction = "right"
            player_animator.update(0, 0)
            img = player_animator.get_current_image()
            if img:
                shake_x = random.randint(-2, 2) if (tick % 48) < 8 else 0
                shake_y = random.randint(-1, 1) if (tick % 48) < 8 else 0
                rect = img.get_rect(center=(TUX_X + shake_x, TUX_Y + shake_y))
                screen.blit(img, rect)

                # ghost ciano durante aberração cromática
                if (tick % 35) in range(0, 5):
                    ghost_img = img.copy()
                    ghost_img.set_alpha(60)
                    tinted = pygame.Surface(img.get_size(), pygame.SRCALPHA)
                    tinted.fill((0, 220, 220, 0))
                    ghost_img.blit(tinted, (0, 0), special_flags=pygame.BLEND_ADD)
                    screen.blit(ghost_img, (rect.x + random.randint(4, 10), rect.y))
        else:
            pygame.draw.ellipse(screen, WHITE, (TUX_X - 20, TUX_Y - 28, 40, 56))
            pygame.draw.ellipse(screen, BLACK, (TUX_X - 14, TUX_Y - 22, 28, 44))

        # ── Diálogos ──────────────────────────────────────────────────────
        for d_start, d_end, speaker, lines, border_col, tail_side in dialogs:
            if not (d_start <= elapsed < d_end):
                continue

            fade_in  = min(1.0, (elapsed - d_start) / 200)
            fade_out = min(1.0, (d_end   - elapsed) / 200)
            alpha    = max(0.0, min(fade_in, fade_out))

            bw = int(W * 0.36)
            bh = 30 + len(lines) * (font_med.get_height() + 8) + 34

            if tail_side == "right":
                bx, by, tip_y = VIRUS_X - bw - 55, VIRUS_Y - bh // 2 - 20, VIRUS_Y
            else:
                bx, by, tip_y = TUX_X + 55, TUX_Y - bh // 2 - 20, TUX_Y

            _draw_speech_bubble(
                screen,
                pygame.Rect(bx, by, bw, bh),
                lines, border_col,
                font_med, font_label,
                speaker, border_col,
                int(alpha * 255),
                tail_side, tip_y, tick,
            )
            break

        # ── Glitch pesado em cima de tudo ─────────────────────────────────
        _glitch_slice(screen, tick)
        _glitch_rgb_split(screen, tick)
        _glitch_screen_tear(screen, tick)
        _flash_red_vignette(screen, tick)

        # ── Barras de alerta (mesmas da intro_chase) ──────────────────────
        alert_pulse = abs(math.sin(tick * 0.15))
        bar_col = tuple(int(c * alert_pulse) for c in NEON_RED)
        pygame.draw.rect(screen, bar_col, (0, 0, W, 6))
        pygame.draw.rect(screen, bar_col, (0, H - 6, W, 6))

        # ── Erros de sistema no topo ──────────────────────────────────────
        if (tick % 60) < 35:
            err_lines = [
                "KERNEL PANIC — MEMORY CORRUPTION DETECTED",
                f"ERR_0x{random.randint(0xA000, 0xFFFF):04X} — LOGIC_GATE_FAULT",
            ]
            err_y = 14
            for err in err_lines:
                err_surf = _glitch_corrupt_text(font_label, err, tick, NEON_RED)
                err_surf.set_alpha(180)
                screen.blit(err_surf, err_surf.get_rect(center=(W // 2, err_y)))
                err_y += 18

        # ── Skip ──────────────────────────────────────────────────────────
        skip_alpha = int(140 + 80 * abs(math.sin(tick * 0.06)))
        skip_surf  = font_skip.render(
            "[ PRESSIONE ENTER / ESC PARA PULAR ]", True, (180, 180, 180)
        )
        skip_surf.set_alpha(skip_alpha)
        screen.blit(skip_surf, skip_surf.get_rect(center=(W // 2, H - 28)))

        _draw_scanlines(screen, alpha=35)

        prev_frame.blit(screen, (0, 0))
        pygame.display.flip()
        clock.tick(60)
        tick += 1


# ─── Teste isolado ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    pygame.display.set_caption("Teste — Dialog Cutscene")
    clock = pygame.time.Clock()
    show_intro_dialog(screen, clock)
    pygame.quit()
    sys.exit()