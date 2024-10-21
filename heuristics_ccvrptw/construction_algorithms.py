import numpy as np

from heuristics_ccvrptw.utils import (
    check_route_is_feasible,
    service_start_times_from_route,
    t_k_i_from_routes,
)


def nearest_neighbors_heuristic(all_times, customers, capacity):
    routes = []
    t_k_i = []
    pending_customers = customers.copy()

    while len(pending_customers) > 0:
        # print("-- Doing route: ", len(routes) + 1)
        new_route = [0]
        service_start_times = []
        current_time = 0
        current_capacity = 0
        can_add_new_point = True
        while can_add_new_point and (len(pending_customers) > 0):
            times_from_prev = all_times.loc[
                pending_customers.index, new_route[-1]
            ].sort_values(ascending=True)
            for idx in times_from_prev.index:
                this_time = times_from_prev[idx]
                this_customer = customers.loc[idx]
                if (
                    (this_customer["latest"] > current_time + this_time)
                    and (current_capacity + this_customer["demand"] < capacity)
                ):  # if it arrives on time to that place and has enough capacity to supply
                    new_route.append(idx)
                    pending_customers.drop(index=idx, inplace=True)
                    # print("Remaining customers to visit:", len(pending_customers))

                    if current_time + this_time < this_customer["earliest"]:
                        current_time = this_customer[
                            "earliest"
                        ]  # if it arrives earlier than start of the window, needs to wait until it opens
                    else:
                        current_time += (
                            this_time  # else, it just rides and starts the service
                        )

                    service_start_times.append(current_time)
                    current_time += +this_customer["cost"]  # add the service time
                    current_capacity += this_customer["demand"]

                    can_add_new_point = (
                        len(pending_customers) > 0
                    )  # we managed to add a point, so we can move on to the next test only if there are any other points to add
                    break
                else:
                    can_add_new_point = (
                        False  # didn't add a point in any case, we go back to depot
                    )

        new_route.append(0)
        routes.append(new_route)
        t_k_i.append(service_start_times)

    return routes, t_k_i


def stochastic_neighbors_heuristic(all_times, customers, capacity, seed):
    routes = []
    t_k_i = []
    pending_customers = customers.copy()

    rng = np.random.default_rng(seed)

    while len(pending_customers) > 0:
        # print("-- Doing route: ", len(routes) + 1)
        new_route = [0]
        service_start_times = []
        current_time = 0
        current_capacity = 0
        can_add_new_point = True
        while can_add_new_point and (len(pending_customers) > 0):
            random_order = rng.permutation(
                pending_customers.index
            )  # add randomness by checking the points in a random order
            for idx in random_order:
                this_time = all_times.loc[idx, new_route[-1]]
                this_customer = customers.loc[idx]
                if (
                    (this_customer["latest"] > current_time + this_time)
                    and (current_capacity + this_customer["demand"] < capacity)
                ):  # if it arrives on time to that place and has enough capacity to supply
                    new_route.append(idx)
                    pending_customers.drop(index=idx, inplace=True)
                    # print("Remaining customers to visit:", len(pending_customers))

                    if current_time + this_time < this_customer["earliest"]:
                        current_time = this_customer[
                            "earliest"
                        ]  # if it arrives earlier than start of the window, needs to wait until it opens
                    else:
                        current_time += (
                            this_time  # else, it just rides and starts the service
                        )

                    service_start_times.append(current_time)
                    current_time += +this_customer["cost"]  # add the service time
                    current_capacity += this_customer["demand"]

                    can_add_new_point = (
                        len(pending_customers) > 0
                    )  # we managed to add a point, so we can move on to the next test only if there are any other points to add
                    break
                else:
                    can_add_new_point = (
                        False  # didn't add a point in any case, we go back to depot
                    )

        new_route.append(0)
        routes.append(new_route)
        t_k_i.append(service_start_times)

    return routes, t_k_i
