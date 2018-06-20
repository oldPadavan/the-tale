
import smart_imports

smart_imports.all()


class HabilitiesNonBattleTest(utils_testcase.TestCase):

    def setUp(self):
        super(HabilitiesNonBattleTest, self).setUp()
        game_logic.create_test_map()

        account = self.accounts_factory.create_account()
        self.hero = logic.load_hero(account_id=account.id)

    def tearDown(self):
        pass

    def test_charisma(self):
        self.assertTrue(1.0 < nonbattle_abilities.CHARISMA().modify_attribute(relations.MODIFIERS.QUEST_MONEY_REWARD, 1.0))

    def test_huckster(self):
        self.assertTrue(1.0 > nonbattle_abilities.HUCKSTER().modify_attribute(relations.MODIFIERS.BUY_PRICE, 1.0))
        self.assertTrue(1.0 < nonbattle_abilities.HUCKSTER().modify_attribute(relations.MODIFIERS.SELL_PRICE, 1.0))

    def test_dandy(self):
        priorities = {record:record.priority for record in relations.ITEMS_OF_EXPENDITURE.records}
        priorities = nonbattle_abilities.DANDY().modify_attribute(relations.MODIFIERS.ITEMS_OF_EXPENDITURE_PRIORITIES, priorities)

        self.assertEqual(relations.ITEMS_OF_EXPENDITURE.INSTANT_HEAL.priority, priorities[relations.ITEMS_OF_EXPENDITURE.INSTANT_HEAL])
        self.assertEqual(relations.ITEMS_OF_EXPENDITURE.USELESS.priority, priorities[relations.ITEMS_OF_EXPENDITURE.USELESS])
        self.assertEqual(relations.ITEMS_OF_EXPENDITURE.IMPACT.priority, priorities[relations.ITEMS_OF_EXPENDITURE.IMPACT])

        self.assertTrue(relations.ITEMS_OF_EXPENDITURE.BUYING_ARTIFACT.priority < priorities[relations.ITEMS_OF_EXPENDITURE.BUYING_ARTIFACT])
        self.assertTrue(relations.ITEMS_OF_EXPENDITURE.SHARPENING_ARTIFACT.priority < priorities[relations.ITEMS_OF_EXPENDITURE.SHARPENING_ARTIFACT])
        self.assertTrue(relations.ITEMS_OF_EXPENDITURE.REPAIRING_ARTIFACT.priority < priorities[relations.ITEMS_OF_EXPENDITURE.REPAIRING_ARTIFACT])

    @mock.patch('the_tale.game.balance.constants.ARTIFACT_FOR_QUEST_PROBABILITY', 0)
    def test_businessman(self):
        self.assertFalse(any(self.hero.can_get_artifact_for_quest() for i in range(1000)))
        self.hero.abilities.add(nonbattle_abilities.BUSINESSMAN.get_id())
        self.assertTrue(any(self.hero.can_get_artifact_for_quest() for i in range(1000)))

    def test_picky(self):
        with self.check_increased(lambda: self.hero.rare_artifact_probability_multiplier):
            with self.check_increased(lambda: self.hero.epic_artifact_probability_multiplier):
                self.hero.abilities.add(nonbattle_abilities.PICKY.get_id())

    def test_ethereal_magnet(self):
        old_crit_chance = self.hero.might_crit_chance
        self.hero.abilities.add(nonbattle_abilities.ETHEREAL_MAGNET.get_id())
        self.assertTrue(self.hero.might_crit_chance > old_crit_chance)

    def test_wanderer(self):
        old_speed = self.hero.move_speed
        self.hero.abilities.add(nonbattle_abilities.WANDERER.get_id())
        self.assertTrue(self.hero.move_speed > old_speed)

    def test_gifted(self):
        old_experience_modifier = self.hero.experience_modifier

        self.hero.abilities.add(nonbattle_abilities.GIFTED.get_id())

        self.assertTrue(old_experience_modifier < self.hero.experience_modifier)

    def test_thrifty(self):
        self.assertEqual(self.hero.max_bag_size, c.MAX_BAG_SIZE)

        self.hero.abilities.add(nonbattle_abilities.THRIFTY.get_id())

        self.assertEqual(self.hero.max_bag_size, c.MAX_BAG_SIZE + 2)


    def test_diplomatic(self):
        old_power_modifier = self.hero.politics_power_multiplier()

        self.hero.abilities.add(nonbattle_abilities.DIPLOMATIC.get_id())

        self.assertTrue(old_power_modifier < self.hero.politics_power_multiplier())


    def test_open_minded(self):
        with self.check_increased(lambda: self.hero.habits_increase_modifier):
            self.hero.abilities.add(nonbattle_abilities.OPEN_MINDED.get_id())


    def test_selfish(self):
        from the_tale.game.quests import relations as quests_relations

        with self.check_increased(lambda: self.hero.modify_quest_priority(quests_relations.QUESTS.HUNT)):
            with self.check_not_changed(lambda: self.hero.modify_quest_priority(quests_relations.QUESTS.SPYING)):
                self.hero.abilities.add(nonbattle_abilities.SELFISH.get_id())
