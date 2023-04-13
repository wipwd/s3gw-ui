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

import httpx

from backend.admin_ops import signed_request
from backend.admin_ops.types import AdminOpsError, UserInfo


async def get_user_info(url: str, access_key: str, secret_key: str) -> UserInfo:
    """
    Obtain informations about the user to whom the `access_key:secret_key` pair
    belongs to.
    """
    req = signed_request(
        access=access_key,
        secret=secret_key,
        method="GET",
        url=f"{url}/admin/user",
        params={"access-key": access_key},
    )

    async with httpx.AsyncClient() as client:
        res: httpx.Response = await client.send(req)
        if not res.is_success:
            raise AdminOpsError(res.status_code)

        return UserInfo.parse_obj(res.json())
