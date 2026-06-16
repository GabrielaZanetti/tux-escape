"""
terminal_animation.py
─────────────────────
Animação de texto estilo terminal hacker para "Tux Escape".
Adicione este arquivo ao projeto e importe show_terminal_briefing() onde precisar.

USO:
    from terminal_animation import show_terminal_briefing

    # Antes da Fase 1
    show_terminal_briefing(screen, clock, 1)

    # Antes da Fase 2
    show_terminal_briefing(screen, clock, 2)

    # Antes da Fase 3
    show_terminal_briefing(screen, clock, 3)
"""

import pygame
import sys
import math
import random

# ─── Paleta cyberpunk ──────────────────────────────────────────────────────────
PURE_BLACK   = (0,   0,   0  )
NEON_CYAN    = (0,   220, 220)
NEON_GREEN   = (0,   210, 80 )
NEON_PURPLE  = (160, 60,  240)
NEON_AMBER   = (255, 180, 0  )
NEON_RED     = (220, 30,  30 )
DIM_CYAN     = (0,   80,  80 )
DIM_GREEN    = (0,   60,  30 )
GRID_LINE    = (10,  28,  28 )

# ─── Conteúdo das briefings ────────────────────────────────────────────────────
BRIEFINGS = {
    1: {
        "titulo":  ">> MISSÃO 01 — INICIALIZAÇÃO <<",
        "cor_titulo": NEON_CYAN,
        "linhas": [
            ("SYS", NEON_GREEN,  "KERNEL BOOT: detectando ameaça..."),
            ("SYS", NEON_GREEN,  "Vírus [LOGIK.EXE] encontrado no barramento."),
            ("ERR", NEON_RED,    "ALARME: 3 portas lógicas bloqueadas!"),
            ("TUX", NEON_CYAN,   "Preciso reativar as portas AND, OR e NOR."),
            ("TUX", NEON_CYAN,   "Cada porta resolvida drena energia do vírus."),
            ("SYS", NEON_AMBER,  "DICA: encoste nas portas para interagir."),
            ("SYS", NEON_GREEN,  "Aguardando input do operador... GO."),
        ],
    },
    2: {
        "titulo":  ">> MISSÃO 02 — CAMADA PROFUNDA <<",
        "cor_titulo": NEON_PURPLE,
        "linhas": [
            ("SYS", NEON_GREEN,  "FASE 1 concluída. Vírus recuando..."),
            ("ERR", NEON_RED,    "ALERTA: novo núcleo detectado — LOGIK_CORE."),
            ("SYS", NEON_GREEN,  "Portas XOR, XNOR e NAND precisam de ativação."),
            ("TUX", NEON_CYAN,   "Essas portas operam em paridade e inversão."),
            ("TUX", NEON_CYAN,   "XOR: saída 1 só quando entradas DIFEREM."),
            ("TUX", NEON_CYAN,   "XNOR: saída 1 só quando entradas são IGUAIS."),
            ("TUX", NEON_CYAN,   "NAND: inverte o AND — quase sempre 1."),
            ("SYS", NEON_AMBER,  "DICA: experimente as entradas com calma."),
            ("SYS", NEON_GREEN,  "Decodificando camada 2... EXECUTE."),
        ],
    },
    3: {
        "titulo":  ">> MISSÃO 03 — CIRCUITO FINAL <<",
        "cor_titulo": NEON_RED,
        "linhas": [
            ("SYS", NEON_GREEN,  "Núcleo do vírus localizado no setor 0xFF."),
            ("ERR", NEON_RED,    "CRÍTICO: circuito combinado detectado!"),
            ("SYS", NEON_GREEN,  "Estrutura: AND(A,B,C)  OU  NOT(D)"),
            ("TUX", NEON_CYAN,   "Qualquer combinação que dê saída 1 funciona."),
            ("TUX", NEON_CYAN,   "Tente: A=1,B=1,C=1 com D em qualquer valor."),
            ("TUX", NEON_CYAN,   "Ou: mantenha D=0 e todas saem liberadas."),
            ("ERR", NEON_RED,    "TEMPO CRÍTICO — sinal do vírus aumentando!"),
            ("SYS", NEON_AMBER,  "Clique nas entradas A/B/C/D para alternar."),
            ("SYS", NEON_GREEN,  "ÚLTIMA CHANCE — RESOLVA O CIRCUITO AGORA."),
        ],
    },
}


# ─── Utilitários de desenho ────────────────────────────────────────────────────

def _draw_scanlines(surface, alpha=40):
    """Linhas horizontais finas que imitam um monitor CRT."""
    h = surface.get_height()
    w = surface.get_width()
    scan = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(0, h, 4):
        pygame.draw.line(scan, (0, 0, 0, alpha), (0, y), (w, y), 1)
    surface.blit(scan, (0, 0))


def _draw_grid(surface):
    """Grade cyberpunk ao fundo."""
    w, h = surface.get_width(), surface.get_height()
    for x in range(0, w, 40):
        pygame.draw.line(surface, GRID_LINE, (x, 0), (x, h), 1)
    for y in range(0, h, 40):
        pygame.draw.line(surface, GRID_LINE, (0, y), (w, y), 1)


