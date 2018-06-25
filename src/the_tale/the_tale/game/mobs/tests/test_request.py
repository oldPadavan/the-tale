
import smart_imports

smart_imports.all()


class PostMixin(object):
    def get_create_data(self, name='mob name'):
        word = names.generator().get_test_name(name=name)

        data = linguistics_helpers.get_word_post_data(word, prefix='name')

        data.update({'level': 666,
                     'terrains': [map_relations.TERRAIN.PLANE_GRASS, map_relations.TERRAIN.HILLS_GRASS],
                     'abilities': ['hit', 'strong_hit', 'sidestep'],
                     'type': beings_relations.TYPE.CIVILIZED,
                     'archetype': game_relations.ARCHETYPE.NEUTRAL,
                     'description': 'mob description',
                     'communication_verbal': beings_relations.COMMUNICATION_VERBAL.CAN,
                     'communication_gestures': beings_relations.COMMUNICATION_GESTURES.CAN,
                     'communication_telepathic': beings_relations.COMMUNICATION_TELEPATHIC.CAN,
                     'intellect_level': beings_relations.INTELLECT_LEVEL.NORMAL,

                     'structure': beings_relations.STRUCTURE.STRUCTURE_1,
                     'features': [beings_relations.FEATURE.FEATURE_1, beings_relations.FEATURE.FEATURE_7],
                     'movement': beings_relations.MOVEMENT.MOVEMENT_2,
                     'body': beings_relations.BODY.BODY_3,
                     'size': beings_relations.SIZE.SIZE_4,
                     'orientation': beings_relations.ORIENTATION.HORIZONTAL,
                     'weapon_1': artifacts_relations.STANDARD_WEAPON.WEAPON_1,
                     'material_1': tt_artifacts_relations.MATERIAL.MATERIAL_1,
                     'power_type_1': artifacts_relations.ARTIFACT_POWER_TYPE.NEUTRAL,
                     'weapon_2': artifacts_relations.STANDARD_WEAPON.WEAPON_10,
                     'material_2': tt_artifacts_relations.MATERIAL.MATERIAL_10,
                     'power_type_2': artifacts_relations.ARTIFACT_POWER_TYPE.MOST_MAGICAL})

        return data

    def get_update_data(self, name='new name'):
        word = names.generator().get_test_name(name=name)

        data = linguistics_helpers.get_word_post_data(word, prefix='name')

        data.update({'level': 667,
                     'terrains': [map_relations.TERRAIN.PLANE_JUNGLE, map_relations.TERRAIN.HILLS_JUNGLE],
                     'abilities': ['hit', 'speedup'],
                     'type': beings_relations.TYPE.ANIMAL,
                     'archetype': game_relations.ARCHETYPE.MAGICAL,
                     'description': 'new description',
                     'communication_verbal': beings_relations.COMMUNICATION_VERBAL.CAN_NOT,
                     'communication_gestures': beings_relations.COMMUNICATION_GESTURES.CAN_NOT,
                     'communication_telepathic': beings_relations.COMMUNICATION_TELEPATHIC.CAN_NOT,
                     'intellect_level': beings_relations.INTELLECT_LEVEL.LOW,

                     'structure': beings_relations.STRUCTURE.STRUCTURE_1,
                     'features': [beings_relations.FEATURE.FEATURE_1, beings_relations.FEATURE.FEATURE_7],
                     'movement': beings_relations.MOVEMENT.MOVEMENT_2,
                     'body': beings_relations.BODY.BODY_3,
                     'size': beings_relations.SIZE.SIZE_4,
                     'orientation': beings_relations.ORIENTATION.VERTICAL,
                     'weapon_1': artifacts_relations.STANDARD_WEAPON.WEAPON_1,
                     'material_1': tt_artifacts_relations.MATERIAL.MATERIAL_1,
                     'power_type_1': artifacts_relations.ARTIFACT_POWER_TYPE.MOST_PHYSICAL,
                     'weapon_2': artifacts_relations.STANDARD_WEAPON.WEAPON_10,
                     'material_2': tt_artifacts_relations.MATERIAL.MATERIAL_10,
                     'power_type_2': artifacts_relations.ARTIFACT_POWER_TYPE.PHYSICAL})

        return data

    def get_moderate_data(self, approved=True):
        data = self.get_update_data()
        data['approved'] = approved
        data['uuid'] = 'new_uuid'
        return data


