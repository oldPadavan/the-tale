
import random

import markdown

from django.core.urlresolvers import reverse

from dext.views import handler, validate_argument
from dext.common.utils.urls import UrlBuilder, full_url

from the_tale.common.utils.resources import Resource
from the_tale.common.utils.decorators import lazy_property

from the_tale.game.politic_power import conf as politic_power_conf
from the_tale.game import relations as game_relations
from the_tale.game.jobs import effects as jobs_effects

from the_tale.game.heroes.habilities import ABILITIES, ABILITY_TYPE, ABILITY_ACTIVATION_TYPE, ABILITY_AVAILABILITY
from the_tale.game.heroes.conf import heroes_settings
from the_tale.game.heroes.relations import PREFERENCE_TYPE

from the_tale.game.places import conf as places_conf
from the_tale.game.persons import conf as persons_conf
from the_tale.game.persons import relations as persons_relations
from the_tale.game.pvp.conf import pvp_settings
from the_tale.game.pvp import abilities as pvp_abilities

from the_tale.game.cards import cards

from the_tale.accounts.clans.conf import clans_settings
from the_tale.accounts.conf import accounts_settings


class APIReference(object):

    def __init__(self, id_, name, method):
        self.id = id_
        self.name = name
        self.documentation = markdown.markdown(method.__doc__)


class TypeReference(object):

    def __init__(self, id_, name, relation, filter=lambda record: True, fields=(('значение', 'value'), ('описание', 'text'))):
        self.id = id_
        self.name = name
        self.relation = relation
        self.fields = fields
        self.filter = filter

    @lazy_property
    def records(self):
        try:
            records = []
            for record in self.relation.records:
                if not self.filter(record):
                    continue
                records.append([getattr(record, field_id) for field_name, field_id in self.fields])
            return records
        except Exception as e:
            print(e)


def get_api_types():
    from the_tale.game.relations import GENDER, RACE
    from the_tale.game.artifacts.relations import ARTIFACT_TYPE, RARITY as ARTIFACT_RARITY, ARTIFACT_EFFECT
    from the_tale.game.heroes.relations import EQUIPMENT_SLOT
    from the_tale.game.persons import relations as persons_relations
    from the_tale.game.abilities.relations import ABILITY_TYPE as ANGEL_ABILITY_TYPE
    from the_tale.game.actions.relations import ACTION_TYPE
    from the_tale.game.quests.relations import ACTOR_TYPE
    from the_tale.game.cards.relations import RARITY as CARD_RARITY
    from the_tale.game.cards.cards import CARD
    from the_tale.game.jobs import effects as job_effects
    from the_tale.game.places import modifiers as places_modifiers
    from the_tale.game.places import relations as places_relations
    from the_tale.accounts.third_party.relations import AUTHORISATION_STATE

    return [TypeReference('artifact_rarity', 'Артефакты: редкость', ARTIFACT_RARITY),
            TypeReference('artifact_type', 'Артефакты: типы', ARTIFACT_TYPE),
            TypeReference('equipment_slot', 'Артефакты: типы экипировки', EQUIPMENT_SLOT),
            TypeReference('artifact_effect', 'Артефакты: эффекты', ARTIFACT_EFFECT),

            TypeReference('cards_types', 'Карты: типы', CARD),
            TypeReference('card_rarity', 'Карты: редкость', CARD_RARITY),

            TypeReference('action_type', 'Герои: тип действия', ACTION_TYPE),

            TypeReference('places_modifiers', 'Города: специализация', places_modifiers.CITY_MODIFIERS),
            TypeReference('places_attributes', 'Города: аттрибуты', places_relations.ATTRIBUTE),

            TypeReference('actor_types', 'Задания: типы актёров', ACTOR_TYPE),
            TypeReference('buildings_types', 'Здания: типы', places_relations.BUILDING_TYPE),

            TypeReference('ability_type', 'Игрок: тип способности', ANGEL_ABILITY_TYPE,
                          fields=(('значение', 'value'), ('описание', 'text'), ('атрибуты запроса', 'request_attributes'))),

            TypeReference('gender', 'Общее: пол', GENDER),
            TypeReference('race', 'Общее: раса', RACE),
            TypeReference('habits', 'Общее: черты', game_relations.HABIT_TYPE,
                          fields=(('значение целое', 'value'), ('значение строковое', 'verbose_value'), ('описание', 'text'))),
            TypeReference('habits', 'Общее: честь', game_relations.HABIT_HONOR_INTERVAL,
                          fields=(('значение', 'value'), ('для героя', 'text'), ('для города', 'place_text'))),
            TypeReference('habits', 'Общее: миролюбие', game_relations.HABIT_PEACEFULNESS_INTERVAL,
                          fields=(('значение', 'value'), ('для героя', 'text'), ('для города', 'place_text'))),

            TypeReference('authorisation_state', 'Прочее: состояние авторизации', AUTHORISATION_STATE),
            TypeReference('game_state', 'Прочее: состояние игры', game_relations.GAME_STATE),

            TypeReference('person_profession', 'Мастер: профессия', persons_relations.PERSON_TYPE),
            TypeReference('person_social', 'Мастер: тип социальной связи', persons_relations.SOCIAL_CONNECTION_TYPE),
            TypeReference('person_personality_cosmetic', 'Мастер: косметические особенности характера', persons_relations.PERSONALITY_COSMETIC),
            TypeReference('person_personality_practival', 'Мастер: практические особенности характера', persons_relations.PERSONALITY_PRACTICAL),

            TypeReference('job_effect', 'Проекты: типы эфектов', job_effects.EFFECT)]


