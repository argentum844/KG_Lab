import pygame
import pygame_gui
from collections import deque


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Закраска произвольной области текстурой")
        self.WIDTH = 1200
        self.HEIGHT = 700
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.pos_area = self.WIDTH - self.HEIGHT
        self.manager = pygame_gui.UIManager((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()

        self.text_box_texture = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect(20, 10, 250, 70),
                                                              html_text="",
                                                              manager=self.manager)
        self.button_texture = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(300, 10, 180, 70),
                                                           text="Выбрать Текстуру",
                                                           manager=self.manager)

        self.text_box_bg = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect(20, 120, 250, 70),
                                                         html_text="",
                                                         manager=self.manager)
        self.button_bg = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(300, 120, 180, 70),
                                                      text="Выбрать Основу",
                                                      manager=self.manager)
        self.text_box_x = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect(20, 200, 50, 30),
                                                        html_text="X: ",
                                                        manager=self.manager)
        self.input_box_x = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(70, 200, 50, 30))
        self.text_box_y = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect(20, 250, 50, 30),
                                                        html_text="Y: ",
                                                        manager=self.manager)
        self.input_box_y = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(70, 250, 50, 30))

        self.text_box_dx = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect(20, 300, 50, 30),
                                                         html_text="DX: ",
                                                         manager=self.manager)
        self.input_box_dx = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(70, 300, 50, 30))

        self.text_box_dy = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect(20, 350, 50, 30),
                                                         html_text="DY: ",
                                                         manager=self.manager)
        self.input_box_dy = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(70, 350, 50, 30))

        self.clear_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.WIDTH - self.HEIGHT - 200, self.HEIGHT - 100, 180, 50),
            manager=self.manager,
            text="Очистить рисунок")

        self.field = Field(self)
        self.dialog_bg = None
        self.dialog_texture = None


    def update(self):
        self.field.update()
        pygame.display.flip()

    def draw(self):
        self.screen.fill((0, 0, 0))
        pygame.draw.line(self.screen, (0, 255, 0), (self.WIDTH - self.HEIGHT - 3, 0),
                         (self.WIDTH - self.HEIGHT - 3, self.HEIGHT), width=5)
        self.screen.blit(self.field.surface, self.field.rect)

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)
            self.check_button_clicked(event)
            self.check_close_file_dialog(event)
            self.field.check_click(event)
            self.manager.process_events(event)

    def check_close_file_dialog(self, event):
        if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
            if event.ui_element == self.dialog_bg:
                self.text_box_bg.set_text(event.text)
                self.field.change_image(event.text)
            if event.ui_element == self.dialog_texture:
                self.text_box_texture.set_text(event.text)
                self.field.change_texture(event.text)

    def check_button_clicked(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.button_texture:
                self.dialog_texture = pygame_gui.windows.UIFileDialog(manager=self.manager, rect=pygame.Rect(0, 0, 700, 700))
            elif event.ui_element == self.button_bg:
                self.dialog_bg = pygame_gui.windows.UIFileDialog(manager=self.manager, rect=pygame.Rect(0, 0, 700, 700))

    def run(self):
        while True:
            time_delta = self.clock.tick(60) / 1000.0
            self.check_events()
            self.update()
            self.manager.update(time_delta)
            self.draw()
            self.manager.draw_ui(self.screen)


class Field:
    def __init__(self, app):
        self.app = app
        self.surface = pygame.Surface((app.HEIGHT, app.HEIGHT))
        self.rect = pygame.Rect(self.app.WIDTH - self.app.HEIGHT, 0, self.app.HEIGHT, self.app.HEIGHT)
        self.surface.fill((255, 255, 255))
        self.image = None
        self.texture = None

    def update(self):
        pass

    def draw(self):
        pass

    def change_image(self, path):
        self.image = pygame.transform.scale(pygame.image.load(path), (self.app.HEIGHT, self.app.HEIGHT))
        self.surface.blit(self.image, self.image.get_rect())

    def change_texture(self, path):
        self.texture = pygame.image.load(path)

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if (not (self.image is None) and not (self.texture is None) and self.app.input_box_x.text != ""
                    and self.app.input_box_y.text != "" and self.app.input_box_dy.text != "" and self.app.input_box_dx.text != ""):
                    x = int(self.app.input_box_x.text)
                    y = int(self.app.input_box_y.text)
                    dx = float(self.app.input_box_dx.text)
                    dy = float(self.app.input_box_dy.text)
                    self.task((event.pos[0] - self.app.WIDTH + self.app.HEIGHT, event.pos[1]), (x, y), dx, dy)

    def task(self, pos_bg, pos_texture, dx, dy):
        # print(pos_bg, pos_texture)
        q = deque()
        q.append((0, 0))
        visited = set()
        color = self.surface.get_at(pos_bg)
        while len(q) != 0:
            x, y = q.pop()
            visited.add((x, y))
            xt = int(pos_texture[0] + dx*x) % self.texture.get_size()[0]
            yt = int(pos_texture[1] + dy*y) % self.texture.get_size()[1]
            self.surface.set_at((pos_bg[0]+x, pos_bg[1]+y), self.texture.get_at((xt, yt)))
            for i in (-1, 0, 1):
                for j in (-1, 0, 1):
                    if ((x+i, y+j) not in visited and pos_bg[0]+x+i >= 0 and pos_bg[0]+x+i < self.app.HEIGHT and
                        pos_bg[1]+y+j >= 0 and pos_bg[1]+y+j < self.app.HEIGHT
                        and self.surface.get_at((pos_bg[0]+x+i, pos_bg[1]+y+j)) == color):
                        q.append((x+i, y+j))





if __name__ == "__main__":
    app = App()
    app.run()