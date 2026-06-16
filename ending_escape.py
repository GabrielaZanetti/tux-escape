"""
ending_escape.py
────────────────
Cena final do Tux Escape: o Tux sai de dentro do computador para o mundo real.

Sequência:
  1. Terminal: mensagem de vitória digitada linha por linha (estilo briefing)
  2. "Racha" na tela — efeito de glitch abrindo uma fenda
  3. Tux voa em direção ao centro da tela e some pela fenda
  4. Fade para preto total
  5. Tela de créditos / parabéns com efeito de partículas
"""

import pygame
import sys
import math
import random
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Paleta ────────────────────────────────────────────────────────────────────
PURE_BLACK  = (0,   0,   0  )
PURE_WHITE  = (255, 255, 255)
NEON_CYAN   = (0,   220, 220)
NEON_GREEN  = (0,   210, 80 )
NEON_AMBER  = (255, 180, 0  )
NEON_RED    = (220, 30,  30 )
NEON_PURPLE = (160, 60,  240)
GRID_LINE   = (10,  28,  28 )
DIM_GREEN   = (0,   60,  30 )


# ─── Utilitários compartilhados ────────────────────────────────────────────────

def _draw_grid(surface):
    w, h = surface.get_width(), surface.get_height()
    for x in range(0, w, 40):
        pygame.draw.line(surface, GRID_LINE, (x, 0), (x, h), 1)
    for y in range(0, h, 40):
        pygame.draw.line(surface, GRID_LINE, (0, y), (w, y), 1)


def _draw_scanlines(surface, alpha=30):
    h = surface.get_height()
    w = surface.get_width()
    scan = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(0, h, 4):
        pygame.draw.line(scan, (0, 0, 0, alpha), (0, y), (w, y), 1)
    surface.blit(scan, (0, 0))


def _make_hex_drops(surface, count=60):
    w, h = surface.get_width(), surface.get_height()
    return [
        {
            "x": random.randint(0, w - 12),
            "y": random.uniform(-h, 0),
            "speed": random.uniform(1.2, 3.0),
        }
        for _ in range(count)
    ]


def _draw_hex_rain(surface, drops, font_tiny):
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


# ─── ETAPA 1 — Terminal de vitória ─────────────────────────────────────────────

VICTORY_LINES = [
    ("SYS", NEON_GREEN,  "VÍRUS [LOGIK.EXE] ELIMINADO COM SUCESSO."),
    ("SYS", NEON_GREEN,  "Todos os circuitos restaurados. Sistema limpo."),
    ("TUX", NEON_CYAN,   "Finalmente... consegui! Mas ainda estou preso aqui."),
    ("SYS", NEON_AMBER,  "AVISO: barreira digital ainda ativa."),
    ("TUX", NEON_CYAN,   "Se eu usar a energia liberada das portas..."),
    ("TUX", NEON_CYAN,   "...posso abrir uma fenda na tela e sair!"),
    ("ERR", NEON_RED,    "SOBRECARGA DE ENERGIA DETECTADA NO SETOR 0x00!"),
    ("SYS", NEON_GREEN,  "Iniciando protocolo de EVASÃO DIGITAL..."),
    ("SYS", NEON_AMBER,  "BOA SORTE, TUX. O MUNDO REAL TE ESPERA."),
]


