# -*- coding: utf-8 -*-
import pygame, sys, random, time, math, os
from pygame.locals import *
from game import mapa
import numpy as np

# Configuración
NUM_ITERATIONS = 500  # Número de iteraciones a ejecutar
TIME_LIMIT = 15  # Límite de tiempo por iteración (en segundos)
RENDER = True  # Establecer en False para desactivar visuales
USE_SAVED_WEIGHTS = True  # Establecer en True para cargar la tabla Q guardada, False para empezar de nuevo
SAVE_WEIGHTS = True  # Establecer en True para guardar la tabla Q después del entrenamiento
MIN_SPAWN_DISTANCE = 200  # Distancia mínima entre Tom y Jerry al aparecer

pygame.mixer.pre_init(44100, 16, 2, 1024)
pygame.init()

# Inicializar un modo de video mínimo incluso si el renderizado está desactivado
if not RENDER:
    pygame.display.set_mode((1, 1), pygame.NOFRAME)  # Modo de video mínimo

BLANCO = (255, 255, 255)
AMARILLO = (255, 255, 0)

tipoLetra = pygame.font.Font('Grandezza.ttf', 30)
tipoLetra2 = pygame.font.Font('Grandezza.ttf', 35)

imagenDeFondo = 'images/Noticia_TomJerry.jpg'
imagenGatoContento = 'images/gato.png'
imagenRatonContento = 'images/raton1.png'
imagenQueso = 'images/q.png'

if RENDER:
    visor = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Ejemplo de Mapa')

def pausa():
    esperar = True
    while esperar:
        for evento in pygame.event.get():
            if evento.type == KEYDOWN:
                esperar = False

def mostrarIntro():
    if RENDER:
        fondo = pygame.image.load(imagenDeFondo).convert()
        visor.blit(fondo, (0, 0))
        mensaje = 'Pulsa una tecla para comenzar'
        texto = tipoLetra.render(mensaje, True, AMARILLO)
        visor.blit(texto, (60, 550, 350, 30))
        pygame.display.update()
        pausa()

if RENDER:
    pygame.mouse.set_visible(False)
    mostrarIntro()
    time.sleep(0.75)

def is_position_valid(nivel, x, y):
    # Crear un sprite temporal para verificar colisiones
    temp_sprite = pygame.sprite.Sprite()
    temp_sprite.rect = pygame.Rect(x, y, 40, 40)  # Asumiendo que 40x40 es el tamaño del gato/ratón
    return not pygame.sprite.spritecollideany(temp_sprite, nivel.grupo)

def generate_valid_positions(nivel):
    # Generar posiciones aleatorias para Tom y Jerry, asegurando que no estén demasiado cerca y no en paredes
    while True:
        tom_x = random.randint(0, 800 - 40)  # 40 es el tamaño del gato/ratón
        tom_y = random.randint(0, 600 - 40)
        jerry_x = random.randint(0, 800 - 40)
        jerry_y = random.randint(0, 600 - 40)

        # Verificar si las posiciones son válidas (no en paredes)
        if not is_position_valid(nivel, tom_x, tom_y) or not is_position_valid(nivel, jerry_x, jerry_y):
            continue  # Intentar nuevamente si las posiciones son inválidas

        # Calcular la distancia entre Tom y Jerry
        distance = math.sqrt((tom_x - jerry_x)**2 + (tom_y - jerry_y)**2)

        # Asegurar que la distancia sea superior al umbral mínimo
        if distance >= MIN_SPAWN_DISTANCE:
            return (tom_x, tom_y), (jerry_x, jerry_y)

