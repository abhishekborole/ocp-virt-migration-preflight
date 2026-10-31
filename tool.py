"""Inspect the live migration condition and optionally initiate one VM migration."""
import argparse
from decimal import Decimal
import json
import sys
import subprocess
from datetime import datetime, timezone
from oc_client import Client, VM, VMI, MIG, SNAP, quantity, age_hours, condition, require_name, stopped, escape, migration


def execute(client,args):
    name = require_name(args)
    vmi = client.get(VMI, name)
    result = {'name':name, 'phase':vmi.get('status', {}).get('phase'), 'node':vmi.get('status', {}).get('nodeName'), 'live_migratable':condition(vmi, 'LiveMigratable')}
    if args.migrate: result['change'] = migration(client, vmi, args.apply)
    return result


def main():
    parser = argparse.ArgumentParser(description='Inspect the live migration condition and optionally initiate one VM migration.')
    parser.add_argument('--context',required=True,help='Explicit existing oc kubeconfig context')
    parser.add_argument('--namespace',required=True,help='Namespace for workload operations')
    parser.add_argument('--name',help='Exact workload/resource name where required')
    parser.add_argument('--apply',action='store_true',help='Execute the requested change; default is preview')
    parser.add_argument('--migrate', action='store_true')
    args = parser.parse_args()
    try:
        result = execute(Client(args.context,args.namespace),args)
        print(json.dumps({'context':args.context,'namespace':args.namespace,'collected_at':datetime.now(timezone.utc).isoformat(),'result':result},indent=2))
    except (RuntimeError,ValueError,KeyError,OSError,TimeoutError,subprocess.SubprocessError) as error:
        print(str(error),file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__': raise SystemExit(main())
