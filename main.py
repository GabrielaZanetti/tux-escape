import pygame
import sys
import os
import math
from terminal_animation import show_terminal_briefing
from ending_escape import show_ending
from intro_chase import show_intro_chase
from intro_dialog import show_intro_dialog

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class PlayerAnimator:
    """Gerencia a animação do personagem baseado na direção e movimentação."""
    def __init__(self, images_path=None, scale=0.55):
        self.images_path = images_path or os.path.join(BASE_DIR, "images")
        self.scale = scale
        self.animations = {}
        self.current_direction = "front"
        self.current_frame = 0
        self.frame_counter = 0
        self.frame_delay = 8  # Frames para trocar de sprite (60/8 = 7.5 FPS)
        self.last_dx = 0
        self.last_dy = 0
        self.load_animations()
    
    def load_animations(self):
        """Carrega todas as imagens de animação."""
        fallback_path = os.path.join(BASE_DIR, "images", "tux.png")
        fallback_img = None
        if os.path.exists(fallback_path):
            fallback_img = pygame.image.load(fallback_path).convert_alpha()

        direction_files = {
            "front": "front",
            "back": "back",
            "left": "left",
            "right": "right",
        }
        for direction, file_prefix in direction_files.items():
            self.animations[direction] = []
            for i in range(1, 4):  # 3 frames por direção
                path = os.path.join(self.images_path, f"{file_prefix}{i}.png")
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                elif fallback_img:
                    img = fallback_img.copy()
                else:
                    img = pygame.Surface((40, 52), pygame.SRCALPHA)
                    pygame.draw.ellipse(img, (255, 255, 255), (6, 4, 28, 44))
                    pygame.draw.ellipse(img, (0, 0, 0), (10, 8, 20, 36))
                if self.scale != 1:
                    width = max(1, int(img.get_width() * self.scale))
                    height = max(1, int(img.get_height() * self.scale))
                    img = pygame.transform.smoothscale(img, (width, height))
                self.animations[direction].append(img)
    
    def update(self, dx, dy):
        """Atualiza a animação baseado no movimento."""
        # Só anima se houver movimento
        if dx != 0 or dy != 0:
            # Detecta a direção do movimento
            if abs(dx) > abs(dy):
                self.current_direction = "right" if dx > 0 else "left"
            else:
                self.current_direction = "front" if dy > 0 else "back"
            
            # Incrementa contador de frames apenas durante movimento
            self.frame_counter += 1
            if self.frame_counter >= self.frame_delay:
                self.frame_counter = 0
                frames = self.animations.get(self.current_direction, [])
                if frames:
                    self.current_frame = (self.current_frame + 1) % len(frames)
                else:
                    self.current_frame = 0
        else:
            # Reseta a animação quando parar de se mover
            self.frame_counter = 0
            self.current_frame = 0
    
    def get_current_image(self):
        """Retorna a imagem atual da animação."""
        frames = self.animations.get(self.current_direction, [])
        if not frames:
            for fallback_frames in self.animations.values():
                if fallback_frames:
                    frames = fallback_frames
                    break
        if frames:
            self.current_frame %= len(frames)
            return frames[self.current_frame]
        return None
    
    def get_rect(self, pos):
        """Retorna o rect da imagem atual centralizado na posição."""
        img = self.get_current_image()
        if img:
            return img.get_rect(center=pos)
        return pygame.Rect(pos[0], pos[1], int(40 * self.scale), int(52 * self.scale))

def load_intro_surface():
    path_png = os.path.join(BASE_DIR, "images", "intro.png")
    try:
        if os.path.exists(path_png):
            img = pygame.image.load(path_png)
            return img.convert_alpha()
    except Exception:
        pass

    return None


def load_menu_background():
    path_png = os.path.join(BASE_DIR, "images", "background_menu.png")
    try:
        if os.path.exists(path_png):
            img = pygame.image.load(path_png)
            return img.convert()
    except Exception:
        pass
    return None


def make_radial_glow(radius, color, max_alpha=70, steps=20):
    """Pre-renderiza um halo radial suave (camadas concentricas, sem dependencia de blur)."""
    surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for i in range(steps, 0, -1):
        r = max(1, int(radius * i / steps))
        t = i / steps
        alpha = int(max_alpha * (1 - t) ** 1.6)
        pygame.draw.circle(surf, color + (alpha,), (radius, radius), r)
    return surf


