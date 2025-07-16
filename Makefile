serve: ## データのホスティング
	pnpm run serve

init:
	cd batch && \
	pnpm run init

uv_activate: ## uv環境を有効化
	cd batch && \
	uv sync && \
	source .venv/bin/activate

uv_deactivate: ## uv環境を無効化
	cd batch && \
	deactivate

ensyurin_update: ## 演習林のデータ更新
	cd batch && \
	tippecanoe -o ../data/entries/pmtiles/vector/ensyurin.pmtiles \
	$$(find data/ensyurin -name '*.geojson') --force -z17

poi_update: ## POI、検索データの更新 feature_idを追加
	cd batch && \
	ogr2ogr -f GeoJSON -overwrite data/search/fac_poi_with_id.geojson data/search/fac_poi.geojson -lco id_field=id -nln fac_poi && \
	uv run scripts/create_poi_search_data.py && \
	tippecanoe -o ../data/entries/pmtiles/vector/fac_search.pmtiles data/search/fac_poi_with_id.geojson --force -l fac_poi && \
	rm data/search/fac_poi_with_id.geojson

360_update: ## 360度パノラマのデータ更新
	cd batch && \
	uv run scripts/node.py && \
	tippecanoe -o ../data/street-view/THETA360.pmtiles data/THETA360.geojson data/THETA360_line.geojson -ai --force

# search_update: ## 検索データの更新
# 	cd batch && \
# 	uv run scripts/create_search_data.py && \
# 	tippecanoe -o ../data/entries/pmtiles/vector/fac_search.pmtiles data/search/fac_building_point.geojson data/search/fac_poi.geojson data/search/fac_ziriki_point.geojson --force




