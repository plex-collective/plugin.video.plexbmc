import zope.interface

#===============================================================================
# Section Interface Markers
#===============================================================================
class IListItemVideo(Interface):
    ''' Video marker '''
class IListItemVideoShows(Interface):
    ''' Video Shows marker '''
class IListItemVideoSeasons(Interface):
    ''' Video Seasons marker '''
class IListItemVideoEpisodes(Interface):
    ''' Video Episodes marker '''
class IListItemVideoMovies(Interface):
    ''' Video Movies marker '''

class IListItemMusic(Interface):
    ''' Music marker '''
class IListItemMusicArtists(Interface):
    ''' Music Artists marker '''
class IListItemMusicAlbums(Interface):
    ''' Music Albums marker '''
class IListItemMusicTracks(Interface):
    ''' Music Tracks marker '''

class IListItemPhoto(Interface):
    ''' Photo marker '''
class IListItemPhotoPictures(Interface):
    ''' Photo Pictures marker '''


#===============================================================================
# IInfo (ListItem) Interface
#===============================================================================
class IInfo(zope.interface.Interface):
    """Creates a new ListItem."""

    def __init__(label='', label2='', iconImage=None, thumbnailImage=None, path=None):
        """
        label: string or unicode - label1 text.
        label2: string or unicode - label2 text.
        iconImage: string - icon filename.
        thumbnailImage: string - thumbnail filename.
        path: string or unicode - listitem's path.

        Example:
        listitem = xbmcgui.ListItem('Casino Royale', '[PG-13]', 'blank-poster.tbn', 'poster.tbn', path='f:\\movies\\casino_royale.mov')
        """

    def addStreamInfo(type, values):
        """
        addStreamInfo(type, values) -- Add a stream with details.

        type              : string - type of stream(video/audio/subtitle).
        values            : dictionary - pairs of { label: value }.

        Video Values:
        codec         : string (h264)
        aspect        : float (1.78)
        width         : integer (1280)
        height        : integer (720)
        duration      : integer (seconds)

        Audio Values:
        codec         : string (dts)
        language      : string (en)
        channels      : integer (2)

        Subtitle Values:
        language      : string (en)

        example:
        - self.list.getSelectedItem().addStreamInfo('video', { 'Codec': 'h264', 'Width' : 1280 })
        """

    def getLabel():
        """Returns the listitem label."""

    def getLabel2():
        """Returns the listitem's second label."""

    def setLabel(label):
        """Sets the listitem's label.

        label: string or unicode - text string.
        """

    def setLabel2(label2):
        """Sets the listitem's second label.

        label2: string or unicode - text string.
        """

    def setIconImage(icon):
        """Sets the listitem's icon image.

        icon: string or unicode - image filename.
        """

    def setThumbnailImage(thumb):
        """Sets the listitem's thumbnail image.

        thumb: string or unicode - image filename.
        """

    def select(selected):
        """Sets the listitem's selected status.

        selected: bool - True=selected/False=not selected.
        """

    def isSelected():
        """Returns the listitem's selected status."""

    def setInfo(type, infoLabels):
        """Sets the listitem's infoLabels.

        type: string - type of media(video/music/pictures).
        infoLabels: dictionary - pairs of { label: value }.

        Note:
            To set pictures exif info, prepend 'exif:' to the label. Exif values must be passed
            as strings, separate value pairs with a comma. (eg. {'exif:resolution': '720,480'}
            See CPictureInfoTag::TranslateString in PictureInfoTag.cpp for valid strings.

        General Values that apply to all types:
            count: integer (12) - can be used to store an id for later, or for sorting purposes
            size: long (1024) - size in bytes
            date: string (%d.%m.%Y / 01.01.2009) - file date

        Video Values:
            genre: string (Comedy)
            year: integer (2009)
            episode: integer (4)
            season: integer (1)
            top250: integer (192)
            tracknumber: integer (3)
            rating: float (6.4) - range is 0..10
            watched: depreciated - use playcount instead
            playcount: integer (2) - number of times this item has been played
            overlay: integer (2) - range is 0..8.  See GUIListItem.h for values
            cast: list (Michal C. Hall)
            castandrole: list (Michael C. Hall|Dexter)
            director: string (Dagur Kari)
            mpaa: string (PG-13)
            plot: string (Long Description)
            plotoutline: string (Short Description)
            title: string (Big Fan)
            originaltitle: string (Big Fan)
            duration: string - duration in minutes (95)
            studio: string (Warner Bros.)
            tagline: string (An awesome movie) - short description of movie
            writer: string (Robert D. Siegel)
            tvshowtitle: string (Heroes)
            premiered: string (2005-03-04)
            status: string (Continuing) - status of a TVshow
            code: string (tt0110293) - IMDb code
            aired: string (2008-12-07)
            credits: string (Andy Kaufman) - writing credits
            lastplayed: string (%Y-%m-%d %h:%m:%s = 2009-04-05 23:16:04)
            album: string (The Joshua Tree)
            votes: string (12345 votes)
            trailer: string (/home/user/trailer.avi)

        Music Values:
            tracknumber: integer (8)
            duration: integer (245) - duration in seconds
            year: integer (1998)
            genre: string (Rock)
            album: string (Pulse)
            artist: string (Muse)
            title: string (American Pie)
            rating: string (3) - single character between 0 and 5
            lyrics: string (On a dark desert highway...)
            playcount: integer (2) - number of times this item has been played
            lastplayed: string (%Y-%m-%d %h:%m:%s = 2009-04-05 23:16:04)

        Picture Values:
            title: string (In the last summer-1)
            picturepath: string (/home/username/pictures/img001.jpg)
            exif*: string (See CPictureInfoTag::TranslateString in PictureInfoTag.cpp for valid strings)

        Example:
            self.list.getSelectedItem().setInfo('video', { 'Genre': 'Comedy' })
        """

    def setProperty(key, value):
        """Sets a listitem property, similar to an infolabel.

        key: string - property name.
        value: string or unicode - value of property.

        Note:
            Key is NOT case sensitive.

        Some of these are treated internally by XBMC, such as the 'StartOffset' property, which is
        the offset in seconds at which to start playback of an item.  Others may be used in the skin
        to add extra information, such as 'WatchedCount' for tvshow items

        Example:
            self.list.getSelectedItem().setProperty('AspectRatio', '1.85 : 1')
            self.list.getSelectedItem().setProperty('StartOffset', '256.4')
        """

    def getProperty(key):
        """Returns a listitem property as a string, similar to an infolabel.

        key: string - property name.

        Note:
            Key is NOT case sensitive.
        """

    def addContextMenuItems(list, replaceItems=False):
        """Adds item(s) to the context menu for media lists.

        items: list - [(label, action)] A list of tuples consisting of label and action pairs.
            label: string or unicode - item's label.
            action: string or unicode - any built-in function to perform.
        replaceItems: bool - True=only your items will show/False=your items will be added to context menu.

        List of functions: http://wiki.xbmc.org/?title=List_of_Built_In_Functions

        Example:
            listitem.addContextMenuItems([('Theater Showtimes', 'XBMC.RunScript(special://home/scripts/showtimes/default.py,Iron Man)')])
        """

    def setPath(path):
        """
        setPath(path) -- Sets the listitem's path.
        path           : string or unicode - path, activated when item is clicked.
        *Note, You can use the above as keywords for arguments.

        example:
        - self.list.getSelectedItem().setPath(path='ActivateWindow(Weather)')
        """


