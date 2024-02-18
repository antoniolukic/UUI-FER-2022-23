import math
import sys


class Node:
    name = None
    value = None
    subtrees = None

    def __init__(self, name, value, subtrees):
        self.name = name
        self.value = value
        self.subtrees = subtrees


class ID3:

    root = None

    def __init__(self, depth=None):
        self.depth = depth

    def most_common_label(self, y):
        count = {}
        max_count = 0
        most_common_label = None

        for i in y:
            if i in count:
                count[i] += 1
            else:
                count[i] = 1

            if (count[i] > max_count) or (count[i] == max_count and i < most_common_label):  # abecedni poredak
                max_count = count[i]
                most_common_label = i

        return most_common_label

    def last_column(self, D):
        last_column = []
        for i in D:
            last_column.append(i[-1])
        return last_column

    def same_labels(self, y):
        flag = None
        for i in y:
            if flag is None:
                flag = i
            elif flag != i:
                return False
        return True

    def set_V(self, D, X):  # za koje značajke koje vrijednosti postoje
        self.V = {}
        for i in range(len(X) - 1):  # ne postavljamo labele
            v = {}
            for j in D:
                v[j[i]] = 1
            self.V[X[i]] = v

    def IG(self, D, x):
        total = len(D)
        labels = {}
        for i in range(len(D)):  # pobroji grananja
            labels[D[i][x]] = 1

        inf_gain = 0
        partition = {}
        for i in D:
            if i[-1] not in partition:  # početni E
                partition[i[-1]] = 1
            else:
                partition[i[-1]] += 1
        for i in partition:
            inf_gain -= partition[i] / total * math.log2(partition[i] / total)

        for i in labels:  # po granama
            partition = {}
            partition_len = 0
            for j in D:  # po primjerima
                if j[x] == i:
                    partition_len += 1
                    if j[-1] not in partition:
                        partition[j[-1]] = 1
                    else:
                        partition[j[-1]] += 1
            entropy = 0
            for j in partition:
                entropy -= partition[j] / partition_len * math.log2(partition[j] / partition_len)
            inf_gain -= partition_len / total * entropy
        return inf_gain

    def recursion(self, D, D_parent, X, depth):
        if len(D) <= 0:  # prazan trenutni skup
            v = self.most_common_label(self.last_column(D_parent))
            return Node("Leaf", v, None)

        if depth is not None and depth <= 0:  # ako smo došli do ograničene dubine
            v = self.most_common_label(self.last_column(D))
            return Node("Leaf", v, None)

        v = self.most_common_label(self.last_column(D))
        if len(X) <= 0 or self.same_labels(self.last_column(D)):  # X nema više ništa ili su svi isti
            return Node("Leaf", v, None)

        max_x = -1
        label_x = None

        for i in range(len(X)):
            x = self.IG(D, i)
            if label_x is None or x > max_x or (x == max_x and X[i] < label_x):  # prvi ili bolji ili jednak pa abecedno bolji
                max_x = x
                label_x = X[i]

        subtrees = []
        for i in self.V[label_x]:  # po svim prijelazima
            where = X.index(label_x)
            sub_D = []
            for j in D:
                if j[where] == i:
                    temp = []
                    for k in range(len(X)):
                        if k != where: # briši stupac
                            temp.append(j[k])
                    temp.append(j[-1])  # dodaj labelu
                    sub_D.append(temp)

            sub_X = X.copy()
            sub_X.remove(label_x)
            if depth is None:
                t = self.recursion(sub_D, D, sub_X, depth)
            else:
                t = self.recursion(sub_D, D, sub_X, depth - 1)
            subtrees.append([i, t])

        return Node(label_x, None, subtrees)

    def fit(self, D):
        self.data = D[1:]
        self.set_V(D[1:], D[0])
        self.root = self.recursion(D[1:], D[1:], D[0][:-1], self.depth)
        self.print_tree([None, self.root], 1, "")

    def print_tree(self, pair, depth, output):
        if pair[0] is None and pair[1].value is None:  # root čvor
            print("[BRANCHES]:")
            output += "1:" + pair[1].name + "="
            for i in pair[1].subtrees:
                self.print_tree(i, depth + 1, output)
        elif pair[1].value is None:  # podstablo je
            output += pair[0] + " " + str(depth) + ":" + pair[1].name + "="
            for i in pair[1].subtrees:
                self.print_tree(i, depth + 1, output)
        elif pair[1].subtrees is None:  # list je
            if pair[0] is not None:
                output += pair[0] + " " + pair[1].value
            else:
                output += "[BRANCHES]:\n" + pair[1].value
            print(output)

    def predict(self, D):
        X = D[0][:-1]
        D = D[1:]
        labels = []
        for i in D:
            current = self.root
            current_data = self.data
            for j in range(len(X) + 1):
                if current.subtrees is None:  # došli smo do lista
                    labels.append(current.value)
                    break
                elif current.value is None:
                    exists = False
                    where = X.index(current.name)
                    for k in current.subtrees:
                        if k[0] == i[where]:  # postoji prijelaz kojim možemo ići
                            current = k[1]
                            temp = []
                            for l in current_data:  # suzi podatke
                                if l[where] == k[0]:
                                    temp.append(l)
                            current_data = temp
                            exists = True
                            break

                    if not exists:  # ako je neviđena vrijednost značajke vraćamo najčešću vrijednost
                        # ciljne varijable u podskupu podataka za treniranje u tom čvoru
                        labels.append(self.most_common_label(self.last_column(current_data)))
                        break

        self.print_predict(labels)
        return labels

    def print_predict(self, predictions):
        s = "[PREDICTIONS]:"
        for i in predictions:
            s += " " + i
        print(s)

    def accuracy(self, predictions, D):
        confusion_matrix = {}
        D = D[1:]  # ne trebaju nam imena zančajki
        true_values = self.last_column(D)
        correct = 0

        values = []
        for i in true_values:  # pobroji kojih labela ima
            if i not in values:
                values.append(i)
        for i in predictions:
            if i not in values:
                values.append(i)
        for i in values:
            for j in values:
                confusion_matrix[str(i) + "," + str(j)] = 0
        for i in range(len(predictions)):
            if predictions[i] == true_values[i]:
                correct += 1
            confusion_matrix[str(true_values[i]) + "," + str(predictions[i])] += 1

        print("[ACCURACY]: " + str("{:.5f}".format(correct / len(predictions))))
        print("[CONFUSION_MATRIX]:")
        keys = sorted(list(confusion_matrix.keys()))  # abecedni ispis
        row = int(math.sqrt(len(keys)))
        for i in range(row):
            output = ""
            for j in range(row):
                output += str(confusion_matrix[keys[i * row + j]]) + " "
            print(output)

def read_files():
    train_dataset = sys.argv[1]
    test_dataset = sys.argv[2]
    f = open(train_dataset, "r")
    text_train = f.readlines()
    f.close()
    f = open(test_dataset, "r")
    text_test = f.readlines()
    f.close()
    train_dataset, test_dataset = [], []
    for i in text_train:
        train_dataset.append(i[:-1].split(','))
    for i in text_test:
        test_dataset.append(i[:-1].split(','))
    return train_dataset, test_dataset


train, test = read_files()
if len(sys.argv) != 4:
    model = ID3()
else:
    model = ID3(int(sys.argv[3]))

model.fit(train)
predictions = model.predict(test)
model.accuracy(predictions, test)
