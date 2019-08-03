# coding: utf-8
from xde.core.constant import ACTION_COMMENT, SNS_NAME_INSTAGRAM
from xde.models.audience import Audience


def build_audience_from_comment(post, comment):
    """
    Builds audience model from post's comment

    :param post: Post object having comment or dict containing keys
        sns_id (post_id)
        user_sns_id
    :param comment: comment of above post
    Type: Comment object or dict containing following keys
        id  (this is ins' comment id)
        owner
            id (ins's commenter id)
            username
        created_at

        Example
            {
                id: "17850332725499911",
                text: "❤️❤️❤️",
                created_at: 1563741121,
                owner: {
                    id: "9937933636",
                    profile_pic_url: "<url-to-pic>",
                    username: "andi_oficial_"
                },
                viewer_has_liked: false,
                edge_liked_by: {
                count: 0
                }
            }
    :return:
    """
    engaged_username = comment.get('owner', {}).get('username')
    engaged_sns_id = comment.get('owner', {}).get('id')
    acted_at = comment.get('created_at')  # time of commenting
    body = comment.get('text')

    # TODO - verify if username is still used?
    audience = Audience(
        sns_name=SNS_NAME_INSTAGRAM,
        sns_id=comment['id'],
        post_sns_id=post.get('sns_id'),
        user_sns_id=post.get('user_sns_id'),
        username=post.get('sns_account', {}).get('username'),
        engaged_username=engaged_username,
        engaged_sns_id=engaged_sns_id,
        action=ACTION_COMMENT,
        body=body,
        acted_at=acted_at,
    )
    return audience

