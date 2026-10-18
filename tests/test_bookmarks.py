import ast
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'game/python-packages'))
import reading_bookmarks as bookmarks
from tools.compile_story import render_bookmarks

class BookmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.story=json.loads((ROOT/'game/data/story.json').read_text())
        cls.voices=json.loads((ROOT/'game/data/voice_manifest.json').read_text())['voices']
        cls.catalog=bookmarks.make_catalog(cls.story,cls.voices)
    def entry(self,key,**changes):
        record=self.catalog[key]
        return SimpleNamespace(**(dict(who=record['speaker'],what=record['text'],rain_line_id=key)|changes))
    def test_catalog_matches_all_authored_lines_and_original_voices(self):
        self.assertEqual(len(self.catalog),560)
        self.assertEqual(sum(bool(row['voice']) for row in self.catalog.values()),17)
        # characters.rpy declares no per-character voice tag; preserve original gain.
        self.assertTrue(all(row['voice_tag'] is None for row in self.catalog.values()))
        self.assertEqual(self.catalog['s01_arrival_l005']['voice'],'audio/voice/heroine_s01_arrival_l005_v1.ogg')
    def test_only_a_real_read_record_can_create_a_bookmark(self):
        key='s01_arrival_l005'
        self.assertEqual(bookmarks.toggle([],key,[],self.catalog),{})
        added=bookmarks.toggle([],key,[self.entry(key)],self.catalog,now=1)
        self.assertEqual(bookmarks.clean_ids(added,self.catalog),[key])
        removed=bookmarks.toggle(added,key,[],self.catalog,now=2)
        self.assertEqual(bookmarks.clean_ids(removed,self.catalog),[])
        self.assertEqual(removed[key],[False,2])
    def test_native_import_merge_preserves_old_additions_and_newer_deletions_and_readds(self):
        key='s01_arrival_l005'
        added=bookmarks.toggle({},key,[self.entry(key)],self.catalog,now=1)
        self.assertEqual(bookmarks.clean_ids(bookmarks.merge(added,{},self.catalog),self.catalog),[key])
        removed=bookmarks.toggle(added,key,[],self.catalog,now=2)
        self.assertEqual(bookmarks.clean_ids(bookmarks.merge(removed,added,self.catalog),self.catalog),[])
        reread=bookmarks.toggle(removed,key,[self.entry(key)],self.catalog,now=3)
        self.assertEqual(bookmarks.clean_ids(bookmarks.merge(removed,reread,self.catalog),self.catalog),[key])
        self.assertEqual(bookmarks.clean_ids(bookmarks.merge(reread,removed,self.catalog),self.catalog),[key])
    def test_stale_line_identity_does_not_bind_another_record(self):
        key='s01_arrival_l005'
        self.assertIsNone(bookmarks.identify(self.entry(key,what='并非原句'),self.catalog))
        self.assertIsNone(bookmarks.identify(self.entry(key,rain_line_id='future'),self.catalog))
    def test_legacy_fallback_requires_a_unique_exact_speaker_and_text(self):
        key='s01_arrival_l005';entry=self.entry(key,rain_line_id=None)
        self.assertEqual(bookmarks.identify(entry,self.catalog),key)
        duplicated=dict(self.catalog,duplicate=self.catalog[key])
        self.assertIsNone(bookmarks.identify(entry,duplicated))
    def test_cleanup_preserves_order_and_ignores_unknown_or_invalid_values(self):
        keys=list(self.catalog)[:2]
        self.assertEqual(bookmarks.clean_ids([keys[0],[],99,'unknown',*keys],self.catalog),keys)
        self.assertEqual(bookmarks.clean_ids({},self.catalog),[])
    def test_chapter_filter_cannot_add_an_unread_record(self):
        keys=list(self.catalog);ids=[keys[0],'s01_arrival_l005']
        for chapter in self.story['chapters']:
            rows=bookmarks.bookmark_rows(ids,self.catalog,chapter['id'])
            self.assertTrue(all(row['chapter']==chapter['id'] and row['id'] in ids for row in rows))
    def test_player_catalog_is_generated_from_the_source_without_runtime_author_json(self):
        generated=render_bookmarks(self.story,self.voices)
        self.assertEqual(generated,(ROOT/'game/script/bookmarks_generated.rpy').read_text())
        payload=next(line.split(' = ',1)[1] for line in generated.splitlines() if 'RAIN_READING_CATALOG =' in line)
        self.assertEqual(ast.literal_eval(payload),self.catalog)
        runtime=(ROOT/'game/bookmarks.rpy').read_text()
        self.assertNotIn('game/data',runtime);self.assertNotIn('renpy.file(',runtime)
