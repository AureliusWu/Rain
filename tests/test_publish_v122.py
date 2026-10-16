import copy
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from tools.publish_v122 import (BASELINE,HUMAN_PENDING,REPO,artifact_for,digest,
    extract_checked,validate_native,validate_run,validate_source_changes,validate_web)


class ExactV122PublicationTests(unittest.TestCase):
    def setUp(self):
        self.commit='a'*40
        self.run={'id':123,'head_sha':self.commit,'head_branch':'main','event':'push',
            'path':'.github/workflows/game.yml','status':'completed','conclusion':'success',
            'repository':{'full_name':REPO}}

    def test_only_successful_exact_main_native_run_is_accepted(self):
        validate_run(self.run,self.commit,'.github/workflows/game.yml')
        for key,value in [('head_sha',BASELINE),('head_branch','feature'),('event','pull_request'),
            ('conclusion','failure'),('status','in_progress'),('path','.github/workflows/web.yml')]:
            with self.subTest(key=key),self.assertRaises(ValueError):
                validate_run({**self.run,key:value},self.commit,'.github/workflows/game.yml')

    def test_runtime_or_broad_tool_changes_cannot_use_prior_candidate(self):
        validate_source_changes(['docs/STATUS.md','tools/publish_v122.py','tools/build/export_review.py'])
        for path in ['game/history_search.rpy','game/data/story.json','VERSION','tools/build/package.py',
            'scripts/pwa-native-browser.mjs','tools/release_gate.py','.github/workflows/game.yml']:
            with self.subTest(path=path),self.assertRaises(ValueError):validate_source_changes([path])

    def test_artifact_is_bound_to_run_commit_and_digest(self):
        item={'id':1,'name':'windows-'+self.commit,'expired':False,'digest':'sha256:'+'b'*64,
            'workflow_run':{'id':123,'head_sha':self.commit}}
        self.assertEqual(artifact_for([item],item['name'],123,self.commit),item)
        for change in [{'expired':True},{'digest':None},{'workflow_run':{'id':124,'head_sha':self.commit}},
            {'workflow_run':{'id':123,'head_sha':BASELINE}}]:
            with self.subTest(change=change),self.assertRaises(ValueError):
                artifact_for([{**item,**change}],item['name'],123,self.commit)
        with self.assertRaises(ValueError):artifact_for([item,item],item['name'],123,self.commit)

    def test_archive_traversal_duplicate_and_symlink_are_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for index,name in enumerate(['../escape','/absolute','C:/drive','a\\b']):
                archive=root/f'{index}.zip'
                with zipfile.ZipFile(archive,'w') as bundle:bundle.writestr(name,'bad')
                with self.subTest(name=name),self.assertRaises(ValueError):extract_checked(archive,root/'out')
            archive=root/'link.zip'
            with zipfile.ZipFile(archive,'w') as bundle:
                entry=zipfile.ZipInfo('link');entry.external_attr=0o120777<<16;bundle.writestr(entry,'target')
            with self.assertRaises(ValueError):extract_checked(archive,root/'out')

    def test_native_requires_all_current_history_cases_and_real_upgrade(self):
        with tempfile.TemporaryDirectory() as temp:
            package=Path(temp)/'BeforeTheRainStops-1.2.2-win.zip'
            with zipfile.ZipFile(package,'w') as bundle:bundle.writestr('game/build','fixture')
            def suite(c,a,s):return dict(cases=c,assertions=a,screenshots_checked=s,
                failed=0,xfailed=0,xpassed=0,skipped=0,not_run=0,process={'returncode':0,'timed_out':False})
            machine={'version':'1.2.2','candidate_commit':self.commit,'run_id':123,
                'status':'technical_passed_visual_pending','human_acceptance_is_not_claimed':True,
                'human_pending':HUMAN_PENDING,'unresolved_machine_issues':[],
                'suites':{'source':suite(37,477,84),'standalone':suite(37,477,84),
                    'fresh_process':suite(1,16,3),'upgrade_writer':suite(1,14,3),'upgrade_reader':suite(2,26,4)},
                'screenshots_count':178,'screenshots':[{}]*178,
                'voice_smoke':{'status':'passed','iterations':[suite(7,132,31),suite(7,132,31)]},
                'package':{'file':package.name,'sha256':digest(package),'size_in_bytes':package.stat().st_size,
                    'crc':'passed','assets_checked':85,'test_scripts_in_original_zip':False},
                'upgrade':{'status':'passed','package_sha256':{'current':digest(package)}}}
            validate_native(machine,self.commit,123,package)
            for key,value in [('cases',36),('cases',37.0),('assertions',448),('screenshots_checked',82),('failed',1),('skipped',1)]:
                bad=copy.deepcopy(machine);bad['suites']['standalone'][key]=value
                with self.subTest(key=key),self.assertRaises(ValueError):validate_native(bad,self.commit,123,package)
            bad=copy.deepcopy(machine);bad['upgrade']['package_sha256']['current']='0'*64
            with self.assertRaises(ValueError):validate_native(bad,self.commit,123,package)

    def test_pwa_public_revision_errors_and_exact_bytes_are_checked(self):
        with tempfile.TemporaryDirectory() as temp:
            package=Path(temp)/'web.zip'
            with zipfile.ZipFile(package,'w') as bundle:bundle.writestr('index.html','fixture')
            build={'status':'built','version':'1.2.2','engine':'RenPy 8.5.3 official WASM',
                'web_sdk_sha256':'954db897e65f51ea63cb2fb7b203d02be0447f4e22069514020bbe6c6691fdfc',
                'web_zip_sha256':digest(package),'official_runtime_validation':{'game_zip_crc':'passed'},'revision':'fixed'}
            acceptance={'status':'passed','version':'1.2.2','checks':['case']*14,'errors':[],'requests_outside_application':[]}
            public={'status':'passed','version':'1.2.2','revision':'fixed','errors':[],
                'target':'https://aureliuswu.github.io/Rain/','exact_tested_artifact':True,'human_physical_device':False}
            validate_web(build,acceptance,public,package)
            with self.assertRaises(ValueError):validate_web(build,acceptance,{**public,'revision':'old'},package)
            with self.assertRaises(ValueError):validate_web(build,{**acceptance,'errors':['pageerror']},public,package)
            with self.assertRaises(ValueError):validate_web({**build,'web_zip_sha256':'0'*64},acceptance,public,package)


if __name__=='__main__':unittest.main()
