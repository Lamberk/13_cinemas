import requests
import operator
import argparse

from bs4 import BeautifulSoup


SHEDULE_URL = 'http://www.afisha.ru/msk/schedule_cinema_product/{}/'
AFISHA_URL = 'http://www.afisha.ru/msk/schedule_cinema/'
KINOPOISK_SEARCH_URL = 'https://www.kinopoisk.ru/index.php'
KINOPOISK_URL = 'https://www.kinopoisk.ru{}'


def load_afisha_page():
    soup = BeautifulSoup(requests.get(AFISHA_URL).text, 'lxml')
    films = []
    for film in soup.select('div.object.s-votes-hover-area.collapsed'):
        film_id = int(film['id'].split('_')[1])
        film_name = film.select('h3.usetags a')[0].contents[0]
        films.append({'id': film_id, 'name': film_name})
    return films


def get_cinemas_count(film):
    shedule = requests.get(SHEDULE_URL.format(film.get('id'))).text
    soup = BeautifulSoup(shedule, 'lxml')
    count_3d = len(soup.select('tr.s-tr-next3d'))
    count = (len(soup.select('td.b-td-item')))
    all_count = count + count_3d
    return all_count


def get_rating(film):
    film_page = requests.get(
        KINOPOISK_SEARCH_URL, params={'kp_query': film.get('name')},
    ).text
    soup = BeautifulSoup(film_page, 'lxml')
    film_url = soup.select(
        'div.element.most_wanted p.name a.js-serp-metrika'
    )[0]['data-url']
    film = requests.get(KINOPOISK_URL.format(film_url)).text
    soup = BeautifulSoup(film, 'lxml')
    try:
        rating = float(soup.select('div.div1 span.rating_ball')[0].contents[0])
    except IndexError as e:
        rating = 0
    return rating


def output_movies_to_console(films):
    for film in films:
        print('#'*80)
        print('Film name:', film.get('name'))
        print('Film rating:', film.get('rating'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-e',
        action='store_true',
        help='Easy to find, big cinemas_count',
    )
    args = parser.parse_args()

    films = load_afisha_page()
    for film in films:
        cinemas_count = get_cinemas_count(film)
        rating = get_rating(film)
        film['cinemas_count'] = cinemas_count
        film['rating'] = rating
    if args.e:
        films = [film for film in films if film['cinemas_count'] > 50]
    sorted_films = sorted(films, key=lambda x: x['rating'])
    output_movies_to_console(sorted_films[-10:])
