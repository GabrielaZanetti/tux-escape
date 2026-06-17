"""
intro_chase.py
──────────────
Cutscene de abertura: Tux fugindo de um vírus dentro do sistema.
Estabelece visualmente a temática cyberpunk antes do jogo começar.

USO:
    from intro_chase import show_intro_chase

    # Logo após o menu, antes de run_game() / show_portal_map()
    show_intro_chase(screen, clock, player_animator)
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


def _draw_grid(surface, offset=0):
    """Grade de circuito que se move levemente para dar sensação de velocidade."""
    w, h = surface.get_width(), surface.get_height()
    off = int(offset) % 40
    for x in range(-40 + off, w, 40):
        pygame.draw.line(surface, GRID_LINE, (x, 0), (x, h), 1)
    for y in range(0, h, 40):
        pygame.draw.line(surface, GRID_LINE, (0, y), (w, y), 1)


def _draw_scanlines(surface, alpha=35):
    w, h = surface.get_width(), surface.get_height()
    scan = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(0, h, 4):
        pygame.draw.line(scan, (0, 0, 0, alpha), (0, y), (w, y), 1)
    surface.blit(scan, (0, 0))


def _draw_virus_blob(surface, center, radius, tick, color=VIRUS_CORE):
    """Mancha de vírus orgânica e pulsante, com tentáculos de corrupção de dados."""
    cx, cy = center
    pulse = (math.sin(tick * 0.18) + 1.0) / 2.0
    r = radius + pulse * 6

    glow = pygame.Surface((int(r * 4), int(r * 4)), pygame.SRCALPHA)
    pygame.draw.circle(glow, (*color, 60), (glow.get_width() // 2, glow.get_height() // 2), int(r * 1.8))
    surface.blit(glow, (cx - glow.get_width() // 2, cy - glow.get_height() // 2))

    # corpo irregular (polígono pulsante)
    points = []
    n_points = 10
    for i in range(n_points):
        angle = (2 * math.pi * i) / n_points
        jitter = math.sin(tick * 0.3 + i * 1.7) * (r * 0.25)
        rr = r + jitter
        px = cx + math.cos(angle) * rr
        py = cy + math.sin(angle) * rr
        points.append((px, py))
    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, (255, 255, 255), points, 1)

    # "tentáculos" de glitch saindo do corpo
    for i in range(5):
        angle = (tick * 0.05 + i * (2 * math.pi / 5))
        length = r * (1.3 + 0.3 * math.sin(tick * 0.2 + i))
        ex = cx + math.cos(angle) * length
        ey = cy + math.sin(angle) * length
        pygame.draw.line(surface, color, (cx, cy), (ex, ey), 2)
        pygame.draw.circle(surface, (255, 80, 80), (int(ex), int(ey)), 3)

    # núcleo
    core_pulse = 0.6 + 0.4 * pulse
    pygame.draw.circle(surface, (255, 255, 255), (cx, cy), int(r * 0.25 * core_pulse))


def _draw_corruption_glitches(surface, tick, intensity=1.0):
    """Pequenas barras de glitch RGB picando aleatoriamente na tela."""
    w, h = surface.get_width(), surface.get_height()
    n = int(3 * intensity)
    for _ in range(n):
        if random.random() < 0.5:
            continue
        gy = random.randint(0, h - 10)
        gh = random.randint(2, 14)
        gx = random.randint(0, w - 100)
        gw = random.randint(40, 180)
        col = random.choice([NEON_RED, NEON_CYAN, NEON_PURPLE, WHITE])
        glitch_surf = pygame.Surface((gw, gh), pygame.SRCALPHA)
        glitch_surf.fill((*col, 90))
        surface.blit(glitch_surf, (gx, gy))


def _render_text_safely(font, text, color):
    return font.render(text, True, color)


def show_intro_chase(screen, clock, player_animator=None):
    """
    Cutscene de abertura mostrando o Tux fugindo do vírus.

    Parâmetros
    ----------
    screen : pygame.Surface
    clock  : pygame.time.Clock
    player_animator : PlayerAnimator opcional. Se None, usa um placeholder simples.
    """
    W, H = screen.get_width(), screen.get_height()

    font_big    = pygame.font.Font(None, 56)
    font_med    = pygame.font.Font(None, 32)
    font_small  = pygame.font.Font(None, 24)
    font_skip   = pygame.font.Font(None, 22)

    # ── Importa PlayerAnimator só se não foi passado (evita import circular) ───
    if player_animator is None:
        try:
            from main import PlayerAnimator
            player_animator = PlayerAnimator()
        except Exception:
            player_animator = None

    # ── Posições da perseguição ───────────────────────────────────────────────
    tux_x        = -60.0
    tux_y        = H * 0.62
    tux_speed    = 3.4

    virus_x      = -260.0
    virus_y      = H * 0.62
    virus_speed  = 3.15  # ligeiramente mais lento — cria tensão sem alcançar

    grid_offset  = 0.0

    # ── Roteiro de texto (aparece e desaparece em momentos certos) ──────────────
    # (tempo_inicio_ms, tempo_fim_ms, texto, cor)
    script = [
        (0,    2200, "SISTEMA COMPROMETIDO", NEON_RED),
        (2200, 4600, "UM VÍRUS INVADIU O NÚCLEO", NEON_CYAN),
        (4600, 7000, "TUX PRECISA ESCAPAR ANTES QUE SEJA TARDE DEMAIS", WHITE),
        (7000, 9400, "A ÚNICA SAÍDA: ATRAVESSAR AS PORTAS LÓGICAS", NEON_CYAN),
        (9400, 11800, "RESOLVA CADA PORTA PARA SOBREVIVER", NEON_RED),
    ]
    total_duration_ms = 12400  # cutscene termina aqui (ou ao pular)

    tick = 0
    start_ticks = pygame.time.get_ticks()
    running = True
    skip_requested = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                    skip_requested = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                skip_requested = True

        elapsed = pygame.time.get_ticks() - start_ticks
        if skip_requested or elapsed >= total_duration_ms:
            running = False
            break

        # ── Atualiza posições (perseguição contínua, atravessando a tela) ──────────
        grid_offset -= 2.2
        tux_x   += tux_speed
        virus_x += virus_speed

        # Quando saem da tela, reposiciona em loop pra perseguição parecer infinita
        if tux_x > W + 80:
            tux_x = -60
            virus_x = -260
        if virus_x > W + 200:
            virus_x = -260

        if player_animator:
            player_animator.update(tux_speed, 0)

        # ── Render ───────────────────────────────────────────────────────────────
        screen.fill(BLACK)
        _draw_grid(screen, grid_offset)

        # vírus perseguindo (atrás do Tux)
        virus_radius = 46
        _draw_virus_blob(screen, (int(virus_x), int(virus_y)), virus_radius, tick)

        # rastro de corrupção atrás do vírus
        for i in range(1, 5):
            trail_alpha = max(0, 90 - i * 18)
            trail_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (*VIRUS_CORE, trail_alpha), (15, 15), 14 - i * 2)
            screen.blit(trail_surf, (int(virus_x) - i * 22 - 15, int(virus_y) - 15))

        # Tux fugindo
        if player_animator:
            player_animator.current_direction = "right"
            img = player_animator.get_current_image()
            if img:
                rect = img.get_rect(center=(int(tux_x), int(tux_y)))
                screen.blit(img, rect)
        else:
            # placeholder simples se não houver animator disponível
            pygame.draw.ellipse(screen, WHITE, (int(tux_x) - 20, int(tux_y) - 28, 40, 56))
            pygame.draw.ellipse(screen, BLACK, (int(tux_x) - 14, int(tux_y) - 22, 28, 44))

        # glitches de corrupção aumentam conforme o vírus se aproxima
        proximity = max(0.0, 1.0 - (abs(tux_x - virus_x) / 260))
        _draw_corruption_glitches(screen, tick, intensity=1.0 + proximity * 2.5)

        # ── Texto narrativo no topo ──────────────────────────────────────────────
        for t_start, t_end, texto, cor in script:
            if t_start <= elapsed < t_end:
                fade_in  = min(1.0, (elapsed - t_start) / 300)
                fade_out = min(1.0, (t_end - elapsed) / 300)
                alpha = max(0.0, min(fade_in, fade_out))
                txt_surf = font_med.render(texto, True, cor)
                txt_surf.set_alpha(int(255 * alpha))

                shadow = font_med.render(texto, True, BLACK)
                shadow.set_alpha(int(180 * alpha))
                rect = txt_surf.get_rect(center=(W // 2, 90))
                screen.blit(shadow, (rect.x + 2, rect.y + 2))
                screen.blit(txt_surf, rect)
                break

        # barra de alerta pulsante no topo
        alert_pulse = abs(math.sin(tick * 0.15))
        bar_h = 6
        bar_col = tuple(int(c * alert_pulse) for c in NEON_RED)
        pygame.draw.rect(screen, bar_col, (0, 0, W, bar_h))
        pygame.draw.rect(screen, bar_col, (0, H - bar_h, W, bar_h))

        # ── Indicação de pular ───────────────────────────────────────────────────
        skip_alpha = int(140 + 80 * abs(math.sin(tick * 0.06)))
        skip_surf = font_skip.render("[ PRESSIONE ENTER / ESC PARA PULAR ]", True, (180, 180, 180))
        skip_surf.set_alpha(skip_alpha)
        screen.blit(skip_surf, skip_surf.get_rect(center=(W // 2, H - 28)))

        _draw_scanlines(screen, alpha=30)

        pygame.display.flip()
        clock.tick(60)
        tick += 1


# ─── Teste isolado ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    pygame.display.set_caption("Teste — Intro Chase")
    clock = pygame.time.Clock()

    show_intro_chase(screen, clock)

    pygame.quit()
    sys.exit()