def _draw_border(surface, color, tick):
    """Borda animada com cantos que 'correm'."""
    w, h = surface.get_width(), surface.get_height()
    m = 18           # margem
    corner = 40      # comprimento do traço de canto
    speed = (tick // 4) % corner

    pygame.draw.rect(surface, color, (m, m, w - m*2, h - m*2), 2)

    # cantos animados que percorrem a borda
    for cx, cy, dx, dy in [
        (m, m, 1, 0), (m, m, 0, 1),
        (w-m, m, -1, 0), (w-m, m, 0, 1),
        (m, h-m, 1, 0), (m, h-m, 0, -1),
        (w-m, h-m, -1, 0), (w-m, h-m, 0, -1),
    ]:
        x1 = cx + dx * speed
        y1 = cy + dy * speed
        x2 = cx + dx * (speed + 12)
        y2 = cy + dy * (speed + 12)
        pygame.draw.line(surface, (255, 255, 255), (x1, y1), (x2, y2), 3)


def _glitch_text(surface, text_surf, pos, tick, intensity=0.25):
    """
    Cola o texto com possíveis deslocamentos horizontais tipo glitch.
    intensity: 0.0 = nunca glita, 1.0 = glita sempre.
    """
    if random.random() < intensity and (tick % 7 < 2):
        shift = random.randint(-8, 8)
        # fatia colorida acima
        slice_h = random.randint(2, 8)
        sub = text_surf.subsurface((0, 0, text_surf.get_width(), min(slice_h, text_surf.get_height())))
        surface.blit(sub, (pos[0] + shift, pos[1]), special_flags=pygame.BLEND_ADD)
    else:
        surface.blit(text_surf, pos)


def _draw_hex_rain(surface, drops, font_tiny):
    """Caracteres hexadecimais caindo ao fundo (Matrix effect leve)."""
    hex_chars = "0123456789ABCDEF"
    for drop in drops:
        ch = random.choice(hex_chars)
        col = (0, random.randint(60, 130), random.randint(30, 80))
        surf = font_tiny.render(ch, True, col)
        surface.blit(surf, (drop["x"], int(drop["y"])))
        drop["y"] += drop["speed"]
        if drop["y"] > surface.get_height():
            drop["y"] = random.randint(-200, 0)
            drop["x"] = random.randint(0, surface.get_width() - 12)
            drop["speed"] = random.uniform(1.2, 3.0)


def _make_drops(surface, count=50):
    """Inicializa as gotas de chuva hexadecimal."""
    w, h = surface.get_width(), surface.get_height()
    return [
        {
            "x": random.randint(0, w - 12),
            "y": random.uniform(-h, 0),
            "speed": random.uniform(1.2, 3.0),
        }
        for _ in range(count)
    ]


# ─── Animação principal ────────────────────────────────────────────────────────

def show_terminal_briefing(screen, clock, phase_number: int):
    """
    Exibe a briefing estilo terminal hacker antes de cada fase.

    Parâmetros
    ----------
    screen : pygame.Surface
    clock  : pygame.time.Clock
    phase_number : int  — 1, 2 ou 3
    """
    W, H = screen.get_width(), screen.get_height()

    # ── Fontes ──────────────────────────────────────────────────────────────────
    font_title  = pygame.font.Font(None, 52)
    font_label  = pygame.font.Font(None, 28)   # [SYS] / [ERR] / [TUX]
    font_body   = pygame.font.Font(None, 28)
    font_cursor = pygame.font.Font(None, 28)
    font_tiny   = pygame.font.Font(None, 18)
    font_skip   = pygame.font.Font(None, 22)

    # ── Dados da briefing ────────────────────────────────────────────────────────
    data = BRIEFINGS.get(phase_number, BRIEFINGS[1])
    titulo     = data["titulo"]
    cor_titulo = data["cor_titulo"]
    linhas     = data["linhas"]   # lista de (tag, cor, texto)

    # ── Estado de digitação ──────────────────────────────────────────────────────
    CHARS_PER_TICK = 2        # quantos caracteres adicionar por frame
    linha_atual    = 0
    char_atual     = 0
    textos_visiveis: list[tuple[str, tuple, str]] = []   # (tag, cor, texto_parcial)

    # chuva hexadecimal ao fundo
    drops = _make_drops(screen)

    tick    = 0
    running = True
    phase_complete = False   # True quando todo o texto foi digitado

    LINHA_H    = 38    # altura de cada linha de log
    LOG_TOP    = 140   # Y onde começa o bloco de log
    LOG_LEFT   = 60

    while running:
        # ── Eventos ──────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    if phase_complete or event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        # acelera: mostra tudo imediatamente
                        textos_visiveis = [(tag, cor, txt) for tag, cor, txt in linhas]
                        linha_atual     = len(linhas)
                        phase_complete  = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if phase_complete:
                    running = False

        # ── Lógica de digitação ───────────────────────────────────────────────────
        if linha_atual < len(linhas):
            tag, cor, texto_completo = linhas[linha_atual]

            # garante que a linha atual já existe em textos_visiveis
            if len(textos_visiveis) <= linha_atual:
                textos_visiveis.append((tag, cor, ""))

            char_atual += CHARS_PER_TICK
            parcial = texto_completo[:char_atual]
            textos_visiveis[linha_atual] = (tag, cor, parcial)

            if char_atual >= len(texto_completo):
                # linha concluída → avança para a próxima
                char_atual  = 0
                linha_atual += 1

                # pequena pausa de "carregamento" entre linhas (em frames)
                # implementada como tick bloqueado não é necessária —
                # o CHARS_PER_TICK já regula a velocidade naturalmente.

        elif not phase_complete:
            phase_complete = True

        # ── Renderização ──────────────────────────────────────────────────────────
        screen.fill(PURE_BLACK)
        _draw_grid(screen)
        _draw_hex_rain(screen, drops, font_tiny)

        # borda animada
        _draw_border(screen, cor_titulo, tick)

        # ── Título ────────────────────────────────────────────────────────────────
        pulse = (math.sin(tick * 0.07) + 1.0) / 2.0
        bright = tuple(min(255, int(c * (0.7 + 0.3 * pulse))) for c in cor_titulo)
        title_surf = font_title.render(titulo, True, bright)

        # sombra neon
        shadow = font_title.render(titulo, True, (
            int(cor_titulo[0] * 0.3),
            int(cor_titulo[1] * 0.3),
            int(cor_titulo[2] * 0.3),
        ))
        screen.blit(shadow, title_surf.get_rect(center=(W // 2 + 2, 72 + 2)))
        _glitch_text(screen, title_surf, title_surf.get_rect(center=(W // 2, 72)), tick, 0.15)

        # linha separadora piscante
        sep_alpha = int(160 + 95 * math.sin(tick * 0.12))
        sep_surf  = pygame.Surface((W - 120, 2), pygame.SRCALPHA)
        sep_surf.fill((*cor_titulo, sep_alpha))
        screen.blit(sep_surf, (60, 100))

        # ── Log de linhas ─────────────────────────────────────────────────────────
        for i, (tag, cor, parcial) in enumerate(textos_visiveis):
            y = LOG_TOP + i * LINHA_H

            # rótulo [TAG]
            label_str  = f"[{tag}]"
            label_surf = font_label.render(label_str, True, cor)
            screen.blit(label_surf, (LOG_LEFT, y))

            # texto do corpo
            body_x = LOG_LEFT + 74
            body_surf = font_body.render(parcial, True, (200, 220, 200))
            screen.blit(body_surf, (body_x, y))

            # cursor piscante na linha sendo digitada
            if i == linha_atual and not phase_complete:
                if (tick // 18) % 2 == 0:
                    cur_x  = body_x + body_surf.get_width() + 2
                    cur    = font_cursor.render("▌", True, cor_titulo)
                    screen.blit(cur, (cur_x, y))

        # ── Mensagem de continuar ─────────────────────────────────────────────────
        if phase_complete:
            skip_pulse = abs(math.sin(tick * 0.09))
            skip_alpha = int(160 + 95 * skip_pulse)
            skip_col   = tuple(min(255, int(c * skip_pulse)) for c in NEON_GREEN)
            skip_surf  = font_skip.render("[ PRESSIONE ENTER ou CLIQUE PARA CONTINUAR ]", True, skip_col)
            skip_bg    = pygame.Surface((skip_surf.get_width() + 20, skip_surf.get_height() + 8), pygame.SRCALPHA)
            skip_bg.fill((0, 0, 0, 140))
            skip_rect  = skip_surf.get_rect(center=(W // 2, H - 36))
            screen.blit(skip_bg, (skip_rect.x - 10, skip_rect.y - 4))
            screen.blit(skip_surf, skip_rect)

        # ── Overlay de scanlines (por cima de tudo) ───────────────────────────────
        _draw_scanlines(screen, alpha=30)

        pygame.display.flip()
        clock.tick(60)
        tick += 1


# ─── Onde inserir no seu main.py ──────────────────────────────────────────────
#
#  Em show_portal_map(), antes de show_portal_phase(), adicione:
#
#      from terminal_animation import show_terminal_briefing
#
#      # Fase 1
#      show_terminal_briefing(screen, clock, 1)
#      completed, player_pos = show_portal_phase(...)
#
#      # Fase 2
#      show_terminal_briefing(screen, clock, 2)
#      completed, player_pos = show_portal_phase(...)
#
#      # Fase 3
#      show_terminal_briefing(screen, clock, 3)
#      show_portal_phase3(...)
#
# ─────────────────────────────────────────────────────────────────────────────


# ─── Teste isolado ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    pygame.display.set_caption("Teste — Terminal Briefing")
    clock = pygame.time.Clock()

    for fase in (1, 2, 3):
        show_terminal_briefing(screen, clock, fase)

    pygame.quit()
    sys.exit()
