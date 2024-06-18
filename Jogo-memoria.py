# Jogo da Memória - Imagem e Texto
# Autor: Sebastião Tadeu de Oliveira Almeida
# Email: almeida_sto@ufrrj.br
# version 1.0
# Licença: Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)
# Você é livre para compartilhar e adaptar este material, desde que atribua o devido crédito ao autor e não use o material para fins comerciais.
# Para ver uma cópia desta licença, visite http://creativecommons.org/licenses/by-nc/4.0/

import pygame
import random
import time
import os
import sys
from pygame.locals import *

# Inicializar Pygame
pygame.init()
pygame.mixer.init()  # Inicializar o mixer para tocar música

# Configurações da janela do jogo
screen_width = 1200
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Jogo da Memória - Imagem e texto")

# Cores
white = (255, 255, 255)
black = (0, 0, 0)
gray = (200, 200, 200)
blue = (0, 0, 255)
red = (255, 0, 0)
green = (0, 255, 0)

# Fontes
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)
number_font = pygame.font.Font(None, 48)

# Função para carregar as imagens e nomes do arquivo
def load_cards(filename):
    images = []
    names = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                image, name = line.strip().split(',')
                images.append(image)
                names.append(name)
    except FileNotFoundError:
        print(f"Arquivo {filename} não encontrado.")
        pygame.quit()
        exit()
    return images, names

# Carregar as imagens e nomes do arquivo
images, names = load_cards('cards.txt')
cards = images + names
random.shuffle(cards)

#Adicionar numeração às cartas
card_numbers=list(range(1,len(cards)+1))

# Dimensões das cartas
card_width = 175
card_height = 200
margin = 20
y_offset = 100  # Deslocamento vertical para abaixar as cartas

# Estados do jogo
first_card = None
second_card = None
first_card_index = None
second_card_index = None
matches = 0
attempts = 0
card_rects = []
revealed_cards = [False] * len(cards)  # Estado de revelação das cartas
current_team = 1  # Equipe 1 começa
scores = [0, 0]  # Pontuação das equipes

# Carregar e redimensionar imagens
card_images = {}
for img in images:
    if os.path.exists(img):
        image = pygame.image.load(img)
        image = pygame.transform.scale(image, (card_width, card_height))
        card_images[img] = image
    else:
        print(f"Imagem {img} não encontrada.")
        pygame.quit()
        exit()

# Carregar imagem de fundo
background_image = 'fundo.png'  # Substitua pelo nome do seu arquivo de imagem de fundo
if os.path.exists(background_image):
    background = pygame.image.load(background_image)
    background = pygame.transform.scale(background, (screen_width, screen_height))
else:
    print(f"Imagem de fundo {background_image} não encontrada.")
    pygame.quit()
    exit()

# Carregar música de fundo
music_file = 'musica_fundo.mp3'  # Substitua pelo nome do seu arquivo de música
if os.path.exists(music_file):
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.play(-1)  # Tocar em loop
else:
    print(f"Arquivo de música {music_file} não encontrado.")
    pygame.quit()
    exit()

# Função para ajustar a fonte para caber no retângulo
def fit_text_to_rect(text_lines, font, max_width, max_height):
    while True:
        text_surface = [font.render(line, True, black) for line in text_lines]
        text_widths = [surface.get_width() for surface in text_surface]
        text_heights = [surface.get_height() for surface in text_surface]

        if max(text_widths) <= max_width and sum(text_heights) <= max_height:
            break
        font = pygame.font.Font(None, font.get_height() - 2)
    return font

# Função para quebrar o texto em múltiplas linhas e ajustar a fonte
def wrap_and_fit_text(text, font, rect_width, rect_height):
    wrapped_text = wrap_text(text, font, rect_width)
    fitted_font = fit_text_to_rect(wrapped_text, font, rect_width, rect_height)
    return wrapped_text, fitted_font

