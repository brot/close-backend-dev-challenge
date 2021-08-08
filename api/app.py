import random
import string
from typing import List, Sequence

import redis
import requests
from flask import Flask, request, url_for

app = Flask(__name__)
redis_cache = redis.StrictRedis(host="redis", port=6379)


REDIS_SORTED_SET = "API_URL_REQUEST_STATS"


@app.route("/api/<path:url_path>/", methods=["GET"])
def simulated_api_endpoints(url_path: str):
    """
    Count the requests for every single unique URL in Redis.

    The Redis data structure used to store the statistic data is a Sorted Set.
    A Sorted Set does not allow duplicate members and the members are ordered.

    :param url_path: randomly generated URL path
    """
    redis_cache.zincrby(REDIS_SORTED_SET, 1, request.path)

    # not sure what to return, so just return a simple message as response body
    return f"Request {request.path} finished"


@app.route("/stats/", methods=["GET"])
def get_stats():
    """
    Get statistics for all URL request counts ordered from most requested to least requested.
    """
    # Because the request_count is already stored ordered in Redis we
    # just need to read all members from the Sorted Set in descending
    # request_count order
    return {
        "URL request counts": [
            {"url": url.decode("utf-8"), "request_count": request_count}
            for url, request_count in redis_cache.zrevrangebyscore(
                REDIS_SORTED_SET, "inf", "-inf", withscores=True, score_cast_func=int
            )
        ]
    }


def _create_random_string_list(amount: int, str_length: int) -> List[str]:
    """
    Return a list of random lowercase ASCII strings.

    Depending on the real-world problem, I would define default values for the
    `amount` and `str_length` parameters.
    For this exercise I decided to set these values explicit in the
    `start_test_run` function

    :param amount: number of randomly generated strings in the return list
    :param str_length: length of one randomly generated string
    """
    return [
        "".join(random.sample(string.ascii_lowercase, str_length))
        for _ in range(amount)
    ]


def _create_random_url_path(
    string_list: Sequence[str], min_path_segments: int, max_path_segments: int
) -> str:
    """
    Return a randomly generated URL path.

    Depending on the real-world problem, I would define default values for the
    `min_path_segments` and `max_path_segments` parameters.
    For this exercise I decided to set these values explicit in the
    `start_test_run` function

    :param string_list: List of strings with which we generate the URL path
    :param min_path_segments: minimum number of path segments
    :param max_path_segments: maximum numbe of path segments
    """
    number_of_path_segments: int = random.randint(min_path_segments, max_path_segments)
    return "/".join(random.choice(string_list) for i in range(number_of_path_segments))


@app.route("/test/<int:number_of_requests>/", methods=["POST"])
def start_test_run(number_of_requests: int):
    """
    Starts a test run of with the given number of requests.

    The test run will perform GET requests to the /api endpoint.
    Each test request will add a randomly generated URL path.

    :param number_of_requests: number of requests for a single test run
    """
    string_list = _create_random_string_list(amount=3, str_length=3)

    with requests.Session() as session:
        for url_path in (
            _create_random_url_path(
                string_list, min_path_segments=1, max_path_segments=6
            )
            for _ in range(number_of_requests)
        ):
            # generate URL to the simulation endpoint and remove the leading "/"
            simulated_url_path = url_for("simulated_api_endpoints", url_path=url_path)
            simulated_url_path = simulated_url_path.lstrip("/")

            session.get(f"{request.root_url}{simulated_url_path}")

    # not sure what to return, so just return a simple message as response body
    return f"Finished test run with {number_of_requests} requests"
