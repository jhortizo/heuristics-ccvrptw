from itertools import product

import pandas as pd
from tqdm import tqdm
import time

from heuristics_ccvrptw.algorithms import (
    apply_repair_method,
    stochastic_neighbors_heuristic,
)
from heuristics_ccvrptw.constants import CASES_PER_TYPE
from heuristics_ccvrptw.parse_instances import parse_instance
from heuristics_ccvrptw.plotter import plot_routes
from heuristics_ccvrptw.utils import (
    calculate_cost_function,
    calculate_times_matrix,
    check_routes_are_feasible,
)


def get_multiple_solutions(
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

    costs = []
    vehicle_nr_obtaineds = []
    solutions = []
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

        if repaired_routes in solutions: # TODO: there's a chance here that the routes are the same but ordered differently, and then this would say the solution does not exist in the list
            continue  # in case the solution gets repeated, if the repair method throws it back to the same point
        else:
            solutions.append(repaired_routes)
            cost = calculate_cost_function(t_k_i)
            # print("Cost:", cost)
            # print("Number of routes:", len(repaired_routes), "Vehicle number:", vehicle_nr)
            if plot_instance:
                plot_routes(repaired_routes, all_points)

            costs.append(cost)
            vehicle_nr_obtaineds.append(len(repaired_routes))
        seed += 1

    return costs, vehicle_nr_obtaineds, vehicle_nr


def main():
    reference_data = pd.read_csv("reference_data/instances.csv")
    kinds = ["c", "r", "rc"]
    kind_types = ["1", "2"]
    number_of_solutions = 10

    cases = product(
        kinds,
        kind_types,
        range(1, max(CASES_PER_TYPE[k][t] for k in kinds for t in kind_types) + 1),
    )
    instance_names = []
    avg_costs = []
    min_costs = []
    avg_vehicle_nr_obtaineds = []
    min_vehicle_nr_obtaineds = []
    vehicle_nr_originals = []
    times = []
    for kind, kind_type, case_number in tqdm(cases, desc="Running instances"):
        if case_number > CASES_PER_TYPE[kind][kind_type]:
            continue
        instance_name = f"{kind.upper()}{kind_type}{case_number:02d}"
        ref_vehicle_nr = reference_data.loc[
            reference_data["Instance"] == instance_name, "k"
        ].values[0]
        init_time = time.time()
        costs, vehicle_nr_obtaineds, original_vehicle_nr = get_multiple_solutions(
            kind,
            kind_type,
            case_number,
            number_of_solutions,
            ref_vehicle_nr=ref_vehicle_nr,
            plot_instance=False,
        )
        end_time = time.time()
        instance_names.append(instance_name)
        avg_costs.append(sum(costs) / len(costs))
        min_costs.append(min(costs))
        avg_vehicle_nr_obtaineds.append(
            sum(vehicle_nr_obtaineds) / len(vehicle_nr_obtaineds)
        )
        min_vehicle_nr_obtaineds.append(min(vehicle_nr_obtaineds))
        vehicle_nr_originals.append(original_vehicle_nr)
        times.append((end_time - init_time) / number_of_solutions)

    # create dataframe with results
    results = pd.DataFrame(
        {
            "Instance": instance_names,
            "average_cost": avg_costs,
            "minimum_cost": min_costs,
            "average_vehicle_number_obtained": avg_vehicle_nr_obtaineds,
            "minimum_vehicle_number_obtained": min_vehicle_nr_obtaineds,
            "vehicle_number_original": vehicle_nr_originals,
            "time": times,
        }
    )
    results.to_csv(f"results/multiple_solutions_{number_of_solutions}.csv", index=False)


if __name__ == "__main__":
    main()
