import pickle
import os
# import pkg_resources


class Pianpan(object):
    def __init__(self):
        # self.path = pkg_resources.resource_filename(__name__, "data.pkl")
        # self.path = os.getcwd() + '/data.pkl'
        self.path = os.path.dirname(__file__) + '/data.pkl'
        with open(self.path, 'rb') as f:
            self.data = pickle.load(f)

    def toPianpan(self, input_char):
        if input_char in self.data:
            result = ''
            results = self.data.get(input_char)
            for i in results[0]:
                result += i
        else:
            result = input_char
        return result

#
# if __name__ == "__main__":
#     pp = Pianpan()
#     c = '里'
#     a = '你'
#     result = pp.toPianpan(a)
#
#     print(result)