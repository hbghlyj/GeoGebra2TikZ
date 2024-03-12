https://tex.cjhb.site
# Use the script in three steps
1. Upload `.ggb` file via `import from GeoGebra` button
2. The script will output the LaTeX code in the editor
3. Compile via `TexLive.net` button
# Known Bug
labelOffset not correctly handled. I need to look at https://github.com/geogebra/geogebra/blob/06ea32f2c67488596efc4fddde1913e57e0f9731/common/src/main/java/org/geogebra/common/export/pstricks/GeoGebraToPgf.java#L1680