# Função para desenhar as cartas
def draw_cards():
    screen.blit(background, (0, 0))  # Desenhar a imagem de fundo
    card_rects.clear()  # Limpar lista de retângulos de cartas
    for i, card in enumerate(cards):
        x = (i % 6) * (card_width + margin) + margin
        y = (i // 6) * (card_height + margin) + margin + y_offset
        rect = pygame.Rect(x, y, card_width, card_height)
        card_rects.append(rect)
        if revealed_cards[i] or i == first_card_index or i == second_card_index:
            if card in card_images:
                screen.blit(card_images[card], rect)
            else:
                # Quebrar o texto e ajustar a fonte para caber no retângulo
                wrapped_text, fitted_font = wrap_and_fit_text(card, number_font, rect.width, rect.height)
                total_height = len(wrapped_text) * fitted_font.get_height()
                for j, line in enumerate(wrapped_text):
                    text = fitted_font.render(line, True, black)
                    screen.blit(text, (rect.x + (rect.width - text.get_width()) // 2, rect.y + (rect.height - total_height) // 2 + j * fitted_font.get_height()))
        else:
            pygame.draw.rect(screen, gray, rect)
        pygame.draw.rect(screen, black, rect, 2)

        # Desenhar o número da carta
        number_text = font.render(str(card_numbers[i]), True, black)
        screen.blit(number_text, (rect.x + 5, rect.y + 5))

    # Mostrar qual equipe deve jogar
    team_text = font.render(f"Equipe {current_team} deve jogar", True, blue if current_team == 1 else red)
    screen.blit(team_text, (screen_width // 2 - team_text.get_width() // 2, 10))
    pygame.display.flip()

# Função para quebrar o texto em várias linhas
def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = []
    current_width = 0

    for word in words:
        word_width, _ = font.size(word + ' ')
        if current_width + word_width <= max_width:
            current_line.append(word)
            current_width += word_width
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_width = word_width

    lines.append(' '.join(current_line))
    return lines


# Função para exibir a mensagem de informações
def show_info_message():
    info_message = [
        "O \"Jogo da Memória - Imagem e Texto\" é uma ferramenta educativa interativa desenvolvida",
        "em Python usando a biblioteca Pygame. O jogo foi projetado para ser utilizado por professores",
        "em sala de aula, visando facilitar o aprendizado de diversos conceitos em diferentes",
        "disciplinas através de um método interativo e lúdico.",
        "Autor: Sebastião Tadeu de Oliveira Almeida",
        "Email: almeida_sto@ufrrj.br"
    ]
    
    info_screen = pygame.Surface((screen_width, screen_height))
    info_screen.fill(white)
    
    for i, line in enumerate(info_message):
        text = font.render(line, True, black)
        info_screen.blit(text, (50, 150 + i * 50))
    
    ok_button = pygame.Rect(screen_width // 2 - 50, screen_height - 150, 100, 50)
    pygame.draw.rect(info_screen, green, ok_button)
    ok_text = font.render("OK", True, black)
    info_screen.blit(ok_text, (ok_button.x + (ok_button.width - ok_text.get_width()) // 2, ok_button.y + (ok_button.height - ok_text.get_height()) // 2))
    
    screen.blit(info_screen, (0, 0))
    pygame.display.flip()
    
    waiting_for_ok = True
    while waiting_for_ok:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos
                if ok_button.collidepoint(mouse_x, mouse_y):
                    waiting_for_ok = False

# Tela inicial com as regras
def show_start_screen():
    screen.blit(background, (0, 0))  # Desenhar a imagem de fundo
    title = large_font.render("Jogo da Memória - Imagem e Texto", True, black)
    screen.blit(title, (screen_width // 2 - title.get_width() // 2, 100))

    rules = [
        "Regras do Jogo:",
        "1. O jogo é para duas equipes.",
        "2. Enquanto uma equipe acertar, ela continua jogando.",
        "3. Se errar, passa a vez para a outra equipe.",
        "4. Ganha quem encontrar mais pares de cartas.",
        "Clique no botão para começar o jogo!"
    ]

    for i, rule in enumerate(rules):
        text = font.render(rule, True, black)
        screen.blit(text, (50, 200 + i * 50))

    start_button = pygame.Rect(screen_width // 2 - 100, screen_height - 150, 200, 50)
    pygame.draw.rect(screen, green, start_button)
    start_text = font.render("Começar", True, black)
    screen.blit(start_text, (start_button.x + (start_button.width - start_text.get_width()) // 2, start_button.y + (start_button.height - start_text.get_height()) // 2))

    info_button = pygame.Rect(screen_width // 2 - 100, screen_height - 100, 200, 50)
    pygame.draw.rect(screen, blue, info_button)
    info_text = font.render("Informações", True, black)
    screen.blit(info_text, (info_button.x + (info_button.width - info_text.get_width()) // 2, info_button.y + (info_button.height - info_text.get_height()) // 2))

    pygame.display.flip()
    return start_button, info_button

# Tela de fim de jogo com resultados
def show_end_screen():
    screen.blit(background, (0, 0))  # Desenhar a imagem de fundo
    title = large_font.render("Fim de Jogo", True, black)
    screen.blit(title, (screen_width // 2 - title.get_width() // 2, 100))

    result_text = font.render(f"Equipe 1: {scores[0]} pontos | Equipe 2: {scores[1]} pontos", True, black)
    screen.blit(result_text, (screen_width // 2 - result_text.get_width() // 2, 300))

    if scores[0] > scores[1]:
        winner_text = font.render("Equipe 1 Venceu!", True, blue)
    elif scores[1] > scores[0]:
        winner_text = font.render("Equipe 2 Venceu!", True, red)
    else:
        winner_text = font.render("Empate!", True, black)

    attempts_text = font.render(f"Número total de tentativas: {attempts}", True, black)
    screen.blit(attempts_text, (screen_width // 2 - attempts_text.get_width() // 2, 500))

    play_again_button = pygame.Rect(screen_width // 2 - 150, screen_height - 200, 300, 50)
    quit_button = pygame.Rect(screen_width // 2 - 150, screen_height - 120, 300, 50)

    pygame.draw.rect(screen, green, play_again_button)
    play_again_text = font.render("Jogar Novamente", True, black)
    screen.blit(play_again_text, (play_again_button.x + (play_again_button.width - play_again_text.get_width()) // 2, play_again_button.y + (play_again_button.height - play_again_text.get_height()) // 2))

    pygame.draw.rect(screen, red, quit_button)
    quit_text = font.render("Sair", True, black)
    screen.blit(quit_text, (quit_button.x + (quit_button.width - quit_text.get_width()) // 2, quit_button.y + (quit_button.height - quit_text.get_height()) // 2))

    pygame.display.flip()
    return play_again_button, quit_button

# Função principal do jogo
def main():
    global first_card, second_card, first_card_index, second_card_index, matches, attempts, current_team, scores, revealed_cards, cards
    running = True
    game_active = False
    play_again_button = None
    quit_button = None
    start_button, info_button = show_start_screen()

    while running:
        if game_active:
            draw_cards()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos

                if not game_active:
                    if start_button.collidepoint(mouse_x, mouse_y):
                        game_active = True
                        cards = images + names
                        random.shuffle(cards)
                        revealed_cards = [False] * len(cards)
                        first_card = None
                        second_card = None
                        first_card_index = None
                        second_card_index = None
                        matches = 0
                        attempts = 0
                        current_team = 1
                        scores = [0, 0]
                    elif info_button.collidepoint(mouse_x, mouse_y):
                        show_info_message()
                        start_button, info_button = show_start_screen()

                if game_active:
                    for i, rect in enumerate(card_rects):
                        if rect.collidepoint(mouse_x, mouse_y) and not revealed_cards[i]:
                            if first_card is None:
                                first_card = cards[i]
                                first_card_index = i
                                draw_cards()  # Desenhar cartas para mostrar a primeira carta virada
                            elif second_card is None and i != first_card_index:
                                second_card = cards[i]
                                second_card_index = i
                                attempts += 1
                                draw_cards()
                                pygame.time.wait(2000)
                                if (first_card in images and second_card == names[images.index(first_card)]) or (second_card in images and first_card == names[images.index(second_card)]):
                                    matches += 1
                                    revealed_cards[first_card_index] = True
                                    revealed_cards[second_card_index] = True
                                    scores[current_team - 1] += 1
                                else:
                                    current_team = 3 - current_team  # Alternar equipe
                                first_card = None
                                second_card = None
                                first_card_index = None
                                second_card_index = None

                if matches == len(cards) // 2:
                    game_active = False
                    play_again_button, quit_button = show_end_screen()

                if not game_active and play_again_button is not None and play_again_button.collidepoint(mouse_x, mouse_y):
                    game_active = True
                    cards = images + names
                    random.shuffle(cards)
                    revealed_cards = [False] * len(cards)
                    first_card = None
                    second_card = None
                    first_card_index = None
                    second_card_index = None
                    matches = 0
                    attempts = 0
                    current_team = 1
                    scores = [0, 0]
                elif not game_active and quit_button is not None and quit_button.collidepoint(mouse_x, mouse_y):
                    running = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
