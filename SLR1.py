import copy

def augment_grammar(rules, nonterminals, start_symbol):
    new_rules = []
    new_char = start_symbol + "'"
    while new_char in nonterminals:
        new_char += "'"
    new_rules.append([new_char, ['.', start_symbol]])
    for rule in rules:
        k = rule.split("->")
        lhs = k[0].strip()
        rhs = k[1].strip()
        multirhs = rhs.split('|')
        for rhs1 in multirhs:
            rhs1 = rhs1.strip().split()
            rhs1.insert(0, '.')
            new_rules.append([lhs, rhs1])
    return new_rules

def find_closure(input_state, dot_symbol):
    global start_symbol, separated_rules_list, states_dict
    closure_set = []
    if dot_symbol == start_symbol:
        for rule in separated_rules_list:
            if rule[0] == dot_symbol:
                closure_set.append(rule)
    else:
        closure_set = input_state
    prev_len = -1
    while prev_len != len(closure_set):
        prev_len = len(closure_set)
        temp_closure_set = []
        for rule in closure_set:
            index_of_dot = rule[1].index('.')
            if rule[1][-1] != '.':
                dot_points_here = rule[1][index_of_dot + 1]
                for in_rule in separated_rules_list:
                    if dot_points_here == in_rule[0] and in_rule not in temp_closure_set:
                        temp_closure_set.append(in_rule)
        for rule in temp_closure_set:
            if rule not in closure_set:
                closure_set.append(rule)
    return closure_set

def compute_goto(state):
    global states_dict, state_count
    generate_states_for = []
    for rule in states_dict[state]:
        if rule[1][-1] != '.':
            index_of_dot = rule[1].index('.')
            dot_points_here = rule[1][index_of_dot + 1]
            if dot_points_here not in generate_states_for:
                generate_states_for.append(dot_points_here)
    if len(generate_states_for) != 0:
        for symbol in generate_states_for:
            goto(state, symbol)
    return

def goto(state, char_next_to_dot):
    global states_dict, state_count, state_map
    new_state = []
    for rule in states_dict[state]:
        index_of_dot = rule[1].index('.')
        if rule[1][-1] != '.':
            if rule[1][index_of_dot + 1] == char_next_to_dot:
                shifted_rule = copy.deepcopy(rule)
                shifted_rule[1][index_of_dot] = shifted_rule[1][index_of_dot + 1]
                shifted_rule[1][index_of_dot + 1] = '.'
                new_state.append(shifted_rule)
    add_closure_rules = []
    for rule in new_state:
        index_dot = rule[1].index('.')
        if rule[1][-1] != '.':
            closure_res = find_closure(new_state, rule[1][index_dot + 1])
            for rule in closure_res:
                if rule not in add_closure_rules and rule not in new_state:
                    add_closure_rules.append(rule)
    for rule in add_closure_rules:
        new_state.append(rule)
    state_exists = -1
    for state_num in states_dict:
        if states_dict[state_num] == new_state:
            state_exists = state_num
            break
    if state_exists == -1:
        state_count += 1
        states_dict[state_count] = new_state
        state_map[(state, char_next_to_dot)] = state_count
    else:
        state_map[(state, char_next_to_dot)] = state_exists
    return

def generate_states(states_dict):
    prev_len = -1
    called_goto_on = []
    while len(states_dict) != prev_len:
        prev_len = len(states_dict)
        keys = list(states_dict.keys())
        for key in keys:
            if key not in called_goto_on:
                called_goto_on.append(key)
                compute_goto(key)
    return

def compute_first(rule):
    global rules, nonterminals, terminals, rule_dict, first_sets
    if len(rule) != 0 and rule is not None:
        if rule[0] in terminals:
            return rule[0]
        elif rule[0] == '#':
            return '#'
    if len(rule) != 0:
        if rule[0] in list(rule_dict.keys()):
            fres = []
            rhs_rules = rule_dict[rule[0]]
            for itr in rhs_rules:
                indiv_res = compute_first(itr)
                if type(indiv_res) is list:
                    for i in indiv_res:
                        fres.append(i)
                else:
                    fres.append(indiv_res)
            if '#' not in fres:
                return fres
            else:
                fres.remove('#')
                if len(rule) > 1:
                    ans_new = compute_first(rule[1:])
                    if ans_new is not None:
                        if type(ans_new) is list:
                            return fres + ans_new
                        else:
                            return fres + [ans_new]
                fres.append('#')
                return fres

