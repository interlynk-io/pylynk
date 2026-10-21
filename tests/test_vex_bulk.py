"""Bulk VEX performance and matching regressions; no live API writes."""
import contextlib
import io
import json
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from pylynk.api.client import LynkAPIClient
from pylynk.cli.commands import vex
from pylynk.utils.config import Config


def finding(identifier, name='linux', version='1.0', alias=None):
    return {'id': identifier, 'vuln': {'id': identifier, 'vulnId': 'CVE-2026-1234',
                                     'nvdAliasId': alias},
            'component': {'name': name, 'version': version}}


class BulkVexTests(unittest.TestCase):
    def setUp(self):
        self.config = Config(SimpleNamespace(prod='test', env='default', ver='1.0'))
        self.config.env_id = 'env'
        self.config.ver_id = 'sbom'
        self.client = LynkAPIClient(self.config)

    def resolve(self, nodes, **filters):
        index = vex._index_vulnerabilities(self.client, nodes)
        with contextlib.redirect_stdout(io.StringIO()):
            return vex._resolve_component_vuln_id_from_index(
                self.client, index, 'cve-2026-1234', **filters)

    def test_optional_filters_and_ambiguity(self):
        nodes = [finding('a'), finding('b', version='2.0'), finding('c', name='other')]
        self.assertIsNone(self.resolve(nodes))
        self.assertIsNone(self.resolve(nodes, component_name='LINUX'))
        self.assertIsNone(self.resolve(nodes, component_version='1.0'))
        self.assertEqual(self.resolve(nodes, component_name='LINUX', component_version='2.0'), 'b')
        self.assertIsNone(self.resolve(nodes, component_name='missing'))

    def test_duplicate_aliases_and_empty_fields_do_not_create_ambiguity(self):
        node = finding('a', name='', version='', alias='CVE-2026-1234')
        self.assertEqual(self.resolve([node]), 'a')
        index = vex._index_vulnerabilities(self.client, [node])
        self.assertEqual(vex._resolve_component_vuln_id_from_index(self.client, index, 'a'), 'a')

    def test_174_rows_fetch_pages_once_cache_status_and_preserve_notes(self):
        rows = []
        nodes = []
        for i in range(174):
            cve = f'CVE-2026-{1000+i}'
            node = finding(str(i))
            node['vuln']['vulnId'] = cve
            nodes.append(node)
            rows.append({'vuln': cve, 'component': 'linux', 'component_version': '1.0',
                         'status': 'fixed', 'note': f'Patch for {cve}'})
        nodes.extend(finding(f'other-{i}', name='other') for i in range(500))
        mutations = []

        def request(query, variables=None, operation_name=None):
            if operation_name == 'GetVulnProductDetails':
                self.assertEqual(variables['first'], 500)
                start = int(variables['after'] or 0)
                end = min(start + variables['first'], len(nodes))
                return {'data': {'sbom': {'vulns': {
                    'nodes': nodes[start:end], 'totalCount': len(nodes),
                    'pageInfo': {'hasNextPage': end < len(nodes), 'endCursor': str(end)}}}}}
            if operation_name == 'GetVexStatuses':
                return {'data': {'vexStatuses': [{'id': 'fixed-id', 'name': 'Fixed'}]}}
            if operation_name == 'UpdateBulkCompVex':
                mutations.append(dict(variables))
                return {'data': {'componentVexBulkUpdate': {
                    'componentVulns': [{'id': i} for i in variables['comVulnIds']]}}}
            self.fail(f'Unexpected operation: {operation_name}')

        self.client._make_request = Mock(side_effect=request)
        self.client.resolve_product_env = Mock(return_value=True)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json') as file:
            json.dump(rows, file)
            file.flush()
            self.config.vex_file = file.name
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(vex._execute_bulk_update(self.client, self.config), 0)
        operations = [c.args[2] if len(c.args) > 2 else c.kwargs['operation_name']
                      for c in self.client._make_request.call_args_list]
        self.assertEqual(operations.count('GetVulnProductDetails'), 2)
        self.assertEqual(operations.count('GetVexStatuses'), 1)
        self.assertEqual(len(mutations), 174)
        for i, mutation in enumerate(mutations):
            self.assertEqual(mutation['comVulnIds'], [str(i)])
            self.assertEqual(mutation['note'], rows[i]['note'])
            self.assertEqual(mutation['vexStatusId'], 'fixed-id')

    def test_explicit_ids_skip_vulnerability_fetch_and_identical_payloads_batch(self):
        rows = [{'component_vuln_id': str(i), 'status_id': 'fixed-id', 'note': 'Patched'}
                for i in range(174)]
        self.client.resolve_product_env = Mock(return_value=True)
        self.client.get_vulnerabilities = Mock(side_effect=AssertionError('Unexpected fetch'))
        self.client.bulk_update_component_vex = Mock(return_value={'componentVulns': []})
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json') as file:
            json.dump(rows, file)
            file.flush()
            self.config.vex_file = file.name
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(vex._execute_bulk_update(self.client, self.config), 0)
        self.client.bulk_update_component_vex.assert_called_once()
        self.assertEqual(len(self.client.bulk_update_component_vex.call_args.args[0]['comVulnIds']), 174)


if __name__ == '__main__':
    unittest.main()
