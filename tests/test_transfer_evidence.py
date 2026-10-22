"""Keep full native evidence transferable as the media inventory grows."""
import hashlib
from pathlib import Path
import re
import tempfile
import unittest

from tools.build.transfer_evidence import MAX_PARTS, PART_BYTES, split_bundle
from tools.story_model import ROOT


class EvidenceTransferTests(unittest.TestCase):
    def test_parts_reconstruct_exact_bytes_and_digests(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = root / 'bundle.zip'
            archive.write_bytes(b'0123456789')
            parts = split_bundle(archive, root, part_bytes=4, max_parts=3)
            self.assertEqual([p['bytes'] for p in parts], [4, 4, 2])
            chunks = [(root / f"part{p['index']:02d}" / 'bundle.part').read_bytes() for p in parts]
            self.assertEqual(b''.join(chunks), archive.read_bytes())
            self.assertEqual([p['sha256'] for p in parts], [hashlib.sha256(b).hexdigest() for b in chunks])

    def test_all_workflow_slots_have_matching_bound_paths_and_names(self):
        workflow = (ROOT / '.github/workflows/game.yml').read_text()
        pattern = (r"      - name: Upload exact transfer part (\d{2})\n"
                   r"        if: \$\{\{ hashFiles\('transfer/part\1/bundle.part'\) != '' \}\}\n"
                   r"        uses: actions/upload-artifact@v4\n"
                   r"        with:\n"
                   r"          name: release-transfer-\$\{\{ github.sha \}\}-\1\n"
                   r"          path: transfer/part\1/\n"
                   r"          if-no-files-found: error")
        self.assertEqual([int(i) for i in re.findall(pattern, workflow)], list(range(MAX_PARTS)))
        self.assertEqual(PART_BYTES, 20 * 1024 * 1024)

    def test_exact_capacity_boundary_is_accepted(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = root / 'bundle.zip'
            archive.write_bytes(b'x' * MAX_PARTS)
            parts = split_bundle(archive, root, part_bytes=1)
            self.assertEqual(len(parts), MAX_PARTS)
            self.assertEqual(parts[-1]['index'], MAX_PARTS - 1)

    def test_overflow_is_rejected_before_any_partial_outputs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = root / 'bundle.zip'
            archive.write_bytes(b'x' * (MAX_PARTS + 1))
            with self.assertRaisesRegex(ValueError, 'workflow capacity'):
                split_bundle(archive, root, part_bytes=1)
            self.assertEqual(list(root.iterdir()), [archive])
