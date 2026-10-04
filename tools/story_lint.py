"""Mechanical prose checks. Character intent and timeline still require review."""
from collections import Counter
import hashlib
import re
from tools.story_model import ROOT, load_story, validate_structure, scene_lines
from tools.prompt_registry import prompt_by_file


def lint(story):
    errors = validate_structure(story)
    version = (ROOT / "VERSION").read_text().strip()
    options = (ROOT / "game/options.rpy").read_text(encoding="utf-8")
    declared = re.search(r'define config.version = "([^"]+)"', options)
    if story.get("version") != version or not declared or declared.group(1) != version:
        errors.append("Story / VERSION / config.version mismatch")
    for node in story["nodes"]:
        if not node.get("lines"):
            continue
        prompt = ROOT / node.get("draft_prompt", "missing")
        if not prompt.is_file() or hashlib.sha256(prompt.read_bytes()).hexdigest() != node.get("draft_prompt_sha256"):
            errors.append(f"{node['id']}: missing/stale Scene Prompt")
        try:
            if prompt_by_file(ROOT, node.get("draft_prompt"))["id"] != node.get("draft_prompt_id"):
                errors.append(f"{node['id']}: Scene Prompt Registry binding mismatch")
        except (ValueError, OSError) as exc:
            errors.append(f"{node['id']}: Scene Prompt Registry: {exc}")
    texts = [line["text"] for n in story["nodes"] for line in scene_lines(n)]
    warnings = []
    for text, count in Counter(texts).items():
        if count > 1 and len(text) > 15:
            warnings.append(f"Repeated line ({count}): {text[:45]}")
    for text in texts:
        if len(text) > 140:
            warnings.append(f"Long dialogue line: {text[:45]}")
        if any(word in text for word in ["TODO", "待补充", "作为一个人工智能", "不禁陷入了沉思"]):
            errors.append(f"Draft marker / stock phrase: {text[:45]}")
        if "\n" in text or len(text) > 220:
            errors.append(f"Dialogue exceeds display budget: {text[:45]}")
    return errors, warnings


def main():
    story = load_story()
    errors, warnings = lint(story)
    for x in errors:
        print("ERROR:", x)
    for x in warnings:
        print("REVIEW:", x)
    count = sum(len(line["text"]) for n in story["nodes"] for line in scene_lines(n))
    print(f"Story lint: {len(errors)} errors, {len(warnings)} review notes; {count} characters (all branches).")
    print("Manual review required: character consistency, emotional logic, timeline, and pacing.")
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