#===============================================================================
# ListItem InfoLabel Interfaces
#===============================================================================
class IListItemLabel(Interface):
    ''' Shows the left label of the currently selected item in a list or thumb control '''

class IListItemLabel2(Interface):
    ''' Shows the right label of the currently selected item in a list or thumb control '''

class IListItemTitle(Interface):
    ''' Shows the title of the currently selected song or movie in a list or thumb control '''

class IListItemOriginalTitle(Interface):
    ''' Shows the original title of the currently selected movie in a list or thumb control '''

class IListItemSortLetter(Interface):
    ''' Shows the first letter of the current file in a list or thumb control '''

class IListItemTrackNumber(Interface):
    ''' Shows the track number of the currently selected song in a list or thumb control '''

class IListItemArtist(Interface):
    ''' Shows the artist of the currently selected song in a list or thumb control '''

class IListItemProperty_Artist_Born(Interface):
    ''' Date of Birth of the currently selected Artist '''

class IListItemProperty_Artist_Died(Interface):
    ''' Date of Death of the currently selected Artist '''

class IListItemProperty_Artist_Formed(Interface):
    ''' Formation date of the currently selected Band '''

class IListItemProperty_Artist_Disbanded(Interface):
    ''' Disbanding date of the currently selected Band '''

class IListItemProperty_Artist_YearsActive(Interface):
    ''' Years the currently selected artist has been active '''

