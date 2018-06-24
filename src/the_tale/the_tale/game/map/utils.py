
import smart_imports

smart_imports.all()


def get_person_race_percents(persons):
    race_powers = dict((race.value, 0) for race in game_relations.RACE.records)

    for person in persons:
        race_powers[person.race.value] += politic_power_storage.persons.total_power_fraction(person.id)

    return race_powers


def get_race_percents(places):
    race_powers = dict( (race.value, 0) for race in game_relations.RACE.records)

    for place in places:
        for race in game_relations.RACE.records:
            race_powers[race.value] += place.races.get_race_percents(race) * place.attrs.size

    total_power = sum(race_powers.values()) + 1  # +1 - to prevent division by 0

    return dict( (race_id, float(power) / total_power) for race_id, power in race_powers.items())
