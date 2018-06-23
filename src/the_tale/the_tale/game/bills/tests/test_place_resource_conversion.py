
import smart_imports

smart_imports.all()


class PlaceResourceConversionTests(helpers.BaseTestPrototypes):

    def setUp(self):
        super(PlaceResourceConversionTests, self).setUp()

        self.conversion_1, self.conversion_2 = helpers.choose_conversions()

        self.bill_data = bills.place_resource_conversion.PlaceResourceConversion(place_id=self.place1.id,
                                                 conversion=self.conversion_1)

        self.bill = prototypes.BillPrototype.create(self.account1, 'bill-1-caption', self.bill_data,
                                         chronicle_on_accepted='chronicle-on-accepted')


    def test_create(self):
        self.assertEqual(self.bill.data.place_id, self.place1.id)
        self.assertEqual(self.bill.data.conversion, self.conversion_1)
        self.assertEqual(self.bill.data.old_name_forms, self.place1.utg_name)

        self.assertEqual(self.bill.data.place.id, self.place1.id)

        self.assertEqual(self.bill.data.old_name_forms, self.place1.utg_name)

        self.assertFalse(self.bill.data.place_name_changed)

    def test_user_form_initials(self):
        self.assertEqual(self.bill.data.user_form_initials(),
                         {'place': self.bill.data.place_id,
                          'conversion': self.bill.data.conversion})

    def test_actors(self):
        self.assertEqual(set(id(a) for a in self.bill_data.actors), set([id(self.place1)]))

    def test_update(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'new-caption',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted',
                                                         'place': self.place2.id,
                                                         'conversion': self.conversion_2})
        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = prototypes.BillPrototype.get_by_id(self.bill.id)

        self.assertEqual(self.bill.data.place_id, self.place2.id)
        self.assertEqual(self.bill.data.conversion, self.conversion_2)
        self.assertEqual(self.bill.data.old_name_forms, self.place2.utg_name)

        self.assertEqual(self.bill.data.place.id, self.place2.id)

        self.assertEqual(self.bill.data.old_name_forms, self.place2.utg_name)

        self.assertFalse(self.bill.data.place_name_changed)


    def test_form_validation__success(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'long caption',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted',
                                                         'place': self.place1.id,
                                                         'conversion': self.conversion_1})
        self.assertTrue(form.is_valid())

    @mock.patch('the_tale.game.balance.constants.PLACE_MAX_BILLS_NUMBER', 0)
    def test_user_form_validation__maximum_bills_reached(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'long caption',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted',
                                                         'place': self.place1.id,
                                                         'conversion': self.conversion_1})
        self.assertFalse(form.is_valid())


    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def apply_bill(self):
        prototypes.VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        prototypes.VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.FOR)

        form = bills.place_resource_conversion.PlaceResourceConversion.ModeratorForm({'caption': 'long caption',
                                                      'chronicle_on_accepted': 'chronicle-on-accepted',
                                                      'place': self.place1.id,
                                                      'conversion': self.conversion_1,
                                                      'approved': True})
        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)

        self.assertEqual(len(places_storage.resource_exchanges.all()), 0)

        self.assertTrue(self.bill.apply())

    def test_apply(self):

        old_storage_version = places_storage.resource_exchanges._version

        self.apply_bill()

        self.assertNotEqual(old_storage_version, places_storage.resource_exchanges._version)
        self.assertEqual(len(places_storage.resource_exchanges.all()), 1)

        bill = prototypes.BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state.is_ACCEPTED)

        exchange = places_storage.resource_exchanges.all()[0]

        self.assertEqual(exchange.place_1.id, self.place1.id)
        self.assertEqual(exchange.place_2, None)
        self.assertEqual(exchange.resource_1, self.conversion_1.resource_from)
        self.assertEqual(exchange.resource_2, self.conversion_1.resource_to)
        self.assertEqual(exchange.bill_id, bill.id)

    def test_decline__success(self):
        self.apply_bill()

        old_storage_version = places_storage.resource_exchanges._version

        decliner = prototypes.BillPrototype.create(self.account1, 'bill-1-caption', self.bill_data, chronicle_on_accepted='chronicle-on-accepted')

        self.bill.decline(decliner)

        self.assertNotEqual(old_storage_version, places_storage.resource_exchanges._version)

        self.assertEqual(len(places_storage.resource_exchanges.all()), 0)


    def test_decline__no_excange(self):
        self.apply_bill()

        places_prototypes.ResourceExchangePrototype._db_all().delete()

        places_storage.resource_exchanges.refresh()

        self.assertEqual(len(places_storage.resource_exchanges.all()), 0)

        old_storage_version = places_storage.resource_exchanges._version

        decliner = prototypes.BillPrototype.create(self.account1, 'bill-1-caption', self.bill_data, chronicle_on_accepted='chronicle-on-accepted')

        self.bill.decline(decliner)

        self.assertEqual(old_storage_version, places_storage.resource_exchanges._version)


    def test_end__success(self):
        self.apply_bill()

        old_storage_version = places_storage.resource_exchanges._version

        self.bill.end()

        self.assertNotEqual(old_storage_version, places_storage.resource_exchanges._version)

        self.assertEqual(len(places_storage.resource_exchanges.all()), 0)

    def test_end__no_excange(self):
        self.apply_bill()

        places_prototypes.ResourceExchangePrototype._db_all().delete()

        places_storage.resource_exchanges.refresh()

        self.assertEqual(len(places_storage.resource_exchanges.all()), 0)

        old_storage_version = places_storage.resource_exchanges._version

        self.bill.end()

        self.assertEqual(old_storage_version, places_storage.resource_exchanges._version)
