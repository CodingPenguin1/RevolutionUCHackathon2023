import pyglet
from objects import Ship, Projectile


pyglet.resource.path = ['../Sprites']
pyglet.resource.reindex()

window = pyglet.window.Window(1280, 720, resizable=True)
window.set_minimum_size(640, 360)
#window.set_maximum_size(1000, 1000)

game_objects = []
to_add = []
ship_batch = pyglet.graphics.Batch()


@window.event
def on_draw():
    window.clear()
    ship_batch.draw()


def update(dt):
    for obj in game_objects:
        obj.update(dt)
        to_add.extend(obj.new_objects)
        obj.new_objects = []

    # Collision checks
    for i in range(len(game_objects)):
        for j in range(i + 1, len(game_objects)):
            obj_1 = game_objects[i]
            obj_2 = game_objects[j]

            if not obj_1.dead and not obj_2.dead:
                if obj_1.collides_with(obj_2):
                    obj_1.handle_collision_with(obj_2)
                    obj_2.handle_collision_with(obj_1)

    # Remove dead objects
    for to_remove in [obj for obj in game_objects if obj.dead]:
        to_remove.delete()
        game_objects.remove(to_remove)

    # TODO: If player ship dies, display death UI and disable input
    if (ship.dead):
        print("YOU DIED")
        exit()

    # Last
    game_objects.extend(to_add)
    to_add.clear()


if __name__ == '__main__':
    ship_image = pyglet.resource.image("ship2.png")
    bullet_image = pyglet.resource.image("ShotRegular/blueShot.png")  # TODO: Load all sprites at launch
    exhaust_image = pyglet.resource.image("Exhaust/exhaust4.png")

    exhaust_image.anchor_x = exhaust_image.width * 1.5
    exhaust_image.anchor_y = exhaust_image.height / 2

    ship = Ship(image=ship_image, batch=ship_batch, team=0)
    ship2 = Ship(image=ship_image, batch=ship_batch, x=300, y=300, team=1)
    
    game_objects = [ship, ship2]

    window.push_handlers(ship)

    pyglet.clock.schedule_interval(update, 1/120.0)
    
    pyglet.app.run()