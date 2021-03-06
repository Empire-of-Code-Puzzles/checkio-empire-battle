from battle import ROLE, PARTY

ERR_ID_TYPE = "{name} ID must be an integer"
ERR_ARRAY_TYPE = "{name} must be a list/tuple"
ERR_COORDINATES_TYPE = "{name} must be a list/tuple with two numbers."
ERR_CALLABLE_TYPE = "{name} must be callable (function)"
ERR_STR_TYPE = "{name} must be a string"
ERR_NUMBER_TYPE = "{name} must be a number."
ERR_NUMBER_POSITIVE_VALUE = "{name} must be a positive."
ERR_ARRAY_VALUE = "{name} must contains only correct values"


def check_coordinates(coordinates, name):
    if not (isinstance(coordinates, (list, tuple)) and
            len(coordinates) == 2 and
            all(isinstance(n, (float, int)) for n in coordinates)):
        raise TypeError(ERR_COORDINATES_TYPE.format(name=name))


def check_item_id(item_id):
    if not isinstance(item_id, int):
        raise TypeError(ERR_ID_TYPE.format(name="Item"))


def check_array(array, correct_values, name):
    if not isinstance(array, (list, tuple)):
        raise TypeError(ERR_ARRAY_TYPE.format(name=name))
    if not all(el in correct_values for el in array):
        raise ValueError(ERR_ARRAY_VALUE.format(name=name))


def check_radius(number):
    if not isinstance(number, (int, float)):
        raise TypeError(ERR_NUMBER_TYPE.format(name="Radius"))
    if number <= 0:
        raise ValueError(ERR_NUMBER_POSITIVE_VALUE.format(name="Radius"))


def check_callable(func, name):
    if not callable(func):
        raise TypeError(ERR_CALLABLE_TYPE.format(name))


def check_str_type(data, name):
    if not isinstance(data, str):
        raise TypeError(ERR_STR_TYPE.format(name))


class Client(object):
    CLIENT = None

    def __init__(self):
        assert self.CLIENT
        self._initial_info = self.ask_my_info()

    @property
    def item_id(self):
        return self._initial_info["id"]

    @property
    def player_id(self):
        return self._initial_info["player_id"]

    @classmethod
    def set_client(cls, client):
        cls.CLIENT = client

    def ask(self, fields):
        return self.CLIENT.select(fields=[fields])[0]

    select = ask

    def ask_my_info(self):
        return self.ask(
            {
                'field': 'my_info'
            })

    def ask_item_info(self, item_id):
        check_item_id(item_id)
        return self.ask(
            {
                'field': 'item_info',
                'data': {
                    "id": item_id
                }
            })

    def ask_items(self, parties=PARTY.ALL, roles=ROLE.ALL):
        check_array(parties, PARTY.ALL, "Parties")
        check_array(roles, ROLE.ALL, "Roles")
        return self.ask(
            {
                'field': 'items',
                'data': {
                    PARTY.REQUEST_NAME: parties,
                    ROLE.REQUEST_NAME: roles
                }
            })

    def ask_enemy_items(self):
        return self.ask_items(parties=(PARTY.ENEMY,))

    def ask_my_items(self):
        return self.ask_items(parties=(PARTY.MY,))

    def ask_buildings(self):
        return self.ask_items(roles=(ROLE.CENTER, ROLE.BUILDING))

    def ask_towers(self):
        return self.ask_items(roles=(ROLE.TOWER,))

    def ask_center(self):
        centers = self.ask_items(roles=(ROLE.CENTER,))
        return centers[0] if centers else None

    def ask_units(self):
        return self.ask_items(roles=(ROLE.UNIT,))

    def ask_players(self, parties=PARTY.ALL):
        check_array(parties, PARTY.ALL, "Parties")
        return self.ask(
            {
                'field': 'players',
                'data': {
                    PARTY.REQUEST_NAME: parties
                }
            })

    def ask_enemy_players(self):
        return self.ask_players(parties=(PARTY.ENEMY,))

    def ask_nearest_enemy(self):
        return self.ask(
            {
                'field': 'nearest_enemy',
                'data': {
                    'id': self.item_id
                }
            })

    def ask_my_range_enemy_items(self):
        return self.ask(
            {
                'field': 'enemy_items_in_my_firing_range',
                'data': {
                    'id': self.item_id
                }
            })

    ask_enemy_items_in_my_firing_range = ask_my_range_enemy_items

    def do(self, action, data):
        return self.CLIENT.set_action(action, data)

    def do_attack(self, item_id):
        check_item_id(item_id)
        return self.do('attack', {'id': item_id})

    attack_item = do_attack

    def do_move(self, coordinates):
        check_coordinates(coordinates, "Coordinates")
        return self.do('move', {'coordinates': coordinates})

    move_to_point = do_move

    def when(self, event, callback, data=None):
        check_callable(callback, "Callback")
        check_str_type(event, "Event")
        return self.CLIENT.subscribe(event, callback, data)

    subscribe = when

    def unsubscribe_all(self):
        return self.when('unsubscribe_all', None)

    def when_in_area(self, center, radius, callback):
        check_coordinates(center, "Center coordinates")
        check_radius(radius)
        return self.when('im_in_area', callback, {
            'coordinates': center,
            'radius': radius
        })

    subscribe_im_in_area = when_in_area

    def when_item_in_area(self, center, radius, callback):
        check_coordinates(center, "Center coordinates")
        check_radius(radius)
        return self.when('any_item_in_area', callback, {
            'coordinates': center,
            'radius': radius
        })

    subscribe_any_item_in_area = when_item_in_area

    def when_stop(self, callback):
        return self.when('im_stop', callback, {})

    subscribe_im_stop = when_stop

    def when_idle(self, callback):
        return self.when('im_idle', callback, {})

    subscribe_im_idle = when_idle

    def when_enemy_in_range(self, callback):
        return self.when('enemy_in_my_firing_range', callback)

    subscribe_enemy_in_my_firing_range = when_enemy_in_range

    def when_enemy_out_range(self, item_id, callback):
        check_item_id(item_id)
        return self.when('the_item_out_my_firing_range', callback, {"item_id": item_id})

    subscribe_the_item_out_my_firing_range = when_enemy_out_range

    def when_item_destroyed(self, item_id, callback):
        check_item_id(item_id)
        return self.when('death', callback, {'id': item_id})

    subscribe_the_item_is_dead = when_item_destroyed
