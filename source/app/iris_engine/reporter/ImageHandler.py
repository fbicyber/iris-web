#  IRIS Source Code
#  Copyright (C) 2021 - Airbus CyberSecurity (SAS)
#  contact@dfir-iris.org
#  Created by Lukas Zurschmiede @LukyLuke
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
import logging
import os
import shutil
import uuid
import re

from pathlib import Path
from docxtpl import DocxTemplate

from docx_generator.exceptions.rendering_error import RenderingError
from docx_generator.globals.picture_globals import PictureGlobals

from app.datamgmt.datastore.datastore_db import datastore_get_local_file_path


class ImageHandler(PictureGlobals):
    def __init__(self, template: DocxTemplate, base_path: str, caseid: int):
        self._logger = logging.getLogger(__name__)
        # The case actually being reported. Used to scope datastore lookups so a link
        # crafted with a foreign cid can't pull another case's file into this report.
        self._caseid = caseid
        PictureGlobals.__init__(self, template, base_path)

    def _process_remote(self, image_path: str) -> str:
        """
        Checks if the given Link is a datastore-link and if so, save the image locally for further processing.
        :
        A Datastore Links looks like this: https://localhost:4433/datastore/file/view/2?cid=1
        """
        res = re.search(r'datastore\/file\/view\/(\d+)\?cid=(\d+)', image_path)
        if res and image_path[:4] == 'http' and len(res.groups()) == 2:
            file_id = res.groups(0)[0]
            # Deliberately ignore the cid embedded in the link and use the report's own
            # case id instead: the link's cid is attacker-controlled markdown content,
            # and honoring it would let a report pull a file from any other case.
            has_error, dsf = datastore_get_local_file_path(file_id, self._caseid)

            if has_error:
                raise RenderingError(self._logger, f'File-ID {file_id} does not exist in Case {self._caseid}')
            if not Path(dsf.file_local_name).is_file():
                raise RenderingError(self._logger, f'File {dsf.file_local_name} does not exists on the server. Update or delete virtual entry')

            file_ext = os.path.splitext(dsf.file_original_name)[1]
            file_name = os.path.join(self._output_path, str(uuid.uuid4())) + file_ext
            return_value = shutil.copy(dsf.file_local_name, file_name)
            return return_value

        # Any other remote URL is intentionally not fetched: the base implementation
        # (PictureGlobals._process_remote) performs an unrestricted requests.get() on
        # whatever URL is embedded in the report content, which is a server-side request
        # forgery primitive (internal services, cloud metadata endpoints, etc.) reachable
        # by anyone who can write to the reported case's content.
        raise RenderingError(self._logger, f'Refusing to fetch non-datastore remote image: {image_path}')
