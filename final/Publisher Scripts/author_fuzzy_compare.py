import string
from whoswho import who
from thefuzz import fuzz


def check_same_person(list1, list2):
    """Check if names in two lists refer to the same persons."""
    pub_lost_boys = []
    wos_lost_boys = []

    for name1, name2 in zip(list1, list2):
        match, match2 = get_match_ratios(name1, name2)
        if match < 50 and match2 < 50:
            name2_modified = modify_name_format(name2)
            match, match2 = get_match_ratios(name1, name2_modified)
            if match < 50 and match2 < 50:
                if not check_longest_word(name1, name2_modified):
                    pub_lost_boys.append(name1)
                    wos_lost_boys.append(name2_modified)

    return lost_boys_search(pub_lost_boys, wos_lost_boys)


def lost_boys_search(lost_boys1, lost_boys2):
    final_lost_boys1 = lost_boys1
    final_lost_boys2 = lost_boys2

    to_remove1 = []
    to_remove2 = []

    for boy1 in lost_boys1:
        for boy2 in lost_boys2:
            match, match2 = get_match_ratios(boy1, boy2)

            if (match > 50 or match2 > 50) or check_longest_word(boy1, boy2):
                to_remove1.append(boy1)
                to_remove2.append(boy2)

    for name in to_remove1:
        if name in final_lost_boys1:
            final_lost_boys1.remove(name)

    for name in to_remove2:
        if name in final_lost_boys2:
            final_lost_boys2.remove(name)

    return final_lost_boys1, final_lost_boys2


def get_match_ratios(name1, name2):
    match = who.ratio(name1, name2)
    match2 = fuzz.token_sort_ratio(name1, name2)
    return match, match2


def modify_name_format(name):
    name = name.replace(".", " ").replace("  ", " ")
    modified_name = ''
    name += ' '
    if not name.isupper():
        for i in range(len(name) - 1):
            if name[i].isupper() and ((name[i + 1].isupper()) or (name[i + 1] == " ")):
                modified_name += name[i] + '.' + ' '
            else:
                modified_name += name[i]
    else:
        modified_name = name
    return modified_name.strip()


def check_longest_word(name1, name2):
    name2 = name2.translate(str.maketrans('', '', string.punctuation))
    name2_list = name2.split()
    longest_word = max(name2_list, key=len)
    name1 = name1.replace(" ", "")
    if longest_word.lower() in name1.lower():
        return True
    else:
        return False

