from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup 

def fetchFromURL(url):
    try:

        with closing(get(url, stream=True)) as resp:

            if is_good_response(resp):

                return resp.content

            else:
                return None



    except RequestException as e:

        log_error('Error during request to {0}:{1}' . format(url, str(e)))

        return None

 

def is_good_response(resp):

    """

    Returns True if response looks like HTML

    """

    content_type = resp.headers['Content-Type'].lower()

    return (resp.status_code == 200

            and content_type is not None

            and content_type.find('html') > -1)

 

def log_error(e):

    """

    log those errors or you'll regret it later...

    """

    print(e)

 

def get_target_urls(target):

    """

    Example of isolating different parent elements to gather subsequent URLs

    """

    soup = BeautifulSoup(target, 'html.parser')

    print(soup.prettify())
    for row in soup.find_all('td'):

        for link in row.find_all('a'):

            print(link.get('href'))