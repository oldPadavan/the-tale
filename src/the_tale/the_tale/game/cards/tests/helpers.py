
import smart_imports

smart_imports.all()


class CardsTestMixin(game_tests_helpers.ComplexChangeTaskMixin):
    LOGIC = postponed_tasks.UseCardTask
