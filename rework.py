from dataclasses import dataclass, field
from typing import List, Dict
import csv, re

RECIPEFILE = 'recipes.dat'
FOODFILE = 'food.csv'

@dataclass
class FoodItem:
    weight: float = field(init=False, repr=False) 
    name: str # Name of the food item e.g. "Fluffy Wheat"
    oredict: list # Ore Dict key for categories

    materials: list = field(init=False, repr=False) 
    cooked: bool = field(init=False, repr=False)
    mod: str  # Name of parent mod
    id: str # Game ID of food e.g. example:fluffy_wheat
    
    hunger: int = 0
    saturation: float = 0.0

    step: int = -1

    def __post_init__(self):
        self.weight = self.getWeight()
        self.materials = self.getMaterials()
        self.cooked = self.isCooked()
        self.oredict = [f'ore:{ore}' for ore in self.oredict]

    
    def __str__(self):
        if self.materials:
            return f'{self.name} made with {len(self.materials)} mats'
        else:
            return f'{self.name} is basic'

    
    def toCSV(self):
        "Writes data in CSV format"
        pass

    def isCooked(self):
        "Returns if item is cooked"
        for ore in self.oredict:
            if 'cook' in ore:
                return True
        return False

    def isBasic(self):
        "Returns if food is crop, raw meat, or other non-crafted fooditem"
        return self.materials == None


    def getMaterialDict(self):
        if self.id in RECIPEDICT.keys():
            return RECIPEDICT[self.id].materials.copy()
        return None

    
    def getMaterials(self):
        "Assigned to materials value"
        if self.id in RECIPEDICT.keys():
            return list(RECIPEDICT[self.id].materials.keys())
        self.step = 0
        return None


    def getWeight(self):
        #TODO Calculate weight of item using Calamari method in TODO.txt
        return None


@dataclass
class RecipeItem:
    name: str
    materials: dict # {Material name, count}



FIELDNAMES = ['Registry name', 'Hunger', 'Saturation', 'Meta/dmg', 'Display name', 'Ore Dict keys', 'Mod name', 'Item ID', 'Subtypes']
FOODDICT = {} # FIlled with FoodItems
RECIPEDICT = {}
OREDICT = {'gemAmbrosium': ['aether_legacy:ambrosium_shard']}
COOKINGTOOLS = [
    'animania:carving_knife',
    'ore:toolBakeware',
    'ore:toolMixingbowl',
    'ore:toolMortarandpestle',
    'ore:toolPot',
    'ore:toolSaucepan',
    'ore:toolCuttingboard',
    'ore:toolJuicer',
    'ore:toolSkillet',
    'minecraft:dye', 
    'ore:foodOliveoil',
    'ore:foodVinegar',
    'ore:foodVanilla',
    'ore:foodGroundcinnamon',
    'ore:foodSoysauce',
    'ore:foodHoisinsauce',
    'ore:foodCornmeal',
    'ore:foodDough',
    'ore:foodMeringue',
    'ore:foodButter',
    'ore:foodBatter',
    'ore:foodFlour',
    'ore:foodPasta',
    'ore:foodNoodles',
    'ore:foodMayo',
    'ore:foodBlackpepper',
    'ore:foodCocoapowder',
    'ore:dustSalt',
    'ore:itemSalt',
    'ore:foodFivespice',
    'ore:foodGroundbeef',
    'ore:foodGroundpork',
    'minecraft:snowball', # Smoothies
    'forge:bucketfilled',
    'minecraft:milk_bucket',
    'ore:listAllwater',
    'ore:foodBubblywater',
    'minecraft:glass_bottle',
    'minecraft:bowl',
    'betternether:stalagnate_bowl',
    'minecraft:nether_wart',
    'biomesoplenty:mushroom',
    'rats:plague_essence',
    'minecraft:reeds',
    'bountifulbaubles:trinketshulkerheart', # Sandwich Horror
    'ore:flower',
    'minecraft:cactus',
    'minecraft:flint' # Miner Stew
    ]
SKIPPED = [ # fuck cheese wheels
    'aether_legacy:ambrosium_block',
    'charm:rotten_flesh_block',
    'animania:friesian_cheese_wheel',
    'animania:goat_cheese_wheel', 
    'animania:holstein_cheese_wheel', 
    'animania:jersey_cheese_wheel',
    'animania:sheep_cheese_wheel'
    ]


