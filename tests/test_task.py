from xde.tasks import crawl_user

if __name__ == '__main__':
    res = crawl_user.delay(['theplugbyxomad'])
    print(res)

