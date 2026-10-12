#!/usr/bin/env python3
"""Read-only bounded inspection of Android AXML and Apple bundle plists.

Neither target is executed, extracted or trusted as executable instructions.
AXML yields manifest declarations, not resource-resolved Android behavior.
"""
from __future__ import annotations
import argparse
import json
import plistlib
import struct
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from json_writer import write_exclusive

MAX_BYTES=8*1024*1024
MAX_CHUNKS=30000
MAX_STRINGS=120000
MAX_TAGS=5000
ANDROID_NS='http://schemas.android.com/apk/res/android'

class ManifestError(ValueError): pass


def part(data:bytes,at:int,length:int)->bytes:
    if at<0 or length<0 or at+length>len(data):
        raise ManifestError(f'out-of-range AXML structure at {at} length {length}')
    return data[at:at+length]


def u16(data:bytes,p:int)->int:
    return struct.unpack('<H',part(data,p,2))[0]


def u32(data:bytes,p:int)->int:
    return struct.unpack('<I',part(data,p,4))[0]


def v8(data:bytes,p:int,limit:int)->tuple[int,int]:
    a=part(data,p,1)[0];p+=1
    if a&0x80:
        b=part(data,p,1)[0];p+=1
        a=((a&127)<<8)|b
    return a,p


def v16(data:bytes,p:int,limit:int)->tuple[int,int]:
    a=u16(data,p);p+=2
    if a&0x8000:
        b=u16(data,p);p+=2
        a=((a&0x7fff)<<16)|b
    return a,p


def strings_in_pool(data:bytes,start:int,size:int,header:int)->list[str]:
    if header<28:raise ManifestError('invalid string pool header')
    count=u32(data,start+8);styles=u32(data,start+12)
    flags=u32(data,start+16);texts_at=u32(data,start+20)
    if count>MAX_STRINGS or styles>MAX_STRINGS or header+4*(count+styles)>size:
        raise ManifestError('string pool table exceeds limits')
    if texts_at<header+4*(count+styles) or texts_at>size:
        raise ManifestError('invalid string pool data offset')
    utf8=bool(flags&0x100);strings=[]
    for i in range(count):
        offset=u32(data,start+header+i*4)
        if offset>size-texts_at:raise ManifestError('string offset exceeds pool')
        p=start+texts_at+offset
        if utf8:
            chars,p=v8(data,p,start+size)
            bytelen,p=v8(data,p,start+size)
            if chars>65535 or bytelen>65535 or p+bytelen+1>start+size:
                raise ManifestError('invalid UTF-8 string length')
            value=part(data,p,bytelen).decode('utf-8','replace')
            if part(data,p+bytelen,1)!=b'\0':raise ManifestError('missing UTF-8 string terminator')
        else:
            chars,p=v16(data,p,start+size)
            if chars>65535 or p+chars*2+2>start+size:raise ManifestError('invalid UTF-16 string length')
            value=part(data,p,chars*2).decode('utf-16-le','replace')
            if part(data,p+chars*2,2)!=b'\0\0':raise ManifestError('missing UTF-16 terminator')
        strings.append(value[:8192])
    return strings


def decode_typed(kind:int,data:int,strs:list[str]):
    if kind==0x03:return strs[data] if data<len(strs) else f'[invalid-string:{data}]'
    if kind==0x12:return bool(data)
    if kind==0x10:return data-(1<<32) if data>=1<<31 else data
    if kind==0x11:return f'0x{data:08x}'
    if kind in (0x01,0x02,0x07,0x08):return f'@0x{data:08x}'
    return f'[typed:0x{kind:02x}:0x{data:08x}]'


def manifest_summary(elements:list[dict],format_name:str)->dict:
    manifest=next((x for x in elements if x['tag']=='manifest'),{})
    package=manifest.get('attributes',{}).get('package')
    permissions=[];components=[];features=[]
    for item in elements:
        tag=item['tag'];attrs=item['attributes']
        if tag in ('uses-permission','uses-permission-sdk-23','permission'):
            permissions.append({'tag':tag,'name':attrs.get('android:name')})
        elif tag in ('activity','activity-alias','service','receiver','provider'):
            components.append({'kind':tag,'name':attrs.get('android:name'),
                               'exported':attrs.get('android:exported'),
                               'permission':attrs.get('android:permission')})
        elif tag in ('uses-feature','uses-sdk'):
            features.append({'tag':tag,'attributes':{k:v for k,v in attrs.items() if k in
                           ('android:name','android:required','android:minSdkVersion','android:targetSdkVersion')}})
    return {'format':format_name,'package':package,
            'version_code':manifest.get('attributes',{}).get('android:versionCode'),
            'permissions':permissions[:200],'components':components[:1000],
            'features':features[:200],'parsed_tags':len(elements),
            'truncated_output':len(permissions)>200 or len(components)>1000 or len(features)>200,
            'coverage':'Manifest declarations only; exported intent-filter defaults, resource and policy resolution not implemented'}


