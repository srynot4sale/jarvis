# Jarvis TV function
import function
import kernel.job

import datetime, re
import tvrage

def init():
    return tvfunc()

class tvfunc(function.function):
    def __init__(self):
        function.function.__init__(self, 'tv')

class job_hourly(kernel.job.job):

    def execute(self):

        call = self.function.kernel.call

        shows = call('list', 'view', ['tvshowstofetch']).data

        oldshows = call('list', 'view', ['tvshows']).data
        oldids = []
        if oldshows is not None and len(oldshows):
            for s in oldshows:
                oldids.append(s[0])

        api = tvrage.TVRage(self.function.kernel.getConfig('function_tv_apikey'))

        today = datetime.datetime.today() + datetime.timedelta(1)
        limit = today - datetime.timedelta(5)

        upcoming = {}
        count = 0

        upcoming[str(today)] = 'Today'

        if shows is not None:
            for show in shows:
                show = show[1]
                try:
                    matches = api.search(show)
                    showid = matches[0].showid
                except Exception:
                    upcoming[show] = 'Couldn\'t load %s' % show
                    continue

                status = ''
                nextep = None
                lastep = None
                try:
                    data = api.get_showinfo(showid)
                except Exception:
                    upcoming[show] = 'Couldn\'t load info for %s' % show
                    continue

                # Grab episode list
                try:
                    eps = api.get_episode_list(showid)
                except Exception:
                    upcoming[show] = 'Couldn\'t load ep list for %s' % show
                    continue

                seasons = eps.seasons
                for season in seasons:
                    seps = season.episodes
                    for sep in seps:
                        if sep.airdate is not None:
                            if sep.airdate >= today and (nextep is None or sep.airdate < nextep):
                                nextep = sep.airdate
                                continue

                            if sep.airdate < today and (lastep is None or sep.airdate > lastep):
                                lastep = sep.airdate
                                continue

                status = ''
                if data.status not in ('Returning Series', 'New Series'):
                    status = ' (%s)' % data.status

                if lastep > limit:
                    lastep = lastep + datetime.timedelta(1)
                    datestr = lastep.strftime('%y-%b-%d')
                    lastep = str(lastep)
                    upcoming[lastep] = '%s - %s%s' % (datestr, show, status)

                if nextep is not None and nextep > limit:
                    nextep = nextep + datetime.timedelta(1)
                    datestr = nextep.strftime('%y-%b-%d')
                    nextep = str(nextep)
                    upcoming[nextep] = '%s - %s%s' % (datestr, show, status)

            keys = upcoming.keys()
            keys.sort()

            for k in keys:
                if len(oldids):
                    call('list', 'update', ['tvshows', oldids.pop(0), upcoming[k]])
                else:
                    call('list', 'add', ['tvshows', upcoming[k]])

            for o in oldids:
                call('list', 'remove', ['tvshows', oldids.pop(0)])

