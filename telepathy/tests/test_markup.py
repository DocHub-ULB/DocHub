from telepathy.templatetags.custommardown import youtube_url


def test_youtube_url():
    assert youtube_url.match("https://www.youtube.com/watch?v=TluTv5V0RmE&list=PLUl4u3cNGP60A3XMwZ5sep719_nh95qOe&index=5")
    assert youtube_url.match("https://youtube.com/watch?v=TluTv5V0RmE&list=PLUl4u3cNGP60A3XMwZ5sep719_nh95qOe&index=5")
    assert youtube_url.match("https://www.youtube.com/watch?v=0-CwXKrRCF0")
    assert youtube_url.match("https://www.youtube.com/watch?v=pJfDnJtsxc4")
    assert youtube_url.match("https://youtu.be/pJfDnJtsxc4?t=2s")
