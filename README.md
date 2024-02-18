# feedwater

This is a simple, one-purpose python library that spawns a process with a shell command an allows you to concurrently feed data into its stdin, while being able to read its stdout and check its status.

## Rationale
Python's subprocess library is very powerful. Yet, simply starting a server program that continuously reads from standard input remained surprisingly elusive. Eventually, as I found myself delving into the mysteries of process groups to properly kill a zombie process, making repeated calls to `flush` in an act of naked desperation trying to get output without blocking my whole program, and being unable to query the status of my subprocess without wrestling with byzantine return code policies, I finally gave up. The subprocess API seemed to fight me at every turn. I realized that subprocess was simply not designed for my use case.

That's when I made feedwater.

If you
 - want to invoke another program from your python script that reads from standard input and has an indefinite lifecycle
 - want to sometimes pass data to said program
 - want to query it's output in a non-blocking way
 - want occasionally to query its status
 - want to be able to kill it and all child processes it may or may not have spawned 

then feedwater may be for you.

