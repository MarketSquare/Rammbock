

class ConditionParser(object):

    def __init__(self, condition):
        if '==' in condition:
            self.name, self.value = self._parse('==', condition)

            def evaluate(msg_fields):
                return self._get_field(msg_fields) == self.value
            self.evaluate = evaluate
        elif '!=' in condition:
            self.name, self.value = self._parse('!=', condition)

            def evaluate(msg_fields):
                return self._get_field(msg_fields) != self.value
            self.evaluate = evaluate
        else:
            raise IllegalConditionException('Unsupported operation: %s' % condition)

    def _parse(self, operator, condition):
        cond = condition.partition(operator)
        name = cond[0].strip()
        if not name:
            raise IllegalConditionException('Illegal condition: %s' % condition)
        value = self._parse_value(cond[2].strip())
        return name, value

    def _parse_value(self, value):
        try:
            return int(value)
        except:
            raise IllegalConditionException('Expected integer, unsupported value given: %s' % value)

    def _get_field(self, msg_fields):
        if self.name not in msg_fields:
            raise IllegalConditionException('Given name condition: %s not found in message fields' % self.name)
        return msg_fields[self.name].int


class IllegalConditionException(Exception):
    pass
