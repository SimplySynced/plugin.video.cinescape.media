# -*- coding: utf-8 -*-
# Module: Cinescape Media
# Author: Dex Burgess
# Created on: 2/10/2021
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

from urllib import urlencode

import xbmc
from urlparse import parse_qsl
import xbmcgui
import xbmcplugin
from collections import Counter

from resources.lib import website

def run_addon(argv):
    try:
        # ...here possible future others code initializations...

        Directory(argv).router()
    except Exception as exc:
        # todo show possible errors as message to the user and print to kodi log details...
        xbmc.log(str(exc), xbmc.LOGERROR)
        # Tell Kodi we have failed to load after loading has failed.
        xbmcplugin.endOfDirectory(handle=int(argv[1]), succeeded=False)


class Directory(object):

    def __init__(self, argv):
        self.paramstring = argv[2][1:]
        # Get the plugin url in plugin:// notation.
        self._url = argv[0]
        # Get the plugin handle as an integer number.
        self._handle = int(argv[1])

    def router(self):
        """
        Router function that calls other functions depending on the provided paramstring
        """
        # Parse a URL-encoded paramstring to the dictionary of
        # {<parameter>: <value>} elements
        params = dict(parse_qsl(self.paramstring))
        # Check the parameters passed to the plugin
        if params:
            if params['action'] == 'getSeasons':
                # Display the seasons of the selected show.
                self.list_seasons(params['shownum'])
            elif params['action'] == 'getEpisodes':
                # Display the episodes of the given seasons.
                self.list_episodes(params['shownum'],params['seasonnum'])
            elif params['action'] == 'play':
                # Play a video from a provided URL.
                self.play_video(params['video'])
            else:
                # If the provided paramstring does not contain a supported action we raise an exception.
                raise ValueError('Invalid paramstring: {0}!'.format(self.paramstring))
        else:
            # If the plugin is called from Kodi UI without any parameters, display the list of shows.
            self.list_shows()

    def get_url(self, **kwargs):
        """
        Create a URL for calling the plugin recursively from the given set of keyword arguments.
        """
        return '{0}?{1}'.format(self._url, urlencode(kwargs))

    def get_shows(self):
        """
        Get the list of show names from json feed.
        """
        data = website.get_cinescape_data()
        showNames = map(lambda value: value['title'], data['series'])

        return showNames

    def count_seasons(self, shownum):
        """
        Get a count of a shows seasons
        """
        data = website.get_cinescape_data()
        print(data)

        sc = len(map(lambda value: value['seasonNumber'], data['series'][shownum]['seasons']))

        return sc

    def count_totalepisodes(self, shownum):
        """
        Get a count of a shows total episodes
        """
        data = website.get_cinescape_data()

        te = 0

        for season in data['series'][shownum]['seasons']:
            te += len(season['episodes'])

        return te

    def get_seasons(self, shownum):
        """
        Get all the seasons for the choosen show.
        """
        data = website.get_cinescape_data()
        seasons = map(lambda value: value['seasonNumber'], data['series'][shownum]['seasons'])
        #xbmc.log(seasons)

        return seasons

    def count_episodes(self, shownum,seasonnum):
        """
        Get a count of the seasons episodes
        """
        data = website.get_cinescape_data()

        ec = len(map(lambda value: value['title'], data['series'][shownum]['seasons'][seasonnum]['episodes']))

        return ec

    def get_episodes(self, shownum,seasonnum):
        """
        Get the episodes for the choosen season.
        """
        data = website.get_cinescape_data()
        episodes = map(lambda value: value['title'], data['series'][shownum]['seasons'][seasonnum]['episodes'])

        return episodes

    def list_shows(self):
        """
        Create the list of shows in the Kodi interface.
        """
        data = website.get_cinescape_data()
        # Set plugin category. It is displayed in some skins as the name of the current section.
        xbmcplugin.setPluginCategory(self._handle, 'Shows')
        # Set plugin content. It allows Kodi to select appropriate views for this type of content.
        xbmcplugin.setContent(self._handle, 'tvshows')
        # Get Shows
        shows = self.get_shows()
        # Start JSON Counter
        i = 0
        for show in shows:
            # Get count of seasons for show
            seasoncount = self.count_seasons(i)
            # Get count of total episodes
            totalepisodes = self.count_totalepisodes(i)
            # Create a list item with a text label and a thumbnail image.
            list_item = xbmcgui.ListItem(label=show, offscreen=True)
            # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
            list_item.setArt({'thumb': data['series'][i]['thumbnail'],
                              'icon': data['series'][i]['thumbnail'],
                              'fanart': data['series'][i]['thumbnail'],
                              'poster': data['series'][i]['poster']})
            # Set additional info for the list item.
            list_item.setInfo('video', {'mediatype': 'tvshow',
                                        'title': show,
                                        'genre': data['series'][i]['genres'],
                                        'plot': data['series'][i]['shortDescription'],
                                        'premiered': data['series'][i]['releaseDate'],
                                        'studio': data['providerName'],
                                        'tvshowtitle': show,
                                        'season': seasoncount,
                                        'episode': totalepisodes})
            # Set Seasons Property
            # list_item.setProperty('TotalSeasons','3')
            # Create a URL for a plugin recursive call.
            url = self.get_url(action='getSeasons', shownum=i)
            # is_folder = True means that this item opens a sub-list of lower level items.
            is_folder = True
            # Add our item to the Kodi virtual folder listing.
            xbmcplugin.addDirectoryItem(self._handle, url, list_item, is_folder)
            # Add 1 to counter
            i = i + 1
        # Add a sort method for the virtual folder items (alphabetically, ignore articles)
        xbmcplugin.addSortMethod(self._handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
        # Finish creating a virtual folder.
        xbmcplugin.endOfDirectory(self._handle)

    def list_seasons(self, shownum):
        """
        Create the list of seaons in the Kodi interface.
        """
        data = website.get_cinescape_data()
        # Set plugin category. It is displayed in some skins as the name of the current section.
        xbmcplugin.setPluginCategory(self._handle, 'Seasons')
        # Set plugin content. It allows Kodi to select appropriate views for this type of content.
        xbmcplugin.setContent(self._handle, 'seasons')
        # Get Seasons
        shownum = int(shownum)
        seasons = self.get_seasons(shownum)
        # Start JSON Counter
        i = 0
        list_items = []
        for season in seasons:
            # Get a count of the seasons Episodes
            episodecount = self.count_episodes(shownum,i)
            # Create a list item with a text label and a thumbnail image.
            season = 'Season '+ str(season)
            list_item = xbmcgui.ListItem(label=season, offscreen=True)
            # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
            list_item.setArt({'thumb': data['series'][shownum]['thumbnail'],
                              'icon': data['series'][shownum]['thumbnail'],
                              'fanart': data['series'][shownum]['thumbnail']})
            # Set additional info for the list item.
            list_item.setInfo('video', {'mediatype': 'season',
                                        'title': data['series'][shownum]['seasons'][i]['seasonNumber'],
                                        'genre': data['series'][shownum]['genres'],
                                        'plot': data['series'][shownum]['shortDescription'],
                                        'premiered': data['series'][shownum]['releaseDate'],
                                        'studio': data['providerName'],
                                        'season': data['series'][shownum]['seasons'][i]['seasonNumber'],
                                        'sortseason': data['series'][shownum]['seasons'][i]['seasonNumber'],
                                        'episode': episodecount,
                                        'mpaa': 'R'})
            # Create a URL for a plugin recursive call.
            url = self.get_url(action='getEpisodes', seasonnum=i, shownum=shownum)
            # is_folder = True means that this item opens a sub-list of lower level items.
            is_folder = True
            # Add our item to the Kodi virtual folder listing.
            list_items.append((url, list_item, is_folder))
            #xbmcplugin.addDirectoryItem(self._handle, url, list_item, is_folder)
            # Add 1 to counter
            i = i + 1
        # Add all our items to the Kodi virtual folder listing
        xbmcplugin.addDirectoryItems(self._handle, list_items)
        # Add a sort method for the virtual folder items (alphabetically, ignore articles)
        xbmcplugin.addSortMethod(self._handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
        # Finish creating a virtual folder.
        xbmcplugin.endOfDirectory(self._handle)

    def list_episodes(self, shownum, seasonnum):
        """
        Return a list of all episodes for the given season
        """
        data = website.get_cinescape_data()
        # Set plugin category. It is displayed in some skins as the name of the current section.
        xbmcplugin.setPluginCategory(self._handle, 'Episodes')
        # Set plugin content. It allows Kodi to select appropriate views for this type of content.
        xbmcplugin.setContent(self._handle, 'episodes')
        # Get the list of videos in the category.
        shownum = int(shownum)
        seasonnum = int(seasonnum)
        episodes = self.get_episodes(shownum,seasonnum)
        # print(episodes)
        # Iterate through episodes.
        i = 0
        list_items = []
        for episode in episodes:
            # Debug Print
            # print(episode)
            # Create a list item with a text label and a thumbnail image.
            list_item = xbmcgui.ListItem(label=episode, offscreen=True)
            # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
            list_item.setArt({'thumb': data['series'][shownum]['seasons'][seasonnum]['episodes'][i]['thumbnail'],
                              'icon': data['series'][shownum]['seasons'][seasonnum]['episodes'][i]['thumbnail'],
                              'fanart': data['series'][shownum]['thumbnail']})
            # Set additional info for the list item.
            # 'mediatype' is needed for skin to display info for this ListItem correctly.
            list_item.setInfo('video', {'mediatype': 'episode',
                                        'title': episode,
                                        'genre': data['series'][shownum]['genres'],
                                        'plot': data['series'][shownum]['seasons'][seasonnum]['episodes'][i]['shortDescription'],
                                        'premiered': data['series'][shownum]['seasons'][seasonnum]['episodes'][i]['releaseDate'],
                                        'duration': data['series'][shownum]['seasons'][seasonnum]['episodes'][i]['content']['duration'],
                                        'season': data['series'][shownum]['seasons'][seasonnum]['seasonNumber'],
                                        'episode': data['series'][shownum]['seasons'][seasonnum]['episodes'][i]['episodeNumber'],
                                        'sortepisode': data['series'][shownum]['seasons'][seasonnum]['episodes'][i]['episodeNumber'],
                                        'studio': data['providerName'],
                                        'mpaa': 'R'})
            # Set 'IsPlayable' property to 'true'.  This is mandatory for playable items!
            list_item.setProperty('IsPlayable', 'true')

            # xbmc.log(str(seasonnum))
            # Create a URL for a plugin recursive call.
            url = self.get_url(action='play', video=data['series'][shownum]['seasons'][seasonnum]['episodes'][i]['content']['videos'][0]['url'])
            # Add the list item to a virtual Kodi folder.
            # is_folder = False means that this item won't open any sub-list.
            is_folder = False

            list_items.append((url, list_item, is_folder))
            ##  Add our item to the Kodi virtual folder listing.
            # xbmcplugin.addDirectoryItem(self._handle, url, list_item, is_folder)

            # Add 1 to counter
            i = i + 1
        # Add all our items to the Kodi virtual folder listing
        xbmcplugin.addDirectoryItems(self._handle, list_items)  # <<<<<<<<< this is a lot more performant <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        # Add a sort method for the virtual folder items (alphabetically, ignore articles)
        xbmcplugin.addSortMethod(self._handle, xbmcplugin.SORT_METHOD_EPISODE)
        # Finish creating a virtual folder.
        xbmcplugin.endOfDirectory(self._handle)

    def play_video(self, path):
        """
        Play a video by the provided path.
        """
        # Create a playable item with a path to play.
        play_item = xbmcgui.ListItem(path=path)
        # Pass the item to the Kodi player.
        xbmcplugin.setResolvedUrl(self._handle, True, listitem=play_item)