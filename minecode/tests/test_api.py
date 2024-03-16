#
# Copyright (c) nexB Inc. and others. All rights reserved.
# purldb is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/purldb for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import json
import os

from django.contrib.auth.models import Group, User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from minecode.models import ScannableURI
from minecode.utils_test import JsonBasedTesting
from packagedb.models import Package, Resource


class ScannableURIAPITestCase(JsonBasedTesting, TestCase):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'testfiles')

    def setUp(self):
        self.user = User.objects.create_user(
            username="username",
            email="e@mail.com",
            password="secret"
        )
        scan_queue_workers_group, _ = Group.objects.get_or_create(name='scan_queue_workers')
        scan_queue_workers_group.user_set.add(self.user)
        self.auth = f"Token {self.user.auth_token.key}"
        self.csrf_client = APIClient(enforce_csrf_checks=True)
        self.csrf_client.credentials(HTTP_AUTHORIZATION=self.auth)

        self.package1 = Package.objects.create(
            download_url='https://test-url.com/package1.tar.gz',
            type='type1',
            name='name1',
            version='1.0',
        )
        self.scannable_uri1 = ScannableURI.objects.create(
            uri='https://test-url.com/package1.tar.gz',
            package=self.package1
        )

        self.package2 = Package.objects.create(
            download_url='https://test-url.com/package2.tar.gz',
            type='type2',
            name='name2',
            version='2.0',
        )
        self.scannable_uri2 = ScannableURI.objects.create(
            uri='https://test-url.com/package2.tar.gz',
            package=self.package2
        )

        self.client = APIClient()

    def test_api_scannable_uri_list_endpoint(self):
        response = self.client.get('/api/scan_queue/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.csrf_client.get('/api/scan_queue/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, response.data.get('count'))

    def test_api_scannable_uri_get_next_download_url(self):
        response = self.client.get('/api/scan_queue/get_next_download_url/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.csrf_client.get('/api/scan_queue/get_next_download_url/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('scannable_uri_uuid'), self.scannable_uri1.uuid)
        self.assertEqual(response.data.get('download_url'), self.scannable_uri1.uri)

        response = self.csrf_client.get('/api/scan_queue/get_next_download_url/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('scannable_uri_uuid'), self.scannable_uri2.uuid)
        self.assertEqual(response.data.get('download_url'), self.scannable_uri2.uri)

        response = self.csrf_client.get('/api/scan_queue/get_next_download_url/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('scannable_uri_uuid'), '')
        self.assertEqual(response.data.get('download_url'), '')

    def test_api_scannable_uri_update_status(self):
        self.assertEqual(ScannableURI.SCAN_NEW, self.scannable_uri1.scan_status)

        response = self.client.post('/api/scan_queue/update_status/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        data = {
            "scannable_uri_uuid": self.scannable_uri1.uuid,
            "scan_status": 'failed',
            'scan_log': 'scan_log',
        }
        response = self.csrf_client.post('/api/scan_queue/update_status/', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.scannable_uri1.refresh_from_db()
        self.assertEqual(ScannableURI.SCAN_FAILED, self.scannable_uri1.scan_status)
        self.assertEqual('scan_log', self.scannable_uri1.scan_error)

        self.assertFalse(self.package2.md5)
        self.assertFalse(self.package2.sha1)
        self.assertFalse(self.package2.sha256)
        self.assertFalse(self.package2.sha512)
        self.assertFalse(self.package2.size)
        self.assertFalse(self.package2.declared_license_expression)
        self.assertFalse(self.package2.copyright)
        self.assertEqual(0, Resource.objects.all().count())
        scan_file_location = self.get_test_loc('scancodeio/get_scan_data.json')
        summary_file_location = self.get_test_loc('scancodeio/scan_summary_response.json')
        project_extra_data = {
            'md5': 'md5',
            'sha1': 'sha1',
            'sha256': 'sha256',
            'sha512': 'sha512',
            'size': 100,
        }
        with open(scan_file_location) as scan_file:
            with open(summary_file_location) as summary_file:
                data = {
                    "scannable_uri_uuid": self.scannable_uri2.uuid,
                    "scan_status": 'scanned',
                    'project_extra_data': json.dumps(project_extra_data),
                    'scan_results_file': scan_file,
                    'scan_summary_file': summary_file,
                }
                response = self.csrf_client.post('/api/scan_queue/update_status/', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.scannable_uri2.refresh_from_db()
        self.assertEqual(ScannableURI.SCAN_INDEXED, self.scannable_uri2.scan_status)
        self.package2.refresh_from_db()
        self.assertEqual('md5', self.package2.md5)
        self.assertEqual('sha1', self.package2.sha1)
        self.assertEqual('sha256', self.package2.sha256)
        self.assertEqual('sha512', self.package2.sha512)
        self.assertEqual(100, self.package2.size)
        self.assertEqual('apache-2.0', self.package2.declared_license_expression)
        self.assertEqual('Copyright (c) Apache Software Foundation', self.package2.copyright)
        self.assertFalse(self.scannable_uri2.scan_error)
        self.assertEqual(64, Resource.objects.all().count())

        data = {}
        response = self.csrf_client.post('/api/scan_queue/update_status/', data=data)
        expected_response = {'error': 'missing scannable_uri_uuid'}
        self.assertEqual(expected_response, response.data)

        data = {
            'scannable_uri_uuid': self.scannable_uri2.uuid,
            'scan_status': 'invalid'
        }
        response = self.csrf_client.post('/api/scan_queue/update_status/', data=data)
        expected_response = {'error': 'invalid scan_status: invalid'}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(expected_response, response.data)

        data = {
            'scannable_uri_uuid': 'asdf',
            'scan_status': 'scanned'
        }
        response = self.csrf_client.post('/api/scan_queue/update_status/', data=data)
        expected_response = {'error': 'invalid scannable_uri_uuid: asdf'}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(expected_response, response.data)
