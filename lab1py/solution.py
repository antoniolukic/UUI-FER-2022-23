import sys
import queue


# svaki čvor treba pamtiti dubinu, cijenu, prethodnika, te svoju heuristiku ako ju ima
class Node:
    name = ""
    depth = -1
    price = -1
    reference = ""
    heuristic = None

    def __init__(self, name, depth, price, reference, heuristic):
        self.name = name
        self.depth = depth
        self.price = price
        self.reference = reference
        self.heuristic = heuristic

    def __lt__(self, obj):  # pisanje komporatora kako bi se klasa Node mogla koristiti u priorityQueue
        """self < obj."""
        if self.heuristic is None:  # za algoritam ucs
            if self.price == obj.price:
                return self.name < obj.name
            else:
                return self.price < obj.price
        else:  # za algoritam astar
            if self.price + self.heuristic == obj.price + obj.heuristic:
                return self.name < obj.name
            else:
                return self.price + self.heuristic < obj.price + obj.heuristic


class Algorithm:
    pathStateDescriptor = ""
    pathHeuristicDescriptor = ""
    method = ""

    def __init__(self, pathStateDescriptor, pathHeuristicDescriptor, method):
        self.pathStateDescriptor = pathStateDescriptor
        self.pathHeuristicDescriptor = pathHeuristicDescriptor
        self.method = method

    def readstatedescriptor(self):
        f = open(self.pathStateDescriptor, "r")
        text = f.readlines()
        f.close()
        lines = []
        for i in text:  # izbacivanje komentara
            if i.strip()[0] != "#":
                lines.append(i.strip())
        initialState = lines[0]  # prebacivanje u strukture podataka
        goalStatesTemp = lines[1].split(' ')
        goalStates = {}
        for i in goalStatesTemp:
            goalStates[i] = 1
        transitions = {}
        for i in range(2, len(lines)):
            currentState = lines[i].split(':')[0]
            nextStates = lines[i].split(':')[1].strip().split(' ')
            nextStates.sort()
            for i in range(len(nextStates)):
                nextStates[i] = nextStates[i].split(',')
            transitions[currentState] = nextStates
        return initialState, goalStates, transitions

    def readheuristicdescriptor(self):
        f = open(self.pathHeuristicDescriptor, "r")
        text = f.readlines()
        f.close()
        lines = []
        for i in text:  # izbacivanje komentara
            if i.strip()[0] != "#":
                lines.append(i.strip())
        heuristic = {}
        for i in lines:  # prebacivanje heuristike u strukture podataka
            heuristic[i.split(':')[0]] = float(i.split(':')[1].strip())
        return heuristic

    def solve(self):
        if method == "bfs" or method == "ucs":
            self.bfs_ucs()
        elif method == "astar":
            self.astar()
        elif method == "--check-optimistic":
            self.optimistic()
        elif method == "--check-consistent":
            self.consistent()

    def bfs_ucs(self):
        initialState, goalStates, transitions = self.readstatedescriptor()  # procitaj iz datoteke opisnik stanja
        visited = {}
        if self.method == "bfs":
            print("# BFS")
            q = queue.Queue()
        else:
            print("# UCS")
            q = queue.PriorityQueue()
        first = Node(initialState, 1, 0, "#$%&", None)  # pocetni cvor i njegova referenca na prethodni
        q.put(first)
        while not q.empty():
            temp = q.get()
            if self.method == "ucs":
                if temp.name in visited and visited[temp.name].price < temp.price:  # za ucs ako postoji neki cvor na fronti, a nije jeftiniji put
                    continue
            visited[temp.name] = temp
            if temp.name in goalStates:  # ispis rjesenja
                print("[FOUND_SOLUTION]: yes")
                print("[STATES_VISITED]: " + str(len(visited)))
                print("[PATH_LENGTH]: " + str(temp.depth))
                print("[TOTAL_COST]: " + str("{:.1f}".format(temp.price)))
                backwards = temp
                path = [backwards.name]
                while backwards.reference != "#$%&":
                    path.append(backwards.reference)
                    backwards = visited[backwards.reference]
                output = "[PATH]: "
                for i in reversed(path):
                    output += i + " => "
                print(output[:-4])
                return
            for i in transitions[temp.name]:  # širenje
                if i[0] == '':
                    continue
                if self.method == "bfs":
                    if i[0] not in visited:
                        q.put(Node(i[0], temp.depth + 1, temp.price + float(i[1]), temp.name, None))
                else:
                    if i[0] not in visited or visited[i[0]].price > temp.price + float(
                            i[1]):  # ako nije stanje posjećeno ili ako do njega mozemo doci jeftinije
                        q.put(Node(i[0], temp.depth + 1, temp.price + float(i[1]), temp.name, None))
        print("[FOUND_SOLUTION]: no")

    def astar(self):
        initialState, goalStates, transitions = self.readstatedescriptor()  # procitaj iz datoteke opisnik stanja
        heuristic = self.readheuristicdescriptor()  # procitaj iz datoteke opisnik heuristike
        visited = {}
        opened = {}
        print("# A-STAR " + self.pathHeuristicDescriptor)
        q = queue.PriorityQueue()
        first = Node(initialState, 1, 0, "#$%&",
                     heuristic[initialState])  # pocetni cvor i njegova referenca na prethodni kao null
        q.put(first)
        opened[first.name] = first
        while not q.empty():
            temp = q.get()
            del opened[temp.name]
            visited[temp.name] = temp
            if temp.name in goalStates:  # ispis
                print("[FOUND_SOLUTION]: yes")
                print("[STATES_VISITED]: " + str(len(visited)))
                print("[PATH_LENGTH]: " + str(temp.depth))
                print("[TOTAL_COST]: " + str("{:.1f}".format(temp.price)))
                backwards = temp
                path = [backwards.name]
                while backwards.reference != "#$%&":
                    path.append(backwards.reference)
                    backwards = visited[backwards.reference]
                output = "[PATH]: "
                for i in reversed(path):
                    output += i + " => "
                print(output[:-4])
                return
            for i in transitions[temp.name]:  # širenje
                if i[0] == '':
                    continue
                if i[0] in visited or i[0] in opened:
                    if (i[0] in visited and visited[i[0]].price < temp.price + float(i[1])) or \
                            (i[0] in opened and opened[i[0]].price < temp.price + float(i[1])):
                        continue
                    else:
                        if i[0] in visited:
                            del visited[i[0]]
                        if i[0] in opened:
                            del opened[i[0]]
                newNode = Node(i[0], temp.depth + 1, temp.price + float(i[1]), temp.name, heuristic[i[0]])
                q.put(newNode)
                opened[i[0]] = newNode
        print("[FOUND_SOLUTION]: no")

    def optimistic(self):
        print("# HEURISTIC-OPTIMISTIC " + self.pathHeuristicDescriptor)
        #  napraviti cemo svoj ucs s obrnutim putanjama tako da iz svih rjesenja krećemo prema svim čvorovima
        #  u pravilu nam goalStates ne trebaju jer želimo obići sve čvorove
        initialState, goalStates, transitions = self.readstatedescriptor()  # procitaj iz datoteke opisnik stanja
        heuristic = self.readheuristicdescriptor()  # procitaj iz datoteke opisnik heuristike
        initialState = goalStates
        reversedTranstions = {}  # okrecemo usmjereni graf
        for i in transitions:
            for j in transitions[i]:
                if j[0] == '':
                    continue
                if j[0] not in reversedTranstions:
                    reversedTranstions[j[0]] = []
                reversedTranstions[j[0]].append([i, j[1]])
        for i in heuristic:  # dodavanje prijelaza cvorova koji su ponori
            if i not in reversedTranstions:
                reversedTranstions[i] = [['']]
        visited = {}
        bestPrice = {}
        q = queue.PriorityQueue()
        for i in initialState:
            first = Node(i, 1, 0, "#$%&", None)  # pocetni cvor i njegova referenca na prethodni
            q.put(first)
            bestPrice[i] = 0
        while not q.empty():
            temp = q.get()
            if temp.name in visited and visited[temp.name].price < temp.price:  # za ucs ako postoji neki cvor na fronti, a nije jeftiniji put
                continue
            visited[temp.name] = temp
            bestPrice[temp.name] = temp.price #  azuriranje najbolje cijene puta
            for i in reversedTranstions[temp.name]:  # širenje
                if i[0] == '':
                    continue
                if i[0] not in visited or visited[i[0]].price > temp.price + float(i[1]):  # ako nije stanje posjećeno ili ako do njega mozemo doci jeftinije
                    q.put(Node(i[0], temp.depth + 1, temp.price + float(i[1]), temp.name, None))
        bestPriceSorted = []  # sortiranje cvorova
        for i in bestPrice:
            bestPriceSorted.append([i, bestPrice[i]])
        bestPriceSorted.sort()
        conclusion = True
        for i in bestPriceSorted:
            if heuristic[i[0]] <= i[1]:
                msg = "OK"
            else:
                msg = "ERR"
                conclusion = False
            print("[CONDITION]: [" + msg + "] h(" + i[0] + ") <= h*: " + str(heuristic[i[0]]) + " <= " + str("{:.1f}".format(i[1])))
        if conclusion:
            print("[CONCLUSION]: Heuristic is optimistic.")
        else:
            print("[CONCLUSION]: Heuristic is not optimistic.")

    def consistent(self):
        print("# HEURISTIC-CONSISTENT " + self.pathHeuristicDescriptor)
        initialState, goalStates, transitions = self.readstatedescriptor()  # procitaj iz datoteke opisnik stanja
        heuristic = self.readheuristicdescriptor()  # procitaj iz datoteke opisnik heuristike
        conclusion = True
        transitions = dict(sorted(transitions.items()))  # sortiranje prijelaza
        for i in transitions:
            for j in transitions[i]:
                if j[0] == '':
                    continue
                if heuristic[i] <= heuristic[j[0]] + float(j[1]):
                    msg = "OK"
                else:
                    msg = "ERR"
                    conclusion = False
                print("[CONDITION]: [" + msg + "] h(" + str(i) + ") <= h(" + str(j[0]) +
                      ") + c: " + str("{:.1f}".format(heuristic[i])) + " <= " + str("{:.1f}".format(heuristic[j[0]])) +
                      " + " + str("{:.1f}".format(float(j[1]))))
        if conclusion:
            print("[CONCLUSION]: Heuristic is consistent.")
        else:
            print("[CONCLUSION]: Heuristic is not consistent.")


pathStateDescriptor = ""  # unos argumenata komandne linije
pathHeuristicDescriptor = ""
method = ""
for i in range(1, len(sys.argv)):
    if sys.argv[i] == "--ss":
        pathStateDescriptor = sys.argv[i + 1]
    elif sys.argv[i] == "--h":
        pathHeuristicDescriptor = sys.argv[i + 1]
    elif sys.argv[i] == "--alg":
        method = sys.argv[i + 1]
    elif sys.argv[i] == "--check-optimistic" or sys.argv[i] == "--check-consistent":
        method = sys.argv[i]

alg = Algorithm(pathStateDescriptor, pathHeuristicDescriptor, method)
alg.solve()
