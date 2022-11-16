import uvicorn


if __name__ == "__main__":
    config = uvicorn.Config("apis:app", port=8080, log_level="info",reload='true')
    server = uvicorn.Server(config)
    server.run()