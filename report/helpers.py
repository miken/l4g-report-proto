def str_truncate(string):
    '''
    If a string is longer than 30 characters, add
    ellipsis to the string and truncate it
    '''
    if len(string) > 30:
        return u'{}...'.format(string[:30])
    else:
        return string
