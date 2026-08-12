#!/usr/bin/env python3
"""Offline contract and target-policy tests for the canonical adapter."""
from __future__ import annotations
import importlib.util, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
WORKFLOW=(ROOT/'.github/workflows/codex-execute.yml').read_text()

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); module=importlib.util.module_from_spec(spec)
    assert spec.loader; sys.modules[name]=module; spec.loader.exec_module(module); return module
policy=load('policy',ROOT/'scripts/codex_repository_policy.py')
publication=load('publication',ROOT/'scripts/codex_publication.py')

def payload(**changes):
    value={'contract_version':'ai-sdlc-contract/v2','target_repository':'Young-Consultations/consulting-playbook','executor':'codex','execution_mode':'implement','task_type':'documentation','draft_pr_only':True,'delivery_id':'delivery-42','correlation_id':'corr-42','task_id':'TASK-42','source_issue':'Young-Consultations/portfolio-tasks#42','project_component':'documentation'}
    value.update(changes); return value

def validate(value): return policy.validate_policy(value,'Young-Consultations/consulting-playbook')
def rejected(**changes):
    try: validate(payload(**changes))
    except ValueError: return
    raise AssertionError('request was not rejected')

def metadata(**changes):
    result={'delivery_id':'delivery-42','payload_digest':validate(payload())['payload_digest'],'target_repository':'Young-Consultations/consulting-playbook','branch':policy.delivery_branch('delivery-42'),'source_issue':'Young-Consultations/portfolio-tasks#42'}; result.update(changes); return result

def pr(data,**changes):
    value={'url':'https://example.test/1','state':'OPEN','isDraft':True,'body':publication.marker(data)}; value.update(changes); return value

class Fake:
    def __init__(self,branch=False,prs=()): self.branch,self.prs,self.creates=branch,list(prs),0
    def branch_exists(self,*_): return self.branch
    def pull_requests(self,*_): return list(self.prs)
    def create_draft(self,*_): self.creates+=1; return 'https://example.test/1'

def test_pin_and_single_interface():
    assert WORKFLOW.count('c6090e5bbadcc2102a1cb91875466e9decdada1e')==2
    inputs=WORKFLOW.split('    inputs:',1)[1].split('    secrets:',1)[0]
    assert 'execution_input_json:' in inputs and 'concurrency_group:' in inputs
    assert 'enabled' not in WORKFLOW and 'registry-disabled' not in WORKFLOW

def test_target_policy_rejections():
    for change in ({'target_repository':'x/y'},{'contract_version':'v1'},{'executor':'other'},{'execution_mode':'run'},{'task_type':'unknown'},{'draft_pr_only':False}): rejected(**change)

def test_branch_and_digest_are_delivery_bound():
    first=validate(payload()); second=validate(payload(project_component='changed'))
    assert first['branch']==second['branch'] and first['payload_digest']!=second['payload_digest']
    assert policy.delivery_branch('a/b')!=policy.delivery_branch('a-b')

def test_matching_draft_reuse_and_conflicts():
    data=metadata(); decision=publication.classify(Fake(True,[pr(data)]),data)
    assert decision.state=='reuse-completed-delivery'
    changed=metadata(payload_digest='0'*64)
    assert publication.classify(Fake(True,[pr(changed)]),data).state=='ambiguous'
    assert publication.classify(Fake(True,[pr(data),pr(data,url='https://example.test/2')]),data).state=='ambiguous'

def test_ambiguous_remote_states_fail_closed():
    data=metadata()
    assert publication.classify(Fake(True),data).failure_category=='orphaned_branch'
    assert publication.classify(Fake(True,[pr(data,state='CLOSED')]),data).failure_category=='manual_recovery_required'

def test_verify_has_no_codex_or_publication_path():
    verify=WORKFLOW.split('Verify repository without effects',1)[1].split('Create deterministic local branch',1)[0]
    assert 'run-codex' not in verify and 'git push' not in verify and 'codex_publication.py publish' not in verify

def test_security_and_receiver_boundaries():
    assert 'secrets: inherit' not in WORKFLOW
    assert 'gh pr merge' not in WORKFLOW and 'git push origin main' not in WORKFLOW
    assert 'timeout-minutes: 40' in WORKFLOW
    assert 'jsonschema[format]' in WORKFLOW
    assert 'codex-result-receiver.yml@c6090e5bbadcc2102a1cb91875466e9decdada1e' in WORKFLOW

if __name__=='__main__':
    tests=[v for k,v in sorted(globals().items()) if k.startswith('test_')]
    for test in tests: test()
    print(f'passed {len(tests)} target-adapter checks')
