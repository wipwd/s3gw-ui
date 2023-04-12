# Copyright 2023 SUSE LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
from fastapi import HTTPException, status

from backend.api import S3GWClient, bucket


@pytest.mark.anyio
async def test_api_bucket_list(s3_client: S3GWClient) -> None:
    # create a couple of buckets
    async with s3_client.conn() as client:
        await client.create_bucket(Bucket="foo")
        await client.create_bucket(Bucket="bar")

    res: bucket.BucketListResponse = await bucket.get_bucket_list(s3_client)
    assert "foo" in res.buckets
    assert "bar" in res.buckets
    assert len(res.buckets) == 2


@pytest.mark.anyio
async def test_api_bucket_create(
    s3_client: S3GWClient, is_mock_server: bool
) -> None:
    await bucket.bucket_create(s3_client, "asdasd", enable_object_locking=False)

    raised = False
    try:
        await bucket.bucket_create(
            s3_client, "asdasd", enable_object_locking=False
        )
    except HTTPException as e:
        assert e.status_code == status.HTTP_409_CONFLICT
        assert e.detail == "Bucket already exists"
        raised = True

    # apparently the moto mock server will always return success even if a
    # bucket already exists, whereas s3gw will be compliant with S3 semantics
    # and return an error about the bucket already existing.
    if is_mock_server:
        assert not raised
    else:
        assert raised
