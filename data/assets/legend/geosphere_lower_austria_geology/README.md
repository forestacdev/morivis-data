# ニーダーエスターライヒ州地質図 1:200,000の凡例記号

- 提供元: GeoSphere Austria
- 取得元: https://gis.geosphere.at/maps/rest/services/geologie/nied_200/MapServer/legend?f=pjson
- 記号数: 414
- 形式: lossless WebP

公式 ArcGIS REST の凡例APIが返す項目別PNGを、画素を保持したままWebPへ変換したもの。PLANAR_NIED の402項目と TEKT_NIED の12項目を保持している。

source.json に出典、原語ラベル、ファイル名の対応を保存している。morivis側の凡例定義は frontend/src/routes/map/data/entries/raster/image_tile/categorical/_legends/geosphere_lower_austria_geology.ts 。記号の内容は描き直していない。

