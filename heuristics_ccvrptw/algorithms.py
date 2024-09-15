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


def apply_repair_method(routes, vehicle_nr, all_times, customers, capacity):
    # Apply repair method
    repaired_routes = routes.copy()
    reparation_feasible = True
    non_repairable_routes = []
    while len(repaired_routes) > vehicle_nr:
        # print("----- -----: Current number of routes:", len(repaired_routes))
        # get smallest route that is not among the non-repairable ones
        reparable_routes = [
            route for route in repaired_routes if route not in non_repairable_routes
        ]

        if len(reparable_routes) == 0:
            reparation_feasible = False
            # print("No more reparable routes")
            break
        else:
            min_route = min(
                reparable_routes,
                key=lambda x: len(x),
            )
            # print("Reallocating route:", min_route)
            before_repairing = repaired_routes.copy()
            for stop in min_route[1:-1]:
                reallocation_feasible = False
                # print("Reassigning stop:", stop)
                # Find closest stops to that one
                stops_not_in_route = [
                    stop for stop in customers.index if stop not in min_route
                ]
                times_from_stop = all_times.loc[stops_not_in_route, stop].sort_values(
                    ascending=True
                )
                for proposed_closest in times_from_stop.index:
                    # Find that stop in the routes
                    proposed_closest_route = [
                        route for route in repaired_routes if proposed_closest in route
                    ][0]
                    proposed_closest_idx = proposed_closest_route.index(
                        proposed_closest
                    )
                    # Check if it is feasible to add that stop to the route
                    new_proposed_route = proposed_closest_route.copy()
                    new_proposed_route.insert(proposed_closest_idx, stop)
                    # print('Trying route:', new_proposed_route)
                    new_service_start_times = service_start_times_from_route(
                        new_proposed_route, all_times, customers
                    )
                    feasible = check_route_is_feasible(
                        new_proposed_route, new_service_start_times, customers, capacity
                    )
                    if feasible:
                        # Update the route
                        # print("Done, old route: ", proposed_closest_route)
                        # print("New route: ", new_proposed_route)
                        repaired_routes.remove(proposed_closest_route)
                        repaired_routes.append(new_proposed_route)
                        reallocation_feasible = True
                        break
                    else:
                        new_proposed_route = proposed_closest_route.copy()
                        new_proposed_route.insert(proposed_closest_idx + 1, stop)
                        # print('Trying route:', new_proposed_route)
                        new_service_start_times = service_start_times_from_route(
                            new_proposed_route, all_times, customers
                        )
                        feasible = check_route_is_feasible(
                            new_proposed_route,
                            new_service_start_times,
                            customers,
                            capacity,
                        )
                        if feasible:
                            # Update the route
                            # print("Done, old route: ", proposed_closest_route)
                            # print("New route: ", new_proposed_route)
                            repaired_routes.remove(proposed_closest_route)
                            repaired_routes.append(new_proposed_route)
                            reallocation_feasible = True
                            break
                if not reallocation_feasible:
                    print(
                        # "Could not reallocate stop ", stop, "route cannot be repaired"
                    )
                    break

            if not reallocation_feasible:
                non_repairable_routes.append(min_route)
                repaired_routes = before_repairing.copy()  # undo the changes
                # print("Route could not be repaired:", min_route)
            else:
                # print("Reallocated route:", min_route)
                repaired_routes.remove(min_route)

    # print(
    #     "Reparation done successfully"
    #     if reparation_feasible
    #     else "Reparation not feasible, number of routes:",
    #     len(repaired_routes),
    # )

    return repaired_routes, t_k_i_from_routes(repaired_routes, all_times, customers)
