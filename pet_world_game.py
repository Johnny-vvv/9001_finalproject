import random
import time
import json
import os

# Type advantage chart
TYPE_ADVANTAGE = {
    "Fire": "Grass",
    "Grass": "Water",
    "Water": "Fire",
    "Ice": "Earth",
    "Earth": "Wind",
    "Wind": "Grass",
    "Thunder": "Ice"
}

# Base map configurations
BASE_MAPS = {
    "Forest": {"monsters": ["Tree Sprite", "Giant Boar"], "base_level_range": (1, 3), "type": "Grass"},
    "Volcano": {"monsters": ["Fire Serpent", "Lava Golem"], "base_level_range": (3, 5), "type": "Fire"},
    "Lake": {"monsters": ["Water Nymph", "Octopus Monster"], "base_level_range": (4, 6), "type": "Water"},
    "Desert": {"monsters": ["Sand Scorpion", "Stone Golem"], "base_level_range": (5, 7), "type": "Earth"},
    "Snowy Mountain": {"monsters": ["Ice Wolf", "Snow Giant"], "base_level_range": (6, 8), "type": "Ice"},
    "Sky Realm": {"monsters": ["Thunder Eagle", "Cloud Dragon"], "base_level_range": (7, 9), "type": "Wind"},
    "Thunder Valley": {"monsters": ["Electric Snake", "Thunder Beast"], "base_level_range": (8, 10), "type": "Thunder"}
}

ITEMS = {
    "Small Healing Potion": {"heal": 30, "price": 8},
    "Large Healing Potion": {"heal": 60, "price": 15}
}

UPGRADE_COST = 12


class Skill:
    def __init__(self, name, skill_type, power):
        self.name = name
        self.skill_type = skill_type
        self.power = power

    def use(self, user, target=None):
        if self.skill_type == "attack":
            damage = max(1, user.attack + self.power - target.defense + random.randint(-2, 2))
            if TYPE_ADVANTAGE.get(user.pet_type) == target.monster_type:
                damage = int(damage * 1.5)
                print("Type advantage! Damage increased!")
            elif TYPE_ADVANTAGE.get(target.monster_type) == user.pet_type:
                damage = int(damage * 0.75)
                print("Type disadvantage, damage reduced.")
            target.hp -= damage
            target.hp = int(max(0, target.hp))
            print(f"{user.name} uses [{self.name}] and deals {damage} damage!")
        elif self.skill_type == "heal":
            heal_amount = int(min(self.power, user.max_hp - user.hp))
            user.hp += heal_amount
            user.hp = int(user.hp)
            print(f"{user.name} uses [{self.name}] and restores {heal_amount} HP!")
        elif self.skill_type == "defense":
            user.defense += self.power
            print(f"{user.name} uses [{self.name}], defense increased by {self.power} for this round!")


class Pet:
    def __init__(self, name, pet_type, level=1, exp=0, gold=0):
        self.name = name
        self.pet_type = pet_type
        self.level = level
        self.exp = exp
        self.gold = gold
        self.max_hp = 80 + (level - 1) * 15
        self.hp = self.max_hp
        self.attack = 8 + (level - 1) * 4
        self.defense = 4 + (level - 1) * 2
        self.speed = 4 + (level - 1) * 2
        self.base_defense = self.defense
        skill_map = {
            "Fire": Skill("Flame Impact", "attack", 20),
            "Water": Skill("Water Whip", "attack", 20),
            "Grass": Skill("Vine Entanglement", "attack", 20),
            "Earth": Skill("Rock Missile", "attack", 20),
            "Ice": Skill("Frost Spike", "attack", 20),
            "Wind": Skill("Storm Blade", "attack", 20),
            "Thunder": Skill("Thunder Strike", "attack", 20)
        }
        self.skills = [skill_map.get(pet_type, Skill("Normal Attack", "attack", 20))]
        self.items = {}

    def is_alive(self):
        return self.hp > 0

    def gain_exp(self, amount):
        self.exp += amount
        print(f"{self.name} gains {amount} experience points!")
        if self.exp >= 12:
            self.level_up()

    def gain_gold(self, amount):
        self.gold += amount
        print(f"{self.name} gains {amount} gold coins!")

    def level_up(self):
        self.level += 1
        self.exp = 0
        self.max_hp += 15
        self.hp = self.max_hp
        self.attack += 4
        self.defense += 2
        self.base_defense = self.defense
        self.speed += 2
        print(f"🎉 {self.name} levels up to {self.level}!")
        if self.level == 3:
            self.skills.append(Skill("Healing Spell", "heal", 30))
            print(f"{self.name} learns the skill [Healing Spell]!")
        if self.level == 5:
            self.skills.append(Skill("Sandstorm", "attack", 25))
            print(f"{self.name} learns the skill [Sandstorm]!")
        if self.level == 7:
            self.skills.append(Skill("Shield Spell", "defense", 8))
            print(f"{self.name} learns the skill [Shield Spell]!")
        if self.level == 10:
            skill_map_advanced = {
                "Fire": Skill("Blazing Dragon", "attack", 30),
                "Water": Skill("Torrential Wave", "attack", 30),
                "Grass": Skill("Thorn Storm", "attack", 30),
                "Earth": Skill("Earthquake Wave", "attack", 30),
                "Ice": Skill("Frozen World", "attack", 30),
                "Wind": Skill("Hurricane Slash", "attack", 30),
                "Thunder": Skill("Thunderous Might", "attack", 30)
            }
            advanced_skill = skill_map_advanced.get(self.pet_type, Skill("Powerful Attack", "attack", 30))
            self.skills.append(advanced_skill)
            print(f"{self.name} learns the skill [{advanced_skill.name}]!")

    def use_item(self):
        if not self.items:
            print("You have no items.")
            return
        print("\nYour Inventory:")
        for i, (item, count) in enumerate(self.items.items()):
            print(f"{i + 1}. {item} x{count}")
        choice = input("Enter item number: ")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(self.items):
                item_name = list(self.items.keys())[idx]
                item = ITEMS[item_name]
                self.hp = int(min(self.max_hp, self.hp + item["heal"]))
                self.items[item_name] -= 1
                if self.items[item_name] == 0:
                    del self.items[item_name]
                print(f"Used {item_name}, restored {item['heal']} HP")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input, please enter a number.")

    def reset_defense(self):
        self.defense = self.base_defense

    def fully_heal(self):
        if self.hp < self.max_hp:
            heal_amount = int(self.max_hp - self.hp)
            self.hp = self.max_hp
            return heal_amount
        return 0


