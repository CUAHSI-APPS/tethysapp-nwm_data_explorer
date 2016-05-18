from tethys_sdk.base import TethysAppBase, url_map_maker


class NationalWaterModelDataExplorer(TethysAppBase):
    """
    Tethys app class for National Water Model Data Explorer.
    """

    name = 'National Water Model Data Explorer'
    index = 'nwm_data_explorer:home'
    icon = 'nwm_data_explorer/images/icon.gif'
    package = 'nwm_data_explorer'
    root_url = 'nwm-data-explorer'
    color = '#e74c3c'
    description = 'This app explores the National Water Data provided for the NFIE Summer Institute and provides an ' \
                  'API for accessing the data externally.'
    enable_feedback = False
    feedback_emails = []

    def url_maps(self):
        """
        Add controllers
        """
        url_map = url_map_maker(self.root_url)

        url_maps = (url_map(name='home',
                            url='nwm-data-explorer',
                            controller='nwm_data_explorer.controllers.home'),
                    url_map(name='irods_explorer',
                            url='nwm-data-explorer/irods_explorer',
                            controller='nwm_data_explorer.controllers.data_explorer'),
                    url_map(name='files_explorer',
                            url='nwm-data-explorer/files_explorer',
                            controller='nwm_data_explorer.controllers.data_explorer'),
                    url_map(name='api',
                            url='nwm-data-explorer/api',
                            controller='nwm_data_explorer.controllers.api'),
                    url_map(name='get_folder_contents',
                            url='nwm-data-explorer/.*/get-folder-contents',
                            controller='nwm_data_explorer.controllers_ajax.get_folder_contents'),
                    url_map(name='download_file',
                            url='nwm-data-explorer/.*/download-file',
                            controller='nwm_data_explorer.controllers_ajax.download_file'),
                    url_map(name='download_files',
                            url='nwm-data-explorer/.*/download-files',
                            controller='nwm_data_explorer.controllers_ajax.download_files'),
                    url_map(name='delete_temp_files',
                            url='nwm-data-explorer/.*/delete-temp-files',
                            controller='nwm_data_explorer.controllers_ajax.delete_temp_files'),
                    url_map(name='api_get_file_list',
                            url='nwm-data-explorer/api/GetFileList',
                            controller='nwm_data_explorer.api.api_get_file_list'),
                    url_map(name='api_get_file',
                            url='nwm-data-explorer/api/GetFile',
                            controller='nwm_data_explorer.api.api_get_file'),
                    url_map(name='api_get_file_metadata',
                            url='nwm-data-explorer/api/GetFileMetadata',
                            controller='nwm_data_explorer.api.api_get_file_metadata')
                    )

        return url_maps
