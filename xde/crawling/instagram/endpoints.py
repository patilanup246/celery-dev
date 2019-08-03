import json

from xde.helpers.collections import remove_skip_values

HOST = 'www.instagram.com'
MOBILE_HOST = 'i.instagram.com'
BASE_URL = 'https://www.instagram.com'
LOGIN_URL = BASE_URL + '/accounts/login/ajax/'
LOGOUT_URL = BASE_URL + '/accounts/logout/'
QUERY_URL = BASE_URL + '/query/'
GRAPHQL_URL = BASE_URL + '/graphql/query/'
CDN_URL = 'https://scontent.cdninstagram.com/'
WEB_LOGIN_URL = BASE_URL + '/accounts/login'
#
# ACCOUNT_PAGE = 'https://www.instagram.com/{username}'
MEDIA_LINK = 'https://www.instagram.com/p/%s'
ACCOUNT_MEDIAS = 'https://www.instagram.com/%s/media/?max_id=%s'
ACCOUNT_JSON_INFO = 'https://www.instagram.com/%s/?__a=1'
ACCOUNT_HTML_INFO = 'https://www.instagram.com/%s/'
USER_INFO_BY_ID = 'https://i.instagram.com/api/v1/users/%s/info/'
ACCOUNT_JSON_INFO_BY_ID = 'ig_user(%s){id,username,external_url,full_name,profile_pic_url,biography,followed_by{count},follows{count},media{count},is_private,is_verified}'
MEDIA_JSON_INFO = 'https://www.instagram.com/p/%s/?__a=1'
LOCATION_JSON_INFO = 'https://www.instagram.com/explore/locations/%s/?__a=1&page=%d'
RECENT_MEDIAS_BY_TAG = 'https://www.instagram.com/explore/tags/%s/?__a=1'
MEDIAS_BY_TAG = 'https://www.instagram.com/explore/tags/%s/'
MEDIAS_BY_LOCATION = 'https://www.instagram.com/explore/locations/%s/'
FOLLOWERS_JSON_BY_ID = 'https://www.instagram.com/graphql/query/?query_hash=%s&variables={"id":%s,"first":%s,"after":"%s"}'
FOLLOWS_JSON_BY_ID = 'https://www.instagram.com/graphql/query/?query_hash=%s&variables={"id":%s,"first":%s,"after":"%s"}'
AUDIENCE_JSON_BY_SHORTCODE = 'https://www.instagram.com/graphql/query/?query_hash=%s&variables={"shortcode": "%s","first":%s,"after":"%s"}'
# MEDIA_JSON_BY_LOCATION_ID = 'https://www.instagram.com/explore/locations/{{facebookLocationId}}/?__a=1&max_id={{maxId}}'
# MEDIA_JSON_BY_TAG = 'https://www.instagram.com/explore/tags/{tag}/?__a=1&max_id={max_id}'
# GENERAL_SEARCH = 'https://www.instagram.com/web/search/topsearch/?query={query}'
# LAST_COMMENTS_BY_CODE = 'ig_shortcode({{code}}){comments.last({{count}}){count,nodes{id,created_at,text,user{id,profile_pic_url,username,follows{count},followed_by{count},biography,full_name,media{count},is_private,external_url,is_verified}},page_info}}'
# COMMENTS_BEFORE_COMMENT_ID_BY_CODE = 'ig_shortcode({{code}}){comments.before({{commentId}},{{count}}){count,nodes{id,created_at,text,user{id,profile_pic_url,username,follows{count},followed_by{count},biography,full_name,media{count},is_private,external_url,is_verified}},page_info}}'
# LAST_LIKES_BY_CODE = 'ig_shortcode(%s){likes{nodes{id,user{id,profile_pic_url,username,follows{count},followed_by{count},biography,full_name,media{count},is_private,external_url,is_verified}},page_info}}'
#
# FOLLOWER_JSON_BY_ID = 'https://www.instagram.com/graphql/query/?query_id=17851374694183129&id=%s&first=%s'
# MEDIA_LIKES_JSON_BY_SHORTCODE = 'https://www.instagram.com/graphql/query/?query_id=17864450716183058&variables={"shortcode":"%s","first":%s, "after": "%s"}'

FOLLOWERS_QUERY_ID = 17851374694183129
FOLLOWING_QUERY_ID = 17874545323001329

LIKES_QUERY_ID = 17864450716183058
LIKES_QUERY_HASH = '1cb6ec562846122743b61e492c85999f'
COMMENTS_QUERY_ID = 17852405266163336
COMMENTS_QUERY_HASH = '33ba35852cb50da46f5b5e889df7d159'
MEDIA_QUERY_ID = 17888483320059182
MEDIA_QUERY_HASH = 'f2405b236d85e8296cf30347c9f08c2a'
HASHTAG_QUERY_ID = 17875800862117404

