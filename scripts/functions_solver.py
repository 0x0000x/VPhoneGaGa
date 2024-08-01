# this pattern to traverse the entire code segment, 
# find their location, 
# and then use Unicorn to simulate the execution engine to solve it:
#'''
# Let me briefly explain the idea: 
# After the code is decompiled sentence by sentence, 
# the script will identify the fixed pattern of the decryption loop,
# and then match all instructions except jump instructions as long as possible forward 
# (in the direction of small addresses), so that the register state when the string is decrypted can be restored to the greatest extent. 
#  Every time such a pattern is recognized, let Unicorn run the code before the loop first. At this time, the characters in the stack have been placed,
#  and then start the recorder that writes to memory, and then run the loop code, so that the characters on the stack are decrypted one by one, 
#   and we also know the decrypted character sequence through the hook. 
# After running the script, a lot of strings were indeed decrypted:

from sys import argv 
from elftools.elf.elffile import ELFFile, Section 
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM 
from unicorn import * 
from unicorn.arm64_const import *

assert  len(argv) >= 2
so = ELFFile( open (argv[ 1 ], 'rb' )) 
section: Section = so.get_section_by_name( '.text' ) 
base: int = section.header.sh_addr 
code = section.data()

class State:
    def __init__(self):
        self._ops = set('mov str movz ldp ldr adrp add sub movi ldrh and strh orr ldrb subs ldurb ldur strb eor sturb lsr movn movk csinc madd ubfx asr mul cmn lsl nop cinc ext sxtw smaddl fcvtzs udiv msub smull ldrsw smulh adds mvn neg sturh umull csneg umov sshll sdiv ldrsb stlrb bfi ands sxtb ushl umaddl umulh sxth bic orn ror rev sbfiz ldursw bfxil sbfx ldpsw ldrsh'.split())
        self._pat = ('ldrb ldr add eor strb add cmp b.ne', 'ldrb ldr eor strb add cmp b.ne', 'ldrb ldur add eor strb add cmp b.ne', 'ldrb ldur eor strb add cmp b.ne')
        self._pat = tuple(tuple(item.split()) for item in self._pat)
        self._step = [0] * len(self._pat)
        self._set = set()

    def update(self, addr, op):
        match = None
        if op in self._ops:
            self._set.add(addr)
        for i, pat in enumerate(self._pat):
            if op == pat[self._step[i]]:
                self._step[i] += 1
            else: self._step[i] = 0
            if self._step[i] == len(pat):
                self._step[i] = 0
                assert match is None
                match = i
        if match is not None:
            pos = None
            end = addr - 4 * len(self._pat[match]) + 4
            for p in range(end - 4, -4, -4):
                if p in self._set:
                    pos = p
                else: break
            assert pos is not None
            return pos, end

class DataRecorder:
    def __init__(self):
        self.reset()

    def reset(self):
        self._current = None
        self._data = None
        self.enable = False

    def hit(self, addr, data):
        if self.enable:
            if self._current is None:
                self._current = addr
                self._data = bytearray()
            else:
                self._current += 1
                assert addr == self._current
            self._data.append(data)

    def finish(self):
        try:
            data = self._data.decode('utf-8')
        except UnicodeDecodeError:
            data = bytes(self._data)
        self.reset()
        return data

def onmemwrite(uc: Uc, kind: int, addr: int, size: int, value: int, dr: DataRecorder):
    if kind == UC_MEM_WRITE:
        assert size == 1 or not dr.enable
        dr.hit(addr, value)
        uc.mem_write(addr, int.to_bytes(value & (1 << (size << 3)) - 1, size, 'little'))
    else: assert 0

uc = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
uc.mem_map(base, (len(code) + 0xFFF) // 0x1000 * 0x1000, UC_PROT_READ | UC_PROT_EXEC)
uc.mem_write(base, code)
stack = (base + len(code) + 0x1000) // 0x1000 * 0x1000
stack_size = 0x100000
uc.mem_map(stack, stack_size, UC_PROT_READ | UC_PROT_WRITE)
uc.reg_write(UC_ARM64_REG_SP, stack)
dr = DataRecorder()
uc.hook_add(UC_HOOK_MEM_WRITE, onmemwrite, dr, stack, stack + stack_size - 1)

state = State()
cs = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
current = base

while current != base + len (code):
    for addr, _, op, operand in cs.disasm_lite(code[current-base:], current):
        current = addr         
        result = state.update(addr, op) 
        if result is not None :             
            start, mid = result             
            end = addr + 4
            try:
                print( 'found encrypted string at 0x%X 0x%X 0x%X: ' % (*result, end), end= '' )                 
                uc.emu_start(start, mid)
                dr.enable = True                 
                uc.emu_start(mid, end) 
                print ( repr (dr.finish())) 
            except (UcError, AssertionError) as e: 
                print ( repr (e))                 
                dr.reset()     
                current += 4
        