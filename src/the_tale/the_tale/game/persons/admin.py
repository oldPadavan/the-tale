
import smart_imports

smart_imports.all()


class PersonAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'place', 'type', 'name', 'politic_power', 'created_at')

    list_filter = ('gender', 'race', 'type', 'place')

    def politic_power(self, obj):
        return logic.load_person(person_model=obj).politic_power

    def name(self, obj):
        return logic.load_person(person_model=obj).name


class SocialConnectionAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'connection', 'person_1', 'person_2', 'created_at')
    list_filter = ('connection',)


django_admin.site.register(models.Person, PersonAdmin)
django_admin.site.register(models.SocialConnection, SocialConnectionAdmin)
