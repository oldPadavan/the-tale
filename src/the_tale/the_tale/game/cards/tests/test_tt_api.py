
import smart_imports

smart_imports.all()


class TTStorageAPiTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()
        tt_api.debug_clear_service()

        companions_models.CompanionRecord.objects.all().delete()
        companions_storage.companions.refresh()

        for rarity, rarity_abilities in companions_tests_helpers.RARITIES_ABILITIES.items():
            companions_logic.create_random_companion_record('%s companion' % rarity,
                                                            mode=companions_relations.MODE.AUTOMATIC,
                                                            abilities=rarity_abilities,
                                                            state=companions_relations.STATE.ENABLED)


        self.cards = [objects.Card(cards.CARD.KEEPERS_GOODS_COMMON, uid=uuid.uuid4()),
                      objects.Card(cards.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4()),
                      objects.Card(cards.CARD.KEEPERS_GOODS_LEGENDARY, uid=uuid.uuid4()),
                      cards.CARD.GET_COMPANION_UNCOMMON.effect.create_card(cards.CARD.GET_COMPANION_UNCOMMON, available_for_auction=True),
                      objects.Card(cards.CARD.KEEPERS_GOODS_COMMON, uid=uuid.uuid4()),
                      objects.Card(cards.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())]

    def test_load_no_cards(self):
        cards = tt_api.load_cards(666)
        self.assertEqual(cards, {})

    def fill_storage(self):
        tt_api.change_cards(account_id=666,
                            operation_type='#test',
                            to_add=[self.cards[0], self.cards[1], self.cards[3]],
                            to_remove=[])

        tt_api.change_cards(account_id=777,
                            operation_type='#test',
                            to_add=[self.cards[4]],
                            to_remove=[])

        tt_api.change_cards(account_id=666,
                            operation_type='#test',
                            to_add=[self.cards[2], self.cards[5]],
                            to_remove=[self.cards[1]])

    def test_change_and_load(self):
        self.fill_storage()

        cards = tt_api.load_cards(666)

        self.assertEqual(cards, {card.uid: card for card in [self.cards[0], self.cards[2], self.cards[3], self.cards[5]]})

    def test_has_card(self):
        self.fill_storage()

        self.assertTrue(tt_api.has_cards(666, [self.cards[0].uid, self.cards[3].uid]))
        self.assertFalse(tt_api.has_cards(666, [self.cards[0].uid, self.cards[4].uid]))

    def test_change_cards_owner(self):

        tt_api.change_cards(account_id=666,
                            operation_type='#test',
                            to_add=[self.cards[0], self.cards[1], self.cards[3]],
                            to_remove=[])

        tt_api.change_cards_owner(old_owner_id=666,
                                  new_owner_id=888,
                                  operation_type='#test-move',
                                  new_storage=relations.STORAGE.FAST,
                                  cards_ids=[self.cards[0].uid, self.cards[3].uid])

        self.assertTrue(tt_api.has_cards(666, [self.cards[1].uid]))
        self.assertFalse(tt_api.has_cards(666, [self.cards[0].uid, self.cards[3].uid]))

        self.assertFalse(tt_api.has_cards(888, [self.cards[1].uid]))
        self.assertTrue(tt_api.has_cards(888, [self.cards[0].uid, self.cards[3].uid]))
