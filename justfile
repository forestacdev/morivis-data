docker:
    @docker compose up -d

# データのホスティング
dev:
    @echo "Checking if port 9000 is in use..."
    @lsof -ti:9000 && echo "Port 9000 is in use, killing process..." && npx kill-port 9000 || echo "Port 9000 is free"
    pnpm install
    pnpm run dev


# 座標変換
proj:
    cd data/scripts/python && \
    uv sync && \
    source .venv/bin/activate && \
    uv run proj.py && \
    deactivate

# iconからspriteを作成
sprite_bundle:
    cd data/scripts/node && pnpm run sprite:bundle

# uv環境を有効化
uv_activate:
    cd data/scripts/python && \
    uv sync && \
    source .venv/bin/activate

# uv環境を無効化
uv_deactivate:
    cd data/scripts/python && deactivate

# POI、検索データの更新 feature_idを追加
poi_update:
    cd data/scripts/python && \
    rm -f data/search/fac_poi_with_id.geojson && \
    ogr2ogr -f GeoJSON -overwrite data/search/fac_poi_with_id.geojson data/search/fac_poi.geojson -lco id_field=id -nln fac_poi && \
    uv run create_poi_search_data.py && \
    uv run icon_image.py && \
    mkdir -p ../../assets/entries/pmtiles/vector && \
    tippecanoe -o ../../assets/entries/pmtiles/vector/fac_search.pmtiles data/search/fac_poi_with_id.geojson --force -l fac_poi && \
    rm -f data/search/fac_poi_with_id.geojson

# 360度パノラマのデータ更新
update_360:
    cd data/scripts/python && \
    uv run node.py && \
    tippecanoe -o ../../assets/street_view/panorama.pmtiles -L panorama_nodes:../../assets/street_view/nodes.fgb -L panorama_links:../../assets/street_view/links.fgb -ai --force

api:
    pnpm run api

python-lint: ## Pythonコードのlint自動修正・フォーマット
	cd data/scripts/python && uv run --group dev ruff check --fix . --exclude .venv && uv run --group dev ruff format . --exclude .venv
