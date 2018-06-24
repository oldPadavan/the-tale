
import smart_imports

smart_imports.all()


class META_TERRAIN(rels_django.DjangoEnum):
    records = (('WATER', 0, 'вода'),
               ('MOUNTAINS', 1, 'горы'),
               ('DESERT', 2, 'пустыня'),
               ('SWAMP', 3, 'болото'),
               ('NORMAL', 4, 'зелень'),
               ('JUNGLE', 5, 'джунгли'))


class META_HEIGHT(rels_django.DjangoEnum):
    records = (('WATER', 0, 'вода'),
               ('PLAINS', 1, 'равнины'),
               ('HILLS', 2, 'холмы'),
               ('MOUNTAINS', 3, 'горы'))


class META_VEGETATION(rels_django.DjangoEnum):
    records = (('NONE', 0, 'нет растительности'),
               ('GRASS', 1, 'трава'),
               ('TREES', 2, 'деревья'))


class TERRAIN(rels_django.DjangoEnum):
    meta_height = rels.Column(unique=False, primary=False)
    meta_terrain = rels.Column(unique=False, primary=False)
    meta_vegetation = rels.Column(unique=False, primary=False)

    records = (('WATER_DEEP',            0, 'глубокая вода',                   META_HEIGHT.WATER, META_TERRAIN.WATER, META_VEGETATION.NONE),
               ('WATER_SHOAL',           1, 'мелкая вода',                     META_HEIGHT.WATER, META_TERRAIN.WATER, META_VEGETATION.NONE),
               ('MOUNTAINS_HIGH',        2, 'высокие горы',                    META_HEIGHT.MOUNTAINS, META_TERRAIN.MOUNTAINS, META_VEGETATION.NONE),
               ('MOUNTAINS_LOW',         3, 'низкие горы',                     META_HEIGHT.MOUNTAINS, META_TERRAIN.MOUNTAINS, META_VEGETATION.NONE),

               ('PLANE_SAND',            4, 'пустыня',                         META_HEIGHT.PLAINS, META_TERRAIN.DESERT, META_VEGETATION.NONE),
               ('PLANE_DRY_LAND',        5, 'высохшая растрескавшаяся земля',  META_HEIGHT.PLAINS, META_TERRAIN.DESERT, META_VEGETATION.NONE),
               ('PLANE_MUD',             6, 'грязь',                           META_HEIGHT.PLAINS, META_TERRAIN.SWAMP, META_VEGETATION.NONE),
               ('PLANE_DRY_GRASS',       7, 'сухие луга',                      META_HEIGHT.PLAINS, META_TERRAIN.NORMAL, META_VEGETATION.GRASS),
               ('PLANE_GRASS',           8, 'луга',                            META_HEIGHT.PLAINS, META_TERRAIN.NORMAL, META_VEGETATION.GRASS),
               ('PLANE_SWAMP_GRASS',     9, 'болото',                          META_HEIGHT.PLAINS, META_TERRAIN.SWAMP, META_VEGETATION.GRASS),
               ('PLANE_CONIFER_FOREST',  10, 'хвойный лес',                    META_HEIGHT.PLAINS, META_TERRAIN.NORMAL, META_VEGETATION.TREES),
               ('PLANE_GREENWOOD',       11, 'лиственный лес',                 META_HEIGHT.PLAINS, META_TERRAIN.NORMAL, META_VEGETATION.TREES),
               ('PLANE_SWAMP_FOREST',    12, 'заболоченный лес',               META_HEIGHT.PLAINS, META_TERRAIN.SWAMP, META_VEGETATION.TREES),
               ('PLANE_JUNGLE',          13, 'джунгли',                        META_HEIGHT.PLAINS, META_TERRAIN.JUNGLE, META_VEGETATION.TREES),
               ('PLANE_WITHERED_FOREST', 14, 'мёртвый лес',                    META_HEIGHT.PLAINS, META_TERRAIN.DESERT, META_VEGETATION.TREES),

               ('HILLS_SAND',            15, 'песчаные дюны',                  META_HEIGHT.HILLS, META_TERRAIN.DESERT, META_VEGETATION.NONE),
               ('HILLS_DRY_LAND',        16, 'высохшие растрескавшиеся холмы', META_HEIGHT.HILLS, META_TERRAIN.DESERT, META_VEGETATION.NONE),
               ('HILLS_MUD',             17, 'грязевые холмы',                 META_HEIGHT.HILLS, META_TERRAIN.SWAMP, META_VEGETATION.NONE),
               ('HILLS_DRY_GRASS',       18, 'холмы с высохшей травой',        META_HEIGHT.HILLS, META_TERRAIN.NORMAL, META_VEGETATION.GRASS),
               ('HILLS_GRASS',           19, 'зелёные холмы',                  META_HEIGHT.HILLS, META_TERRAIN.NORMAL, META_VEGETATION.GRASS),
               ('HILLS_SWAMP_GRASS',     20, 'заболоченные холмы',             META_HEIGHT.HILLS, META_TERRAIN.SWAMP, META_VEGETATION.GRASS),
               ('HILLS_CONIFER_FOREST',  21, 'хвойный лес на холмах',          META_HEIGHT.HILLS, META_TERRAIN.NORMAL, META_VEGETATION.TREES),
               ('HILLS_GREENWOOD',       22, 'лиственный лес на холмах',       META_HEIGHT.HILLS, META_TERRAIN.NORMAL, META_VEGETATION.TREES),
               ('HILLS_SWAMP_FOREST',    23, 'заболоченный лес на холмах',     META_HEIGHT.HILLS, META_TERRAIN.SWAMP, META_VEGETATION.TREES),
               ('HILLS_JUNGLE',          24, 'джунгли на холмах',              META_HEIGHT.HILLS, META_TERRAIN.JUNGLE, META_VEGETATION.TREES),
               ('HILLS_WITHERED_FOREST', 25, 'мёртвый лес на холмах',          META_HEIGHT.HILLS, META_TERRAIN.DESERT, META_VEGETATION.TREES))


