# Complete your game here
import pygame
import math
import random

import os
os.chdir(os.path.dirname(__file__))

class Coord:
    def __init__(self, position: tuple) -> None:
        if type(position) == Coord:
            self.x, self.y = position.x, position.y
        else:
            self.x, self.y = position

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def give_coordinates(self) -> tuple:
        return (self.x, self.y)
        
    def invert_x(self):
        self.x *= -1
    
    def invert_y(self):
        self.y *= -1    

    def invert_coord(self):
        self.invert_x()
        self.invert_y()

    def absolute(self):
        self = Coord((abs(self.x), abs(self.y)))

    @classmethod
    def borders(cls, object: 'Obj') -> tuple:
        x1 = object.position.x
        x2 = x1 + object.image.get_width()

        y1 = object.position.y
        y2 = y1 + object.image.get_height()
        
        return {
            "x1": x1,
            "x2": x2,
            "y1": y1,
            "y2": y2
        }
    
    @classmethod
    def between(cls, a: int, b: int, x: int) -> bool:
        if x < a or x > b:
            return False
        else:
            return True   

    @classmethod
    def detect_collision(cls, obj_a: 'Obj', obj_b: 'Obj'):

        def decider(criteria: callable) -> tuple:
            if criteria(obj_a) > criteria(obj_b):
                return (obj_a, obj_b)
            else:
                return (obj_b, obj_a)

        x_bigger, x_smaller = decider(lambda x: x.image.get_width())

        y_bigger, y_smaller = decider(lambda x: x.image.get_height())

        x_big_borders = Coord.borders(x_bigger)
        x_small_borders = Coord.borders(x_smaller)

        if Coord.between(x_big_borders["x1"], x_big_borders["x2"], x_small_borders["x1"]) or Coord.between(x_big_borders["x1"], x_big_borders["x2"], x_small_borders["x2"]):
            is_x_bw = True
        else:
            is_x_bw = False

        y_big_borders = Coord.borders(y_bigger)
        y_small_borders = Coord.borders(y_smaller)

        if Coord.between(y_big_borders["y1"], y_big_borders["y2"], y_small_borders["y1"]) or Coord.between(y_big_borders["y1"], y_big_borders["y2"], y_small_borders["y2"]):
            is_y_bw = True
        else:
            is_y_bw = False

        return is_x_bw and is_y_bw
    
    @classmethod
    def distance_between(cls, pos1: 'Coord', pos2: 'Coord') -> float:
        diff = (pos1 - pos2)
        diff.absolute()
        dx, dy = diff.x, diff.y
        return math.sqrt(dx**2 + dy**2)
    
    @classmethod
    def within_radius_of(cls, radius: int, object: 'Obj', pos: 'Coord'):
        if Coord.distance_between(object.position, pos) <= radius:
            return True
        return False

    def __add__(self, another):
        x = self.x + another.x
        y = self.y + another.y
        return Coord((x, y))
    
    def __sub__(self, another):
        x = self.x - another.x
        y = self.y - another.y
        return Coord((x, y))
    
    def __truediv__(self, num: int):
        x = self.x / num
        y = self.y / num
        return Coord((x, y))
    
class Cooldown:
    current_time = 0.0

    def __init__(self, cooldown: float = 1.0, last_use: float = 0.0) -> None:
        self.cooldown = cooldown
        self.last_use = last_use
    
    def is_on_cooldown(self):
        if self.last_use == 0:
            return False
        if Cooldown.current_time - self.cooldown < self.last_use:
            return True
        return False

    def use(self):
        self.last_use = Cooldown.current_time
    
class Obj:
    id = 0

    def __init__(self, image: pygame.surface, position: tuple = (-100, -100), velocity: tuple = (0, 0)) -> None:
        self.position = Coord(position)
        self.image = image
        self.velocity = Coord(velocity)

        self.id = Obj.id
        Obj.id += 1

        self.cooldowns = {}

    def give_coordinates_as_tuple(self) -> tuple:
        return self.position.give_coordinates()
    
    def move_by_specified_amount(self, amount: Coord):
        self.position += amount

    def change_velocity(self, amount: Coord):
        self.velocity += amount

    def set_velocity(self, velocity: Coord):
        self.velocity = velocity

    def move_at_velocity(self):
        self.position += self.velocity

    def turn_towards_point(self, pos_point: 'Coord'):
        # First translate self to origin to find the vector parallel to our target vector
        relative_pos = pos_point - self.position
        distance = Coord.distance_between(self.position, pos_point)
        sin = relative_pos.y / distance
        cos = relative_pos.x / distance
        mag_v = Coord.distance_between(self.velocity, Coord((0, 0)))
        self.velocity = Coord((mag_v * cos, mag_v * sin))
    
    def middle_of_image(self):
        coords = Coord.borders(self)
        x = (coords["x1"] + coords["x2"])/2
        y = (coords["y1"] + coords["y2"])/2
        return Coord((x, y))
    

