

import smart_imports

smart_imports.all()


class UseCardTask(game_postponed_tasks.ComplexChangeTask):
    TYPE = 'use-card'

    def construct_processor(self):
        return cards.CARD(self.processor_id).effect