class Monster:
    def __init__(self, name, level, monster_type):
        self.name = name
        self.level = level
        self.monster_type = monster_type
        self.max_hp = 40 + level * 8
        self.hp = self.max_hp
        self.attack = 5 + level * 1.8
        self.defense = 3 + level * 1.5
        self.speed = 4 + level * 1.5

    def is_alive(self):
        return self.hp > 0

    def attack_pet(self, pet):
        damage = int(max(1, self.attack - pet.defense + random.randint(-2, 2)))
        pet.hp -= damage
        pet.hp = int(max(0, pet.hp))
        print(f"{self.name} attacks {pet.name} and deals {damage} damage!")


# Dynamically adjust map level ranges based on pet level (increase difficulty)
def get_adaptive_maps(pet_level):
    adaptive_maps = {}
    for map_name, info in BASE_MAPS.items():
        base_min, base_max = info["base_level_range"]
        offset = max(0, pet_level - 4)
        min_level = max(1, base_min + offset)
        max_level = base_max + offset * 1.5

        adaptive_maps[map_name] = {
            "monsters": info["monsters"],
            "level_range": (int(min_level), int(max_level)),
            "type": info["type"]
        }
    return adaptive_maps


def generate_monster(map_name, pet_level):
    maps = get_adaptive_maps(pet_level)
    try:
        info = maps[map_name]
        name = random.choice(info["monsters"])
        level = random.randint(*info["level_range"])
        return Monster(name, level, info["type"])
    except KeyError:
        print(f"Map {map_name} does not exist.")
        raise


