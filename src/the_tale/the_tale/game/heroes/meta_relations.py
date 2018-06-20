
import smart_imports

smart_imports.all()


class Hero(utils_meta_relations.MetaType):
    __slots__ = ('caption', )
    TYPE = 9
    TYPE_CAPTION = 'Герой'

    def __init__(self, caption, **kwargs):
        super(Hero, self).__init__(**kwargs)
        self.caption = caption

    @property
    def url(self):
        return dext_urls.url('game:heroes:show', self.id)

    @classmethod
    def create_from_object(cls, hero):
        return cls(id=hero.id, caption=hero.name)

    @classmethod
    def create_from_id(cls, id):
        hero = logic.load_hero(hero_id=id)
        if hero is None:
            return None

        return cls.create_from_object(hero)

    @classmethod
    def create_from_ids(cls, ids):
        return [cls.create_from_id(id) for id in ids]