class IListItemProperty_Artist_Instrument(Interface):
    ''' Instruments played by the currently selected artist '''

class IListItemProperty_Artist_Description(Interface):
    ''' Shows a biography of the currently selected artist '''

class IListItemProperty_Artist_Mood(Interface):
    ''' Shows the moods of the currently selected artist '''

class IListItemProperty_Artist_Style(Interface):
    ''' Shows the styles of the currently selected artist '''

class IListItemProperty_Artist_Genre(Interface):
    ''' Shows the genre of the currently selected artist '''

class IListItemAlbum(Interface):
    ''' Shows the album of the currently selected song in a list or thumb control '''

class IListItemProperty_Album_Mood(Interface):
    ''' Shows the moods of the currently selected Album '''

class IListItemProperty_Album_Style(Interface):
    ''' Shows the styles of the currently selected Album '''

class IListItemProperty_Album_Theme(Interface):
    ''' Shows the themes of the currently selected Album '''

class IListItemProperty_Album_Type(Interface):
    ''' Shows the Album Type (e.g. compilation, enhanced, explicit lyrics) of the currently selected Album '''

class IListItemProperty_Album_Label(Interface):
    ''' Shows the record label of the currently selected Album '''

class IListItemProperty_Album_Description(Interface):
    ''' Shows a review of the currently selected Album '''

class IListItemDiscNumber(Interface):
    ''' Shows the disc number of the currently selected song in a list or thumb control '''

class IListItemYear(Interface):
    ''' Shows the year of the currently selected song, album or movie in a list or thumb control '''

class IListItemPremiered(Interface):
    ''' Shows the release/aired date of the currently selected episode, show or movie in a list or thumb control '''

class IListItemGenre(Interface):
    ''' Shows the genre of the currently selected song, album or movie in a list or thumb control '''

class IListItemDirector(Interface):
    ''' Shows the director of the currently selected movie in a list or thumb control '''

class IListItemCountry(Interface):
    ''' Shows the production country of the currently selected movie in a list or thumb control '''

class IListItemEpisode(Interface):
    ''' Shows the episode number value for the currently selected episode. It also shows the number of total, watched or unwatched episodes for the currently selected tvshow or season, based on the the current watched filter. '''

class IListItemSeason(Interface):
    ''' Shows the season value for the currently selected tvshow '''

class IListItemTVShowTitle(Interface):
    ''' Shows the name value for the currently selected tvshow in the season and episode depth of the video library '''

class IListItemProperty_TotalSeasons(Interface):
    ''' Shows the total number of seasons for the currently selected tvshow '''

class IListItemProperty_TotalEpisodes(Interface):
    ''' Shows the total number of episodes for the currently selected tvshow or season '''

class IListItemProperty_WatchedEpisodes(Interface):
    ''' Shows the number of watched episodes for the currently selected tvshow or season '''

class IListItemProperty_UnWatchedEpisodes(Interface):
    ''' Shows the number of unwatched episodes for the currently selected tvshow or season '''

class IListItemProperty_NumEpisodes(Interface):
    ''' Shows the number of total, watched or unwatched episodes for the currently selected tvshow or season, based on the the current watched filter. '''

class IListItemPictureAperture(Interface):
    ''' Shows the F-stop used to take the selected picture. This is the value of the EXIF FNumber tag (hex code 0x829D). '''

