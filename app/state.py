from exceptions import StatefulObjectException


class StateFactory(object):

    @staticmethod
    def create(states):
        model = object()
        model.ALL = xrange(len(states))
        for i in model.ALL:
            setattr(model, states[i], i)

        return model


class StateTransition(object):

    @property
    def from_state(self):
        return self._from_state

    @property
    def to_state(self):
        return self._to_state

    @property
    def conditional(self):
        return self._conditional

    @property
    def trigger(self):
        return self._trigger

    def __init__(self, from_state, to_state, conditional=None, trigger=None):
        self._from_state = from_state
        self._to_state = to_state
        self._conditional = conditional
        self._trigger = trigger


class StatefulObject(object):

    @staticmethod
    def generate_transitions_map(transitions):
        transitions_map = {}
        for transition in transitions:
            if not isinstance(transition, StateTransition):
                raise StatefulObjectException("invalid transition provided.")

            transitions_map.setdefault(transition.from_state, []).append(transition)

        return transitions_map

    def __init__(self, model, states, transitions, default_state=None):
        if model is None:
            raise StatefulObjectException("invalid model provided.")

        if not isinstance(states, list) or len(states) < 1:
            raise StatefulObjectException("empty states list provided")

        if not isinstance(transitions, list) or len(transitions) < 1:
            raise StatefulObjectException("empty transitions list provided")

        self._model = model
        self._states = states
        self._transitions_map = self.generate_transitions_map(transitions)
        self._state = default_state or states[0]

    def refresh(self):
        transitions = self._transitions_map.get(self._state)
        for transition in transitions:
            conditional = getattr(self._model, transition.conditional)
            trigger = getattr(self._model, transition.trigger)

            if conditional:
                if conditional[0] == '!':
                    conditional = conditional[1:]
                    conditional_check = False
                else:
                    conditional_check = True

                if conditional() != conditional_check:
                    continue

            self._state = transition.to_state

            if trigger:
                trigger()

            return

        raise StatefulObjectException("no valid next state found from state {}".format(self._state))

    def matches(self, state):
        return self._state == state

    def set_state(self, state):
        if state not in self._states:
            raise StatefulObjectException("invalid state provided: {}".format(state))

        self._state = state