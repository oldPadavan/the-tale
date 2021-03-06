
from django.db import models, IntegrityError, transaction

from dext.common.utils.urls import full_url

from the_tale.common.utils.prototypes import BasePrototype
from the_tale.common.utils import bbcode
from the_tale.common.utils.decorators import lazy_property

from the_tale.accounts.personal_messages import tt_api as pm_tt_api
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.accounts.clans.models import Clan, Membership, MembershipRequest
from the_tale.accounts.clans.relations import MEMBER_ROLE, MEMBERSHIP_REQUEST_TYPE
from the_tale.accounts.clans import exceptions
from the_tale.accounts.clans.conf import clans_settings

from the_tale.forum.prototypes import CategoryPrototype
from the_tale.forum.prototypes import SubCategoryPrototype
from the_tale.forum.prototypes import PermissionPrototype as ForumPermissionPrototype
from the_tale.forum.prototypes import ThreadPrototype


class ClanPrototype(BasePrototype):
    _model_class = Clan
    _readonly = ('id',
                 'created_at',
                 'updated_at',
                 'members_number',
                 'forum_subcategory_id')
    _bidirectional = ('name', 'abbr', 'motto', 'description')
    _get_by = ('id',)

    @property
    def description_html(self):
        return bbcode.render(self.description)

    @classmethod
    def get_forum_subcategory_caption(cls, clan_name):
        return 'Раздел гильдии «%s»' % clan_name

    @classmethod
    @transaction.atomic
    def create(cls, owner, abbr, name, motto, description):

        forum_category = CategoryPrototype.get_by_slug(clans_settings.FORUM_CATEGORY_SLUG)

        subcategory_order = SubCategoryPrototype._db_filter(category=forum_category.id).aggregate(models.Max('order'))['order__max']
        if subcategory_order is None:
            subcategory_order = 0
        else:
            subcategory_order += 1

        forum_subcategory = SubCategoryPrototype.create(category=forum_category,
                                                        caption=cls.get_forum_subcategory_caption(name),
                                                        order=subcategory_order,
                                                        restricted=True)

        clan_model = cls._model_class.objects.create(name=name,
                                                     abbr=abbr,
                                                     motto=motto,
                                                     description=description,
                                                     members_number=1,
                                                     forum_subcategory=forum_subcategory._model)

        clan = cls(clan_model)

        MembershipPrototype.create(owner, clan, role=MEMBER_ROLE.LEADER)

        owner.set_clan_id(clan.id)

        return clan

    @transaction.atomic
    def update(self, abbr, name, motto, description):
        self.abbr = abbr
        self.name = name
        self.motto = motto
        self.description = description

        forum_subcateogry = SubCategoryPrototype.get_by_id(self.forum_subcategory_id)
        forum_subcateogry.caption = self.get_forum_subcategory_caption(name)
        forum_subcateogry.save()

        self.save()

    @transaction.atomic
    def add_member(self, account):
        try:
            MembershipPrototype.create(account, self, role=MEMBER_ROLE.MEMBER)
        except IntegrityError:
            raise exceptions.AddMemberFromClanError(member_id=account.id, clan_id=self.id)

        MembershipRequestPrototype._db_filter(account_id=account.id).delete()

        account.set_clan_id(self.id)

        self._model.members_number = MembershipPrototype._db_filter(clan_id=self.id).count()
        self.save()

    @transaction.atomic
    def remove_member(self, account):
        membership = MembershipPrototype.get_by_account_id(account.id)
        if membership is None:
            raise exceptions.RemoveNotMemberFromClanError(member_id=account.id, clan_id=self.id)
        if membership.clan_id != self.id:
            raise exceptions.RemoveMemberFromWrongClanError(member_id=account.id, clan_id=self.id)
        if membership.role.is_LEADER:
            raise exceptions.RemoveLeaderFromClanError(member_id=account.id, clan_id=self.id)

        account.set_clan_id(None)

        membership.remove()

        self._model.members_number = MembershipPrototype._db_filter(clan_id=self.id).count()
        self.save()

    def create_remove_member_message(self, initiator, removed_account):
        message = '''
Игрок %(clan_leader_link)s исключил вас из гильдии %(clan_link)s.
''' % {'clan_leader_link': '[url="%s"]%s[/url]' % (full_url('https', 'accounts:show', initiator.id), initiator.nick_verbose),
       'clan_link': '[url="%s"]%s[/url]' % (full_url('https', 'accounts:clans:show', self.id), self.name)}

        pm_tt_api.send_message(sender_id=initiator.id,
                              recipients_ids=[removed_account.id],
                              body=message)

    def save(self):
        self._model.save()

    @transaction.atomic
    def remove(self):
        for membership_model in MembershipPrototype._db_filter(clan_id=self.id):
            membership = MembershipPrototype(model=membership_model)
            membership.remove()

        SubCategoryPrototype.get_by_id(self.forum_subcategory_id).delete()

        self._model.delete()

    def get_leader(self):
        return AccountPrototype.get_by_id(MembershipPrototype._model_class.objects.get(clan_id=self.id, role=MEMBER_ROLE.LEADER).account_id)


