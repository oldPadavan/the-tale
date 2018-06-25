
import smart_imports

smart_imports.all()


ABILITIES_CHOICES = sorted([(key, ability.NAME) for key, ability in heroes_habilities.ABILITIES.items()], key=lambda x: x[1])


BASE_INDEX_FILTERS = [utils_list_filter.reset_element(),
                      utils_list_filter.choice_element('тип:', attribute='type', choices=[(None, 'все')] + sorted(list(beings_relations.TYPE.select('value', 'text')), key=lambda x: x[1])),
                      utils_list_filter.choice_element('архетип:', attribute='archetype', choices=[(None, 'все')] + sorted(list(game_relations.ARCHETYPE.select('value', 'text')), key=lambda x: x[1])),
                      utils_list_filter.choice_element('территория:', attribute='terrain', choices=[(None, 'все')] + sorted(list(map_relations.TERRAIN.select('value', 'text')), key=lambda x: x[1])),
                      utils_list_filter.choice_element('способность:', attribute='ability', choices=[(None, 'все')] + ABILITIES_CHOICES),
                      utils_list_filter.choice_element('сортировка:',
                                                 attribute='order_by',
                                                 choices=relations.INDEX_ORDER_TYPE.select('value', 'text'),
                                                 default_value=relations.INDEX_ORDER_TYPE.BY_NAME.value) ]

MODERATOR_INDEX_FILTERS = BASE_INDEX_FILTERS + [utils_list_filter.choice_element('состояние:',
                                                                           attribute='state',
                                                                           default_value=relations.MOB_RECORD_STATE.ENABLED.value,
                                                                           choices=relations.MOB_RECORD_STATE.select('value', 'text'))]


class UnloginedIndexFilter(utils_list_filter.ListFilter):
    ELEMENTS = BASE_INDEX_FILTERS


class ModeratorIndexFilter(utils_list_filter.ListFilter):
    ELEMENTS = MODERATOR_INDEX_FILTERS


def argument_to_mob(value): return storage.mobs.get(int(value), None)


class MobResourceBase(utils_resources.Resource):

    @dext_old_views.validate_argument('mob', argument_to_mob, 'mobs', 'Запись о монстре не найдена')
    def initialize(self, mob=None, *args, **kwargs):
        super(MobResourceBase, self).initialize(*args, **kwargs)
        self.mob = mob

        self.can_create_mob = self.account.has_perm('mobs.create_mobrecord')
        self.can_moderate_mob = self.account.has_perm('mobs.moderate_mobrecord')


def argument_to_mob_state(value):
    return relations.MOB_RECORD_STATE(int(value))


def argument_to_mob_type(value):
    return beings_relations.TYPE(int(value))


def argument_to_archetype(value):
    return game_relations.ARCHETYPE(int(value))


def argument_to_ability(value):
    return value


@dext_old_views.validator(code='mobs.mob_disabled', message='монстр находится вне игры', status_code=404)
def validate_mob_disabled(resource, *args, **kwargs):
    return not resource.mob.state.is_DISABLED or resource.can_create_mob or resource.can_moderate_mob


class GuideMobResource(MobResourceBase):

    @dext_old_views.validate_argument('state', argument_to_mob_state, 'mobs', 'неверное состояние записи о монстре')
    @dext_old_views.validate_argument('terrain', lambda value: map_relations.TERRAIN(int(value)), 'mobs', 'неверный тип территории')
    @dext_old_views.validate_argument('order_by', relations.INDEX_ORDER_TYPE, 'mobs', 'неверный тип сортировки')
    @dext_old_views.validate_argument('archetype', argument_to_archetype, 'mobs', 'неверный архетип монстра')
    @dext_old_views.validate_argument('ability', argument_to_ability, 'mobs', 'неверная способность монстра')
    @dext_old_views.validate_argument('type', argument_to_mob_type, 'mobs', 'неверный тип монстра')
    @dext_old_views.handler('', method='get')
    def index(self,
              state=relations.MOB_RECORD_STATE.ENABLED,
              terrain=None,
              order_by=relations.INDEX_ORDER_TYPE.BY_NAME,
              type=None,
              archetype=None,
              ability=None):

        mobs = storage.mobs.all()

        if not self.can_create_mob and not self.can_moderate_mob:
            mobs = [mob for mob in mobs if mob.state.is_ENABLED] # pylint: disable=W0110

        is_filtering = False

        if not state.is_ENABLED: # if not default
            is_filtering = True
        mobs = [mob for mob in mobs if mob.state == state] # pylint: disable=W0110

        if terrain is not None:
            is_filtering = True
            mobs = [mob for mob in mobs if terrain in mob.terrains] # pylint: disable=W0110

        if order_by.is_BY_NAME:
            mobs = sorted(mobs, key=lambda mob: mob.name)
        elif order_by.is_BY_LEVEL:
            mobs = sorted(mobs, key=lambda mob: mob.level)

        if type is not None:
            mobs = [mob for mob in mobs if mob.type == type] # pylint: disable=W0110

        if archetype is not None:
            mobs = [mob for mob in mobs if mob.archetype == archetype] # pylint: disable=W0110

        if ability is not None:
            mobs = [mob for mob in mobs if ability in mob.abilities]

        url_builder = dext_urls.UrlBuilder(django_reverse('guide:mobs:'), arguments={ 'state': state.value if state is not None else None,
                                                                     'terrain': terrain.value if terrain is not None else None,
                                                                     'type': type.value if type is not None else None,
                                                                     'archetype': archetype.value if archetype is not None else None,
                                                                     'ability': ability if ability is not None else None,
                                                                     'order_by': order_by.value})

        IndexFilter = ModeratorIndexFilter if self.can_create_mob or self.can_moderate_mob else UnloginedIndexFilter #pylint: disable=C0103

        index_filter = IndexFilter(url_builder=url_builder, values={'state': state.value if state is not None else None,
                                                                    'terrain': terrain.value if terrain is not None else None,
                                                                    'type': type.value if type is not None else None,
                                                                    'archetype': archetype.value if archetype is not None else None,
                                                                    'ability': ability if ability is not None else None,
                                                                    'order_by': order_by.value})

        return self.template('mobs/index.html',
                             {'mobs': mobs,
                              'is_filtering': is_filtering,
                              'relations.MOB_RECORD_STATE': relations.MOB_RECORD_STATE,
                              'TERRAIN': map_relations.TERRAIN,
                              'state': state,
                              'terrain': terrain,
                              'ability': ability,
                              'order_by': order_by,
                              'relations.INDEX_ORDER_TYPE': relations.INDEX_ORDER_TYPE,
                              'url_builder': url_builder,
                              'index_filter': index_filter,
                              'section': 'mobs'})

    @validate_mob_disabled()
    @dext_old_views.handler('#mob', name='show', method='get')
    def show(self):
        return self.template('mobs/show.html', {'mob': self.mob,
                                                'mob_meta_object': meta_relations.Mob.create_from_object(self.mob),
                                                'section': 'mobs'})

    @validate_mob_disabled()
    @dext_old_views.handler('#mob', 'info', method='get')
    def show_dialog(self):
        return self.template('mobs/info.html', {'mob': self.mob,
                                                'mob_meta_object': meta_relations.Mob.create_from_object(self.mob),})