class BaseTestRequests(utils_testcase.TestCase):

    def setUp(self):
        super(BaseTestRequests, self).setUp()
        storage.mobs.sync(force=True)

        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()
        self.account_3 = self.accounts_factory.create_account()

        self.request_login(self.account_1.email)

        group_create = utils_permissions.sync_group('create mob', ['mobs.create_mobrecord'])
        group_add = utils_permissions.sync_group('add mob', ['mobs.moderate_mobrecord'])

        group_create.user_set.add(self.account_2._model)
        group_add.user_set.add(self.account_3._model)


class TestIndexRequests(BaseTestRequests):

    def setUp(self):
        super(TestIndexRequests, self).setUp()

    def test_no_mobs(self):
        models.MobRecord.objects.all().delete()
        storage.mobs.clear()
        self.check_html_ok(self.request_html(django_reverse('guide:mobs:')), texts=(('pgf-no-mobs-message', 1),))

    def test_simple(self):
        texts = ['mob_1', 'mob_2', 'mob_3', ('pgf-create-mob-button', 0), ('pgf-filter-state', 0)]
        self.check_html_ok(self.request_html(django_reverse('guide:mobs:')), texts=texts)

    def test_create_mob_button(self):
        self.request_logout()
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(django_reverse('guide:mobs:')), texts=[('pgf-create-mob-button', 1)])

    def test_mob_state_filter(self):
        self.request_logout()
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(django_reverse('guide:mobs:')), texts=[('pgf-filter-state', 1)])

        self.request_logout()
        self.request_login(self.account_3.email)
        self.check_html_ok(self.request_html(django_reverse('guide:mobs:')), texts=[('pgf-filter-state', 1)])

    def test_disabled_mobs(self):
        logic.create_random_mob_record(uuid='bandit', state=relations.MOB_RECORD_STATE.DISABLED)
        texts = ['mob_1', 'mob_2', 'mob_3', ('bandit', 0)]
        self.check_html_ok(self.request_html(django_reverse('guide:mobs:')), texts=texts)

    def test_filter_by_state_no_mobs_message(self):
        self.check_html_ok(self.request_html(django_reverse('guide:mobs:')+('?state=%d' % relations.MOB_RECORD_STATE.DISABLED.value)), texts=(('pgf-no-mobs-message', 1),))

    def test_filter_by_state(self):
        texts = ['mob_1', 'mob_2', 'mob_3']
        self.check_html_ok(self.request_html(django_reverse('guide:mobs:')+('?state=%d' % relations.MOB_RECORD_STATE.ENABLED.value)), texts=texts)

    def test_filter_by_terrain_no_mobs_message(self):
        models.MobRecord.objects.all().delete()
        storage.mobs.clear()
        logic.create_random_mob_record(uuid='bandit', terrains=[map_relations.TERRAIN.PLANE_GRASS])
        self.check_html_ok(self.request_html(django_reverse('guide:mobs:')+('?terrain=%d' % map_relations.TERRAIN.HILLS_GRASS.value)), texts=(('pgf-no-mobs-message', 1),))

    def test_filter_by_terrain(self):
        models.MobRecord.objects.all().delete()
        storage.mobs.clear()
        logic.create_random_mob_record(uuid='bandit', terrains=[map_relations.TERRAIN.PLANE_GRASS])
        self.check_html_ok(self.request_html(django_reverse('guide:mobs:')+('?terrain=%d' % map_relations.TERRAIN.PLANE_GRASS.value)), texts=['bandit'])

    def test_filter_by_type_no_mobs_message(self):
        models.MobRecord.objects.all().delete()
        storage.mobs.clear()
        logic.create_random_mob_record(uuid='bandit', type=beings_relations.TYPE.COLDBLOODED)
        self.check_html_ok(self.request_html(dext_urls.url('guide:mobs:', type=beings_relations.TYPE.CIVILIZED.value)), texts=(('pgf-no-mobs-message', 1),))

    def test_filter_by_type(self):
        models.MobRecord.objects.all().delete()
        storage.mobs.clear()
        logic.create_random_mob_record(uuid='bandit', type=beings_relations.TYPE.COLDBLOODED)
        self.check_html_ok(self.request_html(dext_urls.url('guide:mobs:', type=beings_relations.TYPE.COLDBLOODED.value)), texts=['bandit'])


