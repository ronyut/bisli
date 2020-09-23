#!/usr/bin/env python
# coding: utf-8

# 
# <center>
#         <img src="assets/img/dbconfig.png" width="10%" height="10%" alt="imports and Excel reading and configuration">
#         <h3>Imports and Excel reading and configuration:</h3>
# </center>
# <hr>

# In[22]:


import pandas as pd
import numpy as np
import collections
import codecs, difflib, Levenshtein
import re # regex
from graphviz import Source

'''
Pandas Definitions
'''
df = pd.read_excel (r'../../docs/220819 - ALL data merged from natalia for shahar.xlsx') #(use "r" before the path string to address special character, such as '\')
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 50)

'''
DEFINITIONS
'''
# languages and their range in the excel file (column numbers)
LANGUAGES = {"hebrew": ["EL", "GO"], "russian": ["CH", "EK"]}
# vowels
VOWELS = "aeiou"
# symbols to be replaced
REPLACE_SYMBOLS =  {'ç': 'c', '"': "'", "-": " "}
# Hebrew: symbols to be removed. Don't add / because we need to remove N/A
REMOVE_SYMBOLS_RUS = "_*.,`?()"
REMOVE_SYMBOLS_HEB = REMOVE_SYMBOLS_RUS + "'"
# check for transcribers' typos in words?
CHECK_FOR_TYPOS = False
# word similarity threshold
SIMILARITY_THRESHOLD = 0.7
# inspection list of possible errors and inaccuracies
INSPECT = list()


# <center>
#         <img src="assets/img/Word_Frequency.png" width="20%" height="20%" alt="Find words frequencies">
#         <h3>Find words frequencies:</h3>
# </center>
# <hr>

# In[2]:


#heb_rep_phase_1 = {"c'":"צ", "b": "ב", "g": "ג", "d": "ד", "sh": "ש", "v": "ב/ו", "h": "ה", "z": "ז", "x": "ח", "t": "ת", "'": "ע", "y": "י", "k": "כ", "l": "ל", "m": "מ", "n": "נ", "s": "ס", "p": "פ", "q": "ק", "r": "ר"}
#heb_rep_phase_2 = {"a": "א", "e": "א", "i": "א", "o": "א", "u": "א"}

'''
repl_symbols: takes a string and removes specific symbols from it
'''
def repl_symbols(string, lang):    
    if lang == "hebrew":
        remove_symbols = REMOVE_SYMBOLS_HEB
    elif lang == "russian":
        remove_symbols = REMOVE_SYMBOLS_RUS
    
    for a, b in REPLACE_SYMBOLS.items():
        string = string.replace(a, b)
    for a in remove_symbols:
        string = string.replace(a, '')
    return string

'''
hasDigits: checks if a word has digits in it or at sign (@) which indicates that the word is innovative
'''
def hasDigits(string):
    return any(char.isdigit() for char in string)

'''
loop_freq: returns a dictionary of each word in the dataframe and its frequency (sorted by frequency DESC)
'''
def loop_freq(col, lang):
    freq = {}
    
    for row in col:
        # skip NaN cells (empty cell)
        if isinstance(row, (bool, float)) and str(row).lower() == "nan" or str(row) == "":
            continue
            
        row = str(row)
        # inspect cells with numbers
        if hasDigits(row) and "CS" not in row:
            INSPECT.append(row)
            continue
            
        split = repl_symbols(row, lang).split(' ')
        for word in split:
            # ignore marks and short words and child's mistakes (usually capitalized)
            if len(word) < 3 or "@" in word or "xx" in word or "XX" in word or word != word.lower():
                continue
            if word in freq:
                freq[word] += 1
            else:
                freq[word] = 1            

    # delete keys
    keys_del = ['CORRECT', 'n/a', 'N/A', 'N/a', 'n/A']
    for key in keys_del:
        if key in freq:
            del freq[key]

    freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    freq = collections.OrderedDict(freq)
        
    return freq


# <center>
#     <img src="assets/img/rus-il.png" width="13%" height="13%" alt="Shared functions for both languages">
#     <h3>Functions for both languages:</h3>
# </center>
# <hr>

# In[3]:


'''
isSamePair: check if a pair of strings are equal to other pair of strings
'''
def isSamePair(s1, s2, t1, t2):
    if (s1 == t1 and s2 == t2) or (s1 == t2 and s2 == t1):
        print(s1, s2, "same!")
    

'''
hasOnly: checks if a string has only specific letters
'''
def hasOnly(string, letters):
    for s in string:
        if s not in letters:
            return False
    return True

'''
comb_checks: takes two substring and two strings, and checks whether both strings contain one substring 
'''
def comb_checks(sub1, sub2, str1, str2):
    if (sub1 in str1 and sub2 in str2) or (sub1 in str2 and sub2 in str1):
        return True
    return False

