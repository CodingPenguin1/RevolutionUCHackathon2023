import pyglet
from pyglet.window import key

from math import sin, cos, radians, degrees

from network import Network, Node, load_network_from_file
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

        self.team = team
        
        self.wraps = wraps  # Does the object wrap around when it hits the edge of the screen
        if self.velocity is None:
            self.velocity = [0, 0]
        self.dead = False
    
    def update(self, dt):
        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt
        
        self.check_bounds()

    def check_bounds(self):
        min_x = -self.image.width / 2
        min_y = -self.image.height / 2
        max_x = 1690 + self.image.width / 2
        max_y = 950 + self.image.height / 2
        if self.x < min_x:
            if (not self.wraps):
                self.die(0)
            self.x = max_x
        elif self.x > max_x:
            if (not self.wraps):
                self.die(0)
            self.x = min_x
        if self.y < min_y:
            if (not self.wraps):
                self.die(0)
            self.y = max_y
        elif self.y > max_y:
            if (not self.wraps):
                self.die(0)
            self.y = min_y
    
    def collides_with(self, other_object):
        # Friendly fire off
        if (self.team == other_object.team):
            return False

        self_rect = util.define_rect(self.x, self.y, self.image.width, self.image.height, self.rotation)
        obj_rect = util.define_rect(other_object.x, other_object.y, other_object.image.width, other_object.image.height, other_object.rotation)
        collision = util.rects_overlap(self_rect, obj_rect)

        return collision

    def handle_collision_with(self, other_object):
        # TODO: this is where we do damage
        self.die(0)

    def die(self, dt):
        self.dead = True


class Ship(PhysicalObject):
    def __init__(self, name, image, batch, x=0, y=0, ship_properties=None, team=0, ai_filepath=None):
        super().__init__(image, batch=batch, x=x, y=y, wraps=True, team=team)
        # Properties of the ship
        self.name = name
        if ship_properties is None:
            self.ship_properties = {
                'thrust': 100,
                'max_speed': 10,
                'turn_speed': 50,
                'weapons': ['laser'],
                'bullet_speed': 700.0,
                'fire_rate': 25,  # How many physics updates between shots
            }
        
        if ai_filepath is not None:
            self.brain = load_network_from_file(ai_filepath)
        else:
            self.brain = Network(2, 4)  # (distance, angle), (right, left, thrust, fire)
            # self.brain.add_node(Node(0, 1, 5))
            # self.brain.add_node(Node(0, 1, 1))
            # self.brain.add_node(Node(1, 1, 'abs'), [1])
            # self.brain.add_node(Node(2, 1, '>'), [8, 7])
            # self.brain.add_node(Node(2, 1, '>='), [6, 0])
            # self.brain.add_node(Node(2, 1, 'and'), [9, 10], [5])
            # self.brain.add_node(Node(0, 1, -1))
            # self.brain.add_node(Node(2, 1, '<'), [1, 12], [3])
            # self.brain.add_node(Node(2, 1, '>'), [1, 7], [2])
        
        self.object_locations = []  # The data of all objects {type, x, y, rotation, velocity}
        
        self.keys = {
                    'left': False,
                    'right': False,
                    'up': False,
                    'space': False
                    }
    
        self.ai_actions = {
                    'left': False,
                    'right': False,
                    'up': False,
                    'space': False,
                    'updates_since_last_shot': 0
        }

    def update(self, dt):
        # Physics update
        super().update(dt)
        
        # === AI Update ===
        if self.name == 'wallhacks':
            # Calculate inputs
            inputs = []  # Inputs for the network
            for obj in self.object_locations:
                if obj['type'] == Ship:
                    # If ship is not me
                    if util.distance((self.x, self.y), (obj['x'], obj['y'])) > 2:
                        # Angle between heading of me and the enemy ship
                        heading_vector = (-cos(radians(self.rotation)), sin(radians(self.rotation)))
                        position_vector = (self.x - obj['x'], self.y - obj['y'])
                        angle = degrees(util.angle(heading_vector, position_vector)) % 360
                        
                        # Check which side the enemy is on by checking rotation - 1 degree
                        test_rotation = self.rotation - 1
                        heading_vector = (-cos(radians(test_rotation)), sin(radians(test_rotation)))
                        position_vector = (self.x - obj['x'], self.y - obj['y'])
                        test_angle = degrees(util.angle(heading_vector, position_vector)) % 360
                        
                        # If the test angle is less than the actual angle, then the enemy is on the left
                        if test_angle < angle:
                            angle = -angle
                        
                        # Distance between me and the enemy ship
                        distance = util.distance((self.x, self.y), (obj['x'], obj['y']))
                        inputs = [distance, angle]
            
            # Use brain to get outputs
            self.brain.reset()
            print('INPUT', inputs)
            if len(inputs) > 0:
                outputs = self.brain.parse_network(inputs)  # right, left, thrust, fire
                print('OUTPUT', outputs)
                
                # Parse outputs into "keystrokes"
                self.ai_actions['right'] = bool(outputs[0])
                self.ai_actions['left'] = bool(outputs[1])
                self.ai_actions['up'] = bool(outputs[2])
                self.ai_actions['space'] = bool(outputs[3])
        
        # === Perform Actions ===
        if self.keys['left'] or self.ai_actions['left']:
            self.turn('left', dt)
        if self.keys['right'] or self.ai_actions['right']:
            self.turn('right', dt)
        if self.keys['up'] or self.ai_actions['up']:
            self.accelerate(dt)
        if self.keys['space']:
            self.fire(self.team)
            self.keys['space'] = False

        # If AI attempts to fire and can fire
        if self.ai_actions['space'] and self.ai_actions['updates_since_last_shot'] > self.ship_properties['fire_rate']:
            self.fire(self.team)
            self.ai_actions['updates_since_last_shot'] = 0
        else:
            self.ai_actions['updates_since_last_shot'] += 1

    def fire(self, team=0):
        # Calculate projectile position, rotation and instantiate
        angle_radians = -radians(self.rotation)
        ship_radius = self.image.width / 2
        bullet_x = self.x + cos(angle_radians) * ship_radius
        bullet_y = self.y + sin(angle_radians) * ship_radius
        bullet_image = pyglet.resource.image("ShotRegular/blueShot.png")
        new_bullet = Projectile(image=bullet_image, batch=self.batch, x=bullet_x, y=bullet_y, team=team)
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
            self.keys['space'] = True

    def on_key_release(self, symbol, modifiers):
        if symbol == key.UP:
            self.keys['up'] = False
        elif symbol == key.LEFT:
            self.keys['left'] = False
        elif symbol == key.RIGHT:
            self.keys['right'] = False
        elif symbol == key.SPACE:
            self.keys['space'] = False


class Projectile(PhysicalObject):
    def __init__(self, image, batch, x=0, y=0, team=0):
        super().__init__(image, batch=batch, x=x, y=y, wraps=False, team=team)
        
        self.scale = 0.5