class MAP_STATISTICS(rels_django.DjangoEnum):
    records = (('LOWLANDS', 0, 'низины'),
               ('PLAINS', 1, 'равнины'),
               ('UPLANDS', 2, 'возвышенности'),
               ('DESERTS', 3, 'пустыни'),
               ('GRASS', 4, 'луга'),
               ('FORESTS', 5, 'леса'))


_SPRITE_ID = -1


def sprite(name, x=0, y=0, base=None):
    global _SPRITE_ID
    _SPRITE_ID += 1

    if base is None:
        base = name

    return (name, _SPRITE_ID, name, x * conf.map_settings.CELL_SIZE, y * conf.map_settings.CELL_SIZE, base)


class SPRITES(rels_django.DjangoEnum):
    x = rels.Column(unique=False, primary=False)
    y = rels.Column(unique=False, primary=False)
    base = rels.Column(unique=False, primary=False, single_type=False)

    records = (
        # Heroes (neutral gender equal to male)
        sprite('HERO_HUMAN_MALE',       x=0, y=8),
        sprite('HERO_HUMAN_FEMALE',     x=1, y=8),
        sprite('HERO_DWARF_MALE',       x=2, y=8),
        sprite('HERO_DWARF_FEMALE',     x=3, y=8),
        sprite('HERO_ELF_MALE',         x=4, y=8),
        sprite('HERO_ELF_FEMALE',       x=5, y=8),
        sprite('HERO_GOBLIN_MALE',      x=6, y=8),
        sprite('HERO_GOBLIN_FEMALE',    x=7, y=8),
        sprite('HERO_ORC_MALE',         x=8, y=8),
        sprite('HERO_ORC_FEMALE',       x=9, y=8),

        sprite('HERO_HUMAN_NEUTER',     x=0, y=8),
        sprite('HERO_DWARF_NEUTER',     x=2, y=8),
        sprite('HERO_ELF_NEUTER',       x=4, y=8),
        sprite('HERO_GOBLIN_NEUTER',    x=6, y=8),
        sprite('HERO_ORC_NEUTER',       x=8, y=8),

        # Terrain
        sprite('WATER_DEEP',            y=2, x=4),
        sprite('WATER_SHOAL',           y=2, x=3),
        sprite('MOUNTAINS_HIGH',        y=2, x=1, base='MOUNTAINS_BACKGROUND'),
        sprite('MOUNTAINS_LOW',         y=2, x=0, base='MOUNTAINS_BACKGROUND'),
        sprite('PLANE_SAND',            y=0, x=1),
        sprite('PLANE_DRY_LAND',        y=0, x=3),
        sprite('PLANE_MUD',             y=0, x=4),
        sprite('PLANE_DRY_GRASS',       y=0, x=5),
        sprite('PLANE_GRASS',           y=0, x=0),
        sprite('PLANE_SWAMP_GRASS',     y=0, x=2),
        sprite('PLANE_CONIFER_FOREST',  y=1, x=0, base='PLANE_CONIFER_GRASS'),
        sprite('PLANE_GREENWOOD',       y=1, x=1, base='PLANE_GRASS'),
        sprite('PLANE_SWAMP_FOREST',    y=1, x=2, base='PLANE_SWAMP_GRASS'),
        sprite('PLANE_JUNGLE',          y=1, x=3, base='JUNGLE_BACKGROUD'),
        sprite('PLANE_WITHERED_FOREST', y=2, x=5, base='PLANE_DRY_GRASS'),
        sprite('HILLS_SAND',            y=0, x=7, base='PLANE_SAND'),
        sprite('HILLS_DRY_LAND',        y=0, x=11, base='PLANE_DRY_LAND'),
        sprite('HILLS_MUD',             y=0, x=10, base='PLANE_MUD'),
        sprite('HILLS_DRY_GRASS',       y=0, x=9, base='PLANE_DRY_GRASS'),
        sprite('HILLS_GRASS',           y=0, x=6, base='PLANE_GRASS'),
        sprite('HILLS_SWAMP_GRASS',     y=0, x=8, base='PLANE_SWAMP_GRASS'),
        sprite('HILLS_CONIFER_FOREST',  y=1, x=6, base='PLANE_CONIFER_GRASS'),
        sprite('HILLS_GREENWOOD',       y=1, x=7, base='PLANE_GRASS'),
        sprite('HILLS_SWAMP_FOREST',    y=1, x=8, base='PLANE_SWAMP_GRASS'),
        sprite('HILLS_JUNGLE',          y=1, x=9, base='JUNGLE_BACKGROUD'),
        sprite('HILLS_WITHERED_FOREST', y=2, x=6, base='PLANE_DRY_GRASS'),
        sprite('PLANE_CONIFER_GRASS',   y=2, x=7),

        sprite('MOUNTAINS_BACKGROUND',  y=2, x=2),
        sprite('JUNGLE_BACKGROUD',      y=1, x=11),

        # Cities
        sprite('CITY_HUMAN_SMALL',     y=6, x=0),
        sprite('CITY_HUMAN_MEDIUM',    y=6, x=1),
        sprite('CITY_HUMAN_LARGE',     y=6, x=2),
        sprite('CITY_HUMAN_CAPITAL',   y=6, x=3),

        sprite('CITY_DWARF_SMALL',     y=6, x=4),
        sprite('CITY_DWARF_MEDIUM',    y=6, x=5),
        sprite('CITY_DWARF_LARGE',     y=6, x=6),
        sprite('CITY_DWARF_CAPITAL',   y=6, x=7),

        sprite('CITY_ELF_SMALL',     y=6, x=8),
        sprite('CITY_ELF_MEDIUM',    y=6, x=9),
        sprite('CITY_ELF_LARGE',     y=6, x=10),
        sprite('CITY_ELF_CAPITAL',   y=6, x=11),

        sprite('CITY_GOBLIN_SMALL',     y=7, x=0),
        sprite('CITY_GOBLIN_MEDIUM',    y=7, x=1),
        sprite('CITY_GOBLIN_LARGE',     y=7, x=2),
        sprite('CITY_GOBLIN_CAPITAL',   y=7, x=3),

        sprite('CITY_ORC_SMALL',     y=7, x=4),
        sprite('CITY_ORC_MEDIUM',    y=7, x=5),
        sprite('CITY_ORC_LARGE',     y=7, x=6),
        sprite('CITY_ORC_CAPITAL',   y=7, x=7),

        # Roads
        sprite('R4',        x=3, y=3),
        sprite('R3',        x=1, y=3),
        sprite('R_VERT',    x=5, y=3),
        sprite('R_HORIZ',   x=2, y=3),
        sprite('R_ANGLE',   x=4, y=3),
        sprite('R1',        x=0, y=3),

        # cursors
        sprite('SELECT_LAND',         x=0, y=9),
        sprite('CELL_HIGHLIGHTING',   x=1, y=9),

        # buildings
        sprite('BUILDING_SAWMILL',        y=4, x=0),
        sprite('BUILDING_WATCHTOWER',     y=4, x=1),
        sprite('BUILDING_MAGE_TOWER',     y=4, x=2),
        sprite('BUILDING_SCAFFOLD',       y=4, x=3),
        sprite('BUILDING_RANCH',          y=4, x=4),
        sprite('BUILDING_SMITHY',         y=4, x=5),
        sprite('BUILDING_HUNTER_HOUSE',   y=4, x=6),
        sprite('BUILDING_FISHING_LODGE',  y=4, x=7),
        sprite('BUILDING_TRADING_POST',   y=4, x=8),
        sprite('BUILDING_INN',            y=4, x=9),
        sprite('BUILDING_FARM',           y=4, x=10),
        sprite('BUILDING_MINE',           y=4, x=11),
        sprite('BUILDING_TEMPLE',         y=5, x=0),
        sprite('BUILDING_LABORATORY',     y=5, x=1),
        sprite('BUILDING_HOSPITAL',       y=5, x=2),
        sprite('BUILDING_MANOR',          y=5, x=3),
        sprite('BUILDING_DEN_OF_THIEVE',  y=5, x=4),
        sprite('BUILDING_GUILDHALL',      y=5, x=5),
        sprite('BUILDING_MEWS',           y=5, x=6),
        sprite('BUILDING_SCENE',          y=5, x=7),
        sprite('BUILDING_TAILOR_SHOP',    y=5, x=8),
        sprite('BUILDING_BUREAU',         y=5, x=9))
