# DWG fixtures

`kitchen-equipment.dwg` is `fixtures/dwg/kitchen-equipment.dwg` of https://github.com/getcadcraft/bimcraft at commit
`e36a94db95aa472c19ea1580864ea7622056d00e`, copied unchanged, under that repository's Apache License 2.0 (Copyright 2026
The Data Design Group, Inc.; the licence is `vendor/cc-dwg/LICENSE`). Its own notes call it example data and a test
fixture. AutoCAD 2018 format (AC1032): 254 model-space entities, 229 of them block inserts, with hatches, linear and
radius dimensions, a spline, an ellipse, text and multiline text, an image and a multileader.

SHA-256 `091840a55018d97cb92c5534f8b46b91cd53f2441f1a43ded42daa0c47f904f1` is checked by
`tests/e2e/bim_phase252_dwg_check.mjs`, which opens it through the app's Import file picker and saves the plan back as
DWG.