LOCATION_QUERY_ID = 17865274345132052
SUGGESTION_QUERY_HASH = '079d12b6833f01726234bd37625b4527'
STORY_QUERY_ID = 17873473675158481
# STORY_QUERY_ID = 17890626976041463
CHAINING_QUERY_ID = 17845312237175864
FOLLOWERS_QUERY_HASH = '7dd9a7e2160524fd85f50317462cff9f'
FOLLOWINGS_QUERY_HASH = 'c56ee0ae1f89cdbd1c89e2bc6b8f3d18'
HASHTAG_QUERY_HASH = 'f92f56d47dc7a55b606908374b43a314'
PROFILE_BY_ID_QUERY_HASH = '7c16654f22c819fb63d1183034a5162f'


def _build_query_string(**kwargs):
    _kwargs = remove_skip_values(kwargs)
    return '&'.join(
        map(
            lambda kv_tuple: '%s=%s' % (kv_tuple[0], json.dumps(kv_tuple[1])
            if isinstance(kv_tuple[1], dict)
            else kv_tuple[1]), _kwargs.iteritems()
        )
    )


def build_graphql_query(query_id=None, query_hash=None, **kwargs):
    _kwargs = kwargs.copy()
    if query_id:
        _kwargs['query_id'] = query_id
    elif query_hash:
        _kwargs['query_hash'] = query_hash
    else:
        raise ValueError('query_id or query_hash must be provided')
    return '%s?%s' % (GRAPHQL_URL, _build_query_string(**_kwargs))


def media_likes(shortcode, first=10, after=None):
    return build_graphql_query(query_hash=LIKES_QUERY_HASH,
                               variables={'shortcode': shortcode, 'first': first, 'after': after})


def media_comments(shortcode, first=10, after=None):
    return build_graphql_query(query_hash=COMMENTS_QUERY_HASH,
                               variables={'shortcode': shortcode, 'first': first, 'after': after})


def user_followers(id, first=10, after=None):
    return build_graphql_query(query_id=FOLLOWERS_QUERY_ID, id=id, first=first, after=after)


def user_following(id, first=10, after=None):
    return build_graphql_query(query_id=FOLLOWING_QUERY_ID, id=id, first=first, after=after)


def user_medias(id, first=12, after=None):
    return build_graphql_query(query_hash=MEDIA_QUERY_HASH, id=id, first=first, after=after)


def hashtag_medias(tag_name, first=12, after=None):
    return build_graphql_query(query_hash=HASHTAG_QUERY_HASH, tag_name=tag_name, first=first, after=after)


def recent_hashtag_medias(tag_name):
    return RECENT_MEDIAS_BY_TAG % tag_name


def location_medias(id, first=12, after=None):
    return build_graphql_query(query_id=LOCATION_QUERY_ID, id=id, first=first, after=after)


def user_suggestions(id):
    return build_graphql_query(query_hash=SUGGESTION_QUERY_HASH, variables={'chaining_id': id, 'skip_chaining': False,
                                                                            'skip_suggested_users': True})


def user_stories(ids, precomposed_overlay=False):
    return build_graphql_query(STORY_QUERY_ID, variables={'reel_ids': ids, 'precomposed_overlay': precomposed_overlay})


def media_link(shortcode):
    return '%s/p/%s/' % (BASE_URL, shortcode)


def chaining_users(id):
    return build_graphql_query(CHAINING_QUERY_ID, variables={'id': str(id)})


def user_followers_by_id(id, first=50, after=None):
    return FOLLOWERS_JSON_BY_ID % (FOLLOWERS_QUERY_HASH, id, first, after)


def user_followings_by_id(id, first=50, after=None):
    return FOLLOWS_JSON_BY_ID % (FOLLOWINGS_QUERY_HASH, id, first, after)


def media_likes_by_shortcode(shortcode, first=50, after=None):
    return AUDIENCE_JSON_BY_SHORTCODE % (LIKES_QUERY_HASH, shortcode, first, after)


def media_comments_by_shortcode(shortcode, first=50, after=None):
    return AUDIENCE_JSON_BY_SHORTCODE % (COMMENTS_QUERY_HASH, shortcode, first, after)


def user_info_by_id(id):
    return build_graphql_query(query_hash=PROFILE_BY_ID_QUERY_HASH, variables={'user_id': id, 'include_reel': True})


if __name__ == '__main__':
    print(user_info_by_id('5849639380'))
