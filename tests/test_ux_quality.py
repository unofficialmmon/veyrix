from __future__ import annotations
import contextlib, io, json, os, shutil, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import veyrix
from veyrix import jsonc
from veyrix.cli import main
from veyrix.common import Error
from veyrix.provenance import installed_pin
from test_veyrix import REPO, commit, initialize, write

class Metadata:
    version=veyrix.__version__
    def __init__(self,url,sha): self.url,self.sha=url,sha
    def read_text(self,name):
        return json.dumps({"url":self.url,"vcs_info":{"vcs":"git","commit_id":self.sha,"requested_revision":"main"}})
    def locate_file(self,name): return Path(veyrix.__file__)

class FrozenUXQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_temp=tempfile.TemporaryDirectory(); cls.source=Path(cls.source_temp.name)/"source"
        shutil.copytree(REPO,cls.source,ignore=shutil.ignore_patterns(".git","__pycache__","*.egg-info"))
        initialize(cls.source); cls.pin=commit(cls.source); cls.repository=cls.source.as_uri()
    @classmethod
    def tearDownClass(cls): cls.source_temp.cleanup()
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
        self.project=self.root/"project"; initialize(self.project)
        self.cache=self.root/"cache"; self.home=self.root/"home"; self.home.mkdir()
        self.env=patch.dict(os.environ,{"HOME":str(self.home),"XDG_CONFIG_HOME":str(self.home/".config"),
                                        "OPENCODE_CONFIG_DIR":str(self.home/".config/opencode")}); self.env.start()
    def tearDown(self): self.env.stop(); self.tmp.cleanup()
    def cli(self,*args,offline=False):
        argv=["--project",str(self.project),"--cache-dir",str(self.cache),"--allow-local-source"]
        if offline: argv+=["--offline"]
        with contextlib.redirect_stdout(io.StringIO()) as out: code=main(argv+list(args))
        return code,json.loads(out.getvalue())
    def init(self,*extra):
        code,out=self.cli("init","--profile","java","--repository",self.repository,"--ref",self.pin,*extra)
        self.assertEqual(code,0,out); return out
    def inventory(self):
        return {p.relative_to(self.project).as_posix():p.read_bytes() for p in self.project.rglob("*")
                if p.is_file() and ".git" not in p.relative_to(self.project).parts}

    def test_installed_provenance_uses_commit_not_requested_revision(self):
        with patch("veyrix.provenance.distribution",return_value=Metadata(self.repository,self.pin)):
            self.assertEqual(installed_pin(self.repository,True),self.pin)

    def test_profiles_and_addons_are_read_only_and_pinned(self):
        with patch("veyrix.provenance.distribution",return_value=Metadata(self.repository,self.pin)):
            code,out=self.cli("profiles","--repository",self.repository)
        self.assertEqual(code,0,out); self.assertEqual(out["commit"],self.pin)
        self.assertIn("java",[x["id"] for x in out["profiles"]]); self.assertEqual(self.inventory(),{})

    def test_quality_addon_materializes_three_skills_and_routes(self):
        out=self.init("--addon","engineering-quality")
        expected={"engineering-quality","regression-proof","security-review"}
        self.assertTrue(expected<=set(out["skills"])); self.assertEqual(set(out["routes"]["oracle"]),expected)
        for name in expected: self.assertTrue((self.project/".agents/skills"/name/"SKILL.md").is_file())
        self.assertEqual(out["host_runtime"],"NOT_RUN")

    def test_quality_removal_preserves_manual_omo_and_agents(self):
        write(self.project,"AGENTS.md","project-owned\n")
        write(self.project,".opencode/oh-my-opencode-slim.jsonc",
              '{"agents":{"oracle":{"model":"manual","skills_add":["outside"]}}}')
        self.init("--addon","engineering-quality")
        spec=json.loads((self.project/"veyrix.yml").read_bytes()); spec["addons"]=[]
        write(self.project,"veyrix.yml",json.dumps(spec,indent=2,sort_keys=True)+"\n")
        code,out=self.cli("sync"); self.assertEqual(code,0,out)
        conf=jsonc.parse((self.project/".opencode/oh-my-opencode-slim.jsonc").read_text()).value["agents"]["oracle"]
        self.assertEqual(conf["skills_add"],["outside"]); self.assertEqual(conf["model"],"manual")
        self.assertEqual((self.project/"AGENTS.md").read_text(),"project-owned\n")

    def test_doctor_is_cache_only_and_reports_static_health(self):
        self.init("--addon","engineering-quality"); before=self.inventory()
        code,out=self.cli("doctor"); self.assertEqual((code,out["result"]),(0,"HEALTHY"),out)
        self.assertEqual(out["source_access"],"CACHE_ONLY"); self.assertEqual(out["host_runtime"],"NOT_RUN")
        self.assertEqual(before,self.inventory())

    def test_actionable_error_keeps_existing_code(self):
        code,out=self.cli("sync")
        self.assertEqual((code,out["code"]),(2,"NOT_INITIALIZED")); self.assertTrue(out["next_action"])

    def test_modified_quality_file_blocks_removal(self):
        self.init("--addon","engineering-quality")
        write(self.project,".agents/skills/security-review/SKILL.md","user edit")
        spec=json.loads((self.project/"veyrix.yml").read_bytes()); spec["addons"]=[]
        write(self.project,"veyrix.yml",json.dumps(spec,indent=2,sort_keys=True)+"\n")
        before=self.inventory(); code,out=self.cli("sync")
        self.assertEqual((code,out["code"]),(2,"MANAGED_MODIFIED")); self.assertEqual(before,self.inventory())

if __name__=="__main__": unittest.main()