class TestNewRequests(BaseTestRequests):

    def setUp(self):
        super(TestNewRequests, self).setUp()

    def test_unlogined(self):
        self.request_logout()
        request_url = django_reverse('game:mobs:new')
        self.check_redirect(request_url, accounts_logic.login_page_url(request_url))

    def test_create_rights(self):
        self.check_html_ok(self.request_html(django_reverse('game:mobs:new')), texts=[('mobs.create_mob_rights_required', 1),
                                                                             ('pgf-new-mob-form', 0)])

    def test_simple(self):
        self.request_logout()
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(django_reverse('game:mobs:new')), texts=[('pgf-new-mob-form', 2)])


class TestCreateRequests(BaseTestRequests, PostMixin):

    def setUp(self):
        super(TestCreateRequests, self).setUp()

        self.request_logout()
        self.request_login(self.account_2.email)

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(django_reverse('game:mobs:create'), self.get_create_data()), 'common.login_required')

    def test_create_rights(self):
        self.request_logout()
        self.request_login(self.account_1.email)
        self.check_ajax_error(self.client.post(django_reverse('game:mobs:create'), self.get_create_data()), 'mobs.create_mob_rights_required')

    def test_form_errors(self):
        self.check_ajax_error(self.client.post(django_reverse('game:mobs:create'), {}), 'mobs.create.form_errors')

    def test_simple(self):
        self.assertEqual(models.MobRecord.objects.count(), 3)

        response = self.client.post(django_reverse('game:mobs:create'), self.get_create_data())

        self.assertEqual(models.MobRecord.objects.count(), 4)
        mob_record = logic.construct_from_model(models.MobRecord.objects.all().order_by('-created_at')[0])

        self.check_ajax_ok(response, data={'next_url': django_reverse('guide:mobs:show', args=[mob_record.id])})

        self.assertEqual(mob_record.name, 'mob name-нс,ед,им')
        self.assertEqual(mob_record.level, 666)
        self.assertEqual(mob_record.terrains, frozenset([map_relations.TERRAIN.PLANE_GRASS, map_relations.TERRAIN.HILLS_GRASS]))
        self.assertEqual(mob_record.abilities, frozenset(['hit', 'strong_hit', 'sidestep']) )
        self.assertEqual(mob_record.description, 'mob description')
        self.assertTrue(mob_record.state.is_DISABLED)
        self.assertTrue(mob_record.type.is_CIVILIZED)
        self.assertTrue(mob_record.archetype.is_NEUTRAL)
        self.assertTrue(mob_record.editor_id, self.account_2.id)
        self.assertTrue(mob_record.communication_verbal.is_CAN)
        self.assertTrue(mob_record.communication_gestures.is_CAN)
        self.assertTrue(mob_record.communication_telepathic.is_CAN)
        self.assertTrue(mob_record.intellect_level.is_NORMAL)

    def test_duplicate_name(self):
        self.client.post(django_reverse('game:mobs:create'), self.get_create_data())

        with self.check_not_changed(models.MobRecord.objects.count):
            self.check_ajax_error(self.client.post(django_reverse('game:mobs:create'), self.get_create_data()), 'mobs.create.duplicate_name')