'''
removeSharedLetters: takes two strings and removes common letters, i.e. letters both share
                     Note: the result of removeSharedLetters("abb", "a") is ['b'] and not ['b', 'b']
'''
def removeSharedLetters(x, y):
    count = lambda x: collections.Counter(c for c in x.lower())
    cx, cy = count(x), count(y)
    diff  = cx - cy
    rev_diff = cy - cx    
    rev_diff = list(rev_diff)
    diff = list(diff)
    
    return sorted(rev_diff + diff)

'''
isEdgeLettersSame: checks if the edge letters are the same
'''
def isEdgeLettersSame(s1, s2, exceptions):
    startOk = False
    endOk = False
    
    # if the first letter of each word aren't the same - don't merge
    if s1[0] != s2[0]:
        for c in exceptions:
            if (s1[0] == c and s2[0] in exceptions) or (s2[0] == c and s1[0] in exceptions):
                startOk = True
                break
    else:
        startOk = True
    
    # if the last letter of each word aren't the same - don't merge
    if s1[-1] != s2[-1]:
        for c in exceptions:
            if (s1[-1] == c and s2[-1] in exceptions) or (s2[-1] == c and s1[-1] in exceptions):
                endOk = True
                break
    else:
        endOk = True
    
    # return true only if start and end are okay
    if (s1[0] == s2[0] and s1[-1] == s2[-1]) or (startOk and endOk):
        return True
    else:
        return False


# <center>
#     <img src="assets/img/israel.png?v=1" width="8%" height="8%" alt="Functions for Hebrew">
#     <h3>Functions for Hebrew:</h3>
# </center>
# <hr>

# In[4]:


'''
allCombChecks: check all specific combinations 
'''
def allCombChecks(s1, s2, diff):
    # e.g. rayinu - rainu ראינו
    if comb_checks("yi", "i", s1, s2) and "y" in diff:
        return True
    
    # e.g. beyit - beyt בית
    if comb_checks("y", "yi", s1, s2) and "i" in diff:
        return True
    
    # e.g. eix - eyx
    if comb_checks("ei", "ey", s1, s2):
        return True
    
    # e.g. yihiye - hihiye
    if comb_checks("hi", "yi", s1, s2):
        return True
    
    # e.g. bayit - bayt בית
    if comb_checks("ayi", "ay", s1, s2) and "i" in diff:
        return True
    
    # e.g. yihiye yihye diff
    if comb_checks("iy", "y", s1, s2) and "i" in diff:
        return True
    
    # e.g. beyit - beit בית
    if comb_checks("eyi", "ei", s1, s2) and "y" in diff:
        return True
    
    # if h is preceded and follwed by a vowel, e.g. imahot - imaot אמהות
    if "h" in diff:
        hasH = s1 if "h" in s1 else s2
        if hasVHV(hasH):
            return True
        
    # e.g. haimahot - haimaot
    if "h" in s1 or "h" in s2:
        if (hasVHV(s1) and not hasVHV(s2)) or (hasVHV(s2) and not hasVHV(s1)):
            return True
    
    # e.g. raaa - raa ראה
    if comb_checks("aaa", "aa", s1, s2) and "a" in diff:
        return True
    
    # e.g. eyze - eyzeh, ayom - hayom
    if check_h(s1, s2):
        return True
    return False

'''
hasVHV: checks if a string has a vowel-h-vowel, e.g. imAHOt
'''
def hasVHV(string):
    return bool(re.search("["+ "".join(VOWELS) +"]h[" + "".join(VOWELS) + "]", string))

'''
isNikud: checks if a letter is a vowel
'''
def isNikud(letter):
    if letter in VOWELS:
        return True
    return False

'''
check_h: take two words and checks if there's h in the beginning or ending of one word that is preceeded or followed
         by a vowel, and not in the other word e.g. eyze - ezyeh, hayom - ayom
'''
def check_h(s1, s2):
    # e.g. hayom - ayom
    if (s1[0] == "h" and isNikud(s1[1]) and isNikud(s2[0])):
        return True
    # e.g. eyzeh - eyze
    if (s1[-1] == "h" and isNikud(s1[-2]) and isNikud(s2[-1])):
        return True
    # e.g. ayom - hayom
    if (s2[0] == "h" and isNikud(s2[1]) and isNikud(s1[0])):
        return True
    # e.g. eyze - eyzeh
    if(s2[-1] == "h" and isNikud(s2[-2]) and isNikud(s1[-1])):
        return True
    return False


