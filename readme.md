each process in Python’s multiprocessing lives in its own memory space. A simple attribute on the parent (or on one process) won’t be visible to the Loader process.

Here’s what that super().__init__(…) is doing:

Calling the base-class constructor
Picker inherits from multiprocessing.Process. By doing super().__init__(name=…), you’re invoking Process.__init__ under the hood. That sets up all of the plumbing that Python’s multiprocessing library needs to track and start a new process (things like its target function, its internal locks, process name, etc.).