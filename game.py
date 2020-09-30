import arcade
import random
import pyglet
import math
import playsound

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 700

platform = pyglet.window.get_platform()
display = platform.get_default_display()
screen = display.get_default_screen()
bird_picture = "data/Bird.png"

MONITOR_WIDTH = screen.width
MONITOR_HEIGHT = screen.height
PLAYER_SCALING = 0.06


class Bird(arcade.Sprite):
    def __init__(self, filename, scaling):
        super().__init__(filename, scaling)
        self.center_x = 0.5 * SCREEN_WIDTH
        self.center_y = 0.6 * SCREEN_HEIGHT
        self.radius = 10
        self.change_y = 0
        self.moving = False
        self.started = False
        self.dead = False
        self.playsound = False

    def move(self, d_time):
        if self.center_y < self.radius + 2:
            self.moving = False
            self.dead = True
            if not self.playsound:
                playsound.playsound("data/sfx_hit.wav", block=False)
                self.playsound = True
        self.change_y -= 50 * d_time
        self.center_y += self.change_y
        if self.change_y > 0:
            self.angle = 3 * self.change_y
        elif self.change_y < 0 and self.change_y > -15:
            self.angle = 3 * self.change_y
        else:
            self.angle = -45

    def jump_up(self):
        if self.moving and not self.dead:
            self.change_y = 16
            playsound.playsound("data/sfx_wing.wav", block=False)


class Pipe(arcade.Sprite):
    def __init__(self):
        super().__init__("data/Pipe.png", 0.336)
        self.center_x = SCREEN_WIDTH + 80
        self.center_y = random.randint(100, 550) - 642
        self.change_x = -250
        self.gap = 50
        self.pair_centre_y = self.center_y + self.gap + 642 * 2

    def update(self, delta_time):
        self.center_x += self.change_x * delta_time


class PipePair(arcade.Sprite):
    def __init__(self, pair):
        super().__init__("data/Pipe.png", 0.336)
        self.center_x = SCREEN_WIDTH + 80
        self.center_y = pair.pair_centre_y
        self.change_x = -250
        self.angle = 180

    def update(self, delta_time):
        self.center_x += self.change_x * delta_time


class Title(arcade.Sprite):
    def __init__(self):
        super().__init__("data/Title.png", 2)
        self.center_x = 0.5 * SCREEN_WIDTH
        self.center_y = 0.9 * SCREEN_HEIGHT
        self.change_y = 0
        self.height_angle = 1
        self.height_angle_rad = 0

    def update(self):
        self.height_angle_rad = math.radians(self.height_angle)
        self.center_y += math.sin(self.height_angle_rad) * 0.5
        self.height_angle += 5


class MyGame(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height, "FlappyBird")
        self.player = Bird(bird_picture, PLAYER_SCALING)
        self.pipe_list = None
        self.set_location(MONITOR_WIDTH // 2 - SCREEN_WIDTH // 2, MONITOR_HEIGHT // 2 - SCREEN_HEIGHT // 2)
        self.score = 0
        arcade.set_background_color(arcade.color.LIGHT_BLUE)
        self.player_list = None
        self.background_image = arcade.load_texture("data/Background.png")
        self.flash_drawn = 0
        self.title_list = None
        self.current_pipe = None
        self.frame = 0
        self.fps = 0
        self.temp_fps = 0

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.pipe_list = arcade.SpriteList()
        self.title_list = arcade.SpriteList()

        self.title = Title()
        self.new_pipe = Pipe()
        self.new_pipe_pair = PipePair(self.new_pipe)
        self.pipe_list.append(self.new_pipe)
        self.pipe_list.append(self.new_pipe_pair)
        self.player_list.append(self.player)
        self.title_list.append(self.title)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, self.background_image.width, self.background_image.height, self.background_image, 0)
        self.pipe_list.draw()

        if self.player.started and not self.player.moving and self.flash_drawn < 5:
            arcade.draw_rectangle_filled(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT, arcade.color.WHITE)
            self.flash_drawn += 1

        elif self.player.dead:
            arcade.draw_text("\t   Score: {}\nPress R to restart".format(self.score), 0.19 * SCREEN_WIDTH, 0.9 * SCREEN_HEIGHT, arcade.color.WHITE, 30, bold=True, font_name="Rockwell Nova")
        elif self.player.started:
            arcade.draw_text("{}".format(self.score), SCREEN_WIDTH // 2, int(0.9 * SCREEN_HEIGHT), arcade.color.WHITE, 30, bold=True, font_name="Rockwell Nova")
        # Call draw() on all your sprite lists below
        self.player_list.draw()

        if not self.player.started:
            self.title_list.draw()

        arcade.draw_text(str(self.fps), 0.9 * SCREEN_WIDTH, 0.95 * SCREEN_HEIGHT, arcade.color.WHITE, 20, bold=True)

    def update(self, delta_time):
        self.title_list.update()
        self.current_pipe = self.new_pipe

        if round(1/delta_time) < 30:
            print("Frame rate is {}".format(round(1/delta_time)))

        self.frame += 1
        if self.frame % 5:
            self.fps = round(1/delta_time)

        #if self.player.center_y < self.new_pipe.center_y + 625:
        #    self.player.jump_up()

        if self.new_pipe.center_x < SCREEN_WIDTH - 300:
            self.new_pipe = Pipe()
            self.new_pipe_pair = PipePair(self.new_pipe)
            self.pipe_list.append(self.new_pipe)
            self.pipe_list.append(self.new_pipe_pair)

        if self.player.center_x - self.player.radius > self.current_pipe.center_x + 0.5 * self.current_pipe.width + 3:
            self.score += 1
            playsound.playsound("data/sfx_point.wav", block=False)

        if self.player.started:
            self.player.move(delta_time)

        if self.player.moving:
            for pipe in self.pipe_list:
                pipe.update(delta_time)
                if pipe.center_x < -30:
                    self.pipe_list.remove(pipe)
            self.hit_list = arcade.check_for_collision_with_list(self.player, self.pipe_list)
            if len(self.hit_list) > 0:
                self.player.moving = False
                playsound.playsound("data/sfx_hit.wav", block=False)
                self.player.change_y = 5
                self.player.playsound = True

    def on_key_press(self, key, key_modifiers):
        if key == arcade.key.SPACE and not self.player.started:
            self.player.started = True
            self.player.moving = True
            self.player.jump_up()

        elif key == arcade.key.SPACE and self.player.started and self.player.moving:
            self.player.jump_up()

        elif key == arcade.key.R:
            self.restart()

    def restart(self):
        self.player = Bird(bird_picture, PLAYER_SCALING)
        self.setup()
        self.score = 0
        self.flash_drawn = 0


def main():
    """ Main method """
    #playsound.playsound("data/background_music.wav", block=False)
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
