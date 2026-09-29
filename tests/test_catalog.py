from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from veyrix.cli import main
from veyrix.common import Error, encoded
from test_veyrix import REPO, initialize, commit, write

spec=importlib.util.spec_from_file_location('check_catalog',REPO/'tools/check_catalog.py')
checker=importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class CatalogTests(unittest.TestCase):
    def test_real_catalog_integrity_and_migration(self):
        out=checker.check(REPO)
        self.assertEqual(out['skills'],44)
        self.assertEqual(out['migration'],{'KEEP':43,'DEFER':3,'EXCLUDE':49})
        self.assertEqual(out['host_runtime'],'NOT_RUN')

    def test_no_vue_or_operational_scope(self):
        catalog=json.loads((REPO/'catalog/skills.json').read_bytes())['skills']
        for name in ('vue','nuxt','pinia','impeccable','swift-concurrency','kotlin-coroutines-flows','flutter-apply-architecture-best-practices','wrangler'):
            self.assertNotIn(name,catalog)

    def test_preserved_local_origins_not_rebranded_external(self):
        catalog=json.loads((REPO/'catalog/skills.json').read_bytes())['skills']
        for name in ('api-contract','generated-code','java-style'):
            self.assertEqual(catalog[name]['upstream']['sourceType'],'local-derived')

    def test_every_conditional_has_limitations(self):
        catalog=json.loads((REPO/'catalog/skills.json').read_bytes())['skills']
        for name,entry in catalog.items():
            if entry['status']=='conditional':self.assertTrue(entry['limitations'],name)

    def test_taste_emil_and_web_review_are_selected_not_new_guides(self):
        craft=json.loads((REPO/'addons/frontend-craft.json').read_bytes())['roles']['designer']
        self.assertEqual(set(craft),{'design-taste-frontend','redesign-existing-projects','emil-design-eng','animate','review-animations','web-design-guidelines'})

    def test_modified_vendor_bytes_fail(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/'repo';shutil.copytree(REPO,root,ignore=shutil.ignore_patterns('.git','__pycache__','*.egg-info'))
            write(root,'skills/java-style/SKILL.md','modified')
            with self.assertRaises(Error) as exc:checker.check(root)
            self.assertEqual(exc.exception.code,'HASH')

    def test_unknown_profile_id_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/'repo';shutil.copytree(REPO,root,ignore=shutil.ignore_patterns('.git','__pycache__','*.egg-info'))
            write(root,'profiles/java.json',encoded({'schema':1,'roles':{'fixer':['missing']}}))
            with self.assertRaises(Error):checker.check(root)

    def test_missing_migration_reason_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/'repo';shutil.copytree(REPO,root,ignore=shutil.ignore_patterns('.git','__pycache__','*.egg-info'))
            obj=json.loads((root/'catalog/migration.json').read_bytes());obj['decisions']['java-style'].pop('reason')
            write(root,'catalog/migration.json',encoded(obj))
            with self.assertRaises(Error):checker.check(root)

    def test_all_real_profiles_materialize_and_noop(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);source=root/'source'
            shutil.copytree(REPO,source,ignore=shutil.ignore_patterns('.git','__pycache__','*.egg-info'))
            initialize(source);pin=commit(source)
            home=root/'home';home.mkdir();cache=root/'cache'
            with patch.dict(os.environ,{'HOME':str(home),'XDG_CONFIG_HOME':str(home/'.config'),'OPENCODE_CONFIG_DIR':str(home/'.config/opencode')}):
                for file in sorted((REPO/'profiles').glob('*.json')):
                    project=root/file.stem;initialize(project)
                    base=['--project',str(project),'--cache-dir',str(cache),'--allow-local-source']
                    with self.subTest(profile=file.stem),contextlib.redirect_stdout(io.StringIO()) as out:
                        code=main(base+['init','--profile',file.stem,'--repository',source.as_uri(),'--ref',pin])
                        self.assertEqual(code,0,out.getvalue())
                        before={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.git' not in p.relative_to(project).parts}
                        with contextlib.redirect_stdout(io.StringIO()) as second:
                            self.assertEqual(main(base+['--offline','sync']),0)
                        self.assertEqual(json.loads(second.getvalue())['result'],'NOOP')
                        after={str(p.relative_to(project)):p.read_bytes() for p in project.rglob('*') if p.is_file() and '.git' not in p.relative_to(project).parts}
                        self.assertEqual(before,after)


if __name__=='__main__':unittest.main()
