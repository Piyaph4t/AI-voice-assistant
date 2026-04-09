import importlib
import sys
from pathlib import Path

import dotenv
import os
sys.path.append(Path(__file__).resolve().parent)
dotenv.load_dotenv()
from core.agent import Agent
agent = Agent()

