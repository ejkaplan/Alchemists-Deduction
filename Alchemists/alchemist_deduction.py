from copy import deepcopy


def potion(alc_a, alc_b):
    """
    Determines the result of mixing two alchemics
    
    Args:
        alc_a (str): the first alchemic being mixed
        alc_b (str): the second alchemic being mixed
        
    Returns:
        str: the potion created, which will be of the form [color][sign], like "R+" or "G-".
            might also be "N" if neutral
    """
    for i in range(3):
        a = alc_a[2 * i:2 * i + 2]
        b = alc_b[2 * i:2 * i + 2]
        if a[0] != b[0] and a[1] == b[1]:
            return f"{a[0].upper()}{a[1]}"
    return "N"


def valid(alc_a, alc_b, result):
    """
    Evaluates if a given result is a possible combination of two (potentially incomplete) alchemics.

    Args:
        alc_a (str): The first alchemic, with _ substituted for unknown parts.
        alc_b (str): Second alchemic, same format
        result (str): The result, of the form [color][sign], like "R+" or "G-" or "N"

    Returns:
        bool: Whether or not this pair of alchemics could possibly create the result
    """
    result = result.upper()
    if result == "N":
        poss = ["N"]
    else:
        sign = result[-1]
        colors = result[:-1]
        if len(colors) == 0:
            colors = "RGB"
        poss = [f"{c}{sign}" for c in colors]
    for r in poss:
        if potion(alc_a, alc_b) == r:
            return True
    return False


def reverse_caps(string):
    return string.lower() if string.isupper() else string.upper()


alchemics = ["r-g+B-", "r+g-B+", "r+G-b-", "r-G+b+", "R-g-b+", "R+g+b-", "R+G+B+", "R-G-B-"]
ingredients = ["mushroom", "fern", "toad", "claw", "flower", "mandrake", "scorpion", "feather"]