class IListItemPictureAuthor(Interface):
    ''' Shows the name of the person involved in writing about the selected picture. This is the value of the IPTC Writer tag (hex code 0x7A). (Gotham addition) '''

class IListItemPictureByline(Interface):
    ''' Shows the name of the person who created the selected picture. This is the value of the IPTC Byline tag (hex code 0x50). (Gotham addition) '''

class IListItemPictureBylineTitle(Interface):
    ''' Shows the title of the person who created the selected picture. This is the value of the IPTC BylineTitle tag (hex code 0x55). (Gotham addition) '''

class IListItemPictureCamMake(Interface):
    ''' Shows the manufacturer of the camera used to take the selected picture. This is the value of the EXIF Make tag (hex code 0x010F). '''

class IListItemPictureCamModel(Interface):
    ''' Shows the manufacturer's model name or number of the camera used to take the selected picture. This is the value of the EXIF Model tag (hex code 0x0110). '''

class IListItemPictureCaption(Interface):
    ''' Shows a description of the selected picture. This is the value of the IPTC Caption tag (hex code 0x78). '''

class IListItemPictureCategory(Interface):
    ''' Shows the subject of the selected picture as a category code. This is the value of the IPTC Category tag (hex code 0x0F). (Gotham addition) '''

class IListItemPictureCCDWidth(Interface):
    ''' Shows the width of the CCD in the camera used to take the selected picture. This is calculated from three EXIF tags (0xA002 * 0xA210 / 0xA20e). (Gotham addition) '''

class IListItemPictureCity(Interface):
    ''' Shows the city where the selected picture was taken. This is the value of the IPTC City tag (hex code 0x5A). (Gotham addition) '''

class IListItemPictureColour(Interface):
    ''' Shows whether the selected picture is "Colour" or "Black and White". (Gotham addition) '''

class IListItemPictureComment(Interface):
    ''' Shows a description of the selected picture. This is the value of the EXIF User Comment tag (hex code 0x9286). This is the same value as Slideshow.SlideComment. '''

class IListItemPictureCopyrightNotice(Interface):
    ''' Shows the copyright notice of the selected picture. This is the value of the IPTC Copyright tag (hex code 0x74). (Gotham addition) '''

class IListItemPictureCountry(Interface):
    ''' Shows the full name of the country where the selected picture was taken. This is the value of the IPTC CountryName tag (hex code 0x65). (Gotham addition) '''

class IListItemPictureCountryCode(Interface):
    ''' Shows the country code of the country where the selected picture was taken. This is the value of the IPTC CountryCode tag (hex code 0x64). (Gotham addition) '''

class IListItemPictureCredit(Interface):
    ''' Shows who provided the selected picture. This is the value of the IPTC Credit tag (hex code 0x6E). (Gotham addition) '''

class IListItemPictureDate(Interface):
    ''' Shows the localized date of the selected picture. The short form of the date is used. The value of the EXIF DateTimeOriginal tag (hex code 0x9003) is preferred. If the DateTimeOriginal tag is not found, the value of DateTimeDigitized (hex code 0x9004) or of DateTime (hex code 0x0132) might be used. '''

class IListItemPictureDatetime(Interface):
    ''' Shows the date/timestamp of the selected picture. The localized short form of the date and time is used. The value of the EXIF DateTimeOriginal tag (hex code 0x9003) is preferred. If the DateTimeOriginal tag is not found, the value of DateTimeDigitized (hex code 0x9004) or of DateTime (hex code 0x0132) might be used. '''

class IListItemPictureDesc(Interface):
    ''' Shows a short description of the selected picture. The SlideComment, EXIFComment, or Caption values might contain a longer description. This is the value of the EXIF ImageDescription tag (hex code 0x010E). '''

class IListItemPictureDigitalZoom(Interface):
    ''' Shows the digital zoom ratio when the selected picture was taken. This is the value of the EXIF DigitalZoomRatio tag (hex code 0xA404). (Gotham addition) '''

class IListItemPictureExpMode(Interface):
    ''' Shows the exposure mode of the selected picture. The possible values are "Automatic", "Manual", and "Auto bracketing". This is the value of the EXIF ExposureMode tag (hex code 0xA402). '''

