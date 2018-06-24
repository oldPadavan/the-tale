
import smart_imports

smart_imports.all()


class LogicTests(utils_testcase.TestCase):

    def setUp(self):
        super(LogicTests, self).setUp()

        game_logic.create_test_map()

    def test_create_companion_record(self):
        name = names.generator().get_test_name()
        description = 'test description'

        type = beings_relations.TYPE.random()
        dedication = relations.DEDICATION.random()
        archetype = game_relations.ARCHETYPE.random()
        max_health = 10
        mode = relations.MODE.random()
        communication_verbal = beings_relations.COMMUNICATION_VERBAL.random()
        communication_gestures = beings_relations.COMMUNICATION_GESTURES.random()
        communication_telepathic = beings_relations.COMMUNICATION_TELEPATHIC.random()
        intellect_level = beings_relations.INTELLECT_LEVEL.random()

        with self.check_delta(models.CompanionRecord.objects.count, 1):
            with self.check_changed(lambda: storage.companions._version):
                with self.check_delta(storage.companions.__len__, 1):
                    companion_record = logic.create_companion_record(utg_name=name,
                                                                     description=description,
                                                                     type=type,
                                                                     max_health=max_health,
                                                                     dedication=dedication,
                                                                     archetype=archetype,
                                                                     mode=mode,
                                                                     abilities=helpers.FAKE_ABILITIES_CONTAINER_1,
                                                                     communication_verbal=communication_verbal,
                                                                     communication_gestures=communication_gestures,
                                                                     communication_telepathic=communication_telepathic,
                                                                     intellect_level=intellect_level,
                                                                     structure=beings_relations.STRUCTURE.STRUCTURE_2,
                                                                     features=frozenset((beings_relations.FEATURE.FEATURE_1, beings_relations.FEATURE.FEATURE_3)),
                                                                     movement=beings_relations.MOVEMENT.MOVEMENT_4,
                                                                     body=beings_relations.BODY.BODY_5,
                                                                     size=beings_relations.SIZE.SIZE_1,
                                                                     orientation=beings_relations.ORIENTATION.HORIZONTAL,
                                                                     weapons=[artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.WEAPON_1,
                                                                                                       material=tt_artifacts_relations.MATERIAL.MATERIAL_1,
                                                                                                       power_type=artifacts_relations.ARTIFACT_POWER_TYPE.NEUTRAL),
                                                                              artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.WEAPON_3,
                                                                                                       material=tt_artifacts_relations.MATERIAL.MATERIAL_3,
                                                                                                       power_type=artifacts_relations.ARTIFACT_POWER_TYPE.MOST_PHYSICAL)])

        self.assertTrue(companion_record.state.is_DISABLED)

        self.assertEqual(companion_record.name, name.normal_form())
        self.assertEqual(companion_record.utg_name, name)
        self.assertEqual(companion_record.description, description)
        self.assertEqual(companion_record.type, type)
        self.assertEqual(companion_record.max_health, max_health)
        self.assertEqual(companion_record.archetype, archetype)
        self.assertEqual(companion_record.mode, mode)
        self.assertEqual(companion_record.dedication, dedication)
        self.assertEqual(companion_record.abilities, helpers.FAKE_ABILITIES_CONTAINER_1)
        self.assertEqual(companion_record.communication_verbal, communication_verbal)
        self.assertEqual(companion_record.communication_gestures, communication_gestures)
        self.assertEqual(companion_record.communication_telepathic, communication_telepathic)
        self.assertEqual(companion_record.intellect_level, intellect_level)

        self.assertTrue(companion_record.structure.is_STRUCTURE_2)
        self.assertEqual(companion_record.features, frozenset((beings_relations.FEATURE.FEATURE_1, beings_relations.FEATURE.FEATURE_3)))
        self.assertTrue(companion_record.movement.is_MOVEMENT_4)
        self.assertTrue(companion_record.body.is_BODY_5)
        self.assertTrue(companion_record.size.is_SIZE_1)
        self.assertTrue(companion_record.orientation.is_HORIZONTAL)
        self.assertEqual(companion_record.weapons, [artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.WEAPON_1,
                                                                             material=tt_artifacts_relations.MATERIAL.MATERIAL_1,
                                                                             power_type=artifacts_relations.ARTIFACT_POWER_TYPE.NEUTRAL),
                                                    artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.WEAPON_3,
                                                                             material=tt_artifacts_relations.MATERIAL.MATERIAL_3,
                                                                             power_type=artifacts_relations.ARTIFACT_POWER_TYPE.MOST_PHYSICAL)])

        model = models.CompanionRecord.objects.get(id=companion_record.id)

        loaded_companion = objects.CompanionRecord.from_model(model)

        self.assertEqual(loaded_companion, companion_record)

    def test_create_companion_record__set_state(self):
        companion_record = logic.create_companion_record(utg_name=names.generator().get_test_name(),
                                                         description='description',
                                                         type=beings_relations.TYPE.random(),
                                                         max_health=10,
                                                         dedication=relations.DEDICATION.random(),
                                                         archetype=game_relations.ARCHETYPE.random(),
                                                         mode=relations.MODE.random(),
                                                         abilities=helpers.FAKE_ABILITIES_CONTAINER_1,
                                                         communication_verbal=beings_relations.COMMUNICATION_VERBAL.random(),
                                                         communication_gestures=beings_relations.COMMUNICATION_GESTURES.random(),
                                                         communication_telepathic=beings_relations.COMMUNICATION_TELEPATHIC.random(),
                                                         intellect_level=beings_relations.INTELLECT_LEVEL.random(),
                                                         structure=beings_relations.STRUCTURE.random(),
                                                         features=frozenset((beings_relations.FEATURE.random(), beings_relations.FEATURE.random())),
                                                         movement=beings_relations.MOVEMENT.random(),
                                                         body=beings_relations.BODY.random(),
                                                         size=beings_relations.SIZE.random(),
                                                         orientation=beings_relations.ORIENTATION.random(),
                                                         weapons=[artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.random(),
                                                                                           material=tt_artifacts_relations.MATERIAL.random(),
                                                                                           power_type=artifacts_relations.ARTIFACT_POWER_TYPE.random())],
                                                         state=relations.STATE.ENABLED)

        self.assertTrue(companion_record.state.is_ENABLED)

    def test_create_companion_record__linguistics_restriction_setupped(self):
        with mock.patch('the_tale.linguistics.logic.sync_restriction') as sync_restriction:
            companion_record = logic.create_companion_record(utg_name=names.generator().get_test_name(),
                                                            description='description',
                                                            type=beings_relations.TYPE.random(),
                                                            max_health=10,
                                                            dedication=relations.DEDICATION.random(),
                                                            archetype=game_relations.ARCHETYPE.random(),
                                                            mode=relations.MODE.random(),
                                                            abilities=helpers.FAKE_ABILITIES_CONTAINER_1,
                                                            communication_verbal=beings_relations.COMMUNICATION_VERBAL.random(),
                                                            communication_gestures=beings_relations.COMMUNICATION_GESTURES.random(),
                                                            communication_telepathic=beings_relations.COMMUNICATION_TELEPATHIC.random(),
                                                            intellect_level=beings_relations.INTELLECT_LEVEL.random(),
                                                            structure=beings_relations.STRUCTURE.STRUCTURE_2,
                                                            features=frozenset((beings_relations.FEATURE.FEATURE_1, beings_relations.FEATURE.FEATURE_3)),
                                                            movement=beings_relations.MOVEMENT.MOVEMENT_4,
                                                            body=beings_relations.BODY.BODY_5,
                                                            size=beings_relations.SIZE.SIZE_1,
                                                            orientation=beings_relations.ORIENTATION.random(),
                                                            weapons=[artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.WEAPON_1,
                                                                                              material=tt_artifacts_relations.MATERIAL.MATERIAL_1,
                                                                                              power_type=artifacts_relations.ARTIFACT_POWER_TYPE.NEUTRAL),
                                                                     artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.WEAPON_3,
                                                                                              material=tt_artifacts_relations.MATERIAL.MATERIAL_3,
                                                                                              power_type=artifacts_relations.ARTIFACT_POWER_TYPE.MOST_PHYSICAL)],
                                                            state=relations.STATE.ENABLED,)

        self.assertEqual(sync_restriction.call_args_list, [mock.call(group=linguistics_relations.TEMPLATE_RESTRICTION_GROUP.COMPANION,
                                                                     external_id=companion_record.id,
                                                                     name=companion_record.name)])

    def test_update_companion_record(self):
        old_name = names.generator().get_test_name(name='old')
        new_name = names.generator().get_test_name(name='new')

        type = beings_relations.TYPE.random()
        dedication = relations.DEDICATION.random()
        archetype = game_relations.ARCHETYPE.random()
        mode = relations.MODE.random()
        max_health = 666
        communication_verbal = beings_relations.COMMUNICATION_VERBAL.random()
        communication_gestures = beings_relations.COMMUNICATION_GESTURES.random()
        communication_telepathic = beings_relations.COMMUNICATION_TELEPATHIC.random()
        intellect_level = beings_relations.INTELLECT_LEVEL.random()

        structure = beings_relations.STRUCTURE.random()
        features = frozenset((beings_relations.FEATURE.random(), beings_relations.FEATURE.random()))
        movement = beings_relations.MOVEMENT.random()
        body = beings_relations.BODY.random()
        size = beings_relations.SIZE.random()
        orientation = beings_relations.ORIENTATION.random()
        weapons = [artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.random(),
                                            material=tt_artifacts_relations.MATERIAL.random(),
                                            power_type=artifacts_relations.ARTIFACT_POWER_TYPE.random())]

        companion_record = logic.create_companion_record(utg_name=old_name,
                                                         description='old-description',
                                                         type=beings_relations.TYPE.random(),
                                                         max_health=10,
                                                         dedication=relations.DEDICATION.random(),
                                                         archetype=game_relations.ARCHETYPE.random(),
                                                         mode=relations.MODE.random(),
                                                         abilities=helpers.FAKE_ABILITIES_CONTAINER_1,
                                                         communication_verbal=beings_relations.COMMUNICATION_VERBAL.random(),
                                                         communication_gestures=beings_relations.COMMUNICATION_GESTURES.random(),
                                                         communication_telepathic=beings_relations.COMMUNICATION_TELEPATHIC.random(),
                                                         intellect_level=beings_relations.INTELLECT_LEVEL.random(),
                                                         structure=beings_relations.STRUCTURE.random(),
                                                         features=frozenset((beings_relations.FEATURE.random(), beings_relations.FEATURE.random())),
                                                         movement=beings_relations.MOVEMENT.random(),
                                                         body=beings_relations.BODY.random(),
                                                         size=beings_relations.SIZE.random(),
                                                         orientation=beings_relations.ORIENTATION.random(),
                                                         weapons=[artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.random(),
                                                                                           material=tt_artifacts_relations.MATERIAL.random(),
                                                                                           power_type=artifacts_relations.ARTIFACT_POWER_TYPE.random())])

        with self.check_increased(lambda: models.CompanionRecord.objects.get(id=companion_record.id).updated_at):
            with self.check_not_changed(lambda: models.CompanionRecord.objects.get(id=companion_record.id).created_at):
                with self.check_not_changed(models.CompanionRecord.objects.count):
                    with self.check_changed(lambda: storage.companions._version):
                        with self.check_not_changed(storage.companions.__len__):
                            logic.update_companion_record(companion_record,
                                                          utg_name=new_name,
                                                          description='new-description',
                                                          type=type,
                                                          max_health=max_health,
                                                          dedication=dedication,
                                                          archetype=archetype,
                                                          mode=mode,
                                                          abilities=helpers.FAKE_ABILITIES_CONTAINER_2,
                                                          communication_verbal=communication_verbal,
                                                          communication_gestures=communication_gestures,
                                                          communication_telepathic=communication_telepathic,
                                                          intellect_level=intellect_level,
                                                          structure=structure,
                                                          features=features,
                                                          movement=movement,
                                                          body=body,
                                                          size=size,
                                                          orientation=orientation,
                                                          weapons=weapons)

        self.assertEqual(companion_record.name, new_name.normal_form())
        self.assertEqual(companion_record.description, 'new-description')
        self.assertEqual(companion_record.type, type)
        self.assertEqual(companion_record.dedication, dedication)
        self.assertEqual(companion_record.max_health, max_health)
        self.assertEqual(companion_record.mode, mode)
        self.assertEqual(companion_record.archetype, archetype)
        self.assertEqual(companion_record.abilities, helpers.FAKE_ABILITIES_CONTAINER_2)
        self.assertEqual(companion_record.communication_verbal, communication_verbal)
        self.assertEqual(companion_record.communication_gestures, communication_gestures)
        self.assertEqual(companion_record.communication_telepathic, communication_telepathic)
        self.assertEqual(companion_record.intellect_level, intellect_level)
        self.assertEqual(companion_record.structure, structure)
        self.assertEqual(companion_record.features, features)
        self.assertEqual(companion_record.movement, movement)
        self.assertEqual(companion_record.body, body)
        self.assertEqual(companion_record.size, size)
        self.assertEqual(companion_record.orientation, orientation)
        self.assertEqual(companion_record.weapons, weapons)

        storage.companions.refresh()

        companion_record = storage.companions[companion_record.id]

        self.assertEqual(companion_record.name, new_name.normal_form())
        self.assertEqual(companion_record.description, 'new-description')
        self.assertEqual(companion_record.type, type)
        self.assertEqual(companion_record.dedication, dedication)
        self.assertEqual(companion_record.max_health, max_health)
        self.assertEqual(companion_record.mode, mode)
        self.assertEqual(companion_record.archetype, archetype)
        self.assertEqual(companion_record.abilities, helpers.FAKE_ABILITIES_CONTAINER_2)
        self.assertEqual(companion_record.communication_verbal, communication_verbal)
        self.assertEqual(companion_record.communication_gestures, communication_gestures)
        self.assertEqual(companion_record.communication_telepathic, communication_telepathic)
        self.assertEqual(companion_record.intellect_level, intellect_level)
        self.assertEqual(companion_record.structure, structure)
        self.assertEqual(companion_record.features, features)
        self.assertEqual(companion_record.movement, movement)
        self.assertEqual(companion_record.body, body)
        self.assertEqual(companion_record.size, size)
        self.assertEqual(companion_record.orientation, orientation)
        self.assertEqual(companion_record.weapons, weapons)

    def test_enable_companion_record(self):

        type = beings_relations.TYPE.random()
        dedication = relations.DEDICATION.random()
        archetype = game_relations.ARCHETYPE.random()
        mode = relations.MODE.random()
        max_health = 666
        communication_verbal = beings_relations.COMMUNICATION_VERBAL.random()
        communication_gestures = beings_relations.COMMUNICATION_GESTURES.random()
        communication_telepathic = beings_relations.COMMUNICATION_TELEPATHIC.random()
        intellect_level = beings_relations.INTELLECT_LEVEL.random()

        structure = beings_relations.STRUCTURE.random()
        features = frozenset((beings_relations.FEATURE.random(), beings_relations.FEATURE.random()))
        movement = beings_relations.MOVEMENT.random()
        body = beings_relations.BODY.random()
        size = beings_relations.SIZE.random()
        orientation = beings_relations.ORIENTATION.random()
        weapons = [artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.random(),
                                            material=tt_artifacts_relations.MATERIAL.random(),
                                            power_type=artifacts_relations.ARTIFACT_POWER_TYPE.random())]

        companion_record = logic.create_companion_record(utg_name=names.generator().get_test_name(name='old'),
                                                         description='old-description',
                                                         type=type,
                                                         max_health=max_health,
                                                         dedication=dedication,
                                                         archetype=archetype,
                                                         mode=mode,
                                                         abilities=helpers.FAKE_ABILITIES_CONTAINER_1,
                                                         communication_verbal=communication_verbal,
                                                         communication_gestures=communication_gestures,
                                                         communication_telepathic=communication_telepathic,
                                                         intellect_level=intellect_level,
                                                         structure=structure,
                                                         features=features,
                                                         movement=movement,
                                                         body=body,
                                                         size=size,
                                                         orientation=orientation,
                                                         weapons=weapons)

        with self.check_increased(lambda: models.CompanionRecord.objects.get(id=companion_record.id).updated_at):
            with self.check_not_changed(lambda: models.CompanionRecord.objects.get(id=companion_record.id).created_at):
                with self.check_not_changed(models.CompanionRecord.objects.count):
                    with self.check_changed(lambda: storage.companions._version):
                        with self.check_not_changed(storage.companions.__len__):
                            logic.enable_companion_record(companion_record)

        self.assertEqual(companion_record.description, 'old-description')
        self.assertEqual(companion_record.type, type)
        self.assertEqual(companion_record.dedication, dedication)
        self.assertEqual(companion_record.max_health, max_health)
        self.assertEqual(companion_record.archetype, archetype)
        self.assertEqual(companion_record.mode, mode)
        self.assertTrue(companion_record.state.is_ENABLED)
        self.assertEqual(companion_record.abilities, helpers.FAKE_ABILITIES_CONTAINER_1)
        self.assertEqual(companion_record.communication_verbal, communication_verbal)
        self.assertEqual(companion_record.communication_gestures, communication_gestures)
        self.assertEqual(companion_record.communication_telepathic, communication_telepathic)
        self.assertEqual(companion_record.intellect_level, intellect_level)
        self.assertEqual(companion_record.structure, structure)
        self.assertEqual(companion_record.features, features)
        self.assertEqual(companion_record.movement, movement)
        self.assertEqual(companion_record.body, body)
        self.assertEqual(companion_record.size, size)
        self.assertEqual(companion_record.orientation, orientation)
        self.assertEqual(companion_record.weapons, weapons)

        storage.companions.refresh()

        companion_record = storage.companions[companion_record.id]

        self.assertEqual(companion_record.description, 'old-description')
        self.assertEqual(companion_record.type, type)
        self.assertEqual(companion_record.dedication, dedication)
        self.assertEqual(companion_record.max_health, max_health)
        self.assertEqual(companion_record.archetype, archetype)
        self.assertEqual(companion_record.mode, mode)
        self.assertTrue(companion_record.state.is_ENABLED)
        self.assertEqual(companion_record.abilities, helpers.FAKE_ABILITIES_CONTAINER_1)
        self.assertEqual(companion_record.communication_verbal, communication_verbal)
        self.assertEqual(companion_record.communication_gestures, communication_gestures)
        self.assertEqual(companion_record.communication_telepathic, communication_telepathic)
        self.assertEqual(companion_record.intellect_level, intellect_level)
        self.assertEqual(companion_record.structure, structure)
        self.assertEqual(companion_record.features, features)
        self.assertEqual(companion_record.movement, movement)
        self.assertEqual(companion_record.body, body)
        self.assertEqual(companion_record.size, size)
        self.assertEqual(companion_record.orientation, orientation)
        self.assertEqual(companion_record.weapons, weapons)

    def test_update_companion_record__linguistics_restrictions(self):
        old_name = names.generator().get_test_name(name='old')
        new_name = names.generator().get_test_name(name='new')

        companion_record = logic.create_companion_record(utg_name=old_name,
                                                         description='old-description',
                                                         type=beings_relations.TYPE.random(),
                                                         max_health=10,
                                                         dedication=relations.DEDICATION.random(),
                                                         archetype=game_relations.ARCHETYPE.random(),
                                                         mode=relations.MODE.random(),
                                                         abilities=helpers.FAKE_ABILITIES_CONTAINER_1,
                                                         communication_verbal=beings_relations.COMMUNICATION_VERBAL.random(),
                                                         communication_gestures=beings_relations.COMMUNICATION_GESTURES.random(),
                                                         communication_telepathic=beings_relations.COMMUNICATION_TELEPATHIC.random(),
                                                         intellect_level=beings_relations.INTELLECT_LEVEL.random(),
                                                         structure=beings_relations.STRUCTURE.random(),
                                                         features=frozenset((beings_relations.FEATURE.random(), beings_relations.FEATURE.random())),
                                                         movement=beings_relations.MOVEMENT.random(),
                                                         body=beings_relations.BODY.random(),
                                                         size=beings_relations.SIZE.random(),
                                                         orientation=beings_relations.ORIENTATION.random(),
                                                         weapons=[artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.random(),
                                                                                           material=tt_artifacts_relations.MATERIAL.random(),
                                                                                           power_type=artifacts_relations.ARTIFACT_POWER_TYPE.random())])

        with mock.patch('the_tale.linguistics.logic.sync_restriction') as sync_restriction:
            logic.update_companion_record(companion_record,
                                          utg_name=new_name,
                                          description='new-description',
                                          type=beings_relations.TYPE.random(),
                                          max_health=10,
                                          dedication=relations.DEDICATION.random(),
                                          archetype=game_relations.ARCHETYPE.random(),
                                          mode=relations.MODE.random(),
                                          abilities=helpers.FAKE_ABILITIES_CONTAINER_2,
                                          communication_verbal=beings_relations.COMMUNICATION_VERBAL.random(),
                                          communication_gestures=beings_relations.COMMUNICATION_GESTURES.random(),
                                          communication_telepathic=beings_relations.COMMUNICATION_TELEPATHIC.random(),
                                          intellect_level=beings_relations.INTELLECT_LEVEL.random(),
                                          structure=beings_relations.STRUCTURE.random(),
                                          features=frozenset((beings_relations.FEATURE.random(), beings_relations.FEATURE.random())),
                                          movement=beings_relations.MOVEMENT.random(),
                                          body=beings_relations.BODY.random(),
                                          size=beings_relations.SIZE.random(),
                                          orientation=beings_relations.ORIENTATION.random(),
                                          weapons=[artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.random(),
                                                                            material=tt_artifacts_relations.MATERIAL.random(),
                                                                            power_type=artifacts_relations.ARTIFACT_POWER_TYPE.random())])

        self.assertEqual(sync_restriction.call_args_list, [mock.call(group=linguistics_relations.TEMPLATE_RESTRICTION_GROUP.COMPANION,
                                                                     external_id=companion_record.id,
                                                                     name=new_name.normal_form())])

    def test_create_companion(self):
        companion_record = logic.create_companion_record(utg_name=names.generator().get_test_name(),
                                                         description='description',
                                                         type=beings_relations.TYPE.random(),
                                                         max_health=10,
                                                         dedication=relations.DEDICATION.random(),
                                                         archetype=game_relations.ARCHETYPE.random(),
                                                         mode=relations.MODE.random(),
                                                         abilities=helpers.FAKE_ABILITIES_CONTAINER_1,
                                                         communication_verbal=beings_relations.COMMUNICATION_VERBAL.random(),
                                                         communication_gestures=beings_relations.COMMUNICATION_GESTURES.random(),
                                                         communication_telepathic=beings_relations.COMMUNICATION_TELEPATHIC.random(),
                                                         intellect_level=beings_relations.INTELLECT_LEVEL.random(),
                                                         structure=beings_relations.STRUCTURE.random(),
                                                         features=frozenset((beings_relations.FEATURE.random(), beings_relations.FEATURE.random())),
                                                         movement=beings_relations.MOVEMENT.random(),
                                                         body=beings_relations.BODY.random(),
                                                         size=beings_relations.SIZE.random(),
                                                         orientation=beings_relations.ORIENTATION.random(),
                                                         weapons=[artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.random(),
                                                                                           material=tt_artifacts_relations.MATERIAL.random(),
                                                                                           power_type=artifacts_relations.ARTIFACT_POWER_TYPE.random())],
                                                         state=relations.STATE.ENABLED)

        companion = logic.create_companion(companion_record)

        self.assertEqual(companion.record.id, companion_record.id)
        self.assertEqual(companion.health, companion_record.max_health)
        self.assertEqual(companion.coherence, 0)
