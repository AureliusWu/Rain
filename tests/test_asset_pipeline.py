import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image
from tools.asset_paths import project_file, sha256
from tools.asset_validator import validate_assets
from tools.image_process.import_asset import import_image, rebuild_image, verify_rebuilds
from tools.image_process.metadata import image_metadata
from tools.prompt_registry import render_registry, validate_registry


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for directory in ['assets_source/character', 'assets_source/ui', 'prompts/character', 'game/data']:
            (self.root / directory).mkdir(parents=True)
        self.source = 'assets_source/character/heroine_v1.png'
        image = Image.new('RGBA', (64, 96))
        image.paste((80, 120, 180, 254), (12, 8, 52, 88))
        image.save(self.root / self.source)
        self.prompt = 'prompts/character/heroine_v1.md'
        (self.root / self.prompt).write_text('Version: 1. Adult original heroine.\n')
        self.write_registry()
        self.manifest = self.root / 'game/data/asset_manifest.json'
        self.manifest.write_text('{"schema_version": 1, "assets": []}\n')
        self.arguments = dict(root=self.root, source=self.source, asset_id='heroine_normal', kind='sprite',
                              output='characters/heroine_v1.png', version=1, prompt=self.prompt,
                              source_label='Original test illustration', license_name='Project MIT')

    def write_registry(self):
        (self.root / 'prompts/registry.json').write_text(json.dumps(render_registry(self.root), indent=2) + '\n')

    def assets(self):
        return json.loads(self.manifest.read_text())

    def errors(self, manifest=None, story=None):
        return validate_assets(root=self.root, story=story or {'nodes': []}, manifest=manifest, voices=[])

    def test_repeat_import_and_saved_recipe_are_idempotent(self):
        import_image(**self.arguments)
        file = self.root / 'game' / self.arguments['output']
        original = (self.manifest.read_bytes(), file.read_bytes())
        self.assertFalse(import_image(**self.arguments)['changed'])
        self.assertFalse(rebuild_image('heroine_normal', root=self.root)['changed'])
        self.assertEqual(original, (self.manifest.read_bytes(), file.read_bytes()))
        self.assertEqual(verify_rebuilds(self.root), ([], ['heroine_normal']))
        self.assertEqual(self.errors(), [])
        with Image.open(file) as image:
            self.assertEqual(image.size, (540, 700))
            self.assertEqual(image.getchannel('A').getextrema(), (0, 254))

    def test_dry_run_never_creates_output_or_changes_manifest(self):
        before = self.manifest.read_bytes()
        report = import_image(**self.arguments, dry_run=True)
        self.assertTrue(report['changed'])
        self.assertEqual(before, self.manifest.read_bytes())
        self.assertFalse((self.root / 'game/characters').exists())

    def test_ui_keeps_native_size_and_alpha(self):
        source = 'assets_source/ui/check_v1.png'
        image = Image.new('RGBA', (25, 36), (0, 0, 0, 0))
        image.paste((90, 170, 210, 255), (3, 5, 8, 30))
        image.save(self.root / source)
        args = dict(self.arguments, source=source, asset_id='ui_check', kind='ui', output='gui/check.png', prompt=None)
        import_image(**args)
        self.assertEqual((self.root / source).read_bytes(), (self.root / 'game/gui/check.png').read_bytes())
        self.assertEqual(self.assets()['assets'][0]['image']['width'], 25)

    def test_opaque_or_empty_sprite_is_rejected_before_write(self):
        before = self.manifest.read_bytes()
        for mode, color in [('RGB', 'blue'), ('RGBA', (0, 0, 0, 0))]:
            Image.new(mode, (64, 96), color).save(self.root / self.source)
            with self.assertRaisesRegex(ValueError, 'transparen|visible'):
                import_image(**self.arguments)
        self.assertEqual(before, self.manifest.read_bytes())
        self.assertFalse((self.root / 'game/characters').exists())

    def test_missing_reference_and_changed_prompt_do_not_leave_output(self):
        before = self.manifest.read_bytes()
        with self.assertRaisesRegex(ValueError, 'Missing file'):
            import_image(**self.arguments, reference_source='assets_source/character/missing.png')
        (self.root / self.prompt).write_text('Changed, not registered.\n')
        with self.assertRaisesRegex(ValueError, 'Prompt hash mismatch'):
            import_image(**self.arguments)
        self.assertEqual(before, self.manifest.read_bytes())
        self.assertFalse((self.root / 'game/characters').exists())

    def test_version_change_required_and_downgrade_rejected(self):
        import_image(**self.arguments)
        before = (self.manifest.read_bytes(), (self.root / 'game/characters/heroine_v1.png').read_bytes())
        image = Image.new('RGBA', (64, 96))
        image.paste((140, 100, 160, 254), (12, 8, 52, 88))
        image.save(self.root / self.source)
        with self.assertRaisesRegex(ValueError, 'higher asset version'):
            import_image(**self.arguments)
        self.assertEqual(before, (self.manifest.read_bytes(), (self.root / 'game/characters/heroine_v1.png').read_bytes()))
        import_image(**dict(self.arguments, version=2))
        with self.assertRaisesRegex(ValueError, 'downgrade'):
            import_image(**self.arguments)

    def test_output_collision_and_untracked_file_are_rejected(self):
        import_image(**self.arguments)
        with self.assertRaisesRegex(ValueError, 'another asset ID'):
            import_image(**dict(self.arguments, asset_id='other_heroine'))
        file = self.root / 'game/characters/untracked.png'
        file.write_bytes(b'keep me')
        with self.assertRaisesRegex(ValueError, 'untracked'):
            import_image(**dict(self.arguments, asset_id='other_heroine', output='characters/untracked.png'))
        self.assertEqual(file.read_bytes(), b'keep me')

    def test_manifest_replace_failure_restores_previous_image(self):
        import_image(**self.arguments)
        target = self.root / 'game/characters/heroine_v1.png'
        before = (self.manifest.read_bytes(), target.read_bytes())
        image = Image.new('RGBA', (64, 96))
        image.paste((180, 60, 50, 254), (12, 8, 52, 88))
        image.save(self.root / self.source)
        replace = os.replace

        def fail_manifest(source, destination):
            if Path(destination) == self.manifest:
                raise OSError('simulated manifest write failure')
            return replace(source, destination)

        with patch('tools.image_process.import_asset.os.replace', side_effect=fail_manifest):
            with self.assertRaisesRegex(OSError, 'simulated'):
                import_image(**dict(self.arguments, version=2))
        self.assertEqual(before, (self.manifest.read_bytes(), target.read_bytes()))
        self.assertEqual(list(self.root.rglob('.asset-import-*')), [])

    def test_failed_first_import_removes_partial_image(self):
        replace = os.replace

        def fail_manifest(source, destination):
            if Path(destination) == self.manifest:
                raise OSError('simulated failure')
            return replace(source, destination)

        before = self.manifest.read_bytes()
        with patch('tools.image_process.import_asset.os.replace', side_effect=fail_manifest):
            with self.assertRaises(OSError):
                import_image(**self.arguments)
        self.assertEqual(self.manifest.read_bytes(), before)
        self.assertFalse((self.root / 'game/characters/heroine_v1.png').exists())

    def test_traversal_and_cross_platform_paths_are_rejected(self):
        for path in ['../outside.png', '/tmp/outside.png', 'assets_source/../outside.png',
                     'assets_source\\character\\x.png', 'C:/outside.png', 'assets_source//x.png']:
            with self.subTest(path=path), self.assertRaises(ValueError):
                project_file(self.root, path, 'assets_source', must_exist=False)

    def test_symlink_cannot_escape_asset_folder(self):
        # Use a real link when permitted; otherwise simulate its resolved target.
        with tempfile.TemporaryDirectory() as outside:
            link = self.root / 'assets_source/character/link.png'
            destination = Path(outside) / 'outside.png'
            try:
                link.symlink_to(destination)
            except OSError:
                resolve = Path.resolve
                with patch.object(Path, 'resolve', lambda p, *a, **k: destination if p == link else resolve(p, *a, **k)):
                    with self.assertRaisesRegex(ValueError, 'escapes'):
                        project_file(self.root, 'assets_source/character/link.png', 'assets_source', must_exist=False)
                return
            with self.assertRaisesRegex(ValueError, 'escapes'):
                project_file(self.root, 'assets_source/character/link.png', 'assets_source', must_exist=False)

    def test_reference_rebinding_requires_a_new_asset_version(self):
        first = 'assets_source/character/reference_v1.png'
        second = 'assets_source/character/reference_v2.png'
        content = (self.root / self.source).read_bytes()
        (self.root / first).write_bytes(content)
        (self.root / second).write_bytes(content)
        import_image(**self.arguments, reference_source=first)
        before = self.manifest.read_bytes()
        with self.assertRaisesRegex(ValueError, 'higher asset version'):
            import_image(**self.arguments, reference_source=second)
        self.assertEqual(before, self.manifest.read_bytes())

    def test_corrupt_png_with_matching_file_hash_is_still_rejected(self):
        import_image(**self.arguments)
        file = self.root / 'game/characters/heroine_v1.png'
        file.write_bytes(b'not a PNG')
        manifest = self.assets()
        manifest['assets'][0]['sha256'] = sha256(file.read_bytes())
        self.assertTrue(any('Undecodable image' in e for e in self.errors(manifest)))

    def test_duplicate_output_and_wrong_reference_type_are_rejected(self):
        import_image(**self.arguments)
        manifest = self.assets()
        clone = copy.deepcopy(manifest['assets'][0])
        clone['id'] = 'second_asset'
        manifest['assets'].append(clone)
        story = {'nodes': [{'id': 'test_scene', 'background': 'heroine_normal', 'lines': []}]}
        errors = self.errors(manifest, story)
        self.assertIn('Duplicate asset output path', errors)
        self.assertTrue(any('wrong asset type' in e for e in errors))

    def test_registered_prompt_binding_cannot_point_to_another_id(self):
        import_image(**self.arguments)
        manifest = self.assets()
        manifest['assets'][0]['prompt_id'] = 'unrelated_prompt'
        self.assertTrue(any('Registry binding mismatch' in e for e in self.errors(manifest)))

    def test_prompt_registry_rejects_duplicate_and_wrong_versions(self):
        registry = render_registry(self.root)
        registry['prompts'].append(dict(registry['prompts'][0], version=2))
        errors = validate_registry(self.root, registry)
        self.assertTrue(any('Duplicate/invalid Prompt ID' in e for e in errors))
        self.assertTrue(any('version disagrees' in e for e in errors))

    def test_missing_component_is_rejected(self):
        (self.root / self.prompt).write_text('Version: 1\nShared components: `prompts/character/missing_v1.json`\n')
        self.write_registry()
        self.assertTrue(any('Missing/invalid Prompt component' in e for e in validate_registry(self.root)))


if __name__ == '__main__':
    unittest.main()