class IListItemPictureExposure(Interface):
    ''' Shows the class of the program used by the camera to set exposure when the selected picture was taken. Values include "Manual", "Program (Auto)", "Aperture priority (Semi-Auto)", "Shutter priority (semi-auto)", etc. This is the value of the EXIF ExposureProgram tag (hex code 0x8822). (Gotham addition) '''

class IListItemPictureExposureBias(Interface):
    ''' Shows the exposure bias of the selected picture. Typically this is a number between -99.99 and 99.99. This is the value of the EXIF ExposureBiasValue tag (hex code 0x9204). (Gotham addition) '''

class IListItemPictureExpTime(Interface):
    ''' Shows the exposure time of the selected picture, in seconds. This is the value of the EXIF ExposureTime tag (hex code 0x829A). If the ExposureTime tag is not found, the ShutterSpeedValue tag (hex code 0x9201) might be used. '''

class IListItemPictureFlashUsed(Interface):
    ''' Shows the status of flash when the selected picture was taken. The value will be either "Yes" or "No", and might include additional information. This is the value of the EXIF Flash tag (hex code 0x9209). (Gotham addition) '''

class IListItemPictureFocalLen(Interface):
    ''' Shows the lens focal length of the selected picture '''

class IListItemPictureFocusDist(Interface):
    ''' Shows the focal length of the lens, in mm. This is the value of the EXIF FocalLength tag (hex code 0x920A). '''

class IListItemPictureGPSLat(Interface):
    ''' Shows the latitude where the selected picture was taken (degrees, minutes, seconds North or South). This is the value of the EXIF GPSInfo.GPSLatitude and GPSInfo.GPSLatitudeRef tags. '''

class IListItemPictureGPSLon(Interface):
    ''' Shows the longitude where the selected picture was taken (degrees, minutes, seconds East or West). This is the value of the EXIF GPSInfo.GPSLongitude and GPSInfo.GPSLongitudeRef tags. '''

class IListItemPictureGPSAlt(Interface):
    ''' Shows the altitude in meters where the selected picture was taken. This is the value of the EXIF GPSInfo.GPSAltitude tag. '''

class IListItemPictureHeadline(Interface):
    ''' Shows a synopsis of the contents of the selected picture. This is the value of the IPTC Headline tag (hex code 0x69). (Gotham addition) '''

class IListItemPictureImageType(Interface):
    ''' Shows the color components of the selected picture. This is the value of the IPTC ImageType tag (hex code 0x82). (Gotham addition) '''

class IListItemPictureIPTCDate(Interface):
    ''' Shows the date when the intellectual content of the selected picture was created, rather than when the picture was created. This is the value of the IPTC DateCreated tag (hex code 0x37). (Gotham addition) '''

class IListItemPictureIPTCTime(Interface):
    ''' Shows the time when the intellectual content of the selected picture was created, rather than when the picture was created. This is the value of the IPTC TimeCreated tag (hex code 0x3C). (Gotham addition) '''

class IListItemPictureISO(Interface):
    ''' Shows the ISO speed of the camera when the selected picture was taken. This is the value of the EXIF ISOSpeedRatings tag (hex code 0x8827). '''

class IListItemPictureKeywords(Interface):
    ''' Shows keywords assigned to the selected picture. This is the value of the IPTC Keywords tag (hex code 0x19). '''

class IListItemPictureLightSource(Interface):
    ''' Shows the kind of light source when the picture was taken. Possible values include "Daylight", "Fluorescent", "Incandescent", etc. This is the value of the EXIF LightSource tag (hex code 0x9208). (Gotham addition) '''

class IListItemPictureLongDate(Interface):
    ''' Shows only the localized date of the selected picture. The long form of the date is used. The value of the EXIF DateTimeOriginal tag (hex code 0x9003) is preferred. If the DateTimeOriginal tag is not found, the value of DateTimeDigitized (hex code 0x9004) or of DateTime (hex code 0x0132) might be used. (Gotham addition) '''