API_TYPES = get_api_types()


class GuideResource(Resource):

    def initialize(self, *args, **kwargs):
        super(GuideResource, self).initialize(*args, **kwargs)

    @handler('', method='get')
    def index(self):
        return self.redirect(reverse('guide:game'))

    @handler('registration', method='get')
    def registration(self):
        return self.template('guide/registration.html', {'section': 'registration'})

    @handler('user-agreement', method='get')
    def user_agreement(self):
        return self.template('guide/user-agreement.html', {'section': 'user-agreement'})

    @handler('account-types', method='get')
    def account_types(self):
        return self.template('guide/account_types.html', {'section': 'account-types'})

    @handler('payments', method='get')
    def payments(self):
        return self.template('guide/payments.html', {'section': 'payments'})

    @handler('behavior-rules', method='get')
    def behavior_rules(self):
        return self.template('guide/behavior_rules.html', {'section': 'behavior-rules'})

    @handler('game', method='get')
    def game(self):
        return self.template('guide/game.html', {'section': 'game'})

    @handler('keepers', method='get')
    def keepers(self):
        return self.template('guide/keepers.html', {'section': 'keepers'})

    @handler('quests', method='get')
    def quests(self):
        return self.template('guide/quests.html', {'section': 'quests'})

    @handler('persons', method='get')
    def persons(self):
        from the_tale.game.persons import economic
        return self.template('guide/persons.html', {'section': 'persons',
                                                    'persons_settings': persons_conf.settings,
                                                    'BASE_ATTRIBUTES': economic.BASE_ATTRIBUTES,
                                                    'INNER_CIRCLE_SIZE': politic_power_conf.settings.PERSON_INNER_CIRCLE_SIZE,
                                                    'JOBS_EFFECTS': jobs_effects.EFFECT,
                                                    'PERSON_TYPES': sorted(persons_relations.PERSON_TYPE.records, key=lambda r: r.text),
                                                    'PERSONALITY_COSMETIC': sorted(persons_relations.PERSONALITY_COSMETIC.records, key=lambda r: r.text),
                                                    'PERSONALITY_PRACTICAL': sorted(persons_relations.PERSONALITY_PRACTICAL.records, key=lambda r: r.text)})

    @handler('cities', method='get')
    def cities(self):
        from the_tale.game.places.modifiers import CITY_MODIFIERS
        from the_tale.game.places.relations import ATTRIBUTE
        return self.template('guide/cities.html', {'section': 'cities',
                                                   'places_settings': places_conf.settings,
                                                   'INNER_CIRCLE_SIZE': politic_power_conf.settings.PLACE_INNER_CIRCLE_SIZE,
                                                   'ATTRIBUTES': sorted(ATTRIBUTE.records, key=lambda modifier: modifier.text),
                                                   'MODIFIERS': sorted(CITY_MODIFIERS.records, key=lambda modifier: modifier.text) })

    @handler('politics', method='get')
    def politics(self):
        from the_tale.game.bills.conf import bills_settings
        from the_tale.game.bills.bills import BILLS_BY_ID
        return self.template('guide/politics.html', {'section': 'politics',
                                                     'bills_settings': bills_settings,
                                                     'heroes_settings': heroes_settings,
                                                     'BILLS_BY_ID': BILLS_BY_ID})

    @handler('clans', method='get')
    def clans(self):
        return self.template('guide/clans.html',
                             {'section': 'clans',
                              'clans_settings': clans_settings })

    @handler('map', method='get')
    def map(self):
        return self.template('guide/map.html', {'section': 'map'})

    @handler('pvp', method='get')
    def pvp(self):
        return self.template('guide/pvp.html', {'section': 'pvp',
                                                'pvp_settings': pvp_settings,
                                                'pvp_abilities': pvp_abilities})

    @handler('api', method='get')
    def api(self):
        return self.template('guide/api.html', {'section': 'api',
                                                'types': API_TYPES})

    @validate_argument('ability_type', lambda x: ABILITY_TYPE(int(x)), 'guide.hero_abilities', 'Неверный формат типа способности')
    @validate_argument('activation_type', lambda x: ABILITY_ACTIVATION_TYPE(int(x)), 'guide.hero_abilities', 'Неверный формат типа активации')
    @validate_argument('availability', lambda x: ABILITY_AVAILABILITY(int(x)), 'guide.hero_abilities', 'Неверный формат типа доступности')
    @handler('hero-abilities', method='get')
    def hero_abilities(self, ability_type=None, activation_type=None, availability=ABILITY_AVAILABILITY.FOR_ALL):

        abilities = list(ABILITIES.values())

        is_filtering = False

        if ability_type is not None:
            is_filtering = True
            abilities = [ability for ability in abilities if ability.TYPE == ability_type]

        if activation_type is not None:
            is_filtering = True
            abilities = [ability for ability in abilities if ability.ACTIVATION_TYPE == activation_type]

        if availability is not ABILITY_AVAILABILITY.FOR_ALL:
            if availability is not ABILITY_AVAILABILITY.FOR_ALL:
                is_filtering = True
            abilities = [ability for ability in abilities if ability.AVAILABILITY == availability]

        abilities = [ability(level=ability.MAX_LEVEL) for ability in sorted(abilities, key=lambda x: x.NAME)]

        url_builder = UrlBuilder(reverse('guide:hero-abilities'), arguments={'ability_type': ability_type.value if ability_type is not None else None,
                                                                             'activation_type': activation_type.value if activation_type is not None else None,
                                                                             'availability': availability.value})

        return self.template('guide/hero-abilities.html', {'section': 'hero-abilities',
                                                           'url_builder': url_builder,
                                                           'abilities': abilities,
                                                           'is_filtering': is_filtering,
                                                           'ability_type': ability_type,
                                                           'activation_type': activation_type,
                                                           'availability': availability,
                                                           'ABILITY_ACTIVATION_TYPE': ABILITY_ACTIVATION_TYPE,
                                                           'ABILITY_TYPE': ABILITY_TYPE,
                                                           'ABILITY_AVAILABILITY': ABILITY_AVAILABILITY})

    @handler('hero-preferences', method='get')
    def hero_preferences(self):
        return self.template('guide/hero-preferences.html', {'section': 'hero-preferences',
                                                             'change_preferences_card': cards.CARD.CHANGE_PREFERENCE,
                                                             'PREFERENCE_TYPE': PREFERENCE_TYPE})

    @handler('referrals', method='get')
    def referrals(self):
        return self.template('guide/referrals.html', {'section': 'referrals',
                                                      'account': self.account,
                                                      'accounts_settings': accounts_settings,
                                                      'referral_link': full_url('https', 'portal:',
                                                                                **{accounts_settings.REFERRAL_URL_ARGUMENT: self.account.id if self.account else None})})

    @handler('zero-player-game', name='zpg', method='get')
    def zpg(self):
        return self.template('guide/zpg.html', {'section': 'zpg'})

    @handler('hero-habits', method='get')
    def habits(self):
        habit_cards = sorted(cards.HABIT_POINTS_CARDS, key=lambda x: (x.rarity.value, x.text))
        return self.template('guide/hero-habits.html', {'section': 'hero-habits',
                                                        'HABIT_TYPE': game_relations.HABIT_TYPE,
                                                        'HABIT_POINTS_CARDS': habit_cards})

    @validate_argument('habit', lambda x: game_relations.HABIT_TYPE(int(x)), 'guide.hero_habit_info', 'Неверный тип черты')
    @handler('hero-habit-info', method='get')
    def habit_info(self, habit=game_relations.HABIT_TYPE.HONOR):
        return self.template('guide/hero-habit-info.html', {'habit': habit,
                                                            'HABIT_TYPE': game_relations.HABIT_TYPE})

    @handler('press-kit', name='press-kit')
    def press_kit(self):
        from the_tale.game.mobs import storage as mobs_storage
        return self.template('guide/press_kit.html',
                             {'section': 'press-kit',
                              'mob': random.choice(mobs_storage.mobs.get_all_mobs_for_level(level=666))})

    @handler('world')
    def world(self):
        return self.template('guide/world.html', {'section': 'world'})

    @handler('how-to-help')
    def how_to_help(self):
        return self.template('guide/how_to_help.html', {'section': 'how-to-help'})

    @handler('game-resources')
    def game_resources(self):
        return self.template('guide/game_resources.html', {'section': 'game-resources'})
