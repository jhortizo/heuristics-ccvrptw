# Heuristic Methods for CCVRPTW
Solving the Cumulative Capacitated Vehicle Routing Problem with Time Window (CCVRPTW), as the course project for Heuristic Methods of Optimization. Master in Applied Mathematics - 2024-2. Universidad EAFIT.

## Remarks

I am using [poetry](https://python-poetry.org/) for virtual environment dependencies management. Feel free to use it or directly install the requirements from the `pyproject.toml`. You could use a default environment with common libraries installed, it should work without problem.

The scripts in the `scripts` folders contain the code to run, separated by different stages of the project (deliveries for the course), and the results get saved in `results` folder (also included in the repository). The folder `heuristic_ccvrptw` contains modules with utility functions.

The data within `reference_data` is retrieved from [1], which is the main reference for this paper. The codes here are based on the studies presented there.

This repository also uses the data from the well-known Solomon instances for the VRP problem [2]. They are accesed from [CervEdin/solomon-vrptw-benchmarks](https://github.com/CervEdin/solomon-vrptw-benchmarks/tree/main) repository programmatically, so the code downloads them automatically if required.

### What about the `first-delivery` folder?

The first delivery for the course project is a Literature Review, so it's not available here. I chose to respect that numueration, so there is no `first-delivery` here.

## References

[1] N. A. Kyriakakis, I. Sevastopoulos, M. Marinaki, and Y. Marinakis, “A hybrid Tabu search – Variable neighborhood descent algorithm for the cumulative capacitated vehicle routing problem with time windows in humanitarian applications,” Computers & Industrial Engineering, vol. 164, p. 107868, Feb. 2022, doi: 10.1016/j.cie.2021.107868.

[2] M. M. Solomon, “Algorithms for the Vehicle Routing and Scheduling Problems with Time Window Constraints,” Operations Research, vol. 35, no. 2, pp. 254–265, Apr. 1987, doi: 10.1287/opre.35.2.254.


