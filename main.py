import sys
import copy
import re
from pypinyin import lazy_pinyin


class DFA:

    def __init__(self, keyword_list: list):
        self.state_event_dict = self._generate_state_envent_dict(keyword_list)
        self.total = 0
        self.line = 1

    @staticmethod
    def _generate_state_envent_dict(keyword_list: list) -> dict:
        state_event_dict = {}

        for keyword in keyword_list:
            current_dict = state_event_dict
            length = len(keyword)

            for index, ch in enumerate(keyword):
                char_word = lazy_pinyin(ch)[0]
                for char in char_word:
                    if char not in current_dict:
                        next_dict = {"is_end": False}
                        current_dict[char] = next_dict
                        current_dict = next_dict
                    else:
                        next_dict = current_dict[char]
                        current_dict = next_dict

                if index == length - 1:
                    current_dict["is_end"] = keyword

        return state_event_dict

    def match(self, content: str):
        match_list = []
        state_list = []
        temp_match_list = []

        for char_pos, char in enumerate(content):
            temp_word = lazy_pinyin(char.lower())[0]
            first = True
            if char == '\n':
                self.line += 1

            for temp_char in temp_word:
                if temp_char in self.state_event_dict:
                    state_list.append(self.state_event_dict)
                    temp_match_list.append({
                        "Line": self.line,
                        "match": "",
                        "word": ""
                    })

                for index, state in enumerate(state_list):
                    if temp_char in state:
                        state_list[index] = state[temp_char]
                        if first:
                            temp_match_list[index]["word"] += char
                            first = False

                        if state[temp_char]["is_end"] is not False:
                            temp_match_list[index]["match"] += state[temp_char]["is_end"]
                            match_list.append(copy.deepcopy(temp_match_list[index]))
                            self.total += 1

                            if len(state[temp_char].keys()) == 1:
                                state_list.pop(index)
                                temp_match_list.pop(index)
                    elif re.match("[a-zA-Z\u4300-\u9fa5]", char, re.I) is None and temp_match_list[index]["word"] != '':
                        temp_match_list[index]["word"] += char

                    else:
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
    f_ans = open(argv_list[3], 'w', encoding='utf-8', )
    f_ans.write('Total: ' + str(dfa.total) + '\n')
    for i in ans:
        f_ans.write('Line' + str(i['Line']) + ': ' + '<' + str(i['match']) + '> ' + str(i['word']) + '\n')
    f_ans.close()