# noinspection SpellCheckingInspection
class AlchemistsGame(object):

    def __init__(self):
        self.ingredients = {ing: alchemics.copy() for ing in ingredients}
        self.data = []
        self.done = False

    def potion(self, ing_a, ing_b, result):
        """
        Adds the fact that you mixed a potion with a particular result to the log
        
        Args:
            ing_a (str): The name of the first ingredient
            ing_b (str): The name of the second ingredient
            result (str): The result of the form [color][sign], like "R+" or "G-" or "N"
        """
        if ing_a not in ingredients or ing_b not in ingredients:
            raise Exception("Invalid potion")
        exp = ("potion", ing_a, ing_b, result.upper())
        self.data.append(exp)
        self.deduction()

    def periscope(self, ing, result):
        """
        Adds the fact that you peeked at a potion with the periscope to the log
        
        Args:
            ing (str): The name of the ingredient
            result (str): The result of the form [color][sign], like "R+" or "G-" or "N"
        """
        if ing not in ingredients:
            raise Exception("Invalid use of periscope")
        exp = ("periscope", ing, result.upper())
        if exp[2] == "N":
            return
        self.data.append(exp)
        self.deduction()

    def book(self, ing, result):
        """
        Adds the fact that you read a book to the log
        
        Args:
            ing (str): The name of the ingredient
            result (str): "moon" or "sun" depending on what the book said
        """
        self.data.append(("book", ing, 0 if result == "moon" else 1))
        self.deduction()

    def golem(self, ing, ears, chest):
        """
        Adds the fact that you tested the golem to the log
        
        Args:
            ing (str): The ingredient you tested on the golem
            ears (bool): Whether or not the ears steamed
            chest (bool): Whether or not the chest glowed
        """
        exp = ("golem", ing, ears, chest)
        self.data.append(exp)
        self.deduction()

    def known(self, ing):
        """
        Assembles what I know about an ingredient, with underscores in the remaining positions.
        That is, if all possible alchemics for mandrake have a small red element and a minus in the green position,
        but nothing else is consistent, this will give back "r__-__"
        
        Args:
            ing (str): The ingredient to assemble an alchemic string about
            
        Returns:
            str: A string representing the things I know with 100% certainty about the ingredient
        """
        out = list(self.ingredients[ing][0])
        for alc in self.ingredients[ing]:
            for i in range(len(out)):
                if alc[i] != out[i]:
                    out[i] = "_"
        return "".join(out)

    def known_golem(self):
        """
        Assembles what I know about the golem.
        
        Returns:
            Two lists - a list of molecules that might cause the ears to steam and the molecules
            that might cause the chest to glow. Uppercase/lowercase indicates whether it's a
            big element or a small one.
        """
        poss_ears = list("RrGgBb")
        poss_chest = list("RrGgBb")
        for ing in ingredients:
            k = self.known(ing)
            for c in "RrGgBb":
                rev_c = reverse_caps(c)
                if c in k:
                    if self.golem_ears[ing] and rev_c in poss_ears:
                        poss_ears.remove(rev_c)
                    elif not self.golem_ears[ing] and c in poss_ears:
                        poss_ears.remove(c)
                    if self.golem_chest[ing] and rev_c in poss_chest:
                        poss_chest.remove(rev_c)
                    elif not self.golem_chest[ing] and c in poss_chest:
                        poss_chest.remove(c)
        if len(poss_ears) == 1 and poss_ears[0] in poss_chest:
            poss_chest.remove(poss_ears[0])
        if len(poss_chest) == 1 and poss_chest[0] in poss_ears:
            poss_ears.remove(poss_chest[0])
        return poss_ears, poss_chest

    def animate_golem(self):
        """
        Aggregates everything I know to make a list of ingredients that might animate the
        golem. Once this is down to just 2 ingredients, you're ready to animate!
        
        Returns:
            A list of strings of the names of the ingredients that could animate the golem.
        """
        ears, chest = self.known_golem()
        ears = [f"{x.lower()}{'+' if x.isupper() else '-'}" for x in ears]
        chest = [f"{x.lower()}{'+' if x.isupper() else '-'}" for x in chest]
        poss_alc = []
        for alc in alchemics:
            alc = alc.lower()
            ear_flag, chest_flag = False, False
            for e in ears:
                if e in alc:
                    ear_flag = True
                    break
            for c in chest:
                if c in alc:
                    chest_flag = True
                    break
            if ear_flag and chest_flag:
                poss_alc.append(alc)
        poss_ing = []
        for ing in self.ingredients:
            for alc in self.ingredients[ing]:
                alc = alc.lower()
                if alc in poss_alc:
                    poss_ing.append(ing)
                    break
        return poss_ing

    def reset(self):
        self.ingredients = {ing: alchemics.copy() for ing in ingredients}

    def __str__(self):
        out = "".join(
            [f"{ing:>8}: {self.known(ing)} ({', '.join(self.ingredients[ing])})\n" for ing in self.ingredients])
        ears, chest = self.known_golem()
        out += f"ears: {''.join(ears)}\nchest: {''.join(chest)}\n"
        out += f"animate: {', '.join(self.animate_golem())}\n"
        return out

    def deduction(self, ingredients=None):
        """
        Performs as much deduction as is possible based on the data that has been entered into the log
        (see previous functions for how to enter information to the log)
        Doesn't return anything, just stores the information to instance variables.
        """
        if not ingredients:
            ingredients = self.ingredients
        self.golem_ears = {ing: None for ing in ingredients}
        self.golem_chest = {ing: None for ing in ingredients}
        while True:
            original = ingredients
            ingredients = deepcopy(original)
            # Check all the data
            for exp in self.data:
                if exp[0] == "potion":
                    # For each potion I've mixed, eliminate all alchemics for each ingredient
                    # That couldn't possibly mix to make this potion.
                    a_possible = set([])
                    b_possible = set([])
                    for a in ingredients[exp[1]]:
                        for b in ingredients[exp[2]]:
                            if a == b:
                                continue
                            if valid(a, b, exp[3]):
                                if a not in a_possible:
                                    a_possible.add(a)
                                if b not in b_possible:
                                    b_possible.add(b)
                    ingredients[exp[1]] = list(a_possible)
                    ingredients[exp[2]] = list(b_possible)
                elif exp[0] == "book":
                    # For each book I've read, eliminate alchemics that don't match what the book told me.
                    possible = set([])
                    for alc in ingredients[exp[1]]:
                        if alc.count("+") % 2 == exp[2]:
                            possible.add(alc)
                    ingredients[exp[1]] = list(possible)
                elif exp[0] == "periscope":
                    # For each ingredient i've spied, eliminate inconsistent alchemics
                    possible = set([])
                    for alc in ingredients[exp[1]]:
                        if exp[2] in alc.upper():
                            possible.add(alc)
                    ingredients[exp[1]] = list(possible)
                elif exp[0] == "golem":
                    # Register the golem experiments to be dealt with later
                    self.golem_ears[exp[1]] = exp[2]
                    self.golem_chest[exp[1]] = exp[3]
            # Deal with the golem
            ears, chest = self.known_golem()
            ear_poss = {ing: set([]) for ing in ingredients}
            chest_poss = {ing: set([]) for ing in ingredients}
            # Figure out what ingredients could possibly cause the ear and chest reactions
            for e in ears:
                for ing in ingredients:
                    if self.golem_ears[ing] is None:
                        ear_poss[ing] = set(ingredients[ing])
                    else:
                        for alc in ingredients[ing]:
                            if (e if self.golem_ears[ing] else reverse_caps(e)) in alc:
                                ear_poss[ing].add(alc)
            for c in chest:
                for ing in ingredients:
                    if self.golem_chest[ing] is None:
                        chest_poss[ing] = set(ingredients[ing])
                    else:
                        for alc in ingredients[ing]:
                            if (c if self.golem_chest[ing] else reverse_caps(c)) in alc:
                                chest_poss[ing].add(alc)
            # If an ingredient caused a given reaction, eliminate alchemics that are inconsistent with that reaction
            for ing in ingredients:
                ingredients[ing] = list(ear_poss[ing].intersection(chest_poss[ing]))
            # Deal with ingredients that have been ruled down to 1 alchemic
            for ing in ingredients:
                if len(ingredients[ing]) != 1:
                    continue
                alc = ingredients[ing][0]
                for other in ingredients:
                    if ing == other:
                        continue
                    if alc in ingredients[other]:
                        ingredients[other].remove(alc)
            # Deal with alchemics that have been ruled down to 1 ingredient
            for alc in alchemics:
                c = [i for i in ingredients if alc in ingredients[i]]
                if len(c) == 1 and len(ingredients[c[0]]) > 1:
                    ingredients[c[0]] = [alc]
            for ing in ingredients:
                ingredients[ing].sort(key=lambda x: alchemics.index(x))
            # If there has been a change, update. If not, we won't find anything else and end the loop.
            if original != ingredients:
                self.ingredients = ingredients
            else:
                break

    def play(self):
        """
        Runs the game with a text-based interface.
        """
        print("Welcome to the Alchemists deduction engine.")
        while not self.done:
            print("----")
            print(self)
            self.main_menu()

    def main_menu(self):
        options = {"p": self.potion_menu, "g": self.golem_menu, "e": self.book_menu,
                   "s": self.periscope_menu, "h": self.history_menu, "q": self.quit_menu}
        print("[P]otion")
        print("[G]olem")
        print("[E]ncyclopaedia")
        print("Peri[s]cope")
        print("[H]istory")
        print("[Q]uit")
        choice = ""
        while len(choice) == 0 or choice[0] not in options:
            choice = input("What will you do?\n").lower()
        try:
            options[choice[0]]()
        except:
            print("Whoops - looks like you did something wrong.")

    def quit_menu(self):
        choice = input("Are you sure that you want to quit? (y/n)\n")
        if choice[0].lower() == "y":
            print("Bye!")
            self.done = True

    def potion_menu(self):
        print("Enter the numbers of your two ingredients separated by a space.")
        for i in range(len(ingredients)):
            print(f"{i}) {ingredients[i]}")
        stuff = [ingredients[int(x)] for x in input().split(" ")]
        result = input(f"What was the result of mixing {stuff[0]} and {stuff[1]}?\n"
                       f"Give your result in the form [color][sign] (eg G+ for green positive) or N if you made the neutral potion.\n")
        self.potion(stuff[0], stuff[1], result)

    def golem_menu(self):
        print("Enter the number of the ingredient you fed the golem.")
        for i in range(len(ingredients)):
            print(f"{i}) {ingredients[i]}")
        ing = ingredients[int(input())]
        ears = input(f"Did {ing} make the ears steam? (y/n)\n").lower()[0] == "y"
        chest = input(f"Did {ing} make the chest glow? (y/n)\n").lower()[0] == "y"
        self.golem(ing, ears, chest)

    def book_menu(self):
        print("Enter the number of the ingredient you looked up.")
        for i in range(len(ingredients)):
            print(f"{i}) {ingredients[i]}")
        ing = ingredients[int(input())]
        sign = "moon" if input(f"Was {ing} aligned with the [M]oon or [S]un?\n").lower()[0] == "m" else "s"
        self.book(ing, sign)

    def periscope_menu(self):
        print("Enter the number of the ingredient you spied upon.")
        for i in range(len(ingredients)):
            print(f"{i}) {ingredients[i]}")
        ing = ingredients[int(input())]
        result = input(f"What potion did your victim make using {ing}?\n")
        self.periscope(ing, result)

    def history_menu(self):
        print(
            "Here are all the things you've done. If you'd like to delete one, enter the number. Otherwise press enter.")
        for i in range(len(self.data)):
            print(f"{i}) {self.stringify_experiment(self.data[i])}")
        action = input()
        if len(action) == 0:
            return
        else:
            self.data.pop(int(action))
            self.reset()
            self.deduction()

    @staticmethod
    def stringify_experiment(exp):
        if exp[0] == "potion":
            return f"Mixed {exp[1]} and {exp[2]} to make {exp[3]}"
        elif exp[0] == "book":
            return f"Looked up {exp[1]} and found it to be of the {['moon', 'sun'][exp[2]]}"
        elif exp[0] == "golem":
            return f"Fed {exp[1]} to the golem and {('the ears steamed' + (' and ' if exp[3] else '')) if exp[2] else ''}{'the chest glowed' if exp[3] else ''}{'nothing happened' if not (exp[2] or exp[3]) else ''}"
        elif exp[0] == "periscope":
            return f"Spied someone using {exp[1]} to make {exp[2]}"


def main():
    game = AlchemistsGame()
    game.play()


if __name__ == "__main__":
    main()
