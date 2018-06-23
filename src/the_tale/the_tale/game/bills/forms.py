
import smart_imports

smart_imports.all()


class BaseUserForm(dext_forms.Form):
    caption = dext_fields.CharField(label='Название записи',
                               max_length=models.Bill.CAPTION_MAX_LENGTH,
                               min_length=models.Bill.CAPTION_MIN_LENGTH)

    chronicle_on_accepted = dext_fields.TextField(label='Текст летописи при принятии (от {} до {} символов)'.format(conf.bills_settings.CHRONICLE_MIN_LENGTH,
                                                                                                               conf.bills_settings.CHRONICLE_MAX_LENGTH),
                                             widget=django_forms.Textarea(attrs={'rows': 6}),
                                             min_length=conf.bills_settings.CHRONICLE_MIN_LENGTH,
                                             max_length=conf.bills_settings.CHRONICLE_MAX_LENGTH)

    depends_on = dext_fields.ChoiceField(label='Зависит от', required=False)

    def __init__(self, *args, **kwargs):
        original_bill_id = kwargs.pop('original_bill_id', None)

        super().__init__(*args, **kwargs)

        voting_bills = models.Bill.objects.filter(state=relations.BILL_STATE.VOTING)
        self.fields['depends_on'].choices = [(None, ' — ')] + [(bill.id, bill.caption)
                                                               for bill in voting_bills
                                                               if bill.id != original_bill_id]

    def clean_depends_on(self):
        data = self.cleaned_data.get('depends_on')

        if data == 'None':
            return None

        return data


class ModeratorFormMixin(dext_forms.Form):
    approved = dext_fields.BooleanField(label='Одобрено', required=False)
