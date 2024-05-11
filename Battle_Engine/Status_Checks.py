def grounded(mon):
    if mon.type_one == "Flying" or mon.type_two == "Flying":
        return
    if mon.ability == "Levitate":
        return
    return True


def can_swap(mon_1, mon_2):
    if mon_1.rooted:
        return
    if mon_2.trapping[0] != 0:
        return
    if mon_2.blocking:
        return
    if mon_2.ability in ["Arena Trap", "Magnet Pull", "Shadow Tag"]:
        if mon_2.ability == "Arena Trap" and grounded(mon_1):
            return
        if mon_2.ability == "Magnet Pull":
            if mon_1.type_one == "Steel" or mon_1.type_two == "Steel":
                return
        if mon_2.ability == "Shadow Tag":
            return
    return True


def check_for_status_cure(mon_1):
    if mon_1.ability == "Immunity" and mon_1.status in ["PSN", "TOX"]:
        mon_1.status = ""
        # print pop up
    elif mon_1.ability in ["Insomnia", "Vital Spirit"] and mon_1.status == "SLP":
        mon_1.status = ""
        # print pop up
    elif mon_1.ability == "Limber" and mon_1.status == "PAR":
        mon_1.status = ""
        # print pop up
    elif mon_1.ability == "Magma Armor" and mon_1.status == "FRZ":
        mon_1.status = ""
        # print pop up
    elif mon_1.ability == "Water Veil" and mon_1.status == "BRN":
        mon_1.status = ""
        # print pop up
    elif mon_1.ability == "Own Tempo" and mon_1.confused:
        mon_1.confused = False


def can_attack(self, trainer_mon):
    for data in self.suspend:
        if trainer_mon in data:
            self.turn_order.put([1, data[1].speed, data[0], data[1].owner])
            self.suspend.remove(data)
            return False
    if trainer_mon.bide > 0:
        self.turn_order.put([1, trainer_mon.speed, self.moves.get("Bide"), trainer_mon.owner])
    elif trainer_mon.uproar > 0:
        self.turn_order.put([1, trainer_mon.speed, self.moves.get("Uproar"), trainer_mon.owner])
    else:
        return True
