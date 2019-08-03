from xde.core.constant import SNS_NAME_INSTAGRAM, SNS_NAME_TWITTER, WEIGHT_INSTAGRAM, WEIGHT_TWITTER


class Consumer(object):
    """Consumer is an abstract layer on top of SnsAccount and User

    Consumer's schema is documented at https://rxperry.atlassian.net/wiki/pages/viewpage.action?pageId=6946821
    """
    _FIELDS_META = {'id'}

    FIELDS_BASIC_PROFILE = {'sns_name', 'sns_id', 'status', 'created_at', 'updated_at', 'user_id', 'username', 'link',
                            'name', 'bio', 'avatar_url', 'location', 'cover_url', 'source', 'is_private', 'is_verified',
                            'email', 'category', 'is_business', 'phone_number', 'address'}
    FIELDS_ENRICHED = {'birthyear', 'gender', 'marital', 'parental', 'sns', 'tags', 'x_location'}
    FIELDS_METRICS = {'engagement', 'engagement_rate', 'reach', 'posts_count', 'xfluences'}
    FIELDS_STATS = {'followers_count', 'followings_count', 'likes_count', 'lists_count', 'statuses_count'}

    FIELDS_COMPACTED_FORMAT = _FIELDS_META.union(FIELDS_BASIC_PROFILE).union(FIELDS_STATS).union(FIELDS_METRICS)
    ACCEPTED_FIELDS = _FIELDS_META.union(FIELDS_BASIC_PROFILE).union(FIELDS_STATS).union(FIELDS_ENRICHED) \
        .union(FIELDS_METRICS)

    def __init__(self, **kwargs):
        for field in self.ACCEPTED_FIELDS:
            setattr(self, field, kwargs.get(field))

        # sns_name and sns_id are mandatory
        if not self.id:
            self.id = '%s-%s' % (kwargs['sns_name'], kwargs['sns_id'])

    def __repr__(self):
        return '%s:%s' % (self.__class__.__name__, self.id)

    @staticmethod
    def from_sns_account(sns_account):
        if sns_account:
            d = sns_account.as_dict()
            d['source'] = d.pop('sources')
            enriched = sns_account.sns_account_enriched
            if enriched:
                d.update(enriched.as_dict())
                d.update({
                    'updated_at': max(sns_account.updated_at, enriched.updated_at),
                    'marital': enriched.marital_status,
                    'parental': enriched.is_parent
                })
                if enriched.locations and isinstance(enriched.locations, list):
                    x_location = []
                    for l in enriched.locations:
                        l['_all'] = list(set([_ for _ in (
                            l.get('locality'), l.get('region_a'), l.get('region'), l.get('country_a2'),
                            l.get('country_a3'), l.get('country')
                        ) if _]))
                        x_location.append(l)
                    d['x_location'] = x_location
            return Consumer(**d)
        return None

    @staticmethod
    def from_user(user):
        if user:
            d = {
                'sns_name': 'x',
                'sns_id': str(user.user_id),
                'status': user.status,
                'created_at': user.created_at,
                'updated_at': user.updated_at,
                'user_id': user.user_id,
                'link': '/profile/%s' % user.user_id,
                'name': user.fullname,
                'bio': user.bio,
                'avatar_url': user.avatar_url,
                'location': user.locations[0] if user.locations else None,
                'cover_url': user.cover_url
            }

            if user.sns_accounts:
                tags = set()
                x_location = []
                engagement_rate_list = []
                xfluences = {}
                for field in ['engagement', 'reach', 'posts_count', 'followers_count', 'followings_count',
                              'likes_count', 'lists_count', 'statuses_count']:
                    d[field] = 0
                d['sns'] = {}
                for sns_account in user.sns_accounts or []:
                    sns_consumer = Consumer.from_sns_account(sns_account)

                    # Embed SNS compact info
                    d['sns'][sns_consumer.sns_name] = sns_consumer.as_dict(fields=Consumer.FIELDS_COMPACTED_FORMAT)
                    # Accumulate enriched attributes
                    if sns_consumer.tags:
                        tags.update(set(sns_consumer.tags))
                    if sns_consumer.x_location:
                        x_location.extend(sns_consumer.x_location)
                    for field in ['birthyear', 'gender', 'marital', 'parental']:
                        value = getattr(sns_consumer, field)
                        if field not in d and value is not None:
                            d[field] = value

                    # Calculate metrics at User level
                    if sns_consumer.engagement_rate is not None:
                        engagement_rate_list.append(sns_consumer.engagement_rate)
                    if sns_consumer.xfluences:
                        if sns_consumer.sns_name == SNS_NAME_INSTAGRAM:
                            weight = WEIGHT_INSTAGRAM
                        elif sns_consumer.sns_name == SNS_NAME_TWITTER:
                            weight = WEIGHT_TWITTER
                        else:
                            weight = 0.
                        for xfluence in sns_consumer.xfluences:
                            aoi_id = xfluence['aoi_id']
                            if aoi_id not in xfluences:
                                xfluences[aoi_id] = 0
                            xfluences[aoi_id] += weight * xfluence['score']
                    for field in ['engagement', 'reach', 'posts_count']:
                        d[field] += getattr(sns_consumer, field) or 0

                    # Sum up stats
                    for field in Consumer.FIELDS_STATS:
                        d[field] += getattr(sns_consumer, field) or 0

                d['tags'] = list(tags)
                d['x_location'] = x_location
                d['engagement_rate'] = sum(engagement_rate_list) / float(len(engagement_rate_list) or 1)
                d['xfluences'] = [{'aoi_id': aoi_id, 'score': score} for aoi_id, score in xfluences.items()]
                d['xfluences'].sort(key=lambda x: x['score'], reverse=True)

            return Consumer(**d)
        return None

    def as_dict(self, fields=None):
        if fields:
            return {_: getattr(self, _) for _ in fields if _ in self.ACCEPTED_FIELDS}
        return self.__dict__

    def update_from_dict(self, a_dict):
        for k, v in a_dict.items():
            if k in self.ACCEPTED_FIELDS:
                setattr(self, k, v)
