class ConditionParser(object):

    def __init__(self, condition):
        import re
        logicals = re.split('(&&|\|\|)', condition)
        self.conditions = self._get_individual_conditions(logicals)

    def _get_individual_conditions(self, logicals):
        conditions = []
        for element in logicals:
            if element in ('&&', '||'):
                conditions.append(element)
            else:
                conditions.append(ExpressionEvaluator(element))
        return conditions

    def evaluate(self, msg_fields):
        status = True
        operator = '&&'
        for condition in self.conditions:
            if condition in ('&&', '||'):
                operator = condition
            else:
                evaluated = condition.evaluate(msg_fields)
                if operator == '&&':
                    status = status and evaluated
                else:
                    status = status or evaluated
        return status


class ExpressionEvaluator(object):

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

    def _get_field(self, elem):
        for part in self.name.split('.'):
            if part not in elem:
                raise IllegalConditionException('Given name condition: %s not found in message fields' % self.name)
            elem = elem[part]
        return elem.int


class IllegalConditionException(Exception):
    pass