class TestShowRequests(BaseTestRequests):

    def setUp(self):
        super(TestShowRequests, self).setUp()

    def test_wrong_mob_id(self):
        self.check_html_ok(self.request_html(django_reverse('guide:mobs:show', args=['adsd'])), texts=[('mobs.mob.wrong_format', 1)])

    def test_no_mob(self):
        self.check_html_ok(self.request_html(django_reverse('guide:mobs:show', args=[666])), texts=[('mobs.mob.not_found', 1)], status_code=404)

    def test_disabled_mob_declined(self):
        mob = logic.create_random_mob_record(uuid='bandit', state=relations.MOB_RECORD_STATE.DISABLED)
        self.check_html_ok(self.request_html(django_reverse('guide:mobs:show', args=[mob.id])), texts=[('mobs.mob_disabled', 1)], status_code=404)

    def test_disabled_mob_accepted_for_create_rights(self):
        self.request_logout()
        self.request_login(self.account_2.email)
        mob = logic.create_random_mob_record(uuid='bandit', state=relations.MOB_RECORD_STATE.DISABLED)
        self.check_html_ok(self.request_html(django_reverse('guide:mobs:show', args=[mob.id])), texts=[mob.name.capitalize()])

    def test_disabled_mob_accepted_for_add_rights(self):
        self.request_logout()
        self.request_login(self.account_3.email)
        mob = logic.create_random_mob_record(uuid='bandit', state=relations.MOB_RECORD_STATE.DISABLED)
        self.check_html_ok(self.request_html(django_reverse('guide:mobs:show', args=[mob.id])), texts=[mob.name.capitalize()])

    def test_simple(self):
        mob = logic.construct_from_model(models.MobRecord.objects.all()[0])
        self.check_html_ok(self.request_html(django_reverse('guide:mobs:show', args=[mob.id])), texts=[(mob.name.capitalize(), 5),
                                                                                              ('pgf-no-description', 0),
                                                                                              ('pgf-moderate-button', 0),
                                                                                              ('pgf-edit-button', 0),
                                                                                              'pgf-no-folclor'])

    def test_folclor(self):
        from the_tale.blogs.tests import helpers as blogs_helpers

        blogs_helpers.prepair_forum()

        mob = logic.construct_from_model(models.MobRecord.objects.all()[0])

        blogs_helpers.create_post_for_meta_object(self.account_1, 'folclor-1-caption', 'folclor-1-text', meta_relations.Mob.create_from_object(mob))
        blogs_helpers.create_post_for_meta_object(self.account_2, 'folclor-2-caption', 'folclor-2-text', meta_relations.Mob.create_from_object(mob))

        self.check_html_ok(self.request_html(dext_urls.url('guide:mobs:show', mob.id)), texts=[('pgf-no-folclor', 0),
                                                                                     'folclor-1-caption',
                                                                                     'folclor-2-caption'])

    def test_no_description(self):
        mob = storage.mobs.all()[0]
        mob.description = ''
        logic.save_mob_record(mob)
        self.check_html_ok(self.request_html(django_reverse('guide:mobs:show', args=[mob.id])), texts=[('pgf-no-description', 1)])

    def test_edit_button(self):
        self.request_logout()
        self.request_login(self.account_2.email)
        mob = logic.construct_from_model(models.MobRecord.objects.all()[0])
        self.check_html_ok(self.request_html(django_reverse('guide:mobs:show', args=[mob.id])), texts=[('pgf-moderate-button', 0),
                                                                                                ('pgf-edit-button', 1)])

    def test_moderate_button(self):
        self.request_logout()
        self.request_login(self.account_3.email)
        mob = models.MobRecord.objects.all()[0]
        self.check_html_ok(self.request_html(django_reverse('guide:mobs:show', args=[mob.id])), texts=[('pgf-moderate-button', 1),
                                                                                                ('pgf-edit-button', 0)])


