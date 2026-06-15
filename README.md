# Tux Escape: A Revolta dos Circuitos

Jogo educacional para ensinar portas lógicas usando Pygame.

## Tema
O pinguim Tux precisa escapar de um antivírus ativando portas lógicas e montando circuitos.

## Objetivo Educacional
Ensinar portas lógicas: AND, OR, NOT, XOR, NAND, NOR através de jogos interativos.

## Arquivos
- `main.py`: Menu, mapa hub (estilo top-down) e fases.
- `logic_gates.py`: Classes para portas lógicas (AND, OR, NOT, etc.).

## Fluxo do jogo
1. Tela inicial
2. Mapa hub com o pinguim (Tux)
3. O jogador anda ate os portais das fases e aperta `E` para entrar
4. Completa a fase e volta ao mapa

## Controles
- `WASD` ou setas: movimentar o Tux no mapa
- `E`: entrar no portal da fase
- `ESC`: sair da fase e voltar ao mapa
- `ENTER`: confirmar conclusao da fase (quando a resposta estiver correta)

## Fases Implementadas
1. Descobrindo entradas (0 e 1) - Botão A e lâmpada.
2. Porta AND - Botões A e B, porta AND visual, lâmpada conectada.
3. Escolhendo a Porta - Seleção entre AND, OR e NOT para cumprir a regra da fase.

## Como executar
1. Instalar Python e Pygame
2. Rodar: `python3 main.py`

## Equipe
- Gabriela: Programação
- Yago: Interface gráfica
- Laisa: Exercícios
- Eduarda: Testes