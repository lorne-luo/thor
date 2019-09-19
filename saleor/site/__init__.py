class AuthenticationBackends:
    GOOGLE = "google-oauth2"
    FACEBOOK = "facebook"
    WECHAT = "wechat"
    QQ = "qq"
    WEIBO = "weibo"

    BACKENDS = ((FACEBOOK, "Facebook-Oauth2"),
                (GOOGLE, "Google-Oauth2"),
                (WEIBO, "Weibo-Oauth2"),
                (QQ, "QQ-Oauth2"),
                (WECHAT, "Wechat-Oauth2"))
