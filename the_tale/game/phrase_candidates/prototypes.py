# coding: utf-8

from the_tale.common.utils.prototypes import BasePrototype

from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.phrase_candidates import models
from the_tale.game.phrase_candidates import relations


class PhraseCandidatePrototype(BasePrototype):
    _model_class = models.PhraseCandidate
    _readonly = ('id', 'created_at', 'author_id')
    _bidirectional = ('state', 'text', 'moderator_id', 'type', 'type_name', 'subtype', 'subtype_name')
    _get_by = ('id', 'account_id')

    @property
    def author(self):
        if not hasattr(self, '_author'):
            self._author = AccountPrototype.get_by_id(self.author_id)
        return self._author


    @classmethod
    def create(cls, type_, type_name, subtype, subtype_name, author, text):
        model = cls._db_create(type=type_,
                               type_name=type_name,
                                        subtype=subtype,
                                        subtype_name=subtype_name,
                                        author=author._model,
                                        state=relations.PHRASE_CANDIDATE_STATE.IN_QUEUE,
                                        text=text)

        return cls(model)
