
import smart_imports

smart_imports.all()


class DoNothingActionTest(utils_testcase.TestCase):

    @mock.patch('the_tale.game.actions.prototypes.ActionBase.get_description', lambda self: 'abrakadabra')
    def setUp(self):
        super(DoNothingActionTest, self).setUp()

        game_logic.create_test_map()

        account = self.accounts_factory.create_account(is_fast=True)

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(account)
        self.hero = self.storage.accounts_to_heroes[account.id]
        self.action_idl = self.hero.actions.current_action

        self.action_donothing = prototypes.ActionDoNothingPrototype.create(hero=self.hero, duration=7, messages_prefix='QUEST_HOMETOWN_JOURNAL_CHATTING', messages_probability=0.3)


    def tearDown(self):
        pass

    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_donothing.leader, True)
        self.assertEqual(self.action_donothing.textgen_id, 'QUEST_HOMETOWN_JOURNAL_CHATTING')
        self.assertEqual(self.action_donothing.percents_barier, 7)
        self.assertEqual(self.action_donothing.extra_probability, 0.3)
        self.assertEqual(self.action_donothing.bundle_id, self.action_idl.bundle_id)
        self.storage._test_save()

    def test_not_ready(self):
        self.storage.process_turn()
        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action, self.action_donothing)
        self.storage._test_save()

    def test_full(self):

        for i in range(7):
            self.assertEqual(len(self.hero.actions.actions_list), 2)
            self.assertTrue(self.action_donothing.leader)
            self.storage.process_turn(continue_steps_if_needed=False)
            turn.increment()

        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertTrue(self.action_idl.leader)

        self.storage._test_save()