class TestInfoRequests(BaseTestRequests):

    def setUp(self):
        super(TestInfoRequests, self).setUp()

    def test_wrong_mob_id(self):
        self.check_html_ok(self.request_html(dext_urls.url('guide:mobs:info', 'adsd')), texts=[('mobs.mob.wrong_format', 1)])

    def test_no_mob(self):
        self.check_html_ok(self.request_html(dext_urls.url('guide:mobs:info', 666)), texts=[('mobs.mob.not_found', 1)], status_code=404)

    def test_disabled_mob_declined(self):
        mob = logic.create_random_mob_record(uuid='bandit', state=relations.MOB_RECORD_STATE.DISABLED)
        self.check_html_ok(self.request_html(dext_urls.url('guide:mobs:info', mob.id)), texts=[('mobs.mob_disabled', 1)], status_code=404)

    def test_disabled_mob_accepted_for_create_rights(self):
        self.request_logout()
        self.request_login(self.account_2.email)
        mob = logic.create_random_mob_record(uuid='bandit', state=relations.MOB_RECORD_STATE.DISABLED)
        self.check_html_ok(self.request_html(dext_urls.url('guide:mobs:info', mob.id)), texts=[mob.name.capitalize()])

    def test_disabled_mob_accepted_for_add_rights(self):
        self.request_logout()
        self.request_login(self.account_3.email)
        mob = logic.create_random_mob_record(uuid='bandit', state=relations.MOB_RECORD_STATE.DISABLED)
        self.check_html_ok(self.request_html(dext_urls.url('guide:mobs:info', mob.id)), texts=[mob.name.capitalize()])

    def test_simple(self):
        mob = logic.construct_from_model(models.MobRecord.objects.all()[0])
        self.check_html_ok(self.request_html(dext_urls.url('guide:mobs:info', mob.id)), texts=[(mob.name.capitalize(), 1),
                                                                                   ('pgf-no-description', 0),
                                                                                   ('pgf-moderate-button', 0),
                                                                                   ('pgf-edit-button', 0),
                                                                                   'pgf-no-folclor'])

    def test_folclor(self):
        from the_tale.blogs.tests import helpers as blogs_helpers

        blogs_helpers.prepair_forum()

        mob = logic.construct_from_model(models.MobRecord.objects.all()[0])

        blogs_helpers.create_post_for_meta_object(self.account_1, 'folclor-1-caption', 'folclor-1-text', meta_relations.Mob.create_from_object(mob))
        blogs_helpers.create_post_for_meta_object(self.account_2, 'folclor-2-caption', 'folclor-2-text', meta_relations.Mob.create_from_object(mob))

        self.check_html_ok(self.request_html(dext_urls.url('guide:mobs:info', mob.id)), texts=[('pgf-no-folclor', 0),
                                                                                     'folclor-1-caption',
                                                                                     'folclor-2-caption'])


    def test_no_description(self):
        mob = storage.mobs.all()[0]
        mob.description = ''
        logic.save_mob_record(mob)
        self.check_html_ok(self.request_html(dext_urls.url('guide:mobs:info', mob.id)), texts=[('pgf-no-description', 1)])


