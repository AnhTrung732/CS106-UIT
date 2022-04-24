from ortools.algorithms import pywrapknapsack_solver
from test import *
import csv  
import time
import random
from visual import *

def solve(name):
    print(name)
    test = Test(name)
    number,capacities, values, weights  = test.process()
    print(values)
    limit_time = 10

    solver = pywrapknapsack_solver.KnapsackSolver(
        pywrapknapsack_solver.KnapsackSolver.
        KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER, 'KnapsackExample')

    solver.Init(values, weights, capacities)
    solver.set_time_limit(limit_time)
    start_time = time.perf_counter()


    computed_value = solver.Solve()
    end_time = time.perf_counter()

    solution_time = round(end_time - start_time, 5)
    print(solution_time)
    check_optimal = (solution_time < limit_time -1)

    packed_items = []
    packed_weights = []
    packed_values = []
    total_weight = 0
    print('Total value =', computed_value)
    for i in range(len(values)):
        if solver.BestSolutionContains(i):
            packed_items.append(i)
            packed_weights.append(weights[0][i])
            packed_values.append(values[i])
            total_weight += weights[0][i]
    #print('Total weight:', total_weight)
    #print('Packed items:', packed_items)
    #print('Packed_weights:', packed_weights)
    return (computed_value,total_weight,check_optimal,solution_time,packed_weights,packed_values)

def main():
    header = ['name', 'Total_value', 'Total_weight', 'is_optimal','solution_time'] 
    save_dir = "visual/output/"   
    with open('knapsack.csv', 'a', encoding='UTF8') as f:
        writer = csv.writer(f)
        if os.fstat(f.fileno()).st_size == 0:
            writer.writerow(header)
        for i in range (0,13):
            for j in [50,100,200,500,1000,2000,5000,10000] :
                for k in [0,1] :
                    for l in  random.sample(range(1, 100), 1):
                        name = str(i) + '-' + str(j) + '-' + str(k) + '-' + str(l)
                        total_value, total_weight,check_optimal,solution_time,packed_weights,packed_values = solve(name)
                        print(check_optimal,solution_time)
                        if check_optimal is True :
                            visual(save_dir,name=name,value=packed_values,weight=packed_weights)
                        data = [name,total_value,total_weight,check_optimal,solution_time]
                        writer.writerow(data)

        

if __name__ == '__main__':
    main()