def compute_follow(nt):
    global start_symbol, rules, nonterminals, terminals, rule_dict, first_sets, follow_sets
    sol_set = set()
    if nt == start_symbol:
        sol_set.add('$')
    for cur_nt in rule_dict:
        rhs = rule_dict[cur_nt]
        for subrule in rhs:
            if nt in subrule:
                while nt in subrule:
                    index_nt = subrule.index(nt)
                    subrule = subrule[index_nt + 1:]
                    if len(subrule) != 0:
                        res = compute_first(subrule)
                        if '#' in res:
                            res.remove('#')
                            ans_new = compute_follow(cur_nt)
                            if ans_new is not None:
                                if type(ans_new) is list:
                                    res += ans_new
                                else:
                                    res += [ans_new]
                            else:
                                pass
                    else:
                        if nt != cur_nt:
                            res = compute_follow(cur_nt)
                    if res is not None:
                        if type(res) is list:
                            for g in res:
                                sol_set.add(g)
                        else:
                            sol_set.add(res)
    return list(sol_set)

def create_parse_table(states_dict, state_map, T, NT):
    rows = list(states_dict.keys())
    cols = T + ['$'] + NT
    table = []
    temp_row = []
    for y in range(len(cols)):
        temp_row.append('')
    for x in range(len(rows)):
        table.append(copy.deepcopy(temp_row))
    for entry in state_map:
        state = entry[0]
        symbol = entry[1]
        a = rows.index(state)
        b = cols.index(symbol)
        if symbol in NT:
            table[a][b] += f"{state_map[entry]} "
        elif symbol in T:
            table[a][b] += f"S{state_map[entry]} "
    numbered = {}
    key_count = 0
    for rule in separated_rules_list:
        temp_rule = copy.deepcopy(rule)
        temp_rule[1].remove('.')
        numbered[key_count] = temp_rule
        key_count += 1
    added_rule = f"{separated_rules_list[0][0]} -> {separated_rules_list[0][1][1]}"
    rules.insert(0, added_rule)
    for rule in rules:
        k = rule.split("->")
        k[0] = k[0].strip()
        k[1] = k[1].strip()
        rhs = k[1]
        multirhs = rhs.split('|')
        for i in range(len(multirhs)):
            multirhs[i] = multirhs[i].strip()
            multirhs[i] = multirhs[i].split()
        rule_dict[k[0]] = multirhs
    for stateno in states_dict:
        for rule in states_dict[stateno]:
            if rule[1][-1] == '.':
                temp2 = copy.deepcopy(rule)
                temp2[1].remove('.')
                for key in numbered:
                    if numbered[key] == temp2:
                        follow_result = compute_follow(rule[0])
                        for col in follow_result:
                            index = cols.index(col)
                            if key == 0:
                                table[stateno][index] = "Accept"
                            else:
                                table[stateno][index] += f"R{key} "
    print("\nSLR(1) parsing table:\n")
    frmt = "{:>8}" * len(cols)
    print(" ", frmt.format(*cols), "\n")
    ptr = 0
    j = 0
    for y in table:
        frmt1 = "{:>8}" * len(y)
        print(f"{{:>3}} {frmt1.format(*y)}".format('I' + str(j)))
        j += 1

def print_result(rules):
    for rule in rules:
        print(f"{rule[0]} -> {' '.join(rule[1])}")

def print_all_goto(diction):
    for itr in diction:
        print(f"GOTO ( I{itr[0]} , {itr[1]} ) = I{state_map[itr]}")

rules = ["E -> E + T | T",
         "T -> T * F | F",
         "F -> ( E ) | id"
         ]
nonterminals = ['E', 'T', 'F']
terminals = ['id', '+', '*', '(', ')']
start_symbol = nonterminals[0]

separated_rules_list = augment_grammar(rules, nonterminals, start_symbol)
print("\nGrammar after Augmentation: \n")
print_result(separated_rules_list)

start_symbol = separated_rules_list[0][0]
I0 = find_closure(0, start_symbol)

states_dict = {}
state_map = {}

states_dict[0] = I0
state_count = 0

generate_states(states_dict)

print("\nStates Generated: \n")
for st in states_dict:
    print(f"State = I{st}")
    print_result(states_dict[st])
    print()

print("Result of GOTO computation:\n")
print_all_goto(state_map)

rule_dict = {}

create_parse_table(states_dict, state_map, terminals, nonterminals)