'''
shouldMerge_heb: check if two strings are similar enough transcription-wise to be merged
'''
def shouldMerge_heb(s1, s2):
    diff = "".join(removeSharedLetters(s1, s2))
    mixes = ["chx", "hx", "kq", "kx", "hk", "chk"]
    onlyMatch = " ".join(mixes) + " yi hy hi"
    if not hasOnly(diff, onlyMatch):
        return False
    
    mixExists = False
    for mix in mixes:
        if mix in diff:
            mixExists = True
    
    # check if the strings' edges are identical
    if isEdgeLettersSame(s1, s2, "hiy") or isEdgeLettersSame(s1, s2, "ckqx") or check_h(s1, s2):
        # if their body is the same
        if s1[1:-1] == s2[1:-1]:
            return True
        elif mixExists or allCombChecks(s1, s2, diff):
            return True
    return False


# <center>
#     <img src="assets/img/russia.png" width="10%" height="10%" alt="Functions for Russian">
#     <h3>Functions for Russian:</h3>
# </center>
# <hr>

# In[5]:


'''
shouldMerge_rus: check if two strings are similar enough transcription-wise to be merged
'''
def shouldMerge_rus(s1, s2):
    diff = removeSharedLetters(s1, s2)

    # if the difference between the words is one of following leteters, then they shouldn't merge
    badLetters = "rtpsdfgklmnbvcxz" + "'" + VOWELS
    for letter in diff:
        if letter in badLetters:
            return False
    
    # edge letters must be the same in both words
    excpetionsEdge = "jy" # "y" for plural; "j": e.g. esli - jesli 
    edgesOk = isEdgeLettersSame(s1, s2, excpetionsEdge)
    if not edgesOk:
        return False
    
    join = ''.join(diff)
    # if y is not the last word (because it make the word plural), e.g. kot - koty, kust - kusty
    if "y" in join and s1[-1] != "y" and s2[-1] != "y":
        hasY = s1 if "y" in s1 else s2
        # if y is preceded by a vowel or followed by j
        if bool(re.search("["+ "".join(VOWELS) +"]y", hasY)) or "yj" in hasY:
            return True
    
    # check for j
    join = ''.join(diff)
    if "j" in join:
        return True
    
    # e.g. ego - evo
    if comb_checks("go", "vo", s1, s2) and "gv" in diff:
        return True
    
    # e.g. devocka - devochka
    if comb_checks("ck", "chk", s1, s2) and "h" in diff:
        return True
    
    return False


# <center>
#     <img src="assets/img/hamming.png" width="10%" height="10%">
#     <h3>Calculate the similarity of a pair of words and decide whether they should merge:</h3>
# </center>
# <hr>

# In[6]:


'''
shouldMerge: according to the language, apply the function that checks if two strings are similar enough
             transcription-wise to be merged
'''
def shouldMerge(capsule, lang):
    s1 = capsule[0]
    freq1 = capsule[1]
    s2 = capsule[2]
    freq2 = capsule[3]
    sim = capsule[4]
    maxLen = max(len(s1), len(s2))
    
    if not (sim >= SIMILARITY_THRESHOLD or (maxLen == 4 and sim >= 0.6) or (maxLen == 3 and sim >= 0.5)):
        return False
    
    # proceed by lanugage
    lang = lang.lower()
    if lang in "hebrew":
        return shouldMerge_heb(s1, s2)
    elif lang in "russian":
        return shouldMerge_rus(s1, s2)
    else:
        assert False

        
'''
typosStats: check for transcribers' typos in words?
            Note: we can't know if it's a typo or if it's something that the child did say.
            Thus for now I recommend defining CHECK_FOR_TYPOS = False
'''
def typosStats(capsule):
    if not CHECK_FOR_TYPOS:
        return False
    
    sim = capsule[4]
    if sim < 0.9:
        return False
    
    # frequency of word1
    freq1 = capsule[1]
    # frequency of word2
    freq2 = capsule[3]
        
    if (min(freq1, freq2) / (freq1 + freq2) <= 0.1) and min(freq1, freq2) <= 3:
        return True
    return False


'''
similar: get the similarity percentage of two words
'''
def similar(a, b, algo = "difflib"):
    if algo == "difflib":
        return difflib.SequenceMatcher(None, a, b).ratio()
    elif algo == "lev":
        return Levenshtein.ratio(a, b)
    elif algo == "sor":
        return 1 - distance.sorensen(a, b)
    elif algo == "jac":
        return 1 - distance.jaccard(a, b)

    
'''
hamming: get the hamming distance of two strings
'''
def hamming(s1, s2):
    return sum(ch1 != ch2 for ch1,ch2 in zip(s1,s2))


'''
find_sim: returns a dictionary of pairs of similar words that should be merged
'''
def find_sim(freq, lang):
    count = 0
    word_list = list(freq)
    replacements = {}
    
    for i, word in enumerate(freq):
        for j in range(i):
            word2 = word_list[j]
            # calculate similarity percentage using difflib algorithm
            sim = similar(word, word2)
            # wrap all in a capsule
            capsule = [word, freq[word], word2, freq[word2], sim]
            isSamePair(word, word2, "bayita", "baita")
            
            # check if the words should really merge
            if shouldMerge(capsule, lang):
                ##print(word, word2, freq[word], freq[word2], sim)
                replacements[word] = word2
                count += 1
    return replacements


