import plistlib
import struct
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'scripts'))
from app_manifests import ManifestError,parse_plist,parse_axml,parse_android_manifest
from workbench import analyze

def axml_fixture():
    strings=['manifest','package','com.example.app','uses-permission','name',
             'android.permission.INTERNET','http://schemas.android.com/apk/res/android','activity','exported','true']
    payload=bytearray();offsets=[]
    for value in strings:
        text=value.encode('utf-8');offsets.append(len(payload))
        payload.extend(bytes([len(value),len(text)])+text+b'\0')
    poolsize=28+4*len(strings)+len(payload)
    pool=struct.pack('<HHIIIII',1,28,poolsize,len(strings),0,0x100,28+4*len(strings))+struct.pack('<I',0)
    pool+=struct.pack('<'+'I'*len(strings),*offsets)+payload
    def attr(ns,key,raw_index):
        return struct.pack('<IIIHBBI',ns,key,raw_index,8,0,3,raw_index)
    def tag(name_index,attrs):
        attrdata=b''.join(attrs)
        size=36+len(attrdata)
        chunk=struct.pack('<HHI',0x0102,36,size)
        chunk+=struct.pack('<II',0,0xffffffff)
        chunk+=struct.pack('<IIHHHHHH',0xffffffff,name_index,20,20,len(attrs),0,0,0)
        return chunk+attrdata
    manifest=tag(0,[attr(0xffffffff,1,2)])
    permission=tag(3,[attr(6,4,5)])
    root=pool+manifest+permission
    return struct.pack('<HHI',3,8,8+len(root))+root

class AppManifestTests(unittest.TestCase):
    def test_text_manifest(self):
        xml=b'<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.example">'\
            b'<uses-permission android:name="android.permission.INTERNET" />'\
            b'<application><activity android:name=".Main" android:exported="true" /></application></manifest>'
        got=parse_android_manifest(xml)
        self.assertEqual(got['package'],'com.example')
        self.assertEqual(got['components'][0]['kind'],'activity')
        self.assertEqual(got['permissions'][0]['name'],'android.permission.INTERNET')
    def test_binary_axml(self):
        got=parse_axml(axml_fixture())
        self.assertEqual(got['package'],'com.example.app')
        self.assertEqual(got['permissions'][0]['name'],'android.permission.INTERNET')
    def test_binary_axml_truncation(self):
        with self.assertRaises(ManifestError):parse_axml(axml_fixture()[:-1])
    def test_disallow_dtd(self):
        with self.assertRaises(ManifestError):parse_android_manifest(b'<!DOCTYPE manifest><manifest/>')
    def test_plist_readable_binary_and_xml(self):
        source={'CFBundleIdentifier':'app.sample','CFBundleName':'Sample',
                'CFBundleURLTypes':[{'CFBundleURLSchemes':['sample-app']}],
                'SensitivePassword':'SENSITIVE_DO_NOT_EXPORT'}
        for fmt in (plistlib.FMT_BINARY,plistlib.FMT_XML):
            got=parse_plist(plistlib.dumps(source,fmt=fmt))
            self.assertEqual(got['declared_properties']['CFBundleIdentifier'],'app.sample')
            self.assertNotIn('SENSITIVE_DO_NOT_EXPORT',str(got))
            self.assertEqual(got['url_schemes'],['sample-app'])
    def test_mixed_ipa_apk(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'apps.zip'
            with zipfile.ZipFile(p,'w') as z:
                z.writestr('Payload/Demo.app/Info.plist',plistlib.dumps({'CFBundleIdentifier':'com.sample'}))
                z.writestr('AndroidManifest.xml',axml_fixture())
            got=analyze(p)
            self.assertEqual(got['analyzed'],2,got['errors'])
            self.assertEqual(got['formats']['android-axml'],1)
            self.assertEqual(got['formats']['apple-info-plist'],1)

if __name__=='__main__':unittest.main()