class IListItemPictureLongDatetime(Interface):
    ''' Shows the date/timestamp of the selected picture. The localized long form of the date and time is used. The value of the EXIF DateTimeOriginal tag (hex code 0x9003) is preferred. if the DateTimeOriginal tag is not found, the value of DateTimeDigitized (hex code 0x9004) or of DateTime (hex code 0x0132) might be used. (Gotham addition) '''

class IListItemPictureMeteringMode(Interface):
    ''' Shows the metering mode used when the selected picture was taken. The possible values are "Center weight", "Spot", or "Matrix". This is the value of the EXIF MeteringMode tag (hex code 0x9207). (Gotham addition) '''

class IListItemPictureObjectName(Interface):
    ''' Shows a shorthand reference for the selected picture. This is the value of the IPTC ObjectName tag (hex code 0x05). (Gotham addition) '''

class IListItemPictureOrientation(Interface):
    ''' Shows the orientation of the selected picture. Possible values are "Top Left", "Top Right", "Left Top", "Right Bottom", etc. This is the value of the EXIF Orientation tag (hex code 0x0112). (Gotham addition) '''

class IListItemPicturePath(Interface):
    ''' Shows the filename and path of the selected picture '''

class IListItemPictureProcess(Interface):
    ''' Shows the process used to compress the selected picture (Gotham addition) '''

class IListItemPictureReferenceService(Interface):
    ''' Shows the Service Identifier of a prior envelope to which the selected picture refers. This is the value of the IPTC ReferenceService tag (hex code 0x2D). (Gotham addition) '''

class IListItemPictureResolution(Interface):
    ''' Shows the dimensions of the selected picture '''

class IListItemPictureSource(Interface):
    ''' Shows the original owner of the selected picture. This is the value of the IPTC Source tag (hex code 0x73). (Gotham addition) '''

class IListItemPictureSpecialInstructions(Interface):
    ''' Shows other editorial instructions concerning the use of the selected picture. This is the value of the IPTC SpecialInstructions tag (hex code 0x28). (Gotham addition) '''

class IListItemPictureState(Interface):
    ''' Shows the State/Province where the selected picture was taken. This is the value of the IPTC ProvinceState tag (hex code 0x5F). (Gotham addition) '''

class IListItemPictureSublocation(Interface):
    ''' Shows the location within a city where the selected picture was taken - might indicate the nearest landmark. This is the value of the IPTC SubLocation tag (hex code 0x5C). (Gotham addition) '''

class IListItemPictureSupplementalCategories(Interface):
    ''' Shows supplemental category codes to further refine the subject of the selected picture. This is the value of the IPTC SuppCategory tag (hex code 0x14). (Gotham addition) '''

class IListItemPictureTransmissionReference(Interface):
    ''' Shows a code representing the location of original transmission of the selected picture. This is the value of the IPTC TransmissionReference tag (hex code 0x67). (Gotham addition) '''

class IListItemPictureUrgency(Interface):
    ''' Shows the urgency of the selected picture. Values are 1-9. The "1" is most urgent. Some image management programs use urgency to indicate picture rating, where urgency "1" is 5 stars and urgency "5" is 1 star. Urgencies 6-9 are not used for rating. This is the value of the IPTC Urgency tag (hex code 0x0A). (Gotham addition) '''

class IListItemPictureWhiteBalance(Interface):
    ''' Shows the white balance mode set when the selected picture was taken. The possible values are "Manual" and "Auto". This is the value of the EXIF WhiteBalance tag (hex code 0xA403). (Gotham addition) '''

class IListItemFileName(Interface):
    ''' Shows the filename of the currently selected song or movie in a list or thumb control '''

class IListItemPath(Interface):
    ''' Shows the complete path of the currently selected song or movie in a list or thumb control '''

class IListItemFolderName(Interface):
    ''' Shows top most folder of the path of the currently selected song or movie in a list or thumb control '''

class IListItemFileNameAndPath(Interface):
    ''' Shows the full path with filename of the currently selected song or movie in a list or thumb control '''

class IListItemFileExtension(Interface):
    ''' Shows the file extension (without leading dot) of the currently selected item in a list or thumb control '''

