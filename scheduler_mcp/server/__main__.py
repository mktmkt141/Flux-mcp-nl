from scheduler_mcp.server.app import create_server


def main():
    server = create_server()
    server.run(transport="http", host="0.0.0.0", port=8090, path="/mcp")


if __name__ == "__main__":
    main()

