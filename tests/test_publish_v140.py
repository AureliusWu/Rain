import copy
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock
import zipfile
from tools.publish_v140 import (AUTH,BASELINE,HUMAN_PENDING,PUBLICATION_SUPPORT,REPO,SUPPORT,artifact_for,
    complete_items,digest,download_draft,extract_checked,find_draft,prepared_artifact,upload_window,
    validate_draft,validate_evidence_runs,validate_native,validate_prepared_metadata,validate_run,
    validate_source,validate_source_changes,validate_web,verify_public_worker)


class ExactV140PublicationTests(unittest.TestCase):
    def setUp(self):
        self.commit='a'*40
        self.run={'id':123,'run_attempt':1,'head_sha':self.commit,'head_branch':'main','event':'push',
            'path':'.github/workflows/game.yml','status':'completed','conclusion':'success',
            'repository':{'full_name':REPO}}
        self.job={'id':456,'run_id':123,'run_attempt':1,'head_sha':self.commit,'name':'web',
            'status':'completed','conclusion':'success','started_at':'2026-10-16T00:21:41Z',
            'completed_at':'2026-10-16T00:25:00Z','steps':[{'name':'Upload PWA','number':11,
                'status':'completed','conclusion':'success','started_at':'2026-10-16T00:24:51Z',
                'completed_at':'2026-10-16T00:24:54Z'}]}
        self.upload=upload_window([self.job],self.run,'web','Upload PWA')

    def test_only_successful_exact_main_native_run_is_accepted(self):
        validate_run(self.run,self.commit,'.github/workflows/game.yml')
        for key,value in [('head_sha',BASELINE),('head_branch','feature'),('event','pull_request'),
            ('conclusion','failure'),('status','in_progress'),('path','.github/workflows/web.yml'),
            ('run_attempt',0),('run_attempt',True),('repository',{'full_name':'Other/Rain'})]:
            with self.subTest(key=key),self.assertRaises(ValueError):
                validate_run({**self.run,key:value},self.commit,'.github/workflows/game.yml')

    def test_runtime_or_broad_tool_changes_cannot_use_prior_candidate(self):
        validate_source_changes(['docs/STATUS.md','tools/publish_v140.py'])
        for path in ['game/history_search.rpy','game/data/story.json','VERSION','tools/build/package.py',
            'scripts/pwa-native-browser.mjs','tools/release_gate.py','.github/workflows/game.yml']:
            with self.subTest(path=path),self.assertRaises(ValueError):validate_source_changes([path])
        for path in ['tools/build/export_review.py','tests/test_export_review.py',
            '.github/workflows/game.yml','.github/workflows/web.yml']:
            with self.subTest(path=path),self.assertRaises(ValueError):
                validate_source_changes([path],PUBLICATION_SUPPORT)

    def test_metadata_promotion_keeps_both_exact_support_snapshots(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            def git(*args):
                return subprocess.check_output(['git','-c','user.name=Fixture','-c','user.email=fixture@example.invalid',
                    *args],cwd=root,text=True).strip()
            def commit(message):
                git('add','.');git('commit','--quiet','-m',message)
                return git('rev-parse','HEAD')
            git('init','--quiet')
            # Hash fixtures must bind the exact worktree bytes on Windows too.
            git('config','core.autocrlf','false')
            for path in SUPPORT:
                target=root/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(path+'\n')
            (root/'VERSION').write_text('1.4.0\n')
            baseline=commit('baseline')
            (root/'docs').mkdir();(root/'docs/STATUS.md').write_text('runtime validated\n')
            runtime=commit('runtime evidence')
            runtime_hashes={path:digest(root/path) for path in SUPPORT}
            (root/'tools/publish_v140.py').write_text('publication-only fix\n')
            publication=commit('metadata promotion')
            auth={'schema':1,'version':'1.4.0','repository':REPO,'runtime_baseline':runtime,
                'publication_authorized':True,'user_instruction':'全部完成更新推送闭环',
                'human_acceptance_claimed':False,'human_pending':HUMAN_PENDING,
                'support_sha256':{path:digest(root/path) for path in SUPPORT},
                'runtime_validation':{'commit':runtime,'support_sha256':runtime_hashes}}
            with mock.patch('tools.publish_v140.ROOT',root),mock.patch('tools.publish_v140.BASELINE',runtime):
                result=validate_source(publication,runtime,auth)
                self.assertEqual(result['publication_difference'],['tools/publish_v140.py'])
                self.assertEqual(result['runtime_baseline_difference'],[])
                for section in ['support_sha256']:
                    bad=copy.deepcopy(auth)
                    hashes=bad[section] if section=='support_sha256' else bad[section]['support_sha256']
                    hashes['tools/publish_v140.py']='0'*64
                    with self.subTest(section=section),self.assertRaises(ValueError):
                        validate_source(publication,runtime,bad)
                with self.assertRaises(ValueError):validate_source(publication,baseline,auth)
                with self.assertRaises(ValueError):validate_source(runtime,runtime,auth)
                (root/'tools/publish_v140.py').write_text('uncommitted executable change\n')
                with self.assertRaises(ValueError):validate_source(publication,runtime,auth)
                git('checkout','--','tools/publish_v140.py')
                (root/'tools/build').mkdir(exist_ok=True);(root/'tools/build/export_review.py').write_text('post-validation audit change\n')
                changed=commit('not publication metadata')
                bad=copy.deepcopy(auth);bad['support_sha256']['tools/build/export_review.py']=digest(root/'tools/build/export_review.py')
                with self.assertRaises(ValueError):validate_source(changed,runtime,bad)

    def test_completed_review_rerun_preserves_original_successful_native_attempt(self):
        web={**self.run,'id':789,'run_attempt':2,'path':'.github/workflows/web.yml'}
        auth={'runtime_validation':{'native_run':{'id':123,'artifact_attempt':1},
            'pwa_run':{'id':789,'attempt':2}}}
        validate_evidence_runs({**self.run,'run_attempt':2},self.run,web,self.commit,auth)
        for native,origin,pwa in [
            ({**self.run,'conclusion':'failure'},self.run,web),
            (self.run,{**self.run,'conclusion':'failure'},web),
            (self.run,{**self.run,'run_attempt':2},web),
            (self.run,self.run,{**web,'run_attempt':1}),
            (self.run,self.run,{**web,'conclusion':'failure'}),
            (self.run,self.run,{**web,'head_sha':BASELINE})]:
            with self.subTest(native=native,origin=origin,pwa=pwa),self.assertRaises(ValueError):
                validate_evidence_runs(native,origin,pwa,self.commit,auth)

    def test_upload_window_requires_exact_successful_attempt_job_and_step(self):
        self.assertEqual(self.upload['job_id'],456)
        changes=[{'run_attempt':2},{'run_id':124},{'head_sha':BASELINE},{'conclusion':'failure'},
            {'steps':[{**self.job['steps'][0],'conclusion':'skipped'}]},
            {'steps':[{**self.job['steps'][0],'started_at':'2026-10-16T00:18:00Z'}]},
            {'steps':[{**self.job['steps'][0],'completed_at':'2026-10-16T00:25:01Z'}]},
            {'steps':[{**self.job['steps'][0],'started_at':None}]},
            {'steps':self.job['steps']*2}]
        for change in changes:
            with self.subTest(change=change),self.assertRaises(ValueError):
                upload_window([{**self.job,**change}],self.run,'web','Upload PWA')
        with self.assertRaises(ValueError):upload_window([self.job,self.job],self.run,'web','Upload PWA')
        with self.assertRaises(ValueError):upload_window([],self.run,'web','Upload PWA')

    def test_partial_api_pages_cannot_hide_ambiguous_jobs_or_artifacts(self):
        self.assertEqual(complete_items({'total_count':1,'jobs':[self.job]},'jobs'),[self.job])
        for response in [{'total_count':2,'jobs':[self.job]},{'jobs':[self.job]},
            {'total_count':True,'jobs':[self.job]}]:
            with self.subTest(response=response),self.assertRaises(ValueError):complete_items(response,'jobs')

    def test_artifact_is_bound_to_run_commit_and_digest(self):
        item={'id':1,'name':'windows-'+self.commit,'expired':False,'digest':'sha256:'+'b'*64,
            'created_at':'2026-10-16T00:24:54Z','workflow_run':{'id':123,'head_sha':self.commit}}
        self.assertEqual(artifact_for([item],item['name'],123,self.commit,self.upload),item)
        for change in [{'expired':True},{'digest':None},{'workflow_run':{'id':124,'head_sha':self.commit}},
            {'workflow_run':{'id':123,'head_sha':BASELINE}},{'id':0},{'created_at':None}]:
            with self.subTest(change=change),self.assertRaises(ValueError):
                artifact_for([{**item,**change}],item['name'],123,self.commit,self.upload)
        with self.assertRaises(ValueError):artifact_for([item,item],item['name'],123,self.commit,self.upload)

    def test_same_name_from_failed_attempt_is_excluded_by_successful_upload_time(self):
        failed={'id':12015833673,'name':'Rain-Web-'+self.commit,'expired':False,'digest':'sha256:'+'b'*64,
            'created_at':'2026-10-16T00:18:56Z','workflow_run':{'id':123,'head_sha':self.commit}}
        passed={**failed,'id':12016850530,'created_at':'2026-10-16T00:24:54Z'}
        self.assertEqual(artifact_for([passed,failed],passed['name'],123,self.commit,self.upload),passed)
        self.assertEqual(artifact_for([failed,passed],passed['name'],123,self.commit,self.upload),passed)
        for items in [[failed],[passed,passed],[{**passed,'created_at':'2026-10-16T00:24:55Z'}]]:
            with self.subTest(items=items),self.assertRaises(ValueError):
                artifact_for(items,passed['name'],123,self.commit,self.upload)
        with self.assertRaises(ValueError):
            artifact_for([passed],passed['name'],123,self.commit,{**self.upload,'run_id':124})

    def test_archive_traversal_duplicate_and_symlink_are_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for index,name in enumerate(['../escape','/absolute','C:/drive','a\\b']):
                archive=root/f'{index}.zip'
                # ZipInfo normalizes backslashes on Windows. Write the raw
                # illegal member name into both ZIP headers on either host.
                with zipfile.ZipFile(archive,'w') as bundle:bundle.writestr(name.replace('\\','/'),'bad')
                if '\\' in name:archive.write_bytes(archive.read_bytes().replace(name.replace('\\','/').encode(),name.encode()))
                with zipfile.ZipFile(archive) as bundle:self.assertEqual([i.orig_filename for i in bundle.infolist()],[name])
                with self.subTest(name=name),self.assertRaises(ValueError):extract_checked(archive,root/'out')
            archive=root/'link.zip'
            with zipfile.ZipFile(archive,'w') as bundle:
                entry=zipfile.ZipInfo('link');entry.external_attr=0o120777<<16;bundle.writestr(entry,'target')
            with self.assertRaises(ValueError):extract_checked(archive,root/'out')

    def test_native_requires_all_current_history_cases_and_real_upgrade(self):
        with tempfile.TemporaryDirectory() as temp:
            package=Path(temp)/'BeforeTheRainStops-1.4.0-win.zip'
            with zipfile.ZipFile(package,'w') as bundle:bundle.writestr('game/build','fixture')
            def suite(c,a,s):return dict(cases=c,assertions=a,screenshots_checked=s,
                failed=0,xfailed=0,xpassed=0,skipped=0,not_run=0,process={'returncode':0,'timed_out':False})
            machine={'version':'1.4.0','candidate_commit':self.commit,'run_id':123,
                'status':'technical_passed_visual_pending','human_acceptance_is_not_claimed':True,
                'human_pending':HUMAN_PENDING,'unresolved_machine_issues':[],
                'suites':{'source':suite(37,498,87),'standalone':suite(37,498,87),
                    'fresh_process':suite(1,17,3),'upgrade_writer':suite(1,14,3),'upgrade_reader':suite(2,26,4)},
                'screenshots_count':184,'screenshots':[{'scope':'source','name':'cg-cafe-photo'},
                    {'scope':'standalone','name':'cg-cafe-photo'}]+[{}]*182,
                'extras':{'images':6,'music_tracks':4},
                'voice_smoke':{'status':'passed','iterations':[suite(7,149,33),suite(7,149,33)]},
                'package':{'file':package.name,'sha256':digest(package),'size_in_bytes':package.stat().st_size,
                    'crc':'passed','assets_checked':87,'test_scripts_in_original_zip':False},
                'upgrade':{'status':'passed','package_sha256':{'current':digest(package)}}}
            validate_native(machine,self.commit,123,package)
            for key,value in [('cases',36),('cases',37.0),('assertions',448),('screenshots_checked',82),('failed',1),('skipped',1)]:
                bad=copy.deepcopy(machine);bad['suites']['standalone'][key]=value
                with self.subTest(key=key),self.assertRaises(ValueError):validate_native(bad,self.commit,123,package)
            for field,value in [('images',5),('music_tracks',3)]:
                bad=copy.deepcopy(machine);bad['extras'][field]=value
                with self.subTest(field=field),self.assertRaises(ValueError):
                    validate_native(bad,self.commit,123,package)
            bad=copy.deepcopy(machine);bad['screenshots'][1]['name']='old-scene'
            with self.assertRaises(ValueError):validate_native(bad,self.commit,123,package)
            bad=copy.deepcopy(machine);bad['package']['assets_checked']=85
            with self.assertRaises(ValueError):validate_native(bad,self.commit,123,package)
            bad=copy.deepcopy(machine);bad['upgrade']['package_sha256']['current']='0'*64
            with self.assertRaises(ValueError):validate_native(bad,self.commit,123,package)

    def test_pwa_public_revision_errors_and_exact_bytes_are_checked(self):
        with tempfile.TemporaryDirectory() as temp:
            package=Path(temp)/'web.zip'
            with zipfile.ZipFile(package,'w') as bundle:bundle.writestr('index.html','fixture')
            build={'status':'built','version':'1.4.0','engine':'RenPy 8.5.3 official WASM',
                'web_sdk_sha256':'954db897e65f51ea63cb2fb7b203d02be0447f4e22069514020bbe6c6691fdfc',
                'web_zip_sha256':digest(package),'official_runtime_validation':{'game_zip_crc':'passed'},'revision':'fixed'}
            acceptance={'status':'passed','version':'1.4.0','checks':['case']*16,'errors':[],'requests_outside_application':[]}
            public={'status':'passed','version':'1.4.0','revision':'fixed','errors':[],
                'target':'https://aureliuswu.github.io/Rain/','exact_tested_artifact':True,'human_physical_device':False}
            validate_web(build,acceptance,public,package)
            with self.assertRaises(ValueError):validate_web(build,acceptance,{**public,'revision':'old'},package)
            with self.assertRaises(ValueError):validate_web(build,{**acceptance,'errors':['pageerror']},public,package)
            with self.assertRaises(ValueError):validate_web({**build,'web_zip_sha256':'0'*64},acceptance,public,package)

    def test_current_public_worker_must_equal_the_exact_tested_package(self):
        with tempfile.TemporaryDirectory() as temp:
            package=Path(temp)/'web.zip'
            worker=b'const BUILD = {"version":"1.4.0","revision":"tested"};\n'
            with zipfile.ZipFile(package,'w') as bundle:bundle.writestr('service-worker.js',worker)
            with mock.patch('urllib.request.urlopen',return_value=io.BytesIO(worker)) as fetch:
                result=verify_public_worker({'revision':'tested'},package)
                self.assertEqual(result['status'],'exact_tested_bytes_verified')
                self.assertEqual(result['revision'],'tested')
                self.assertEqual(fetch.call_args.args[0].full_url,'https://aureliuswu.github.io/Rain/service-worker.js')
            for actual in [worker.replace(b'tested',b'newer'),worker+b' ',b'x'*1_048_577]:
                with self.subTest(bytes=len(actual)),mock.patch('urllib.request.urlopen',return_value=io.BytesIO(actual)):
                    with self.assertRaises(ValueError):verify_public_worker({'revision':'tested'},package)
            with self.assertRaises(ValueError):verify_public_worker({'revision':'other'},package)
            with zipfile.ZipFile(package,'w') as bundle:bundle.writestr('service-worker.js',worker*2)
            with self.assertRaises(ValueError):verify_public_worker({'revision':'tested'},package)

    def test_draft_is_found_by_release_id_without_the_published_tag_endpoint(self):
        draft={'id':456,'tag_name':'v1.4.0','draft':True,'prerelease':False}
        self.assertEqual(find_draft([{'tag_name':'v1.1.1'},draft],'v1.4.0'),draft)
        for releases in [[],[draft,draft],[{**draft,'draft':False}],[{**draft,'prerelease':True}]]:
            with self.subTest(releases=releases),self.assertRaises(ValueError):find_draft(releases,'v1.4.0')

    def test_prepared_draft_requires_the_original_asset_ids_and_digests(self):
        expected={'package.zip':{'id':789,'sha256':'a'*64,'bytes':3}}
        asset={'id':789,'name':'package.zip','digest':'sha256:'+'a'*64,'size':3}
        draft={'tag_name':'v1.4.0','draft':True,'prerelease':False,'assets':[asset]}
        validate_draft(draft,'v1.4.0',expected)
        for change in [{'draft':False},{'tag_name':'v1.1.1'},{'assets':[]},{'assets':[asset,asset]},
            {'assets':[{**asset,'id':790}]},{'assets':[{**asset,'digest':'sha256:'+'b'*64}]},
            {'assets':[{**asset,'size':4}]}]:
            with self.subTest(change=change),self.assertRaises(ValueError):
                validate_draft({**draft,**change},'v1.4.0',expected)

    def test_draft_download_uses_authenticated_asset_ids_and_checks_actual_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);fixture=root/'fixture';fixture.write_bytes(b'raw')
            expected={'package.zip':{'id':789,'sha256':digest(fixture),'bytes':3}}
            draft={'tag_name':'v1.4.0','draft':True,'prerelease':False,
                'assets':[{'id':789,'name':'package.zip','digest':'sha256:'+digest(fixture),'size':3}]}
            def transfer(command,stdout,check):
                self.assertEqual(command,['gh','api','-H','Accept: application/octet-stream',
                    'repos/'+REPO+'/releases/assets/789'])
                stdout.write(b'raw')
            with mock.patch('tools.publish_v140.subprocess.run',side_effect=transfer):
                download_draft(draft,root/'good',expected)
            def tampered(command,stdout,check):stdout.write(b'bad')
            with mock.patch('tools.publish_v140.subprocess.run',side_effect=tampered):
                with self.assertRaises(ValueError):download_draft(draft,root/'bad',expected)

    def test_preparation_artifact_is_pinned_to_the_failed_publisher_and_original_source(self):
        pin={'id':456,'name':'publication','digest':'sha256:'+'a'*64,'bytes':123,'run_id':789,'run_attempt':1}
        run={**self.run,'id':789,'path':'.github/workflows/release-v140.yml','event':'workflow_run','conclusion':'failure'}
        item={'id':456,'name':'publication','digest':pin['digest'],'size_in_bytes':123,'expired':False,
            'workflow_run':{'id':789,'head_sha':self.commit}}
        self.assertEqual(prepared_artifact(item,run,pin,self.commit),item)
        for change in [{'id':457},{'expired':True},{'digest':'sha256:'+'b'*64},
            {'workflow_run':{'id':789,'head_sha':BASELINE}}]:
            with self.subTest(change=change),self.assertRaises(ValueError):
                prepared_artifact({**item,**change},run,pin,self.commit)
        for change in [{'id':790},{'run_attempt':2},{'head_sha':BASELINE},{'conclusion':'success'},
            {'repository':{'full_name':'Other/Rain'}}]:
            with self.subTest(change=change),self.assertRaises(ValueError):
                prepared_artifact(item,{**run,**change},pin,self.commit)

    def test_recovery_metadata_keeps_original_source_authorization_and_all_accepted_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            def git(*args):
                return subprocess.check_output(['git','-c','user.name=Fixture','-c','user.email=fixture@example.invalid',
                    *args],cwd=root,text=True).strip()
            def commit(message):
                git('add','.');git('commit','--quiet','-m',message)
                return git('rev-parse','HEAD')
            git('init','--quiet')
            # Hash fixtures must bind the exact worktree bytes on Windows too.
            git('config','core.autocrlf','false')
            for path in SUPPORT:
                target=root/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(path+'\n')
            runtime=commit('complete tested runtime')
            (root/'tools/publish_v140.py').write_text('preparation publisher\n')
            previous={'runtime_validation':{'commit':runtime},'support_sha256':{path:digest(root/path) for path in SUPPORT}}
            auth_file=root/AUTH;auth_file.parent.mkdir(parents=True);auth_file.write_text(json.dumps(previous))
            publication=commit('original draft preparation')
            paths=git('diff','--name-only',runtime,publication).splitlines()
            record={'schema':1,'project':'Rain','version':'1.4.0','tag':'v1.4.0','runtime_baseline':runtime,
                'publication_commit':publication,'runtime_commit':runtime,'tag_commit':runtime,
                'human_acceptance_claimed':False,'human_pending':HUMAN_PENDING,
                'publication_authorization':previous,
                'source_difference':{'runtime_baseline_difference':[],'publication_difference':paths},
                'native_run':{'id':123,'url':'native','artifact_attempt':1,'completed_attempt':2},
                'pwa_run':{'id':789,'url':'web','attempt':2}}
            for field in ('artifacts','artifact_upload_steps','files','native_suites','native_screenshot_audit',
                'pwa_build','pwa_acceptance','published_pwa','current_public_worker','visual_review','source_identity'):
                record[field]={'accepted':field}
            (root/'tools/publish_v140.py').write_text('completion publisher\n')
            completion=commit('draft API recovery only')
            expected=copy.deepcopy(record);expected['publication_commit']=completion
            expected['native_run']['completed_attempt']=3
            with mock.patch('tools.publish_v140.ROOT',root),mock.patch('tools.publish_v140.BASELINE',runtime):
                validate_prepared_metadata(record,publication,runtime,previous,expected)
                changes=[('runtime_commit',BASELINE),('human_acceptance_claimed',True),
                    ('publication_authorization',{}),('source_difference',{})]
                changes.extend((field,{}) for field in ('artifacts','artifact_upload_steps','files','native_suites',
                    'native_screenshot_audit','pwa_build','pwa_acceptance','published_pwa','current_public_worker',
                    'visual_review','source_identity','pwa_run'))
                changes.append(('native_run',{**record['native_run'],'completed_attempt':4}))
                for field,value in changes:
                    bad=copy.deepcopy(record);bad[field]=value
                    with self.subTest(field=field),self.assertRaises(ValueError):
                        validate_prepared_metadata(bad,publication,runtime,previous,expected)
                original=subprocess.check_output
                def changed_blob(command,**kwargs):
                    if command==['git','show',publication+':tools/publish_v140.py']:return b'tampered support'
                    return original(command,**kwargs)
                with mock.patch('tools.publish_v140.subprocess.check_output',side_effect=changed_blob):
                    with self.assertRaises(ValueError):validate_prepared_metadata(record,publication,runtime,previous,expected)


if __name__=='__main__':unittest.main()
