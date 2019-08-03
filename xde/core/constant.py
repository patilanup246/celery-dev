# Copyright (C) 2015 Xomad. All rights reserved.
#
# Created on 12/11/2015

import math

SNS_NAME_FACEBOOK = 'fb'
SNS_NAME_INSTAGRAM = 'ins'
SNS_NAME_SNAPCHAT = 'sc'
SNS_NAME_TWITTER = 'tw'
SNS_NAME_WEB = 'web'
SNS_NAME_XOMAD = 'x'
SNS_NAME_YOUTUBE = 'yt'
ACCEPTED_SNS_NAMES = {SNS_NAME_FACEBOOK, SNS_NAME_INSTAGRAM, SNS_NAME_SNAPCHAT, SNS_NAME_TWITTER, SNS_NAME_YOUTUBE,
                      SNS_NAME_WEB}

STATUS_ACTIVE = 1
STATUS_INACTIVE = 0

# The percentile for a sns account to have to gain the status expert
# The default setting is 90, means a sns account has to have the score that is larger than 90% of the rest,
# or in the top 10% of all
EXPERT_PERCENTILE = 90

# TTL 90 days
REDIS_TTL = 90 * 24 * 3600
# temp TTL 4 weeks
REDIS_TEMP_TTL = 4 * 7 * 24 * 3600
# TTL 90 days
CASSANDRA_TTL = 365 * 24 * 3600

# decay parameters
DECAY_INTERVAL_GURU = 8

DECAY_INTERVAL = 4
DECAY_VALUE = 0.8

DECAY_RATE = math.pow(DECAY_VALUE, 1.0 / DECAY_INTERVAL)
DECAY_RATE_GURU = math.pow(DECAY_VALUE, 1.0 / DECAY_INTERVAL_GURU)

TWITTER = 'tw'
INSTAGRAM = 'in'

INSTAGRAM_QUALITY_NETWORK = 'instagram_quality_network'
INSTAGRAM_ENGAGEMENT = 'instagram_engagement'
INSTAGRAM_IMPRESSION = 'instagram_impression'
INSTAGRAM_XFLUENCE = 'instagram_xfluence'

TWITTER_QUALITY_NETWORK = 'twitter_quality_network'
TWITTER_ENGAGEMENT = 'twitter_engagement'
TWITTER_IMPRESSION = 'twitter_impression'
TWITTER_XFLUENCE = 'twitter_xfluence'

XFLUENCE = 'xfluence'

METRICS = {
    INSTAGRAM_QUALITY_NETWORK: 1,
    TWITTER_QUALITY_NETWORK: 2,
    INSTAGRAM_ENGAGEMENT: 3,
    TWITTER_ENGAGEMENT: 4,
    INSTAGRAM_IMPRESSION: 5,
    TWITTER_IMPRESSION: 6,
    INSTAGRAM_XFLUENCE: 7,
    TWITTER_XFLUENCE: 8,
    XFLUENCE: 9
}

LOG_BASE = math.e

SCHEME_GOOGLE_CLOUD_STORAGE = 'gs'

# WEIGHT_INSTAGRAM_QUALITY_NETWORK = 0.2
WEIGHT_INSTAGRAM_ENGAGEMENT = 1.
WEIGHT_INSTAGRAM_REACH = 1.

# WEIGHT_TWITTER_QUALITY_NETWORK = 0.2
WEIGHT_TWITTER_ENGAGEMENT = 1.
WEIGHT_TWITTER_REACH = 1.

WEIGHT_TWITTER = 0.3
WEIGHT_INSTAGRAM = 0.7

# VIP INVITATION EMAIL TYPE
NON_EXISTED_EMAIL = 1
EXISTED_EMAIL = 2
FROM_HOST = 3

# AUDIENCES
ACTION_LIKE = 0
ACTION_COMMENT = 1

# SPONSORED POSTS
SPONSORED_HASHTAGS = ["#ad", "#brandambassador", "#collaboration", "#disclosure", "#gift", "#gifted", "#giftedby",
                      "#giftfrom", "#partner", "#promo", "#promotion", "#sp", "#spon", "#sponsored", "#sponsor",
                      "#sponsorship", "#sponsoreret", "#sponsoredpost", ""]

SPONSORED_PHRASES = ["brought to you by", "compensated by", "gift from", "gifted by", "in collaboration with",
                     "collaborated with", "in partnership with", "paid ad", "paid advertisement", "paid by",
                     "paid for by", "paid partnership with", "paid post", "paid promo", "paid promotion",
                     "paid sponsorship", "partnered up with", "partnered with", "partnering with", "partnership with",
                     "sponsored by", "sponsored post", "teamed up with", "teamed with", "teaming up with",
                     "teaming with", "brand partner", "working with", "promo code", "coupon code", "discount code",
                     "referral link", "brand partnership", "representing", "advertising", "advertisement",
                     "in collaboration with"]

# crawlers
PAGE_NOT_FOUND_MSG = "Sorry, this page isn't available."
PRIVATE_ACCOUNT_MSG = 'This Account is Private'
PRIVATE_ACCOUNT_POST_COUNT = -1

# PIPES
collab_pipe = 'collab'
stream_pipe = 'stream'

