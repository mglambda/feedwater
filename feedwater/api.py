import subprocess, os, signal, threading
from queue import Queue, Empty

def run(cmd):
    """Spawns a process with command CMD, executed in a shell environment in text mode. Returns a Process object. This function is non-blocking.

    Parameter
    cmd : str
    A shell command, like 'ls -la'.
    Returns
    Process
    A Process object that can be queried for execution results, errors, its status, or to write to the underlying stdin."""
    return Process(cmd)

# FIXME: in the future, add more functions that modify Process constructor arguments for e.g. binary mode, non-shell mode, etc

class Process(object):
    """A subprocess that can run continuously and provides non-blocking interactions."""

    def __init__(self, cmd):
        """Initialize and start a subprocess.

        Paramter
        cmd : str
        A string that will be executed in a shell environment, in text mode."""
        self._proc = None
        self.stderr_log = Queue()
        self.stdout_log = Queue()
        self._exit_code = None
        if type(cmd) == type([]):
            cmdstring = " ".join(cmd)
        elif type(cmd) == type(""):
            cmdstring = cmd
        else:
            raise ValueError("cmd must be a string or a list with program name + arguments.")
        
        self._cmdstring = cmdstring
        self._proc = subprocess.Popen(self._cmdstring,
                                      text=True,
                                      stdin=subprocess.PIPE,
                                      shell=True,
                                      preexec_fn=os.setsid,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)

        self._threads_stop = threading.Event()
        t1 = threading.Thread(target=self._reader, args=[self._proc.stdout, self.stdout_log])
        t2 = threading.Thread(target=self._reader, args=[self._proc.stderr, self.stderr_log])
        t1.daemon = True
        t2.daemon = True
        t1.start()
        t2.start()

        # this one is just for return code
        def f():
            if not(self._proc):
                return
            self._exit_code = self._proc.wait()
            
        t3 = threading.Thread(target=f)
        t3.daemon = True
        t3.start()
        
        
    def _reader(self, stream, q):
        while w := stream.readline():
            q.put(w)
            if self._threads_stop.isSet():
                return
            
    def write_line(self, w):
        """Like write, but adds a newline."""
        return self.write(w + "\n")
        
    def write(self, w):
        """Write data to the underlying process.
        Parameter
        w : str
        Data to be written. Note that you may need to add a newline at the end for the underlying process to properly consume the input.
        
        Returns
        bool
        True on error, otherwise False.""" 

        if self._proc is None:
            return True
        
        self._proc.stdin.flush()
        self._proc.stdout.flush()
        self._proc.stderr.flush()
        self._proc.stdin.write(w)
        self._proc.stdin.flush()
        self._proc.stderr.flush()
        self._proc.stdout.flush()
        return False

    def is_running(self):
        """Returns true if the underlying process is still running. False if it has exited."""
        if not(self._proc):
            return False

        if self._exit_code is None:
            return True
        return False

    def exit_code(self):
        """Returns the exit code of the underlying process if it has finished. Otherwise returns None."""
        return self._exit_code
    
        

    def get_error(self):
        """Returns a list of lines from the stderr of the underlying process. This will empty the stderr queue. Will return empty list if process is not running. Use is_running() to check if process is still alive.
        This function is non-blocking."""
        return self._get_queue(self.stderr_log)

    def get(self):
        """Returns a list of lines from stdout of the underlying process. This will empty the stdout queue. Returns empty list if no new output is present or if the process is not running. Use is_running to check if the underlying process is still alive.
        This function is non-blocking."""
        return self._get_queue(self.stdout_log)
    
    def _get_queue(self, q):
        if not(self._proc):
            return ""
        lines = []
        try:
            while w := q.get_nowait():
                lines.append(w)
        except Empty:
            return lines
        return lines

    def close(self):
        # since shell=true spawns child processes that may still be running , we have to terminate by sending kill signal to entire process group
        # FIXME: this doesn't work on windows
        if self._proc:
            os.killpg(os.getpgid(self._proc.pid), signal.SIGTERM)
            self._proc = None


