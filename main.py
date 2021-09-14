#coding=utf-8

import sys
import copy
import re
from pypinyin import lazy_pinyin, pinyin, Style
from pianpan import Pianpan


def word_all_chinese(word):
    for ch in word:
        if not '\u4e00' <= ch <= '\u9fa5':
            return False
    return True


def get_comb(word, py_word, sx_word, cur_list, new_keyword, lev):
    if lev == len(word):
        new_keyword.append(cur_list)
        # print(new_keyword)
        return
    for i in range(3):
        if i == 0:
            get_comb(word, py_word, sx_word, cur_list + [word[lev]], new_keyword, lev + 1)
        elif i == 1:
            get_comb(word, py_word, sx_word, cur_list + [py_word[lev]], new_keyword, lev + 1)
        elif i == 2:
            get_comb(word, py_word, sx_word, cur_list + [sx_word[lev]], new_keyword, lev + 1)
    return


class DFA:

    def __init__(self, keyword_list: list):
        self.state_event_dict = self._generate_state_envent_dict(keyword_list)
        self.ass_even_dict = self._generate_ass_event_dict(keyword_list)
        self.total = 0
        self.line = 1

    # 构建主状态存储结构
    @staticmethod
    def _generate_state_envent_dict(keyword_list: list) -> dict:
        state_event_dict = {}

        for keyword in keyword_list:
            if word_all_chinese(keyword):
                py = lazy_pinyin(keyword)
                sx = pinyin(keyword, style=Style.FIRST_LETTER)
                py_word = [item for item in py]
                sx_word = [item[0] for item in sx]
                new_keyword = []
                get_comb(keyword, py_word, sx_word, [], new_keyword, 0)

            else:
                new_keyword = [keyword]

            for chars in new_keyword:
                length = len(chars)
                current_dict = state_event_dict
                for index, ch in enumerate(chars):
                    if '\u4e00' <= ch <= '\u9fa5':
                        ch = lazy_pinyin(ch)[0]
                        if ch not in current_dict:
                            next_dict = {'is_end': False}
                            current_dict[ch] = next_dict
                            current_dict = next_dict
                        else:
                            next_dict = current_dict[ch]
                            current_dict = next_dict
                    else:
                        for c in ch:
                            if c not in current_dict:
                                next_dict = {'is_end': False}
                                current_dict[c] = next_dict
                                current_dict = next_dict
                            else:
                                next_dict = current_dict[c]
                                current_dict = next_dict
                    if index == length - 1:
                        current_dict["is_end"] = keyword

        return state_event_dict

    # 构建辅助状态存储结构（偏旁转换）
    @staticmethod
    def _generate_ass_event_dict(keyword_list: list):
        ass_dict = {}

        pp = Pianpan()

        for keyword in keyword_list:
            if '\u4e00' <= keyword <= '\u9fa5':
                for char_word in keyword:

                    pianpan_char = pp.toPianpan(char_word)
                    current_dict = ass_dict
                    pianpan_len = len(pianpan_char)
                    for index, c in enumerate(pianpan_char):
                        if c not in current_dict:
                            next_dict = {'is_end': False}
                            current_dict[c] = next_dict
                            current_dict = next_dict
                        else:
                            next_dict = current_dict[c]
                            current_dict = next_dict
                        if index == pianpan_len - 1:
                            current_dict['is_end'] = lazy_pinyin(char_word)[0]

        return ass_dict

    # 状态匹配函数
    def match(self, content: str):
        match_list = []  # 匹配完成加入该列表
        state_list = []  # 主状态列表
        finish_flag = True  # 状态完成标志
        ass_dict = {}  # 辅助状态列表
        ass_str = ''
        ass_flag = False
        ass_str_flag = False
        temp_match_list = []  # 匹配进度暂存列表
        temp_list = []  # 回溯状态列表
        temp_match_list = []  # 匹配进度暂存列表

        type = 0  # 字符类型 0其他 1中文 2英文
        last_word = 0  # 已读入的最后一个字符 0其他 1中文 2英文

        for char_pos, char in enumerate(content):
            type = 0
            if '\u4e00' <= char <= '\u9fa5':
                type = 1
            elif 'a' <= char <= 'z' or 'A' <= char <= 'Z':
                type = 2
            temp_char = lazy_pinyin(char.lower())[0]  # 小写处理，拼音化处理
            if char == '\n':
                self.line += 1

            if char in self.ass_even_dict:
                ass_dict = self.ass_even_dict
                temp_list = []
                ass_str = ''

            if char in ass_dict:
                ass_flag = True
                ass = ass_dict[char]
                ass_dict = ass
                ass_str += char
                if ass_dict['is_end'] is not False:
                    ass_flag = False
                    ass_str_flag = True
                    temp_char = ass_dict['is_end']
                    ass_dict = self.ass_even_dict
                    if len(temp_list) != 0:
                        state_list = temp_list
                        temp_list = []
                        temp_match_list = temp_match_list_bk
                        match_list.pop()
                        self.total -= 1
            else:
                ass_str = ''
                ass_str_flag = False
                ass_flag = False
                ass_dict = self.ass_even_dict

            if temp_char in self.state_event_dict:
                finish_flag = True
                state_list = []
                temp_match_list = []
                state_list.append(self.state_event_dict)
                temp_match_list.append({
                    "Line": self.line,
                    "match": "",
                    "word": ""
                })

            for index, state in enumerate(state_list):
                if temp_char in state:
                    state_list[index] = state[temp_char]
                    if ass_flag:
                        temp_list.append(state)  # 可能产生回溯，储存状态
                        temp_match_list_bk = copy.deepcopy(temp_match_list)
                    if ass_str_flag:
                        temp_match_list[index]["word"] += ass_str
                        last_word = 1
                        ass_str_flag = False
                        ass_str = ''
                    else:
                        temp_match_list[index]["word"] += char
                        last_word = type

                    if state[temp_char]["is_end"] is not False:
                        if not finish_flag:
                            self.total -= 1
                            match_list.pop()
                        temp_match_list[index]["match"] = state[temp_char]['is_end']
                        match_list.append(copy.deepcopy(temp_match_list[index]))
                        self.total += 1
                        last_word = 0

                        if len(state[temp_char].keys()) == 1:
                            state_list.pop(index)
                            temp_match_list.pop(index)
                            finish_flag = True
                        else:
                            finish_flag = False

                elif last_word == 1 and re.match("[\u4e00-\u9fa5]", char, re.I) is None:
                    temp_match_list[index]["word"] += char
                elif last_word == 2 and re.match("[a-zA-Z\u4e00-\u9fa5]", char, re.I) is None:
                    temp_match_list[index]["word"] += char

                # elif re.match("[a-zA-Z\u4e00-\u9fa5]", char, re.I) is None and temp_match_list[index]["word"] != '':
                #     temp_match_list[index]["word"] += char

                elif ass_flag:
                    pass
                else:
                    last_word = 0
                    finish_flag = True
                    state_list.pop(index)
                    temp_match_list.pop(index)

        return match_list


if __name__ == "__main__":
    argv_list = []
    for i in sys.argv:
        argv_list.append(i)

    f_sensitive = open(argv_list[1], encoding='utf-8')
    keyword_list = [i.strip('\n') for i in f_sensitive.readlines()]

    f_content = open(argv_list[2], encoding='utf-8')
    content = f_content.read()

    dfa = DFA(keyword_list)
    ans = dfa.match(content)
    # print(ans)
    # print(dfa.state_event_dict)
    # print(dfa.ass_even_dict)
    f_ans = open(argv_list[3], 'w', encoding='utf-8', )
    f_ans.write('Total: ' + str(dfa.total) + '\n')
    for i in ans:
        f_ans.write('Line' + str(i['Line']) + ': ' + '<' + str(i['match']) + '> ' + str(i['word']) + '\n')
    f_ans.close()