
import smart_imports

smart_imports.all()


class BaseForm(forms.BaseUserForm):
    new_place = dext_fields.ChoiceField(label='Новый город')
    person = dext_fields.ChoiceField(label='Мастер')

    def __init__(self, choosen_person_id, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        self.fields['new_place'].choices = places_storage.places.get_choices()
        self.fields['person'].choices = persons_objects.Person.form_choices(choosen_person=persons_storage.persons.get(choosen_person_id))

    def clean_new_place(self):
        place_id = int(self.cleaned_data['new_place'])

        if len(places_storage.places[place_id].persons) >= c.PLACE_MAX_PERSONS:
            raise django_forms.ValidationError('В городе достигнут максимум Мастеров. Чтобы переселить Мастера, необходимо кого-нибудь выселить.')

        return place_id

    def clean_person(self):
        person_id = int(self.cleaned_data['person'])

        person = persons_storage.persons[person_id]

        if person.has_building:
            raise django_forms.ValidationError('У Мастера в собственности есть постройка. Прежде чем переехать он должен от неё избавиться.')

        if person.on_move_timeout:
            raise django_forms.ValidationError('Мастер недавно переезжал. Должно пройти время, прежде чем он снова сможет переехать.')

        if len(person.place.persons) <= c.PLACE_MIN_PERSONS:
            raise django_forms.ValidationError('В текущем городе Мастера слишком мало мастеров. Чтобы переселить Мастера, необходимо кого-нибудь вселить вместо него.')

        return person_id


class UserForm(BaseForm):

    def __init__(self, choosen_person_id, owner_id, *args, **kwargs):
        super(UserForm, self).__init__(choosen_person_id, *args, **kwargs)
        self.owner_id = owner_id

    def clean_person(self):
        person_id = super().clean_person()

        if not politic_power_logic.get_inner_circle(person_id=person_id).in_circle(self.owner_id):
            raise django_forms.ValidationError('Ваш герой должен быть в ближнем круге Мастера')

        return person_id


class ModeratorForm(BaseForm, forms.ModeratorFormMixin):
    pass


class PersonMove(base_person_bill.BasePersonBill):
    type = relations.BILL_TYPE.PERSON_MOVE

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    CAPTION = 'Переезд Мастера'
    DESCRIPTION = 'Мастера можно сподвигнуть на переезд в другой город. Но сделать это может только Хранитель героя из ближнего круга Мастера. Герой должен быть в ближнем круге на момент создания записи и/или её редактирования.'

    def __init__(self, new_place_id=None, new_place_name_forms=None, **kwargs):
        super(PersonMove, self).__init__(**kwargs)
        self.new_place_id = new_place_id
        self.new_place_name_forms = new_place_name_forms

        if self.new_place_name_forms is None and self.new_place_id is not None:
            self.new_place_name_forms = self.new_place.utg_name

    @property
    def new_place(self): return places_storage.places[self.new_place_id]

    @property
    def new_place_name(self):
        return self.new_place_name_forms.normal_form()

    @property
    def new_place_name_changed(self):
        return self.new_place_name != self.new_place.name

    @property
    def actors(self): return [self.place, self.new_place, self.person]

    def has_meaning(self):
        return (self.person.place.id != self.new_place_id and
                not self.person.on_move_timeout and
                not self.person.has_building and
                len(self.person.place.persons) > c.PLACE_MIN_PERSONS and
                len(self.new_place.persons) < c.PLACE_MAX_PERSONS)

    def apply(self, bill=None):
        if not self.has_meaning():
            return

        persons_logic.move_person_to_place(self.person, self.new_place)

    @classmethod
    def get_user_form_create(cls, post=None, owner_id=None):
        return cls.UserForm(None, owner_id, post) #pylint: disable=E1102

    def get_user_form_update(self, post=None, initial=None, owner_id=None, original_bill_id=None):
        if initial:
            return self.UserForm(self.person_id, owner_id, initial=initial, original_bill_id=original_bill_id) #pylint: disable=E1102
        return self.UserForm(self.person_id, owner_id, post, original_bill_id=original_bill_id) #pylint: disable=E1102

    def get_moderator_form_update(self, post=None, initial=None, original_bill_id=None):
        if initial:
            return self.ModeratorForm(self.person_id, initial=initial, original_bill_id=original_bill_id) #pylint: disable=E1102
        return self.ModeratorForm(self.person_id, post, original_bill_id=original_bill_id) #pylint: disable=E1102

    def user_form_initials(self):
        initials = super(PersonMove, self).user_form_initials()
        initials['new_place'] = self.new_place_id
        return initials

    def initialize_with_form(self, user_form):
        super(PersonMove, self).initialize_with_form(user_form)
        self.new_place_id = int(user_form.c.new_place)
        self.new_place_name_forms = self.new_place.utg_name

    def serialize(self):
        data = super(PersonMove, self).serialize()
        data['new_place_id'] = self.new_place_id
        data['new_place_name_forms'] = self.new_place_name_forms.serialize()
        return data

    @classmethod
    def deserialize(cls, data):
        obj = super(PersonMove, cls).deserialize(data)
        obj.new_place_id = data['new_place_id']
        obj.new_place_name_forms = utg_words.Word.deserialize(data['new_place_name_forms'])
        return obj
