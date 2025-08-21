# What this is
The "MCP client" can be thought of as two separate components
1. Session
2. LLM usage

- Handles the setup of the transportation layer (streamable http) 
- Initialization of a Client Session, which is the class that is actually
  req/res'ing to the MCP Server for things like, listing and calling tools 

The startup flow looks like this:
1. Defining our `auth` layer (`async_auth_flow` method), with the targeted
server in our configuration
2. Establishing the transport layer, which results in our read and write streams
3. Starting a new client session with the streams

# Important
The client session handles the connection to the mcp server. The
session is making the request to `list_tools` or `call_tool`, among other
things. Anything that is interacting with the MCP server goes through the
session.

The LLM is simply taking the response of `list_tools` along with the query and 
deciding if it wants to call a tool. To be clear, it does NOT call the tool. 
Instead programmatically, we parse the llm response, see what tool it wants to
call with the provided arguments and pass this to the SESSION. What the session 
responds with is then passed to LLM, which decides how to respond and THAT is
passed to the user as the output.


