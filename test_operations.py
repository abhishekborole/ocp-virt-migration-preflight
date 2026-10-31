from unittest import TestCase
from unittest.mock import Mock
from oc_client import migration

class MigrationTests(TestCase):
    def test_active_migration_blocks_duplicate(self):
        client=Mock()
        client.items.return_value=[{'spec':{'vmiName':'vm'},'status':{'phase':'Running'}}]
        vmi={'metadata':{'name':'vm'},'status':{'phase':'Running','conditions':[{'type':'LiveMigratable','status':'True'}]}}
        with self.assertRaises(ValueError):migration(client,vmi,True)
        client.create.assert_not_called()
    def test_eligible_preview_creates_scoped_manifest_without_apply(self):
        client=Mock();client.items.return_value=[]
        vmi={'metadata':{'name':'vm'},'status':{'phase':'Running','conditions':[{'type':'LiveMigratable','status':'True'}]}}
        migration(client,vmi,False)
        args=client.create.call_args.args
        self.assertEqual(args[0]['spec']['vmiName'],'vm');self.assertFalse(args[1])
