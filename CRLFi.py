#!/usr/bin/python3

from termcolor import colored
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor

from lib.Engine import Engine
from lib.PathFunctions import urler
from lib.Globals import payloads, to_try, Color
from lib.Functions import starter, write_output, send_payload, parse_args

argv = parse_args()
input_wordlist = starter(argv)
Payloader = Engine()

def async_generator(url: str):
    global to_try
    parsed_url = urlparse(urler(url))
    print_generator = lambda data: print(f"{Color.information} Generating {data} for: {colored(url, color='cyan')}")
    if parsed_url.query:
        print_generator('query payload')
        try:
            for url in Payloader.query_generator(parsed_url, payloads):
                to_try.append(url)
        except Exception as E:
            print(E)
        print_generator('path payload')
        try:
            for url in Payloader.path_generator(parsed_url, payloads):
                to_try.append(url)
        except Exception as E:
            print(E)
    elif parsed_url.path:
        print_generator('path payload')
        try:
            for url in Payloader.path_generator(parsed_url, payloads):
                to_try.append(url)
        except Exception as E:
            print(E)
    elif parsed_url.netloc:
        print_generator('domain payload')
        for url in Payloader.netloc_generator(parsed_url, payloads):
            to_try.append(url)

with ThreadPoolExecutor(max_workers=argv.threads) as mapper:
    mapper.map(async_generator, input_wordlist)

with ThreadPoolExecutor(max_workers=argv.threads) as submitter:
    objects = (submitter.submit(send_payload, url) for url in to_try)
    obj = tuple(objects)
    if argv.output_directory:
        write_output(obj, filename = argv.domain, path = argv.output_directory)
    elif argv.output:
        write_output(obj, filename = argv.output)

