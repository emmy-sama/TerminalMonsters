import random


class Queue:
    def __init__(self):
        self.lst = []

    def put(self, data):
        if self.lst:
            if data[0] < self.lst[0][0]:
                self.lst.insert(0, data)
            elif data[0] == self.lst[0][0] and data[1] > self.lst[0][1]:
                self.lst.insert(0, data)
            elif data[0] == self.lst[0][0] and data[1] == self.lst[0][1]:
                if random.randint(0, 1) == 0:
                    self.lst.append(data)
                else:
                    self.lst.insert(0, data)
            else:
                self.lst.append(data)
        else:
            self.lst.append(data)

    def append(self, data):
        self.lst.append(data)

    def peek(self):
        if not self.lst:
            return None
        else:
            return self.lst[0][2]

    def len(self):
        return len(self.lst)

    def dequeue(self):
        return self.lst.pop(0)[2]

    def move_dequeue(self):
        return self.lst.pop(0)

    def focus_punch(self):
        temp = []
        for item in self.lst:
            if isinstance(item, dict):
                if item[3].get("name") == "Focus Punch":
                    temp.append(item[4])
        return temp

    def rage(self):
        temp = []
        for item in self.lst:
            if isinstance(item, dict) and item[3].get("name") == "Rage":
                temp.append(item[3])
        return temp


