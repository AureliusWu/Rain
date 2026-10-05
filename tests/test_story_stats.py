import unittest
from tools.story_model import load_story
from tools.story_stats import measure


class StoryStatsTests(unittest.TestCase):
    def setUp(self):
        self.story = load_story()
        self.story['entry'] = 'entry'
        self.story['expected_routes'] = 2
        self.story['chapters'] = [{'id': 'ch00', 'title': '章', 'goal': '统计', 'entry': 'entry'}]
        common = {'chapter': 'ch00', 'location': '站台', 'time': '21:00', 'dramatic_purpose': '统计'}
        self.story['nodes'] = [
            {**common, 'id': 'entry', 'lines': [{'id': 'entry_line', 'speaker': 'n', 'text': '入口一'}],
             'choices': [
                 {'id': 'choice_a', 'text': '问甲', 'effects': {'trust': 1}, 'next': 'ending_a',
                  'response': [{'id': 'response_a', 'speaker': 'p', 'text': '甲回应'}]},
                 {'id': 'choice_b', 'text': '问乙', 'effects': {'trust': -1}, 'next': 'ending_b',
                  'response': [{'id': 'response_b', 'speaker': 'p', 'text': '乙回应较长'}]},
             ]},
            {**common, 'id': 'ending_a', 'ending': 'normal', 'lines': [{'id': 'line_a', 'speaker': 'n', 'text': '甲结尾'}]},
            {**common, 'id': 'ending_b', 'ending': 'true', 'lines': [{'id': 'line_b', 'speaker': 'n', 'text': '乙的结尾更长'}]},
        ]

    def test_routes_count_only_their_selected_response(self):
        report = measure(self.story)
        self.assertEqual(report['all_branch_body_characters'], 20)
        self.assertEqual([r['body_characters'] for r in report['routes']], [9, 14])
        self.assertEqual([r['body_lines'] for r in report['routes']], [3, 3])
        self.assertEqual([r['narrative_scenes'] for r in report['routes']], [2, 2])

    def test_menu_and_title_do_not_inflate_body(self):
        self.story['chapters'][0]['title'] = '额外章节标题' * 100
        self.story['nodes'][0]['choices'][0]['text'] = '另一个更长的选项'
        report = measure(self.story)
        self.assertEqual(report['all_branch_body_characters'], 20)
        self.assertEqual([r['body_characters'] for r in report['routes']], [9, 14])
        self.assertEqual(report['all_menu_characters'], 10)
        self.assertEqual([r['menu_characters'] for r in report['routes']], [10, 10])

    def test_unreachable_text_cannot_be_reported_as_valid_content(self):
        self.story['nodes'].append({**self.story['nodes'][1], 'id': 'orphan',
                                   'lines': [{'id': 'orphan_line', 'speaker': 'n', 'text': '不可达正文'}]})
        with self.assertRaisesRegex(ValueError, 'Unreachable scene'):
            measure(self.story)