class MembershipPrototype(BasePrototype):
    _model_class = Membership
    _readonly = ('id',
                 'created_at',
                 'updated_at',
                 'clan_id',
                 'account_id',
                 'role')
    _bidirectional = ()
    _get_by = ('clan_id', 'account_id')

    @classmethod
    @transaction.atomic
    def create(cls, account, clan, role):
        model = cls._model_class.objects.create(clan=clan._model,
                                                account=account._model,
                                                role=role)
        ForumPermissionPrototype.create(account, SubCategoryPrototype.get_by_id(clan.forum_subcategory_id))
        return cls(model)

    def remove(self):
        ForumPermissionPrototype.get_for(account_id=self.account_id, subcategory_id=ClanPrototype.get_by_id(self.clan_id).forum_subcategory_id).remove()
        self._model.delete()


class MembershipRequestPrototype(BasePrototype): #pylint: disable=R0904
    _model_class = MembershipRequest
    _readonly = ('id',
                 'created_at',
                 'updated_at',
                 'clan_id',
                 'account_id',
                 'initiator_id',
                 'text')
    _bidirectional = ('type',)
    _get_by = ('id', 'clan_id', 'account_id')

    @classmethod
    def get_for(cls, clan_id, account_id):
        try:
            return cls(model=cls._model_class.objects.get(clan_id=clan_id, account_id=account_id))
        except cls._model_class.DoesNotExist:
            return None

    @lazy_property
    def account(self): return AccountPrototype.get_by_id(self.account_id)

    @lazy_property
    def clan(self): return ClanPrototype.get_by_id(self.clan_id)

    def create_invite_message(self, initiator):
        message = '''
Игрок %(clan_leader_link)s предлагает вам вступить в гильдию %(clan_link)s:

%(text)s

----------
принять или отклонить предложение вы можете на этой странице: %(invites_link)s
''' % {'clan_leader_link': '[url="%s"]%s[/url]' % (full_url('https', 'accounts:show', initiator.id), initiator.nick_verbose),
       'text': self.text,
       'clan_link': '[url="%s"]%s[/url]' % (full_url('https', 'accounts:clans:show', self.clan.id), self.clan.name),
       'invites_link': '[url="%s"]Приглашения в гильдию [/url]' % full_url('https', 'accounts:clans:membership:for-account')}

        pm_tt_api.send_message(sender_id=initiator.id,
                              recipients_ids=[self.account.id],
                              body=message)


    def create_request_message(self, initiator):
        message = '''
Игрок %(account)s просит принять его в вашу гильдию:

%(text)s

----------
принять или отклонить предложение вы можете на этой странице: %(invites_link)s
''' % {'account': '[url="%s"]%s[/url]' % (full_url('https', 'accounts:show', self.account.id), self.account.nick_verbose),
       'text': self.text,
       'invites_link': '[url="%s"]Заявки в гильдию[/url]' % full_url('https', 'accounts:clans:membership:for-clan')}

        pm_tt_api.send_message(sender_id=initiator.id,
                              recipients_ids=[self.clan.get_leader().id],
                              body=message)


    def create_accept_request_message(self, initiator):
        message = '''
Игрок %(clan_leader_link)s принял вас в гильдию %(clan_link)s.
''' % {'clan_leader_link': '[url="%s"]%s[/url]' % (full_url('https', 'accounts:show', initiator.id), initiator.nick_verbose),
       'clan_link': '[url="%s"]%s[/url]' % (full_url('https', 'accounts:clans:show', self.clan.id), self.clan.name)}

        pm_tt_api.send_message(sender_id=initiator.id,
                              recipients_ids=[self.account.id],
                              body=message)


    def create_reject_request_message(self, initiator):
        message = '''
Игрок %(clan_leader_link)s отказал вам в принятии в гильдию %(clan_link)s.
''' % {'clan_leader_link': '[url="%s"]%s[/url]' % (full_url('https', 'accounts:show', initiator.id), initiator.nick_verbose),
       'clan_link': '[url="%s"]%s[/url]' % (full_url('https', 'accounts:clans:show', self.clan.id), self.clan.name)}

        pm_tt_api.send_message(sender_id=initiator.id,
                              recipients_ids=[self.account.id],
                              body=message)

    @classmethod
    @transaction.atomic
    def create(cls, initiator, account, clan, text, type):

        model = cls._model_class.objects.create(clan=clan._model,
                                                account=account._model,
                                                initiator=initiator._model,
                                                type=type,
                                                text=text)
        return cls(model)

    @classmethod
    def get_for_clan(cls, clan_id):
        models = cls._db_filter(clan_id=clan_id, type=MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT).order_by('created_at')
        return [cls(model=model) for model in models]

    @classmethod
    def get_for_account(cls, account_id):
        models = cls._db_filter(account_id=account_id, type=MEMBERSHIP_REQUEST_TYPE.FROM_CLAN).order_by('created_at')
        return [cls(model=model) for model in models]

    @property
    def text_html(self):
         return bbcode.render(self.text)

    def remove(self):
        self._model.delete()