def isFood(name):
    "Returns if recipe name is a food item"
    with open(FOODFILE) as f:
        if '<' in name:
            name = name[1:-1]
        for line in f:
            if name == line.split(',')[0]:
                return True
        return False
            
            
def isOre(name: str):
    "Returns if name (id) is an ore"
    return name.startswith('ore:')


def updateOres(foodID, step):
    if FOODDICT[foodID].oredict:
        for ore in FOODDICT[foodID].oredict:
            for food in OREDICT[ore]:
                FOODDICT[food].step = step


def cleanID(foodID: str):
    "Turns string into clean, standard format of mod_name:registry_name"
    if '<' in foodID:
        foodID = foodID[1:-1] # removes < and > from ends
    if len(foodID.split(':')) > 2:
        foodID = foodID[:foodID.rindex(':')]
    return foodID
     

def FillRecipeDict():
    "Pulls lines from RECIPEFILE and converts them to more accessible format"

    with open(RECIPEFILE) as r:
        linecount = 0
        for line in r:
            linecount += 1
            # Sorry the below line does a lot of python magic but it works so...
            words = re.findall('<(.*?)>', "".join(line.split()))
            if len(words) > 1:
                # dict = {'name': f'<{words[0]}>', 'mats': {f'<{i}>': words[1:].count(i) for i in words[1:]}}
                recipe = RecipeItem(name=words[0], materials={
                    cleanID(item): words[1:].count(item) for item in words[1:]})
                
                if isFood(recipe.name) and all([mat not in SKIPPED for mat in recipe.materials ]):
                    RECIPEDICT[recipe.name] = recipe


def FillFoodDict():
    if len(RECIPEDICT) == 0:
        FillRecipeDict()

    with open(FOODFILE, 'r') as f:
        readCSV = csv.DictReader(f, quotechar='"', fieldnames=FIELDNAMES)
        for row in readCSV:
            #Registry name,Hunger,Saturation,Meta/dmg,Display name,Ore Dict keys,Mod name,Item ID,Subtypes
            food = FoodItem(
                id = row['Registry name'],
                hunger = row['Hunger'],
                saturation = row['Saturation'],
                name = row['Display name'],
                oredict = row['Ore Dict keys'].split(','),
                mod = row['Mod name'],
            )
            FOODDICT[food.id] = food

            #Cause FUCK ambrosium
            if food.id == 'aether_legacy:ambrosium_shard':
                food.step=0
            # Updates OREDICT to include every food under oredict key
            if not food.oredict[0].isspace():
                for ore in food.oredict:
                    if ore in OREDICT.keys():
                        OREDICT[ore].append(f'{food.id}')
                    else:
                        OREDICT[ore]=[food.id]
            else:
                food.oredict = None


def calcSteps():
    #TODO dumb bitch broked
    "Calculates how many steps required to craft item."
    from collections import deque
    queue = deque(FOODDICT.values()) # This is just a queue of FoodItems
    ERR=[]
    count=0
    while queue: # Runs until empty, don't ever do this
        food = queue.popleft()
        count+=1
        if count % 50 == 0:
            print(len(queue))
        highestStep = 1 # Set to be one higher than basic ingredients (which are 0)
        notReady = False

        if food.step > -1: # This means step was declared
            continue       # And needs to be removed from deque

        for material in food.materials:
            testStep = None
            if material in COOKINGTOOLS:
                continue
            elif isOre(material):
                # print(sorted(FOODDICT.values(), key = lambda x: x.step))
                # Use above in need to grab highest or lowest value FoodItem from OREDICT
                try:
                    testStep = FOODDICT[OREDICT[material][0]].step
                except:
                    ERR.append(material)
                    print(ERR)
                    continue
            else:
                try:
                    testStep = FOODDICT[material].step
                except:
                    ERR.append(material)
                    print(ERR)
                    continue
            if testStep == -1:
                notReady = True
                break
            if testStep > highestStep:
                highestStep=testStep+1

        if notReady:
            queue.append(food)
        else:
            food.step = highestStep
            # Update to updateOre method
            updateOres(food.id, food.step)
    print(ERR)


if __name__ == '__main__':
    FillRecipeDict()
    FillFoodDict()
    calcSteps()
    for food in FOODDICT.values():
        if food.steps > 2:
            print(food)
    
