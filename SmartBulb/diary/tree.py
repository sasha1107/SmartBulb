import pandas as pd
import re
import numpy as np
from ckonlpy.tag import Twitter
from soynlp.hangle import jamo_levenshtein
import random
from pathlib import Path
import sys
import warnings
import os

warnings.filterwarnings("ignore")
BASE_DIR = Path(__file__).resolve().parent.parent
filename3 = os.path.join(BASE_DIR, 'diary', 'SentiWord_Dict.txt')
sys.setrecursionlimit(10**7)
sent_dict = ""
twitter = Twitter()
pos_list = []
neg_list = []
pos_head = ['pos_head', 1.53]
neg_head = ['neg_head', -1.48]
pos_tree = ""
neg_tree = ""


def sim(s1, s2):
    length = max(len(s1), len(s2))
    si = jamo_levenshtein(s1, s2)/ length
    return si


def load_sent_dict():
    global sent_dict
    sent_d = pd.read_csv(filename3, sep='\t', header=None)
    sent_d = sent_d.dropna()
    df_sorted = sent_d.sort_values(by=1, ascending=False)
    df_list = df_sorted.values.tolist()
    df_list = df_list[:9000]
    sent_dict = df_list


class BstNode:
    def __init__(self, li):
        self.li = li
        self.word = li[0]
        self.num = li[1]
        self.right = None
        self.left = None

    def insert(self, li):
        if self.word == li[0]:
            return
        elif self.num < li[1]:
            if self.right is None:
                self.right = BstNode(li)
            else:
                self.right.insert(li)
        else:
            if self.left is None:
                self.left = BstNode(li)
            else:
                self.left.insert(li)

    def display(self):
        lines, *_ = self._display_aux()
        for line in lines[:100]:
            print(line)

    def _display_aux(self):
        """Returns list of strings, width, height, and horizontal coordinate of the root."""
        # No child.
        if self.right is None and self.left is None:
            line = '%s' % self.li
            width = len(line)
            height = 1
            middle = width // 2
            return [line], width, height, middle

        # Only left child.
        if self.right is None:
            lines, n, p, x = self.left._display_aux()
            s = '%s' % self.li
            u = len(s)
            first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s
            second_line = x * ' ' + '/' + (n - x - 1 + u) * ' '
            shifted_lines = [line + u * ' ' for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, n + u // 2

        # Only right child.
        if self.left is None:
            lines, n, p, x = self.right._display_aux()
            s = '%s' % self.li
            u = len(s)
            first_line = s + x * '_' + (n - x) * ' '
            second_line = (u + x) * ' ' + '|' + (n - x - 1) * ' '
            shifted_lines = [u * ' ' + line for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, u // 2

        # Two children.
        left, n, p, x = self.left._display_aux()
        right, m, q, y = self.right._display_aux()
        s = '%s' % self.li
        u = len(s)
        first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s + y * '_' + (m - y) * ' '
        second_line = x * ' ' + '/' + (n - x - 1 + u + y) * ' ' + '|' + (m - y - 1) * ' '
        if p < q:
            left += [n * ' '] * (q - p)
        elif q < p:
            right += [m * ' '] * (p - q)
        zipped_lines = zip(left, right)
        lines = [first_line, second_line] + [a + u * ' ' + b for a, b in zipped_lines]
        return lines, n + m + u, max(p, q) + 2, n + u // 2


def bfs(root, new_word):
    # Base Case
    if root is None:
        return
    # Create an empty queue
    # for level order traversal
    queue = []

    # Enqueue Root and initialize height
    queue.append(root)

    while len(queue) > 0:

        word1 = queue[0].word
        score = sim(word1, new_word)
        if score <= 0.9:
            # print(word1)
            new_num = queue[0].num
            return [new_word, new_num]

        node = queue.pop(0)

        # Enqueue left child
        if node.left is not None:
            queue.append(node.left)

        # Enqueue right child
        if node.right is not None:
            queue.append(node.right)


def set_tree():
    global pos_tree, pos_head, neg_tree, neg_tree, sent_dict
    pos_tree = BstNode(pos_head)
    neg_tree = BstNode(neg_head)

    for i in range(0, 8000 + 1):
        if sent_dict[i][1] >= 0:
            pos_tree.insert(sent_dict[i])
        else:
            neg_tree.insert(sent_dict[i])


def text_preprocess(x):
    text = []
    a = re.sub('[^가-힣0-9a-zA-Z\\s]', '', x)
    for j in a.split():
        text.append(j)
    return ' '.join(text)


def tokenize(x):
    global twitter
    text = []
    tokens = twitter.pos(x)
    for token in tokens:
        if token[1] == 'Adjective' or token[1] == 'Noun' or token[1] == 'Verb':
            text.append(token[0])
    return text


def set_sent_list():
    global sent_dict, pos_list, neg_list
    for i in range(len(sent_dict)):
        if sent_dict[i][1] >= 0:
            pos_list.append(sent_dict[i])
        else:
            neg_list.append(sent_dict[i])


def posneg_decision(new_word):
    rand_num = 200
    pos_words = []
    neg_words = []
    pos_score = 0
    neg_score = 0

    for i in range(rand_num):
        idx = random.randint(0, 40)
        pos_words.append(pos_list[idx])

    for i in range(rand_num):
        idx = random.randint(0, 60)
        neg_words.append(neg_list[idx])

    for i in range(rand_num):
        score = sim(pos_words[i][0], new_word)
        pos_score += score

    for i in range(rand_num):
        score = sim(neg_words[i][0], new_word)
        neg_score += score

    if pos_score <= neg_score:
        return 'positive'
    else:
        return 'negative'


def get_sentiment(new_sent):
    sent_words = tokenize(text_preprocess(new_sent))
    new_li = []
    sum = 0
    for i in range(len(sent_words)):
        pos_or_neg = posneg_decision(sent_words[i])
    if pos_or_neg == 'positive':
        new_node = bfs(pos_tree, sent_words[i])
        sum += new_node[1]
        new_li.append(new_node)
    else:
        new_node = bfs(neg_tree, sent_words[i])
        sum += new_node[1]
        new_li.append(new_node)
    try:
        avr = sum/len(new_li)
    except ZeroDivisionError:
        return

    if -2 <= avr < -0.2:
        return '부정'
    elif 2 >= avr > 0.2:
        return '긍정'
    else:
        return '중립'


def new_insert(new_sent):
    sent_words = tokenize(text_preprocess(new_sent))
    new_li =[]
    sum = 0
    for i in range(len(sent_words)):
        pos_or_neg = posneg_decision(sent_words[i])
        if pos_or_neg == 'positive':
            new_node = bfs(pos_tree, sent_words[i])
            sum += new_node[1]
            new_li.append(new_node)
            pos_tree.insert(new_node)
        else:
            new_node = bfs(neg_tree, sent_words[i])
            sum += new_node[1]
            new_li.append(new_node)
            neg_tree.insert(new_node)


load_sent_dict()
set_tree()
set_sent_list()
