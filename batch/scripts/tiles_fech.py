#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
タイル画像ダウンローダー
指定されたURLテンプレートと座標範囲でタイル画像をダウンロードします
"""

import sys
import argparse
import requests
import time
import math
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed


class TileDownloader:
    def __init__(self, base_url, output_dir="tiles", max_workers=10, delay=0.1):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.max_workers = max_workers
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

    def deg2num(self, lat_deg, lon_deg, zoom):
        """緯度経度からタイル座標を計算"""
        lat_rad = math.radians(lat_deg)
        n = 2.0**zoom
        x = int((lon_deg + 180.0) / 360.0 * n)
        y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return (x, y)

    def num2deg(self, x, y, zoom):
        """タイル座標から緯度経度を計算"""
        n = 2.0**zoom
        lon_deg = x / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
        lat_deg = math.degrees(lat_rad)
        return (lat_deg, lon_deg)

    def create_directory_structure(self, zoom, x, y):
        """ディレクトリ構造を作成"""
        tile_dir = self.output_dir / str(zoom) / str(x)
        tile_dir.mkdir(parents=True, exist_ok=True)
        return tile_dir / f"{y}.png"

    def download_tile(self, zoom, x, y):
        """単一のタイル画像をダウンロード"""
        try:
            # URLを構築
            url = self.base_url.format(z=zoom, x=x, y=y)

            # ファイルパスを作成
            file_path = self.create_directory_structure(zoom, x, y)

            # 既に存在する場合はスキップ
            if file_path.exists():
                return f"スキップ: {file_path}"

            # ダウンロード実行
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # ファイルに保存
            with open(file_path, "wb") as f:
                f.write(response.content)

            # 遅延
            time.sleep(self.delay)

            return f"完了: {file_path}"

        except Exception as e:
            return f"エラー: zoom={zoom}, x={x}, y={y} - {str(e)}"

    def download_by_zoom_range(
        self, min_zoom, max_zoom, north=85, south=-85, east=180, west=-180
    ):
        """ズームレベル範囲でダウンロード"""
        total_tiles = 0

        # 各ズームレベルでのタイル範囲を計算
        for zoom in range(min_zoom, max_zoom + 1):
            # 座標範囲を計算
            min_x, max_y = self.deg2num(north, west, zoom)
            max_x, min_y = self.deg2num(south, east, zoom)

            # 範囲を調整
            min_x = max(0, min_x)
            max_x = min(2**zoom - 1, max_x)
            min_y = max(0, min_y)
            max_y = min(2**zoom - 1, max_y)

            tiles_count = (max_x - min_x + 1) * (max_y - min_y + 1)
            total_tiles += tiles_count

            print(
                f"ズーム {zoom}: X={min_x}-{max_x}, Y={min_y}-{max_y} ({tiles_count} タイル)"
            )

        print(f"\n総ダウンロード予定タイル数: {total_tiles}")

        # ダウンロード実行
        downloaded = 0
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []

            for zoom in range(min_zoom, max_zoom + 1):
                min_x, max_y = self.deg2num(north, west, zoom)
                max_x, min_y = self.deg2num(south, east, zoom)

                min_x = max(0, min_x)
                max_x = min(2**zoom - 1, max_x)
                min_y = max(0, min_y)
                max_y = min(2**zoom - 1, max_y)

                for x in range(min_x, max_x + 1):
                    for y in range(min_y, max_y + 1):
                        future = executor.submit(self.download_tile, zoom, x, y)
                        futures.append(future)

            # 結果を処理
            for future in as_completed(futures):
                result = future.result()
                downloaded += 1
                if downloaded % 100 == 0:
                    print(
                        f"進捗: {downloaded}/{total_tiles} ({downloaded / total_tiles * 100:.1f}%)"
                    )

        print(f"\nダウンロード完了: {downloaded} タイル")

    def download_by_coordinates(self, min_zoom, max_zoom, min_x, max_x, min_y, max_y):
        """座標範囲でダウンロード"""
        total_tiles = 0

        for zoom in range(min_zoom, max_zoom + 1):
            # ズームレベルに応じて座標をスケール
            scale = 2 ** (zoom - min_zoom)
            scaled_min_x = min_x * scale
            scaled_max_x = max_x * scale
            scaled_min_y = min_y * scale
            scaled_max_y = max_y * scale

            tiles_count = (scaled_max_x - scaled_min_x + 1) * (
                scaled_max_y - scaled_min_y + 1
            )
            total_tiles += tiles_count

            print(
                f"ズーム {zoom}: X={scaled_min_x}-{scaled_max_x}, Y={scaled_min_y}-{scaled_max_y} ({tiles_count} タイル)"
            )

        print(f"\n総ダウンロード予定タイル数: {total_tiles}")

        # ダウンロード実行
        downloaded = 0
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []

            for zoom in range(min_zoom, max_zoom + 1):
                scale = 2 ** (zoom - min_zoom)
                scaled_min_x = min_x * scale
                scaled_max_x = max_x * scale
                scaled_min_y = min_y * scale
                scaled_max_y = max_y * scale

                for x in range(scaled_min_x, scaled_max_x + 1):
                    for y in range(scaled_min_y, scaled_max_y + 1):
                        future = executor.submit(self.download_tile, zoom, x, y)
                        futures.append(future)

            for future in as_completed(futures):
                result = future.result()
                downloaded += 1
                if downloaded % 100 == 0:
                    print(
                        f"進捗: {downloaded}/{total_tiles} ({downloaded / total_tiles * 100:.1f}%)"
                    )

        print(f"\nダウンロード完了: {downloaded} タイル")


def main():
    parser = argparse.ArgumentParser(description="タイル画像ダウンローダー")
    parser.add_argument(
        "url",
        help="タイルURLテンプレート (例: https://tile.openstreetmap.org/{z}/{x}/{y}.png)",
    )
    parser.add_argument("--min-zoom", type=int, required=True, help="最小ズームレベル")
    parser.add_argument("--max-zoom", type=int, required=True, help="最大ズームレベル")
    parser.add_argument(
        "--output", "-o", default="tiles", help="出力ディレクトリ (デフォルト: tiles)"
    )
    parser.add_argument(
        "--workers", type=int, default=10, help="並行ダウンロード数 (デフォルト: 10)"
    )
    parser.add_argument(
        "--delay", type=float, default=0.1, help="リクエスト間隔(秒) (デフォルト: 0.1)"
    )

    # 範囲指定方法
    area_group = parser.add_mutually_exclusive_group(required=True)
    area_group.add_argument(
        "--bbox",
        nargs=4,
        type=float,
        metavar=("WEST", "SOUTH", "EAST", "NORTH"),
        help="境界ボックス (西経度 南緯度 東経度 北緯度)",
    )
    area_group.add_argument(
        "--tiles",
        nargs=4,
        type=int,
        metavar=("MIN_X", "MIN_Y", "MAX_X", "MAX_Y"),
        help="タイル座標範囲 (最小X 最小Y 最大X 最大Y)",
    )

    args = parser.parse_args()

    # バリデーション
    if args.min_zoom > args.max_zoom:
        print("エラー: 最小ズームレベルは最大ズームレベル以下である必要があります")
        sys.exit(1)

    if args.min_zoom < 0 or args.max_zoom > 20:
        print("警告: ズームレベルは通常0-20の範囲です")

    # ダウンローダーを初期化
    downloader = TileDownloader(
        base_url=args.url,
        output_dir=args.output,
        max_workers=args.workers,
        delay=args.delay,
    )

    print(f"タイルURL: {args.url}")
    print(f"ズーム範囲: {args.min_zoom} - {args.max_zoom}")
    print(f"出力ディレクトリ: {args.output}")
    print(f"並行数: {args.workers}, 遅延: {args.delay}秒")

    try:
        if args.bbox:
            west, south, east, north = args.bbox
            print(f"境界ボックス: 西={west}, 南={south}, 東={east}, 北={north}")
            downloader.download_by_zoom_range(
                args.min_zoom, args.max_zoom, north, south, east, west
            )
        else:
            min_x, min_y, max_x, max_y = args.tiles
            print(f"タイル座標: X={min_x}-{max_x}, Y={min_y}-{max_y}")
            downloader.download_by_coordinates(
                args.min_zoom, args.max_zoom, min_x, max_x, min_y, max_y
            )

    except KeyboardInterrupt:
        print("\n中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
