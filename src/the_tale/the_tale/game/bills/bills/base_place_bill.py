
import smart_imports

smart_imports.all()


class BasePlaceBill(base_bill.BaseBill):
    type = None
    UserForm = None
    CAPTION = None
    DESCRIPTION = None

    def __init__(self, place_id=None, old_name_forms=None):
        super(BasePlaceBill, self).__init__()
        self.place_id = place_id
        self.old_name_forms = old_name_forms

        if self.old_name_forms is None and self.place_id is not None:
            self.old_name_forms = self.place.utg_name

    @property
    def old_name(self): return self.old_name_forms.normal_form()

    @property
    def place(self): return places_storage.places[self.place_id]

    @property
    def actors(self): return [self.place]

    def user_form_initials(self):
        return {'place': self.place_id}

    @property
    def place_name_changed(self):
        return self.old_name != self.place.name

    def initialize_with_form(self, user_form):
        self.place_id = int(user_form.c.place)
        self.old_name_forms = self.place.utg_name

    def serialize(self):
        return {'type': self.type.name.lower(),
                'place_id': self.place_id,
                'old_name_forms': self.old_name_forms.serialize()}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.place_id = data['place_id']

        if 'old_name_forms' in data:
            obj.old_name_forms = utg_words.Word.deserialize(data['old_name_forms'])
        elif 'old_place_name_forms' in data:
            obj.old_name_forms = utg_words.Word.deserialize(data['old_place_name_forms'])
        else:
            obj.old_name_forms = names.generator().get_fast_name('название утрачено')

        return obj
