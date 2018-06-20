
import smart_imports

smart_imports.all()


def get_simple_cache_data(*argv, **kwargs):
    return {'ui_caching_started_at': kwargs.get('ui_caching_started_at', 0),
            'changed_fields': [],
            'patch_turn': None,
            'action': {'data': None}}


class HeroTest(utils_testcase.TestCase, pm_helpers.Mixin):

    def setUp(self):
        super(HeroTest, self).setUp()

        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        account = self.accounts_factory.create_account(is_fast=True)

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(account)
        self.hero = self.storage.accounts_to_heroes[account.id]

        pm_tt_api.debug_clear_service()


    def test_create(self):
        self.assertFalse(self.hero.force_save_required)

        self.assertTrue(self.hero.is_alive)
        self.assertEqual(self.hero.created_at_turn, turn.number())
        self.assertEqual(self.hero.abilities.get('hit').level, 1)
        self.assertEqual(self.hero.abilities.get('coherence').level, 1)

        self.assertTrue(self.hero.preferences.risk_level.is_NORMAL)

        self.assertEqual(models.HeroPreferences.objects.count(), 1)
        self.assertEqual(models.HeroPreferences.objects.get(hero_id=self.hero.id).energy_regeneration_type, self.hero.preferences.energy_regeneration_type)
        self.assertEqual(models.HeroPreferences.objects.get(hero_id=self.hero.id).risk_level, self.hero.preferences.risk_level)

    def test_helps_number_restriction(self):
        self.assertEqual(self.hero.last_help_on_turn, 0)
        self.assertEqual(self.hero.helps_in_turn, 0)

        self.assertTrue(self.hero.can_be_helped())

        for i in range(conf.heroes_settings.MAX_HELPS_IN_TURN-1):
            self.hero.on_help()

        self.assertEqual(self.hero.helps_in_turn, conf.heroes_settings.MAX_HELPS_IN_TURN-1)

        self.assertTrue(self.hero.can_be_helped())

        self.hero.on_help()

        self.assertFalse(self.hero.can_be_helped())

        turn.increment()

        self.assertTrue(self.hero.can_be_helped())

        self.hero.on_help()

        self.assertEqual(self.hero.last_help_on_turn, turn.number())
        self.assertEqual(self.hero.helps_in_turn, 1)


    def test_is_premium(self):
        self.assertFalse(self.hero.is_premium)
        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=10)
        self.assertTrue(self.hero.is_premium)

    def test_is_banned(self):
        self.assertFalse(self.hero.is_banned)
        self.hero.ban_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=10)
        self.assertTrue(self.hero.is_banned)

    def test_is_active(self):
        self.assertTrue(self.hero.is_active)
        self.hero.active_state_end_at = datetime.datetime.now()
        self.assertFalse(self.hero.is_active)

    def test_create_time(self):
        turn.increment()
        turn.increment()
        turn.increment()

        account = self.accounts_factory.create_account(is_fast=True)

        hero = logic.load_hero(account_id=account.id)

        self.assertEqual(hero.created_at_turn, turn.number())

        self.assertTrue(hero.created_at_turn != self.hero.created_at_turn)

    def test_experience_modifier__banned(self):
        self.assertEqual(self.hero.experience_modifier, c.EXP_FOR_NORMAL_ACCOUNT)
        self.hero.ban_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        self.assertEqual(self.hero.experience_modifier, 0)

    def test_experience_modifier__risk_level(self):
        self.assertEqual(self.hero.experience_modifier, c.EXP_FOR_NORMAL_ACCOUNT)

        self.hero.preferences.set(relations.PREFERENCE_TYPE.RISK_LEVEL, relations.RISK_LEVEL.VERY_HIGH)
        self.assertTrue(c.EXP_FOR_NORMAL_ACCOUNT < self.hero.experience_modifier)

        self.hero.preferences.set(relations.PREFERENCE_TYPE.RISK_LEVEL, relations.RISK_LEVEL.VERY_LOW)
        self.assertTrue(c.EXP_FOR_NORMAL_ACCOUNT > self.hero.experience_modifier)

    def test_experience_modifier__active_inactive_state(self):
        self.assertEqual(self.hero.experience_modifier, c.EXP_FOR_NORMAL_ACCOUNT)

        self.hero.active_state_end_at = datetime.datetime.now() - datetime.timedelta(seconds=60)

        # inactive heroes get the same exp, insteed experience penalty  there action delayed
        self.assertTrue(self.hero.experience_modifier, c.EXP_FOR_NORMAL_ACCOUNT)

        self.hero.update_with_account_data(is_fast=False,
                                           premium_end_at=datetime.datetime.now(),
                                           active_end_at=datetime.datetime.now() + datetime.timedelta(seconds=60),
                                           ban_end_at=datetime.datetime.now() - datetime.timedelta(seconds=60),
                                           might=0,
                                           actual_bills=[])

        self.assertEqual(self.hero.experience_modifier, c.EXP_FOR_NORMAL_ACCOUNT)

    def test_experience_modifier__with_premium(self):
        self.assertEqual(self.hero.experience_modifier, c.EXP_FOR_NORMAL_ACCOUNT)

        self.hero.active_state_end_at = datetime.datetime.now() - datetime.timedelta(seconds=60)
        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)

        self.assertEqual(self.hero.experience_modifier, c.EXP_FOR_PREMIUM_ACCOUNT)

        self.hero.update_with_account_data(is_fast=False,
                                           premium_end_at=datetime.datetime.now(),
                                           active_end_at=datetime.datetime.now() + datetime.timedelta(seconds=60),
                                           ban_end_at=datetime.datetime.now() - datetime.timedelta(seconds=60),
                                           might=666,
                                           actual_bills=[])

        self.assertEqual(self.hero.experience_modifier, c.EXP_FOR_NORMAL_ACCOUNT)

    def test_can_participate_in_pvp(self):
        self.assertFalse(self.hero.can_participate_in_pvp)

        self.hero.is_fast = False

        self.assertTrue(self.hero.can_participate_in_pvp)
        with mock.patch('the_tale.game.heroes.objects.Hero.is_banned', True):
            self.assertFalse(self.hero.can_participate_in_pvp)

    def test_can_change_person_power(self):
        self.assertFalse(self.hero.can_change_person_power(self.place_1.persons[0]))

    def test_can_change_person_power__premium(self):
        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        self.assertTrue(self.hero.can_change_person_power(self.place_1.persons[0]))

    def test_can_change_person_power__depends_from_all_heroes(self):
        with mock.patch('the_tale.game.places.objects.Place.depends_from_all_heroes', True):
            self.assertTrue(self.hero.can_change_person_power(self.place_1.persons[0]))

    def test_can_change_person_power__banned(self):
        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)

        with mock.patch('the_tale.game.places.objects.Place.depends_from_all_heroes', True):
            with mock.patch('the_tale.game.heroes.objects.Hero.is_banned', True):
                self.assertFalse(self.hero.can_change_person_power(self.place_1.persons[0]))


    def test_can_change_place_power(self):
        self.assertFalse(self.hero.can_change_place_power(self.place_1))

    def test_can_change_place_power__premium(self):
        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        self.assertTrue(self.hero.can_change_place_power(self.place_1))

    def test_can_change_place_power__depends_from_all_heroes(self):
        with mock.patch('the_tale.game.places.objects.Place.depends_from_all_heroes', True):
            self.assertTrue(self.hero.can_change_place_power(self.place_1))

    def test_can_change_place_power__banned(self):
        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)

        with mock.patch('the_tale.game.places.objects.Place.depends_from_all_heroes', True):
            with mock.patch('the_tale.game.heroes.objects.Hero.is_banned', True):
                self.assertFalse(self.hero.can_change_person_power(self.place_1))

    def test_can_repair_building(self):
        self.assertFalse(self.hero.can_repair_building)
        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        self.assertTrue(self.hero.can_repair_building)

        with mock.patch('the_tale.game.heroes.objects.Hero.is_banned', True):
            self.assertFalse(self.hero.can_repair_building)

    def test_update_with_account_data(self):
        self.hero.is_fast = True
        self.hero.active_state_end_at = datetime.datetime.now() - datetime.timedelta(seconds=1)

        self.hero.update_with_account_data(is_fast=False,
                                           premium_end_at=datetime.datetime.now() + datetime.timedelta(seconds=60),
                                           active_end_at=datetime.datetime.now() + datetime.timedelta(seconds=60),
                                           ban_end_at=datetime.datetime.now() + datetime.timedelta(seconds=60),
                                           might=666,
                                           actual_bills=[7])

        self.assertFalse(self.hero.is_fast)
        self.assertTrue(self.hero.active_state_end_at > datetime.datetime.now())
        self.assertTrue(self.hero.premium_state_end_at > datetime.datetime.now())
        self.assertTrue(self.hero.ban_state_end_at > datetime.datetime.now())
        self.assertEqual(self.hero.might, 666)
        self.assertEqual(self.hero.actual_bills, [7])

    def test_reward_modifier__risk_level(self):
        self.assertEqual(self.hero.quest_money_reward_multiplier(), 1.0)
        self.hero.preferences.set(relations.PREFERENCE_TYPE.RISK_LEVEL, relations.RISK_LEVEL.VERY_HIGH)
        self.assertTrue(self.hero.quest_money_reward_multiplier() > 1.0)
        self.hero.preferences.set(relations.PREFERENCE_TYPE.RISK_LEVEL, relations.RISK_LEVEL.VERY_LOW)
        self.assertTrue(self.hero.quest_money_reward_multiplier() < 1.0)

    def test_push_message(self):
        message = messages.MessageSurrogate(turn_number=turn.number(),
                                            timestamp=time.time(),
                                            key=None,
                                            externals=None,
                                            message='abrakadabra')

        self.hero.journal.clear()

        self.assertEqual(len(self.hero.journal), 0)

        with self.check_calls_count('the_tale.game.heroes.tt_api.push_message_to_diary', 0):
            self.hero.push_message(message)

        self.assertEqual(len(self.hero.journal), 1)

        with self.check_calls_count('the_tale.game.heroes.tt_api.push_message_to_diary', 1):
            self.hero.push_message(message, diary=True)

        self.assertEqual(len(self.hero.journal), 2)

        with self.check_calls_count('the_tale.game.heroes.tt_api.push_message_to_diary', 1):
            self.hero.push_message(message, diary=True, journal=False)

        self.assertEqual(len(self.hero.journal), 2)


    def test_add_message__inactive_hero(self):

        self.hero.journal.clear()

        self.assertTrue(self.hero.is_active)

        with self.check_calls_count('the_tale.game.heroes.tt_api.push_message_to_diary', 1):
            with mock.patch('the_tale.linguistics.logic.get_text', mock.Mock(return_value='message_1')):
                self.hero.add_message('hero_common_journal_level_up', diary=True, journal=True)

        self.assertEqual(len(self.hero.journal), 1)

        with mock.patch('the_tale.game.heroes.objects.Hero.is_active', False):
            with self.check_calls_count('the_tale.game.heroes.tt_api.push_message_to_diary', 1):
                with mock.patch('the_tale.linguistics.logic.get_text', mock.Mock(return_value='message_2')):
                    self.hero.add_message('hero_common_journal_level_up', diary=True, journal=True)

            self.assertEqual(len(self.hero.journal), 2)

            with self.check_calls_count('the_tale.game.heroes.tt_api.push_message_to_diary', 0):
                with mock.patch('the_tale.linguistics.logic.get_text', mock.Mock(return_value='message_2')):
                    self.hero.add_message('hero_common_journal_level_up', diary=False, journal=True)

            self.assertEqual(len(self.hero.journal), 0)

            with self.check_calls_count('the_tale.game.heroes.tt_api.push_message_to_diary', 0):
                with mock.patch('the_tale.linguistics.logic.get_text', mock.Mock(return_value='message_2')):
                    with mock.patch('the_tale.game.heroes.objects.Hero.is_premium', True):
                        self.hero.add_message('hero_common_journal_level_up', diary=False, journal=True)

            self.assertEqual(len(self.hero.journal), 1)

    def check_rests_from_risk(self, method):
        results = []
        for risk_level in relations.RISK_LEVEL.records:
            values = []
            self.hero.preferences.set(relations.PREFERENCE_TYPE.RISK_LEVEL, risk_level)
            for health_percents in range(1, 100, 1):
                self.hero.health = self.hero.max_health * float(health_percents) / 100
                values.append(method(self.hero))
            results.append(values)

        for i, result_1 in enumerate(results):
            for j, result_2 in enumerate(results):
                if i == j:
                    continue
                self.assertNotEqual(result_1, result_2)

    def test_need_rest_in_settlement__from_risk_level(self):
        self.check_rests_from_risk(lambda hero: hero.need_rest_in_settlement)

    def test_need_rest_in_move__from_risk_level(self):
        self.check_rests_from_risk(lambda hero: hero.need_rest_in_move)

    @mock.patch('the_tale.game.heroes.conf.heroes_settings.RARE_OPERATIONS_INTERVAL', 2)
    def test_process_rare_operations__interval_not_passed(self):
        turn.increment()

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.process_rare_operations()

        self.assertEqual(verify_achievements.call_args_list, [])
        self.assertEqual(self.hero.last_rare_operation_at_turn, 0)

    @mock.patch('the_tale.game.heroes.conf.heroes_settings.RARE_OPERATIONS_INTERVAL', 2)
    def test_process_rare_operations__interval_passed(self):
        turn.increment()
        turn.increment()

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            with mock.patch('the_tale.game.quests.container.QuestsContainer.sync_interfered_persons') as sync_interfered_persons:
                self.hero.process_rare_operations()

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=achievements_relations.ACHIEVEMENT_TYPE.TIME,
                                                                        old_value=0,
                                                                        new_value=0)])

        self.assertEqual(sync_interfered_persons.call_args_list, [mock.call()])

        self.assertEqual(self.hero.last_rare_operation_at_turn, turn.number())


    def test_process_rare_operations__companion_added(self):
        turn.increment(max(conf.heroes_settings.RARE_OPERATIONS_INTERVAL,
                           int(c.TURNS_IN_HOUR * c.COMPANIONS_GIVE_COMPANION_AFTER)))

        self.assertTrue(len(list(companions_storage.companions.enabled_companions())) > 1)

        companions_logic.create_random_companion_record('leaved_companions',
                                                        abilities=companions_abilities_container.Container(start=(companions_abilities_effects.ABILITIES.TEMPORARY, )),
                                                        state=companions_relations.STATE.ENABLED)

        with self.check_changed(lambda: self.hero.companion):
            self.hero.process_rare_operations()

        self.assertTrue(any(ability.is_TEMPORARY for ability in self.hero.companion.record.abilities.start))

        self.assertTrue(self.hero.companion.record.rarity.is_COMMON)


    @mock.patch('the_tale.game.heroes.conf.heroes_settings.RARE_OPERATIONS_INTERVAL', 0)
    def test_process_rare_operations__companion_not_added(self):

        for i in range(1000):
            self.hero.process_rare_operations()
            self.assertEqual(self.hero.companion, None)


    def test_process_rare_operations__age_changed(self):
        turn.increment(tt_calendar.converter.old_converter.seconds_in_year // tt_calendar.converter.old_converter.SECONDS_IN_TURN - 1)

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.process_rare_operations()

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=achievements_relations.ACHIEVEMENT_TYPE.TIME,
                                                                        old_value=0,
                                                                        new_value=0)])

        self.hero.last_rare_operation_at_turn = 0

        turn.increment()

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.process_rare_operations()

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=achievements_relations.ACHIEVEMENT_TYPE.TIME,
                                                                        old_value=0,
                                                                        new_value=1)])


    def test_get_achievement_type_value(self):
        for achievement_type in achievements_relations.ACHIEVEMENT_TYPE.records:
            if achievement_type.source.is_ACCOUNT:
                continue
            if achievement_type.source.is_NONE:
                continue
            self.hero.get_achievement_type_value(achievement_type)

    def test_update_habits__premium(self):
        self.assertEqual(self.hero.habit_honor.raw_value, 0)
        self.assertFalse(self.hero.is_premium)

        self.hero.update_habits(relations.HABIT_CHANGE_SOURCE.QUEST_HONORABLE)

        value_without_premium = self.hero.habit_honor.raw_value

        with mock.patch('the_tale.game.heroes.objects.Hero.is_premium', True):
            self.hero.update_habits(relations.HABIT_CHANGE_SOURCE.QUEST_HONORABLE)

        self.assertTrue(value_without_premium < self.hero.habit_honor.raw_value - value_without_premium)


    def test_reset_accessories_cache(self):
        self.hero.damage_modifier # fill cache

        self.assertTrue(getattr(self.hero, '_cached_modifiers'))

        self.hero.reset_accessors_cache()

        self.assertEqual(self.hero._cached_modifiers, {relations.MODIFIERS.HEALTH: 1.0})

    @mock.patch('the_tale.game.balance.power.Power.damage', lambda self: power.Damage(1, 1))
    @mock.patch('the_tale.game.heroes.objects.Hero.damage_modifier', 2)
    @mock.patch('the_tale.game.heroes.objects.Hero.magic_damage_modifier', 3)
    @mock.patch('the_tale.game.heroes.objects.Hero.physic_damage_modifier', 4)
    def test_basic_damage(self):
        self.assertEqual(self.hero.basic_damage, power.Damage(physic=8, magic=6))


    def test_set_companion(self):
        companion_record = next(companions_storage.companions.enabled_companions())
        companion = companions_logic.create_companion(companion_record)

        self.assertEqual(self.hero.companion, None)

        with self.check_calls_count('the_tale.game.heroes.tt_api.push_message_to_diary', 1):
            self.hero.set_companion(companion)

        self.assertEqual(self.hero.companion.record.id, companion_record.id)
        self.assertEqual(self.hero.companion._hero.id, self.hero.id)


    @mock.patch('the_tale.game.heroes.objects.Hero.companion_max_health_multiplier', 2)
    def test_set_companion__health_maximum(self):
        companion_record = next(companions_storage.companions.enabled_companions())
        companion = companions_logic.create_companion(companion_record)

        self.hero.set_companion(companion)

        self.assertEqual(self.hero.companion.health, self.hero.companion.max_health)


    def test_set_companion__replace(self):
        companion_record_1 = list(companions_storage.companions.enabled_companions())[0]
        companion_record_2 = list(companions_storage.companions.enabled_companions())[1]

        companion_1 = companions_logic.create_companion(companion_record_1)
        companion_2 = companions_logic.create_companion(companion_record_2)

        self.hero.set_companion(companion_1)

        with self.check_calls_count('the_tale.game.heroes.tt_api.push_message_to_diary', 2):
            self.hero.set_companion(companion_2)

        self.assertEqual(self.hero.companion.record.id, companion_record_2.id)

    def test_remove_companion(self):
        companion_record = next(companions_storage.companions.enabled_companions())
        companion = companions_logic.create_companion(companion_record)

        self.hero.set_companion(companion)

        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            self.hero.remove_companion()

        self.assertEqual(reset_accessors_cache.call_count, 1)

        self.assertEqual(self.hero.companion, None)


    def test_remove_companion__switch_next_spending(self):
        companion_record = next(companions_storage.companions.enabled_companions())
        companion = companions_logic.create_companion(companion_record)

        self.hero.set_companion(companion)

        while not self.hero.next_spending.is_HEAL_COMPANION:
            self.hero.switch_spending()

        self.hero.remove_companion()

        self.assertFalse(self.hero.next_spending.is_HEAL_COMPANION)


    def test_switch_next_spending__with_companion(self):
        companion_record = next(companions_storage.companions.enabled_companions())
        companion = companions_logic.create_companion(companion_record)

        self.hero.set_companion(companion)

        spendings = set()

        for i in range(1000):
            self.hero.switch_spending()
            spendings.add(self.hero.next_spending)

        self.assertIn(relations.ITEMS_OF_EXPENDITURE.HEAL_COMPANION, spendings)

    def test_switch_next_spending__with_companion_dedication_is_EVERY_MAN_FOR_HIMSELF(self):
        companion_record = next(companions_storage.companions.enabled_companions())
        companion = companions_logic.create_companion(companion_record)

        self.hero.set_companion(companion)

        self.hero.preferences.set(relations.PREFERENCE_TYPE.COMPANION_DEDICATION, relations.COMPANION_DEDICATION.EVERY_MAN_FOR_HIMSELF)

        for i in range(1000):
            self.hero.switch_spending()
            self.assertFalse(self.hero.next_spending.is_HEAL_COMPANION)

    def test_next_spending_priorities_depends_from_dedication(self):
        heal_companion_priorities = set()

        for dedication in relations.COMPANION_DEDICATION.records:
            self.hero.preferences.set(relations.PREFERENCE_TYPE.COMPANION_DEDICATION, dedication)
            heal_companion_priorities.add(self.hero.spending_priorities()[relations.ITEMS_OF_EXPENDITURE.HEAL_COMPANION])

        self.assertEqual(len(heal_companion_priorities), len(relations.COMPANION_DEDICATION.records))


    def test_switch_next_spending__without_companion(self):
        self.assertEqual(self.hero.companion, None)

        for i in range(1000):
            self.hero.switch_spending()
            self.assertFalse(self.hero.next_spending.is_HEAL_COMPANION)

    def test_actual_bills_number(self):
        self.hero.actual_bills.append(time.time() - bills_conf.bills_settings.BILL_ACTUAL_LIVE_TIME*24*60*60)
        self.hero.actual_bills.append(time.time() - bills_conf.bills_settings.BILL_ACTUAL_LIVE_TIME*24*60*60 + 1)
        self.hero.actual_bills.append(time.time() - 1)
        self.hero.actual_bills.append(time.time())

        self.assertEqual(self.hero.actual_bills_number, 3)


