# -*- coding: utf-8 -*-
import pygame

class Pared(pygame.sprite.Sprite):
    def __init__(self, imagen, pos):
        # Initialize the wall sprite
        pygame.sprite.Sprite.__init__(self)
        self.image = imagen
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

    def update(self):
        pass

class Queso(pygame.sprite.Sprite):
    def __init__(self, imagen, pos):
        # Initialize the cheese sprite
        pygame.sprite.Sprite.__init__(self)
        self.image = imagen
        self.rect = self.image.get_rect()
        self.rect_colision = self.rect.inflate(-30, -10)
        self.delay = 0
        self.se_puede_comer = True
        self.rect.topleft = pos
    
    def update(self):
        pass

    def update_desaparecer(self):
        # Update the cheese to disappear after being eaten
        self.delay -= 1
        if self.delay < 1:
            self.kill()

    def comer(self):
        # Handle the cheese being eaten
        self.delay = 30
        self.update = self.update_desaparecer
        self.se_puede_comer = False

class Mapa:
    def __init__(self, archivo, enable_render=True):
        # Initialize the map
        self.grupo = pygame.sprite.RenderUpdates()
        self.quesos = pygame.sprite.RenderUpdates()
        self.enable_render = enable_render

        if enable_render:
            self.h = pygame.image.load('images/h.png').convert_alpha()
            self.v = pygame.image.load('images/v.png').convert_alpha()
            self.sd = pygame.image.load('images/sd.png').convert_alpha()
            self.id = pygame.image.load('images/id.png').convert_alpha()
            self.ii = pygame.image.load('images/ii.png').convert_alpha()
            self.si = pygame.image.load('images/si.png').convert_alpha()
        self.q = pygame.image.load('images/q.png').convert_alpha()
        
        archivo = open(archivo)
        self.textoMapa = archivo.readlines()
        archivo.close()

        fila = -1
        for linea in self.textoMapa:
            fila += 1
            columna = -1
            for c in linea:
                columna += 1
                x, y = self.aPixel(fila, columna)

                if enable_render:
                    if c == '-':
                        self.grupo.add(Pared(self.h, (x, y)))
                    elif c == '|':
                        self.grupo.add(Pared(self.v, (x, y)))
                    elif c == '7':
                        self.grupo.add(Pared(self.sd, (x, y)))
                    elif c == 'J':
                        self.grupo.add(Pared(self.id, (x, y)))
                    elif c == 'L':
                        self.grupo.add(Pared(self.ii, (x, y)))
                    elif c == 'T':
                        self.grupo.add(Pared(self.si, (x, y)))
                if c == 'k':
                    self.quesos.add(Queso(self.q, (x, y)))

    def actualizar(self, visor):
        # Update the map and draw it on the screen
        visor.fill((173, 216, 230))
        self.grupo.update()
        self.grupo.draw(visor)
        self.quesos.update()
        self.quesos.draw(visor)

    def aPixel(self, fila, columna):
        # Convert grid coordinates to pixel coordinates
        return (columna * 40, fila * 40)

    def aCuadricula(self, x, y):
        # Convert pixel coordinates to grid coordinates
        return (y / 40, x / 40)





