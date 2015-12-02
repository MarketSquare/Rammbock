from unittest import TestCase, main
from Rammbock.condition_parser import ConditionParser, IllegalConditionException
from Rammbock.message import Struct, Field
from Rammbock.binary_tools import to_bin


def uint_field(value='0x00'):
    return Field('uint', 'name', to_bin(value))


def create_message(params):
    struct = Struct('foo', 'foo_type')
    for key in params:
        struct[key] = uint_field(params[key])
    return struct


class TestConditionParser(TestCase):

    def condition(self, cond, msg_param, status):
        parent = create_message(msg_param)
        conditionparser = ConditionParser(cond)
        condition = conditionparser.evaluate(parent)
        self.assertEquals(condition, status)

    def condition_exception(self, cond):
        self.assertRaises(IllegalConditionException, ConditionParser, cond)

    def condition_evaluate_exception(self, cond, msg_param):
        parent = create_message(msg_param)
        conditionparser = ConditionParser(cond)
        self.assertRaises(IllegalConditionException, conditionparser.evaluate, parent)

    def test_create_parser(self):
        self.condition('mycondition == 1', {'mycondition': 0}, False)

    def test_evaluate_condition_returns_true(self):
        self.condition('mycondition == 1', {'mycondition': 1}, True)

    def test_evaluate_unequality_condition(self):
        self.condition('mycondition != 1', {'mycondition': 0}, True)
        self.condition(' mycondition != 1', {'mycondition': 0}, True)
        self.condition('mycondition != 1 ', {'mycondition': 0}, True)
        self.condition(' mycondition != 1', {'mycondition': 1}, False)
        self.condition('mycondition!=1 ', {'mycondition': 1}, False)

    def test_evaluate_unsupported_operator(self):
        self.condition_exception('mycondition >= 1')
        self.condition_exception('mycondition == foo')
        self.condition_exception('mycondition == ')
        self.condition_exception(' == 1')
        self.condition_exception('   ')

    def test_failing_evaluate(self):
        self.condition_evaluate_exception('mycondition != 1', {'foo': 0})

    def test_evaluate_or_conditional(self):
        values = {'foo': 2, 'bar': 3}
        self.condition('foo == 2 || bar != 2', values, True)
        self.condition('foo != 2 || bar != 2', values, True)
        self.condition('foo != 2 || bar != 3', values, False)
        self.condition('foo == 2 || bar != 3', values, True)

    def test_evaluate_and_conditional(self):
        values = {'foo': 2, 'bar': 3}
        self.condition('foo == 2 && bar == 3', values, True)
        self.condition('foo != 1 && bar == 2', values, False)
        self.condition('foo == 3 && bar != 1', values, False)
        self.condition('foo == 1 && bar == 0', values, False)

    def test_evaluate_multiple_and_conditions(self):
        values = {'foo': 2, 'bar': 3}
        self.condition('foo == 2 && bar == 3 && foo == 2', values, True)
        self.condition('foo == 1 || bar == 2 || foo == 4', values, False)