class HeroLevelUpTests(utils_testcase.TestCase, pm_helpers.Mixin):

    def setUp(self):
        super(HeroLevelUpTests, self).setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account(is_fast=True)

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        pm_tt_api.debug_clear_service()


    def test_is_initial_state(self):
        self.assertTrue(self.hero.abilities.is_initial_state())

        self.hero.randomized_level_up(increment_level=True)

        self.assertFalse(self.hero.abilities.is_initial_state())

        self.hero.abilities.reset()

        self.assertTrue(self.hero.abilities.is_initial_state())

    def test_level_up(self):

        with self.check_new_message(self.account.id, number=4):
            self.assertEqual(self.hero.level, 1)
            self.assertEqual(self.hero.experience_modifier, c.EXP_FOR_NORMAL_ACCOUNT)

            self.hero.add_experience(f.exp_on_lvl(1)/2 / self.hero.experience_modifier)
            self.assertEqual(self.hero.level, 1)

            self.hero.add_experience(f.exp_on_lvl(1) / self.hero.experience_modifier)
            self.assertEqual(self.hero.level, 2)
            self.assertEqual(self.hero.experience, f.exp_on_lvl(1)//2)

            self.hero.add_experience(f.exp_on_lvl(2) / self.hero.experience_modifier)
            self.assertEqual(self.hero.level, 3)

            self.hero.add_experience(f.exp_on_lvl(3) / self.hero.experience_modifier)
            self.assertEqual(self.hero.level, 4)

            self.hero.add_experience(f.exp_on_lvl(4) / self.hero.experience_modifier)
            self.assertEqual(self.hero.level, 5)

    def test_increment_level__no_message(self):
        with self.check_no_messages(self.account.id):
            self.hero.increment_level()

    def test_increment_level__message(self):
        with self.check_new_message(self.account.id):
            self.hero.increment_level(send_message=True)

    def test_increment_level__force_save(self):
        self.assertFalse(self.hero.force_save_required)
        self.hero.increment_level()
        self.assertTrue(self.hero.force_save_required)

    def test_max_ability_points_number(self):
        level_to_points_number = { 1: 3,
                                   2: 4,
                                   3: 5,
                                   4: 6,
                                   5: 7}

        for level, points_number in list(level_to_points_number.items()):
            self.hero.level = level
            self.assertEqual(self.hero.abilities.max_ability_points_number, points_number)


    def test_can_choose_new_ability(self):
        self.assertTrue(self.hero.abilities.can_choose_new_ability)
        with mock.patch('the_tale.game.heroes.habilities.AbilitiesPrototype.current_ability_points_number', 3):
            self.assertFalse(self.hero.abilities.can_choose_new_ability)

    def test_next_battle_ability_point_lvl(self):
        level_to_next_level = { 1: 2,
                                2: 5,
                                3: 5,
                                4: 5,
                                5: 8,
                                6: 8,
                                7: 8,
                                8: 11,
                                9: 11,
                                10: 11,
                                11: 14,
                                12: 14,
                                13: 14,
                                14: 17,
                                15: 17}

        for level, next_level in list(level_to_next_level.items()):
            self.hero.reset_level()

            for i in range(level-1):
                self.hero.randomized_level_up(increment_level=True)

            self.assertEqual(self.hero.abilities.next_battle_ability_point_lvl, next_level)

    def test_next_nonbattle_ability_point_lvl(self):
        level_to_next_level = { 1: 3,
                                2: 3,
                                3: 6,
                                4: 6,
                                5: 6,
                                6: 9,
                                7: 9,
                                8: 9,
                                9: 12,
                                10: 12,
                                11: 12,
                                12: 15,
                                13: 15,
                                14: 15,
                                15: 18,
                                16: 18}

        for level, next_level in list(level_to_next_level.items()):
            self.hero.reset_level()

            for i in range(level-1):
                self.hero.randomized_level_up(increment_level=True)

            self.assertEqual(self.hero.abilities.next_nonbattle_ability_point_lvl, next_level)


    def test_next_companion_ability_point_lvl(self):
        level_to_next_level = { 1: 4,
                                2: 4,
                                3: 4,
                                4: 7,
                                5: 7,
                                6: 7,
                                7: 10,
                                8: 10,
                                9: 10,
                                10: 13,
                                11: 13,
                                12: 13,
                                13: 16,
                                14: 16}

        for level, next_level in list(level_to_next_level.items()):
            self.hero.reset_level()

            for i in range(level-1):
                self.hero.randomized_level_up(increment_level=True)

            self.assertEqual(self.hero.abilities.next_companion_ability_point_lvl, next_level)

    def test_next_ability_type(self):
        ability_points_to_type = {1: habilities.ABILITY_TYPE.BATTLE,
                                  2: habilities.ABILITY_TYPE.NONBATTLE,
                                  3: habilities.ABILITY_TYPE.COMPANION,
                                  4: habilities.ABILITY_TYPE.BATTLE,
                                  5: habilities.ABILITY_TYPE.NONBATTLE,
                                  6: habilities.ABILITY_TYPE.COMPANION,

                                  50: habilities.ABILITY_TYPE.NONBATTLE,
                                  51: habilities.ABILITY_TYPE.COMPANION,
                                  52: habilities.ABILITY_TYPE.BATTLE,
                                  53: habilities.ABILITY_TYPE.NONBATTLE,
                                  54: habilities.ABILITY_TYPE.COMPANION,
                                  55: habilities.ABILITY_TYPE.BATTLE,
                                  56: habilities.ABILITY_TYPE.NONBATTLE,
                                  57: habilities.ABILITY_TYPE.COMPANION,
                                  58: habilities.ABILITY_TYPE.BATTLE,
                                  59: habilities.ABILITY_TYPE.NONBATTLE,

                                  60: habilities.ABILITY_TYPE.BATTLE,
                                  61: habilities.ABILITY_TYPE.BATTLE,
                                  62: habilities.ABILITY_TYPE.BATTLE,
                                  63: habilities.ABILITY_TYPE.BATTLE,
                                  64: habilities.ABILITY_TYPE.BATTLE,
                                  65: habilities.ABILITY_TYPE.BATTLE,
                                  66: habilities.ABILITY_TYPE.BATTLE,
                                  67: habilities.ABILITY_TYPE.BATTLE,
                                  68: habilities.ABILITY_TYPE.BATTLE,
                                  69: habilities.ABILITY_TYPE.BATTLE,
                                  70: None,
                                  71: None,
                                  72: None,
                                  73: None}

        for ability_points, next_type in ability_points_to_type.items():
            self.hero.reset_level()
            for i in range(ability_points-1):
                self.hero.randomized_level_up(increment_level=True)

            self.assertEqual(self.hero.abilities.next_ability_type, next_type)


    def test_get_abilities_for_choose_first_time(self):
        abilities = self.hero.abilities.get_for_choose()
        self.assertEqual(len(abilities), c.ABILITIES_FOR_CHOOSE_MAXIMUM)

    def test_get_abilities_for_choose_has_free_slots(self):
        for ability in list(self.hero.abilities.abilities.values()):
            ability.level = ability.MAX_LEVEL
        abilities = self.hero.abilities.get_for_choose()
        self.assertEqual(len(abilities), 4)
        self.assertEqual(len([a for a in abilities if a.level==2 and a.get_id()=='hit']), 0)

    @mock.patch('the_tale.game.heroes.habilities.AbilitiesPrototype.next_ability_type', habilities.ABILITY_TYPE.BATTLE)
    def test_get_abilities_for_choose_all_passive_slots_busy(self):

        passive_abilities = [a for a in [a(level=a.MAX_LEVEL) for a in list(habilities.ABILITIES.values())] if a.activation_type.is_PASSIVE and a.type.is_BATTLE]
        for ability in passive_abilities[:c.ABILITIES_PASSIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        for i in range(100):
            abilities = self.hero.abilities.get_for_choose()
            self.assertEqual(len([a for a in abilities if a.activation_type.is_PASSIVE]), 0)

    @mock.patch('the_tale.game.heroes.habilities.AbilitiesPrototype.next_ability_type', habilities.ABILITY_TYPE.BATTLE)
    def test_get_abilities_for_choose_all_active_slots_busy(self):
        active_abilities = [a for a in [a(level=a.MAX_LEVEL) for a in list(habilities.ABILITIES.values())] if a.activation_type.is_ACTIVE]
        for ability in active_abilities[:c.ABILITIES_ACTIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        for i in range(100):
            abilities = self.hero.abilities.get_for_choose()
            self.assertEqual(len([a for a in abilities if a.activation_type.is_ACTIVE]), 0)

    @mock.patch('the_tale.game.heroes.habilities.AbilitiesPrototype.next_ability_type', habilities.ABILITY_TYPE.BATTLE)
    def test_get_abilities_for_choose_all_slots_busy__battle(self):
        passive_abilities = [a for a in [a(level=a.MAX_LEVEL) for a in habilities.ABILITIES.values()] if a.activation_type.is_PASSIVE and a.type.is_BATTLE]
        for ability in passive_abilities[:c.ABILITIES_PASSIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        active_abilities = [a for a in [a(level=a.MAX_LEVEL) for a in habilities.ABILITIES.values()] if a.activation_type.is_ACTIVE and a.type.is_BATTLE]
        for ability in active_abilities[:c.ABILITIES_ACTIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        for i in range(100):
            abilities = self.hero.abilities.get_for_choose()
            self.assertEqual(len(abilities), 0)

    @mock.patch('the_tale.game.heroes.habilities.AbilitiesPrototype.next_ability_type', habilities.ABILITY_TYPE.BATTLE)
    def test_get_abilities_for_choose_all_slots_busy_but_one_not_max_level__battle(self):
        passive_abilities = [a for a in [a(level=a.MAX_LEVEL) for a in list(battle_abilities.ABILITIES.values())] if a.activation_type.is_PASSIVE and a.availability.value & habilities.ABILITY_AVAILABILITY.FOR_PLAYERS.value and a.type.is_BATTLE]
        for ability in passive_abilities[:c.ABILITIES_PASSIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        active_abilities = [a for a in [a(level=a.MAX_LEVEL) for a in list(battle_abilities.ABILITIES.values())] if a.activation_type.is_ACTIVE and a.availability.value & habilities.ABILITY_AVAILABILITY.FOR_PLAYERS.value and a.type.is_BATTLE]
        for ability in active_abilities[:c.ABILITIES_ACTIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        ability = random.choice([ability for ability in list(self.hero.abilities.abilities.values()) if ability.TYPE.is_BATTLE])
        ability.level -= 1

        for i in range(100):
            abilities = self.hero.abilities.get_for_choose()
            self.assertEqual(abilities, [ability.__class__(level=ability.level+1)])

    @mock.patch('the_tale.game.heroes.habilities.AbilitiesPrototype.next_ability_type', habilities.ABILITY_TYPE.BATTLE)
    def test_get_abilities_for_choose_all_slots_busy_and_all_not_max_level__battle(self):
        passive_abilities = [a for a in [a(level=1) for a in list(habilities.ABILITIES.values())] if a.activation_type.is_PASSIVE and a.type.is_BATTLE]
        for ability in passive_abilities[:c.ABILITIES_PASSIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        active_abilities = [a for a in [a(level=1) for a in list(habilities.ABILITIES.values())] if a.activation_type.is_ACTIVE and a.type.is_BATTLE]
        for ability in active_abilities[:c.ABILITIES_ACTIVE_MAXIMUM]:
            self.hero.abilities.add(ability.get_id(), ability.level)

        for i in range(100):
            abilities = self.hero.abilities.get_for_choose()
            self.assertEqual(len(abilities), c.ABILITIES_OLD_ABILITIES_FOR_CHOOSE_MAXIMUM)


class HeroQuestsTest(utils_testcase.TestCase):

    def setUp(self):
        super(HeroQuestsTest, self).setUp()

        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        account = self.accounts_factory.create_account(is_fast=True)

        self.hero = logic.load_hero(account_id=account.id)

        self.place = places_storage.places.all()[0]
        self.person = self.place.persons[0]


    def test_character_quests__hometown(self):
        self.assertFalse(quests_relations.QUESTS.HOMETOWN in [quest for quest, priority in self.hero.get_quests_priorities()])

        self.hero.preferences.set(relations.PREFERENCE_TYPE.PLACE, self.place)
        self.hero.position.set_place(self.place)
        self.assertFalse(quests_relations.QUESTS.HOMETOWN in [quest for quest, priority in self.hero.get_quests_priorities()])

        self.hero.position.set_coordinates(0, 0, 0, 0, 0)
        self.assertTrue(quests_relations.QUESTS.HOMETOWN in [quest for quest, priority in self.hero.get_quests_priorities()])

    def test_character_quests__friend(self):
        self.assertFalse(quests_relations.QUESTS.HELP_FRIEND in [quest for quest, priority in self.hero.get_quests_priorities()])

        self.hero.preferences.set(relations.PREFERENCE_TYPE.FRIEND, self.person)
        self.hero.position.set_place(self.place)
        self.assertFalse(quests_relations.QUESTS.HELP_FRIEND in [quest for quest, priority in self.hero.get_quests_priorities()])

        self.hero.position.set_coordinates(0, 0, 0, 0, 0)
        self.assertTrue(quests_relations.QUESTS.HELP_FRIEND in [quest for quest, priority in self.hero.get_quests_priorities()])

    def test_character_quests__enemy(self):
        self.assertFalse(quests_relations.QUESTS.INTERFERE_ENEMY in [quest for quest, priority in self.hero.get_quests_priorities()])

        self.hero.preferences.set(relations.PREFERENCE_TYPE.ENEMY, self.person)
        self.hero.position.set_place(self.place)
        self.assertFalse(quests_relations.QUESTS.INTERFERE_ENEMY in [quest for quest, priority in self.hero.get_quests_priorities()])

        self.hero.position.set_coordinates(0, 0, 0, 0, 0)
        self.assertTrue(quests_relations.QUESTS.INTERFERE_ENEMY in [quest for quest, priority in self.hero.get_quests_priorities()])

    def test_character_quests__hunt(self):
        self.assertFalse(quests_relations.QUESTS.HUNT in [quest for quest, priority in self.hero.get_quests_priorities()])
        self.hero.preferences.set(relations.PREFERENCE_TYPE.MOB, mobs_storage.mobs.all()[0])
        self.assertTrue(quests_relations.QUESTS.HUNT in [quest for quest, priority in self.hero.get_quests_priorities()])

    def test_character_quests_searchsmith_with_preferences_without_artifact(self):
        self.hero.equipment._remove_all()
        self.hero.preferences.set(relations.PREFERENCE_TYPE.EQUIPMENT_SLOT, relations.EQUIPMENT_SLOT.PLATE)
        logic.save_hero(self.hero)

        self.assertTrue(quests_relations.QUESTS.SEARCH_SMITH in [quest for quest, priority in self.hero.get_quests_priorities()])

    def test_character_quests_searchsmith_with_preferences_with_artifact(self):
        self.hero.preferences.set(relations.PREFERENCE_TYPE.EQUIPMENT_SLOT, relations.EQUIPMENT_SLOT.PLATE)
        logic.save_hero(self.hero)

        self.assertTrue(self.hero.equipment.get(relations.EQUIPMENT_SLOT.PLATE) is not None)
        self.assertTrue(quests_relations.QUESTS.SEARCH_SMITH in [quest for quest, priority in self.hero.get_quests_priorities()])

    def test_unique_quests__pilgrimage(self):
        self.assertFalse(quests_relations.QUESTS.PILGRIMAGE in [quest for quest, priority in self.hero.get_quests_priorities()])

        self.place.set_modifier(places_modifiers.CITY_MODIFIERS.HOLY_CITY)
        self.hero.position.set_place(self.place)
        self.assertFalse(quests_relations.QUESTS.PILGRIMAGE in [quest for quest, priority in self.hero.get_quests_priorities()])

        self.hero.position.set_coordinates(0, 0, 0, 0, 0)
        self.assertTrue(quests_relations.QUESTS.PILGRIMAGE in [quest for quest, priority in self.hero.get_quests_priorities()])

    def test_get_minimum_created_time_of_active_quests(self):
        with mock.patch('the_tale.game.quests.container.QuestsContainer.min_quest_created_time', datetime.datetime.now() - datetime.timedelta(days=1)):
            logic.save_hero(self.hero)

        account = self.accounts_factory.create_account()
        hero = logic.load_hero(account_id=account.id)

        test_time = datetime.datetime.now() - datetime.timedelta(days=2)

        with mock.patch('the_tale.game.quests.container.QuestsContainer.min_quest_created_time', test_time):
            logic.save_hero(hero)

        # not there are no another quests an get_minimum_created_time_of_active_quests return now()
        self.assertEqual(test_time, logic.get_minimum_created_time_of_active_quests())

    def prepair_quest_priority_preferences(self, friend_priorities=(0, 0), enemy_priorities=(0, 0)):
        friend = self.place_1.persons[0]
        friend.attrs.friends_quests_priority_bonus = friend_priorities[0]
        friend.attrs.enemies_quests_priority_bonus = friend_priorities[1]

        enemy = self.place_2.persons[0]
        enemy.attrs.friends_quests_priority_bonus = enemy_priorities[0]
        enemy.attrs.enemies_quests_priority_bonus = enemy_priorities[1]

        self.hero.preferences.set(relations.PREFERENCE_TYPE.FRIEND, friend)
        self.hero.preferences.set(relations.PREFERENCE_TYPE.ENEMY, enemy)

    def test_modify_quest_priority(self):
        self.prepair_quest_priority_preferences()

        self.assertEqual(self.hero.modify_quest_priority(quests_relations.QUESTS.HELP_FRIEND), quests_relations.QUESTS.HELP_FRIEND.priority)
        self.assertEqual(self.hero.modify_quest_priority(quests_relations.QUESTS.INTERFERE_ENEMY), quests_relations.QUESTS.INTERFERE_ENEMY.priority)

    @mock.patch('the_tale.game.heroes.habits.Peacefulness.interval', game_relations.HABIT_PEACEFULNESS_INTERVAL.RIGHT_3)
    def test_modify_quest_priority__friend(self):
        self.prepair_quest_priority_preferences()

        self.assertTrue(self.hero.modify_quest_priority(quests_relations.QUESTS.HELP_FRIEND) > quests_relations.QUESTS.HELP_FRIEND.priority)
        self.assertEqual(self.hero.modify_quest_priority(quests_relations.QUESTS.INTERFERE_ENEMY), quests_relations.QUESTS.INTERFERE_ENEMY.priority)

    @mock.patch('the_tale.game.heroes.habits.Peacefulness.interval', game_relations.HABIT_PEACEFULNESS_INTERVAL.LEFT_3)
    def test_modify_quest_priority__enemy(self):
        self.prepair_quest_priority_preferences()

        self.assertEqual(self.hero.modify_quest_priority(quests_relations.QUESTS.HELP_FRIEND), quests_relations.QUESTS.HELP_FRIEND.priority)
        self.assertTrue(self.hero.modify_quest_priority(quests_relations.QUESTS.INTERFERE_ENEMY)> quests_relations.QUESTS.INTERFERE_ENEMY.priority)

    def test_modify_quest_priority__from_person(self):
        self.prepair_quest_priority_preferences((1, 2), (3, 4))

        self.assertEqual(self.hero.modify_quest_priority(quests_relations.QUESTS.HELP_FRIEND), quests_relations.QUESTS.HELP_FRIEND.priority + 1)
        self.assertEqual(self.hero.modify_quest_priority(quests_relations.QUESTS.INTERFERE_ENEMY), quests_relations.QUESTS.INTERFERE_ENEMY.priority + 4)


class HeroUiInfoTest(utils_testcase.TestCase):

    def setUp(self):
        super(HeroUiInfoTest, self).setUp()

        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        account = self.accounts_factory.create_account(is_fast=True)

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(account)
        self.hero = self.storage.accounts_to_heroes[account.id]

    def test_is_ui_caching_required(self):
        self.assertTrue(self.hero.is_ui_caching_required) # new hero must be cached, since player, who created him, is in game
        self.hero.ui_caching_started_at -= datetime.timedelta(seconds=conf.heroes_settings.UI_CACHING_TIME + 1)
        self.assertFalse(self.hero.is_ui_caching_required)


    ########################
    # recache required
    ########################

    @mock.patch('the_tale.game.heroes.objects.Hero.is_ui_continue_caching_required', classmethod(lambda cls, tm: True))
    def test_cached_ui_info_from_cache__from_cache_is_true__for_not_visited_heroes(self):
        self.hero.ui_caching_started_at -= datetime.timedelta(seconds=conf.heroes_settings.UI_CACHING_TIME + 1)
        logic.save_hero(self.hero)

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=True, patch_turns=None, for_last_turn=False)
        self.assertEqual(cmd_start_hero_caching.call_count, 1)
        self.assertEqual(ui_info.call_args, mock.call(actual_guaranteed=False))

    @mock.patch('the_tale.game.heroes.objects.Hero.is_ui_continue_caching_required', classmethod(lambda cls, tm: True))
    def test_cached_ui_info_for_hero__data_is_none(self):
        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=True, patch_turns=None, for_last_turn=False)

        self.assertEqual(cmd_start_hero_caching.call_count, 1)
        self.assertEqual(ui_info.call_args, mock.call(actual_guaranteed=False))

    @mock.patch('the_tale.game.heroes.objects.Hero.is_ui_continue_caching_required', classmethod(lambda cls, tm: True))
    def test_cached_ui_info_for_hero__data_is_none__game_stopped(self):
        game_prototypes.GameState.stop()

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=True, patch_turns=None, for_last_turn=False)
        self.assertEqual(cmd_start_hero_caching.call_count, 0)
        self.assertEqual(ui_info.call_args, mock.call(actual_guaranteed=False))


    @mock.patch('dext.common.utils.cache.get', get_simple_cache_data)
    def test_cached_ui_info_for_hero__continue_caching_required__cache_exists(self):
        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=True, patch_turns=None, for_last_turn=False)
        self.assertEqual(cmd_start_hero_caching.call_count, 1)
        self.assertEqual(ui_info.call_count, 0)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_ui_continue_caching_required', classmethod(lambda cls, tm: True))
    @mock.patch('dext.common.utils.cache.get', lambda x: None)
    def test_cached_ui_info_for_hero__continue_caching_required__cache_not_exists(self):
        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=True, patch_turns=None, for_last_turn=False)

        self.assertEqual(cmd_start_hero_caching.call_count, 1)
        self.assertEqual(ui_info.call_args, mock.call(actual_guaranteed=False))

    @mock.patch('dext.common.utils.cache.get', get_simple_cache_data)
    def test_cached_ui_info_for_hero__continue_caching_required__game_stopped__cache_exists(self):
        game_prototypes.GameState.stop()

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=True, patch_turns=None, for_last_turn=False)
        self.assertEqual(cmd_start_hero_caching.call_count, 0)
        self.assertEqual(ui_info.call_count, 0)

    @mock.patch('dext.common.utils.cache.get', lambda x: None)
    def test_cached_ui_info_for_hero__continue_caching_required__game_stopped__cache_not_exists(self):
        game_prototypes.GameState.stop()

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info', mock.Mock(return_value=get_simple_cache_data())) as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=True, patch_turns=None, for_last_turn=False)
        self.assertEqual(cmd_start_hero_caching.call_count, 0)
        self.assertEqual(ui_info.call_args, mock.call(actual_guaranteed=False))

    @mock.patch('dext.common.utils.cache.get', lambda x: get_simple_cache_data(ui_caching_started_at=time.time()))
    def test_cached_ui_info_for_hero__continue_caching_not_required(self):
        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=True, patch_turns=None, for_last_turn=False)
        self.assertEqual(cmd_start_hero_caching.call_count, 0)
        self.assertEqual(ui_info.call_count, 0)


    ########################
    # recache not required
    ########################
    @mock.patch('the_tale.game.heroes.objects.Hero.is_ui_continue_caching_required', classmethod(lambda cls, tm: True))
    def test_cached_ui_info_from_cache__from_cache_is_true__for_not_visited_heroes__recache_not_required(self):
        self.hero.ui_caching_started_at -= datetime.timedelta(seconds=conf.heroes_settings.UI_CACHING_TIME + 1)
        logic.save_hero(self.hero)

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=False, patch_turns=None, for_last_turn=False)
        self.assertEqual(cmd_start_hero_caching.call_count, 0)
        self.assertEqual(ui_info.call_args, mock.call(actual_guaranteed=False))

    @mock.patch('the_tale.game.heroes.objects.Hero.is_ui_continue_caching_required', classmethod(lambda cls, tm: True))
    def test_cached_ui_info_for_hero__data_is_none__recache_not_required(self):
        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=False, patch_turns=None, for_last_turn=False)

        self.assertEqual(cmd_start_hero_caching.call_count, 0)
        self.assertEqual(ui_info.call_args, mock.call(actual_guaranteed=False))

    @mock.patch('the_tale.game.heroes.objects.Hero.is_ui_continue_caching_required', classmethod(lambda cls, tm: True))
    def test_cached_ui_info_for_hero__data_is_none__game_stopped__recache_not_required(self):
        game_prototypes.GameState.stop()

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=False, patch_turns=None, for_last_turn=False)
        self.assertEqual(cmd_start_hero_caching.call_count, 0)
        self.assertEqual(ui_info.call_args, mock.call(actual_guaranteed=False))


    @mock.patch('dext.common.utils.cache.get', get_simple_cache_data)
    def test_cached_ui_info_for_hero__continue_caching_required__cache_exists__recache_not_required(self):
        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=False, patch_turns=None, for_last_turn=False)
        self.assertEqual(cmd_start_hero_caching.call_count, 0)
        self.assertEqual(ui_info.call_count, 0)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_ui_continue_caching_required', classmethod(lambda cls, tm: True))
    @mock.patch('dext.common.utils.cache.get', lambda x: None)
    def test_cached_ui_info_for_hero__continue_caching_required__cache_not_exists__recache_not_required(self):
        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=False, patch_turns=None, for_last_turn=False)

        self.assertEqual(cmd_start_hero_caching.call_count, 0)
        self.assertEqual(ui_info.call_args, mock.call(actual_guaranteed=False))

    @mock.patch('dext.common.utils.cache.get', get_simple_cache_data)
    def test_cached_ui_info_for_hero__continue_caching_required__game_stopped__cache_exists__recache_not_required(self):
        game_prototypes.GameState.stop()

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=False, patch_turns=None, for_last_turn=False)
        self.assertEqual(cmd_start_hero_caching.call_count, 0)
        self.assertEqual(ui_info.call_count, 0)

    @mock.patch('dext.common.utils.cache.get', lambda x: None)
    def test_cached_ui_info_for_hero__continue_caching_required__game_stopped__cache_not_exists__recache_not_required(self):
        game_prototypes.GameState.stop()

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=False, patch_turns=None, for_last_turn=False)
        self.assertEqual(cmd_start_hero_caching.call_count, 0)
        self.assertEqual(ui_info.call_args, mock.call(actual_guaranteed=False))

    @mock.patch('dext.common.utils.cache.get', lambda x: get_simple_cache_data(ui_caching_started_at=time.time()))
    def test_cached_ui_info_for_hero__continue_caching_not_required__recache_not_required(self):
        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_start_hero_caching') as cmd_start_hero_caching:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=False, patch_turns=None, for_last_turn=False)
        self.assertEqual(cmd_start_hero_caching.call_count, 0)
        self.assertEqual(ui_info.call_count, 0)


    @mock.patch('dext.common.utils.cache.get', lambda x: {'ui_caching_started_at': time.time(),
                                                          'a': 1,
                                                          'b': 2,
                                                          'c': 3,
                                                          'd': 4,
                                                          'patch_turn': 666,
                                                          'action': {'data': None},
                                                          'changed_fields': ['b', 'c', 'changed_fields', 'patch_turn']})
    def test_cached_ui_info_for_hero__make_patch(self):
        data = objects.Hero.cached_ui_info_for_hero(self.hero.account_id, recache_if_required=False, patch_turns=[666], for_last_turn=False)
        self.assertEqual(data,
                         {'b': 2,
                          'c': 3,
                          'patch_turn': 666})

    def test_cached_ui_info_for_hero__turn_in_patch_turns(self):
        old_info = self.hero.ui_info(actual_guaranteed=True, old_info=None)
        old_info['patch_turn'] = 666
        old_info['changed_fields'].extend(field for field in old_info.keys() if random.random() < 0.5)

        with mock.patch('dext.common.utils.cache.get', lambda x: copy.deepcopy(old_info)):
            data = self.hero.cached_ui_info_for_hero(account_id=self.hero.account_id, recache_if_required=False, patch_turns=[665, 666, 667], for_last_turn=False)

        self.assertNotEqual(data['patch_turn'], None)
        self.assertEqual(set(data.keys()) | set(('changed_fields',)), set(old_info['changed_fields']))


    def test_cached_ui_info_for_hero__turn_not_in_patch_turns(self):
        old_info = self.hero.ui_info(actual_guaranteed=True, old_info=None)
        old_info['patch_turn'] = 664
        old_info['changed_fields'].extend(field for field in old_info.keys() if random.random() < 0.5)

        with mock.patch('dext.common.utils.cache.get', lambda x: copy.deepcopy(old_info)):
            data = self.hero.cached_ui_info_for_hero(account_id=self.hero.account_id, recache_if_required=False, patch_turns=[665, 666, 667], for_last_turn=False)

        self.assertEqual(set(data.keys()) | set(('changed_fields',)),
                         set(self.hero.ui_info(actual_guaranteed=True, old_info=None).keys()))
        self.assertEqual(data['patch_turn'], None)

    def test_cached_ui_info_for_hero__actual_info(self):
        old_info = self.hero.ui_info(actual_guaranteed=True, old_info=None)
        old_info['action']['data'] = {'pvp__last_turn': 'last_turn',
                                      'pvp__actual': 'actual'}

        with mock.patch('dext.common.utils.cache.get', lambda x: copy.deepcopy(old_info)):
            data = self.hero.cached_ui_info_for_hero(account_id=self.hero.account_id, recache_if_required=False, patch_turns=None, for_last_turn=False)
            self.assertEqual(data['action']['data']['pvp'], 'actual')
            self.assertNotIn('pvp__last_turn', data['action']['data'])
            self.assertNotIn('pvp__actual', data['action']['data'])

            data = self.hero.cached_ui_info_for_hero(account_id=self.hero.account_id, recache_if_required=False, patch_turns=None, for_last_turn=True)
            self.assertEqual(data['action']['data']['pvp'], 'last_turn')
            self.assertNotIn('pvp__last_turn', data['action']['data'])
            self.assertNotIn('pvp__actual', data['action']['data'])


    def test_ui_info_patch(self):
        old_info = self.hero.ui_info(actual_guaranteed=True, old_info=None)

        patched_fields = set(field for field in old_info.keys() if random.random() < 0.5)
        patched_fields |= set(('changed_fields', 'actual_on_turn', 'patch_turn'))

        for field in patched_fields:
            old_info[field] = 'changed'

        new_info = self.hero.ui_info(actual_guaranteed=True, old_info=old_info)

        self.assertEqual(new_info['patch_turn'], old_info['actual_on_turn'])
        self.assertEqual(set(new_info['changed_fields']), patched_fields)

    def test_ui_info__always_changed_fields(self):
        old_info = self.hero.ui_info(actual_guaranteed=True, old_info=None)
        new_info = self.hero.ui_info(actual_guaranteed=True, old_info=old_info)

        self.assertEqual(set(new_info['changed_fields']), set(('changed_fields', 'actual_on_turn', 'patch_turn')))

    def test_ui_info__actual_guaranteed(self):
        self.assertEqual(self.hero.saved_at_turn, 0)

        self.assertEqual(self.hero.ui_info(actual_guaranteed=True)['actual_on_turn'], 0)
        self.assertEqual(self.hero.ui_info(actual_guaranteed=False)['actual_on_turn'], 0)

        turn.set(666)

        self.assertEqual(self.hero.ui_info(actual_guaranteed=True)['actual_on_turn'], 666)
        self.assertEqual(self.hero.ui_info(actual_guaranteed=False)['actual_on_turn'], 0)

        logic.save_hero(self.hero)

        self.assertTrue(self.hero.saved_at_turn, 666)

        self.assertEqual(self.hero.ui_info(actual_guaranteed=True)['actual_on_turn'], 666)
        self.assertEqual(self.hero.ui_info(actual_guaranteed=False)['actual_on_turn'], 666)

    def test_ui_caching_timeout_greate_then_turn_delta(self):
        self.assertTrue(conf.heroes_settings.UI_CACHING_TIMEOUT > c.TURN_DELTA)

    def test_is_ui_continue_caching_required(self):
        self.assertTrue(objects.Hero.is_ui_continue_caching_required(0))
        self.assertFalse(objects.Hero.is_ui_continue_caching_required(time.time() - (conf.heroes_settings.UI_CACHING_TIME - conf.heroes_settings.UI_CACHING_CONTINUE_TIME - 1)))
        self.assertTrue(objects.Hero.is_ui_continue_caching_required(time.time() - (conf.heroes_settings.UI_CACHING_TIME - conf.heroes_settings.UI_CACHING_CONTINUE_TIME + 1)))
        self.assertTrue(objects.Hero.is_ui_continue_caching_required(time.time() - conf.heroes_settings.UI_CACHING_TIME))
