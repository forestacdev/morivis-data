#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
兵庫県森林資源量メッシュGPKGファイル一括ダウンローダー
https://www.geospatial.jp/ckan/dataset/fr_mesh20m_hyogo からgpkgファイルをダウンロード
"""

import sys
import argparse
import requests
import re
from pathlib import Path
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from bs4 import BeautifulSoup


class HyogoGpkgDownloader:
    def __init__(self, output_dir="gpkg_files", max_workers=5, delay=1.0):
        self.base_url = "https://www.geospatial.jp"
        self.dataset_url = "https://www.geospatial.jp/ckan/dataset/fr_mesh20m_hyogo"
        self.output_dir = Path(output_dir)
        self.max_workers = max_workers
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    def get_gpkg_links(self):
        """ページからgpkgファイルのリンクを取得"""
        print("ページを取得しています...")
        response = self.session.get(self.dataset_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # gpkgZIPファイルへのリンクを検索
        gpkg_links = []

        # テキストベースで検索
        gpkg_pattern = re.compile(r"fr_mesh20m_\w+\.gpkgZIP")
        resource_pattern = re.compile(
            r"/ckan/dataset/fr_mesh20m_hyogo/resource/[a-f0-9-]+"
        )

        for link in soup.find_all("a", href=True):
            href = link["href"]
            text = link.get_text(strip=True)

            # gpkgZIPファイルのリンクを検索
            if gpkg_pattern.search(text) and resource_pattern.search(href):
                filename = gpkg_pattern.search(text).group()
                full_url = urljoin(self.base_url, href)
                gpkg_links.append(
                    {"filename": filename, "resource_url": full_url, "text": text}
                )

        print(f"見つかったgpkgファイル: {len(gpkg_links)}個")
        return gpkg_links

    def get_download_url(self, resource_url):
        """リソースページから実際のダウンロードURLを取得"""
        try:
            response = self.session.get(resource_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # ダウンロードリンクを検索
            download_link = soup.find(
                "a", {"class": "btn btn-primary resource-url-analytics"}
            )
            if download_link and download_link.get("href"):
                download_url = download_link["href"]
                if not download_url.startswith("http"):
                    download_url = urljoin(self.base_url, download_url)
                return download_url

            # 別の方法でダウンロードリンクを検索
            for link in soup.find_all("a", href=True):
                if "download" in link["href"].lower() or ".zip" in link["href"].lower():
                    download_url = link["href"]
                    if not download_url.startswith("http"):
                        download_url = urljoin(self.base_url, download_url)
                    return download_url

            return None

        except Exception as e:
            print(f"ダウンロードURL取得エラー: {resource_url} - {e}")
            return None

    def download_file(self, file_info):
        """単一ファイルをダウンロード"""
        filename = file_info["filename"]
        resource_url = file_info["resource_url"]

        try:
            # 出力ファイルパス
            file_path = self.output_dir / filename

            # 既に存在する場合はスキップ
            if file_path.exists():
                return f"スキップ: {filename} (既に存在)"

            # ダウンロードURLを取得
            print(f"ダウンロードURL取得中: {filename}")
            download_url = self.get_download_url(resource_url)

            if not download_url:
                return f"エラー: {filename} - ダウンロードURLが見つかりません"

            # ファイルをダウンロード
            print(f"ダウンロード開始: {filename}")
            response = self.session.get(download_url, stream=True)
            response.raise_for_status()

            # ディレクトリを作成
            self.output_dir.mkdir(parents=True, exist_ok=True)

            # ファイルに保存
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            file_size = file_path.stat().st_size / (1024 * 1024)  # MB

            # 遅延
            time.sleep(self.delay)

            return f"完了: {filename} ({file_size:.1f}MB)"

        except Exception as e:
            return f"エラー: {filename} - {str(e)}"

    def download_all(self):
        """全てのgpkgファイルをダウンロード"""
        # リンクを取得
        gpkg_links = self.get_gpkg_links()

        if not gpkg_links:
            print("gpkgファイルが見つかりませんでした")
            return

        print(f"\n{len(gpkg_links)}個のファイルをダウンロード開始")
        print(f"出力ディレクトリ: {self.output_dir}")
        print(f"並行数: {self.max_workers}, 遅延: {self.delay}秒")

        # ファイルリストを表示
        print("\nダウンロード予定ファイル:")
        for i, link in enumerate(gpkg_links, 1):
            print(f"{i:2d}. {link['filename']}")

        print("\nダウンロード開始...")

        # 並行ダウンロード
        downloaded = 0
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.download_file, link): link for link in gpkg_links
            }

            for future in as_completed(futures):
                result = future.result()
                downloaded += 1
                print(f"[{downloaded}/{len(gpkg_links)}] {result}")

        print(f"\nダウンロード完了: {downloaded}個のファイル")


def main():
    parser = argparse.ArgumentParser(
        description="兵庫県森林資源量メッシュGPKGファイル一括ダウンローダー"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="hyogo_gpkg",
        help="出力ディレクトリ (デフォルト: hyogo_gpkg)",
    )
    parser.add_argument(
        "--workers", type=int, default=3, help="並行ダウンロード数 (デフォルト: 3)"
    )
    parser.add_argument(
        "--delay", type=float, default=2.0, help="リクエスト間隔(秒) (デフォルト: 2.0)"
    )
    parser.add_argument(
        "--list-only",
        action="store_true",
        help="ファイルリストのみ表示（ダウンロードしない）",
    )

    args = parser.parse_args()

    # ダウンローダーを初期化
    downloader = HyogoGpkgDownloader(
        output_dir=args.output, max_workers=args.workers, delay=args.delay
    )

    try:
        if args.list_only:
            # ファイルリストのみ表示
            gpkg_links = downloader.get_gpkg_links()
            print(f"\n見つかったgpkgファイル ({len(gpkg_links)}個):")
            for i, link in enumerate(gpkg_links, 1):
                print(f"{i:2d}. {link['filename']}")
        else:
            # ダウンロード実行
            downloader.download_all()

    except KeyboardInterrupt:
        print("\n中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
