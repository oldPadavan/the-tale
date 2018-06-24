
import smart_imports

smart_imports.all()


class CompanionRecordForm(dext_forms.Form):

    name = linguistics_forms.WordField(word_type=utg_relations.WORD_TYPE.NOUN, label='Название')

    max_health = dext_fields.IntegerField(label='здоровье', min_value=c.COMPANIONS_MIN_HEALTH, max_value=c.COMPANIONS_MAX_HEALTH)

    type = dext_fields.RelationField(label='тип', relation=beings_relations.TYPE)
    dedication = dext_fields.RelationField(label='самоотверженность', relation=relations.DEDICATION)
    archetype = dext_fields.RelationField(label='архетип', relation=game_relations.ARCHETYPE)
    mode = dext_fields.RelationField(label='режим появления в игре', relation=relations.MODE)

    communication_verbal = dext_fields.RelationField(label='вербальное общение', relation=beings_relations.COMMUNICATION_VERBAL)
    communication_gestures = dext_fields.RelationField(label='невербальное общение', relation=beings_relations.COMMUNICATION_GESTURES)
    communication_telepathic = dext_fields.RelationField(label='телепатия', relation=beings_relations.COMMUNICATION_TELEPATHIC)

    intellect_level = dext_fields.RelationField(label='уровень интеллекта', relation=beings_relations.INTELLECT_LEVEL)

    abilities = companions_abilities_forms.AbilitiesField(label='', required=False)

    structure = dext_fields.RelationField(label='структура', relation=beings_relations.STRUCTURE, sort_key=lambda choice: choice[1])
    features = dext_fields.TypedMultipleChoiceField(label='особенности',
                                               choices=sorted(beings_relations.FEATURE.choices(), key=lambda choice: choice[1]),
                                               coerce=beings_relations.FEATURE.get_from_name)
    movement = dext_fields.RelationField(label='способ передвижения', relation=beings_relations.MOVEMENT)
    body = dext_fields.RelationField(label='форма тела', relation=beings_relations.BODY, sort_key=lambda choice: choice[1])
    size = dext_fields.RelationField(label='размер тела', relation=beings_relations.SIZE)
    orientation = dext_fields.RelationField(label='положение тела', relation=beings_relations.ORIENTATION)

    weapon_1 = dext_fields.RelationField(label='оружие 1', relation=artifacts_relations.STANDARD_WEAPON, sort_key=lambda choice: choice[1])
    material_1 = dext_fields.RelationField(label='материал оружия 1', relation=tt_artifacts_relations.MATERIAL, sort_key=lambda choice: choice[1])
    power_type_1 = dext_fields.RelationField(label='тип силы оружия 1', relation=artifacts_relations.ARTIFACT_POWER_TYPE)

    weapon_2 = dext_fields.RelationField(label='оружие 2', required=False, relation=artifacts_relations.STANDARD_WEAPON, sort_key=lambda choice: choice[1])
    material_2 = dext_fields.RelationField(label='материал оружия 2', required=False, relation=tt_artifacts_relations.MATERIAL, sort_key=lambda choice: choice[1])
    power_type_2 = dext_fields.RelationField(label='тип силы оружия 2', required=False, relation=artifacts_relations.ARTIFACT_POWER_TYPE)

    weapon_3 = dext_fields.RelationField(label='оружие 3', required=False, relation=artifacts_relations.STANDARD_WEAPON, sort_key=lambda choice: choice[1])
    material_3 = dext_fields.RelationField(label='материал оружия 3', required=False, relation=tt_artifacts_relations.MATERIAL, sort_key=lambda choice: choice[1])
    power_type_3 = dext_fields.RelationField(label='тип силы оружия 3', required=False, relation=artifacts_relations.ARTIFACT_POWER_TYPE)

    description = utils_bbcode.BBField(label='Описание', required=False)

    def clean_features(self):
        features = self.cleaned_data['features']

        if not features:
            return frozenset()

        return frozenset(features)

    def get_weapons(self):
        weapons = []

        if self.c.weapon_1 and self.c.material_1 and self.c.power_type_1:
            weapons.append(artifacts_objects.Weapon(weapon=self.c.weapon_1, material=self.c.material_1, power_type=self.c.power_type_1))

        if self.c.weapon_2 and self.c.material_2 and self.c.power_type_2:
            weapons.append(artifacts_objects.Weapon(weapon=self.c.weapon_2, material=self.c.material_2, power_type=self.c.power_type_2))

        if self.c.weapon_3 and self.c.material_3 and self.c.power_type_3:
            weapons.append(artifacts_objects.Weapon(weapon=self.c.weapon_3, material=self.c.material_3, power_type=self.c.power_type_3))

        return weapons

    @classmethod
    def get_initials(cls, companion):
        initials = {'description': companion.description,
                    'max_health': companion.max_health,
                    'type': companion.type,
                    'dedication': companion.dedication,
                    'archetype': companion.archetype,
                    'mode': companion.mode,
                    'abilities': companion.abilities,
                    'name': companion.utg_name,
                    'communication_verbal': companion.communication_verbal,
                    'communication_gestures': companion.communication_gestures,
                    'communication_telepathic': companion.communication_telepathic,
                    'intellect_level': companion.intellect_level,
                    'structure': companion.structure,
                    'features': list(companion.features),
                    'movement': companion.movement,
                    'body': companion.body,
                    'size': companion.size,
                    'orientation': companion.orientation}

        for i, weapon in enumerate(companion.weapons, start=1):
            initials['weapon_{}'.format(i)] = weapon.type
            initials['material_{}'.format(i)] = weapon.material
            initials['power_type_{}'.format(i)] = weapon.power_type

        return initials
