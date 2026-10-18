import importlib.util
import inspect
import json
import pathlib
import sys
import types


def install_basic_agent():
    agents_package = types.ModuleType("agents")
    agents_package.__path__ = []
    basic_agent_module = types.ModuleType("agents.basic_agent")

    class BasicAgent:
        def __init__(self, name=None, metadata=None, **kwargs):
            self.name = name
            self.metadata = metadata

    basic_agent_module.BasicAgent = BasicAgent
    sys.modules["agents"] = agents_package
    sys.modules["agents.basic_agent"] = basic_agent_module


def load_agents(path):
    install_basic_agent()
    instances = {}
    for index, source in enumerate(sorted(pathlib.Path(path).glob("*_agent.py"))):
        if source.name == "basic_agent.py":
            continue
        spec = importlib.util.spec_from_file_location(f"grail_agent_{index}", source)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for _, candidate in inspect.getmembers(module, inspect.isclass):
            if (
                candidate.__module__ != module.__name__
                or candidate.__name__ == "BasicAgent"
            ):
                continue
            instance = candidate()
            name = getattr(instance, "name", None)
            metadata = getattr(instance, "metadata", None)
            if isinstance(name, str) and isinstance(metadata, dict):
                instances[name] = instance
    return instances


def main():
    action = sys.argv[1]
    agents = load_agents(sys.argv[2])
    if action == "list":
        print(
            json.dumps(
                [
                    {"name": name, "metadata": agent.metadata}
                    for name, agent in sorted(agents.items())
                ],
                separators=(",", ":"),
            )
        )
        return
    if action != "call":
        raise ValueError(f"unknown action: {action}")

    name = sys.argv[3]
    arguments = json.loads(sys.argv[4])
    agent = agents[name]
    try:
        result = agent.perform(**arguments)
    except Exception as error:
        print(
            json.dumps(
                {"ok": False, "error": str(error)},
                separators=(",", ":"),
            )
        )
        return
    print(
        json.dumps(
            {"ok": True, "result": str(result)},
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
