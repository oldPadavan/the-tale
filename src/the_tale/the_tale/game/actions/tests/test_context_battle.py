
import smart_imports

smart_imports.all()


class BattleContextTest(utils_testcase.TestCase):

    def setUp(self):
        super(BattleContextTest, self).setUp()
        self.context = contexts.BattleContext()

    def check_empty_values(self):
        self.assertEqual(self.context.ability_magic_mushroom, [])
        self.assertEqual(self.context.ability_sidestep, [])
        self.assertEqual(self.context.stun_length, 0)
        self.assertEqual(self.context.crit_chance, 0)
        self.assertEqual(self.context.berserk_damage_modifier, 1.0)
        self.assertEqual(self.context.ninja, 0)
        self.assertEqual(self.context.damage_queue_fire, [])
        self.assertEqual(self.context.damage_queue_poison, [])
        self.assertEqual(self.context.initiative_queue, [])

        self.assertEqual(self.context.incoming_magic_damage_modifier, 1.0)
        self.assertEqual(self.context.incoming_physic_damage_modifier, 1.0)
        self.assertEqual(self.context.outcoming_magic_damage_modifier, 1.0)
        self.assertEqual(self.context.outcoming_physic_damage_modifier, 1.0)

        self.assertEqual(self.context.pvp_advantage, 0)
        self.assertFalse(self.context.pvp_advantage_used)
        self.assertEqual(self.context.pvp_advantage_strike_damage, power.Damage(0, 0))


    def test_create(self):
        self.check_empty_values()

    @mock.patch('the_tale.game.balance.constants.DAMAGE_DELTA', 0)
    def test_damage(self):
        damage = power.Damage(100, 50)
        damage.multiply(0.5, 2)
        self.assertEqual(damage, power.Damage(50, 100))

        damage = power.Damage(100.5, 50.5)
        damage.randomize()
        self.assertEqual(damage.total, 151)

    def test_damage_queue_fire(self):
        self.assertEqual(self.context.fire_damage, None)
        self.context.use_damage_queue_fire([power.Damage(0, 0)])
        self.assertEqual(self.context.fire_damage, None)

        self.context.use_damage_queue_fire([power.Damage(5, 5), power.Damage(5, 5), power.Damage(5, 5)])
        self.assertEqual(self.context.damage_queue_fire, [power.Damage(0, 0), power.Damage(5, 5), power.Damage(5, 5), power.Damage(5, 5)])
        self.context.on_own_turn()
        self.assertEqual(self.context.damage_queue_fire, [power.Damage(5, 5), power.Damage(5, 5), power.Damage(5, 5)])
        self.assertEqual(self.context.fire_damage, power.Damage(5, 5))

        self.context.use_damage_queue_fire([power.Damage(10, 10), power.Damage(5, 5)])
        self.assertEqual(self.context.damage_queue_fire, [power.Damage(5, 5), power.Damage(15, 15), power.Damage(10, 10)])
        self.context.on_own_turn()
        self.assertEqual(self.context.fire_damage, power.Damage(15, 15))

        self.context.on_own_turn()
        self.assertEqual(self.context.damage_queue_fire, [power.Damage(10, 10)])
        self.assertEqual(self.context.fire_damage, power.Damage(10, 10))

        self.context.use_damage_queue_fire([power.Damage(1, 1), power.Damage(1, 1), power.Damage(1, 1), power.Damage(1, 1)])
        self.assertEqual(self.context.damage_queue_fire, [power.Damage(10, 10), power.Damage(1, 1), power.Damage(1, 1), power.Damage(1, 1), power.Damage(1, 1)])
        self.assertEqual(self.context.fire_damage, power.Damage(10, 10))
        self.context.on_own_turn()
        self.assertEqual(self.context.fire_damage, power.Damage(1, 1))

        self.assertEqual(self.context.serialize(), contexts.BattleContext.deserialize(self.context.serialize()).serialize())

    def test_damage_queue_poison(self):
        self.assertEqual(self.context.poison_damage, None)
        self.context.use_damage_queue_poison([power.Damage(0, 0)])
        self.assertEqual(self.context.poison_damage, None)

        self.context.use_damage_queue_poison([power.Damage(5, 5), power.Damage(5, 5), power.Damage(5, 5)])
        self.assertEqual(self.context.damage_queue_poison, [power.Damage(0, 0), power.Damage(5, 5), power.Damage(5, 5), power.Damage(5, 5)])
        self.context.on_own_turn()
        self.assertEqual(self.context.damage_queue_poison, [power.Damage(5, 5), power.Damage(5, 5), power.Damage(5, 5)])
        self.assertEqual(self.context.poison_damage, power.Damage(5, 5))

        self.context.use_damage_queue_poison([power.Damage(10, 10), power.Damage(5, 5), power.Damage(5, 5)])
        self.context.on_own_turn()
        self.assertEqual(self.context.damage_queue_poison, [power.Damage(15, 15), power.Damage(10, 10), power.Damage(5, 5)])
        self.assertEqual(self.context.poison_damage, power.Damage(15, 15))

        self.context.on_own_turn()
        self.assertEqual(self.context.damage_queue_poison, [power.Damage(10, 10), power.Damage(5, 5)])
        self.assertEqual(self.context.poison_damage, power.Damage(10, 10))

        self.context.use_damage_queue_poison([power.Damage(1, 1), power.Damage(1, 1), power.Damage(1, 1), power.Damage(1, 1)])
        self.assertEqual(self.context.damage_queue_poison, [power.Damage(10, 10), power.Damage(6, 6), power.Damage(1, 1), power.Damage(1, 1), power.Damage(1, 1)])
        self.context.on_own_turn()
        self.assertEqual(self.context.damage_queue_poison, [power.Damage(6, 6), power.Damage(1, 1), power.Damage(1, 1), power.Damage(1, 1)])
        self.assertEqual(self.context.poison_damage, power.Damage(6, 6))

        self.assertEqual(self.context.serialize(), contexts.BattleContext.deserialize(self.context.serialize()).serialize())

    def test_initiative_queue(self):
        self.assertEqual(self.context.initiative, 1.0)

        self.context.use_initiative([90, 90, 90, 90])
        self.context.on_own_turn()
        self.assertEqual(self.context.initiative_queue, [90, 90, 90])
        self.assertEqual(self.context.initiative, 90)

        self.context.use_initiative([11, 9])
        self.context.on_own_turn()
        self.assertEqual(self.context.initiative_queue, [810, 90])
        self.assertEqual(self.context.initiative, 810)

        self.context.on_own_turn()
        self.assertEqual(self.context.initiative_queue, [90])
        self.assertEqual(self.context.initiative, 90)

        self.context.use_initiative([10, 10, 10, 10])
        self.assertEqual(self.context.initiative_queue, [900, 10, 10, 10])
        self.context.on_own_turn()
        self.assertEqual(self.context.initiative, 10)


    @mock.patch('the_tale.game.balance.constants.DAMAGE_DELTA', 0)
    def test_ability_magic_mushroom(self):
        self.context.use_ability_magic_mushroom([2.0, 1.0, 0.5])
        self.assertEqual(self.context.ability_magic_mushroom, [None, 2.0, 1.0, 0.5])

        self.context.on_own_turn()
        self.assertEqual(self.context.ability_magic_mushroom, [2.0, 1.0, 0.5])
        self.assertEqual(self.context.modify_outcoming_damage(power.Damage(10, 5)), power.Damage(20, 10))

        self.context.on_own_turn()
        self.assertEqual(self.context.ability_magic_mushroom, [1.0, 0.5])
        self.assertEqual(self.context.modify_outcoming_damage(power.Damage(10, 5)), power.Damage(10, 5))

        self.context.on_own_turn()
        self.assertEqual(self.context.ability_magic_mushroom, [0.5])
        self.assertEqual(self.context.modify_outcoming_damage(power.Damage(10, 5)).total, 8)

        self.context.on_own_turn()
        self.assertEqual(self.context.ability_magic_mushroom, [])
        self.assertEqual(self.context.modify_outcoming_damage(power.Damage(10, 5)), power.Damage(10, 5))


    def test_ability_sidestep(self):
        self.context.use_ability_sidestep([1.0, 0.5, 0.0])
        self.assertEqual(self.context.ability_sidestep, [None, 1.0, 0.5, 0])

        self.context.on_own_turn()
        self.assertEqual(self.context.ability_sidestep, [1.0, 0.5, 0])
        self.assertTrue(self.context.should_miss_attack())

        self.context.on_own_turn()
        self.assertEqual(self.context.ability_sidestep, [0.5, 0])
        self.assertTrue(self.context.should_miss_attack() in [True, False])

        self.context.on_own_turn()
        self.assertEqual(self.context.ability_sidestep, [0])
        self.assertTrue(not self.context.should_miss_attack())

        self.context.on_own_turn()
        self.assertEqual(self.context.ability_sidestep, [])
        self.assertTrue(not self.context.should_miss_attack())


    def test_stun(self):
        self.context.use_stun(3)
        self.assertEqual(self.context.stun_length, 4)

        # longes stun must be used
        self.context.use_stun(1)
        self.assertEqual(self.context.stun_length, 4)

        for i in range(3):
            self.context.on_own_turn()
            self.assertEqual(self.context.stun_length, 3-i)
            self.assertTrue(self.context.is_stunned)

        self.context.on_own_turn()
        self.assertEqual(self.context.stun_length, 0)
        self.assertTrue(not self.context.is_stunned)

    @mock.patch('the_tale.game.balance.constants.DAMAGE_DELTA', 0)
    def test_modify_outcoming_damage(self):
        self.assertEqual(self.context.modify_outcoming_damage(power.Damage(10, 11)).total, 21)
        self.assertEqual(self.context.modify_outcoming_damage(power.Damage(10.4, 11.4)).total, 22)
        self.assertEqual(self.context.modify_outcoming_damage(power.Damage(10.5, 11.5)).total, 22)
        self.assertEqual(self.context.modify_outcoming_damage(power.Damage(10.8, 11.8)).total, 23)

        # advantage_modifier
        self.context.use_pvp_advantage(0.75)
        self.assertEqual(self.context.modify_outcoming_damage(power.Damage(20, 10)),
                         power.Damage(20*(1+c.DAMAGE_PVP_ADVANTAGE_MODIFIER*0.75), 10*(1+c.DAMAGE_PVP_ADVANTAGE_MODIFIER*0.75)))
        self.assertFalse(self.context.pvp_advantage_used)

        self.context.use_pvp_advantage(-0.75)
        self.assertEqual(self.context.modify_outcoming_damage(power.Damage(20, 10)), power.Damage(20, 10))
        self.assertFalse(self.context.pvp_advantage_used)

        self.assertEqual(self.context.serialize(), contexts.BattleContext.deserialize(self.context.serialize()).serialize())

    @mock.patch('the_tale.game.balance.constants.DAMAGE_DELTA', 0)
    def test_modify_outcoming_damage_advantage_strike(self):
        self.context.use_pvp_advantage(1.0)
        self.assertEqual(self.context.modify_outcoming_damage(power.Damage(20, 10)), power.Damage(0, 0)) # pvp_advantage_strike_damage not set
        self.context.use_pvp_advantage_stike_damage(power.Damage(333, 666))
        self.assertEqual(self.context.modify_outcoming_damage(power.Damage(20, 10)), power.Damage(333, 666))
        self.assertTrue(self.context.pvp_advantage_used)


    @mock.patch('the_tale.game.balance.constants.DAMAGE_DELTA', 0)
    def test_critical_hit(self):
        old_damage = self.context.modify_outcoming_damage(power.Damage(100, 1000))
        self.context.use_crit_chance(100)
        new_damage = self.context.modify_outcoming_damage(power.Damage(100, 1000))
        self.assertTrue(old_damage.physic < new_damage.physic)
        self.assertTrue(old_damage.magic < new_damage.magic)

    @mock.patch('the_tale.game.balance.constants.DAMAGE_DELTA', 0)
    def test_berserk(self):
        old_damage = self.context.modify_outcoming_damage(power.Damage(100, 10))
        self.context.use_berserk(1.0)
        self.assertEqual(old_damage, self.context.modify_outcoming_damage(power.Damage(100, 10)))
        self.context.use_berserk(1.5)
        new_damage = self.context.modify_outcoming_damage(power.Damage(100, 10))
        self.assertTrue(old_damage.physic < new_damage.physic)
        self.assertTrue(old_damage.magic < new_damage.magic)

    def test_ninja(self):
        self.context.use_ninja(1.0)
        for i in range(100):
            self.assertTrue(self.context.should_miss_attack())

    @mock.patch('the_tale.game.balance.constants.DAMAGE_DELTA', 0)
    def test_outcoming_damage_modifier(self):
        self.assertEqual(self.context.modify_outcoming_damage(power.Damage(100, 1000)), power.Damage(100, 1000))
        self.context.use_outcoming_damage_modifier(5, 0.25)
        self.assertEqual(self.context.modify_outcoming_damage(power.Damage(100, 1000)), power.Damage(500, 250))
        self.context.use_outcoming_damage_modifier(2, 10)
        self.assertEqual(self.context.modify_outcoming_damage(power.Damage(100, 1000)), power.Damage(1000, 2500))

    def test_incoming_damage_modifier(self):
        self.assertEqual(self.context.modify_incoming_damage(power.Damage(100, 1000)), power.Damage(100, 1000))
        self.context.use_incoming_damage_modifier(5, 0.25)
        self.assertEqual(self.context.modify_incoming_damage(power.Damage(100, 1000)), power.Damage(500, 250))
        self.context.use_incoming_damage_modifier(2, 10)
        self.assertEqual(self.context.modify_incoming_damage(power.Damage(100, 1000)), power.Damage(1000, 2500))


    def test_on_own_turn_with_empty_values(self):
        self.context.on_own_turn()
        self.check_empty_values()
