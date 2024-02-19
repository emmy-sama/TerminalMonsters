pokedex = [
    {"Species": "Bulbasaur", "Typeone": "Grass", "Typetwo": "Poison", "Abilities": ["Overgrow"],
     "Gender Ratio": 0.875, "Catch rate": 11.9, "Height": 28, "Weight": 15.2, "bHP": 45, "bAttack": 49, "bDefense": 49,
     "bSp.Attack": 65, "bSp.Defense": 65, "bSpeed": 45, "EvoLvl": 16, "Evo": 1},
    {"Species": "Ivysaur", "Typeone": "Grass", "Typetwo": "Poison", "Abilities": ["Overgrow"],
     "Gender Ratio": 0.875, "Catch rate": 11.9, "Height": 39, "Weight": 28.7, "bHP": 60, "bAttack": 62, "bDefense": 63,
     "bSp.Attack": 80, "bSp.Defense": 80, "bSpeed": 60}
]

# Hardy, Lonely, Brave, Adamant, Naughty, Bold, Docile, Relaxed, Impish, Lax, Timid, Hasty, Serious, Jolly, Naive,
# Modest, Mild, Quiet, Bashful, Rash, Calm, Gentle, Sassy, Careful, Quirky

natures = \
 [{}, {"Attack": 1.10, "Defense": 0.90}, {"Attack": 1.10, "Speed": 0.90}, {"Attack": 1.10, "Sp.Attack": 0.90},
  {"Attack": 1.10, "Sp.Defense": 0.90}, {"Defense": 1.10, "Attack": 0.90}, {}, {"Defense": 1.10, "Speed": 0.90},
  {"Defense": 1.10, "Sp.Attack": 0.90}, {"Defense": 1.10, "Sp.Defense": 0.90}, {"Speed": 1.10, "Attack": 0.90},
  {"Speed": 1.10, "Defense": 0.90}, {}, {"Speed": 1.10, "Sp.Attack": 0.90}, {"Speed": 1.10, "Sp.Defense": 0.90},
  {"Sp.Attack": 1.10, "Attack": 0.90}, {"Sp.Attack": 1.10, "Defense": 0.90}, {"Sp.Attack": 1.10, "Speed": 0.90}, {},
  {"Sp.Attack": 1.10, "Sp.Defense": 0.90}, {"Sp.Defense": 1.10, "Attack": 0.90}, {"Sp.Defense": 1.10, "Defense": 0.90},
  {"Sp.Defense": 1.10, "Speed": 0.90}, {"Sp.Defense": 1.10, "Sp.Attack": 0.90}, {}]

moves = {"Tackle": {"Name": "Tackle", "Type": "Normal", "DmgType": "Physical", "PP": 35, "Dmg": 35, "Acc": 95,
                    "DoesDmg": True, "ChangesStats": False},
         }

type_effectiveness = {"Normal": {"Rock": 0.5, "Ghost": 0, "Steel": 0.5},

}