class Character(Obj):
    def __init__(self, image, hp: int, position: tuple = (-100, -100), velocity: tuple = (0, 0)) -> None:
        super().__init__(image, position, velocity)
        self.hp = hp # Healthpoints
        self.set_cooldowns()

    def set_cooldowns(self):
        self.cooldowns = {
            "fire": Cooldown(500),
            "HP": Cooldown(500)
        } 

    def lose_hp(self, amount: int = 1):
        if self.cooldowns["HP"].is_on_cooldown():
            return
        self.hp -= amount
        self.cooldowns["HP"].use()

    def fire(self, target: Coord, image: pygame.Surface, velocity: Coord) -> 'Projectile':
        if self.cooldowns["fire"].is_on_cooldown():
            return "COOLDOWN"
        new_projectile = Projectile(image, position=self.middle_of_image(), velocity=velocity, parent_id=self.id)
        new_projectile.turn_towards_point(target)
        self.cooldowns["fire"].use()
        return new_projectile

class Projectile(Obj):
    def __init__(self, image, parent_id: int, position: tuple = (-100, -100), velocity: tuple = (0, 0), ) -> None:
        super().__init__(image, position, velocity)
        self.parent_id = parent_id # Shows who fired the bullet

class GameApp:
    def __init__(self) -> None:
        pygame.init()

        self.load_images()
        self.set_up_window()

        pygame.mouse.set_visible(False)
        pygame.display.set_caption("O shooting robot, a topdown game")

        self.new_game()
        self.clock = pygame.time.Clock()

        self.game_phases = {
            "main": self.game_screen,
            "end": self.end_screen
        } 

        self.game_loop()

    # INIT and MAIN GAME
    def game_loop(self):
        while True:
            self.game_phases[self.current_phase]()

    def game_screen(self):
        Cooldown.current_time = pygame.time.get_ticks()
        self.check_events()            
        self.player_move_according_to_flags()
        self.handle_monster_touch()
        self.all_monsters_fire()
        self.move_bullets()
        self.check_bullet_damage()
        self.look_for_0_hp()
        self.check_score()
        self.populate_monster_dict()
        self.draw_window()
    
    def end_screen(self):
        def middle_of_screen(image):
            half_window = (self.window_dimensions/2)
            x = half_window.x - image.get_width()/2
            y = half_window.y - image.get_height()/2
            return (x, y)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F5:
                    self.new_game()

        game_font = pygame.font.SysFont("Arial", 60)
        if self.score == self.target_score:          
            text = game_font.render("CONGRATULATIONS", True, (255, 0, 0))  
        else:
            text = game_font.render("Game Over", True, (255, 0, 0))
            
        x, y = middle_of_screen(text)
        self.window.blit(text, (x, y))            
        y += text.get_height()

        game_font = pygame.font.SysFont("Arial", 30)
        text = game_font.render(f"Your score: {self.score}", True, (255, 0, 0))
        x = middle_of_screen(text)[0]
        self.window.blit(text, (x, y))

        game_font = pygame.font.SysFont("Arial", 30)
        text = game_font.render(f"press F5 to restart", True, (255, 0, 0))
        self.window.blit(text, (0, 0))
        

        pygame.display.flip()

    def new_game(self):
        self.set_player_flags()
        self.set_player_keybindings()
        self.player_character = Character(self.images["robot"], hp=3, position=(30, 30), velocity=(1, 1))
        self.set_game_cooldowns()
        self.monsters = {} # id: monster
        self.max_monsters = 3
        self.bullets = {} # id: bullet
        self.gamespeed = 180
        self.score = 0
        self.cursorposition = (self.window_dimensions/2).give_coordinates()
        self.current_phase = "main"
        self.target_score = 20

    def load_images(self):
        image_names = ["monster", "robot"]
        self.images = {}
        for name in image_names:
            self.images[name] = pygame.image.load(name + ".png")

        game_font = pygame.font.SysFont("Arial", 12)
        self.images["bullet"] = game_font.render("o", True, (0, 255, 0))
         
    def set_up_window(self):
        self.window_dimensions = Coord((1280, 720))
        self.window = pygame.display.set_mode(self.window_dimensions.give_coordinates())
    
    def set_game_cooldowns(self):
        self.cooldowns = {
            "new monster": Cooldown(4000),
        }       

    # PLAYER and EVENTS
    def set_player_flags(self):
        self.player_flags = {
            "left": False,
            "right": False,
            "up": False,
            "down": False,
            "fire": False
        }

    def set_player_keybindings(self):
        self.player_keybindings = {
            "left": [pygame.K_a, pygame.K_LEFT],
            "right": [pygame.K_d, pygame.K_RIGHT],
            "up": [pygame.K_w, pygame.K_UP],
            "down": [pygame.K_s, pygame.K_DOWN],
        }

    def check_events(self):
        def change_keyboard_flag(names: list, state: bool):
            for name in names:
                if event.key in self.player_keybindings[name]:
                    self.player_flags[name] = state
                if event.key == pygame.K_F5:
                    self.new_game()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            
            keyboard_listen_for = ["left", "right", "up", "down"]
            if event.type == pygame.KEYDOWN:
                change_keyboard_flag(keyboard_listen_for, True)
            if event.type == pygame.KEYUP:
                change_keyboard_flag(keyboard_listen_for, False)            
            
            self.player_flags["fire"] = False
            mouse_status =  pygame.mouse.get_pressed()
            if mouse_status[0]: # left mouse
                self.player_flags["fire"] = True
                    

            if event.type == pygame.MOUSEMOTION:
                self.cursorposition = pygame.mouse.get_pos()

    def look_for_0_hp(self):
        if self.player_character.hp == 0:
            self.end_game()

        todel = []
        for monster in self.monsters.values():
            if monster.hp == 0:
                todel.append(monster.id)
                self.score += 1
        
        for id in todel:
            del self.monsters[id]

    def check_score(self):
        if self.score == self.target_score:
            self.current_phase = "end"

    def end_game(self):
        self.current_phase = "end"

    def player_move_according_to_flags(self):
        vel = 1

        if self.player_flags["left"]:
            self.move_player((-vel, 0))
        
        if self.player_flags["right"]:
            self.move_player((vel, 0))

        if self.player_flags["up"]:
            self.move_player((0, -vel))

        if self.player_flags["down"]:
            self.move_player((0, vel))

        if self.player_flags["fire"]:
            self.fire(self.cursorposition, self.player_character, speed=2)
   
    def move_player(self, amount: tuple):
        c_amount = Coord(amount)
        if self.check_wall_collision(self.player_character, c_amount):
            return
        else:
            self.player_character.move_by_specified_amount(c_amount)

    def handle_monster_touch(self):
        toremove = []
        for id, monster in self.monsters.items():            
            if Coord.detect_collision(self.player_character, monster):
                self.player_character.lose_hp()
                toremove.append(id)
            
        for i in toremove:
            del self.monsters[i]

    # MONSTER
    def populate_monster_dict(self):
        if len(self.monsters) >= self.max_monsters or self.cooldowns["new monster"].is_on_cooldown():
            return
        
        def get_new_coord():
            return Coord((
                random.randint(0, self.window_dimensions.x - self.images["monster"].get_width()) , 
                random.randint(0, self.window_dimensions.y - self.images["monster"].get_height())
                ))
        new_coord = get_new_coord()
        while Coord.within_radius_of(100, self.player_character, new_coord):
            new_coord = get_new_coord()
        
        new_monster = Character(self.images["monster"], hp=3, position=new_coord.give_coordinates())
        self.monsters[new_monster.id] = new_monster
        self.cooldowns["new monster"].use()

    def all_monsters_fire(self):
        for monster in self.monsters.values():
            self.fire(self.player_character.give_coordinates_as_tuple(), monster)

    # Bullets
    def move_bullets(self):
        to_delete = []
        for id, bullet in self.bullets.items():
            bullet.move_at_velocity()

            if self.check_wall_collision(bullet, amount=Coord((0,0))):
                # Delete if not in window
                to_delete.append(id)

        for id in to_delete:
            del self.bullets[id]
        
    def fire(self, target: tuple, actor: Character, speed: float=1):
        new_bullet = actor.fire(Coord(target), self.images["bullet"], Coord((speed, 0)))
        if type(new_bullet) == str:
            pass
        else:
            self.bullets[new_bullet.id] = new_bullet    

    def check_bullet_damage(self):
        todel = []
        all_characters = [i for i in self.monsters.values()]
        all_characters.append(self.player_character)

        for bullet in self.bullets.values():
            for character in all_characters:
                if character.id == bullet.parent_id:
                    continue
                if Coord.detect_collision(bullet, character):
                    character.lose_hp()
                    todel.append(bullet.id)

        for i in todel:
            del self.bullets[i]
                
    # HELPER
    def check_wall_collision(self, object: Obj, amount: Coord):
        obj_border = Coord.borders(object)
        if obj_border["x1"] + amount.x < 0 or obj_border["y1"] + amount.y < 0 or obj_border["x2"] + amount.x > self.window_dimensions.x or obj_border["y2"] + amount.y > self.window_dimensions.y:
            return True
        return False

    # DRAW    
    def draw_window(self):
        self.window.fill((100, 100, 100))

        self.draw_object(self.player_character)
        for monster in self.monsters.values():
            self.draw_object(monster)

        for bullet in self.bullets.values():
            self.draw_object(bullet)
        self.draw_cursor()
        self.draw_top_right_corner()

        pygame.display.flip()
        self.clock.tick(self.gamespeed)

    def draw_cursor(self):
        pygame.draw.circle(self.window, (255, 0, 0), self.cursorposition, 3)
        pygame.draw.circle(self.window, (255, 0, 0), self.cursorposition, 20, 1)

    def draw_object(self, object: Obj):
        self.window.blit(object.image, object.give_coordinates_as_tuple())

    def draw_top_right_corner(self):
        game_font = pygame.font.SysFont("Arial", 24)
        texts = [
            game_font.render(f"Score: {self.score} / {self.target_score}", True, (255, 0, 0)),
            game_font.render(f"HP: {self.player_character.hp}", True, (255, 0, 0)),
        ]

        y = 0
        for t in texts:
            self.window.blit(t, (self.window_dimensions.x - t.get_width(), y))
            y += t.get_height()

app = GameApp()