class IListItemDate(Interface):
    ''' Shows the file date of the currently selected song or movie in a list or thumb control '''

class IListItemDateAdded(Interface):
    ''' Shows the date the currently selected item was added to the library '''

class IListItemSize(Interface):
    ''' Shows the file size of the currently selected song or movie in a list or thumb control '''

class IListItemRating(Interface):
    ''' Shows the IMDB rating of the currently selected movie in a list or thumb control '''

class IListItemVotes(Interface):
    ''' Shows the IMDB votes of the currently selected movie in a list or thumb control (Gotham addition) '''

class IListItemRatingAndVotes(Interface):
    ''' Shows the IMDB rating and votes of the currently selected movie in a list or thumb control '''

class IListItemMpaa(Interface):
    ''' Show the MPAA rating of the currently selected movie in a list or thumb control '''

class IListItemProgramCount(Interface):
    ''' Shows the number of times an xbe has been run from "my programs" '''

class IListItemDuration(Interface):
    ''' Shows the song or movie duration of the currently selected movie in a list or thumb control '''

class IListItemDBID(Interface):
    ''' Shows the database id of the currently selected listitem in a list or thumb control '''

class IListItemCast(Interface):
    ''' Shows a concatenated string of cast members of the currently selected movie, for use in dialogvideoinfo.xml '''

class IListItemCastAndRole(Interface):
    ''' Shows a concatenated string of cast members and roles of the currently selected movie, for use in dialogvideoinfo.xml '''

class IListItemStudio(Interface):
    ''' Studio of current selected Music Video in a list or thumb control '''

class IListItemTrailer(Interface):
    ''' Shows the full trailer path with filename of the currently selected movie in a list or thumb control '''

class IListItemWriter(Interface):
    ''' Name of Writer of current Video in a list or thumb control '''

class IListItemTagline(Interface):
    ''' Small Summary of current Video in a list or thumb control '''

class IListItemPlotOutline(Interface):
    ''' Small Summary of current Video in a list or thumb control '''

class IListItemPlot(Interface):
    ''' Complete Text Summary of Video in a list or thumb control '''

class IListItemPercentPlayed(Interface):
    ''' Returns percentage value [0-100] of how far the selected video has been played '''

class IListItemLastPlayed(Interface):
    ''' Last play date of Video in a list or thumb control '''

class IListItemPlayCount(Interface):
    ''' Playcount of Video in a list or thumb control '''

class IListItemStartTime(Interface):
    ''' Start time of current selected TV programme in a list or thumb control '''

class IListItemEndTime(Interface):
    ''' End time of current selected TV programme in a list or thumb control '''

class IListItemStartDate(Interface):
    ''' Start date of current selected TV programme in a list or thumb control '''

class IListItemDate(Interface):
    ''' Day, start time and end time of current selected TV programme in a list or thumb control '''

class IListItemChannelNumber(Interface):
    ''' Number of current selected TV channel in a list or thumb control '''

class IListItemChannelName(Interface):
    ''' Name of current selected TV channel in a list or thumb control '''

class IListItemVideoCodec(Interface):
    ''' Shows the video codec of the currently selected video (common values: 3iv2, avc1, div2, div3, divx, divx 4, dx50, flv, h264, microsoft, mp42, mp43, mp4v, mpeg1video, mpeg2video, mpg4, rv40, svq1, svq3, theora, vp6f, wmv2, wmv3, wvc1, xvid) '''

class IListItemVideoResolution(Interface):
    ''' Shows the resolution of the currently selected video (possible values: 480, 576, 540, 720, 1080, 4K). Note that 540 usually means a widescreen format (around 960x540) while 576 means PAL resolutions (normally 720x576), therefore 540 is actually better resolution than 576. '''

class IListItemVideoAspect(Interface):
    ''' Shows the aspect ratio of the currently selected video (possible values: 1.33, 1.37, 1.66, 1.78, 1.85, 2.20, 2.35, 2.40, 2.55, 2.76) '''

