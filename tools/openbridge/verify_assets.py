#!/usr/bin/env python3
"""Offline provenance, deterministic-extraction and static SVG safety checks."""
import hashlib,json,re,sys,unittest,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; V=ROOT/'vendor/openbridge'
def sha(b):return hashlib.sha256(b).hexdigest()
def validate_svg(text):
    if '<!' in text or '${' in text:raise ValueError('declaration or template interpolation')
    root=ET.fromstring(text)
    allowed_tags={'svg','path'}
    allowed_attrs={'width','height','viewBox','fill','d','fill-rule','clip-rule','stroke','stroke-width','stroke-linecap','stroke-linejoin','opacity'}
    if root.tag!='{http://www.w3.org/2000/svg}svg' or root.get('viewBox')!='0 0 24 24':raise ValueError('SVG root or viewBox')
    for node in root.iter():
        if node.tag.split('}')[-1] not in allowed_tags:raise ValueError('unexpected element')
        for k,v in node.attrib.items():
            if k not in allowed_attrs or any(x in v.lower() for x in ['url(','javascript:','data:','http:','https:']):raise ValueError('unexpected attribute or reference')
    return True
class Assets(unittest.TestCase):
    def test_manifest_and_license(self):
        m=json.loads((V/'manifest.json').read_text());self.assertEqual(m['license'],'Apache-2.0');self.assertFalse(m['production_integrated'])
        self.assertEqual(m['license_sha256'],sha((V/'LICENSE.TXT').read_bytes()))
        self.assertEqual(m['helper_sha256'],sha((V/'icons.es5.js').read_bytes()))
    def test_all_sources_and_extractions(self):
        m=json.loads((V/'manifest.json').read_text());names=[e['name'] for e in m['icons']];self.assertEqual(len(names),len(set(names)));self.assertEqual(len(names),17)
        for e in m['icons']:
            with self.subTest(icon=e['name']):
                src=(V/'source/icons'/('icon-'+e['name']+'.ts')).read_bytes();svg=(V/'icons'/(e['name']+'.svg')).read_text()
                self.assertEqual(sha(src),e['source_sha256']);self.assertEqual(hashlib.sha1(b'blob '+str(len(src)).encode()+b'\0'+src).hexdigest(),e['source_blob_sha1'])
                self.assertEqual(re.search(r'private icon = svg`(.*?)`;',src.decode(),re.S)[1]+'\n',svg)
                self.assertEqual(sha(svg.encode()),e['svg_sha256']);self.assertTrue(validate_svg(svg))
    def test_palette_values_and_scoping(self):
        m=json.loads((V/'manifest.json').read_text())['palette'];src=(V/'source/variables.css').read_text();css=(V/'tokens.scoped.css').read_text()
        self.assertEqual(sha(src.encode()),m['source_sha256']);self.assertEqual(sha(css.encode()),m['scoped_css_sha256'])
        self.assertNotIn(':root',css);self.assertNotIn('url(',css);self.assertNotIn('@import',css)
        blocks=re.findall(r'(\.bim-ob-preview[^{}]+)\{([^}]+)\}',css);self.assertEqual(len(blocks),8)
        total=0
        for selector,body in blocks:
            theme=re.search(r'data-obc-theme="([^"]+)"',selector)
            key=':root[data-obc-theme="'+theme[1]+'"]' if theme else '.obc-component-size-'+selector.split('obc-component-size-')[1].strip()
            begin=src.index(key+' {');up=src[begin:src.index('}',begin)]
            for name,value in re.findall(r'--([\w-]+):\s*([^;]+);',body):
                total+=1;self.assertEqual(value.strip(),re.search(r'--'+re.escape(name)+r':\s*([^;]+);',up)[1].strip())
        self.assertEqual(total,124)
    def test_hostile_svg_rejected(self):
        valid=(V/'icons/home.svg').read_text()
        for bad in [valid.replace('<path','<script'),valid.replace('<path','<path onload="alert(1)"'),valid.replace('<path','<path href="https://example.com"'),'<!DOCTYPE svg>'+valid,valid.replace('currentColor','url(https://example.com)'),valid+'${evil}']:
            with self.subTest(input=bad[:60]):
                with self.assertRaises((ValueError,ET.ParseError)):validate_svg(bad)
    def test_tampered_bytes_fail_hash(self):
        m=json.loads((V/'manifest.json').read_text());e=m['icons'][0];self.assertNotEqual(sha((V/'icons'/(e['name']+'.svg')).read_bytes()+b' '),e['svg_sha256'])
if __name__=='__main__':unittest.main(verbosity=2)
