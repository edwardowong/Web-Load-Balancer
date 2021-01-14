# Web-Load-Balancer
A web load balancer made in Python that directs clients to the fastest open server

INSTRUCTIONS:
1. run server.py (as many as you want)
2. run balancer.py {server ip}:{server port} {server2 ip}:{server2 port} ...
3. run client.py

enter the balancer's address when prompted in client.py
the balancer.py specifically uses 'test.txt' to test out the server performance, so please have 'test.txt' in the server!