def _show_victory_terminal(screen, clock):
    W, H = screen.get_width(), screen.get_height()
    font_title  = pygame.font.Font(None, 52)
    font_label  = pygame.font.Font(None, 28)
    font_body   = pygame.font.Font(None, 28)
    font_tiny   = pygame.font.Font(None, 18)
    font_skip   = pygame.font.Font(None, 22)

    drops = _make_hex_drops(screen)
    CHARS_PER_TICK = 2
    linha_atual = 0
    char_atual  = 0
    textos_visiveis = []
    tick = 0
    phase_complete = False
    LINHA_H  = 38
    LOG_TOP  = 140
    LOG_LEFT = 60
    cor_titulo = NEON_GREEN
    titulo = ">> SISTEMA RESTAURADO — FUGA INICIADA <<"

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    if phase_complete or event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        textos_visiveis = [(t, c, tx) for t, c, tx in VICTORY_LINES]
                        linha_atual = len(VICTORY_LINES)
                        phase_complete = True
            if event.type == pygame.MOUSEBUTTONDOWN and phase_complete:
                running = False

        # digitação
        if linha_atual < len(VICTORY_LINES):
            tag, cor, texto_completo = VICTORY_LINES[linha_atual]
            if len(textos_visiveis) <= linha_atual:
                textos_visiveis.append((tag, cor, ""))
            char_atual += CHARS_PER_TICK
            parcial = texto_completo[:char_atual]
            textos_visiveis[linha_atual] = (tag, cor, parcial)
            if char_atual >= len(texto_completo):
                char_atual  = 0
                linha_atual += 1
        elif not phase_complete:
            phase_complete = True

        # render
        screen.fill(PURE_BLACK)
        _draw_grid(screen)
        _draw_hex_rain(screen, drops, font_tiny)

        # borda
        m = 18
        pygame.draw.rect(screen, cor_titulo, (m, m, W - m*2, H - m*2), 2)

        # título pulsante
        pulse = (math.sin(tick * 0.07) + 1.0) / 2.0
        bright = tuple(min(255, int(c * (0.7 + 0.3 * pulse))) for c in cor_titulo)
        title_surf = font_title.render(titulo, True, bright)
        screen.blit(title_surf, title_surf.get_rect(center=(W // 2, 72)))

        # separador
        sep_surf = pygame.Surface((W - 120, 2), pygame.SRCALPHA)
        sep_alpha = int(160 + 95 * math.sin(tick * 0.12))
        sep_surf.fill((*cor_titulo, sep_alpha))
        screen.blit(sep_surf, (60, 100))

        # linhas de log
        for i, (tag, cor, parcial) in enumerate(textos_visiveis):
            y = LOG_TOP + i * LINHA_H
            label_surf = font_label.render(f"[{tag}]", True, cor)
            screen.blit(label_surf, (LOG_LEFT, y))
            body_surf = font_body.render(parcial, True, (200, 220, 200))
            screen.blit(body_surf, (LOG_LEFT + 74, y))
            if i == linha_atual and not phase_complete:
                if (tick // 18) % 2 == 0:
                    cur = font_body.render("▌", True, cor_titulo)
                    screen.blit(cur, (LOG_LEFT + 74 + body_surf.get_width() + 2, y))

        if phase_complete:
            skip_pulse = abs(math.sin(tick * 0.09))
            skip_col = tuple(min(255, int(c * skip_pulse)) for c in NEON_GREEN)
            skip_surf = font_skip.render("[ PRESSIONE ENTER ou CLIQUE PARA CONTINUAR ]", True, skip_col)
            skip_rect = skip_surf.get_rect(center=(W // 2, H - 36))
            screen.blit(skip_surf, skip_rect)

        _draw_scanlines(screen, 30)
        pygame.display.flip()
        clock.tick(60)
        tick += 1


# ─── ETAPA 2 — Glitch / fenda na tela ─────────────────────────────────────────

def _show_crack_effect(screen, clock, tux_img):
    """Racha abrindo no centro da tela, com Tux voando em direção à fenda."""
    W, H = screen.get_width(), screen.get_height()
    center = (W // 2, H // 2)

    # Tux começa no canto inferior esquerdo e voa para o centro
    tux_w = tux_img.get_width()
    tux_h = tux_img.get_height()

    total_frames = 180   # 3 segundos @ 60fps
    for frame in range(total_frames):
        t = frame / total_frames   # 0.0 → 1.0
        ease_t = t * t * (3 - 2 * t)  # smooth-step

        # ── Fundo com glitch crescente ──────────────────────────────────────
        screen.fill(PURE_BLACK)
        _draw_grid(screen)

        # Glitch horizontal: fatias da tela deslocadas
        glitch_intensity = int(ease_t * 40)
        if glitch_intensity > 2:
            for _ in range(int(ease_t * 8)):
                gy = random.randint(0, H - 20)
                gh = random.randint(4, 20)
                gshift = random.randint(-glitch_intensity, glitch_intensity)
                if gy + gh <= H:
                    strip = screen.subsurface((0, gy, W, gh)).copy()
                    screen.blit(strip, (gshift, gy))

        # ── Fenda central que cresce ────────────────────────────────────────
        crack_w = int(ease_t * 12)
        crack_h = int(ease_t * H * 0.85)
        crack_x = center[0] - crack_w // 2
        crack_y = center[1] - crack_h // 2

        # brilho ao redor da fenda
        if crack_w > 0:
            glow_surf = pygame.Surface((crack_w + 60, crack_h + 60), pygame.SRCALPHA)
            glow_alpha = int(ease_t * 180)
            pygame.draw.rect(glow_surf, (0, 220, 220, glow_alpha),
                             (30, 30, crack_w, crack_h))
            screen.blit(glow_surf, (crack_x - 30, crack_y - 30))

            # raio de luz branca interno
            pygame.draw.rect(screen, PURE_WHITE, (crack_x, crack_y, max(1, crack_w), crack_h))

            # faíscas ao redor da fenda
            for _ in range(int(ease_t * 20)):
                sx = crack_x + random.randint(-60, crack_w + 60)
                sy = crack_y + random.randint(0, crack_h)
                sl = random.randint(3, 15)
                sc = random.choice([NEON_CYAN, NEON_GREEN, PURE_WHITE, NEON_AMBER])
                pygame.draw.line(screen, sc, (sx, sy),
                                 (sx + random.randint(-sl, sl), sy + random.randint(-sl, sl)), 2)

        # ── Tux voando em direção à fenda ───────────────────────────────────
        start_x, start_y = 100, H - 150
        end_x = center[0] - tux_w // 2
        end_y = center[1] - tux_h // 2

        # Trajetória em arco (parábola)
        tux_x = int(start_x + (end_x - start_x) * ease_t)
        arc_offset = -math.sin(ease_t * math.pi) * 80  # sobe no meio do caminho
        tux_y = int(start_y + (end_y - start_y) * ease_t + arc_offset)

        # Tux encolhe ao se aproximar da fenda
        scale_factor = 1.0 - ease_t * 0.7
        scaled_w = max(4, int(tux_w * scale_factor))
        scaled_h = max(4, int(tux_h * scale_factor))
        scaled_tux = pygame.transform.smoothscale(tux_img, (scaled_w, scaled_h))

        # Sombra de velocidade (motion blur simples)
        if frame > 30:
            trail_alpha = int((1 - ease_t) * 80)
            for trail_i in range(1, 4):
                prev_t = max(0, ease_t - trail_i * 0.03)
                prev_ease = prev_t * prev_t * (3 - 2 * prev_t)
                tx = int(start_x + (end_x - start_x) * prev_ease)
                ty_arc = -math.sin(prev_ease * math.pi) * 80
                ty = int(start_y + (end_y - start_y) * prev_ease + ty_arc)
                trail = scaled_tux.copy()
                trail.set_alpha(trail_alpha // trail_i)
                screen.blit(trail, (tx, ty))

        screen.blit(scaled_tux, (tux_x, tux_y))

        # ── Texto de status ────────────────────────────────────────────────
        font_status = pygame.font.Font(None, 30)
        pct = int(ease_t * 100)
        status = font_status.render(f"ABRINDO FENDA DIGITAL... {pct}%", True, NEON_CYAN)
        screen.blit(status, status.get_rect(center=(W // 2, H - 40)))

        _draw_scanlines(screen, 25)
        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return  # pula

    # Flash final branco
    for alpha in range(0, 256, 12):
        flash = pygame.Surface((W, H))
        flash.fill(PURE_WHITE)
        flash.set_alpha(alpha)
        screen.blit(flash, (0, 0))
        pygame.display.flip()
        clock.tick(60)


# ─── ETAPA 3 — Tela de créditos ────────────────────────────────────────────────

class Particle:
    def __init__(self, W, H):
        self.x = random.randint(0, W)
        self.y = random.randint(0, H)
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-3, -0.5)
        self.size = random.randint(2, 6)
        self.color = random.choice([NEON_CYAN, NEON_GREEN, NEON_AMBER, NEON_PURPLE, PURE_WHITE])
        self.life = random.randint(40, 120)
        self.max_life = self.life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.04   # gravity suave
        self.life -= 1

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
        surface.blit(s, (int(self.x) - self.size, int(self.y) - self.size))


def _show_credits(screen, clock, tux_img):
    W, H = screen.get_width(), screen.get_height()

    font_big    = pygame.font.Font(None, 86)
    font_sub    = pygame.font.Font(None, 42)
    font_small  = pygame.font.Font(None, 30)
    font_tiny   = pygame.font.Font(None, 22)

    particles = []
    tick = 0
    # fade in
    fade_alpha = 255

    # Monitor desenhado na cena — Tux sai de um monitor 8-bit
    monitor_w, monitor_h = 300, 220
    monitor_x = W // 2 - monitor_w // 2
    monitor_y = H // 2 - 30

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                running = False

        # adiciona partículas
        if tick % 3 == 0:
            particles.append(Particle(W, H))
        particles = [p for p in particles if p.life > 0]
        for p in particles:
            p.update()

        # ── Background escuro com grid ───────────────────────────────────
        screen.fill((5, 5, 10))
        _draw_grid(screen)

        # ── Partículas ───────────────────────────────────────────────────
        for p in particles:
            p.draw(screen)

        # ── Monitor 8-bit ────────────────────────────────────────────────
        # Carcaça
        pygame.draw.rect(screen, (40, 40, 50),
                         (monitor_x - 20, monitor_y - 10, monitor_w + 40, monitor_h + 60),
                         border_radius=16)
        pygame.draw.rect(screen, NEON_CYAN,
                         (monitor_x - 20, monitor_y - 10, monitor_w + 40, monitor_h + 60),
                         3, border_radius=16)
        # Tela do monitor (escura — vazia, Tux já saiu)
        screen_rect = pygame.Rect(monitor_x, monitor_y, monitor_w, monitor_h)
        pygame.draw.rect(screen, (10, 10, 15), screen_rect, border_radius=8)
        pygame.draw.rect(screen, (0, 80, 80), screen_rect, 2, border_radius=8)
        # Texto na tela do monitor
        empty_font = pygame.font.Font(None, 22)
        empty1 = empty_font.render("SISTEMA VAZIO", True, (0, 80, 80))
        empty2 = empty_font.render("TUX EVADIU :)", True, (0, 100, 60))
        screen.blit(empty1, empty1.get_rect(center=(W // 2, monitor_y + monitor_h // 2 - 14)))
        screen.blit(empty2, empty2.get_rect(center=(W // 2, monitor_y + monitor_h // 2 + 14)))
        # Base / pé do monitor
        pygame.draw.rect(screen, (40, 40, 50),
                         (W // 2 - 40, monitor_y + monitor_h + 50, 80, 20),
                         border_radius=6)
        pygame.draw.rect(screen, (40, 40, 50),
                         (W // 2 - 20, monitor_y + monitor_h + 48, 40, 60),
                         border_radius=4)

        # ── Tux fora do monitor — flutuando acima ────────────────────────
        tux_scale = 1.0 + 0.04 * math.sin(tick * 0.06)  # bobbing suave
        tw = int(tux_img.get_width() * tux_scale * 1.8)
        th = int(tux_img.get_height() * tux_scale * 1.8)
        tux_scaled = pygame.transform.smoothscale(tux_img, (tw, th))
        tux_x = W // 2 - tw // 2
        tux_y = monitor_y - th - 20 + int(5 * math.sin(tick * 0.06))
        screen.blit(tux_scaled, (tux_x, tux_y))

        # Halo de luz ao redor do Tux
        halo = pygame.Surface((tw + 60, th + 60), pygame.SRCALPHA)
        halo_alpha = int(60 + 30 * math.sin(tick * 0.08))
        pygame.draw.ellipse(halo, (*NEON_CYAN, halo_alpha),
                            (0, 0, tw + 60, th + 60))
        screen.blit(halo, (tux_x - 30, tux_y - 30))

        # ── Textos de crédito ────────────────────────────────────────────
        # Título principal pulsante
        pulse = (math.sin(tick * 0.05) + 1) / 2
        title_col = tuple(min(255, int(NEON_GREEN[i] * (0.7 + 0.3 * pulse))) for i in range(3))
        title_surf = font_big.render("LIBERDADE!", True, title_col)
        # sombra
        shadow = font_big.render("LIBERDADE!", True, (0, 40, 15))
        screen.blit(shadow, title_surf.get_rect(center=(W // 2 + 3, 68 + 3)))
        screen.blit(title_surf, title_surf.get_rect(center=(W // 2, 68)))

        sub_col = tuple(min(255, int(NEON_CYAN[i] * (0.6 + 0.4 * abs(math.sin(tick * 0.04))))) for i in range(3))
        sub_surf = font_sub.render("Tux escapou do computador!", True, sub_col)
        screen.blit(sub_surf, sub_surf.get_rect(center=(W // 2, 118)))

        # Linha separadora
        pygame.draw.line(screen, NEON_GREEN, (80, 145), (W - 80, 145), 1)

        # Rodapé
        footer = font_small.render("Obrigado por jogar  •  Tux Escape", True, (120, 180, 120))
        screen.blit(footer, footer.get_rect(center=(W // 2, H - 60)))

        prompt_pulse = abs(math.sin(tick * 0.08))
        prompt_col = tuple(int(NEON_AMBER[i] * prompt_pulse) for i in range(3))
        prompt = font_tiny.render("[ PRESSIONE QUALQUER TECLA PARA SAIR ]", True, prompt_col)
        screen.blit(prompt, prompt.get_rect(center=(W // 2, H - 30)))

        # ── Fade in inicial ──────────────────────────────────────────────
        if fade_alpha > 0:
            fade = pygame.Surface((W, H))
            fade.fill(PURE_WHITE)
            fade.set_alpha(fade_alpha)
            screen.blit(fade, (0, 0))
            fade_alpha = max(0, fade_alpha - 8)

        _draw_scanlines(screen, 25)
        pygame.display.flip()
        clock.tick(60)
        tick += 1


# ─── Função principal exportada ────────────────────────────────────────────────

def show_ending(screen, clock):
    """
    Chame esta função após a Fase 3 ser concluída.
    Ela exibe a sequência completa de final do jogo.
    """
    # Carrega imagem do Tux
    tux_path = os.path.join(BASE_DIR, "./images/front1.png")
    try:
        tux_img = pygame.image.load(tux_path).convert_alpha()
        # reduz para tamanho razoável
        tw, th = tux_img.get_size()
        scale = min(80 / tw, 100 / th)
        tux_img = pygame.transform.smoothscale(tux_img, (int(tw * scale), int(th * scale)))
    except Exception:
        # fallback: quadrado preto
        tux_img = pygame.Surface((60, 80), pygame.SRCALPHA)
        pygame.draw.ellipse(tux_img, PURE_WHITE, (5, 5, 50, 70))
        pygame.draw.ellipse(tux_img, PURE_BLACK, (15, 15, 30, 50))

    _show_victory_terminal(screen, clock)
    _show_crack_effect(screen, clock, tux_img)
    _show_credits(screen, clock, tux_img)


# ─── Teste isolado ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    pygame.display.set_caption("Teste — Ending Escape")
    clock = pygame.time.Clock()
    show_ending(screen, clock)
    pygame.quit()
    sys.exit()
