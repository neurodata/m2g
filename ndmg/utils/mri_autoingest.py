# Copyright 2014 Open Connectome Project (http://openconnecto.me)
#
# Licensed under the Apache License,  Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,  software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,  either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ndio.remote.ndingest as NI


def main():

    ni = NI.NDIngest()

    """
    Dataset
    """
    dataset_name = 'MNI152'
    imagesize = (182, 218, 182)
    voxelres = (1000000.0, 1000000.0, 1000000.0)
    offset = (0, 0, 0)
    timerange = (0, 199)
    scalinglevels = 0
    scaling = 1
    public = 1
    metadata = ""

    # Add data set information to ingest object
    ni.add_dataset(dataset_name, imagesize, voxelres, offset,
                   timerange, scalinglevels, scaling)
    ni.add_metadata(metadata)

    """
    Project
    """
    project_name = 'KKI2009dti'
    token_name = 'KKI2009dti'

    # Adds project information to ingest object
    ni.add_project(project_name, token_name, public)

    """
    Channel
    """
    # Sets up general channel info
    datatype = 'uint8'
    channel_type = 'timeseries'
    exceptions = 0
    resolution = 0
    windowrange = (0, 0)
    readonly = 0
    data_url = 'http://openconnecto.me/mrdata/share/ingest'
    file_format = 'SLICE'
    file_type = 'png'

    # Lists channel names
    channels = ['113_1', '113_2', '127_1', '127_2', '142_1', '142_2', '239_1',
                '239_2', '346_1', '346_2', '422_1', '422_2', '492_1', '492_2',
                '502_1', '502_2', '505_1', '505_2', '656_1', '656_2', '679_1',
                '679_2', '742_1', '742_2', '800_1', '800_2', '814_1', '814_2',
                '815_1', '815_2', '849_1', '849_2', '906_1', '906_2', '913_1',
                '913_2', '916_1', '916_2', '934_1', '934_2', '959_1', '959_2']

    # Adds each channel's information to ingest object
    for channel_name in channels:
        ni.add_channel(channel_name, datatype, channel_type, data_url,
                       file_format, file_type, exceptions, resolution,
                       windowrange, readonly)

    # Post the data
    ni.post_data(verifytype='Folder')


if __name__ == "__main__":
    main()
