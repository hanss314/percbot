def say_list(l, default='no one'):
    if not l: return default
    elif len(l) == 1: return l[0]
    else:
        s = ''
        for member in l[:-1]:
            s += '{}, '.format(member)
        s += 'and ' + l[-1]
        return s
    
def to_lower(s):
    return s.lower()
    

    
