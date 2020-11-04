from re import findall

from lib.PathFunctions import ender
class ParamReplace:
    def __init__(self):
        pass
    
    def replacement(self, parameter: list, value: list, replace_str: str, only = None) -> list:
        c_counter  = []
        returner_list = []
        counter = 0
        length = len(parameter)
        while counter != length:
            parameter_temporary_value = value[counter]
            for i in range(length):
                value[counter] = replace_str
                c_counter.append(parameter[i] + '=' + value[i])
            returner_list.append(c_counter)
            value[counter] = parameter_temporary_value
            counter += 1
            c_counter = []
        return returner_list
    
    def only_replacement(self, parameter: list, value: list, replace_str: str, only: list) -> list:
        returner_list = []
        c_counter  = []
        counter = 0
        length = len(parameter)
        while counter != length:
            parameter_temporary_value = value[counter]
            for index in range(length):
                value[counter] = replace_str
                if parameter[index] in only:
                    c_counter.append(parameter[index] + '=' + value[index])
            returner_list.append(c_counter)
            value[counter] = parameter_temporary_value
            counter += 1
            c_counter = []
        #c_counter = []
        #for x in returner_list:
        #    if replace_str in [y.split('=')[-1] for y in x]:
        #        c_counter.append(x)
        return [x for x in returner_list if replace_str in [y.split('=')[-1] for y in x]]
        #return c_counter

    def generate_url(self, half_url: str, parameters: list) -> list:
        return [ender(half_url, '?') + '&'.join(parameter) for parameter in parameters]

    def expand_parameter(self, query_data: str) -> tuple:
        p,q = [],[]
        for parameters,values in findall(r'([^&]+)=([^&]+)', query_data):
            p.append(parameters)
            q.append(values)
        if len(p) != len(q):
            return False, False
        return p, q

    def auto(self, upto_path_url, parameter_to_expand, payload):
        parameter, value = self.expand_parameter(parameter_to_expand)
        xpath = self.replacement(parameter, value, payload)
        ypath = self.generate_url(upto_path_url, xpath)
        return ypath
