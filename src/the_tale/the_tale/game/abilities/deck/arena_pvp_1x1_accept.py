
import smart_imports

smart_imports.all()


class ACCEPT_BATTLE_RESULT(rels_django.DjangoEnum):
    records = (('BATTLE_NOT_FOUND', 1, 'битва не найдена'),
               ('WRONG_ACCEPTED_BATTLE_STATE', 2, 'герой не успел принять вызов'),
               ('WRONG_INITIATOR_BATTLE_STATE', 3, 'герой уже находится в сражении'),
               ('NOT_IN_QUEUE', 4, 'битва не находится в очереди балансировщика'),
               ('PROCESSED', 5, 'обработана'))


class ArenaPvP1x1Accept(prototypes.AbilityPrototype):
    TYPE = relations.ABILITY_TYPE.ARENA_PVP_1x1_ACCEPT

    @classmethod
    def accept_battle(cls, pvp_balancer, battle_id, hero_id):

        accepted_battle = pvp_prototypes.Battle1x1Prototype.get_by_id(battle_id)

        if accepted_battle is None:
            return ACCEPT_BATTLE_RESULT.BATTLE_NOT_FOUND

        if not accepted_battle.state.is_WAITING:
            return ACCEPT_BATTLE_RESULT.WRONG_ACCEPTED_BATTLE_STATE

        if not accepted_battle.account_id in pvp_balancer.arena_queue:
            return ACCEPT_BATTLE_RESULT.NOT_IN_QUEUE

        initiator_id = heroes_logic.load_hero(hero_id=hero_id).account_id

        initiator_battle = pvp_prototypes.Battle1x1Prototype.get_by_account_id(initiator_id)

        if initiator_battle is not None and not initiator_battle.state.is_WAITING:
            return ACCEPT_BATTLE_RESULT.WRONG_INITIATOR_BATTLE_STATE

        if initiator_id not in pvp_balancer.arena_queue:
            pvp_balancer.add_to_arena_queue(hero_id)

        pvp_balancer.force_battle(accepted_battle.account_id, initiator_id)

        return ACCEPT_BATTLE_RESULT.PROCESSED


    def use(self, task, storage, pvp_balancer=None, **kwargs):

        if task.step.is_LOGIC:

            task.hero.update_habits(heroes_relations.HABIT_CHANGE_SOURCE.ARENA_SEND)

            task.hero.process_removed_artifacts()

            return task.logic_result(next_step=game_postponed_tasks.ComplexChangeTask.STEP.PVP_BALANCER)

        elif task.step.is_PVP_BALANCER:

            accept_result = self.accept_battle(pvp_balancer, task.data['battle_id'], task.data['hero_id'])

            if not accept_result.is_PROCESSED:
                return task.logic_result(next_step=game_postponed_tasks.ComplexChangeTask.STEP.ERROR)

            return task.logic_result()
