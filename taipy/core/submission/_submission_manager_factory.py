# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from typing import Type

from .._manager._manager_factory import _ManagerFactory
from ..common._utils import _load_fct
from ._submission_fs_repository import _SubmissionFSRepository
from ._submission_manager import _SubmissionManager
from ._submission_sql_repository import _SubmissionSQLRepository


class _SubmissionManagerFactory(_ManagerFactory):

    __REPOSITORY_MAP = {"default": _SubmissionFSRepository, "sql": _SubmissionSQLRepository}

    @classmethod
    def _build_manager(cls) -> Type[_SubmissionManager]:  # type: ignore
        if cls._using_enterprise():
            submission_manager = _load_fct(
                f"{cls._TAIPY_ENTERPRISE_CORE_MODULE}.submission._submission_manager",
                "_SubmissionManager",
            )
            build_repository = _load_fct(
                f"{cls._TAIPY_ENTERPRISE_CORE_MODULE}.submission._submission_manager_factory",
                "_SubmissionManagerFactory",
            )._build_repository
        else:
            submission_manager = _SubmissionManager
            build_repository = cls._build_repository
        submission_manager._repository = build_repository()  # type: ignore
        return submission_manager  # type: ignore

    @classmethod
    def _build_repository(cls):
        return cls._get_repository_with_repo_map(cls.__REPOSITORY_MAP)()
