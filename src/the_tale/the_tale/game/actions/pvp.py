
import smart_imports

smart_imports.all()


class PvPData(object):

    __slots__ = ('advantage', 'effectiveness', 'energy', 'energy_speed', 'turn_advantage', 'turn_effectiveness', 'turn_energy', 'turn_energy_speed')

    def __init__(self):
        self.advantage = 0
        self.effectiveness = c.PVP_EFFECTIVENESS_INITIAL

        self.energy = 0
        self.energy_speed = 1

        self.turn_advantage = 0
        self.turn_effectiveness = 0

        self.turn_energy = 0
        self.turn_energy_speed = 1

        self.store_turn_data()

    def set_advantage(self, value):
        self.advantage = value
        if self.advantage < -1: self.advantage = -1
        if self.advantage > 1: self.advantage = 1

    def set_effectiveness(self, value):
        self.effectiveness = value

    def set_energy(self, value):
        self.energy = value

    def set_energy_speed(self, value):
        self.energy_speed = value

    def serialize(self):
        return {'advantage': self.advantage,
                'effectiveness': self.effectiveness,
                'energy': self.energy,
                'energy_speed': self.energy_speed,

                'turn_advantage': self.turn_advantage,
                'turn_effectiveness': self.turn_effectiveness,
                'turn_energy': self.turn_energy,
                'turn_energy_speed': self.turn_energy_speed }

    @classmethod
    def deserialize(cls, data):
        obj = cls()

        obj.advantage = data.get('advantage', 0)
        obj.effectiveness = data.get('effectiveness', 0)
        obj.energy = data.get('energy', 0)
        obj.energy_speed = data.get('energy_speed', 1)

        obj.turn_advantage = data.get('turn_advantage', 0)
        obj.turn_effectiveness = data.get('turn_effectiveness', 0)
        obj.turn_energy = data.get('turn_energy', 0)
        obj.turn_energy_speed = data.get('turn_energy_speed', 1)

        return obj

    def ui_info(self):
        return  { 'advantage': self.advantage,
                  'effectiveness': int(self.effectiveness),
                  'probabilities': { 'ice': pvp_abilities.Ice.get_probability(self.energy, self.energy_speed),
                                     'blood': pvp_abilities.Blood.get_probability(self.energy, self.energy_speed),
                                     'flame': pvp_abilities.Flame.get_probability(self.energy, self.energy_speed) },
                  'energy': self.energy,
                  'energy_speed': self.energy_speed }

    def turn_ui_info(self):
        return  { 'advantage': self.turn_advantage,
                  'effectiveness': int(self.turn_effectiveness),
                  'probabilities': { 'ice': pvp_abilities.Ice.get_probability(self.turn_energy, self.turn_energy_speed),
                                     'blood': pvp_abilities.Blood.get_probability(self.turn_energy, self.turn_energy_speed),
                                     'flame': pvp_abilities.Flame.get_probability(self.turn_energy, self.turn_energy_speed) },
                  'energy': self.turn_energy,
                  'energy_speed': self.turn_energy_speed }

    def store_turn_data(self):
        self.turn_advantage = self.advantage
        self.turn_effectiveness = self.effectiveness
        self.turn_energy = self.energy
        self.turn_energy_speed = self.energy_speed