class TestEditRequests(BaseTestRequests):

    def setUp(self):
        super(TestEditRequests, self).setUp()

        self.mob = storage.mobs.all()[0]
        self.mob.state = relations.MOB_RECORD_STATE.DISABLED
        logic.save_mob_record(self.mob)

    def test_unlogined(self):
        self.request_logout()
        request_url = django_reverse('game:mobs:edit', args=[self.mob.id])
        self.check_redirect(request_url, accounts_logic.login_page_url(request_url))

    def test_enabled_state(self):
        self.mob.state = relations.MOB_RECORD_STATE.ENABLED
        logic.save_mob_record(self.mob)
        self.check_html_ok(self.request_html(django_reverse('game:mobs:edit', args=[self.mob.id])), texts=[('mobs.disabled_state_required', 1),
                                                                                                  ('pgf-edit-mob-form', 0)])

    def test_create_rights(self):
        self.check_html_ok(self.request_html(django_reverse('game:mobs:edit', args=[self.mob.id])), texts=[('mobs.create_mob_rights_required', 1),
                                                                                                  ('pgf-edit-mob-form', 0)])

    def test_simple(self):
        self.request_logout()
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(django_reverse('game:mobs:edit', args=[self.mob.id])), texts=[('pgf-edit-mob-form', 2),
                                                                                                  self.mob.name,
                                                                                                  (self.mob.description, 1) ])


class TestUpdateRequests(BaseTestRequests, PostMixin):

    def setUp(self):
        super(TestUpdateRequests, self).setUp()

        self.request_logout()
        self.request_login(self.account_2.email)

        self.check_ajax_ok(self.client.post(django_reverse('game:mobs:create'), self.get_create_data()))
        self.mob = logic.construct_from_model(models.MobRecord.objects.all().order_by('-created_at')[0])

    def check_mob(self, mob, data):
        self.assertEqual(mob.name, data['name_0'])
        self.assertEqual(mob.level, data['level'])
        self.assertEqual(mob.terrains, frozenset(data['terrains']) )
        self.assertEqual(mob.abilities, frozenset(data['abilities']) )
        self.assertEqual(mob.description, data['description'])
        self.assertTrue(mob.state.is_DISABLED)
        self.assertEqual(mob.type, data['type'])
        self.assertEqual(mob.archetype, data['archetype'])
        self.assertEqual(mob.editor_id, self.account_2.id)
        self.assertEqual(mob.communication_verbal, data['communication_verbal'])
        self.assertEqual(mob.communication_gestures, data['communication_gestures'])
        self.assertEqual(mob.communication_telepathic, data['communication_telepathic'])
        self.assertEqual(mob.intellect_level, data['intellect_level'])

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(django_reverse('game:mobs:update', args=[self.mob.id]), self.get_update_data()), 'common.login_required')

    def test_create_rights(self):
        self.request_logout()
        self.request_login(self.account_1.email)
        self.check_ajax_error(self.client.post(django_reverse('game:mobs:update', args=[self.mob.id]), self.get_update_data()), 'mobs.create_mob_rights_required')
        self.check_mob(logic.load_by_id(self.mob.id), self.get_create_data())

    def test_form_errors(self):
        self.check_ajax_error(self.client.post(django_reverse('game:mobs:update', args=[self.mob.id]), {}), 'mobs.update.form_errors')
        self.check_mob(logic.load_by_id(self.mob.id), self.get_create_data())

    def test_simple(self):
        response = self.client.post(django_reverse('game:mobs:update', args=[self.mob.id]), self.get_update_data())

        mob_record = logic.load_by_id(self.mob.id)

        self.check_ajax_ok(response, data={'next_url': django_reverse('guide:mobs:show', args=[mob_record.id])})

        self.check_mob(mob_record, self.get_update_data())

    def test_duplicate_name(self):
        self.check_ajax_ok(self.client.post(django_reverse('game:mobs:create'), self.get_create_data(name='name-2-')))

        self.check_ajax_error(self.client.post(django_reverse('game:mobs:update', args=[self.mob.id]), self.get_update_data(name='name-2-')), 'mobs.update.duplicate_name')

        self.check_mob(logic.load_by_id(self.mob.id), self.get_create_data())

    def test_name_does_not_changed(self):
        self.check_ajax_ok(self.client.post(django_reverse('game:mobs:update', args=[self.mob.id]), self.get_update_data(name='mob name')))

        self.check_mob(logic.load_by_id(self.mob.id), self.get_update_data(name='mob name'))


