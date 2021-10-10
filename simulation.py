


def change_demand(demands, time_1, time_2):
    unsatisfied_nodes = []

    for route in time_1:
        while calc_demand(demands, route) > 26:
            unsatisfied_nodes.append(route.pop(-1))


def calc_demand(demand, route):
    return sum([demand[r] for r in route])