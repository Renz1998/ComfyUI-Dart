from test_regressions import plugin
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image


class BatchRunnerBackendTests(unittest.TestCase):
    def test_request_ids_invalidate_cache_without_changing_manual_selection(self):
        cls = plugin.NODE_CLASS_MAPPINGS['DanbooruTagsTransformerImageBatchUpload']
        with tempfile.TemporaryDirectory() as folder:
            for index in range(2): Image.new('RGB', (16, 16), (index * 100, 20, 40)).save(Path(folder)/f'{index}.png')
            names = json.dumps(['0.png', '1.png'])
            fields = dict(images=names, batch_mode='One image per queued run', index=1, wrap_index=False, max_images=1)
            with patch.dict(sys.modules, {'folder_paths': SimpleNamespace(get_input_directory=lambda:folder)}):
                first = cls.IS_CHANGED(**fields, batch_run_id='a:0')
                self.assertEqual(first, cls.IS_CHANGED(**fields, batch_run_id='a:0'))
                self.assertNotEqual(first, cls.IS_CHANGED(**fields, batch_run_id='b:0'))
                self.assertEqual(cls().load(**fields, batch_run_id='a:0')['result'][1], ['1.png'])
                self.assertEqual(cls().load(**fields)['result'][1], ['1.png'])
        self.assertEqual(cls.INPUT_TYPES()['optional']['batch_run_id'][1]['default'], '')


if __name__ == '__main__': unittest.main()
