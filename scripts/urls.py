import fnmatch, string, logging


def fnmatches_multiple(patterns, s):
    for p in patterns:
        if fnmatch.fnmatch(s, p):
            return True
    return False


def domain(url):
    """
    >>> domain('http://https://test.com')
    'https'
    >>> domain('http://test.com?site=https://other.com')
    'test.com'
    >>> domain('http://test.com/index?test=1')
    'test.com'
    >>> domain('http://indiana.facebook.com/dir1/page.html')
    'indiana.facebook.com'
    >>> domain('http://facebook.com')
    'facebook.com'
    >>> domain('http://www.facebook.com:80/')
    'facebook.com'
    """
    url = (''.join(filter(lambda c: c in string.printable, url))).lower()

    # remove protocol
    idx = url.find("://")
    if idx != -1:
        url = url[idx + 3:]

    # remove port
    idx = url.find(":")
    if idx != -1:
        url = url[:idx]

    # remove trailing / and everything that follows
    idx = url.find("/")
    if idx != -1:
        url = url[:idx]

    # remove ? and anything that follows if it wasn't in previous steps
    idx = url.find("?")
    if idx != -1:
        url = url[:idx]

    url_is_clean = False
    while not url_is_clean:
        if url.startswith('www.'):
            url = url[4:]
        elif url.startswith('www2.') or url.startswith('www3.'):
            url = url[5:]
        else:
            url_is_clean = True
    return url


def is_exception(host):
    """
    Exceptions are domain names such as google.co.uk or hire.mil.gov, where the top level domain can be thought of co.uk or mil.gov rather than .uk or .gov. These domains need to be processed as a special case when converting the domain level from one level to another, since they are essentially of one level higher than they would ordinarily be thought of. That is, google.co.uk is a 3rd level domain, but for practicel purposes it should be considered a 2nd level domain.

    >>> is_exception('')
    False
    >>> is_exception('google.com')
    False
    >>> is_exception('google.co.uk')
    True
    >>> is_exception('hire.mil.gov')
    True
    >>> is_exception('indiana.edu')
    False
    >>> is_exception('indiana.edu.us')
    True
    >>> is_exception('whitehouse.gov')
    False
    """
    exceptions = [".com.", ".net.", ".org.", ".edu.", ".mil.", ".gov.", ".co."]
    for e in exceptions:
        if e in host:
            return True
    return False


def is_ip_address(host):
    """
    >>> is_ip_address('')
    False
    >>> is_ip_address('192.168.2.1')
    True
    >>> is_ip_address('192')
    False
    >>> is_ip_address('192.168')
    False
    >>> is_ip_address('192.168.2')
    False
    >>> is_ip_address('...')
    False
    >>> is_ip_address('asdf.asdf.asdf.asdf')
    False
    >>> is_ip_address('999.0.0.1')
    False
    """
    raw_parts = host.strip().split('.')
    parts = [p for p in raw_parts if p != '']
    if len(parts) != 4:
        return False
    else:
        for part in parts:
            if part.isdigit() and int(part) >= 0 and int(part) <= 255:
                pass
            else:
                return False
    return True


def domain_level(host):
    """
    >>> domain_level('')
    0
    >>> domain_level('    ')
    0
    >>> domain_level('com')
    1
    >>> domain_level('facebook.com')
    2
    >>> domain_level('indiana.facebook.com')
    3
    """
    if host.strip() == '':
        return 0
    else:
        raw_parts = host.strip().split('.')
        parts = [p for p in raw_parts if p != '']
        return len(parts)


def nth_level_domain(host, n):
    """
    >>> nth_level_domain('facebook.com', 1)
    'com'
    >>> nth_level_domain('', 2)
    ''
    >>> nth_level_domain('facebook.com', 2)
    'facebook.com'
    >>> nth_level_domain('facebook.com', 3)
    'facebook.com'
    >>> nth_level_domain('indiana.facebook.com', 2)
    'facebook.com'
    """
    raw_parts = host.strip().split('.')
    parts = [p for p in raw_parts if p != '']
    if len(parts) <= n:
        return ".".join(parts)
    else:
        s = ".".join(n * ["%s"])
        new_parts = tuple(parts[-n:])
        return s % new_parts


def change_domain_level(host, domain_level):
    """
    >>> change_domain_level('192.168.2.1', 2)
    '192.168.2.1'
    >>> change_domain_level('192.168.2', 2)
    '168.2'
    >>> change_domain_level('', 2)
    ''
    >>> change_domain_level('indiana.facebook.com', 2)
    'facebook.com'
    >>> change_domain_level('facebook.com', 3)
    'facebook.com'
    >>> change_domain_level('google.co.uk', 2)
    'google.co.uk'
    >>> change_domain_level('google.co.uk', 3)
    'google.co.uk'
    >>> change_domain_level('192.168.2.1.', 3)
    '192.168.2.1'
    """
    raw_parts = host.strip().split(".")
    parts = [p for p in raw_parts if p != '']
    if is_ip_address(host):
        return ".".join(parts)
    elif is_exception(host):
        return nth_level_domain(host, domain_level + 1)
    else:
        return nth_level_domain(host, domain_level)


def parents(url):
    """
    >>> parents('facebook.com')
    []
    >>> parents('indiana.facebook.com')
    ['facebook.com']
    >>> parents('1.2.3.news.bbc.co.uk')
    ['2.3.news.bbc.co.uk', '3.news.bbc.co.uk', 'news.bbc.co.uk', 'bbc.co.uk']
    """
    parent_urls = []
    dl = domain_level(url)
    if is_exception(url):
        end = 2
    else:
        end = 1
    for parent_dl in range(dl - 1, end, -1):
        parent_urls.append(nth_level_domain(url, parent_dl))
    return parent_urls

if __name__ == "__main__":
    logging.info('Testing...')
    import doctest
    doctest.testmod()
