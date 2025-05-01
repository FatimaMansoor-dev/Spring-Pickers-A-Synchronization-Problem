import argparse
from multiprocessing import set_start_method
import multiprocessing as mp
from util import *


def run_orchard(num_fruits, num_pickers, crate_capacity):

    ## just the printing stuff
    process_names = [f"Picker-{i}" for i in range(1, num_pickers + 1)] + ["Loader"]
    header_line = " | ".join(f"{name:^15}" for name in process_names)
    separator = "-" * len(header_line)

    resources = SharedResources(num_fruits, crate_capacity, process_names, header_line, separator)

    print(header_line)
    print(separator)

    loader = Loader(resources)
    pickers = [Picker(i, resources) for i in range(1, num_pickers + 1)]


    ## start everything
    loader.start()
    for p in pickers:
        p.start()
    for p in pickers:
        p.join()

    resources.done.value = True
    resources.full_crate_sem.release()
    loader.join()


if __name__ == "__main__":
    set_start_method('spawn') 
    parser = argparse.ArgumentParser()
    parser.add_argument("--fruits", "-f", type=int, default=26)
    parser.add_argument("--pickers", "-p", type=int, default=3)
    parser.add_argument("--capacity", "-c", type=int, default=12)
    args = parser.parse_args()
    run_orchard(args.fruits, args.pickers, args.capacity)