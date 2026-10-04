"""Validate and enumerate a bounded story graph without executing arbitrary code."""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORY = ROOT / "game/data/story.json"
ID = re.compile(r"^[a-z][a-z0-9_]*$")
STATE_TYPES = {"affection": int, "trust": int, "truth_known": bool}


def load_story(path=STORY):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def condition_met(when, state):
    for name, rule in when.items():
        if isinstance(rule, dict):
            if "gte" in rule and state[name] < rule["gte"]:
                return False
            if "eq" in rule and state[name] != rule["eq"]:
                return False
        elif state[name] != rule:
            return False
    return True


def apply_effects(effects, state):
    result = copy.deepcopy(state)
    for name, value in effects.items():
        if type(value) is bool:
            result[name] = value
        else:
            result[name] += value
    return result


def outgoing(node):
    if "choices" in node:
        return [x["next"] for x in node["choices"]]
    if "routes" in node:
        return [x["next"] for x in node["routes"]]
    return [node["next"]] if "next" in node else []


def scene_lines(node):
    yield from node.get("lines", [])
    for choice in node.get("choices", []):
        yield from choice.get("response", [])


def validate_structure(story):
    errors = []
    if story.get("schema_version") != 1:
        errors.append("Unsupported story schema_version")
    if story.get("initial_state") != {"affection": 0, "trust": 0, "truth_known": False}:
        errors.append("Invalid initial state")
    nodes = story.get("nodes", [])
    ids = [n.get("id", "") for n in nodes]
    if len(ids) != len(set(ids)):
        errors.append("Duplicate scene ID")
    if any(not ID.fullmatch(n) or n == "start" for n in ids):
        errors.append("Invalid scene ID")
    if story.get("entry") not in ids:
        errors.append("Missing entry scene")
    line_ids = set()
    for n in nodes:
        name = n.get("id", "?")
        modes = [k for k in ("next", "choices", "routes", "ending") if k in n]
        if len(modes) != 1:
            errors.append(f"{name}: requires exactly one next/choices/routes/ending")
        if not n.get("location") or not n.get("time"):
            errors.append(f"{name}: missing location/time")
        for target in outgoing(n):
            if target not in ids:
                errors.append(f"{name}: missing target {target}")
        if "choices" in n and len(n["choices"]) < 2:
            errors.append(f"{name}: requires at least two choices")
        for choice in n.get("choices", []):
            if not choice.get("text") or not ID.fullmatch(choice.get("id", "")):
                errors.append(f"{name}: invalid choice")
            if not choice.get("effects"):
                errors.append(f"{name}: choice has no state effect")
            for key, value in choice.get("effects", {}).items():
                if key not in STATE_TYPES or type(value) is not STATE_TYPES.get(key):
                    errors.append(f"{name}: invalid effect {key}")
        choices = n.get("choices", [])
        if len({c.get("id") for c in choices}) != len(choices):
            errors.append(f"{name}: duplicate choice ID")
        for route in n.get("routes", []):
            for key, rule in route.get("when", {}).items():
                if key not in STATE_TYPES:
                    errors.append(f"{name}: unknown condition state {key}")
                elif isinstance(rule, dict):
                    if not rule or set(rule) - {"gte", "eq"}:
                        errors.append(f"{name}: unsupported condition")
                    for op, value in rule.items():
                        if type(value) is not STATE_TYPES[key] or (op == "gte" and type(value) is bool):
                            errors.append(f"{name}: invalid condition value")
                elif type(rule) is not STATE_TYPES[key]:
                    errors.append(f"{name}: invalid condition type")
        if "routes" in n and (not n["routes"] or n["routes"][-1].get("when")):
            errors.append(f"{name}: routes must end in an unconditional fallback")
        for line in scene_lines(n):
            line_id = line.get("id", "")
            if not ID.fullmatch(line_id) or line_id in line_ids:
                errors.append(f"{name}: duplicate/invalid line ID {line_id}")
            line_ids.add(line_id)
            if line.get("speaker") not in {"n", "h", "p"} or not line.get("text", "").strip():
                errors.append(f"{name}: invalid dialogue line")
    return errors


def enumerate_routes(story):
    errors = validate_structure(story)
    if errors:
        return {"errors": errors, "routes": [], "reachable": []}
    nodes = {n["id"]: n for n in story["nodes"]}
    routes, reachable, used_choices = [], set(), set()

    def visit(scene, state, path, selected):
        if scene in path:
            errors.append(f"Infinite loop: {' -> '.join(path + [scene])}")
            return
        if len(routes) > 10000:
            errors.append("Story exceeds small-project route budget")
            return
        reachable.add(scene)
        node = nodes[scene]
        path = path + [scene]
        if "ending" in node:
            routes.append({"ending": node["ending"], "state": state, "path": path, "choices": selected})
        elif "choices" in node:
            for c in node["choices"]:
                used_choices.add((scene, c["id"]))
                visit(c["next"], apply_effects(c["effects"], state), path, selected + [c["id"]])
        elif "routes" in node:
            for r in node["routes"]:
                if condition_met(r.get("when", {}), state):
                    visit(r["next"], state, path, selected)
                    break
            else:
                errors.append(f"Dead route at {scene}: {state}")
        else:
            visit(node["next"], state, path, selected)

    visit(story["entry"], story["initial_state"], [], [])
    for missing in sorted(nodes.keys() - reachable):
        errors.append(f"Unreachable scene: {missing}")
    endings = {r["ending"] for r in routes}
    for n in story["nodes"]:
        if n.get("ending") and n["ending"] not in endings:
            errors.append(f"Unreachable ending: {n['ending']}")
        for c in n.get("choices", []):
            if (n["id"], c["id"]) not in used_choices:
                errors.append(f"Unreachable choice: {n['id']}/{c['id']}")
    return {"errors": sorted(set(errors)), "routes": routes, "reachable": sorted(reachable)}
