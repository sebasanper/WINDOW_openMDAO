__author__ = 'sebasanper'

from numpy.random import random
from numpy import sqrt, array
from copy import deepcopy
from joblib import Parallel, delayed
from openmdao.api import Problem, ScipyOptimizer
# fron openmdao.api imprt pyOptSparseDrivers
from workflow import WorkingGroup
import time

prob = Problem()
# print clock(), "Before defining model"
prob.model = WorkingGroup()
# print clock(), "Before setup"
prob.setup()

# print clock(), "After setup"
def fit(layout):
    prob['indep2.layout'] = layout
    prob.run_model()
    lcoe = prob['lcoe.LCOE']
    if prob['constraint_distance.magnitude_violations'] > 0:
        lcoe += 20.0
    if prob['constraint_boundary.n_constraint_violations'] > 0:
        lcoe += 20.0
    return lcoe

def create():
    k = random()
    l = random()
    return [k * 1120.0, l * 1120.0]
## Inertia weight 0.5+rand/2.0, by: "Inertia weight strategies in particle swarm optimization" by Bansal et al.
def pso():
    try:
        best = open('pso_best_layout2.dat', 'w')
        best_g_fit = open('pso_best_global_fitness2.dat', 'w', 1)

        np = 20 ## Number of particles in swarm
        nt = 9

        if random() < 0.5:
            sign1 = 1.0
        else:
            sign1 = - 1.0
        if random() < 0.5:
            sign2 = 1.0
        else:
            sign2 = - 1.0

        vel = array([[[sign1 * random(), sign2 * random()] for _ in range(nt)] for _ in range(np)])
        best_local = array([[[0.0, 0.0] for _ in range(nt)] for _ in range(np)])
        best_own_fitness = [300.0 for _ in range(np)]
        best_global_fitness = 300.0


        #  Produce starting positions
        particles = array([[create() for _ in range(nt)] for _ in range(np)])

        best_layout = [create() for _ in range(nt)]

        # # Velocity limiting to 10% to start with, for convergence, and then increase speed.
        # k = 0.1
        tol = 100.0
        convergence = 1000.0
        iter = 0
        history = array([[create() for _ in range(nt)] for _ in range(np)])
        while convergence >= tol:
            start_time2 = time.time()
            fitness = [0.0 for x in range(np)]

            for p in range(np):  # Can be parallelised in the future.
                ## Solving Constrained Nonlinear Optimization Problems with Particle Swarm Optimization by Xiaohui Hu and Russell Eberhart. For 1.49445 learning coefficients.
                vel[p] = 0.729 * vel[p] + 1.49618 * random() * (best_local[p] - particles[p]) + 1.49618 * random() * (best_layout - particles[p])
                particles[p] = particles[p] + vel[p]
            # Fitness evaluation skipped if a turbine is out of boundaries. following: BrattonKennedy07 PSO.
            for p in range(np):  # Can be parallelised in the future.
                check = True
                fitness = Parallel(n_jobs=-1)(delayed(fit)(particles[i]) for i in range(np))
                # fitness[p] = fit(particles[p])
                if fitness[p] < best_own_fitness[p]:
                    best_own_fitness[p] = deepcopy(fitness[p])
                    best_local[p] = deepcopy(particles[p])
                if fitness[p] < best_global_fitness:
                    best_global_fitness = deepcopy(fitness[p])
                    best_layout = deepcopy(particles[p])

            if iter % 3 == 0:
                convergence = sum(abs(history - particles).flatten())
                print convergence, iter
                history = deepcopy(particles)

            print("Iteration --- %s seconds ---" % (time.time() - start_time2), iter, best_global_fitness)
            iter += 1
            if iter >= 100:
                print "max number of iterations reached: 100"
                break

        for i in range(nt):
            best.write('{2} {0} {1}\n'.format(best_layout[i][0], best_layout[i][1], i))
        best_g_fit.write('{0}\n'.format(best_global_fitness))
        best.close()
        best_g_fit.close()
    except KeyboardInterrupt:
        for i in range(nt):
            best.write('{2} {0} {1}\n'.format(best_layout[i][0], best_layout[i][1], i))
        best_g_fit.write('{0}\n'.format(best_global_fitness))
        best.close()
        best_g_fit.close()


if __name__ == '__main__':
    pso()
    