from math import floor
from random import randint


def speed_check(self, mon_1, mon_2):
    # Checks priority
    if mon_1[2].get("priority") > mon_2[2].get("priority"):
        return [mon_1, mon_2]
    if mon_1[2].get("priority") < mon_2[2].get("priority"):
        return [mon_2, mon_1]

    # Normal speed calcs
    mon_1_speed = floor(
        mon_1[3].active.speed * self.temp_stat_table_norm.get(mon_1[3].active.temp_stats.get("speed")))
    if mon_1[3].active.ability == "Chlorophyll" and self.weather == "sun":
        mon_1_speed = floor(mon_1_speed * 2)
    if mon_1[3].active.ability == "Swift Swim" and self.weather == "rain":
        mon_1_speed = floor(mon_1_speed * 2)
    if mon_1[3].active.status == "PAR":
        mon_1_speed = floor(mon_1_speed * 0.25)
    mon_2_speed = floor(
        mon_2[3].active.speed * self.temp_stat_table_norm.get(mon_2[3].active.temp_stats.get("speed")))
    if mon_2[3].active.ability == "Chlorophyll" and self.weather == "sun":
        mon_2_speed = floor(mon_2_speed * 2)
    if mon_2[3].active.ability == "Swift Swim" and self.weather == "rain":
        mon_2_speed = floor(mon_2_speed * 2)
    if mon_2[3].active.status == "PAR":
        mon_2_speed = floor(mon_2_speed * 0.25)

    # Returns Turn Order
    if mon_1_speed > mon_2_speed:
        return [mon_1, mon_2]
    if mon_1_speed < mon_2_speed:
        return [mon_2, mon_1]
    if randint(0, 1) == 0:
        return [mon_1, mon_2]
    else:
        return [mon_2, mon_1]
