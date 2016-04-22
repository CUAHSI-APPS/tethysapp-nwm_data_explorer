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
                    url_map(name='api_info',
                            url='nwm-data-explorer/api-info',
                            controller='nwm_data_explorer.controllers.api_info'),
                    url_map(name='get_folder_contents',
                            url='nwm-data-explorer/.*/get-folder-contents',
                            controller='nwm_data_explorer.controllers_ajax.get_folder_contents'),
                    url_map(name='delete_temp_files',
                            url='nwm-data-explorer/.*/delete-temp-files',
                            controller='nwm_data_explorer.controllers_ajax.delete_temp_files')
                    )

        return url_maps