def make_glow_text(font, text, color, glow_color, glow_passes=7, max_offset=16):
    """Pre-renderiza um texto com camadas de brilho neon.
    Retorna (glow_surf, base_surf); glow_surf deve ser desenhado atras de base_surf,
    centralizados no mesmo ponto."""
    base = font.render(text, True, color)
    pad = max_offset * 2 + 10
    glow_surf = pygame.Surface((base.get_width() + pad * 2, base.get_height() + pad * 2), pygame.SRCALPHA)
    glow_text = font.render(text, True, glow_color)
    for i in range(glow_passes, 0, -1):
        offset = int(max_offset * (i / glow_passes))
        alpha = int(46 * (1 - i / (glow_passes + 1)) + 14)
        w = max(1, glow_text.get_width() + offset)
        h = max(1, glow_text.get_height() + offset)
        scaled = pygame.transform.smoothscale(glow_text, (w, h))
        scaled.set_alpha(alpha)
        glow_surf.blit(scaled, scaled.get_rect(center=(glow_surf.get_width() // 2, glow_surf.get_height() // 2)))
    return glow_surf, base


def make_glow_panel(size, color, radius=18, glow_passes=6, max_offset=14):
    """Pre-renderiza o brilho de um painel/botao arredondado."""
    w, h = size
    pad = max_offset * 2 + 6
    glow_surf = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    base_shape = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(base_shape, color, (0, 0, w, h), border_radius=radius)
    for i in range(glow_passes, 0, -1):
        offset = int(max_offset * (i / glow_passes))
        alpha = int(40 * (1 - i / (glow_passes + 1)) + 10)
        scaled = pygame.transform.smoothscale(base_shape, (w + offset, h + offset))
        scaled.set_alpha(alpha)
        glow_surf.blit(scaled, scaled.get_rect(center=(glow_surf.get_width() // 2, glow_surf.get_height() // 2)))
    return glow_surf


def main_menu():
    pygame.init()
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 700
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tux Escape - Menu")

    WHITE = (255, 255, 255)
    SOFT_WHITE = (225, 235, 230)
    RED = (235, 60, 60)
    GREEN = (40, 215, 110)
    GREEN_DARK = (12, 70, 38)
    BLACK = (0, 0, 0)
    GREY_GREEN = (120, 160, 140)

    title_text = "TUX ESCAPE"
    subtitle_text = "Um virus assumiu o sistema. Resolva os circuitos e ajude o Tux a escapar."
    button_text = "INICIAR"

    font_title = pygame.font.Font(None, 96)
    font_title.set_bold(True)
    font_subtitle = pygame.font.Font(None, 28)
    font_button = pygame.font.Font(None, 40)
    font_button.set_bold(True)
    font_footer = pygame.font.Font(None, 22)
    font_tag = pygame.font.Font(None, 20)

    intro_surface = load_intro_surface()
    bg_surface = load_menu_background()

    # Pre-render do titulo com brilho neon (vermelho perigo)
    title_glow, title_base = make_glow_text(font_title, title_text, WHITE, RED, glow_passes=8, max_offset=22)
    subtitle_base = font_subtitle.render(subtitle_text, True, SOFT_WHITE)

    # Pre-render do brilho do botao (verde)
    btn_w, btn_h = 280, 76
    btn_glow = make_glow_panel((btn_w, btn_h), GREEN, radius=16, glow_passes=7, max_offset=18)

    # Escala da arte do personagem
    char_img = None
    char_base_size = None
    if intro_surface:
        iw, ih = intro_surface.get_size()
        target_h = 300
        scale = target_h / ih
        char_base_size = (int(iw * scale), int(ih * scale))
        char_img = pygame.transform.smoothscale(intro_surface, char_base_size)

    char_halo = make_radial_glow(170, GREEN, max_alpha=65, steps=22)

    clock = pygame.time.Clock()
    running = True
    start_game = False
    t0 = pygame.time.get_ticks()

    # Layout vertical
    title_y = 96
    subtitle_y = 156
    char_center_y = 360
    button_y = 552
    footer_y = SCREEN_HEIGHT - 34

    btn_rect = pygame.Rect(0, 0, btn_w, btn_h)
    btn_rect.center = (SCREEN_WIDTH // 2, button_y)

    while running:
        elapsed = pygame.time.get_ticks() - t0
        pulse = (math.sin(elapsed / 480.0) + 1.0) / 2.0  # 0..1 suave
        mouse_pos = pygame.mouse.get_pos()
        hover = btn_rect.collidepoint(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_rect.collidepoint(event.pos):
                    start_game = True
                    running = False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    start_game = True
                    running = False
                if event.key == pygame.K_ESCAPE:
                    running = False

        # ── Fundo ────────────────────────────────────────────────
        if bg_surface:
            screen.blit(bg_surface, (0, 0))
        else:
            screen.fill((10, 14, 12))

        # ── Titulo com brilho pulsante ───────────────────────────
        glow_alpha = 150 + int(80 * pulse)
        glow_copy = title_glow.copy()
        glow_copy.set_alpha(glow_alpha)
        title_pos = (SCREEN_WIDTH // 2, title_y)
        screen.blit(glow_copy, glow_copy.get_rect(center=title_pos))
        screen.blit(title_base, title_base.get_rect(center=title_pos))

        subtitle_pos = subtitle_base.get_rect(center=(SCREEN_WIDTH // 2, subtitle_y))
        screen.blit(subtitle_base, subtitle_pos)

        # ── Personagem com halo suave ──────────────────────────────
        if char_img:
            halo_copy = char_halo.copy()
            halo_copy.set_alpha(150 + int(80 * pulse))
            screen.blit(halo_copy, halo_copy.get_rect(center=(SCREEN_WIDTH // 2, char_center_y)))
            char_rect = char_img.get_rect(center=(SCREEN_WIDTH // 2, char_center_y))
            screen.blit(char_img, char_rect)
        else:
            ph_rect = pygame.Rect(0, 0, 360, 240)
            ph_rect.center = (SCREEN_WIDTH // 2, char_center_y)
            pygame.draw.rect(screen, (30, 40, 36), ph_rect, border_radius=12)
            pygame.draw.rect(screen, GREEN_DARK, ph_rect, 2, border_radius=12)
            txt_ph = font_footer.render("(intro.png nao encontrado)", True, SOFT_WHITE)
            screen.blit(txt_ph, txt_ph.get_rect(center=ph_rect.center))

        # ── Botao iniciar ───────────────────────────────────────
        scale = 1.04 if hover else 1.0
        glow_alpha_btn = 230 if hover else 140 + int(60 * pulse)
        glow_b = btn_glow.copy()
        glow_b.set_alpha(glow_alpha_btn)
        screen.blit(glow_b, glow_b.get_rect(center=btn_rect.center))

        draw_w, draw_h = int(btn_w * scale), int(btn_h * scale)
        draw_rect = pygame.Rect(0, 0, draw_w, draw_h)
        draw_rect.center = btn_rect.center

        fill_top = (60, 235, 130) if hover else GREEN
        fill_bottom = (20, 130, 70) if hover else (16, 110, 60)
        btn_surf = pygame.Surface((draw_w, draw_h), pygame.SRCALPHA)
        for yy in range(draw_h):
            t = yy / max(1, draw_h - 1)
            col = tuple(int(fill_top[i] + (fill_bottom[i] - fill_top[i]) * t) for i in range(3))
            pygame.draw.line(btn_surf, col + (255,), (0, yy), (draw_w, yy))
        mask = pygame.Surface((draw_w, draw_h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, draw_w, draw_h), border_radius=16)
        btn_surf_masked = pygame.Surface((draw_w, draw_h), pygame.SRCALPHA)
        btn_surf_masked.blit(btn_surf, (0, 0))
        btn_surf_masked.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        screen.blit(btn_surf_masked, draw_rect)
        pygame.draw.rect(screen, WHITE, draw_rect, 3, border_radius=16)

        play_pts = [
            (draw_rect.centerx - 70, draw_rect.centery - 11),
            (draw_rect.centerx - 70, draw_rect.centery + 11),
            (draw_rect.centerx - 52, draw_rect.centery),
        ]
        pygame.draw.polygon(screen, BLACK, play_pts)
        label = font_button.render(button_text, True, BLACK)
        screen.blit(label, label.get_rect(center=(draw_rect.centerx + 14, draw_rect.centery)))

        # ── Rodape com instrucoes ───────────────────────────────
        footer_text = "WASD / Setas para mover   •   ESC para voltar a qualquer momento"
        footer_surf = font_footer.render(footer_text, True, GREY_GREEN)
        screen.blit(footer_surf, footer_surf.get_rect(center=(SCREEN_WIDTH // 2, footer_y)))

        tag_surf = font_tag.render("Logica Digital • v1.0", True, (90, 120, 105))
        screen.blit(tag_surf, (16, SCREEN_HEIGHT - 26))

        pygame.display.flip()
        clock.tick(60)

    if start_game:
        show_intro_chase(screen, clock)
        show_intro_dialog(screen, clock)
        run_game(screen, clock)

    pygame.quit()
    sys.exit()


def show_portal_map(screen, clock):
    player_animator = PlayerAnimator()
    player_pos = [500, 600]

    show_terminal_briefing(screen, clock, 1)          # ← linha nova

    completed, player_pos = show_portal_phase(
        screen,
        clock,
        "FASE 1",
        build_portal_gates(1),
        player_animator,
        player_pos,
        bg_filename="background_fase1.png",
    )
    if not completed:
        return

    animate_phase_transition(screen, clock, player_animator, player_pos, "FASE 1", "FASE 2")

    show_terminal_briefing(screen, clock, 2)          # ← linha nova

    player_animator = PlayerAnimator()
    player_pos = [120, 600]

    completed, player_pos = show_portal_phase(
        screen,
        clock,
        "FASE 2",
        build_portal_gates(2),
        player_animator,
        player_pos,
        bg_filename="background_fase2.png",
    )
    if not completed:
        return

    animate_phase_transition(screen, clock, player_animator, player_pos, "FASE 2", "FASE 3")

    show_terminal_briefing(screen, clock, 3)          # ← linha nova

    player_animator = PlayerAnimator()
    player_pos = [120, 600]

    show_portal_phase3(screen, clock, player_animator, player_pos)

    # ── FINAL: Tux escapa do computador ────────────────────────────────────────
    show_ending(screen, clock)


def show_gate_explanation(screen, clock, gate_name, gate_color):
    """Tela de explicação detalhada de cada porta lógica com teste interativo"""
    font_big = pygame.font.Font(None, 64)
    font_medium = pygame.font.Font(None, 44)
    font_small = pygame.font.Font(None, 32)
    font_tiny = pygame.font.Font(None, 24)

    pure_black = (0, 0, 0)
    pure_white = (255, 255, 255)
    green_on = (0, 255, 0)
    red_off = (128, 0, 0)
    dark_gray = (40, 40, 40)

    descriptions = {
        "AND": (
            "Porta E (AND)",
            "x AND x = x",
            "A porta AND so libera saida 1 quando as duas entradas estao em 1 ao mesmo tempo.",
        ),
        "OR": (
            "Porta OU (OR)",
            "x OR x = x",
            "A porta OR libera saida 1 quando pelo menos uma das entradas esta em 1.",
        ),
        "NOR": (
            "Porta NOR",
            "x NOR x = 0",
            "A porta NOR so libera saida 1 quando nenhuma entrada esta em 1.",
        ),
        "XOR": (
            "Porta XOR",
            "x XOR x = 0",
            "A porta XOR libera saida 1 apenas quando as entradas sao diferentes.",
        ),
        "XNOR": (
            "Porta XNOR",
            "x XNOR x = 1",
            "A porta XNOR libera saida 1 quando as duas entradas sao iguais.",
        ),
        "NAND": (
            "Porta NAND",
            "x NAND x = 1",
            "A porta NAND libera saida 1 somente quando uma ou nenhuma entrada esta em 1.",
        ),
    }

    input1 = 0
    input2 = 0
    interacted = False
    completed = False

    btn_input1 = pygame.Rect(120, 215, 54, 54)
    btn_input2 = pygame.Rect(120, 335, 54, 54)

    gate_title, gate_formula, gate_expl = descriptions[gate_name]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_input1.collidepoint(event.pos):
                    input1 = 1 - input1
                    interacted = True
                if btn_input2.collidepoint(event.pos):
                    input2 = 1 - input2
                    interacted = True

        if gate_name == "AND":
            output = input1 and input2
        elif gate_name == "OR":
            output = input1 or input2
        elif gate_name == "NOR":
            output = not (input1 or input2)
        elif gate_name == "XOR":
            output = bool(input1) != bool(input2)
        elif gate_name == "XNOR":
            output = bool(input1) == bool(input2)
        else:
            output = not (input1 and input2)

        completed = interacted and bool(output)

        screen.fill(pure_black)
        draw_gate_explanation_scene(screen, gate_name, gate_color, input1, input2, output, completed)

        title_text = font_big.render(gate_title, True, gate_color)
        formula_text = font_small.render(gate_formula, True, pure_white)
        expl_text = font_tiny.render(gate_expl, True, pure_white)
        screen.blit(title_text, title_text.get_rect(center=(screen.get_width() // 2, 62)))
        screen.blit(formula_text, formula_text.get_rect(center=(screen.get_width() // 2, 112)))
        screen.blit(expl_text, expl_text.get_rect(center=(screen.get_width() // 2, 148)))

        # Operação e instrução
        if gate_name == "AND":
            operation = f"{input1} AND {input2} = {int(output)}"
        elif gate_name == "OR":
            operation = f"{input1} OR {input2} = {int(output)}"
        elif gate_name == "NOR":
            operation = f"{input1} NOR {input2} = {int(output)}"
        elif gate_name == "XOR":
            operation = f"{input1} XOR {input2} = {int(output)}"
        elif gate_name == "XNOR":
            operation = f"{input1} XNOR {input2} = {int(output)}"
        else:
            operation = f"{input1} NAND {input2} = {int(output)}"
        op_text = font_small.render(operation, True, gate_color)
        screen.blit(op_text, (100, 520))

        pygame.display.flip()
        clock.tick(60)

    return completed


def build_portal_gates(phase_number):
    if phase_number == 1:
        return [
            {"name": "AND", "color": (0, 100, 200), "rect": pygame.Rect(150, 150, 150, 200), "done": False},
            {"name": "OR", "color": (255, 255, 0), "rect": pygame.Rect(425, 150, 150, 200), "done": False},
            {"name": "NOR", "color": (0, 200, 0), "rect": pygame.Rect(700, 150, 150, 200), "done": False},
        ]

    return [
        {"name": "XOR", "color": (255, 140, 0), "rect": pygame.Rect(150, 150, 150, 200), "done": False},
        {"name": "XNOR", "color": (180, 90, 220), "rect": pygame.Rect(425, 150, 150, 200), "done": False},
        {"name": "NAND", "color": (0, 180, 180), "rect": pygame.Rect(700, 150, 150, 200), "done": False},
    ]


def draw_gate_icon(surface, gate_name, rect, color, done=False):
    panel_color = (26, 26, 32)
    frame_color = tuple(min(255, c + 40) for c in color)
    wire_color = (230, 230, 230)
    button_on = (0, 210, 0)
    button_off = (120, 35, 35)
    lamp_on = (255, 220, 70)
    lamp_off = (90, 90, 90)

    pygame.draw.rect(surface, panel_color, rect, border_radius=18)
    pygame.draw.rect(surface, frame_color if done else color, rect, 4, border_radius=18)

    font = pygame.font.Font(None, 24)
    title = font.render(f"{gate_name}", True, (255, 255, 255))
    surface.blit(title, title.get_rect(center=(rect.centerx, rect.top + 24)))

    btn1 = pygame.Rect(rect.x + 24, rect.centery - 44, 38, 38)
    btn2 = pygame.Rect(rect.x + 24, rect.centery + 6, 38, 38)
    lamp = pygame.Rect(rect.right - 62, rect.centery - 22, 34, 44)

    # fios e conexoes
    pygame.draw.line(surface, wire_color, (btn1.right, btn1.centery), (lamp.left - 12, btn1.centery), 4)
    pygame.draw.line(surface, wire_color, (btn2.right, btn2.centery), (lamp.left - 12, btn2.centery), 4)
    pygame.draw.line(surface, wire_color, (lamp.left - 12, btn1.centery), (lamp.left - 12, btn2.centery), 4)
    pygame.draw.line(surface, wire_color, (lamp.left - 12, lamp.centery), (lamp.left, lamp.centery), 4)

    pygame.draw.circle(surface, button_on if done else button_off, btn1.center, 19)
    pygame.draw.circle(surface, button_on if done else button_off, btn2.center, 19)
    pygame.draw.circle(surface, (255, 255, 255), btn1.center, 19, 2)
    pygame.draw.circle(surface, (255, 255, 255), btn2.center, 19, 2)

    btn_font = pygame.font.Font(None, 22)
    b1 = btn_font.render("1", True, (255, 255, 255))
    b2 = btn_font.render("2", True, (255, 255, 255))
    surface.blit(b1, b1.get_rect(center=btn1.center))
    surface.blit(b2, b2.get_rect(center=btn2.center))

    pygame.draw.circle(surface, lamp_on if done else lamp_off, lamp.center, 18)
    pygame.draw.circle(surface, (255, 255, 255), lamp.center, 18, 2)
    if done:
        glow = pygame.Surface((80, 80), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 220, 70, 80), (40, 40), 22)
        surface.blit(glow, (lamp.centerx - 40, lamp.centery - 40))

    out_label = font.render("LUZ", True, (255, 255, 255))
    surface.blit(out_label, out_label.get_rect(center=(lamp.centerx, lamp.bottom + 12)))

    if done:
        ok_font = pygame.font.Font(None, 24)
        ok_text = ok_font.render("OK", True, (0, 210, 0))
        ok_bg = pygame.Rect(rect.right - 54, rect.top + 12, 40, 24)
        pygame.draw.rect(surface, (255, 255, 255), ok_bg, border_radius=6)
        surface.blit(ok_text, ok_text.get_rect(center=ok_bg.center))


def draw_gate_explanation_scene(surface, gate_name, gate_color, input1, input2, output, show_ok=False):
    bg = pygame.Surface(surface.get_size())
    bg.fill((10, 10, 12))
    for x in range(0, surface.get_width(), 30):
        pygame.draw.line(bg, (18, 18, 20), (x, 0), (x, surface.get_height()), 1)
    for y in range(0, surface.get_height(), 30):
        pygame.draw.line(bg, (18, 18, 20), (0, y), (surface.get_width(), y), 1)
    surface.blit(bg, (0, 0))

    gate_rect = pygame.Rect(surface.get_width() // 2 - 170, 220, 340, 180)
    panel_rect = pygame.Rect(80, 160, surface.get_width() - 160, 320)
    pygame.draw.rect(surface, (22, 22, 28), panel_rect, border_radius=18)
    pygame.draw.rect(surface, gate_color, panel_rect, 4, border_radius=18)

    wire_on = (0, 210, 0)
    wire_off = (120, 35, 35)
    wire1 = wire_on if input1 else wire_off
    wire2 = wire_on if input2 else wire_off
    wire_out = wire_on if output else wire_off

    btn1 = pygame.Rect(120, 215, 54, 54)
    btn2 = pygame.Rect(120, 335, 54, 54)
    lamp = pygame.Rect(surface.get_width() - 160, 260, 44, 80)

    pygame.draw.line(surface, wire1, (btn1.right, btn1.centery), (gate_rect.left, gate_rect.top + 42), 5)
    pygame.draw.line(surface, wire2, (btn2.right, btn2.centery), (gate_rect.left, gate_rect.bottom - 42), 5)
    pygame.draw.line(surface, wire_out, (gate_rect.right, gate_rect.centery), (lamp.left, lamp.centery), 5)

    pygame.draw.circle(surface, wire1, btn1.center, 25)
    pygame.draw.circle(surface, wire2, btn2.center, 25)
    pygame.draw.circle(surface, (255, 255, 255), btn1.center, 25, 2)
    pygame.draw.circle(surface, (255, 255, 255), btn2.center, 25, 2)
    font_btn = pygame.font.Font(None, 28)
    value1 = font_btn.render(str(input1), True, (255, 255, 255))
    value2 = font_btn.render(str(input2), True, (255, 255, 255))
    surface.blit(value1, value1.get_rect(center=btn1.center))
    surface.blit(value2, value2.get_rect(center=btn2.center))

    body_color = (242, 242, 242)
    outline = (8, 8, 8)
    left = gate_rect.left
    top = gate_rect.top
    bottom = gate_rect.bottom
    right = gate_rect.right
    mid_y = gate_rect.centery
    mid_x = gate_rect.centerx

    if gate_name in {"AND", "NAND"}:
        body = pygame.Rect(left + 10, top + 18, gate_rect.width - 20, gate_rect.height - 36)
        pygame.draw.rect(surface, body_color, (left + 10, top + 18, gate_rect.width // 2, gate_rect.height - 36))
        pygame.draw.arc(surface, body_color, body, math.radians(270), math.radians(90), 6)
        pygame.draw.line(surface, body_color, (left + 10, top + 18), (mid_x, top + 18), 6)
        pygame.draw.line(surface, body_color, (left + 10, bottom - 18), (mid_x, bottom - 18), 6)
        pygame.draw.line(surface, body_color, (left + 10, top + 18), (left + 10, bottom - 18), 6)
    else:
        points = [
            (left + 14, top + 18),
            (mid_x - 30, top + 26),
            (right - 26, mid_y),
            (mid_x - 30, bottom - 26),
            (left + 14, bottom - 18),
            (left + 42, mid_y),
        ]
        pygame.draw.polygon(surface, body_color, points)
        pygame.draw.aalines(surface, outline, True, points)

    if gate_name in {"XOR", "XNOR"}:
        extra = [(px - 14, py) for px, py in [
            (left + 14, top + 18),
            (mid_x - 30, top + 26),
            (right - 26, mid_y),
            (mid_x - 30, bottom - 26),
            (left + 14, bottom - 18),
            (left + 42, mid_y),
        ]]
        pygame.draw.aalines(surface, outline, True, extra)

    if gate_name in {"NOR", "XNOR", "NAND"}:
        pygame.draw.circle(surface, outline, (right + 16, mid_y), 8, 3)

    pygame.draw.line(surface, body_color, (right, mid_y), (right + 42, mid_y), 6)
    pygame.draw.rect(surface, outline, gate_rect.inflate(10, 10), 4, border_radius=18)

    pulse = (math.sin(pygame.time.get_ticks() / 140.0) + 1.0) / 2.0 if show_ok else 0.0
    if output:
        glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        glow_alpha = 60 + int(70 * pulse)
        glow_radius = 28 + int(8 * pulse)
        pygame.draw.circle(glow, (255, 220, 70, glow_alpha), (60, 60), glow_radius)
        surface.blit(glow, (lamp.centerx - 60, lamp.centery - 60))
    lamp_color = (255, 220, 70) if output else (85, 85, 85)
    if show_ok:
        lamp_color = (255, 235, 110) if pulse > 0.5 else (255, 215, 55)
    pygame.draw.circle(surface, lamp_color, lamp.center, 20)
    pygame.draw.circle(surface, (255, 255, 255), lamp.center, 20, 2)
    base = pygame.Rect(lamp.centerx - 12, lamp.bottom - 6, 24, 16)
    pygame.draw.rect(surface, (110, 110, 110), base)
    pygame.draw.rect(surface, (255, 255, 255), base, 2)

    if show_ok:
        ok_font = pygame.font.Font(None, 30)
        ok_text = ok_font.render("OK", True, (0, 210, 0))
        ok_bg = pygame.Rect(lamp.centerx - 28, lamp.top - 38, 56, 26)
        pygame.draw.rect(surface, (255, 255, 255), ok_bg, border_radius=8)
        surface.blit(ok_text, ok_text.get_rect(center=ok_bg.center))

    font_small = pygame.font.Font(None, 30)
    subtitle = font_small.render("Pressione ENTER ou ESC para voltar", True, (255, 255, 255))
    surface.blit(subtitle, subtitle.get_rect(center=(surface.get_width() // 2, surface.get_height() - 42)))


def animate_phase_transition(screen, clock, player_animator, start_pos, from_phase, to_phase):
    font_big = pygame.font.Font(None, 64)
    font_small = pygame.font.Font(None, 32)
    pure_black = (0, 0, 0)
    pure_white = (255, 255, 255)

    transition_pos = [start_pos[0], start_pos[1]]
    step = 6

    while transition_pos[0] < screen.get_width() + 80:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        player_animator.update(step, 0)
        transition_pos[0] += step

        screen.fill(pure_black)

        title = font_big.render(f"{from_phase} concluída", True, pure_white)
        subtitle = font_small.render(f"Indo para {to_phase}...", True, pure_white)
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 90)))
        screen.blit(subtitle, subtitle.get_rect(center=(screen.get_width() // 2, 150)))

        player_img = player_animator.get_current_image()
        if player_img:
            player_rect = player_animator.get_rect(transition_pos)
            screen.blit(player_img, player_rect)

        pygame.display.flip()
        clock.tick(60)


def show_portal_phase(screen, clock, phase_label, gates_info, player_animator, player_pos, bg_filename="background_cyberpunk.png"):
    font_big = pygame.font.Font(None, 64)
    font_small = pygame.font.Font(None, 32)
    font_tiny = pygame.font.Font(None, 20)

    pure_black = (0, 0, 0)
    pure_white = (255, 255, 255)

    # Carrega o fundo cyberpunk especifico da fase
    _bg_path = os.path.join(BASE_DIR, "images", bg_filename)
    _bg_surface = None
    if os.path.exists(_bg_path):
        _bg_surface = pygame.image.load(_bg_path).convert()

    player_speed = 4
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False, player_pos

        if all(gate.get("done") for gate in gates_info):
            return True, player_pos

        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += player_speed

        player_animator.update(dx, dy)

        next_pos = [player_pos[0] + dx, player_pos[1] + dy]
        next_pos[0] = max(50, min(screen.get_width() - 50, next_pos[0]))
        next_pos[1] = max(50, min(screen.get_height() - 100, next_pos[1]))
        player_pos = next_pos

        player_rect = player_animator.get_rect(player_pos)

        for i, gate in enumerate(gates_info):
            gate_trigger = pygame.Rect(
                gate["rect"].x + 8,
                gate["rect"].y,
                gate["rect"].width - 16,
                max(36, gate["rect"].height // 5),
            )
            if player_rect.colliderect(gate_trigger):
                if not gate.get("done"):
                    solved = show_gate_explanation(screen, clock, gate["name"], gate["color"])
                    if solved:
                        gates_info[i]["done"] = True
                player_pos = [gate["rect"].centerx, gate["rect"].bottom + 100]
                break

        if _bg_surface:
            screen.blit(_bg_surface, (0, 0))
        else:
            screen.fill(pure_black)

        title = font_big.render(f"{phase_label} - ESCOLHA UMA PORTA", True, pure_white)
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 20)))

        for gate in gates_info:
            draw_gate_icon(screen, gate["name"], gate["rect"], gate["color"], gate.get("done", False))

        player_img = player_animator.get_current_image()
        if player_img:
            screen.blit(player_img, player_rect)

        hint = font_tiny.render("Encoste em uma porta para entrar | ESC para voltar", True, pure_white)
        screen.blit(hint, (50, screen.get_height() - 30))

        pygame.display.flip()
        clock.tick(60)


# ─── FASE 3 ───────────────────────────────────────────────────

def draw_phase3_circuit_scene(surface, inputs, show_ok=False):
    W, H = surface.get_width(), surface.get_height()

    bg = pygame.Surface((W, H))
    bg.fill((10, 10, 12))
    for x in range(0, W, 30):
        pygame.draw.line(bg, (18, 18, 20), (x, 0), (x, H), 1)
    for y in range(0, H, 30):
        pygame.draw.line(bg, (18, 18, 20), (0, y), (W, y), 1)
    surface.blit(bg, (0, 0))

    A, B, C, D = inputs
    and_out = bool(A and B and C)
    not_out = bool(not D)
    final   = bool(and_out or not_out)

    accent      = (0, 180, 220)
    col_not     = (200, 100, 220)
    col_or      = (255, 180, 0)
    body_color  = (232, 232, 232)
    wire_on     = (0, 210, 0)
    wire_off    = (140, 35, 35)

    panel_rect = pygame.Rect(60, 130, W - 120, H - 200)
    pygame.draw.rect(surface, (22, 22, 28), panel_rect, border_radius=18)
    pygame.draw.rect(surface, accent, panel_rect, 4, border_radius=18)

    and_rect = pygame.Rect(280, 180, 180, 210)
    not_rect = pygame.Rect(280, 430, 120, 80)
    or_rect  = pygame.Rect(600, 280, 160, 160)

    btn_x   = 120
    btn_r   = 26
    and_ys  = [and_rect.top + 42, and_rect.centery, and_rect.bottom - 42]
    not_y   = not_rect.centery
    btn_labels = ["A", "B", "C", "D"]
    btn_vals   = [A, B, C, D]
    btn_ys     = and_ys + [not_y]

    for i, (by, val) in enumerate(zip(btn_ys, btn_vals)):
        c = wire_on if val else wire_off
        pygame.draw.circle(surface, c, (btn_x, int(by)), btn_r)
        pygame.draw.circle(surface, (255, 255, 255), (btn_x, int(by)), btn_r, 2)
        lbl = pygame.font.Font(None, 34).render(btn_labels[i], True, (255, 255, 255))
        surface.blit(lbl, lbl.get_rect(center=(btn_x, int(by))))

    # Fios das entradas A B C → AND
    for i, (by, val) in enumerate(zip(and_ys, [A, B, C])):
        c = wire_on if val else wire_off
        pygame.draw.line(surface, c, (btn_x + btn_r, int(by)), (and_rect.left, int(by)), 4)

    # Fio entrada D → NOT
    c_d = wire_on if D else wire_off
    pygame.draw.line(surface, c_d, (btn_x + btn_r, not_y), (not_rect.left, not_y), 4)

    # Corpo AND (3 entradas): rect + semicírculo
    flat_w = and_rect.width // 2
    pygame.draw.rect(surface, body_color,
                     (and_rect.x, and_rect.y + 12, flat_w, and_rect.height - 24))
    arc_r = pygame.Rect(and_rect.x + flat_w // 2, and_rect.y + 12,
                        and_rect.width - flat_w // 2, and_rect.height - 24)
    pygame.draw.ellipse(surface, body_color, arc_r)
    pygame.draw.rect(surface, body_color,
                     (and_rect.x, and_rect.y + 12, flat_w + 6, and_rect.height - 24))
    pygame.draw.rect(surface, accent,
                     (and_rect.x, and_rect.y + 12, flat_w, and_rect.height - 24), 3)
    pygame.draw.arc(surface, accent, arc_r, math.radians(270), math.radians(90), 3)
    pygame.draw.line(surface, accent,
                     (and_rect.x, and_rect.y + 12), (and_rect.x, and_rect.bottom - 12), 3)
    lbl_and = pygame.font.Font(None, 28).render("AND", True, (30, 30, 30))
    surface.blit(lbl_and, lbl_and.get_rect(center=(and_rect.centerx - 10, and_rect.centery)))

    # Corpo NOT: triângulo + bolinha
    pts_not = [
        (not_rect.x, not_rect.y + 8),
        (not_rect.x, not_rect.bottom - 8),
        (not_rect.right - 18, not_rect.centery),
    ]
    pygame.draw.polygon(surface, body_color, pts_not)
    pygame.draw.polygon(surface, col_not, pts_not, 3)
    pygame.draw.circle(surface, body_color, (not_rect.right - 8, not_rect.centery), 9)
    pygame.draw.circle(surface, col_not, (not_rect.right - 8, not_rect.centery), 9, 3)
    lbl_not = pygame.font.Font(None, 24).render("NOT", True, (30, 30, 30))
    surface.blit(lbl_not, lbl_not.get_rect(center=(not_rect.centerx - 6, not_rect.centery)))

    # Fio AND → OR (em L)
    c_and = wire_on if and_out else wire_off
    and_out_x = and_rect.right + 2
    and_mid_y = and_rect.centery
    or_in1_y  = or_rect.top + or_rect.height // 3
    junc_x    = and_rect.right + 50
    pygame.draw.line(surface, c_and, (and_out_x, and_mid_y), (junc_x, and_mid_y), 4)
    pygame.draw.line(surface, c_and, (junc_x, and_mid_y), (junc_x, or_in1_y), 4)
    pygame.draw.line(surface, c_and, (junc_x, or_in1_y), (or_rect.left, or_in1_y), 4)

    # Fio NOT → OR (em L)
    c_not = wire_on if not_out else wire_off
    not_out_x = not_rect.right + 8 + 9
    junc2_x   = not_rect.right + 60
    or_in2_y  = or_rect.top + 2 * or_rect.height // 3
    pygame.draw.line(surface, c_not, (not_out_x, not_y), (junc2_x, not_y), 4)
    pygame.draw.line(surface, c_not, (junc2_x, not_y), (junc2_x, or_in2_y), 4)
    pygame.draw.line(surface, c_not, (junc2_x, or_in2_y), (or_rect.left, or_in2_y), 4)

    # Corpo OR: polígono em forma de OR gate
    or_pts = [
        (or_rect.x + 14,            or_rect.y + 10),
        (or_rect.centerx - 12,      or_rect.y + 18),
        (or_rect.right - 18,        or_rect.centery),
        (or_rect.centerx - 12,      or_rect.bottom - 18),
        (or_rect.x + 14,            or_rect.bottom - 10),
        (or_rect.x + 40,            or_rect.centery),
    ]
    pygame.draw.polygon(surface, body_color, or_pts)
    pygame.draw.polygon(surface, col_or, or_pts, 3)
    lbl_or = pygame.font.Font(None, 28).render("OR", True, (30, 30, 30))
    surface.blit(lbl_or, lbl_or.get_rect(center=(or_rect.centerx, or_rect.centery)))

    # Fio saída OR → lâmpada
    lamp_cx = or_rect.right + 100
    lamp_cy = or_rect.centery
    c_out   = wire_on if final else wire_off
    pygame.draw.line(surface, c_out, (or_rect.right, lamp_cy), (lamp_cx - 28, lamp_cy), 5)

    # Lâmpada
    pulse = (math.sin(pygame.time.get_ticks() / 130.0) + 1.0) / 2.0 if show_ok else 0.0
    if final:
        glow = pygame.Surface((100, 100), pygame.SRCALPHA)
        ga = 55 + int(65 * pulse)
        gr = 28 + int(8 * pulse)
        pygame.draw.circle(glow, (255, 220, 70, ga), (50, 50), gr)
        surface.blit(glow, (lamp_cx - 50, lamp_cy - 50))
    lamp_color = (255, 220, 70) if final else (70, 70, 70)
    if show_ok and final:
        lamp_color = (255, 235, 110) if pulse > 0.5 else (255, 200, 50)
    pygame.draw.circle(surface, lamp_color, (lamp_cx, lamp_cy), 26)
    pygame.draw.circle(surface, (255, 255, 255), (lamp_cx, lamp_cy), 26, 3)
    base = pygame.Rect(lamp_cx - 14, lamp_cy + 22, 28, 18)
    pygame.draw.rect(surface, (110, 110, 110), base)
    pygame.draw.rect(surface, (255, 255, 255), base, 2)

    saida_lbl = pygame.font.Font(None, 28).render("SAÍDA", True, (255, 255, 255))
    surface.blit(saida_lbl, saida_lbl.get_rect(center=(lamp_cx, lamp_cy + 56)))

    if show_ok and final:
        ok_font = pygame.font.Font(None, 30)
        ok_text = ok_font.render("OK", True, (0, 210, 0))
        ok_bg   = pygame.Rect(lamp_cx - 28, lamp_cy - 66, 56, 26)
        pygame.draw.rect(surface, (255, 255, 255), ok_bg, border_radius=8)
        surface.blit(ok_text, ok_text.get_rect(center=ok_bg.center))

    hint = pygame.font.Font(None, 26).render(
        "Clique nas entradas A/B/C/D para alternar  |  ENTER/ESC para voltar",
        True, (60, 60, 70)
    )
    surface.blit(hint, hint.get_rect(center=(W // 2, H - 30)))

    return final


def show_phase3_circuit(screen, clock):
    font_big   = pygame.font.Font(None, 56)
    font_small = pygame.font.Font(None, 30)

    pure_black = (0, 0, 0)
    pure_white = (255, 255, 255)
    accent     = (0, 180, 220)

    inputs   = [0, 0, 0, 0]
    btn_r    = 26
    and_ys   = [222, 285, 348]
    not_y    = 470
    btn_x    = 120
    btn_ys   = and_ys + [not_y]

    interacted = False
    running    = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for i, by in enumerate(btn_ys):
                    r = pygame.Rect(btn_x - btn_r, int(by) - btn_r, btn_r * 2, btn_r * 2)
                    if r.collidepoint(mx, my):
                        inputs[i] = 1 - inputs[i]
                        interacted = True

        A, B, C, D = inputs
        final = bool((A and B and C) or (not D))
        solved = interacted and final

        screen.fill(pure_black)

        title = font_big.render("FASE 3 — CIRCUITO COMBINADO", True, accent)
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 52)))
        desc = font_small.render(
            "Saída = AND(A, B, C)  OR  NOT(D)",
            True, pure_white
        )
        screen.blit(desc, desc.get_rect(center=(screen.get_width() // 2, 96)))

        draw_phase3_circuit_scene(screen, inputs, solved)

        eq = (
            f"AND({A},{B},{C}) = {int(bool(A and B and C))}    "
            f"NOT({D}) = {int(bool(not D))}    "
            f"OR = {int(final)}"
        )
        eq_surf = font_small.render(eq, True, accent)
        screen.blit(eq_surf, eq_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() - 68)))

        if solved:
            ok_font = pygame.font.Font(None, 50)
            ok_text = ok_font.render("✓  CIRCUITO LIGADO!", True, (0, 220, 80))
            ok_bg   = pygame.Rect(screen.get_width() // 2 - 210, screen.get_height() - 50, 420, 44)
            pygame.draw.rect(screen, (0, 0, 0), ok_bg, border_radius=10)
            pygame.draw.rect(screen, (0, 220, 80), ok_bg, 3, border_radius=10)
            screen.blit(ok_text, ok_text.get_rect(center=ok_bg.center))

        pygame.display.flip()
        clock.tick(60)

    return bool(interacted and (A and B and C or not D))


def draw_circuit_gate_icon(surface, rect, color, done=False):
    panel = (26, 26, 32)
    frame = tuple(min(255, c + 40) for c in color) if done else color
    wc    = (190, 190, 190)
    lamp_on  = (255, 220, 70)
    lamp_off = (80, 80, 80)

    pygame.draw.rect(surface, panel, rect, border_radius=18)
    pygame.draw.rect(surface, frame, rect, 4, border_radius=18)

    font = pygame.font.Font(None, 22)
    title = font.render("CIRCUITO", True, (255, 255, 255))
    surface.blit(title, title.get_rect(center=(rect.centerx, rect.top + 22)))

    and_r = pygame.Rect(rect.x + 22, rect.y + 48, 72, 82)
    pygame.draw.rect(surface, (50, 50, 60), and_r, border_radius=6)
    pygame.draw.rect(surface, (0, 160, 200), and_r, 2, border_radius=6)
    surface.blit(font.render("AND", True, (200, 220, 255)), font.render("AND", True, (200, 220, 255)).get_rect(center=and_r.center))

    not_r = pygame.Rect(rect.x + 22, rect.y + 148, 72, 46)
    pygame.draw.rect(surface, (50, 50, 60), not_r, border_radius=6)
    pygame.draw.rect(surface, (200, 100, 220), not_r, 2, border_radius=6)
    surface.blit(font.render("NOT", True, (220, 180, 255)), font.render("NOT", True, (220, 180, 255)).get_rect(center=not_r.center))

    or_cx = rect.x + 196
    or_cy = rect.centery + 8
    pygame.draw.line(surface, wc, (and_r.right, and_r.centery), (or_cx - 20, and_r.centery), 2)
    pygame.draw.line(surface, wc, (or_cx - 20, and_r.centery), (or_cx - 20, or_cy - 16), 2)
    pygame.draw.line(surface, wc, (or_cx - 20, or_cy - 16), (or_cx, or_cy - 16), 2)
    pygame.draw.line(surface, wc, (not_r.right, not_r.centery), (or_cx - 20, not_r.centery), 2)
    pygame.draw.line(surface, wc, (or_cx - 20, not_r.centery), (or_cx - 20, or_cy + 16), 2)
    pygame.draw.line(surface, wc, (or_cx - 20, or_cy + 16), (or_cx, or_cy + 16), 2)

    or_r = pygame.Rect(or_cx, or_cy - 28, 60, 56)
    pygame.draw.rect(surface, (50, 50, 60), or_r, border_radius=6)
    pygame.draw.rect(surface, (255, 170, 0), or_r, 2, border_radius=6)
    surface.blit(font.render("OR", True, (255, 220, 150)), font.render("OR", True, (255, 220, 150)).get_rect(center=or_r.center))

    lx = or_r.right + 20
    ly = or_cy
    pygame.draw.line(surface, wc, (or_r.right, or_cy), (lx - 8, ly), 2)
    pygame.draw.circle(surface, lamp_on if done else lamp_off, (lx, ly), 10)
    pygame.draw.circle(surface, (255, 255, 255), (lx, ly), 10, 1)
    if done:
        glow = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 220, 70, 70), (20, 20), 12)
        surface.blit(glow, (lx - 20, ly - 20))

    if done:
        ok_font = pygame.font.Font(None, 22)
        ok_text = ok_font.render("OK", True, (0, 200, 0))
        ok_bg = pygame.Rect(rect.right - 52, rect.top + 12, 38, 22)
        pygame.draw.rect(surface, (255, 255, 255), ok_bg, border_radius=5)
        surface.blit(ok_text, ok_text.get_rect(center=ok_bg.center))


def show_portal_phase3(screen, clock, player_animator, player_pos):
    font_big  = pygame.font.Font(None, 58)
    font_tiny = pygame.font.Font(None, 20)

    pure_black = (0, 0, 0)
    pure_white = (255, 255, 255)

    # Carrega o fundo cyberpunk da fase 3 (nucleo final)
    _bg_path = os.path.join(BASE_DIR, "images", "background_fase3.png")
    _bg_surface = None
    if os.path.exists(_bg_path):
        _bg_surface = pygame.image.load(_bg_path).convert()

    gate = {"rect": pygame.Rect(350, 120, 300, 280), "color": (0, 180, 220), "done": False}
    player_speed = 4

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False, player_pos

        if gate["done"]:
            return True, player_pos

        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += player_speed
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy -= player_speed
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy += player_speed

        player_animator.update(dx, dy)
        player_pos = [
            max(50, min(screen.get_width()  - 50, player_pos[0] + dx)),
            max(50, min(screen.get_height() - 100, player_pos[1] + dy)),
        ]
        player_rect = player_animator.get_rect(player_pos)

        trigger = pygame.Rect(
            gate["rect"].x + 8,
            gate["rect"].y,
            gate["rect"].width - 16,
            max(36, gate["rect"].height // 5),
        )
        if player_rect.colliderect(trigger) and not gate["done"]:
            solved = show_phase3_circuit(screen, clock)
            if solved:
                gate["done"] = True
            player_pos = [gate["rect"].centerx, gate["rect"].bottom + 100]

        if _bg_surface:
            screen.blit(_bg_surface, (0, 0))
        else:
            screen.fill(pure_black)

        title = font_big.render("FASE 3 — CIRCUITO FINAL", True, (0, 200, 220))
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 22)))

        draw_circuit_gate_icon(screen, gate["rect"], gate["color"], gate["done"])

        player_img = player_animator.get_current_image()
        if player_img:
            screen.blit(player_img, player_rect)

        hint = font_tiny.render(
            "Encoste no circuito para resolver  |  ESC para voltar",
            True, pure_white
        )
        screen.blit(hint, (50, screen.get_height() - 28))

        pygame.display.flip()
        clock.tick(60)


def run_game(screen, clock):
    # Cena minimalista: apenas preto e branco piscando + dialogos.
    pure_black = (0, 0, 0)
    pure_white = (255, 255, 255)
    soft_white = (241, 242, 243)  # #f1f2f3
    soft_black = (33, 33, 33)     # #212121

    bubble_color = pure_white
    bubble_border = pure_black
    text_color = pure_black
    small_font = pygame.font.Font(None, 28)

    # Inicializa o animador do personagem
    player_animator = PlayerAnimator()
    player_pos      = [120, 460]
    player_speed    = 4
    phase_1_door    = pygame.Rect(60, screen.get_height() - 180, 120, 150)

    in_game = True
    while in_game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                in_game = False

        instruction_visible = True

        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += player_speed

        # Balao de instrucoes no canto superior direito.
        instruction_rect = pygame.Rect(screen.get_width() - 360, 20, 340, 90)

        # Move em dois eixos para tratar colisao com o balao.
        next_pos = [player_pos[0] + dx, player_pos[1] + dy]
        
        # Cria rect temporário para verificar colisões
        player_animator.update(dx, dy)
        player_rect = player_animator.get_rect(next_pos)
        
        if instruction_visible and player_rect.colliderect(instruction_rect):
            next_pos[0] = player_pos[0]
            player_rect = player_animator.get_rect(next_pos)
        
        if instruction_visible and player_rect.colliderect(instruction_rect):
            next_pos[1] = player_pos[1]
            player_rect = player_animator.get_rect(next_pos)

        # Limita os limites da tela
        next_pos[0] = max(20, min(screen.get_width() - 40, next_pos[0]))
        next_pos[1] = max(20, min(screen.get_height() - 52, next_pos[1]))
        player_pos = next_pos

        screen.fill(pure_black)

        # Desenha o personagem animado
        player_img = player_animator.get_current_image()
        if player_img:
            player_rect = player_animator.get_rect(player_pos)
            screen.blit(player_img, player_rect)

        if instruction_visible:
            pygame.draw.rect(screen, bubble_color, instruction_rect, border_radius=14)
            pygame.draw.rect(screen, bubble_border, instruction_rect, 2, border_radius=14)
            line_1 = small_font.render("Movimento:", True, text_color)
            line_2 = small_font.render("WASD / Setas", True, text_color)
            line_3 = small_font.render("ESC para voltar", True, text_color)
            screen.blit(line_1, (instruction_rect.x + 18, instruction_rect.y + 14))
            screen.blit(line_2, (instruction_rect.x + 18, instruction_rect.y + 40))
            screen.blit(line_3, (instruction_rect.x + 18, instruction_rect.y + 64))

            # Porta da Fase 1
            pygame.draw.rect(screen, pure_white, phase_1_door, border_radius=8)
            pygame.draw.rect(screen, pure_black, phase_1_door, 3, border_radius=8)
            door_label = small_font.render("PORTA", True, pure_black)
            phase_label = small_font.render("FASE 1", True, pure_black)
            screen.blit(door_label, door_label.get_rect(center=(phase_1_door.centerx, phase_1_door.y + 45)))
            screen.blit(phase_label, phase_label.get_rect(center=(phase_1_door.centerx, phase_1_door.y + 80)))

            # Ao chegar na porta, vai para o mapa com 3 portas
            if player_rect.colliderect(phase_1_door):
                show_portal_map(screen, clock)
                return

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main_menu()
