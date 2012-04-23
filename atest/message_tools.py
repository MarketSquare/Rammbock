def field_should_not_exist(message_struct, field_name):
    if field_name in message_struct:
        raise AssertionError('Field %s was found in %s' % (field_name, message_struct))
    
def field_should_exist(message_struct, field_name):
    if field_name not in message_struct:
        raise AssertionError('Field %s was not found in %s' % (field_name, message_struct))    