@dext_old_views.validator(code='mobs.create_mob_rights_required', message='Вы не можете создавать мобов')
def validate_create_rights(resource, *args, **kwargs): return resource.can_create_mob

@dext_old_views.validator(code='mobs.moderate_mob_rights_required', message='Вы не можете принимать мобов в игру')
def validate_moderate_rights(resource, *args, **kwargs): return resource.can_moderate_mob

@dext_old_views.validator(code='mobs.disabled_state_required', message='Для проведения этой операции монстр должен быть убран из игры')
def validate_disabled_state(resource, *args, **kwargs): return resource.mob.state.is_DISABLED


class GameMobResource(MobResourceBase):

    @utils_decorators.login_required
    @validate_create_rights()
    @dext_old_views.handler('new', method='get')
    def new(self):
        form = forms.MobRecordForm()
        return self.template('mobs/new.html', {'form': form})

    @utils_decorators.login_required
    @validate_create_rights()
    @dext_old_views.handler('create', method='post')
    def create(self):

        form = forms.MobRecordForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('mobs.create.form_errors', form.errors)

        if [mob for mob in storage.mobs.all() if mob.name == form.c.name.normal_form()]:
            return self.json_error('mobs.create.duplicate_name', 'Монстр с таким названием уже создан')

        mob = logic.create_mob_record(uuid=uuid.uuid4().hex,
                                      level=form.c.level,
                                      utg_name=form.c.name,
                                      type=form.c.type,
                                      archetype=form.c.archetype,
                                      description=form.c.description,
                                      abilities=form.c.abilities,
                                      terrains=form.c.terrains,
                                      editor=self.account,
                                      state=relations.MOB_RECORD_STATE.DISABLED,
                                      communication_verbal=form.c.communication_verbal,
                                      communication_gestures=form.c.communication_gestures,
                                      communication_telepathic=form.c.communication_telepathic,
                                      intellect_level=form.c.intellect_level,
                                      is_mercenary=form.c.is_mercenary,

                                      structure=form.c.structure,
                                      features=form.c.features,
                                      movement=form.c.movement,
                                      body=form.c.body,
                                      size=form.c.size,
                                      orientation=form.c.orientation,
                                      weapons=form.get_weapons(),

                                      is_eatable=form.c.is_eatable)
        return self.json_ok(data={'next_url': django_reverse('guide:mobs:show', args=[mob.id])})

    @utils_decorators.login_required
    @validate_disabled_state()
    @validate_create_rights()
    @dext_old_views.handler('#mob', 'edit', name='edit', method='get')
    def edit(self):
        form = forms.MobRecordForm(initial=forms.MobRecordForm.get_initials(self.mob))

        return self.template('mobs/edit.html', {'mob': self.mob,
                                                'form': form})

    @utils_decorators.login_required
    @validate_disabled_state()
    @validate_create_rights()
    @dext_old_views.handler('#mob', 'update', name='update', method='post')
    def update(self):

        form = forms.MobRecordForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('mobs.update.form_errors', form.errors)

        if [mob for mob in storage.mobs.all() if mob.name == form.c.name.normal_form() and mob.id != self.mob.id]:
            return self.json_error('mobs.update.duplicate_name', 'Монстр с таким названием уже создан')

        logic.update_by_creator(self.mob, form, editor=self.account)

        return self.json_ok(data={'next_url': django_reverse('guide:mobs:show', args=[self.mob.id])})

    @utils_decorators.login_required
    @validate_moderate_rights()
    @dext_old_views.handler('#mob', 'moderate', name='moderate', method='get')
    def moderation_page(self):
        form = forms.ModerateMobRecordForm(initial=forms.ModerateMobRecordForm.get_initials(self.mob))

        return self.template('mobs/moderate.html', {'mob': self.mob,
                                                    'form': form} )

    @utils_decorators.login_required
    @validate_moderate_rights()
    @dext_old_views.handler('#mob', 'moderate', name='moderate', method='post')
    def moderate(self):
        form = forms.ModerateMobRecordForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('mobs.moderate.form_errors', form.errors)

        logic.update_by_moderator(self.mob, form, editor=self.account)

        return self.json_ok(data={'next_url': django_reverse('guide:mobs:show', args=[self.mob.id])})