def battle(pet, monster):
    print(f"\n⚔️ Encountered [{monster.name}] (Lv.{monster.level} / {monster.monster_type})!")
    round_num = 1
    while pet.is_alive() and monster.is_alive():
        print(f"\n--- Round {round_num} ---")
        print(f"{pet.name} HP: {pet.hp}/{pet.max_hp} | {monster.name} HP: {monster.hp}/{monster.max_hp}")
        print("Select a skill:")
        for i, skill in enumerate(pet.skills):
            print(f"{i + 1}. {skill.name}")
        print(f"{len(pet.skills) + 1}. Use Item")
        choice = input("Skill number or item: ")

        try:
            idx = int(choice) - 1
            if idx < len(pet.skills):
                skill = pet.skills[idx]
                first = pet if pet.speed >= monster.speed else monster
                second = monster if first == pet else pet

                if first == pet:
                    skill.use(pet, monster)
                    if monster.is_alive():
                        monster.attack_pet(pet)
                else:
                    monster.attack_pet(pet)
                    if pet.is_alive():
                        skill.use(pet, monster)
            elif idx == len(pet.skills):
                pet.use_item()
                if monster.is_alive():
                    monster.attack_pet(pet)
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input, please enter a number.")

        round_num += 1
        time.sleep(0.5)
    pet.reset_defense()
    if pet.is_alive():
        level_diff = monster.level - pet.level
        exp_multiplier = 1.0
        gold_multiplier = 1.0

        if level_diff >= 3:
            exp_multiplier = 1.8
            gold_multiplier = 1.8
        elif level_diff <= -3:
            exp_multiplier = 0.4
            gold_multiplier = 0.4

        base_exp = monster.level * 10
        base_gold = monster.level * 8
        exp_reward = max(1, int(base_exp * exp_multiplier))
        gold_reward = max(1, int(base_gold * gold_multiplier))

        print(f"🎉 {pet.name} defeated {monster.name}!")
        pet.gain_exp(exp_reward)
        pet.gain_gold(gold_reward)

        if level_diff >= 3:
            print("🌟 Challenged a higher-level monster, rewards greatly increased!")
        elif level_diff <= -3:
            print("💤 Challenged a lower-level monster, rewards significantly reduced.")
    else:
        print(f"💀 {pet.name} has been defeated...")
        pet.hp = max(1, pet.max_hp // 5)
        print(f"💪 {pet.name} regains some strength and can continue the adventure!")


def shop(pet):
    HEAL_PRICE_PER_HP = 0.5
    while True:
        print(f"\n🏪 Shop (Gold: {pet.gold})")
        print(f"❤️ {pet.name} HP: {pet.hp}/{pet.max_hp}")
        print("1. Buy Items")
        print("2. Upgrade Attributes")
        print("3. Restore HP")
        print("4. Exit")
        choice = input("Select an action: ")
        if choice == "1":
            for i, (item, info) in enumerate(ITEMS.items()):
                print(f"{i + 1}. {item} - Restores {info['heal']} HP - {info['price']} Gold")
            idx = input("Enter number to buy (or press Enter to exit): ")
            if idx:
                try:
                    idx = int(idx) - 1
                    item = list(ITEMS.keys())[idx]
                    price = ITEMS[item]["price"]
                    if pet.gold >= price:
                        pet.gold -= price
                        pet.items[item] = pet.items.get(item, 0) + 1
                        print(f"Purchased {item}")
                    else:
                        print("Insufficient gold")
                except (ValueError, IndexError):
                    print("Invalid input, please enter a number.")
        elif choice == "2":
            print("1. Attack +4\n2. Defense +4\n3. Speed +4\n4. Max HP +15")
            attr = input(f"Spend {UPGRADE_COST} Gold to select an upgrade: ")
            if pet.gold >= UPGRADE_COST:
                if attr == "1":
                    pet.attack += 4
                    print("Attack increased!")
                elif attr == "2":
                    pet.defense += 4
                    pet.base_defense += 4
                    print("Defense increased!")
                elif attr == "3":
                    pet.speed += 4
                    print("Speed increased!")
                elif attr == "4":
                    pet.max_hp += 15
                    pet.hp += 15
                    print("Max HP increased!")
                else:
                    print("Invalid selection")
                pet.gold -= UPGRADE_COST
            else:
                print("Insufficient gold")
        elif choice == "3":
            if pet.hp == pet.max_hp:
                print("Your pet is already at full HP!")
                continue

            missing_hp = pet.max_hp - pet.hp
            full_heal_cost = int(missing_hp * HEAL_PRICE_PER_HP)

            print(f"Restoring full HP costs {full_heal_cost} Gold")
            print("1. Restore full HP")
            print("2. Partial restore")
            heal_choice = input("Select: ")

            if heal_choice == "1":
                if pet.gold >= full_heal_cost:
                    pet.gold -= full_heal_cost
                    pet.hp = pet.max_hp
                    print(f"✅ {pet.name} has been fully restored!")
                else:
                    print(f"Insufficient gold, you need {full_heal_cost} Gold")
            elif heal_choice == "2":
                try:
                    amount = int(input(f"Enter HP amount to restore (1-{missing_hp}): "))
                    if 1 <= amount <= missing_hp:
                        cost = int(amount * HEAL_PRICE_PER_HP)
                        if pet.gold >= cost:
                            pet.gold -= cost
                            pet.hp += amount
                            print(f"✅ {pet.name} restored {amount} HP!")
                        else:
                            print(f"Insufficient gold, restoring {amount} HP requires {cost} Gold")
                    else:
                        print(f"Invalid amount, please enter a number between 1-{missing_hp}")
                except ValueError:
                    print("Invalid input, please enter a number")
        elif choice == "4":
            break


def save_game(pet):
    try:
        os.makedirs("saves", exist_ok=True)
        filename = f"saves/save_{pet.name}.json"
        data = {
            "name": pet.name, "type": pet.pet_type, "level": pet.level,
            "exp": pet.exp, "gold": pet.gold, "items": pet.items, "hp": pet.hp
        }
        with open(filename, "w") as f:
            json.dump(data, f)
        print(f"✅ Game saved as {pet.name}")
    except OSError as e:
        print(f"Error saving game: {e}")


def list_saves():
    try:
        if not os.path.exists("saves"):
            return []
        return [f[5:-5] for f in os.listdir("saves") if f.startswith("save_")]
    except OSError as e:
        print(f"Error listing saves: {e}")
        return []


def load_game():
    saves = list_saves()
    if saves:
        print("Existing saves:")
        for i, name in enumerate(saves):
            print(f"{i + 1}. {name}")
        print(f"{len(saves) + 1}. Create new character")
        choice = input("Select number: ")
        try:
            idx = int(choice) - 1
            if idx < len(saves):
                filename = f"saves/save_{saves[idx]}.json"
                with open(filename, "r") as f:
                    d = json.load(f)
                    p = Pet(d["name"], d["type"], d["level"], d["exp"], d["gold"])
                    p.items = d["items"]
                    p.hp = d.get("hp", p.max_hp)
                    if p.level >= 3:
                        p.skills.append(Skill("Healing Spell", "heal", 30))
                    if p.level >= 5:
                        p.skills.append(Skill("Sandstorm", "attack", 25))
                    if p.level >= 7:
                        p.skills.append(Skill("Shield Spell", "defense", 8))
                    if p.level >= 10:
                        skill_map_advanced = {
                            "Fire": Skill("Blazing Dragon", "attack", 30),
                            "Water": Skill("Torrential Wave", "attack", 30),
                            "Grass": Skill("Thorn Storm", "attack", 30),
                            "Earth": Skill("Earthquake Wave", "attack", 30),
                            "Ice": Skill("Frozen World", "attack", 30),
                            "Wind": Skill("Hurricane Slash", "attack", 30),
                            "Thunder": Skill("Thunderous Might", "attack", 30)
                        }
                        p.skills.append(skill_map_advanced.get(p.pet_type, Skill("Powerful Attack", "attack", 30)))
                    return p
        except (ValueError, IndexError):
            print("Invalid input, please enter a number.")

    name = input("Enter pet name: ")
    pet_type = {
        "1": "Fire", "2": "Water", "3": "Grass", "4": "Earth", "5": "Ice", "6": "Wind", "7": "Thunder"
    }.get(input("Select type: 1.Fire 2.Water 3.Grass 4.Earth 5.Ice 6.Wind 7.Thunder: "), "Fire")
    return Pet(name, pet_type)


def main():
    print("🎮 Pet Adventure Game")
    pet = load_game()
    while True:
        print("\n======= Main Menu =======")
        print("1. Explore  2. Check Status  3. Shop  4. Save Game  5. Exit")
        choice = input("Select action: ")
        if choice == "1":
            current_maps = get_adaptive_maps(pet.level)
            print("Map Selection:")
            for i, map_name in enumerate(current_maps):
                level_range = current_maps[map_name]["level_range"]
                print(f"{i + 1}. {map_name} (Recommended Level: {level_range[0]}-{level_range[1]})")
            idx = input("Map number: ")
            if idx.isdigit() and 1 <= int(idx) <= len(current_maps):
                map_name = list(current_maps.keys())[int(idx) - 1]
                level_range = current_maps[map_name]["level_range"]
                if pet.level < level_range[0]:
                    print(
                        f"⚠️ Warning: Your pet's level ({pet.level}) is below the recommended minimum ({level_range[0]}) for this map. This will be very difficult!")
                elif pet.level > level_range[1]:
                    print(
                        f"⚠️ Warning: Your pet's level ({pet.level}) is above the recommended maximum ({level_range[1]}) for this map. Experience and gold rewards will be significantly reduced.")
                confirm = input("Continue entering? (y/n) ")
                if confirm.lower() == 'y':
                    try:
                        monster = generate_monster(map_name, pet.level)
                        battle(pet, monster)
                    except KeyError:
                        print("Invalid map selection.")
        elif choice == "2":
            print(f"{pet.name} Lv.{pet.level} ({pet.pet_type})")
            print(f"HP: {pet.hp}/{pet.max_hp}  Attack: {pet.attack}  Defense: {pet.defense}  Speed: {pet.speed}")
            print(f"Experience: {pet.exp}/12  Gold: {pet.gold}")
            print(f"Skills: {[s.name for s in pet.skills]}")
            print(f"Items: {pet.items if pet.items else 'None'}")
        elif choice == "3":
            shop(pet)
        elif choice == "4":
            save_game(pet)
        elif choice == "5":
            print("Thanks for playing!")
            break
        else:
            print("Invalid input")

if __name__ == "__main__":
    main()