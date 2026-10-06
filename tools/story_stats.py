"""Measure reachable story text; reading estimates are not playtest acceptance."""
import argparse
import hashlib
import json
from pathlib import Path
from tools.story_model import STORY, enumerate_routes, load_story, scene_lines


def measure(story):
    graph = enumerate_routes(story)
    if graph['errors']:
        raise ValueError('; '.join(graph['errors']))
    nodes = {node['id']: node for node in story['nodes']}
    all_lines = {line['id']: line for node in nodes.values() for line in scene_lines(node)}
    chapters = []
    routes = []
    for route in graph['routes']:
        selected = set(route['choices'])
        lines = {}
        menus = []
        for scene in route['path']:
            node = nodes[scene]
            for line in node.get('lines', []):
                lines[line['id']] = line
            for choice in node.get('choices', []):
                menus.append(choice['text'])
                if choice['id'] in selected:
                    for line in choice.get('response', []):
                        lines[line['id']] = line
        body = sum(len(line['text']) for line in lines.values())
        routes.append({
            **route,
            'body_characters': body,
            'body_lines': len(lines),
            'menu_characters': sum(map(len, menus)),
            'narrative_scenes': sum(bool(nodes[scene].get('lines')) for scene in route['path']),
            'router_nodes': sum('routes' in nodes[scene] for scene in route['path']),
            'estimated_reading_minutes': {
                'at_350_chars_per_minute': round(body / 350, 2),
                'at_250_chars_per_minute': round(body / 250, 2),
            },
        })
    for chapter in story['chapters']:
        chapter_nodes = [node for node in nodes.values() if node['chapter'] == chapter['id']]
        chapters.append({
            'id': chapter['id'], 'title': chapter['title'],
            'body_characters': sum(len(line['text']) for node in chapter_nodes for line in scene_lines(node)),
            'narrative_scenes': sum(bool(node.get('lines')) for node in chapter_nodes),
        })
    return {
        'version': story['version'],
        'method': 'Unicode characters including punctuation; body deduplicated by line ID; each route includes only selected responses; both displayed menu options counted separately; title/prompt/router text excluded.',
        'reading_estimate_limit': 'Text reading only, 250–350 characters/minute. No measured playtime, choice or image dwell time, audio listening or breaks.',
        'all_branch_body_characters': sum(len(line['text']) for line in all_lines.values()),
        'all_branch_body_lines': len(all_lines),
        'all_menu_characters': sum(len(choice['text']) for node in nodes.values() for choice in node.get('choices', [])),
        'narrative_scenes': sum(bool(node.get('lines')) for node in nodes.values()),
        'router_nodes': sum('routes' in node for node in nodes.values()),
        'route_count': len(routes),
        'endings': {ending: sum(route['ending'] == ending for route in routes) for ending in sorted({route['ending'] for route in routes})},
        'shortest_route_characters': min(route['body_characters'] for route in routes),
        'longest_route_characters': max(route['body_characters'] for route in routes),
        'chapters': chapters,
        'routes': routes,
    }


def render_markdown(report):
    lines = [
        f"# v{report['version']} 路线字数报告", '',
        f"剧情版本：`{report['version']}`。剧情源 SHA-256：`{report['story_sha256']}`。", '',
        '按台词 ID 去重，正文包含标点，单位为 Unicode 字符；各路线仅计算所选选项的回应。菜单选项单列，章节标题、Prompt 和纯路由节点不计入正文。', '',
        f"全分支正文 **{report['all_branch_body_characters']}** 字符；{report['all_branch_body_lines']} 行；菜单 {report['all_menu_characters']} 字符。共 {report['narrative_scenes']} 个叙事场景、{report['router_nodes']} 个纯路由节点、{report['route_count']} 条路线。", '',
        f"单路线 **{report['shortest_route_characters']}–{report['longest_route_characters']}** 字符。True {report['endings'].get('true', 0)} 条，Normal {report['endings'].get('normal', 0)} 条。", '',
        '阅读估算仅用每分钟 250–350 字符换算正文，不含选择停顿、画面停留、试听和离开游戏的暂停。它不能替代真人 30–60 分钟验收。', '',
        '| 章节 | 全分支正文字符 | 叙事场景 |', '|---|---:|---:|',
    ]
    for chapter in report['chapters']:
        lines.append(f"| {chapter['id']} {chapter['title']} | {chapter['body_characters']} | {chapter['narrative_scenes']} |")
    lines += ['', '| 路线 | 选择顺序 | 结局 | 正文字符 | 菜单字符 | 叙事场景 | 纯文本估算分钟 |',
              '|---|---|---|---:|---:|---:|---:|']
    for index, route in enumerate(report['routes'], 1):
        timing = route['estimated_reading_minutes']
        lines.append(f"| R{index:02d} | {' → '.join(route['choices'])} | {route['ending']} | {route['body_characters']} | {route['menu_characters']} | {route['narrative_scenes']} | {timing['at_350_chars_per_minute']}–{timing['at_250_chars_per_minute']} |")
    lines += ['', '复现：`python -m tools.story_stats --report reports/story-stats.json --markdown reports/story-stats.md`。完整路径及三个终态保存在 JSON 报告中。', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--story', type=Path, default=STORY)
    parser.add_argument('--report', type=Path, default=Path('reports/story-stats.json'))
    parser.add_argument('--markdown', type=Path)
    args = parser.parse_args()
    try:
        report = measure(load_story(args.story))
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    report['story_sha256'] = hashlib.sha256(args.story.read_bytes()).hexdigest()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(render_markdown(report), encoding='utf-8')
    print(f"Body: {report['all_branch_body_characters']} characters; routes: {report['route_count']}; single route: {report['shortest_route_characters']}–{report['longest_route_characters']}; scenes: {report['narrative_scenes']} + {report['router_nodes']} routers")
    print(report['reading_estimate_limit'])


if __name__ == '__main__':
    main()
