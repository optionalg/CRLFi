#!/usr/bin/python3

from termcolor import colored
from urllib.parse import urlparse
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor

from lib.Functions import request_to_try, starter, ColorObj
from lib.Globals import payloads, to_try
from lib.PathFunctions import PathFunction
from lib.PayloadGen import PayloadGenerator

parser = ArgumentParser(description=colored("CRLFi Finding Tool", color='yellow'), epilog=colored("Enjoy bug hunting",color='yellow'))
group = parser.add_mutually_exclusive_group()
group.add_argument('---', '---', action="store_true", dest="stdin", help="Read from stdin")
parser.add_argument('-d', '--domain', type=str, help="Domain")
group.add_argument('-w', '--wordlist', type=str, help="Absolute path of input file")
parser.add_argument('-oD', '--output-directory', type=str, help="Output file directory")
parser.add_argument('-t', '--threads', type=int, help="No of threads")
parser.add_argument('-b', '--banner', action="store_true", help="Print banner and exit")
argv = parser.parse_args()

input_wordlist = starter(argv)
FPathApp = PathFunction()
PayloaderApp = PayloadGenerator()
if argv.domain:
    PayloaderApp.set_error_page(argv.domain)

def async_generator(url: str):
    global to_try
    parsed_url = urlparse(FPathApp.urler(url))
    try:
        if parsed_url.query:
            print(f"{ColorObj.information} Generating query payload for: {colored(url, color='cyan')}")
            for payloads_full_url in PayloaderApp.query_generator(parsed_url, payloads):
                to_try.append(payloads_full_url)
            print(f"{ColorObj.information} Generating path payload for: {colored(url, color='cyan')}")
            for payloads_full_url in PayloaderApp.path_generator(parsed_url, payloads):
                to_try.append(payloads_full_url)
        elif parsed_url.path:
            print(f"{ColorObj.information} Generating path payload for: {colored(url, color='cyan')}")
            for payloads_full_url in PayloaderApp.path_generator(parsed_url, payloads):
                to_try.append(payloads_full_url)
        elif parsed_url.netloc:
            print(f"{ColorObj.information} Generating netloc payload for: {colored(url, color='cyan')}")
            for payloads_full_url in PayloaderApp.netloc_generator(parsed_url, payloads):
               to_try.append(payloads_full_url)
    except Exception as E:
        print(f"Error {E}, {E.__class__} failed async generator")

with ThreadPoolExecutor(max_workers=argv.threads) as Mapper:
    async_generator(argv.domain)
    try:
        Mapper.map(async_generator, input_wordlist)
    except KeyboardInterrupt:
        exit()
    except Exception as E:
        print(f"{ColorObj.bad} Error {E},{E.__class__} in Mapper")

with ThreadPoolExecutor(max_workers=argv.threads) as Submitter:
    try:
        del async_generator
        print(f"{ColorObj.good} Freeing some memory..")
        future_objects = [Submitter.submit(request_to_try, payload_to_try) for payload_to_try in to_try]
    except KeyboardInterrupt:
        print(f"{ColorObj.bad} Keyboard Interrupt detected. Aborting")
        exit()
    except Exception as E:
        print(f"{ColorObj.bad} Exception {E},{E.__class__} occured in future object!")

#output_file = open(FPathApp.slasher(argv.output_directory) + argv.domain + '.CRLFi', 'a')
    # for future_object in future_objects:
        # the_payload, is_exploitable = future_object.result()
        # if is_exploitable:
            # print(f"{ColorObj.good} Yes, the url is exploitable;Payload: {the_payload}")
        # output_file.write("Exploitable:{}, Payload:{}\n".format(is_exploitable, the_payload))
        # continue
#     output_file.close()
