from __future__ import annotations

import contextlib
import copy
import io
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from veyrix import jsonc
from veyrix.cli import main
from veyrix.common import Error, digest, encoded, guarded, load_json, load_yaml, safe_rel
from veyrix.deploy import LOCK, MANIFEST, OMO, RECEIPT, Plan, apply, read_state
from veyrix.resolve import manifest
from veyrix.source import Cache, repository

REPO = Path(__file__).resolve().parents[1]


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(['git', '-C', str(root), '-c', 'core.hooksPath=/dev/null', *args], stderr=subprocess.DEVNULL).decode().strip()


def initialize(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    git(root, 'init', '-q')
    git(root, 'config', 'user.name', 'Fixture')
    git(root, 'config', 'user.email', 'fixture@localhost')


def write(root: Path, rel: str, data: bytes | str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data.encode() if isinstance(data, str) else data)


def commit(root: Path) -> str:
    git(root, 'add', '.')
    git(root, 'commit', '-qm', 'fixture')
    return git(root, 'rev-parse', 'HEAD')


class ParserTests(unittest.TestCase):
    def test_comments_trailing_commas(self):
        self.assertEqual(jsonc.parse('{// hi\n"a": [1,2,], /* keep */}').value, {'a': [1, 2]})

    def test_string_comment_tokens(self):
        self.assertEqual(jsonc.parse('{"url":"https://example.com/*x*/"}').value['url'], 'https://example.com/*x*/')

    def test_duplicate_jsonc(self):
        with self.assertRaises(Error): jsonc.parse('{"a":1,"a":2}')

    def test_duplicate_json(self):
        with self.assertRaises(Error): load_json('{"a":1,"a":2}')

    def test_duplicate_yaml(self):
        with self.assertRaises(Error): load_yaml('a: 1\na: 2')

    def test_malformed_jsonc(self):
        for text in ('', '{', '{"a":1 "b":2}', '{"a":01}', '{"a":NaN}', '{/* never closed'):
            with self.subTest(text=text), self.assertRaises(Error): jsonc.parse(text)

    def test_jsonc_insert_after_line_comment(self):
        text = '{"a":1 // preserve me\n}'
        patched = jsonc.set_value(text, ('b', 'c'), ['x'])
        self.assertIn('// preserve me', patched)
        self.assertEqual(jsonc.parse(patched).value, {'a': 1, 'b': {'c': ['x']}})

    def test_jsonc_preserves_unrelated_bytes(self):
        text = '{\n // secret model comment\n "agents":{"fixer":{"model" : "custom", "skills_add":["manual"]}},\n "mcps": ["one"],\n}'
        out, owned = jsonc.reconcile(text, {'fixer': ['java-style']}, {})
        self.assertIn('"model" : "custom"', out)
        self.assertIn('// secret model comment', out)
        self.assertIn('"mcps": ["one"]', out)
        self.assertEqual(owned, {'fixer': ['java-style']})
        self.assertEqual(jsonc.parse(out).value['agents']['fixer']['skills_add'], ['manual', 'java-style'])

    def test_jsonc_noop(self):
        text = '{"agents":{"fixer":{"skills_add":["java-style"]}}}'
        self.assertEqual(jsonc.reconcile(text, {'fixer': ['java-style']}, {'fixer': ['java-style']})[0], text)

    def test_jsonc_existing_manual_not_claimed(self):
        text = '{"agents":{"fixer":{"skills_add":["java-style"]}}}'
        self.assertEqual(jsonc.reconcile(text, {'fixer': ['java-style']}, {})[1], {})

    def test_jsonc_user_additions_survive_removal(self):
        text = '{"agents":{"fixer":{"skills_add":["java-style","manual"]}}}'
        out, owned = jsonc.reconcile(text, {'fixer': ['spring-boot']}, {'fixer': ['java-style']})
        self.assertEqual(jsonc.parse(out).value['agents']['fixer']['skills_add'], ['manual','spring-boot'])

    def test_jsonc_removed_owned_grant_blocks(self):
        with self.assertRaises(Error): jsonc.reconcile('{}', {}, {'fixer': ['java-style']})

    def test_jsonc_explicit_denial_blocks(self):
        with self.assertRaises(Error): jsonc.reconcile('{"agents":{"fixer":{"skills_remove":["java-style"]}}}', {'fixer':['java-style']}, {})

    def test_unsafe_paths(self):
        for path in ('../x','/tmp/x','a/../b','a//b','a\\b','a/.git/config','x:y','./a'):
            with self.subTest(path=path), self.assertRaises(Error): safe_rel(path)

    def test_source_url_rejections(self):
        for url in ('--upload-pack=evil','ext::sh','https://user:pass@example.com/repo','https://example.com/repo?token=secret','file:///tmp/repo'):
            with self.subTest(url=url), self.assertRaises(Error): repository(url)

    def test_source_supported_transports(self):
        for url in ('git@github.com:owner/repo.git','ssh://git@github.com/owner/repo.git','https://github.com/owner/repo.git'):
            self.assertEqual(repository(url), url)

    def test_invalid_manifest(self):
        for spec in ({'schema':2}, {'schema':1,'profile':'../x','repository':'https://example.com/r'}, {'schema':1,'profile':'java','repository':'https://example.com/r','unknown':True}):
            with self.assertRaises(Error): manifest(encoded(spec))


class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.source = Path(cls.temp.name) / 'source'
        initialize(cls.source)
        catalog = {'schema':1,'skills':{}}
        for name in ('java-style','spring-boot','test-conditional'):
            data = f'---\nname: {name}\ndescription: Safe test fixture\n---\nFixture body.\n'.encode()
            write(cls.source,f'skills/{name}/SKILL.md',data)
            catalog['skills'][name] = {'path':f'skills/{name}','files':{'SKILL.md':digest(data)},
                                       'status':'conditional' if name=='test-conditional' else 'available',
                                       'limitations':['Explicit test limitation'] if name=='test-conditional' else []}
        write(cls.source,'catalog/skills.json',encoded(catalog))
        write(cls.source,'profiles/java.json',encoded({'schema':1,'roles':{'fixer':['java-style']}}))
        write(cls.source,'addons/spring.json',encoded({'schema':1,'roles':{'fixer':['spring-boot']}}))
        write(cls.source,'addons/testing.json',encoded({'schema':1,'roles':{'fixer':['test-conditional']}}))
        for cmd in ('setup','sync','audit'):
            write(cls.source,f'commands/veyrix-{cmd}.md',f'---\ndescription: fixture {cmd}\n---\nfixture\n')
        cls.pin = commit(cls.source)
        write(cls.source,'profiles/java.json',encoded({'schema':1,'roles':{'fixer':['java-style','spring-boot']}}))
        cls.new_pin = commit(cls.source)
        cls.repository = cls.source.as_uri()

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.project = self.root / 'project'
        initialize(self.project)
        self.cache = self.root/'cache'
        self.home = self.root/'home'
        self.home.mkdir()
        self.environment = patch.dict(os.environ, {'HOME':str(self.home),'XDG_CONFIG_HOME':str(self.home/'.config'), 'OPENCODE_CONFIG_DIR':str(self.home/'.config/opencode')})
        self.environment.start()

    def tearDown(self):
        self.environment.stop()
        self.tempdir.cleanup()

    def cli(self, *args, offline=False, extra=()):
        argv = ['--project',str(self.project),'--cache-dir',str(self.cache),'--allow-local-source']
        if offline: argv += ['--offline']
        for root in extra: argv += ['--extra-skill-root',str(root)]
        with contextlib.redirect_stdout(io.StringIO()) as out:
            status = main(argv + list(args))
        return status, json.loads(out.getvalue())

    def init(self, *extra):
        code, output = self.cli('init','--profile','java','--repository',self.repository,'--ref',self.pin,*extra)
        self.assertEqual(code,0,output)
        return output

    def inventory(self):
        return {p.relative_to(self.project).as_posix():p.read_bytes() for p in self.project.rglob('*') if p.is_file() and '.git' not in p.relative_to(self.project).parts}

    def test_init_and_sync_noop(self):
        self.init(); before=self.inventory()
        code,out=self.cli('sync')
        self.assertEqual((code,out['result']),(0,'NOOP'))
        self.assertEqual(before,self.inventory())

    def test_cache_has_no_worktree(self):
        self.init(); objects=next((self.cache/'repositories').glob('*.git'))
        self.assertEqual(subprocess.check_output(['git','--git-dir',str(objects),'rev-parse','--is-bare-repository']).strip(),b'true')
        self.assertFalse((objects/'skills').exists())

    def test_second_sync_preserves_mtime(self):
        self.init(); path=self.project/'.agents/skills/java-style/SKILL.md'; stamp=path.stat().st_mtime_ns
        self.cli('sync'); self.assertEqual(path.stat().st_mtime_ns,stamp)

    def test_sync_never_follows_head(self):
        self.init(); self.cli('sync'); self.assertEqual(load_json((self.project/LOCK).read_bytes())['commit'],self.pin)
        self.assertFalse((self.project/'.agents/skills/spring-boot').exists())

    def test_offline_warm_cache(self):
        self.init(); code,out=self.cli('sync',offline=True); self.assertEqual(code,0,out)

    def test_offline_cache_miss(self):
        code,out=self.cli('init','--profile','java','--repository',self.repository,'--ref',self.pin,offline=True)
        self.assertEqual((code,out['code']),(2,'OFFLINE_MISS')); self.assertEqual(self.inventory(),{})

    def test_init_dry_run_no_project_writes(self):
        out=self.init('--dry-run'); self.assertEqual(out['result'],'CHANGES_PLANNED'); self.assertEqual(self.inventory(),{})

    def test_update_is_preview_by_default(self):
        self.init(); before=self.inventory(); code,out=self.cli('update','--ref',self.new_pin)
        self.assertEqual(code,0,out); self.assertTrue(out['preview']); self.assertEqual(before,self.inventory())

    def test_update_apply_and_noop(self):
        self.init(); code,out=self.cli('update','--ref',self.new_pin,'--apply')
        self.assertEqual(code,0,out); self.assertTrue((self.project/'.agents/skills/spring-boot/SKILL.md').exists())
        self.assertEqual(self.cli('sync')[1]['result'],'NOOP')

    def test_same_pin_addon_selection(self):
        self.init(); spec=load_json((self.project/MANIFEST).read_bytes());spec['addons']=['spring']; write(self.project,MANIFEST,encoded(spec))
        code,out=self.cli('sync'); self.assertEqual(code,0,out); self.assertEqual(out['commit'],self.pin)
        self.assertTrue((self.project/'.agents/skills/spring-boot/SKILL.md').exists())

    def test_removal_only_owned_files(self):
        self.init('--addon','spring');write(self.project,'.agents/skills/unrelated/SKILL.md','manual')
        spec=load_json((self.project/MANIFEST).read_bytes());spec['addons']=[];write(self.project,MANIFEST,encoded(spec))
        code,out=self.cli('sync');self.assertEqual(code,0,out)
        self.assertFalse((self.project/'.agents/skills/spring-boot/SKILL.md').exists())
        self.assertEqual((self.project/'.agents/skills/unrelated/SKILL.md').read_text(),'manual')

    def test_edited_managed_skill_blocks(self):
        self.init();write(self.project,'.agents/skills/java-style/SKILL.md','user edit');before=self.inventory()
        code,out=self.cli('sync');self.assertEqual((code,out['code']),(2,'MANAGED_MODIFIED'));self.assertEqual(before,self.inventory())

    def test_unowned_file_in_skill_blocks(self):
        self.init();write(self.project,'.agents/skills/java-style/notes.md','mine'); before=self.inventory()
        code,out=self.cli('sync');self.assertEqual((code,out['code']),(2,'UNOWNED'));self.assertEqual(before,self.inventory())

    def test_missing_managed_file_restored(self):
        self.init();(self.project/'.agents/skills/java-style/SKILL.md').unlink()
        self.assertEqual(self.cli('audit')[1]['result'],'DRIFT')
        self.assertEqual(self.cli('sync')[0],0);self.assertTrue((self.project/'.agents/skills/java-style/SKILL.md').exists())

    def test_global_identical_collision_blocks(self):
        data=(self.source/'skills/java-style/SKILL.md').read_bytes()
        write(self.home,'.config/opencode/skills/java-style/SKILL.md',data)
        code,out=self.cli('init','--profile','java','--repository',self.repository,'--ref',self.pin)
        self.assertEqual((code,out['code']),(2,'SKILL_COLLISION'));self.assertEqual(self.inventory(),{})

    def test_global_divergent_collision_blocks(self):
        write(self.home,'.agents/skills/java-style/SKILL.md','---\nname: java-style\n---\nother')
        code,out=self.cli('init','--profile','java','--repository',self.repository,'--ref',self.pin)
        self.assertEqual((code,out['code']),(2,'SKILL_COLLISION'))

    def test_project_external_collision_blocks(self):
        write(self.project,'.opencode/skills/java-style/SKILL.md',(self.source/'skills/java-style/SKILL.md').read_bytes())
        code,out=self.cli('init','--profile','java','--repository',self.repository,'--ref',self.pin)
        self.assertEqual((code,out['code']),(2,'SKILL_COLLISION'))

    def test_extra_root_collision(self):
        extra=self.root/'extra';write(extra,'java-style/SKILL.md',(self.source/'skills/java-style/SKILL.md').read_bytes())
        code,out=self.cli('init','--profile','java','--repository',self.repository,'--ref',self.pin,extra=[extra])
        self.assertEqual((code,out['code']),(2,'SKILL_COLLISION'))

    def test_unowned_identical_target_not_adopted(self):
        write(self.project,'.agents/skills/java-style/SKILL.md',(self.source/'skills/java-style/SKILL.md').read_bytes())
        code,out=self.cli('init','--profile','java','--repository',self.repository,'--ref',self.pin)
        self.assertEqual((code,out['code']),(2,'UNOWNED'))

    def test_wrong_singular_agent_root(self):
        write(self.project,'.agent/skills/java-style/SKILL.md','wrong')
        code,out=self.cli('init','--profile','java','--repository',self.repository,'--ref',self.pin)
        self.assertEqual((code,out['code']),(2,'WRONG_SKILL_ROOT'))

    def test_existing_json_omo_blocks(self):
        write(self.project,'.opencode/oh-my-opencode-slim.json','{}'); before=self.inventory()
        code,out=self.cli('init','--profile','java','--repository',self.repository,'--ref',self.pin)
        self.assertEqual((code,out['code']),(2,'LEGACY_OMO_CONFIG'));self.assertEqual(before,self.inventory())

    def test_existing_json_and_jsonc_blocks(self):
        write(self.project,'.opencode/oh-my-opencode-slim.json','{}');write(self.project,OMO,'{}')
        code,out=self.cli('init','--profile','java','--repository',self.repository,'--ref',self.pin)
        self.assertEqual((code,out['code']),(2,'LEGACY_OMO_CONFIG'))

    def test_omo_user_models_comments_and_grants(self):
        write(self.project,OMO,'{// hello\n"agents":{"fixer":{"model":"mine","skills_add":["manual"],"mcps":["one"]}}}')
        self.init();text=(self.project/OMO).read_text();self.assertIn('// hello',text)
        conf=jsonc.parse(text).value['agents']['fixer'];self.assertEqual(conf['model'],'mine');self.assertEqual(conf['mcps'],['one'])
        self.assertEqual(conf['skills_add'],['manual','java-style'])

    def test_user_omo_changes_after_setup_preserved(self):
        self.init();text=(self.project/OMO).read_text();text=jsonc.set_value(text,('agents','fixer','model'),'new-model');write(self.project,OMO,text)
        code,out=self.cli('sync');self.assertEqual(code,0,out);self.assertEqual(out['result'],'NOOP');self.assertEqual((self.project/OMO).read_text(),text)

    def test_missing_owned_route_blocks(self):
        self.init();write(self.project,OMO,'{}');code,out=self.cli('sync');self.assertEqual((code,out['code']),(2,'MANAGED_MODIFIED'))

    def test_conditional_not_silently_accepted(self):
        code,out=self.cli('init','--profile','java','--repository',self.repository,'--ref',self.pin,'--addon','testing')
        self.assertEqual((code,out['code']),(2,'LIMITATIONS'));self.assertEqual(self.inventory(),{})

    def test_explicit_conditional_acceptance(self):
        out=self.init('--addon','testing','--accept-limitations','test-conditional')
        self.assertIn('test-conditional',out['limitations'])

    def test_unknown_profile_blocks(self):
        code,out=self.cli('init','--profile','unknown','--repository',self.repository,'--ref',self.pin)
        self.assertEqual((code,out['code']),(2,'SOURCE_MISSING'));self.assertEqual(self.inventory(),{})

    def test_unknown_addon_blocks(self):
        code,out=self.cli('init','--profile','java','--repository',self.repository,'--ref',self.pin,'--addon','unknown')
        self.assertEqual((code,out['code']),(2,'SOURCE_MISSING'))

    def test_project_agents_and_app_preserved(self):
        write(self.project,'AGENTS.md','user contract');write(self.project,'app.py','print(1)'); self.init()
        self.assertEqual((self.project/'AGENTS.md').read_text(),'user contract');self.assertEqual((self.project/'app.py').read_text(),'print(1)')

    def test_symlink_target_blocks(self):
        external=self.root/'external';external.mkdir();(self.project/'.agents').symlink_to(external,target_is_directory=True)
        code,out=self.cli('init','--profile','java','--repository',self.repository,'--ref',self.pin)
        self.assertEqual((code,out['code']),(2,'SYMLINK'));self.assertEqual(list(external.iterdir()),[])

    def test_tampered_lock_blocks(self):
        self.init();write(self.project,LOCK,'{}');code,out=self.cli('sync');self.assertEqual((code,out['code']),(2,'LOCK_MODIFIED'))

    def test_forged_receipt_path_blocks(self):
        self.init();receipt=load_json((self.project/RECEIPT).read_bytes());receipt['files']['../secret']='0'*64;write(self.project,RECEIPT,encoded(receipt))
        code,out=self.cli('sync');self.assertEqual(code,2);self.assertIn(out['code'],('STATE','UNSAFE_PATH'))

    def test_audit_does_not_write(self):
        self.init();before=self.inventory();code,out=self.cli('audit');self.assertEqual((code,out['result']),(0,'STATIC_MATCH'));self.assertEqual(before,self.inventory())

    def test_changed_manifest_audit_is_drift(self):
        self.init();spec=load_json((self.project/MANIFEST).read_bytes());spec['addons']=['spring'];write(self.project,MANIFEST,encoded(spec));before=self.inventory()
        code,out=self.cli('audit');self.assertEqual((code,out['result']),(1,'DRIFT'));self.assertEqual(before,self.inventory())

    def test_busy_project_lock(self):
        self.init();(self.project/'.agents/skills/java-style/SKILL.md').unlink();(self.project/'.veyrix/write.lock').mkdir()
        code,out=self.cli('sync');self.assertEqual((code,out['code']),(2,'BUSY'))

    def test_apply_rejects_floating_ref(self):
        code,out=self.cli('init','--profile','java','--repository',self.repository,'--ref','main')
        self.assertEqual((code,out['code']),(2,'PIN_REQUIRED'));self.assertEqual(self.inventory(),{})

    def test_preview_resolves_named_ref_without_apply(self):
        branch=git(self.source,'symbolic-ref','--short','HEAD')
        code,out=self.cli('init','--profile','java','--repository',self.repository,'--ref',branch,'--dry-run')
        self.assertEqual(code,0,out);self.assertEqual(out['commit'],self.new_pin);self.assertEqual(self.inventory(),{})

    def test_cache_inside_project_rejected(self):
        self.cache=self.project/'unsafe-cache'
        code,out=self.cli('init','--profile','java','--repository',self.repository,'--ref',self.pin)
        self.assertEqual((code,out['code']),(2,'CACHE_SCOPE'));self.assertFalse(self.cache.exists())

    def test_git_environment_does_not_redirect_cache(self):
        with patch.dict(os.environ,{'GIT_DIR':str(self.root/'wrong.git'),'GIT_WORK_TREE':str(self.root/'wrong')}):
            self.init()
        self.assertFalse((self.root/'wrong.git').exists())

    def test_legacy_file_symlink_rejected(self):
        (self.project/'.opencode').mkdir();(self.project/'.opencode/oh-my-opencode-slim.json').symlink_to(self.root/'absent')
        code,out=self.cli('init','--profile','java','--repository',self.repository,'--ref',self.pin)
        self.assertEqual((code,out['code']),(2,'LEGACY_OMO_CONFIG'))

    def test_info_does_not_modify_project(self):
        self.init();before=self.inventory();code,out=self.cli('info')
        self.assertEqual((code,out['result']),(0,'INFO'));self.assertEqual(before,self.inventory())

    def test_explicit_skill_exclusion_blocks(self):
        write(self.project,OMO,'{"agents":{"fixer":{"skills":["*","!java-style"]}}}')
        code,out=self.cli('init','--profile','java','--repository',self.repository,'--ref',self.pin)
        self.assertEqual((code,out['code']),(2,'ROUTING_DENIED'))

    def test_skill_symlink_blocks_without_target_write(self):
        self.init();target=self.project/'.agents/skills/java-style/SKILL.md';target.unlink()
        external=self.root/'external-file';external.write_text('outside');target.symlink_to(external)
        code,out=self.cli('sync');self.assertEqual((code,out['code']),(2,'SYMLINK'));self.assertEqual(external.read_text(),'outside')

    def test_source_metadata_not_executed(self):
        self.init();self.assertFalse((self.project/'src').exists());self.assertFalse((self.project/'tools').exists())

    def test_recovery_outside_project(self):
        output=self.init();backup=Path(output['recovery']);self.assertFalse(backup.is_relative_to(self.project))
        self.assertEqual(backup.stat().st_mode & 0o777,0o700)
        self.assertEqual(list(backup.rglob('SKILL.md')),[])

    def test_changed_after_plan_is_blocked(self):
        change=Plan(self.project);change.put('note.txt',b'new');write(self.project,'note.txt','concurrent')
        with self.assertRaises(Error) as exc: apply(change,self.cache)
        self.assertEqual(exc.exception.code,'CONCURRENT_CHANGE');self.assertEqual((self.project/'note.txt').read_text(),'concurrent')

    def test_apply_rollback_on_second_write_failure(self):
        write(self.project,'a.txt','old');change=Plan(self.project);change.put('a.txt',b'new');change.put('b.txt',b'new')
        from veyrix import deploy
        original=deploy._replace
        def fail(path,data,mode):
            if path.name=='b.txt' and data is not None: raise OSError('fixture failure')
            original(path,data,mode)
        with patch.object(deploy,'_replace',side_effect=fail),self.assertRaises(Error): apply(change,self.cache)
        self.assertEqual((self.project/'a.txt').read_text(),'old');self.assertFalse((self.project/'b.txt').exists())


if __name__ == '__main__': unittest.main()
