#!/usr/bin/env python3
"""Independent, non-executing EVM bytecode decoder and candidate dispatcher finder.

Opcode availability differs across forks and EVM versions. A PUSH4 constant is
not automatically a function selector; inferred paths are candidates only.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from json_writer import write_exclusive

MAX_BYTECODE=32*1024*1024
MAX_INSTRUCTIONS=300000

class EVMError(ValueError):pass

OPS={
 0x00:'STOP',0x01:'ADD',0x02:'MUL',0x03:'SUB',0x04:'DIV',0x05:'SDIV',0x06:'MOD',0x07:'SMOD',
 0x08:'ADDMOD',0x09:'MULMOD',0x0a:'EXP',0x0b:'SIGNEXTEND',
 0x10:'LT',0x11:'GT',0x12:'SLT',0x13:'SGT',0x14:'EQ',0x15:'ISZERO',0x16:'AND',0x17:'OR',
 0x18:'XOR',0x19:'NOT',0x1a:'BYTE',0x1b:'SHL',0x1c:'SHR',0x1d:'SAR',0x20:'KECCAK256',
 0x30:'ADDRESS',0x31:'BALANCE',0x32:'ORIGIN',0x33:'CALLER',0x34:'CALLVALUE',0x35:'CALLDATALOAD',
 0x36:'CALLDATASIZE',0x37:'CALLDATACOPY',0x38:'CODESIZE',0x39:'CODECOPY',0x3a:'GASPRICE',
 0x3b:'EXTCODESIZE',0x3c:'EXTCODECOPY',0x3d:'RETURNDATASIZE',0x3e:'RETURNDATACOPY',
 0x3f:'EXTCODEHASH',0x40:'BLOCKHASH',0x41:'COINBASE',0x42:'TIMESTAMP',0x43:'NUMBER',
 0x44:'PREVRANDAO',0x45:'GASLIMIT',0x46:'CHAINID',0x47:'SELFBALANCE',0x48:'BASEFEE',
 0x49:'BLOBHASH',0x4a:'BLOBBASEFEE',0x50:'POP',0x51:'MLOAD',0x52:'MSTORE',0x53:'MSTORE8',
 0x54:'SLOAD',0x55:'SSTORE',0x56:'JUMP',0x57:'JUMPI',0x58:'PC',0x59:'MSIZE',0x5a:'GAS',
 0x5b:'JUMPDEST',0x5c:'TLOAD',0x5d:'TSTORE',0x5e:'MCOPY',0x5f:'PUSH0',
 0xf0:'CREATE',0xf1:'CALL',0xf2:'CALLCODE',0xf3:'RETURN',0xf4:'DELEGATECALL',
 0xf5:'CREATE2',0xfa:'STATICCALL',0xfd:'REVERT',0xfe:'INVALID',0xff:'SELFDESTRUCT'
}


def parse_hex(text:str)->bytes:
    cleaned=text.strip()
    if cleaned.startswith('0x'):cleaned=cleaned[2:]
    if not cleaned or len(cleaned)%2 or not re.fullmatch(r'[0-9a-fA-F]+',cleaned):
        raise EVMError('expected even-length hex EVM bytes (optional 0x prefix)')
    if len(cleaned)//2>MAX_BYTECODE:raise EVMError('byte budget exceeded')
    return bytes.fromhex(cleaned)


def analyze_evm(data:bytes,include_instructions=False):
    if len(data)>MAX_BYTECODE:raise EVMError('byte budget exceeded')
    pc=0;inst=[];jumpdests=[];selectors=[];external=[];unknown=[]
    while pc<len(data):
        if len(inst)>=MAX_INSTRUCTIONS:raise EVMError('instruction budget exceeded')
        op=data[pc];label=OPS.get(op)
        if 0x60<=op<=0x7f:label='PUSH'+str(op-0x5f)
        elif 0x80<=op<=0x8f:label='DUP'+str(op-0x7f)
        elif 0x90<=op<=0x9f:label='SWAP'+str(op-0x8f)
        elif 0xa0<=op<=0xa4:label='LOG'+str(op-0xa0)
        if label is None:unknown.append({'offset':pc,'opcode':hex(op)})
        row={'pc':pc,'opcode':f'0x{op:02x}','mnemonic':label or 'UNKNOWN'}
        size=op-0x5f if 0x60<=op<=0x7f else 0
        if size:
            if pc+1+size>len(data):
                row['incomplete_push']=True
                row['available_bytes']=len(data)-(pc+1)
                inst.append(row)
                break
            immediate=data[pc+1:pc+1+size]
            row['immediate']='0x'+immediate.hex()
            if size==4:selectors.append({'pc':pc,'selector':'0x'+immediate.hex(),'evidence':'PUSH4 constant; may not be ABI selector'})
        if op==0x5b:jumpdests.append(pc)
        if op in (0xf0,0xf1,0xf2,0xf4,0xf5,0xfa,0xff,0x55):
            external.append({'pc':pc,'operation':row['mnemonic'], 'effects':'candidate only; stack values unresolved'})
        inst.append(row);pc+=1+size
    complete=not unknown and not any(i.get('incomplete_push') for i in inst)
    out={'format':'evm-bytecode','sha256':hashlib.sha256(data).hexdigest(),
         'byte_size':len(data),'instruction_count':len(inst),
         'jumpdest_offsets':jumpdests,'candidate_selectors':selectors,
         'potential_side_effects':external,'unsupported_opcodes':unknown[:100],
         'complete_decode':complete,'coverage':'bytecode token walk; does not resolve stack, ABI, state, dispatch or fork validity'}
    if include_instructions:out['instructions']=inst
    return out


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('path',type=Path);p.add_argument('-o','--output',type=Path)
    p.add_argument('--hex',action='store_true',help='input is hex text instead of raw .evm bytes')
    p.add_argument('--include-instructions',action='store_true')
    a=p.parse_args(argv)
    try:
        if not a.path.is_file() or a.path.is_symlink():raise EVMError('regular non-symlink file required')
        if a.path.stat().st_size>MAX_BYTECODE:raise EVMError('byte budget exceeded')
        raw=a.path.read_bytes()
        if a.hex:raw=parse_hex(raw.decode('ascii'))
        out=analyze_evm(raw,a.include_instructions)
        s=json.dumps(out,indent=2,ensure_ascii=False)+'\n'
        if a.output:
            if a.output.resolve()==a.path.resolve():raise EVMError('output aliases input')
            write_exclusive(a.output,s,[a.path])
        else:print(s,end='')
        return 0 if out['complete_decode'] else 3
    except (EVMError,OSError,UnicodeError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
