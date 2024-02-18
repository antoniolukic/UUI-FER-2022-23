import sys


class Algorithm:
    pathClauseList = ""
    pathCommandList = ""
    clauses = []
    references = []
    numStartingPremises = 0
    numPremises = 0
    jump = 0
    backref = []

    def __init__(self, pathClauseList, pathCommandList):
        self.pathClauseList = pathClauseList
        self.pathCommandList = pathCommandList

    def readClauseList(self):
        f = open(self.pathClauseList, "r")
        text = f.readlines()
        f.close()
        lines = []
        for i in text:  # izbacivanje komentara
            if i.strip()[0] != "#":
                lines.append(i.strip())
        clauses = []
        if pathCommandList == "":  # hocemo li zadnji uzeti kao negaciju cilja ili ne
            last = 1
        else:
            last = 0
        for i in range(len(lines) - last):
            atoms = lines[i].lower().split(' v ')
            s = set()
            for j in atoms:
                s.add(j)
            clauses.append(s)
        return clauses, lines[len(lines) - 1].lower().split(' v ')

    def clean(self):
        newClauses = []
        for i in range(len(self.clauses)):  # micemo sve tautologije
            flag = True
            for j in self.clauses[i]:
                if (j[0] != "~" and ("~" + j) in self.clauses[i]) or (j[0] == "~" and j[1:] in self.clauses[i]):
                    flag = False
                    break
            if flag:
                newClauses.append(self.clauses[i])
        self.clauses = newClauses
        newClauses = []
        for i in range(len(self.clauses)):  # micemo sve pokrivene klauzule
            flag = True
            for j in range(i + 1, len(self.clauses)):
                if self.clauses[j].issubset(self.clauses[i]):
                    flag = False
                    break
            if flag:
                newClauses.append(self.clauses[i])
                self.jump += 1
        self.clauses = newClauses
        self.numStartingPremises = self.jump - self.numPremises

    def onlyNeeded(self, n):
        if self.references[n][0] == -1:
            return
        else:
            if self.references[n][0] not in self.backref:
                self.backref.append(self.references[n][0])
                self.onlyNeeded(self.references[n][0])
            if self.references[n][1] not in self.backref:
                self.backref.append(self.references[n][1])
                self.onlyNeeded(self.references[n][1])

    def resolution(self):
        self.clean()
        for i in range(len(self.clauses)):
            self.references.append([-1, -1])

        notErased = ["a"]

        while len(notErased) > 0:
            new = []
            newReference = []
            for i in range(len(self.clauses)):
                for j in range(max(self.numStartingPremises, i + 1),
                               len(self.clauses)):  # strategija skupa potpore -> barem jedna iz Sos skupa
                    s = set()
                    for k in self.clauses[i]:
                        if k[0] != "~" and ("~" + k) in self.clauses[j]:  # našli smo komplementarne literale
                            s = self.clauses[i].union(self.clauses[j])
                            s.discard(k)
                            s.discard("~" + k)  # izbacimo komplementarne literale
                            if len(s) == 0:
                                self.clauses.append({"NIL"})
                                self.references.append([min(i, j), max(i, j)])
                                self.backref.append(len(self.clauses) - 1)
                                self.onlyNeeded(len(self.references) - 1)
                                return True
                            break
                        elif k[0] == "~" and (k[1:] in self.clauses[j]):  # ista stvar samo drugi par literala
                            s = self.clauses[i].union(self.clauses[j])
                            s.discard(k)
                            s.discard(k[1:])
                            if len(s) == 0:
                                self.clauses.append({"NIL"})
                                self.references.append([min(i, j), max(i, j)])
                                self.backref.append(len(self.clauses) - 1)
                                self.onlyNeeded(len(self.clauses) - 1)
                                return True
                            break
                    if len(s) > 0:
                        new.append(s)
                        newReference.append([min(i, j), max(i, j)])
            notErased = []
            notErasedReferences = []
            for i in range(
                    len(new)):  # po strategiji brisanja izbacimo sve klauzule koje su podskup već neke postojeće ili su tautologije
                flag = True
                for j in range(len(self.clauses)):  # između novih i postojećih
                    if self.clauses[j].issubset(new[i]):
                        flag = False
                        break
                for j in range(i + 1, len(new)):  # između novih i novih
                    if new[j].issubset(new[i]):
                        flag = False
                        break
                for j in new[i]:  # ako je tautologija
                    if (j[0] != "~" and ("~" + j) in new[i]) or (j[0] == "~" and j[1:] in new[i]):
                        flag = False
                        break
                if flag:
                    notErased.append(new[i])
                    notErasedReferences.append(newReference[i])

            self.numStartingPremises += self.numPremises
            self.numPremises = len(notErased)  # povećaj broj da se ne ponavljamo u ispitivanju premisa

            for i in range(len(notErased)):  # nadodaj u skup klauzula novo znanje
                self.clauses.append(notErased[i])
                self.references.append(notErasedReferences[i])

        return False

    def solve(self):
        self.clauses, lastClause = self.readClauseList()
        if pathCommandList == "":  # ako se radi o resolution
            for i in lastClause:
                s = set()
                if i[0] == "~":
                    s.add(i[1:])
                else:
                    s.add("~" + i)
                self.clauses.append(s)
                self.numPremises += 1
            if not self.resolution():
                print("[CONCLUSION]: " + " v ".join(lastClause) + " is unknown")
            else:
                self.backref.sort()
                sign = False
                number = 1
                for i in self.backref:
                    if not sign and i >= self.jump:
                        print("===============")
                        sign = True
                    if sign:
                        print(str(number) + ". " + " v ".join(self.clauses[i]) + " (" +
                              str(self.backref.index(self.references[i][0]) + 1) + ", " +
                              str(self.backref.index(self.references[i][1]) + 1) + ")")
                    else:
                        print(str(number) + ". " + " v ".join(self.clauses[i]))
                    number += 1
                print("===============")
                print("[CONCLUSION]: " + " v ".join(lastClause) + " is true")
        else:
            print("Constructed with knowledge:")
            for i in self.clauses:
                print(" v ".join(i))
            f = open(self.pathCommandList, "r")
            actions = f.readlines()
            f.close()
            for i in actions:
                print("User's command: " + str(i[:-1]).lower())
                currentKnowledge = self.clauses.copy()
                if i[-2] == "?":  # jer je \n zadnji znak
                    goal = i[:-3].lower().split(' v ')
                    for j in goal:  # negacija cilja
                        s = set()
                        if j[0] == "~":
                            s.add(j[1:])
                        else:
                            s.add("~" + j)
                        self.clauses.append(s)
                        self.numPremises += 1
                    if not self.resolution():
                        print("[CONCLUSION]: " + " v ".join({i[:-3].lower()}) + " is unknown")
                    else:
                        self.backref.sort()
                        sign = False
                        number = 1
                        for j in self.backref:
                            if not sign and j >= self.jump:
                                print("===============")
                                sign = True
                            if sign:
                                print(str(number) + ". " + " v ".join(self.clauses[j]) + " (" +
                                      str(self.backref.index(self.references[j][0]) + 1) + ", " +
                                      str(self.backref.index(self.references[j][1]) + 1) + ")")
                            else:
                                print(str(number) + ". " + " v ".join(self.clauses[j]))
                            number += 1
                        print("===============")
                        print("[CONCLUSION]: " + " v ".join({i[:-3].lower()}) + " is true")

                    self.clauses = currentKnowledge.copy()
                    self.references = []
                    self.numStartingPremises = 0
                    self.numPremises = 0
                    self.jump = 0
                    self.backref = []

                elif i[-2] == "+":  # dodavanje klauzule
                    add = i[:-3].lower().split(' v ')
                    s = set()
                    for j in add:
                        s.add(j)
                    self.clauses.append(s)
                elif i[-2] == "-":  # brisanje klauzule
                    sub = i[:-3].lower().split(' v ')
                    s = set()
                    for j in sub:
                        s.add(j)
                    if s in self.clauses:
                        self.clauses.remove(s)


pathClauseList = ""
pathCommandList = ""
if sys.argv[1] == "resolution":
    pathClauseList = sys.argv[2]
elif sys.argv[1] == "cooking":
    pathClauseList = sys.argv[2]
    pathCommandList = sys.argv[3]

alg = Algorithm(pathClauseList, pathCommandList)
alg.solve()
