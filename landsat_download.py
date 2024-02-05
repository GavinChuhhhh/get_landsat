import argparse
import logging
from typing import List, Tuple
from pystac_client import Client
import planetary_computer as pc
import os
import requests
import subprocess

import time

current_timestamp = time.strftime("%Y%m%d-%H%M%S")
log_file_name = f'./log/download_{current_timestamp}.log'

logging.basicConfig(filename=log_file_name, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_href(items, asset_list=None) -> List:
    if asset_list is None:
        asset_list = [
            "red",
            "blue",
            "green",
            "nir08",
            "swir16",
            "swir22",
            "coastal",
            "qa_pixel",
            "mtl.json",
            "mtl.xml"
        ]

    hrefs = []

    for id, assets in items.items():
        for name, asset in assets.items():
            if name in asset_list:
                hrefs.append(asset.href)

    return hrefs


def download(url: str, output: str = "./", ) -> None:
    file_path = extract_path_from_url(url)
    dir_path = "/".join(file_path.split("/")[:-1])
    file_name = file_path.split("/")[-1]

    logging.info(f"Start downloading: {file_name}")
    print(f"Start downloading: {file_name}")

    # Extract path and build local path
    local_path = os.path.join(output, dir_path)

    # If the path doesn't exist, create it
    if not os.path.exists(local_path):
        os.makedirs(local_path)

    file_path = os.path.join(local_path, file_name)

    # wget参数：-c 继续下载 -O 指定下载到本地的文件地址 -q 静默下载
    command = f'wget -c "{url}" -O {file_path} -q'
    subprocess.run(command, shell=True)
    logging.info(f"Download completed: {file_name}")
    print(f"Download completed: {file_name}")


    # Download the file
    # response = requests.get(url)
    # if not os.path.exists(os.path.join(local_path, file_name)):
    #     with open(os.path.join(local_path, file_name), 'wb') as f:
    #         f.write(response.content)
    #         logging.info(f"Download completed: {file_name}")
    #         print(f"Download completed: {file_name}")
    # else:
    #     # If the file exists, check if its size matches the remote file size
    #     remote_file_size = int(response.headers.get('content-length', 0))
    #     local_file_size = os.path.getsize(os.path.join(local_path, file_name))
    #     if local_file_size != remote_file_size:
    #         response = requests.get(url)
    #         with open(os.path.join(local_path, file_name), 'wb') as f:
    #             f.write(response.content)
    #             logging.info(f"Download completed: {file_name}")
    #             print(f"Download completed: {file_name}")
    #     else:
    #         logging.info(f"File already exists and has the same size: {file_name}")
    #         print(f"File already exists and has the same size: {file_name}")

def wrs_parse(wrs: str) -> Tuple:
    # Slice the string and convert to integers
    wrs_path = int(wrs[:3])
    wrs_row = int(wrs[3:])

    return wrs_path, wrs_row


def search_items(wrs: str, start_date: str = "2023-11-01", end_date: str = "2023-12-30", cloud_cover: int = 30) -> dict:
    # Search against the Planetary Computer STAC API
    client = Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1"
    )
    wrs_path, wrs_row = wrs_parse(wrs)
    state = "ks"

    # Define your search with CQL2 syntax
    search = client.search(filter_lang="cql2-json", filter={
        "op": "and",
        "args": [
            # {"op": "=", "args": [{"property": "collection"}, "landsat-c2-l2"]},
            {"op": "=", "args": [{"property": "collection"}, "naip"]},
            # {"op": "<=", "args": [{"property": "eo:cloud_cover"}, cloud_cover]},
            {"op": "=", "args": [{"property": "naip:state"}, state]},
            # {"op": "=", "args": [{"property": "landsat:wrs_row"}, wrs_row]},
            {"op": ">=", "args": [{"property": "datetime"}, f"{start_date}T00:00:00Z"]},
            {"op": "<", "args": [{"property": "datetime"}, f"{end_date}T00:00:00Z"]},
            # {"op": "or", "args": [
            #     {"op": "=", "args": [{"property": "platform"}, "landsat-7"]},
            #     {"op": "=", "args": [{"property": "platform"}, "landsat-5"]},
            #     {"op": "=", "args": [{"property": "platform"}, "landsat-8"]},
            #     {"op": "=", "args": [{"property": "platform"}, "landsat-9"]}
            # ]}
        ]
    })

    # Grab the first item from the search results and sign the assets
    items = search.items()

    search_result = {}

    for i in items:
        # item = pc.sign(i)
        # 加的token的过期时间应该是24h，如需调整，参考 https://planetarycomputer.microsoft.com/docs/concepts/sas/
        assets = i.assets
        search_result[i.id] = assets

    logging.info(f"Retrieved: {len(search_result)} items")
    print(f"Retrieved: {len(search_result)} items")

    return search_result


def extract_path_from_url(url: str) -> str:
    start_index = url.find("standard/")
    if start_index != -1:
        path = url[start_index + len("standard/"):]
        # Remove query parameters from the link
        if '?' in path:
            path = path.split('?')[0]
        return path


def main():
    parser = argparse.ArgumentParser(description='Parameters for downloading Landsat data ')
    parser.add_argument('-o', '--output',default="./", type=str, help='Download directory, default:"./"')
    parser.add_argument('--wrs', required=True, type=str, help='WRS tile code, 6 int such as 120036')
    parser.add_argument('--start_date', required=True, type=str, help='Start date string, yyyy-mm-dd')
    parser.add_argument('--end_date', type=str, required=True, help='End date string, yyyy-mm-dd')
    parser.add_argument('--cloud_cover', type=int, default=30, help='Cloud cover integer, default 30')
    parser.add_argument('--assets', nargs='*', help='Asset strings')

    args = parser.parse_args()

    logging.info('Start')

    output_dir = args.output
    start_date = args.start_date
    end_date = args.end_date
    asset_list = args.assets
    wrs = args.wrs
    cloud_cover = args.cloud_cover

    items = search_items(start_date=start_date, end_date=end_date, cloud_cover=cloud_cover, wrs=wrs)

    hrefs = get_href(items, asset_list)

    for href in hrefs:
        download(output=output_dir, url=href)

    logging.info('End')


if __name__ == "__main__":
    main()
