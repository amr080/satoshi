Flow
1. Original server starts
2. First client gets the code and becomes server
3. Second client connects to either server
4. Each instance is independent but identical
5. Network grows organically

Independence
- Self-contained code (no external dependencies)
- Base64 encoding for safe transmission
- Async handling for concurrent connections
- Automatic server creation after code receipt

How does independence work?
- Server runs continuously, listening for connections
- When a client connects, it receives the encoded program
- Client can decode and run the received code
- Each new instance becomes its own server
- This creates a chain of self-replicating servers


Original Server: Deployed by the developer.
User A's Server: Replicated by User A.
User B's Server: Replicated by User B.


Sources
- [Quine Computing](https://en.wikipedia.org/wiki/Quine_(computing))
