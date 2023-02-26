import pyglet
from objects import Ship
import menu as menuUI

pyglet.resource.path = ['../Sprites']
pyglet.resource.reindex()

window = pyglet.window.Window(1690, 950, resizable=True)
window.set_minimum_size(640, 360)

game_objects = []
to_add = []
ship_batch = pyglet.graphics.Batch()

menu = menuUI.mainMenu(window)
inMenu = True


@window.event
def on_draw():
    if (inMenu):
        window.clear()
        menu.redraw()
    else:
        window.clear()
        background = pyglet.sprite.Sprite(x=0, y=0, img=pyglet.resource.image("UI/background.png"))
        background.update(scale=1.5)
        background.draw()
        ship_batch.draw()

    if (ship.dead):
        deadText = pyglet.text.Label('You Died',
                font_name='Times New Roman',
                font_size=36,
                x=window.width//2, y=window.height//2,
                anchor_x='center', anchor_y='center')
        deadText.draw()
        pyglet.clock.schedule_once(QuitGame, 5)

    if (ship2.dead):
        winText = pyglet.text.Label('You Win',
                font_name='Times New Roman',
                font_size=36,
                x=window.width//2, y=window.height//2,
                anchor_x='center', anchor_y='center')
        winText.draw()
        pyglet.clock.schedule_once(QuitGame, 5)

def QuitGame():
    print("QUITTING")
    pyglet.app.exit()

@window.event
def on_mouse_press(x, y, button, modifiers):
    menuButtons = menu.getButtons()
    for button in menuButtons:
        spriteX = button.getX()
        spriteY = button.getY()
        image_width = button.getWidth()
        image_height = button.getHeight()
        if spriteX + image_width > x and spriteY + image_height > y and spriteX - image_width < x and spriteY - image_height < y:
            global inMenu
            inMenu = button.trigger()


def update(dt):
    global inMenu #, started

    if (not inMenu):
        # Remove dead objects
        for to_remove in [obj for obj in game_objects if obj.dead]:
            to_remove.delete()
            game_objects.remove(to_remove)
        
        # Physics update and adds new objects
        object_positions = []
        for obj in game_objects:
            obj.update(dt)
            to_add.extend(obj.new_objects)
            obj.new_objects = []

            # Retrieves all object locations
            obj_info = {'type': type(obj),
                        'x': obj.x,
                        'y': obj.y,
                        'angle': obj.rotation,
                        'velocity': obj.velocity
                        }
            object_positions.append(obj_info)
        
        # Broadcast all object locations to all ships
        for obj in game_objects:
            if type(obj) == Ship:
                obj.object_locations = object_positions
        
        # Collision checks
        for i in range(len(game_objects)):
            for j in range(i + 1, len(game_objects)):
                obj_1 = game_objects[i]
                obj_2 = game_objects[j]

                if not obj_1.dead and not obj_2.dead:
                    if obj_1.collides_with(obj_2):
                        obj_1.handle_collision_with(obj_2)
                        obj_2.handle_collision_with(obj_1)

        # Last
        game_objects.extend(to_add)
        to_add.clear()
    

if __name__ == '__main__':
    ship_image = pyglet.resource.image("ship2.png")
    ai_ship_image = pyglet.resource.image("ship3.png")

    ship = Ship(name='billy bob', image=ship_image, batch=ship_batch, x=200, y=450, team=0)

    ai_ship_properties = {
            'thrust': 100,
            'max_speed': 10,
            'turn_speed': 50,
            'weapons': ['laser'],
            'bullet_speed': 700.0,
            'fire_rate': 25,  # How many physics updates between shots
            'bullet_image_file': "redShot.png"
    }

    ship2 = Ship(name='wallhacks', image=ai_ship_image, batch=ship_batch, x=1400, y=550, team=1, ai_filepath='graph.pkl', ship_properties=ai_ship_properties)
    
    game_objects = [ship, ship2]

    window.push_handlers(ship)

    pyglet.clock.schedule_interval(update, 1/120.0)
    
    pyglet.app.run()
