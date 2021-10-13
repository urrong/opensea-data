import time
import grequests
import requests
import diskcache as dc
from pprint import pprint


API_KEY = ""


# def make_order_request(start_from=None):
#     headers = {"Accept": "application/json",
#                # "X-API-KEY": API_KEY
#                }
#     querystring = {"bundled": "false",
#                    "include_bundled": "false",
#                    "include_invalid": "false",
#                    "limit": "50",
#                    "offset": "0",
#                    "order_by": "created_date",
#                    "order_direction": "asc"}
#     if start_from is not None:
#         querystring["listed_after"] = start_from
#
#     request = grequests.get("https://api.opensea.io/wyvern/v1/orders", headers=headers, params=querystring)
#
#     return request
#
#
# def extract_response_orders(response: requests.Response):
#     orders = None
#     if response.status_code == 200:
#         orders_json = response.json()
#         if "count" in orders_json:
#             assert orders_json['count'] == 1, f"count: {orders_json['count']}"
#             orders = orders_json["orders"]
#     else:
#         print("status code:", response.status_code, "reason:", response.reason)
#     return orders


def make_event_request(start_from=None, offset=0, limit=300):
    headers = {"Accept": "application/json",
               # "X-API-KEY": API_KEY
               }
    querystring = {"only_opensea": "false",
                   "offset": str(offset),
                   "limit": str(limit),
                   "event_type": "successful"}

    if start_from is not None:
        querystring["occurred_before"] = start_from

    request = grequests.get("https://api.opensea.io/api/v1/events", headers=headers, params=querystring)
    return request


def extract_response_events(response: requests.Response):
    events = None
    if response.status_code == 200:
        events_json = response.json()
        if "asset_events" in events_json:
            events = events_json["asset_events"]
    else:
        raise Exception("status code:", response.status_code, "reason:", response.reason, "url:", response.url)
    return events


def get_events(start_from=None, limit=300, num_parallel=1):
    print("getting events before date:", start_from)
    requests_list = []
    for i in range(num_parallel):
        request = make_event_request(start_from, i * limit, limit)
        requests_list.append(request)
    tic = time.time()
    results = grequests.map(requests_list)
    toc = time.time()
    events_all = []
    for result in results:
        events = extract_response_events(result)
        if events is not None:
            events_all.extend(events)
    events_all.sort(key=lambda x: x["id"], reverse=True)
    print("got events to:             ", events_all[-1]["created_date"])
    print(f"request time: {(toc - tic) * 1000:.2f} ms")
    return events_all


if __name__ == '__main__':
    def main():
        persistent_cache = dc.Index("../db")

        if len(persistent_cache) > 0:
            last_item = persistent_cache.peekitem(True)
            start_from = last_item[1]["created_date"]
        else:
            start_from = None

        tic = time.time()
        while True:
            events = get_events(start_from, 300, 15)

            start_from = events[-1]["created_date"]
            num_collisions = 0
            for event in events:
                if event["id"] in persistent_cache:
                    num_collisions += 1
                else:
                    persistent_cache[event["id"]] = event
            if num_collisions == 0:
                raise Exception("no collisions happened")
            print("added:", len(events), "- num collisions:", num_collisions,
                  f"- elapsed time: {(time.time() - tic):.2f} s")
            print()
    main()
