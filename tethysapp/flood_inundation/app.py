from tethys_sdk.base import TethysAppBase, url_map_maker


class FloodInundation(TethysAppBase):
    """
    Tethys app class for Flood Inundation.
    """

    name = 'Tuscaloosa Flood Map'
    index = 'flood_inundation:home'
    icon = 'flood_inundation/images/flood.png'
    package = 'flood_inundation'
    root_url = 'flood-inundation'
    color = '#e74c3c'
    description = 'Place a brief description of your app here.'
    enable_feedback = False
    feedback_emails = []

        
    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (UrlMap(name='home',
                           url='flood-inundation',
                           controller='flood_inundation.controllers.home'),
        )

        return url_maps