import pygame as pg
import numpy as np
import math

# 'nome da função':[função -> lambda, dominio xy -> [min, max], contradomínio z -> [min, max]]
FUNCTONS = {
    'sphere':[lambda x, y: (x**2 + y**2)**1, [-1, 1], [0, 2]],
    'rosembrock': [lambda x, y: (1 - x)**2 + 100*(y - x**2)**2, [-1, 1], [0, 404]],
    'mishra_bird': [lambda x, y: math.sin(y)*math.e**((1-math.cos(x))**2) + math.cos(x)*math.e**((1-math.sin(y))**2) + (x - y)**2, [-10, 0], [-105.5, 115.8]],
    'cross_in_tray': [lambda x, y: -0.001*(abs(math.sin(x)*math.sin(y)*math.e**abs(100-(x**2+y**2)**0.5/math.pi))+1)**0.1, [-10, 10], [-20.7,-7.2]],
    'eason': [lambda x, y: -math.cos(x)*math.cos(y)*math.e**-((x-math.pi)**2 + (y-math.pi)**2), [-100, 100], [-1, 0.1]],
    'beale':[lambda x, y: (1.5-x+x*y)**2 + (2.25-x+x*y**2)**2 + (2.625-x+x*y**3)**2, [-4.5, 4.5], [0, 181854]]
}

class LineData:
    def __init__(self, *args): self.points, self.style, self.color, self.width = args