class Raton(pygame.sprite.Sprite):
    def __init__(self, posX, posY):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('images/raton1.png').convert()
        self.image.set_colorkey((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.topleft = (posX, posY)
        self.dy = 0
        self.dx = 0
        self.last_direction_change = time.time()  # Seguir el último cambio de dirección

    def update(self):
        self.pos = self.rect.topleft
        self.rect.move_ip(self.dx, self.dy)

    def deshacer(self):
        self.rect.topleft = self.pos

    def move_random(self, nivel, gato):
        # Cambiar de dirección solo si ha pasado 1 segundo desde el último cambio
        if time.time() - self.last_direction_change >= 0.5:
            # 1/5 de probabilidad de realizar un movimiento aleatorio
            if random.randint(1, 5) == 1:
                directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
                random.shuffle(directions)
                for dx, dy in directions:
                    self.dx, self.dy = dx, dy
                    self.update()
                    if not pygame.sprite.spritecollide(self, nivel.grupo, 0, pygame.sprite.collide_mask):
                        self.last_direction_change = time.time()  # Reiniciar temporizador
                        break
                    self.deshacer()
            else:
                # Moverse lejos del gato
                cat_pos = gato.rect.topleft
                mouse_pos = self.rect.topleft
                dx = mouse_pos[0] - cat_pos[0]  # Moverse horizontalmente
                dy = mouse_pos[1] - cat_pos[1]  # Moverse verticalmente

                # Normalizar la dirección
                magnitude = math.sqrt(dx**2 + dy**2)
                if magnitude != 0:
                    dx = int((dx / magnitude) * 2)
                    dy = int((dy / magnitude) * 2)

                # Intentar moverse lejos del gato
                self.dx, self.dy = dx, dy
                self.update()
                if pygame.sprite.spritecollide(self, nivel.grupo, 0, pygame.sprite.collide_mask):
                    self.deshacer()  # Deshacer el movimiento si choca con una pared
                self.last_direction_change = time.time()  # Reiniciar temporizador

class Gato(pygame.sprite.Sprite):
    def __init__(self, posX, posY):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('images/gato.png').convert()
        self.image.set_colorkey((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.topleft = (posX, posY)
        self.dy = 0
        self.dx = 0
        self.q_table = np.zeros((20, 15, 4))  # Tabla Q para aprendizaje Q (20 filas, 15 columnas, 4 acciones)
        self.alpha = 0.1  # Tasa de aprendizaje
        self.gamma = 0.9  # Factor de descuento
        self.epsilon = 1.0  # Tasa de exploración
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        self.last_direction_change = time.time()  # Seguir el último cambio de dirección
        self.current_action = None  # Seguir la acción actual
        self.last_distance = None  # Seguir la última distancia al ratón

        # Cargar la tabla Q guardada si está habilitado
        if USE_SAVED_WEIGHTS and os.path.exists('q_table.npy'):
            self.q_table = np.load('q_table.npy')
            print("Tabla Q guardada cargada.")

    def update(self):
        self.pos = self.rect.topleft
        self.rect.move_ip(self.dx, self.dy)

    def deshacer(self):
        self.rect.topleft = self.pos

    def choose_action(self, estado):
        if random.uniform(0, 1) < self.epsilon:
            return random.randint(0, 3)  # Explorar: elegir acción aleatoria
        else:
            return np.argmax(self.q_table[estado])  # Explotar: elegir la mejor acción

    def learn(self, estado, action, reward, next_estado):
        predict = self.q_table[estado][action]
        target = reward + self.gamma * np.max(self.q_table[next_estado])
        self.q_table[estado][action] += self.alpha * (target - predict)

    def move_q_learning(self, nivel, raton):
        estado = self.get_estado()  # Siempre obtener el estado actual
        if time.time() - self.last_direction_change >= 0.5:
            self.current_action = self.choose_action(estado)
            self.dx, self.dy = [(0, -2), (0, 2), (-2, 0), (2, 0)][self.current_action]
            self.last_direction_change = time.time()  # Reiniciar temporizador

        # Calcular distancia antes de moverse
        cat_pos = self.rect.topleft
        mouse_pos = raton.rect.topleft
        current_distance = math.sqrt((cat_pos[0] - mouse_pos[0])**2 + (cat_pos[1] - mouse_pos[1])**2)

        # Mover el gato
        self.update()

        # Calcular distancia después de moverse
        new_cat_pos = self.rect.topleft
        new_distance = math.sqrt((new_cat_pos[0] - mouse_pos[0])**2 + (new_cat_pos[1] - mouse_pos[1])**2)

        # Sistema de recompensa/penalización
        if pygame.sprite.spritecollide(self, nivel.grupo, 0, pygame.sprite.collide_mask):
            self.deshacer()
            reward = -20  # Penalización por chocar con una pared
        elif pygame.sprite.collide_rect(self, raton):
            reward = 100  # Gran recompensa por atrapar al ratón
        else:
            # Recompensar por acercarse, penalizar por alejarse
            if self.last_distance is not None:
                distance_change = self.last_distance - new_distance
                reward = distance_change * 10  # Escalar la recompensa basada en el cambio de distancia
            else:
                reward = 0
            self.last_distance = new_distance  # Actualizar la última distancia

        next_estado = self.get_estado()
        self.learn(estado, self.current_action, reward, next_estado)
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def get_estado(self):
        # El estado es la posición del gato (x, y) en coordenadas de cuadrícula
        x, y = self.rect.topleft
        return (x // 40, y // 40)

    def save_q_table(self):
        # Guardar la tabla Q en un archivo
        np.save('q_table.npy', self.q_table)
        print("Tabla Q guardada en 'q_table.npy'.")

# Bucle principal para iteraciones
for iteration in range(NUM_ITERATIONS):
    print(f"Iteración {iteration + 1}/{NUM_ITERATIONS}")

    # Inicializar objetos de juego
    if RENDER:
        visor = pygame.display.set_mode((800, 600), 0, 32)

    # Cargar el mapa
    nivel = mapa.Mapa('game/mapa.txt')

    # Generar posiciones iniciales válidas para Tom y Jerry
    tom_pos, jerry_pos = generate_valid_positions(nivel)
    raton = Raton(jerry_pos[0], jerry_pos[1])
    gato = Gato(tom_pos[0], tom_pos[1])

    grupoRaton = pygame.sprite.RenderUpdates(raton)
    grupoGato = pygame.sprite.RenderUpdates(gato)

    start_time = time.time()
    running = True

    while running:
        elapsed_time = time.time() - start_time
        if elapsed_time > TIME_LIMIT:
            print("Se alcanzó el límite de tiempo. Pasando a la siguiente iteración.")
            break

        for evento in pygame.event.get():
            if evento.type == QUIT or (evento.type == KEYDOWN and evento.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

        if gato.rect.right > 800:
            break

        # El ratón se mueve aleatoriamente o huye del gato
        raton.move_random(nivel, gato)

        # El gato aprende a perseguir al ratón
        gato.move_q_learning(nivel, raton)

        grupoRaton.update()
        grupoGato.update()

        if pygame.sprite.spritecollide(raton, nivel.grupo, 0, pygame.sprite.collide_mask):
            raton.deshacer()

        if pygame.sprite.spritecollide(gato, nivel.grupo, 0, pygame.sprite.collide_mask):
            gato.deshacer()

        for pum in pygame.sprite.groupcollide(grupoRaton, nivel.quesos, 0, 1):
            pass

        # Verificar si todos los quesos han sido recolectados
        if len(nivel.quesos) == 0:
            break

        # Verificar si gato.png toca raton1.png
        if pygame.sprite.spritecollide(raton, grupoGato, 0, pygame.sprite.collide_mask):
            print("¡El gato atrapó al ratón!")
            break

        if RENDER:
            nivel.actualizar(visor)
            grupoRaton.draw(visor)
            grupoGato.draw(visor)
            pygame.display.update()

        # Limitar la tasa de cuadros por segundo
        pygame.time.Clock().tick(60)

    if RENDER:
        pygame.display.quit()

# Guardar la tabla Q después del entrenamiento si está habilitado
if SAVE_WEIGHTS:
    gato.save_q_table()

print("Entrenamiento completo.")