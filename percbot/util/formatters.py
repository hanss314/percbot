def say_list(l, default='no one', before='', after=''):
    if not l: return default
    elif len(l) == 1: return before+l[0]+after
    else:
        s = ''
        for member in l[:-1]:
            s += '{}{}{}, '.format(before,member,after)
        s += 'and ' + before+l[-1]+after
        return s
    
def to_lower(s):
    return s.lower()
    

    
