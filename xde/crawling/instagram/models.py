from .endpoints import media_link
from .utils import extract_hashtags, extract_shortcode, datetime_from_timestamp
import datetime
import json as json_


class Model(dict):
    __api = None

    @classmethod
    def parse(cls, json):
        return cls(json)

    @property
    def api(self):
        if self.__api is None:
            from . import web
            self.use_api(web.InstagramWebApi())
        return self.__api

    @property
    def selenium_api(self):
        from . import web
        return web.InstagramSeleniumApi()

    @property
    def web_api(self):
        from . import web
        return web.InstagramWebApi()

    def use_api(self, api):
        self.__api = api
        return self

    def fetch(self):
        """Fetch model data from Instagram.Com"""
        raise NotImplementedError("Sub class must implement this method.")

    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError('Property "%s" not found in %s.' % (name, self.__class__.__name__))

    def __repr__(self):
        state = ['%s=%s' % (k, repr(v)) for (k, v) in self.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(state))


class User(Model):
    def __init__(self, username=None, **kwargs):
        super(User, self).__init__(username=username, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.api.logout()

    @classmethod
    def parse(cls, json):
        if json is None:
            return cls()

        return cls(
            username=json.get('username'),
            id=json.get('id'),
            full_name=json.get('full_name'),
            profile_picture=json.get('profile_pic_url'),
            profile_picture_hd=json.get('profile_pic_url_hd', json.get('hd_profile_pic_url_info', {}).get('url')),
            bio=json.get('biography'),
            website=json.get('external_url'),
            counts={
                'media': json.get('media_count') if json.get('media_count') else
                json.get('edge_owner_to_timeline_media', {}).get('count'),
                'follows': json.get('following_count') if json.get('following_count') else
                json.get('edge_follow', {}).get('count'),
                'followed_by': json.get('follower_count') if json.get('follower_count') else
                json.get('edge_followed_by', {}).get('count')
            },
            is_verified=json.get('is_verified'),
            is_private=json.get('is_private'),
            email=json.get('business_email'),
            category=json.get('business_category_name'),
            is_business=json.get('is_business_account'),
            phone_number=json.get('business_phone_number'),
            address=json.get('business_address_json')
        )

    @staticmethod
    def parse_mobile_phone_number(json):
        contact_phone_number = json.get('contact_phone_number')
        phone_number = contact_phone_number if contact_phone_number else json.get('public_phone_number')
        if phone_number:
            if phone_number.startswith('0'):
                phone_number = phone_number[1:]
            public_phone_country_code = json.get('public_phone_country_code')
            if public_phone_country_code:
                phone_number = '+{}{}'.format(public_phone_country_code, phone_number)
                return phone_number
        return ''

    @classmethod
    def parse_mobile(cls, json):
        if json is None:
            return cls()
        return cls(
            username=json.get('username'),
            id=str(json.get('pk')),
            full_name=json.get('full_name'),
            profile_picture=json.get('profile_pic_url'),
            profile_picture_hd=json.get('hd_profile_pic_url_info', {}).get('url'),
            bio=json.get('biography'),
            website=json.get('external_url'),
            counts={
                'media': json.get('media_count'),
                'follows': json.get('following_count'),
                'followed_by': json.get('follower_count')
            },
            is_verified=json.get('is_verified'),
            is_private=json.get('is_private'),
            email=json.get('public_email'),
            category=json.get('category'),
            is_business=json.get('is_business'),
            phone_number=cls.parse_mobile_phone_number(json),
            address=json_.dumps(
                {
                    "street_address": json.get('address_street'),
                    "zip_code": json.get('zip'),
                    "city_name": json.get('city_name'),
                    "city_id": json.get('city_id'),
                    "longitude": json.get('longitude'),
                    "latitude": json.get('latitude')
                }
            ),
            usertags_count=json.get('usertags_count'),
            has_anonymous_profile_picture=json.get('has_anonymous_profile_picture')

        )

    def fetch(self):
        if self.get('username'):
            user = self.api.get_user_by_username(self.get('username'))
            self.update(User.parse(user))
        else:
            user = self.api.get_user_by_id(self.get('id'))
            self.update(User.parse(user))
        return self

    def medias(self, count=100):
        """Get the list of medias from user timeline"""
        medias = self.api.get_user_medias_by_id(self.get('id'))
        if count > 0:
            for each in medias:
                yield Media.parse(each)
                count -= 1
                if count == 0:
                    break
        else:
            for each in medias:
                yield Media.parse(each)

    def selenium_medias(self, crawled_urls=None, count=100):
        """Get a given number of medias from a user's timeline"""
        if count < 0:
            for url in self.api.get_media_urls_by_username(self.get('username'), crawled_urls):
                yield Media.parse(self.api.get_media_by_code(extract_shortcode(url)))
        else:
            count_crawled_urls = len(crawled_urls) if isinstance(crawled_urls, list) else 0
            to_crawl = count - count_crawled_urls
            if to_crawl <= 0:
                return
            for url in self.api.get_media_urls_by_username(self.get('username'), crawled_urls):
                yield Media.parse(self.api.get_media_by_code(extract_shortcode(url)))
                to_crawl -= 1
                if to_crawl == 0:
                    break

    def followers(self):
        """Return a list of followers of this user using given credentials"""
        self._make_sure_id_available()
        for each in self.api.get_user_followers(self.get('id')):
            yield User.parse(each)

    def selenium_followers(self):
        """Return a list of followers of this user using given credentials"""
        for each in self.api.get_followers_by_username(self.get('username')):
            yield User.parse(self.api.get_user_by_username(each.get('username')))

    def selenium_followings(self):
        """Return a list of followings of this user using given credentials"""
        for each in self.api.get_followings_by_username(self.get('username')):
            yield User.parse(self.api.get_user_by_username(each.get('username')))

    def following(self):
        """Return a list of following of this user using given credentials"""
        self._make_sure_id_available()
        for each in self.api.get_user_following(self.get('id')):
            yield User.parse(each)

    def suggested_users(self):
        """ Return a list of suggested users for this user using given credentials"""
        self._make_sure_id_available()
        for each in self.api.get_suggested_users(self.get('id')):
            yield User.parse(each)

    def stories(self):
        self._make_sure_id_available()
        return self.api.get_user_stories(self.get('id'))

    def chaining_users(self):
        """Return the list of chaining uses of this user using a given credentials"""
        self._make_sure_id_available()
        for user in self.api.get_chaining_users(self.get('id')):
            yield User.parse(user)

    def _make_sure_id_available(self):
        if self.get('id') is None:
            self.fetch()


class Comment(Model):
    def __init__(self, id=None, **kwargs):
        super(Comment, self).__init__(id=id, **kwargs)

    @classmethod
    def parse(cls, json):
        if json is None:
            return cls()
        return cls(
            id=json.get('id'),
            user=User.parse(json.get('owner')),
            created_time=json.get('created_at'),
            text=json.get('text')
        )


class Media(Model):
    def __init__(self, shortcode=None, id=None, **kwargs):
        super(Media, self).__init__(id=id, shortcode=shortcode, **kwargs)

    @classmethod
    def parse(cls, json):
        if json is None:
            return cls()
        caption = json.get('edge_media_to_caption', {}).get('edges', [])
        caption = caption[-1].get('node') if caption else None
        tags = [tag.lower() for tag in set(extract_hashtags(caption.get('text')) if caption else [])]
        dimensions = json.get('dimensions')
        owner_id = json.get('owner', {}).get('id')
        for key in ('edge_media_preview_comment', 'edge_media_to_comment'):
            if key in json:
                comment = json.get(key, {})
                comment_count = comment.get('count')
                break

        for each in comment.get('edges', []):
            if each.get('node', {}).get('owner', {}).get('id') == owner_id:
                for tag in extract_hashtags(each.get('node', {}).get('text')):
                    tags.append(tag.lower())
        tags = list(set(tags))


        media = cls(
            id=json.get('id'),
            shortcode=json.get('shortcode') or json.get('code'),
            comments={'count': comment_count},
            caption=caption,
            tags=tags,
            likes={'count': json.get('edge_media_preview_like', json.get('edge_liked_by', {})).get('count')},
            link=media_link(json.get('shortcode')),
            user=User.parse(json.get('owner')),
            created_time=json.get('taken_at_timestamp'),
            images={
                'standard_resolution': {
                    'url': json.get('display_url'),
                    'width': dimensions.get('width'),
                    'height': dimensions.get('height')
                }
            },
            type=json.get('__typename').lower().replace('graph', '').strip() if '__typename' in json else None,
            is_ad=json.get('is_ad'),
            location=json.get('location'),
            users_in_photo=[
                {
                    'user': User.parse(edge.get('node').get('user')),
                    'position': {
                        'x': edge.get('node').get('x'),
                        'y': edge.get('node').get('y')
                    }
                } for edge in json.get('edge_media_to_tagged_user', {}).get('edges', [])
            ],
            sponsors=json.get('edge_media_to_sponsor_user', {}).get('edges', [])
        )

        if media.get('type') == 'video' or json.get('is_video'):
            media['videos'] = {
                'standard_resolution': {
                    'url': json.get('video_url'),
                    'width': dimensions.get('width'),
                    'height': dimensions.get('height')

                }
            }
            media['video_view_count'] = json.get('video_view_count')

        return media

    def fetch(self):
        if not self.get('shortcode'):
            raise ValueError('The fetch method requires field `shortcode`')
        media = self.api.get_media_by_code(self.get('shortcode'))
        self.update(Media.parse(media))
        return self

    def comments(self):
        """Returns a list of comments of this media."""
        count = self.get('comments', {}).get('count')
        if count is None or count > 0:
            for each in self.api.get_media_comments_by_code(self.get('shortcode')):
                yield Comment.parse(each)

    def likes(self):
        """Returns a list of users who have liked this media."""
        count = self.get('likes', {}).get('count')
        if count is None or count > 0:
            for each in self.api.get_media_likes_by_code(self.get('shortcode')):
                yield User.parse(each)

    def selenium_likes(self):
        """Returns a list of users who liked this media."""
        for each in self.api.get_likers_from_post(shortcode=self.get('shortcode')):
            yield User.parse(self.api.get_user_by_username(each.get('username')))


class Tag(Model):
    def __init__(self, name, **kwargs):
        if not name:
            raise ValueError('Tag name is required!')

        super(Tag, self).__init__(name=name, **kwargs)

    def count(self):
        """Count number of posts have been tagged with this tag"""
        return self.api.count_medias_by_tag(tag=self.get('name'))

    def medias(self):
        """Get recent medias have been tagged with this tag"""
        for each in self.api.get_medias_by_tag(tag=self.get('name'), per_page=100):
            yield Media.parse(each)

    def selenium_medias(self, crawled_urls=None):
        urls = self.api.get_recent_media_urls_by_tag(tagname=self.get('name'), crawled_urls=crawled_urls)
        for each in urls:
            yield Media.parse(self.api.get_media_by_code(extract_shortcode(each)))

    def medias_with_cusors(self, end_cursor=None):
        """Get recent medias with cursors having this this tag"""
        for media, page_info in self.api.get_medias_with_cursors_by_tag(tag=self.get('name'), per_page=100, end_cursor=end_cursor):
            yield Media.parse(media), page_info

    def top_medias(self):
        for each in self.api.get_top_medias_by_tag(tag=self.get('name')):
            yield Media.parse(each)

    def recent_medias(self, batch=False):
        for each in self.api.get_recent_medias_by_tag(tag=self.get('name'), batch=batch):
            if batch:
                yield [Media.parse(post) for post in each]
            else:
                yield Media.parse(each)


class Location(Model):
    def __init__(self, id, **kwargs):
        if not id:
            raise ValueError('location id is required')
        super(Location, self).__init__(id=id, **kwargs)

    def count(self):
        return self.api.count_medias_by_location(id=self.get('id'))

    def recent_medias(self, batch=False):
        for each in self.api.get_recent_medias_by_location(id=self.get('id'), batch=batch):
            if batch:
                yield [Media.parse(post) for post in each]
            else:
                yield Media.parse(each)

    def top_medias(self):
        for each in self.api.get_top_medias_by_location(id=self.get('id')):
            yield Media.parse(each)


class City(Model):
    def __init__(self, id, **kwargs):
        if not id:
            raise ValueError('city id is required')
        super(City, self).__init__(id=id, **kwargs)

    def locations(self, page=None):
        if page is None:
            page = range(1, 22)
        return self.api.get_locations_by_city(self.id, page)
