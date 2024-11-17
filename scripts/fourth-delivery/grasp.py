import time
from itertools import product

import pandas as pd
from tqdm import tqdm

from heuristics_ccvrptw.constants import CASES_PER_TYPE
from heuristics_ccvrptw.construction_algorithms import (
    stochastic_neighbors_heuristic,
)
from heuristics_ccvrptw.intensification_algorithms import (
    local_search_2opt_intensification,
)
from heuristics_ccvrptw.parse_instances import parse_instance
from heuristics_ccvrptw.plotter import plot_routes
from heuristics_ccvrptw.repair_method import apply_repair_method
from heuristics_ccvrptw.utils import (
    calculate_cost_function,
    calculate_times_matrix,
    check_routes_are_feasible,
)


def get_multiple_solution_and_intensify(
    kind,
    kind_type,
    case_number,
    number_of_solutions,
    ref_vehicle_nr=-1,
    plot_instance=False,
):
    data = parse_instance(kind, kind_type, case_number)
    _, vehicle_nr, capacity, all_points = data

    if ref_vehicle_nr == -1:
        ref_vehicle_nr = vehicle_nr  # use the original vehicle number

    customers = all_points.iloc[1:]

    all_times = calculate_times_matrix(all_points)
    init_time = time.time()

    costs = []
    vehicle_nr_obtaineds = []
    solutions = []
    t_k_is = []
    seed = 0
    while len(costs) < number_of_solutions:
        routes, t_k_i = stochastic_neighbors_heuristic(
            all_times, customers, capacity, seed
        )

        assert check_routes_are_feasible(routes, t_k_i, customers, capacity)

        if len(routes) > ref_vehicle_nr:
            # print("Applying repair method")
            repaired_routes, t_k_i = apply_repair_method(
                routes,
                ref_vehicle_nr,
                all_times,
                customers,
                capacity,
            )
            assert check_routes_are_feasible(
                repaired_routes, t_k_i, customers, capacity
            )
        else:
            repaired_routes = routes

        if (
            repaired_routes in solutions
        ):  # TODO: there's a chance here that the routes are the same but ordered differently, and then this would say the solution does not exist in the list
            continue  # in case the solution gets repeated, if the repair method throws it back to the same point
        else:
            solutions.append(repaired_routes)
            t_k_is.append(t_k_i)
            cost = calculate_cost_function(t_k_i)
            # print("Cost:", cost)
            # print("Number of routes:", len(repaired_routes), "Vehicle number:", vehicle_nr)
            if plot_instance:
                plot_routes(repaired_routes, all_points)

            costs.append(cost)
            vehicle_nr_obtaineds.append(len(repaired_routes))
        seed += 1

    # apply intensification
    best_local_routess = []
    best_local_t_k_is = []
    best_local_costs = []
    for repaired_routes, t_k_i in zip(solutions, t_k_is):
        best_local_routes, best_local_t_k_i, best_local_cost = (
            local_search_2opt_intensification(
                repaired_routes, t_k_i, cost, all_times, customers, capacity
            )
        )
        best_local_routess.append(best_local_routes)
        best_local_t_k_is.append(best_local_t_k_i)
        best_local_costs.append(best_local_cost)

    # get best local cost and route
    best_local_cost = min(best_local_costs)
    best_local_routes = best_local_routess[best_local_costs.index(best_local_cost)]

    end_time = time.time()

    # TODO: Consider applying repair method here to potentially reduce the number of vehicles further

    # print("Cost:", best_local_cost)
    # print("Number of routes:", len(best_local_routes), "Vehicle number:", vehicle_nr)

    return best_local_cost, len(best_local_routes), vehicle_nr, end_time - init_time


def main():
    reference_data = pd.read_csv("reference_data/instances.csv")
    kinds = ["c", "r", "rc"]
    kind_types = ["1", "2"]
    number_of_solutions = 5

    cases = product(
        kinds,
        kind_types,
        range(1, max(CASES_PER_TYPE[k][t] for k in kinds for t in kind_types) + 1),
    )
    instance_names = []
    costs = []
    vehicle_nr_obtaineds = []
    vehicle_nr_originals = []
    times = []
    for kind, kind_type, case_number in tqdm(cases, desc="Running instances"):
        if case_number > CASES_PER_TYPE[kind][kind_type]:
            continue
        instance_name = f"{kind.upper()}{kind_type}{case_number:02d}"
        ref_vehicle_nr = reference_data.loc[
            reference_data["Instance"] == instance_name, "k"
        ].values[0]
        cost, vehicle_nr_obtained, original_vehicle_nr, time = (
            get_multiple_solution_and_intensify(
                kind,
                kind_type,
                case_number,
                number_of_solutions,
                ref_vehicle_nr=ref_vehicle_nr,
                plot_instance=False,
            )
        )
        instance_names.append(instance_name)
        costs.append(cost)
        vehicle_nr_obtaineds.append(vehicle_nr_obtained)
        vehicle_nr_originals.append(original_vehicle_nr)
        times.append(time)

    # create dataframe with results
    results = pd.DataFrame(
        {
            "Instance": instance_names,
            "local_optimum_solution_cost": costs,
            "vehicle_number_obtained": vehicle_nr_obtaineds,
            "vehicle_number_original": vehicle_nr_originals,
            "time": times,
        }
    )
    results.to_csv("results/fourth-delivery/grasp.csv", index=False)


if __name__ == "__main__":
    main()
