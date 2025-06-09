from collections import deque, OrderedDict
from firstfollow import production_list, nt_list as ntl, t_list as tl, compute_first, compute_follow, get_first, get_follow

nt_list, t_list = [], []

class State:
    _id = 0
    def __init__(self, closure):
        self.closure = closure
        self.no = State._id
        State._id += 1

class Item(str):
    def __new__(cls, item, lookahead=list()):
        self = str.__new__(cls, item)
        self.lookahead = lookahead
        return self

    def __str__(self):
        return super(Item, self).__str__() + ", " + '|'.join(self.lookahead)

def closure(items):
    while True:
        flag = 0
        for i in items:
            if i.index('.') == len(i) - 1: continue
            body = i.split('->')[1]
            after_dot = body.split('.')[1]

            Y = after_dot[0]
            symbols = list(after_dot[1:])
            lastr = compute_first(symbols) - {chr(1013)} if symbols else i.lookahead

            for prod in production_list:
                head, body = prod.split('->')
                if head != Y: continue
                newitem = Item(Y + '->.' + body, list(lastr))
                if not any(j == newitem and sorted(set(j.lookahead)) == sorted(set(newitem.lookahead)) for j in items):
                    items.append(newitem)
                    flag = 1
        if not flag: break
    return items

def goto(items, symbol):
    initial = []
    for i in items:
        if i.index('.') == len(i) - 1: continue
        head, body = i.split('->')
        seen, unseen = body.split('.')
        if unseen[0] == symbol and len(unseen) >= 1:
            initial.append(Item(head + '->' + seen + unseen[0] + '.' + unseen[1:], i.lookahead))
    return closure(initial)

def states_equal(s1, s2):
    if len(s1) != len(s2): return False
    s1_sorted = sorted(s1, key=str)
    s2_sorted = sorted(s2, key=str)
    for i in range(len(s1_sorted)):
        if s1_sorted[i] != s2_sorted[i]: return False
        if sorted(s1_sorted[i].lookahead) != sorted(s2_sorted[i].lookahead): return False
    return True

def calc_states():
    head, body = production_list[0].split('->')
    states = [closure([Item(head + '->.' + body, ['$'])])]
    while True:
        flag = 0
        for s in states:
            for e in nt_list + t_list:
                t = goto(s, e)
                if t == [] or any(states_equal(x, t) for x in states):
                    continue
                states.append(t)
                flag = 1
        if not flag: break
    return states

def make_table(states):
    def getstateno(t):
        for s in states:
            if states_equal(s.closure, t):
                return s.no
        return -1

    def getprodno(closure):
        return production_list.index(''.join(closure).replace('.', ''))

    SLR_Table = OrderedDict()
    for i in range(len(states)):
        states[i] = State(states[i])

    for s in states:
        SLR_Table[s.no] = OrderedDict()
        for item in s.closure:
            head, body = item.split('->')
            if body == '.':
                for term in item.lookahead:
                    SLR_Table[s.no].setdefault(term, set()).add('r' + str(getprodno(item)))
                continue

            nextsym = body.split('.')[1]
            if nextsym == '':
                if getprodno(item) == 0:
                    SLR_Table[s.no]['$'] = 'ac'
                else:
                    for term in item.lookahead:
                        SLR_Table[s.no].setdefault(term, set()).add('r' + str(getprodno(item)))
                continue

            nextsym = nextsym[0]
            t = goto(s.closure, nextsym)
            if t != []:
                if nextsym in t_list:
                    SLR_Table[s.no].setdefault(nextsym, set()).add('s' + str(getstateno(t)))
                else:
                    SLR_Table[s.no][nextsym] = str(getstateno(t))
    return SLR_Table

def augment_grammar():
    for i in range(ord('Z'), ord('A') - 1, -1):
        if chr(i) not in nt_list:
            start_prod = production_list[0]
            production_list.insert(0, chr(i) + '->' + start_prod.split('->')[0])
            return

def run_clr(productions):
    from firstfollow import main as ff_main
    global nt_list, t_list
    production_list.clear()
    production_list.extend(productions)
    nt_list.clear()
    t_list.clear()

    ff_main()

    nt_list[:] = list(ntl.keys())
    t_list[:] = list(tl.keys()) + ['$']

    for nt in nt_list:
        compute_first(nt)
        compute_follow(nt)

    augment_grammar()
    states = calc_states()
    parsing_table = make_table(states)

    first_follow_data = {
        nt: {
            "FIRST": get_first(nt),
            "FOLLOW": get_follow(nt)
        }
        for nt in nt_list
    }

    return {
        "first_follow": first_follow_data,
        "states": states,
        "parsing_table": parsing_table,
        "non_terminals": nt_list,
        "terminals": t_list
    }