class IListItemAudioCodec(Interface):
    ''' Shows the audio codec of the currently selected video (common values: aac, ac3, cook, dca, dtshd_hra, dtshd_ma, eac3, mp1, mp2, mp3, pcm_s16be, pcm_s16le, pcm_u8, truehd, vorbis, wmapro, wmav2) '''

class IListItemAudioChannels(Interface):
    ''' Shows the number of audio channels of the currently selected video (possible values: 0, 1, 2, 4, 5, 6, 8) '''

class IListItemAudioLanguage(Interface):
    ''' Shows the audio language of the currently selected video (returns an ISO 639-2 three character code, e.g. eng, epo, deu) '''

class IListItemSubtitleLanguage(Interface):
    ''' Shows the subtitle language of the currently selected video (returns an ISO 639-2 three character code, e.g. eng, epo, deu) '''

class IListItemProperty_Addon_Name(Interface):
    ''' Shows the name of the currently selected addon '''

class IListItemProperty_Addon_Version(Interface):
    ''' Shows the version of the currently selected addon '''

class IListItemProperty_Addon_Summary(Interface):
    ''' Shows a short description of the currently selected addon '''

class IListItemProperty_Addon_Description(Interface):
    ''' Shows the full description of the currently selected addon '''

class IListItemProperty_Addon_Type(Interface):
    ''' Shows the type (screensaver, script, skin, etc...) of the currently selected addon '''

class IListItemProperty_Addon_Creator(Interface):
    ''' Shows the name of the author the currently selected addon '''

class IListItemProperty_Addon_Disclaimer(Interface):
    ''' Shows the disclaimer of the currently selected addon '''

class IListItemProperty_Addon_Changelog(Interface):
    ''' Shows the changelog of the currently selected addon '''

class IListItemProperty_Addon_ID(Interface):
    ''' Shows the identifier of the currently selected addon '''

class IListItemProperty_Addon_Status(Interface):
    ''' Shows the status of the currently selected addon '''

class IListItemProperty_Addon_Broken(Interface):
    ''' Shows a message when the addon is marked as broken in the repo '''

class IListItemProperty_Addon_Path(Interface):
    ''' Shows the path of the currently selected addon '''

class IListItemStartTime(Interface):
    ''' Start time of the selected item (PVR). (Frodo addition) '''

class IListItemEndTime(Interface):
    ''' End time of the selected item (PVR). (Frodo addition) '''

class IListItemStartDate(Interface):
    ''' Start date of the selected item (PVR). (Frodo addition) '''

class IListItemEndDate(Interface):
    ''' End date of the selected item (PVR). (Frodo addition) '''

class IListItemNextTitle(Interface):
    ''' Title of the next item (PVR). (Frodo addition) '''

class IListItemNextGenre(Interface):
    ''' Genre of the next item (PVR). (Frodo addition) '''

class IListItemNextPlot(Interface):
    ''' Plot of the next item (PVR). (Frodo addition) '''

class IListItemNextPlotOutline(Interface):
    ''' Plot outline of the next item (PVR). (Frodo addition) '''

class IListItemNextStartTime(Interface):
    ''' Start time of the next item (PVR). (Frodo addition) '''

class IListItemNextEndTime(Interface):
    ''' End of the next item (PVR). (Frodo addition) '''

class IListItemNextStartDate(Interface):
    ''' Start date of the next item (PVR). (Frodo addition) '''

class IListItemNextEndDate(Interface):
    ''' End date of the next item (PVR). (Frodo addition) '''

class IListItemChannelName(Interface):
    ''' Channelname of the selected item (PVR). (Frodo addition) '''

class IListItemChannelNumber(Interface):
    ''' Channel number of the selected item (PVR). (Frodo addition) '''

class IListItemChannelGroup(Interface):
    ''' Channel group of the selected item (PVR). (Frodo addition) '''

class IListItemProgress(Interface):
    ''' Part of the programme that's been played (PVR). (Frodo addition) '''

class IListItemStereoscopicMode(Interface):
    ''' Returns the stereomode of the selected video (i.e. mono, split_vertical, split_horizontal, row_interleaved, anaglyph_cyan_red, anaglyph_green_magenta)(Gotham addition) '''
