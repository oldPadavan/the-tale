
import smart_imports

smart_imports.all()



class PositionDescriptionsStorage(object):

    def __init__(self):
        self.clear()

    def clear(self):
        self._actual_places_version = places_storage.places._version

        self._position_in_place_cache = {}
        self._position_near_place_cache = {}
        self._position_on_road_cache = {}


    def sync(self):
        if places_storage.places.version != self._actual_places_version:
            self.clear()

    def text_in_place(self, place_id):
        self.sync()

        if place_id not in self._position_in_place_cache:
            self._position_in_place_cache[place_id] = places_storage.places[place_id].name

        return self._position_in_place_cache[place_id]

    def text_near_place(self, place_id):
        self.sync()

        if place_id not in self._position_near_place_cache:
            self._position_near_place_cache[place_id] = 'окрестности %s' % places_storage.places[place_id].utg_name.form(utg_words.Properties(utg_relations.CASE.GENITIVE))

        return self._position_near_place_cache[place_id]

    def text_on_road(self, place_from_id, place_to_id):
        self.sync()

        key = (place_from_id, place_to_id)
        if key not in self._position_on_road_cache:
            self._position_on_road_cache[key] = 'дорога из %s в %s' % (places_storage.places[place_from_id].utg_name.form(utg_words.Properties(utg_relations.CASE.GENITIVE)),
                                                                        places_storage.places[place_to_id].utg_name.form(utg_words.Properties(utg_relations.CASE.ACCUSATIVE)))

        return self._position_on_road_cache[key]

    def text_in_wild_lands(self):
        return 'дикие земли'


position_descriptions = PositionDescriptionsStorage()
