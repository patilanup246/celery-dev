from celery import chain

from xde.tasks.crawling.instagram import crawl_user, process_user, write_user


if __name__ == '__main__':
    # res = crawl_user.delay(['theplugbyxomad'])
    res = chain(
        crawl_user.s(['simplymadhoo']),
        process_user.s(),
        write_user.s()
    ).apply_async()
    print(res)
    print(type(res))

