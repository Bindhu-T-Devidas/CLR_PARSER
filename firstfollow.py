
production_list = []
nt_list = {}
t_list = {}

class NonTerminal:
    def __init__(self):
        self.first = set()
        self.follow = set()
        self.productions = []

def main():
    global nt_list, t_list
    nt_list.clear()
    t_list.clear()
    for prod in production_list:
        head, body = prod.split('->')
        if head not in nt_list:
            nt_list[head] = NonTerminal()
        nt_list[head].productions.append(body)

        for char in body:
            if not char.isupper() and char != '':
                t_list[char] = True

def compute_first(symbols):
    if isinstance(symbols, list):
        result = set()
        for symbol in symbols:
            temp = compute_first(symbol)
            result |= temp - {chr(1013)}
            if chr(1013) not in temp:
                break
        else:
            result.add(chr(1013))
        return result

    if symbols in t_list:
        return {symbols}
    if symbols not in nt_list:
        return set()

    sym_first = nt_list[symbols].first
    if sym_first:
        return sym_first

    nt_list[symbols].first = set()
    for prod in nt_list[symbols].productions:
        if prod == "":
            nt_list[symbols].first.add(chr(1013))
        else:
            for sym in prod:
                f = compute_first(sym)
                nt_list[symbols].first |= f - {chr(1013)}
                if chr(1013) not in f:
                    break
            else:
                nt_list[symbols].first.add(chr(1013))

    return nt_list[symbols].first

def compute_follow(symbol):
    if not nt_list[symbol].follow:
        if production_list[0].startswith(symbol):
            nt_list[symbol].follow.add('$')

        for prod in production_list:
            head, body = prod.split('->')
            for i in range(len(body)):
                if body[i] == symbol:
                    if i + 1 < len(body):
                        temp_first = compute_first(list(body[i + 1:]))
                        nt_list[symbol].follow |= temp_first - {chr(1013)}
                        if chr(1013) in temp_first:
                            nt_list[symbol].follow |= compute_follow(head)
                    else:
                        if head != symbol:
                            nt_list[symbol].follow |= compute_follow(head)
    return nt_list[symbol].follow

def get_first(symbol):
    return nt_list[symbol].first

def get_follow(symbol):
    return nt_list[symbol].follow
