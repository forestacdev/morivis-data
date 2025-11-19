serve: ## データのホスティング
	@echo "Checking port 9000..."
	@if sudo lsof -i :9000 >/dev/null 2>&1; then \
		echo "Port 9000 is in use. Cleaning..."; \
		sudo lsof -i :9000 | awk 'NR>1 {print $$2}' | xargs -r sudo kill -9; \
		sleep 1; \
		echo "Port 9000 cleaned"; \
	else \
		echo "Port 9000 is free"; \
	fi
	@echo "Starting server..."
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
	$$(find data/ensyurin -name '*.fgb') --force -z17 -pf -pk -P

poi_update: ## POI、検索データの更新 feature_idを追加
	cd batch && \
	ogr2ogr -f GeoJSON -overwrite data/search/fac_poi_with_id.geojson data/search/fac_poi.geojson -lco id_field=id -nln fac_poi && \
	uv run scripts/create_poi_search_data.py && \
	uv run scripts/icon_image.py && \
	tippecanoe -o ../data/entries/pmtiles/vector/fac_search.pmtiles data/search/fac_poi_with_id.geojson --force -l fac_poi && \
	rm data/search/fac_poi_with_id.geojson

360_update: ## 360度パノラマのデータ更新
	cd batch && \
	uv run scripts/node.py && \
	tippecanoe -o ../data/street_view/panorama.pmtiles -L panorama_nodes:../data/street_view/nodes.fgb -L panorama_links:../data/street_view/links.fgb -ai --force






