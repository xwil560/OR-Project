from solve_lp import route_modifier

def change_demand(demands, time_1, time_2):
    unsatisfied_nodes = []
    new_routes1 = []
    new_routes2 = []
    N1 = 30 - len(time_1)
    N2 = 30 - len(time_2)
    for route in time_1:
        while calc_demand(demands, route) > 26:
            unsatisfied_nodes.append(route.pop(-1))
            new_routes1.append(route)
    for route in time_2:
        while calc_demand(demands, route) > 26:
            unsatisfied_nodes.append(route.pop(-1))
            new_routes2.append(route)
    
    return new_routes1, new_routes2, unsatisfied_nodes, N1, N2


def calc_demand(demand, route):
    return sum([demand[r] for r in route])


def simulation(Nruns = 100, time_1,time_2):
    
    for i in range(Nruns):
        new_routes1, new_routes2, unsatisfied_nodes, N1, N2 = 