"""Run the learner's code locally. Never sends code or scores over a network."""
import argparse
import datetime
import json
import os
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser(description='AI Interview Lab — offline practice checks')
    p.add_argument('lab',choices=['retrieval','all'])
    p.add_argument('--reference',action='store_true',help='check supplied solutions instead of your exercises')
    p.add_argument('--report',type=Path,help='write a local JSON result; refuses overwrite')
    args=p.parse_args()
    if args.report and args.report.exists():p.error('report exists; use a new filename')
    os.environ['INTERVIEW_LAB_MODE']='solutions' if args.reference else 'exercises'
    suite=unittest.defaultTestLoader.discover(str(ROOT/'checks'),pattern='test_*.py' if args.lab=='all' else 'test_'+args.lab+'.py')
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    count=result.testsRun
    passed=result.wasSuccessful() and count>0 and not result.skipped
    if args.report:
        payload={'edition':'1.0','lab':args.lab,'mode':os.environ['INTERVIEW_LAB_MODE'],'tests':count,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'passed':passed,'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'note':'Practice checks only. Not a hiring-readiness or pass-probability score.'}
        with args.report.open('x') as f:json.dump(payload,f,indent=2)
    print('Practice checks passed.' if passed else 'Practice checks need work. Read the failure and the exercise contract.')
    return 0 if passed else 1

if __name__=='__main__':sys.exit(main())
