
import smart_imports

smart_imports.all()


def can_be_choosen(place, modifier):
    if modifier.is_NONE:
        return True

    if getattr(place.attrs, 'MODIFIER_{}'.format(modifier.name).lower(), c.PLACE_TYPE_NECESSARY_BORDER) < c.PLACE_TYPE_NECESSARY_BORDER:
        return False

    return True


class BaseForm(forms.BaseUserForm):
    place = dext_fields.ChoiceField(label='Город')
    new_modifier = dext_fields.TypedChoiceField(label='Новая специализация', choices=sorted(places_modifiers.CITY_MODIFIERS.choices(), key=lambda g: g[1]), coerce=places_modifiers.CITY_MODIFIERS.get_from_name)

    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        self.fields['place'].choices = places_storage.places.get_choices()



class UserForm(BaseForm):

    def clean(self):
        cleaned_data = super(UserForm, self).clean()

        place = places_storage.places.get(int(cleaned_data['place']))
        modifier = cleaned_data.get('new_modifier')

        if modifier:
            if not can_be_choosen(place, modifier):
                raise django_forms.ValidationError('В данный момент город «%s» нельзя преобразовать в «%s».' % (place.name, modifier.text))

        return cleaned_data


class ModeratorForm(BaseForm, forms.ModeratorFormMixin):
    pass


class PlaceModifier(base_place_bill.BasePlaceBill):
    type = relations.BILL_TYPE.PLACE_CHANGE_MODIFIER

    UserForm = UserForm
    ModeratorForm = ModeratorForm

    CAPTION = 'Изменение специализации города'
    DESCRIPTION = 'Изменяет специализацию города. Изменить специализацию можно только на одну из доступных для этого города. Посмотреть доступные варианты можно в диалоге информации о городе на странице игры.'

    def __init__(self, modifier_id=None, modifier_name=None, old_modifier_name=None, **kwargs):
        super(PlaceModifier, self).__init__(**kwargs)
        self.modifier_id = modifier_id
        self.modifier_name = modifier_name
        self.old_modifier_name = old_modifier_name

    def user_form_initials(self):
        data = super(PlaceModifier, self).user_form_initials()
        data['new_modifier'] = self.modifier_id
        return data

    def initialize_with_form(self, user_form):
        super(PlaceModifier, self).initialize_with_form(user_form)
        self.modifier_id = user_form.c.new_modifier
        self.modifier_name = self.modifier_id.text
        self.old_modifier_name = self.place._modifier.text if not self.place._modifier.is_NONE else None

    def has_meaning(self):
        return self.place._modifier.is_NONE is None or (self.place._modifier != self.modifier_id)

    def apply(self, bill=None):
        if self.has_meaning():
            self.place.set_modifier(self.modifier_id)
            places_logic.save_place(self.place)

    def serialize(self):
        data = super(PlaceModifier, self).serialize()
        data['modifier_id'] = self.modifier_id.value
        data['modifier_name'] = self.modifier_name
        data['old_modifier_name'] = self.old_modifier_name if self.old_modifier_name else None
        return data

    @classmethod
    def deserialize(cls, data):
        obj = super(PlaceModifier, cls).deserialize(data)
        obj.modifier_id = places_modifiers.CITY_MODIFIERS(data['modifier_id'])
        obj.modifier_name = data['modifier_name']
        obj.old_modifier_name = data.get('old_modifier_name')
        return obj
