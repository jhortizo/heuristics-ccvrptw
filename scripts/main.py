from heuristics_ccvrptw.parse_instances import parse_instance

def main():

    # Parse instance
    kind = 'c'
    kind_type = '1'
    case_number = 1
    data = parse_instance(kind, kind_type, case_number)
    instance_name, vehicle_nr, capacity, customers = data



if __name__ == '__main__':
    main()
