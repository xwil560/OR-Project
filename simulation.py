from solve_lp import route_modifier

def change_demand(demands, time_1, time_2):
    unsatisfied_nodes1 = []
    unsatisfied_nodes2 = []
    N1 = 30 - len(time_1)
    N2 = 30 - len(time_2)
    for route in time_1:
        while calc_demand(demands, route) > 26:
            unsatisfied_nodes1.append(route.pop(-1))

    for route in time_2:
        while calc_demand(demands, route) > 26:
            unsatisfied_nodes2.append(route.pop(-1))
    
    return unsatisfied_nodes1, unsatisfied_nodes2, N1, N2


def calc_demand(demand, route):
    return sum([demand[r] for r in route])


def simulation(Nruns = 100)