class TestModerationPageRequests(BaseTestRequests):

    def setUp(self):
        super(TestModerationPageRequests, self).setUp()

        self.mob = storage.mobs.all()[0]
        self.mob.state = relations.MOB_RECORD_STATE.DISABLED
        logic.save_mob_record(self.mob)

    def test_unlogined(self):
        self.request_logout()
        request_url = django_reverse('game:mobs:moderate', args=[self.mob.id])
        self.check_redirect(request_url, accounts_logic.login_page_url(request_url))

    def test_moderate_rights(self):
        self.check_html_ok(self.request_html(django_reverse('game:mobs:moderate', args=[self.mob.id])), texts=[('mobs.moderate_mob_rights_required', 1),
                                                                                                        ('pgf-moderate-mob-form', 0)])

    def test_simple(self):
        self.request_logout()
        self.request_login(self.account_3.email)
        self.check_html_ok(self.request_html(django_reverse('game:mobs:moderate', args=[self.mob.id])), texts=[('pgf-moderate-mob-form', 2),
                                                                                                        self.mob.name,
                                                                                                        (self.mob.description, 1)])


class TestModerateRequests(BaseTestRequests, PostMixin):

    def setUp(self):
        super(TestModerateRequests, self).setUp()

        self.request_logout()
        self.request_login(self.account_2.email)

        self.check_ajax_ok(self.client.post(django_reverse('game:mobs:create'), self.get_create_data()))
        self.mob = logic.construct_from_model(models.MobRecord.objects.all().order_by('-created_at')[0])

        self.name = names.generator().get_test_name(name='new name')

        self.request_logout()
        self.request_login(self.account_3.email)

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(django_reverse('game:mobs:moderate', args=[self.mob.id]), self.get_moderate_data()), 'common.login_required')

    def test_moderate_rights(self):
        self.request_logout()
        self.request_login(self.account_1.email)
        self.check_ajax_error(self.client.post(django_reverse('game:mobs:moderate', args=[self.mob.id]), self.get_moderate_data()), 'mobs.moderate_mob_rights_required')
        self.assertEqual(logic.load_by_id(self.mob.id).uuid, self.mob.uuid)

    def test_form_errors(self):
        self.check_ajax_error(self.client.post(django_reverse('game:mobs:moderate', args=[self.mob.id]), {}), 'mobs.moderate.form_errors')
        self.assertEqual(logic.load_by_id(self.mob.id).uuid, self.mob.uuid)

    def test_simple(self):
        response = self.client.post(django_reverse('game:mobs:moderate', args=[self.mob.id]), self.get_moderate_data())

        mob_record = logic.load_by_id(self.mob.id)

        self.check_ajax_ok(response, data={'next_url': django_reverse('guide:mobs:show', args=[mob_record.id])})

        self.assertEqual(mob_record.uuid, self.mob.uuid)
        self.assertEqual(mob_record.name, 'new name-нс,ед,им')
        self.assertEqual(mob_record.utg_name, self.name)
        self.assertEqual(mob_record.level, 667)
        self.assertEqual(mob_record.terrains, frozenset([map_relations.TERRAIN.PLANE_JUNGLE, map_relations.TERRAIN.HILLS_JUNGLE]))
        self.assertEqual(mob_record.abilities, frozenset(['hit', 'speedup']) )
        self.assertEqual(mob_record.description, 'new description')
        self.assertTrue(mob_record.state.is_ENABLED)
        self.assertTrue(mob_record.type.is_ANIMAL)
        self.assertTrue(mob_record.archetype.is_MAGICAL)
        self.assertTrue(mob_record.editor_id, self.account_3.id)

    def test_simple_not_approved(self):
        self.check_ajax_ok(self.client.post(django_reverse('game:mobs:moderate', args=[self.mob.id]), self.get_moderate_data(approved=False)))

        mob_record = logic.load_by_id(self.mob.id)

        self.assertTrue(mob_record.state.is_DISABLED)
