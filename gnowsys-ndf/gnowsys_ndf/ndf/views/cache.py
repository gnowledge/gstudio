from django import http
from django.shortcuts import render_to_response
from django.conf import settings
from django.core.cache import cache

import datetime, re
import subprocess

def cache_status(request):

    try:
        import memcache
    except ImportError:
        raise http.Http404

    if not (request.user.is_authenticated() and
            request.user.is_staff):
        raise http.Http404

    # get first memcached URI
    # m = re.match(
    #     "memcached://([.\w]+:\d+)", settings.CACHE_BACKEND
    # )
    # if not m:
    #     raise http.Http404

    host = memcache._Host('127.0.0.1:11211')
    host.connect()
    host.send_cmd("stats")

    class Stats:
        pass

    stats = Stats()

    while 1:
        line = host.readline().split(None, 2)
        if line[0] == "END":
            break
        stat, key, value = line
        try:
            # convert to native type, if possible
            value = int(value)
            if key == "uptime":
                value = datetime.timedelta(seconds=value)
            elif key == "time":
                value = datetime.datetime.fromtimestamp(value)
        except ValueError:
            pass
        setattr(stats, key, value)

    host.close_socket()

    shell_cmd_stats_items = subprocess.Popen( ['echo "stats items" | nc 127.0.0.1 11211'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    shell_cmd_stats_items_output, error = shell_cmd_stats_items.communicate()
    shell_cmd_stats_items_output = shell_cmd_stats_items_output.splitlines()[:-1]

    shell_cmd_stats_item_no_list = list(set([x.replace(' ', '').split(':')[1] for x in shell_cmd_stats_items_output]))
    # print shell_cmd_stats_item_no_list

    all_items_list = []
    for each_item in shell_cmd_stats_item_no_list:
        shell_cmd_stats_each_item = subprocess.Popen( ['echo "stats cachedump '+ each_item +' 100" | nc 127.0.0.1 11211'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        shell_cmd_stats_each_item_output, error = shell_cmd_stats_each_item.communicate()
        # print shell_cmd_stats_each_item_output
        shell_cmd_stats_each_item_output = shell_cmd_stats_each_item_output.splitlines()[:-1]
        all_items_list += [x.split(":")[2] for x in shell_cmd_stats_each_item_output]

    # print all_items_list
    stats_cmd_get = stats.cmd_get | 1

    return render_to_response(
        'ndf/memcached_status.html', dict(
            stats=stats,
            hit_rate=100 * (stats.get_hits / stats_cmd_get),
            time=datetime.datetime.now(), # server time
            all_cached_items=all_items_list,
        ))


def invalidate_cache_page(view_name, args=[], namespace=None, key_prefix=None):
    """
        This function allows you to invalidate any view-level cache which is implemented
        with @cache_page.
        view_name: view function you wish to invalidate or it's named url pattern
        args: any arguments passed to the view function
        namepace: optioal, if an application namespace is needed
        key prefix: for the @cache_page decorator for the function (if any)
    """
    from django.core.urlresolvers import reverse
    from django.http import HttpRequest
    from django.utils.cache import get_cache_key

    # create a fake request object
    request = HttpRequest()
    # Loookup the request path:
    if namespace:
        view_name = namespace + ":" + view_name
    # request.path = reverse(view_name, args=args)
    # get cache key, expire if the cached item exists:
    key = get_cache_key(request, key_prefix=key_prefix)
    if key:
        if cache.get(key):
            # print key
            # Delete the cache entry.
            #
            # Note that there is a possible race condition here, as another
            # process / thread may have refreshed the cache between
            # the call to cache.get() above, and the cache.set(key, None)
            # below.  This may lead to unexpected performance problems under
            # severe load.
            cache.set(key, None, 0)
        return True
    return False


def invalidate_set_cache(cache_key):
    '''
        Invalidates cache set by cache.set() method.
        Returns True with key value set to NULL, if key found else returns False.
    '''

    cache_result = cache.get(cache_key)

    if cache_result:
        cache.set(cache_key, None, 0)
        return True
    else:
        return False
