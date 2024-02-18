import sys
import csv
import numpy as np


def get_data(path):
    x, y = [], []
    with open(path, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            x.append(np.array([float(value) for value in row[:-1]]))
            y.append(np.array([float(row[-1])]))
    x = np.array(x)
    y = np.array(y)
    return x, y


def parse_layers(input_l):
    output = []
    layers = input_l.split('s')
    for layer in layers:
        if len(layer) > 0:
            output.append(int(layer))
    return output


class Nnetwork:

    def __init__(self, layers, weights=None, b=None):
        self.layers = layers
        if weights is None:
            self.init_weights()
        else:
            self.weights = weights
            self.b = b

    def __lt__(self, other):
        return True

    def weight_array(self, mean, dev, size):
        return np.random.normal(mean, dev, size=size)

    def init_weights(self):
        dev = 0.01

        self.weights = []
        self.b = []

        for i in range(1, len(self.layers)):
            self.weights.append(self.weight_array(0, dev, [self.layers[i], self.layers[i - 1]]))
            self.b.append(self.weight_array(0, dev, self.layers[i]))

    def feed_forward(self, x):

        h = x
        for i in range(len(self.layers) - 1):
            net = self.weights[i].dot(h) + self.b[i]
            if not (i + 1 == len(self.layers) - 1):
                out = 1.0 / (1.0 + np.exp(-net))
            else:
                out = net
            h = out

        return h


class GenAlg:
    population = []

    def __init__(self, layers, pop_size, elitism, p, K, iter):
        self.elitism = elitism
        self.p = p
        self.K = K
        self.iter = iter

        for i in range(pop_size):
            self.population.append(Nnetwork(layers))

    def cross(self, nnetwork1, nnetwork2):
        weights, b = [], []
        for i in range(len(nnetwork1.weights)):
            weights.append((nnetwork1.weights[i] + nnetwork2.weights[i]) / 2)
            b.append((nnetwork1.b[i] + nnetwork2.b[i]) / 2)
        return Nnetwork(nnetwork1.layers, weights, b)

    def mutate(self, nnetwork, deviation, p):
        for i in range(len(nnetwork.weights)):
            shape = (len(nnetwork.weights[i]), len(nnetwork.weights[i][0]))
            mutation_w = np.random.choice([0, np.random.normal(0, deviation)],
                                          size=shape,
                                          p=[1 - p, p])
            nnetwork.weights[i] += mutation_w

        for i in range(len(nnetwork.b)):
            shape = (len(nnetwork.b[i]))
            mutation_b = np.random.choice([0, np.random.normal(0, deviation)],
                                          size=shape,
                                          p=[1 - p, p])
            nnetwork.b[i] += mutation_b

        return nnetwork

    def fit(self, train_x, train_y):
        epoch = 0

        while epoch < self.iter + 1:
            all_errors = []
            for i in range(len(self.population)):
                error = 0
                for j in range(len(train_x)):
                    error += np.sum(np.square(self.population[i].feed_forward(train_x[j]) - train_y[j]))
                error /= len(train_x)
                all_errors.append(error)

            goodness = 1 / np.array(all_errors)

            population_sorted = sorted(zip(goodness, self.population), reverse=True)  # sortiramo populaciju prema E
            goodness = [pair[0] for pair in population_sorted]
            self.population = [pair[1] for pair in population_sorted]

            if epoch % 2000 == 0 and epoch != 0:
                print("[Train error @" + str(epoch) + "]: " + str("{:.6f}".format(1 / goodness[0])))

            new_population = []
            for i in range(self.elitism):  # dodaj n najboljih
                new_population.append(self.population[i])

            for i in range(len(self.population) - self.elitism):  # generiraj novu populaciju
                parents = np.random.choice(self.population, size=2, replace=False, p=goodness / np.sum(goodness))
                crossed = self.cross(parents[0], parents[1])  # križaj
                mutated = self.mutate(crossed, self.K, self.p)  # mutiraj
                new_population.append(mutated)

            self.population = new_population

            epoch += 1

    def predict(self, test_x, test_y):
        best_value = None
        for i in range(len(self.population)):
            error = 0
            for j in range(len(test_x)):
                error += np.sum(np.square(self.population[i].feed_forward(test_x[j]) - test_y[j]))
            error /= len(test_x)
            if best_value is None or best_value > error:
                best_value = error
        return best_value

paramethers = {}
for i in range(1, len(sys.argv), 2):
    paramethers[sys.argv[i]] = sys.argv[i + 1]

train_x, train_y = get_data(paramethers["--train"])
test_x, test_y = get_data(paramethers["--test"])

layers = parse_layers(str(len(train_x[0])) + "s" + paramethers["--nn"] + "1s")
pop_size = int(paramethers["--popsize"])
elitism = int(paramethers["--elitism"])
p = float(paramethers["--p"])
K = float(paramethers["--K"])
iter = int(paramethers["--iter"])
model = GenAlg(layers, pop_size, elitism, p, K, iter)
model.fit(train_x, train_y)
value = model.predict(test_x, test_y)
print("[Test error]: " + str("{:.6f}".format(value)))
