
import smart_imports

smart_imports.all()


class AbilityModifiersBase(prototypes.AbilityPrototype):

    INCOMING_MAGIC_DAMAGE_MODIFIER = [1, 1, 1, 1, 1]
    INCOMING_PHYSIC_DAMAGE_MODIFIER = [1, 1, 1, 1, 1]

    OUTCOMING_MAGIC_DAMAGE_MODIFIER = [1, 1, 1, 1, 1]
    OUTCOMING_PHYSIC_DAMAGE_MODIFIER = [1, 1, 1, 1, 1]

    @property
    def incoming_magic_damage_modifier(self): return self.INCOMING_MAGIC_DAMAGE_MODIFIER[self.level-1]

    @property
    def incoming_physic_damage_modifier(self): return self.INCOMING_PHYSIC_DAMAGE_MODIFIER[self.level-1]

    @property
    def outcoming_magic_damage_modifier(self): return self.OUTCOMING_MAGIC_DAMAGE_MODIFIER[self.level-1]

    @property
    def outcoming_physic_damage_modifier(self): return self.OUTCOMING_PHYSIC_DAMAGE_MODIFIER[self.level-1]

    def update_context(self, actor, enemy):
        actor.context.use_incoming_damage_modifier(self.incoming_physic_damage_modifier, self.incoming_magic_damage_modifier)
        actor.context.use_outcoming_damage_modifier(self.outcoming_physic_damage_modifier, self.outcoming_magic_damage_modifier)


class MAGE(AbilityModifiersBase):

    TYPE = relations.ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.PASSIVE

    NAME = 'Маг'
    normalized_name = NAME
    DESCRIPTION = 'Маг всё своё усердие направляет в совершенствование магических умений, поэтому имеет увеличенный магический урон, защиту от магии и уменьшенные физический урон и защиту от физических атак. Увеличение магических способностей сильнее, чем ослабление физических.'

    INCOMING_MAGIC_DAMAGE_MODIFIER =   [0.950, 0.900, 0.850, 0.800, 0.750]
    INCOMING_PHYSIC_DAMAGE_MODIFIER =  [1.025, 1.050, 1.075, 1.100, 1.125]

    OUTCOMING_MAGIC_DAMAGE_MODIFIER =  [1.050, 1.100, 1.150, 1.200, 1.250]
    OUTCOMING_PHYSIC_DAMAGE_MODIFIER = [0.975, 0.950, 0.925, 0.900, 0.875]


class WARRIOR(AbilityModifiersBase):

    TYPE = relations.ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.PASSIVE

    NAME = 'Воин'
    normalized_name = NAME
    DESCRIPTION = 'Воин большую часть времени тратит на физические тренировки, благодаря чему наносит больший физический урон, имеет хорошую защиту от физических атак, но слабо противостоит магии и сам с трудом ей пользуется. Увеличение физических способностей сильнее, чем ослабление магических.'

    INCOMING_MAGIC_DAMAGE_MODIFIER =   [1.025, 1.050, 1.075, 1.100, 1.125]
    INCOMING_PHYSIC_DAMAGE_MODIFIER =  [0.950, 0.900, 0.850, 0.800, 0.750]

    OUTCOMING_MAGIC_DAMAGE_MODIFIER =  [0.975, 0.950, 0.925, 0.900, 0.875]
    OUTCOMING_PHYSIC_DAMAGE_MODIFIER = [1.050, 1.100, 1.150, 1.200, 1.250]


class GARGOYLE(AbilityModifiersBase):

    TYPE = relations.ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.PASSIVE

    NAME = 'Горгулья'
    normalized_name = NAME
    DESCRIPTION = 'Подобно горгулье, обладатель этой способности имеет увеличенную защиту от всех типов атак.'

    INCOMING_MAGIC_DAMAGE_MODIFIER =  [0.975, 0.950, 0.925, 0.900, 0.875]
    INCOMING_PHYSIC_DAMAGE_MODIFIER = [0.975, 0.950, 0.925, 0.900, 0.875]


class KILLER(AbilityModifiersBase):

    TYPE = relations.ABILITY_TYPE.BATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.PASSIVE

    NAME = 'Убийца'
    normalized_name = NAME
    DESCRIPTION = 'Ориентируясь на короткий бой, убийца совершенствует свои атакующие способности в ущерб защитным.'

    OUTCOMING_MAGIC_DAMAGE_MODIFIER =  [1.050, 1.100, 1.150, 1.200, 1.260]
    OUTCOMING_PHYSIC_DAMAGE_MODIFIER = [1.050, 1.100, 1.150, 1.200, 1.260]

    INCOMING_MAGIC_DAMAGE_MODIFIER =   [1.025, 1.050, 1.075, 1.100, 1.115]
    INCOMING_PHYSIC_DAMAGE_MODIFIER =  [1.025, 1.050, 1.075, 1.100, 1.115]


ABILITIES = dict( (ability.get_id(), ability)
                  for ability in globals().values()
                  if isinstance(ability, type) and issubclass(ability, AbilityModifiersBase) and ability != AbilityModifiersBase)