def parse_axml(data:bytes)->dict:
    if len(data)>MAX_BYTES:raise ManifestError('Android manifest byte budget exceeded')
    if len(data)<8 or u16(data,0)!=3:raise ManifestError('not an Android binary XML')
    header=u16(data,2);total=u32(data,4)
    if header<8 or total!=len(data):raise ManifestError('invalid binary XML root bounds')
    strs=[];elements=[];p=header
    for count in range(MAX_CHUNKS):
        if p==total:break
        if p+8>total:raise ManifestError('incomplete binary XML chunk header')
        tag=u16(data,p);hdr=u16(data,p+2);size=u32(data,p+4)
        if hdr<8 or size<hdr or p+size>total:raise ManifestError('invalid binary XML chunk boundary')
        if tag==0x0001:
            strs=strings_in_pool(data,p,size,hdr)
        elif tag==0x0102:
            if not strs:raise ManifestError('start element before string pool')
            if hdr<36:raise ManifestError('invalid start element header')
            name=u32(data,p+20)
            if name>=len(strs):raise ManifestError('start element string index invalid')
            atstart=u16(data,p+24);atsize=u16(data,p+26);atcount=u16(data,p+28)
            if atsize<20 or atcount>2000 or 16+atstart+atsize*atcount>size:
                raise ManifestError('start element attributes exceed chunk')
            attrs={}
            for i in range(atcount):
                a=p+16+atstart+atsize*i
                namespace=u32(data,a);key=u32(data,a+4);raw=u32(data,a+8)
                if key>=len(strs):raise ManifestError('attribute key index invalid')
                if u16(data,a+12)<8:raise ManifestError('malformed typed value')
                dtype=part(data,a+15,1)[0];typed=u32(data,a+16)
                label=strs[key]
                if namespace!=0xffffffff:
                    if namespace>=len(strs):raise ManifestError('namespace index invalid')
                    label=('android:'+label) if strs[namespace]==ANDROID_NS else '{'+strs[namespace]+'}'+label
                attrs[label]=strs[raw] if raw!=0xffffffff and raw<len(strs) else decode_typed(dtype,typed,strs)
            elements.append({'tag':strs[name],'attributes':attrs})
            if len(elements)>MAX_TAGS:raise ManifestError('tag budget exceeded')
        p+=size
    else:
        raise ManifestError('chunk budget exceeded')
    if p!=total:raise ManifestError('unparsed Android XML data')
    return manifest_summary(elements,'android-axml')


def parse_android_manifest(data:bytes)->dict:
    if data.startswith(b'\x03\x00'):
        return parse_axml(data)
    if len(data)>MAX_BYTES:raise ManifestError('manifest byte budget exceeded')
    # ElementTree does not load external DTDs; reject DOCTYPE/entities explicitly.
    if b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper():
        raise ManifestError('XML entity declarations not supported')
    try:root=ET.fromstring(data)
    except ET.ParseError as ex:raise ManifestError('invalid text Android XML') from ex
    elements=[]
    for e in root.iter():
        name=e.tag.split('}')[-1]
        attrs={}
        for k,v in e.attrib.items():
            key=('android:'+k.split('}')[-1]) if k.startswith('{'+ANDROID_NS+'}') else k.split('}')[-1]
            attrs[key]=v[:8192]
        elements.append({'tag':name,'attributes':attrs})
        if len(elements)>MAX_TAGS:raise ManifestError('tag budget exceeded')
    return manifest_summary(elements,'android-text-xml')


def parse_plist(data:bytes)->dict:
    if len(data)>MAX_BYTES:raise ManifestError('plist byte budget exceeded')
    # Apple plistlib rejects malformed syntax, and cannot execute target code.
    try:obj=plistlib.loads(data)
    except (ValueError,TypeError,OverflowError,ET.ParseError) as exc:
        raise ManifestError('invalid Apple plist') from exc
    if not isinstance(obj,dict):raise ManifestError('Apple bundle plist must be dictionary')
    whitelist=('CFBundleIdentifier','CFBundleName','CFBundleExecutable','CFBundlePackageType',
               'CFBundleShortVersionString','CFBundleVersion','LSMinimumSystemVersion',
               'MinimumOSVersion','CFBundleSupportedPlatforms','UIRequiredDeviceCapabilities')
    values={}
    for key in whitelist:
        v=obj.get(key)
        if isinstance(v,str):values[key]=v[:1024]
        elif isinstance(v,(bool,int,float)):values[key]=v
        elif isinstance(v,(tuple,list)):
            values[key]=[x[:512] if isinstance(x,str) else x for x in v[:50] if isinstance(x,(str,int,float,bool))]
    url_schemes=[]
    for item in obj.get('CFBundleURLTypes',[]) if isinstance(obj.get('CFBundleURLTypes',[]),list) else []:
        if isinstance(item,dict) and isinstance(item.get('CFBundleURLSchemes'),list):
            url_schemes.extend(str(x)[:128] for x in item['CFBundleURLSchemes'][:20])
    return {'format':'apple-info-plist','declared_properties':values,'url_schemes':url_schemes[:100],
            'key_count':len(obj),'coverage':'Bundle Info.plist declarations only; no app behavior or code signatures'}


def main(argv=None)->int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('path',type=Path);ap.add_argument('-o','--output',type=Path)
    a=ap.parse_args(argv)
    try:
        if a.path.is_symlink() or not a.path.is_file() or a.path.stat().st_size>MAX_BYTES:
            raise ManifestError('regular bounded file required')
        data=a.path.read_bytes()
        parsed=parse_plist(data) if a.path.suffix.lower()=='.plist' else parse_android_manifest(data)
        s=json.dumps(parsed,indent=2,ensure_ascii=False)+'\n'
        if a.output:
            if a.output.resolve()==a.path.resolve():raise ManifestError('output aliases source')
            write_exclusive(a.output,s,[a.path])
        else:print(s,end='')
        return 0 if not parsed.get('truncated_output') else 3
    except (ManifestError,OSError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
