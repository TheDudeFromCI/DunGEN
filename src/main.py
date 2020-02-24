from generator.dungeon import gen_map
from paint.painter import create_layered_image

if __name__ == '__main__':
    dungeon = gen_map()
    dungeon.name = 'The Sewers'
    dungeon.index = 2

    create_layered_image(dungeon)
