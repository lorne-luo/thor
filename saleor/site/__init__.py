class AuthenticationBackends:
    GOOGLE = "google-oauth2"
    FACEBOOK = "facebook"
    WEIXIN = "weixin"
    WEIXINMP = "weixinmp"
    QQ = "qq"
    WEIBO = "weibo"

    BACKENDS = (
        (WEIBO, "Weibo-Oauth2"),
        (QQ, "QQ-Oauth2"),
        (WEIXIN, "Weixin-Oauth2"),
        (WEIXINMP, "WeixinMP-Oauth2"),
        # (FACEBOOK, "Facebook-Oauth2"),
        # (GOOGLE, "Google-Oauth2")
    )
