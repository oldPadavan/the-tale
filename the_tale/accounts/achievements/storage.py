# coding: utf-8
import contextlib

from the_tale.common.utils.storage import create_storage_class

from the_tale.accounts.achievements.prototypes import AchievementPrototype, AccountAchievementsPrototype
from the_tale.accounts.achievements.exceptions import AchievementsError


class AchievementsStorage(create_storage_class('achievements change time', AchievementPrototype, AchievementsError)):

    def by_group(self, group, only_approved):
        by_group =  (achievement for achievement in self.all() if achievement.group == group)

        if only_approved:
            by_group = (achievement for achievement in by_group if  achievement.approved)

        return by_group

    def by_type(self, type, only_approved):
        by_type =  (achievement for achievement in self.all() if achievement.type == type)

        if only_approved:
            by_type = (achievement for achievement in by_type if  achievement.approved)

        return by_type


    def verify_achievements(self, account_id, type, object, old_value, new_value):
        if old_value == new_value:
            return

        for achievement in self.by_type(type, only_approved=True):
            if achievement.check(object, old_value, new_value):
                AccountAchievementsPrototype.give_achievement(account_id=account_id, achievement=achievement)

    @contextlib.contextmanager
    def verify(self, account_id, type, object, value_callback):
        old_value = value_callback()
        yield
        self.verify_achievements(account_id,
                                 type=type,
                                 object=object,
                                 old_value=old_value,
                                 new_value=value_callback())



achievements_storage = AchievementsStorage()
