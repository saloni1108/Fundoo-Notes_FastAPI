from fastapi import FastAPI

def create_app(name):
    return FastAPI(title = name)
