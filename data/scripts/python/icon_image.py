from PIL import Image
from pathlib import Path


def crop_to_square_and_resize(input_path, output_path, target_size=60):
    """
    画像を正方形にクリップし、指定サイズにリサイズする

    Args:
        input_path (str): 入力画像のパス
        output_path (str): 出力画像のパス
        target_size (int): 最終的な画像サイズ（正方形）
    """
    try:
        # 画像を開く
        with Image.open(input_path) as img:
            # RGBAモードに変換（透明度を保持）
            if img.mode != "RGBA":
                img = img.convert("RGBA")

            width, height = img.size

            # 短い辺を基準にして正方形の領域を計算
            min_dimension = min(width, height)

            # センタークロップの座標を計算
            left = (width - min_dimension) // 2
            top = (height - min_dimension) // 2
            right = left + min_dimension
            bottom = top + min_dimension

            # 正方形にクリップ
            cropped_img = img.crop((left, top, right, bottom))

            # 指定サイズにリサイズ（高品質リサンプリング使用）
            resized_img = cropped_img.resize(
                (target_size, target_size), Image.Resampling.LANCZOS
            )

            # WebP形式で保存
            resized_img.save(output_path, "WEBP", quality=90)

        return True

    except Exception as e:
        print(f"エラー処理中: {input_path} - {str(e)}")
        return False


def collect_webp_files(input_dir):
    input_dir = Path(input_dir)

    webp_files = []

    for input_path in sorted(input_dir.glob("*.webp")):
        webp_files.append((input_path, input_path.name))

    for input_path in sorted(input_dir.glob("*/01.webp")):
        webp_files.append((input_path, f"{input_path.parent.name}.webp"))

    return webp_files


def process_directory(input_dir, output_dir=None, target_size=60):
    """
    指定ディレクトリ内の全WebP画像を処理する

    Args:
        input_dir (str): 入力ディレクトリのパス
        output_dir (str): 出力ディレクトリのパス（Noneの場合は input_dir + '_processed'）
        target_size (int): 最終的な画像サイズ
    """
    # 出力ディレクトリが指定されていない場合のデフォルト設定
    input_dir = Path(input_dir)

    if output_dir is None:
        output_dir = input_dir.parent / f"{input_dir.name}_processed"
    else:
        output_dir = Path(output_dir)

    # 出力ディレクトリを作成
    output_dir.mkdir(parents=True, exist_ok=True)

    # WebP画像ファイルを検索
    webp_files = collect_webp_files(input_dir)

    if not webp_files:
        print(f"WebP画像が見つかりません: {input_dir}")
        return

    print(f"処理開始: {len(webp_files)}個のWebP画像を処理します")

    success_count = 0

    for input_path, output_filename in webp_files:
        output_path = output_dir / output_filename

        print(f"処理中: {input_path.relative_to(input_dir)}")

        if crop_to_square_and_resize(input_path, output_path, target_size):
            success_count += 1
            print(f"  ✓ 完了: {output_filename}")
        else:
            print(f"  ✗ 失敗: {input_path}")

    print(f"\n処理完了: {success_count}/{len(webp_files)}個の画像を正常に処理しました")
    print(f"出力ディレクトリ: {output_dir}")


SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR.parents[2] / "assets"
# 使用例
if __name__ == "__main__":
    # 設定
    INPUT_DIRECTORY = (
        SCRIPT_DIR.parents[1] / "assets" / "images" / "feature"
    )  # ここに実際のディレクトリパスを指定
    OUTPUT_DIRECTORY = (
        SCRIPT_DIR.parents[1] / "assets" / "images" / "icons"
    )  # 出力先（オプション）
    TARGET_SIZE = 60  # 最終的な画像サイズ

    # ディレクトリ内の全WebP画像を処理
    process_directory(
        input_dir=INPUT_DIRECTORY,
        output_dir=OUTPUT_DIRECTORY,  # Noneにすると自動で出力ディレクトリを生成
        target_size=TARGET_SIZE,
    )

    # 単体ファイルを処理する場合の例
    # crop_to_square_and_resize("input.webp", "output.webp", 60)
