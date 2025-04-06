
ensyurin_update: ## 演習林のデータ更新
	cd batch && \
	tippecanoe -o ../data/entry/pmtiles/vector/ensyurin.pmtiles \
	$$(find data/ensyurin -name '*.geojson') --force

360_update: ## データの更新
	cd batch && \
	uv run scripts/node.py && \
	tippecanoe -o ../data/streetView/THETA360.pmtiles data/THETA360.geojson data/THETA360_line.geojson -ai --force

search_data_update: ## 検索データの更新
	cd batch && \
	uv run scripts/create_search_data.py && \
	tippecanoe -o ../data/entry/pmtiles/vector/fac_search.pmtiles data/search/fac_building_point.geojson data/search/fac_poi.geojson data/search/fac_ziriki_point.geojson --force




