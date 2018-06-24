
import smart_imports

smart_imports.all()


def create_test_map_info():
    storage.map_info_storage.set_item(prototypes.MapInfoPrototype.create(turn_number=0,
                                                      width=conf.map_settings.WIDTH,
                                                      height=conf.map_settings.HEIGHT,
                                                      terrain=[ [relations.TERRAIN.PLANE_GREENWOOD for j in range(conf.map_settings.WIDTH)] for i in range(conf.map_settings.HEIGHT)], # pylint: disable=W0612
                                                      world=prototypes.WorldInfoPrototype.create(w=conf.map_settings.WIDTH, h=conf.map_settings.HEIGHT)))


_TERRAIN_LINGUISTICS_CACHE = {}

def get_terrain_linguistics_restrictions(terrain):

    if _TERRAIN_LINGUISTICS_CACHE:
        return _TERRAIN_LINGUISTICS_CACHE[terrain]

    for terrain_record in relations.TERRAIN.records:
        _TERRAIN_LINGUISTICS_CACHE[terrain_record] = ( linguistics_storage.restrictions_storage.get_restriction(linguistics_relations.TEMPLATE_RESTRICTION_GROUP.TERRAIN, terrain_record.value).id,
                                                       linguistics_storage.restrictions_storage.get_restriction(linguistics_relations.TEMPLATE_RESTRICTION_GROUP.META_TERRAIN, terrain_record.meta_terrain.value).id,
                                                       linguistics_storage.restrictions_storage.get_restriction(linguistics_relations.TEMPLATE_RESTRICTION_GROUP.META_HEIGHT, terrain_record.meta_height.value).id,
                                                       linguistics_storage.restrictions_storage.get_restriction(linguistics_relations.TEMPLATE_RESTRICTION_GROUP.META_VEGETATION, terrain_record.meta_vegetation.value).id )

    return _TERRAIN_LINGUISTICS_CACHE[terrain]


def region_url(turn=None):
    arguments = {'api_version': conf.map_settings.REGION_API_VERSION,
                 'api_client': django_settings.API_CLIENT}

    if turn is not None:
        arguments['turn'] = turn

    return dext_urls.url('game:map:api-region', **arguments)


def region_versions_url():
    arguments = {'api_version': conf.map_settings.REGION_API_VERSION,
                 'api_client': django_settings.API_CLIENT}

    return dext_urls.url('game:map:api-region-versions', **arguments)