class Graph: # gráfico para plotar dados
    def __init__(self, position, size):
        self.position = position
        self.width, self.height = size
        self.bg_color = [255,255,255]
        self.surface = pg.Surface(size)
        self.data = []
        self.settings = {'x_max':None, 'x_min':None, 'y_max':None, 'y_min':None}
        self.clear()

        self.axis_font = pg.font.SysFont('calibre', 18)
        self.axis_color = (180,180,180)

        self.xymouse = False
        self.xymouse_surface = pg.Surface(size, pg.SRCALPHA)
        self.xymouse_color = (0,100,100)
        self.grid = False

        self.origin = np.array([0, self.height])
        self.horientation = np.array([1, -1])
        (self.x_max, self.x_min), (self.y_max, self.y_min) = (1, -1), (1, -1)
        self.scale = np.array([1, 1])

    def calculate_parameters(self):
        points = np.concatenate([line.points for line in self.data])
        self.x_max, self.y_max = np.amax(points, axis=0)
        self.x_min, self.y_min = np.amin(points, axis=0)

        if self.settings['x_max'] != None: self.x_max = self.settings['x_max']
        if self.settings['x_min'] != None: self.x_min = self.settings['x_min']
        if self.settings['y_max'] != None: self.y_max = self.settings['y_max']
        if self.settings['y_min'] != None: self.y_min = self.settings['y_min']

        dy = self.y_max-self.y_min
        if not dy: dy = 1
        dx = self.x_max-self.x_min
        if not dx: dx = 1

        self.scale = np.array([self.width/dx, self.height/dy])
        self.origin = np.array([-self.x_min*self.scale[0], self.height + self.y_min*self.scale[1]])

    def plot(self, x_data, y_data, style='-', color=(0,0,0), w=2):
        self.data.append(LineData(np.stack((x_data, y_data), axis=1), style, color, w))
        self.calculate_parameters()

        self.surface.fill(self.bg_color)
        for line in self.data:
        	points = (line.points*self.scale*self.horientation + self.origin).astype(int)
        	if '-' in line.style and len(points)>=2: pg.draw.lines(self.surface, line.color, False, points, line.width)
        	if 'o' in line.style:
        		for x, y in points: pg.draw.ellipse(self.surface, line.color,
        			[int(x-line.width), int(y-line.width), line.width*2, line.width*2])
        	if line.style == 'bar':
        		w = self.width//len(points)
        		for x, y in points:
        			pg.draw.polygon(self.surface, line.color, [(x-w//2, y), (x+w//2, y), (x+w//2, self.height), (x-w//2, self.height)])
        if self.grid: self.draw_grid()

    def show(self, root):
        if self.xymouse and pg.Rect(self.position, self.xymouse_surface.get_size()).collidepoint(pg.mouse.get_pos()):
            self.xymouse_surface.fill(pg.SRCALPHA)
            pg.mouse.set_visible(False)
            mx, my = mouse_pos = np.array(pg.mouse.get_pos()) - np.array(self.position)
            pg.draw.line(self.xymouse_surface, (255,100,100), (mx-5, my), (mx+5, my))
            pg.draw.line(self.xymouse_surface, (255,100,100), (mx, my-5), (mx, my+5))
            x, y = (mouse_pos-self.origin)/self.scale*self.horientation
            text = self.axis_font.render(f'x: {x:.2f}   y: {y:.2f}  ', False, self.xymouse_color)
            self.xymouse_surface.blit(text, (
                mx-text.get_width() if mx-text.get_width()>0 else mx+10,
                my-text.get_height() if my-text.get_height()>0 else my+10
            ))
        else:
            self.xymouse_surface.fill(pg.SRCALPHA)
            pg.mouse.set_visible(True)
        root.blit(self.surface, self.position)
        root.blit(self.xymouse_surface, self.position)

    def clear(self):
        self.data = []
        self.surface.fill(self.bg_color)

    def draw_grid(self, w=10):
        for i in range(w):
            x = self.width//w * i
            y = self.height//w * i
            pg.draw.line(self.surface, self.axis_color, (x, 0), (x, self.height))
            self.surface.blit(self.axis_font.render(f'{((x-self.origin[0])/self.scale[0])*self.horientation[0]:.2f}', False, self.axis_color), (x+1, self.height-w))
            pg.draw.line(self.surface, self.axis_color, (0, y), (self.width, y))
            self.surface.blit(self.axis_font.render(f'{((y-self.origin[1])/self.scale[1])*self.horientation[1]:.2f}', False, self.axis_color), (w, y+1))

class Label:
    def __init__(self, text, position, font):
        self.text = font.render(text, False, (0,0,0))
        self.rect = self.text.get_rect()
        self.rect.topleft = position
        self.font = font

    def draw(self, surface): surface.blit(self.text, self.rect)

    def set_text(self, text):
        self.text = self.font.render(text, False, (0,0,0))

class Button:
    def __init__(self, text, position, font):
        self.t = text
        self.text = font.render(text, False, (0,0,0))
        self.rect = self.text.get_rect()
        self.rect.topleft = position

        self.is_pressed = False

    def draw(self, surface):
        pg.draw.rect(surface, (0,255,255) if self.is_pressed else (200,200,200), self.rect)
        surface.blit(self.text, self.rect)

class Slider:
    def __init__(self, min_value, max_value, position, size, font, default_value=None):
        self.min, self.max = min_value, max_value
        self.value  = default_value if default_value else self.min
        self.font = font
        self.text = self.font.render(str(self.value), False, (0,0,0))
        self.position = position
        self.slider_rects = [pg.Rect((self.position[0], self.position[1] + self.text.get_rect().height), size) for _ in range(3)]
        self.slider_rects[1].inflate_ip(0, int(-2/3*size[1]))
        self.slider_rects[1].centery = self.slider_rects[0].centery
        self.slider_rects[2].inflate_ip(int(-9.5/10*size[0]), 0)
        self.size = [size[0], size[1]+self.text.get_rect().height]
        self.update_slider_position()

        self.is_pressed = False

    def update_slider_position(self):
        k = self.slider_rects[0].width/(self.max-self.min)
        c = self.slider_rects[0].right-self.max*k
        self.slider_rects[2].centerx = int(self.value*k + c)
        self.text = self.font.render(f'{self.value:.2f}', False, (0,0,0))

    def set_value(self, value):
        self.value = np.clip(value, self.min, self.max)
        self.update_slider_position()

    def draw(self, surface):
        pg.draw.rect(surface, (150,150,150), self.slider_rects[1])
        pg.draw.rect(surface, (255,0,0), self.slider_rects[2])
        surface.blit(self.text, (self.slider_rects[2].centerx, self.position[1]))

class Field:
    def __init__(self, position, size, len_particles, scale=10, function_name='sphere'):
        self.position = np.array(position)
        self.size = self.width, self.height = np.array(size)
        self.len_particles = len_particles

        self.m = -1 # 1 para achar o ponto mais alto e -1 para mais baixo

        self.f, (self.lim_min, self.lim_max), (self.ylim_min, self.ylim_max) = FUNCTONS[function_name]

        k = 1/(self.ylim_max - self.ylim_min)
        c = 1 - self.ylim_max*k
        self.field = [[(self.f(x, y)*k + 1 - self.ylim_max*k) * np.array([255, 0, -255]) + np.array([0, 0, +255])
            for x in np.linspace(self.lim_min, self.lim_max, self.width//scale)]
            for y in np.linspace(self.lim_min, self.lim_max, self.height//scale)]
        self.field = np.clip(np.array(self.field), 0, 255)
        self.field = pg.transform.scale( pg.surfarray.make_surface(self.field), self.size)

        self.surface = pg.Surface(self.size)

        self.positions = np.random.choice(np.linspace(self.lim_min, self.lim_max, 100), (self.len_particles, 2))
        self.speeds = np.random.choice(np.linspace(-1, 1, 100), (self.len_particles, 2))
        self.bests_positions = self.positions[:]
        self.fitness = [self.f(x, y)*self.m for x, y in self.positions]
        self.gbest = self.bests_positions[0]

        self.evolution = []

        self.c1 = 0
        self.c2 = 0
        self.w = 0

    def update(self):
        self.gbest = self.bests_positions[self.fitness.index(sorted(self.fitness)[-1])]
        r1, r2 = np.random.rand(self.len_particles, 1), np.random.rand(self.len_particles, 1)
        self.speeds = self.w*self.speeds + self.c1*r1*(self.bests_positions - self.positions) + self.c2*r2*(self.gbest - self.positions)
        self.positions = self.positions + self.speeds
        for i, fitness in enumerate([self.f(x, y)*self.m for x, y in self.positions]):
            if fitness > self.fitness[i]:
                self.fitness[i] = fitness
                self.bests_positions[i] = self.positions[i]
        self.evolution.append(np.median(self.fitness))

    def draw(self, root):
        self.surface.fill((0,0,0))
        self.surface.blit(self.field, self.position)
        for position in self.positions:
            s = self.size/(self.lim_max - self.lim_min)
            k = self.size - self.position - self.lim_max*s
            x, y = np.clip((position*s + k).astype(int), (0, 0), self.size)
            pg.draw.line(self.surface, (255,255,0), (x - 5, y), (x + 5, y))
            pg.draw.line(self.surface, (255,255,0), (x, y - 5), (x, y + 5))
        root.blit(self.surface, self.position)

def field_update():
    global field
    field = Field((0,0), (h_width,h_height), len_particles, scale, function_name)
    field.c1 = C1
    field.c2 = C2
    field.w = W

pg.init()
pg.display.set_caption('PSO algorithm')
size = width, height = (600,600)
h_width, h_height = width//2, height//2
screen = pg.display.set_mode(size)

plt = Graph((0, h_height), (width, h_height))
plt.grid = True
plt.xymouse = True

title = Label('Otimização por enxame de párticulas', (h_width, 10), pg.font.SysFont('corbel', 18, bold=True))
title.rect.centerx = pg.Rect(h_width, 0, h_height, title.rect.height).centerx

font1 = pg.font.SysFont('corbel', 15, bold=True)
label_function = Label('Função: ', (h_width+10, title.rect.bottom+10), font1)
buttons = []
for i, name_button in enumerate(list(FUNCTONS.keys())[:3]):
    buttons.append(Button(' '+name_button+' ',
        (label_function.rect.left + 5*i + (sum([button.rect.width if i!=j else 0 for j, button in enumerate(buttons)]) if i else 0),
         label_function.rect.bottom + 5), font1))
for i, name_button in enumerate(list(FUNCTONS.keys())[3:]):
    buttons.append(Button(' '+name_button+' ',
        (label_function.rect.left + 5*i + (sum([button.rect.width if i!=j else 0 for j, button in enumerate(buttons[3:])]) if i else 0),
         label_function.rect.bottom + 10 + buttons[0].rect.height), font1))

buttons[0].is_pressed = True

label_len_particles = Label('Particulas:', (h_width, buttons[-1].rect.bottom+5), font1)
slider_len_particles = Slider(1, 100, (label_len_particles.rect.right+10, buttons[-1].rect.bottom), (120, 20), font1, 10)
label_len_particles.rect.centery = slider_len_particles.slider_rects[0].centery

label_c1 = Label('Parâmetro cognitivo:', (h_width, slider_len_particles.slider_rects[0].bottom+5), font1)
slider_c1 = Slider(0, 1, (label_c1.rect.right+10, slider_len_particles.slider_rects[0].bottom+5), (120, 20), font1)
label_c1.rect.centery = slider_c1.slider_rects[0].centery

label_c2 = Label('Parâmetro social:', (h_width, slider_c1.slider_rects[0].bottom+5), font1)
slider_c2 = Slider(0, 1, (label_c2.rect.right+10, slider_c1.slider_rects[0].bottom+5), (120, 20), font1, 1)
label_c2.rect.centery = slider_c2.slider_rects[0].centery

label_w = Label('Parâmetro inercial:', (h_width, slider_c2.slider_rects[0].bottom+5), font1)
slider_w = Slider(0, 1, (label_w.rect.right+10, slider_c2.slider_rects[0].bottom+5), (120, 20), font1)
label_w.rect.centery = slider_w.slider_rects[0].centery

play_button = Button(' > ', (h_width+20, slider_w.slider_rects[0].bottom+10), pg.font.SysFont('corbel', 24, bold=True))
pause_button = Button(' || ', (h_width+20+play_button.rect.width+10, slider_w.slider_rects[0].bottom+10), pg.font.SysFont('corbel', 24, bold=True))
reload_button = Button(' << ', (h_width+20+play_button.rect.width+20+pause_button.rect.width, slider_w.slider_rects[0].bottom+10), pg.font.SysFont('corbel', 24, bold=True))

label_bestxy = Label('______________',
    (h_width+20+play_button.rect.width+30+pause_button.rect.width+reload_button.rect.width, slider_w.slider_rects[0].bottom+10),
    pg.font.SysFont('corbel', 15))

function_name = list(FUNCTONS.keys())[0]
len_particles = 10
C1 = 0
C2 = 1
W = 0
scale = 10
field_update()

run = False
while True:
    # pg.time.Clock().tick(1)
    for event in pg.event.get():
        if event.type == pg.QUIT: quit()
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                if slider_len_particles.slider_rects[2].collidepoint(event.pos):
                    slider_len_particles.is_pressed = True
                elif slider_c1.slider_rects[2].collidepoint(event.pos):
                    slider_c1.is_pressed = True
                elif slider_c2.slider_rects[2].collidepoint(event.pos):
                    slider_c2.is_pressed = True
                elif slider_w.slider_rects[2].collidepoint(event.pos):
                    slider_w.is_pressed = True
                elif pause_button.rect.collidepoint(event.pos):
                        run = False
                        pause_button.is_pressed = True
                        play_button.is_pressed = False
                        reload_button.is_pressed = False
                elif play_button.rect.collidepoint(event.pos):
                        run = True
                        play_button.is_pressed = True
                        pause_button.is_pressed = False
                        reload_button.is_pressed = False
                elif reload_button.rect.collidepoint(event.pos):
                        field_update()
                        play_button.is_pressed = False
                        pause_button.is_pressed = False
                        reload_button.is_pressed = True
                else:
                    for i, button in enumerate(buttons):
                        if button.rect.collidepoint(event.pos):
                            button.is_pressed = True
                            function_name = button.t.strip(' ')
                            field_update()
                            break
                    for j, button in enumerate(buttons):
                        if j != i: button.is_pressed = False
        elif event.type == pg.MOUSEMOTION:
            for i, slider in enumerate([slider_len_particles, slider_c1, slider_c2, slider_w]):
                if slider.is_pressed:
                    k = slider.slider_rects[0].width/(slider.max-slider.min)
                    c = slider.slider_rects[0].right-slider.max*k
                    slider.set_value((event.pos[0]-c)/k)
                    if i == 0: len_particles = int(slider.value)
                    elif i == 1: C1 = slider.value
                    elif i == 2: C2 = slider.value
                    elif i == 3: W = slider.value
                    field.c1 = C1
                    field.c2 = C2
                    field.w = W
        elif event.type == pg.MOUSEBUTTONUP:
            for slider in [slider_len_particles, slider_c1, slider_c2, slider_w]:
                if slider.is_pressed: slider.is_pressed = False

    screen.fill((255,255,255))

    if run: field.update()
    field.draw(screen)

    plt.clear()
    try: plt.plot(range(len(field.evolution)), field.evolution)
    except: pass
    plt.show(screen)

    label_bestxy.set_text('x: {gbestx:.2f}, y: {gbesty:.2f}'.format(gbestx=field.gbest[0], gbesty=field.gbest[1]))

    for item in [title, label_function,label_len_particles, slider_len_particles, label_c1, slider_c1,
        label_c2, slider_c2, label_w, slider_w, pause_button, play_button, reload_button, label_bestxy]+buttons:
        item.draw(screen)

    pg.display.flip()
