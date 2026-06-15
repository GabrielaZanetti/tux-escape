import pygame
import sys
import os
import math

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
        fallback_path = os.path.join(BASE_DIR, "tux.png")
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
    path_png = os.path.join(BASE_DIR, "intro.png")
    try:
        if os.path.exists(path_png):
            img = pygame.image.load(path_png)
            return img.convert_alpha()
    except Exception:
        pass

    return None


def main_menu():
    pygame.init()
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 700
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tux Escape - Menu")

    DARK_BG = (18, 18, 26)
    WHITE = (255, 255, 255)
    SOFT_WHITE = (240, 240, 240)
    RED = (220, 30, 30)
    GREEN = (30, 180, 60)
    BLACK = (0, 0, 0)

    font_large = pygame.font.Font(None, 64)
    font = pygame.font.Font(None, 36)
    small = pygame.font.Font(None, 24)

    intro_surface = load_intro_surface()

    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill(DARK_BG)

        mouse_pos = pygame.mouse.get_pos()

        # Top margin and available sizes
        top_margin = 40
        max_img_w = int(SCREEN_WIDTH * 0.75)
        max_img_h = 300
        current_y = top_margin

        # Intro image / placeholder
        if intro_surface:
            iw, ih = intro_surface.get_size()
            scale = min(max_img_w / iw, max_img_h / ih, 1)
            new_w = int(iw * scale)
            new_h = int(ih * scale)
            img = pygame.transform.smoothscale(intro_surface, (new_w, new_h))
            img_rect = img.get_rect(center=(SCREEN_WIDTH // 2, current_y + new_h // 2))
            screen.blit(img, img_rect)
            current_y += new_h + 20
        else:
            ph_w = max_img_w
            ph_h = 200
            ph_rect = pygame.Rect((SCREEN_WIDTH - ph_w) // 2, current_y, ph_w, ph_h)
            pygame.draw.rect(screen, (60, 60, 70), ph_rect, border_radius=8)
            txt_ph = small.render("(intro.png não encontrado)", True, SOFT_WHITE)
            screen.blit(txt_ph, txt_ph.get_rect(center=ph_rect.center))
            current_y += ph_h + 20

        # Texto vermelho centralizado
        red_text = font_large.render("INICIAR O JOGO", True, RED)
        red_rect = red_text.get_rect(center=(SCREEN_WIDTH // 2, current_y + 24))
        screen.blit(red_text, red_rect)
        current_y += 80

        # Botão verde estilo 'tec'
        btn_w = 260
        btn_h = 72
        btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - btn_w // 2, current_y, btn_w, btn_h)
        hover = btn_rect.collidepoint(mouse_pos)
        base = GREEN
        color = tuple(min(255, c + 30) for c in base) if hover else base
        pygame.draw.rect(screen, color, btn_rect, border_radius=12)
        pygame.draw.rect(screen, BLACK, btn_rect, 3, border_radius=12)
        label = font.render("Iniciar", True, BLACK)
        screen.blit(label, label.get_rect(center=btn_rect.center))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_rect.collidepoint(event.pos):
                    show_portal_map(screen, clock)
                    running = False

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


def show_portal_map(screen, clock):
    player_animator = PlayerAnimator()
    player_pos = [500, 600]

    completed, player_pos = show_portal_phase(
        screen,
        clock,
        "FASE 1",
        build_portal_gates(1),
        player_animator,
        player_pos,
    )
    if not completed:
        return

    animate_phase_transition(screen, clock, player_animator, player_pos, "FASE 1", "FASE 2")

    player_animator = PlayerAnimator()
    player_pos = [120, 600]

    completed, player_pos = show_portal_phase(
        screen,
        clock,
        "FASE 2",
        build_portal_gates(2),
        player_animator,
        player_pos,
    )
    if not completed:
        return


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
            "A porta NAND libera saida 0 somente quando as duas entradas estao em 1.",
        ),
    }

    input1 = 0
    input2 = 0
    interacted = False
    completed = False

    # Botões de entrada (empilhados)
    btn_input1 = pygame.Rect(120, 215, 54, 54)
    btn_input2 = pygame.Rect(120, 335, 54, 54)

    # Lâmpada
    lamp_rect = pygame.Rect(820, 260, 44, 80)

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


def show_portal_phase(screen, clock, phase_label, gates_info, player_animator, player_pos):
    font_big = pygame.font.Font(None, 64)
    font_small = pygame.font.Font(None, 32)
    font_tiny = pygame.font.Font(None, 20)

    pure_black = (0, 0, 0)
    pure_white = (255, 255, 255)

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
    player_pos = [120, 460]
    player_speed = 4
    phase_1_door = pygame.Rect(60, screen.get_height() - 180, 120, 150)

    dialog_duration_ms = 3000
    first_start = 0
    first_end = first_start + dialog_duration_ms
    second_start = first_end
    second_end = second_start + dialog_duration_ms

    # Pisca de forma suave entre #f1f2f3 e #212121.
    blink_period_ms = 2200
    start_ticks = pygame.time.get_ticks()

    in_game = True
    while in_game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                in_game = False

        elapsed = pygame.time.get_ticks() - start_ticks
        dialog_phase = elapsed < second_end
        instruction_visible = elapsed >= second_end

        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        # Enquanto os dialogos aparecem, personagem nao anda.
        if not dialog_phase:
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

        if dialog_phase:
            phase = (elapsed % blink_period_ms) / blink_period_ms
            wave = (math.sin(phase * 2 * math.pi) + 1.0) / 2.0
            bg = (
                int(soft_black[0] + (soft_white[0] - soft_black[0]) * wave),
                int(soft_black[1] + (soft_white[1] - soft_black[1]) * wave),
                int(soft_black[2] + (soft_white[2] - soft_black[2]) * wave),
            )
            fg = pure_black if wave > 0.5 else pure_white
        else:
            # Ao finalizar os dialogos, fundo fica preto total.
            bg = pure_black
            fg = pure_white

        screen.fill(bg)

        # Desenha o personagem animado
        player_img = player_animator.get_current_image()
        if player_img:
            player_rect = player_animator.get_rect(player_pos)
            screen.blit(player_img, player_rect)

        if first_start <= elapsed < first_end:
            bubble_1 = pygame.Rect(screen.get_width() - 560, 20, 540, 90)
            pygame.draw.rect(screen, bubble_color, bubble_1, border_radius=14)
            pygame.draw.rect(screen, bubble_border, bubble_1, 2, border_radius=14)
            txt_1 = small_font.render("O virus atacou o sistema e desligou as lizes", True, text_color)
            screen.blit(txt_1, txt_1.get_rect(center=bubble_1.center))

        elif second_start <= elapsed < second_end:
            bubble_2 = pygame.Rect(screen.get_width() - 560, 20, 540, 90)
            pygame.draw.rect(screen, bubble_color, bubble_2, border_radius=14)
            pygame.draw.rect(screen, bubble_border, bubble_2, 2, border_radius=14)
            txt_2 = small_font.render("Ajuste as missoes para fugir", True, text_color)
            screen.blit(txt_2, txt_2.get_rect(center=bubble_2.center))

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
