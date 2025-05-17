import environ
import os

env = environ.Env()

# Set the default value for the environment variable
BASE_DIR = environ.Path(__file__) - 2
APPS_DIR = BASE_DIR.path("apps")
STORAGE_DIR = BASE_DIR.path("storage")

def read_env():
    """
    Reads the .env file and sets the environment variables.
    """
    env.read_env(os.path.join(BASE_DIR.path(".env")))