from requests import get
from re import search, findall
from requests.exceptions import Timeout,ConnectionError

from lib.Skipper import Skip
from lib.Globals import Color
from lib.ParamReplacer import ParamReplace
from lib.PathFunctions import merge, unstarter, urler, urlerslasher, ender, unender

class Engine:
    def __init__(self):
        self.Skipper = Skip()
        self.Replacer = ParamReplace()
        self.print_skip = lambda value: print(f"{Color.bad} Skipping some used {value}!")
    
    def query_generator(self, parsed_url, payloads: list) -> list:
        params_to_try, to_try = [], []
        upto_path, query = merge(parsed_url.netloc, parsed_url.path), parsed_url.query
        if len(query) > 500:
            return to_try
        parameters, values = self.Replacer.expand_parameter(query)
        for parameter in parameters:
            if not self.Skipper.check_parameter(upto_path, parameter):
                self.Skipper.add_parameter(upto_path, [parameter])
            else:
                self.print_skip("query"); continue 
            if not self.Skipper.check_unique_parameter(parameter):
                self.Skipper.add_unique_parameter([parameter])
            else:
                self.print_skip("query"); continue
            params_to_try.append(parameter)
        if not params_to_try:
            return to_try
        for payload in payloads:
            query_list = self.Replacer.only_replacement(parameters, values, unstarter(payload, '/'), params_to_try)
            payloads_list = self.Replacer.generate_url(upto_path, query_list)
            _ = [to_try.append(line) for line in payloads_list if line]
        return to_try

    def path_generator(self, parsed_url, payloads: list) -> list:
        to_try = []
        if parsed_url.path.count('/') == 1:
            return [line for line in self.netloc_generator(parsed_url, payloads) if line] 

        path_list = [ender(path, '/') for path in findall(r'([^/]+)', parsed_url.path)]
        path_range = range(len(path_list) -1, 0, -1)

        for index in path_range:
            return_variable = True
            before_index = path_list[index-1]
            unslashed = unender(before_index, '/')
            if self.Skipper.check_path(before_index) or search('[a-zA-Z].+[0-9]$', unslashed):
                pass
            elif search('^[0-9].*$', unslashed) and len(unslashed) >= 2:
                pass
            else:
                self.Skipper.add_path(before_index)
                return_variable = False
            if return_variable:
                self.print_skip("path")
                return to_try
            for payload in payloads:
                path_list[index] = unstarter(payload, '/')
                to_try.append(urlerslasher(parsed_url.netloc) + "".join(path_list))
            path_list.pop()
        return to_try

    def netloc_generator(self, parsed_url, payloads: list) -> list:
        return_variable = True
        if parsed_url.netloc.count('.') >= 5 or len(parsed_url.netloc) > 40 or self.Skipper.check_netloc(parsed_url.netloc):
            pass
        else:
            self.Skipper.add_netloc(parsed_url.netloc)
            return_variable = False
        if return_variable:
            self.print_skip("netloc")
            return []
        try:
            get(urler(parsed_url.netloc))
            return_variable = False
        except (ConnectionError,Timeout):
            pass
        except Exception as E:
            self.print_skip(f"netloc due to {str(E.__class__.__name__)}")
        if return_variable:
            self.print_skip("netloc")
            return []
        return [merge(parsed_url.netloc, payload) for payload in payloads if payload]
