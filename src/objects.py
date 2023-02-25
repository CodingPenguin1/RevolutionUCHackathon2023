import pyglet
from pyglet.window import key

from math import sin, cos, radians

import util


class PhysicalObject(pyglet.sprite.Sprite):
    def __init__(self, image, batch, x=0, y=0, velocity=None, wraps=False, team=0):
        # Anchor image to center and set up sprite super class
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2
        super().__init__(image, batch=batch)
        
        self.x = x
        self.y = y
        self.velocity = velocity
        self.new_objects = []
        self.reacts_to_bullets = True
        self.is_bullet = False

        self.team = team
        
        self.wraps = wraps  # Does the object wrap around when it hits the edge of the screen
        if self.velocity is None:
            self.velocity = [0, 0]
        self.dead = False
    
    def update(self, dt):
        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt
        
        if (self.wraps):
            self.check_bounds()

    def check_bounds(self):
        min_x = -self.image.width / 2
        min_y = -self.image.height / 2
        max_x = 1280 + self.image.width / 2
        max_y = 720 + self.image.height / 2
        if self.x < min_x:
            self.x = max_x
        elif self.x > max_x:
            self.x = min_x
        if self.y < min_y:
            self.y = max_y
        elif self.y > max_y:
            self.y = min_y
    
    def collides_with(self, other_object):
        # Friendly fire off
        if (self.team == other_object.team):
            return False
        # if not self.reacts_to_bullets and other_object.is_bullet:
        #     return False
        # if self.is_bullet and not other_object.reacts_to_bullets:
        #     return False

        self_rect = util.define_rect(self.x, self.y, self.image.width, self.image.height, self.rotation)
        obj_rect = util.define_rect(other_object.x, other_object.y, other_object.image.width, other_object.image.height, other_object.rotation)
        collision = util.rects_overlap(self_rect, obj_rect)
        if collision:
            print('Collision detected!')
        return collision

    def handle_collision_with(self, other_object):
        # TODO: this is where we do damage
        self.dead = True

    def die(self, dt):
        self.dead = True

    def handle_collision_with(self, other_object):
        if other_object.__class__ == self.__class__:
            self.dead = False
        else:
            self.dead = True


class Ship(PhysicalObject):
    def __init__(self, image, batch, x=0, y=0, ship_properties=None, team=0):
        super().__init__(image, batch=batch, x=x, y=y, wraps=True, team=team)
        
        # Properties of the ship
        if ship_properties is None:
            self.ship_properties = {
                'thrust': 100,
                'max_speed': 10,
                'turn_speed': 50,
                'weapons': ['laser'],
                'bullet_speed': 700.0
            }

        self.reacts_to_bullets = False
        
        # TODO: this whole thing
        self.brain = None
        
        self.keys = {
                    'left': False,
                    'right': False,
                    'up': False
                    }

    def update(self, dt):
        super().update(dt)
        
        if self.keys['left']:
            self.turn('left', dt)
        elif self.keys['right']:
            self.turn('right', dt)
        elif self.keys['up']:
            self.accelerate(dt)

    def fire(self):
        # Calculate projectile position and instantiate
        angle_radians = -radians(self.rotation)
        ship_radius = self.image.width / 2
        bullet_x = self.x + cos(angle_radians) * ship_radius
        bullet_y = self.y + sin(angle_radians) * ship_radius
        bullet_image = pyglet.resource.image("ShotRegular/blueShot.png")
        new_bullet = Projectile(image=bullet_image, batch=self.batch, x=bullet_x, y=bullet_y, team=0)
        new_bullet.rotation = self.rotation

        # Set projectile velocity
        bullet_vx = ( self.velocity[0] + cos(angle_radians) * self.ship_properties['bullet_speed'] )
        bullet_vy = ( self.velocity[1] + sin(angle_radians) * self.ship_properties['bullet_speed'] )
        new_bullet.velocity[0] = bullet_vx
        new_bullet.velocity[1] = bullet_vy

        # Add to new game objects list
        self.new_objects.append(new_bullet)

    def accelerate(self, dt):
        # Update the velocity based on the direction
        angle_radians = -radians(self.rotation)
        dv_x = self.ship_properties['thrust'] * cos(angle_radians) * dt
        dv_y = self.ship_properties['thrust'] * sin(angle_radians) * dt
        self.velocity[0] += dv_x
        self.velocity[1] += dv_y
    
    def turn(self, turn_direction, dt):
        if turn_direction == 'left':
            self.rotation = self.rotation - self.ship_properties['turn_speed'] * dt
        elif turn_direction == 'right':
            self.rotation = self.rotation + self.ship_properties['turn_speed'] * dt

    def on_key_press(self, symbol, modifiers):
        if symbol == key.UP:
            self.keys['up'] = True
        elif symbol == key.LEFT:
            self.keys['left'] = True
        elif symbol == key.RIGHT:
            self.keys['right'] = True
        elif symbol == key.SPACE:
            self.fire()

    def on_key_release(self, symbol, modifiers):
        if symbol == key.UP:
            self.keys['up'] = False
        elif symbol == key.LEFT:
            self.keys['left'] = False
        elif symbol == key.RIGHT:
            self.keys['right'] = False


class Projectile(PhysicalObject):
    def __init__(self, image, batch, x=0, y=0, team=0):
        super().__init__(image, batch=batch, x=x, y=y, wraps=False, team=team)
        pyglet.clock.schedule_once(self.die, 0.5)
        
        self.is_bullet = True
        self.reacts_to_bullets = False
        self.scale = 0.5