# <center>
#     <img src="assets/img/replace.png" width="10%" height="10%" alt="Helper functions for replacing">
#     <h3 align="center">Helper functions for replacing:</h3>
# </center>
# <hr>

# In[7]:


'''
xlsColIndex: convert Excel column to index, e.g. Z -> 25 | CH -> 85
'''
def xlsColIndex(col):
    col = col.lower()
    if len(col) == 1:
        return ord(col[0]) - 97
    elif len(col) == 2:
        return (ord(col[0]) - 97 + 1) * 26 + (ord(col[1]) - 97)

'''
replaceInDataFrame: ___________
'''
def replaceInDataFrame(df, colname, replacements, lang):
    if lang == "hebrew":
        remove_symbols = REMOVE_SYMBOLS_HEB
        
    elif lang == "russian":
        remove_symbols = REMOVE_SYMBOLS_RUS
    
    # replace symbols
    for orig, rep in REPLACE_SYMBOLS.items():
        df[colname] = df[colname].str.replace(r"" + orig, rep)
    
    # remove symbols, @ marks, and XXXX
    pattern = r"[\\"+ "\\".join(remove_symbols) + r"]|@[\w\:\.\;]+|\s[Xx]{1,}$|^[Xx]{1,}\s|\s[Xx]{1,}\s"
    df[colname] = df[colname].str.replace(pattern, '')
    
    # trim and remove multiple spaces
    df[colname] = df[colname].str.strip()
    df[colname] = df[colname].str.replace("([\s]+)", ' ')
    
    # finally replace the words
    replacements = {r'\b{}\b'.format(k):v for k, v in replacements.items()}
    df[colname] = df[colname].replace(to_replace = replacements, regex=True)


# <center>
#     <img src="assets/img/start95.jpg" width="20%" height="20%" alt="Main">
#     <h1 align="center">Main</h1>
# </center>
# <hr>

# In[8]:


'''
MAIN
'''
def Main():
    # total replacements counter
    count = 0

    for lang, rang in LANGUAGES.items():

        for i in range (xlsColIndex(rang[0]), xlsColIndex(rang[1])):
            colname = df.columns[i]
            heb_data = df[colname]
            heb_freq = loop_freq(heb_data, lang)
            replacements = find_sim(heb_freq, lang)
            this_count = len(replacements)

            if this_count > 0:
                print("--------------------------")
                print(replacements)
                # update the total replacements counter
                count += this_count
                # apply replacements
                replaceInDataFrame(df, colname, replacements, lang)

    # replace NaN with blank in all rows
    df.replace(np.nan, '', regex=True, inplace=True)

    print("\nTotal replacements: " + str(count))
    ##print(df.iloc[:, 141:142].head(500))

    # print inspections
    if len(INSPECT) > 0:
        print("*** Inspect problematic cells: " + " | ".join(INSPECT))


# <center>
#     <img src="assets/img/sandbox.png" width="10%" height="10%" alt="Testing Area">
#     <h3 align="center">Testing Area</h3>
# </center>
# <hr>

# In[25]:


def testing():
    '''s = ["teh", "tey", "agilit", "hagilit", "baita", "bayita", "mesaxeket", "mesaxeqet"]
    s1 = s[4]
    s2 = s[5]
    exceptions = "hiy"
    sim = similar(s1, s2)
    print("Similarity: " + str(sim))
    print(isEdgeLettersSame(s1, s2, exceptions))
    print(check_h(s1, s2))
    print(shouldMerge_heb(s1, s2))
    print(shouldMerge([s1, 4, s2, 4, sim], "hebrew"))'''
    
    path = 'pyan-master/myuses.dot'
    s = Source.from_file(path)
    s.view()

testing()


# <center>
#     <img src="assets/img/todo.png" width="10%" height="10%" alt="To Do List">
#     <h3 align="center">To Do List</h3>
# </center>
# <hr>

# To Do:
# 1. yihiye hihiye
# 2. why <b>bayita</b> and <b>baita</b> dont show!
# 3. while no replacements run main --?
#     * better solution: make a list and every time we add to replacements dictionary, check if someone in the pair
#     already exists in the list. if it does - flip key and value.
#     * e.g: we have (1) "xatul" (2) "hatul" (3) "chatul".<br>
#     Now the list is empty so we add to dict dict[1] = 2. now list = [2].<br>
#     now we look at 2 and 3. we won't do dict[2] = 3 cuz 2 is in the list, so we'll do dict[3] = 2.<br>
#     now we have to deal with 1 and 3:<br>
#     we we'll look up each of them in dict, and see if they exist. if they do, we take their value (2) and 
