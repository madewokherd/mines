
import haxe.ds.*;

#if js
private abstract IntArray(js.html.Uint32Array) {
    static inline public var bits_per_item = 32;
    static inline public var item_shift = 5;
    
    public inline function new(size:Int) {
        this = new js.html.Uint32Array(size);
    }

    public inline function copy_range(dst_offset, src:IntArray, src_offset, length)
    {
        this.set(src.get_real().subarray(src_offset, src_offset+length), dst_offset);
    }

    public inline function copy_from(dst_offset, src:IntArray)
    {
        this.set(src.get_real(), dst_offset);
    }

    public var length(get, never):Int;

    public inline function get_length() {
        return this.length;
    }

    @:arrayAccess
    public inline function get(ofs) {
        return this[ofs];
    }

    @:arrayAccess
    public inline function set(ofs, value) {
        this[ofs] = value;
        return value;
    }

    private static var debruijn_multiplier:Int = 0x4653adf;
    private static var debruijn_table:Array<Int> = [0, 1, 2, 6, 3, 11, 7, 16, 4, 14, 12, 21, 8, 23, 17, 26, 31, 5, 10, 15, 13, 20, 22, 25, 30, 9, 19, 24, 29, 18, 28, 27];

    public static function least_set_bit(x:Int):Int {
        x = x & (-x); // clear all bits except the least set bit
        var index = ((x * debruijn_multiplier) >> 27) & 31;
        return debruijn_table[index];
    }

    public static function count_set_bits(x:Int):Int {
        x = x - ((x >> 1) & 0x55555555);
        x = (x & 0x33333333) + ((x >> 2) & 0x33333333);
        x = (x + (x >> 4)) & 0x0f0f0f0f;
        x = (x + (x >> 8)) & 0x00ff00ff;
        x = (x + (x >> 16)) & 0x0000ffff;
        return x;
    }

#else

// Vector-based implementation
#if 0 // UInt64 in cpp isn't usable :(
private abstract IntArray(haxe.ds.Vector<cpp.UInt64>) {
    static inline public var bits_per_item = 64;
    static inline public var item_shift = 6;
    
    public inline function new(size:Int) {
        this = new haxe.ds.Vector<cpp.UInt64>(size);
    }

    private static var debruijn_multiplier:cpp.UInt64 = 0x218a392cd3d5dbf;
    private static var debruijn_table:Array<Int> = [0, 1, 2, 7, 3, 13, 8, 19, 4, 25, 14, 28, 9, 34, 20, 40, 5, 17, 26, 38, 15, 46, 29, 48, 10, 31, 35, 54, 21, 50, 41, 57, 63, 6, 12, 18, 24, 27, 33, 39, 16, 37, 45, 47, 30, 53, 49, 56, 62, 11, 23, 32, 36, 44, 52, 55, 61, 22, 43, 51, 60, 42, 59, 58];

    public static function least_set_bit(x:cpp.UInt64):Int {
        x = x & (-x); // clear all bits except the least set bit
        var index = ((x * debruijn_multiplier) >> 58) & 63;
        return debruijn_table[index];
    }
#else
private abstract IntArray(haxe.ds.Vector<Int>) {
    static inline public var bits_per_item = 32;
    static inline public var item_shift = 5;
    
    public inline function new(size:Int) {
        this = new haxe.ds.Vector<Int>(size);
    }

    private static var debruijn_multiplier:Int = 0x4653adf;
    private static var debruijn_table:Array<Int> = [0, 1, 2, 6, 3, 11, 7, 16, 4, 14, 12, 21, 8, 23, 17, 26, 31, 5, 10, 15, 13, 20, 22, 25, 30, 9, 19, 24, 29, 18, 28, 27];

    public static function least_set_bit(x:Int):Int {
        x = x & (-x); // clear all bits except the least set bit
        var index = ((x * debruijn_multiplier) >> 27) & 31;
        return debruijn_table[index];
    }

    public static function count_set_bits(x:Int):Int {
        x = x - ((x >> 1) & 0x55555555);
        x = (x & 0x33333333) + ((x >> 2) & 0x33333333);
        x = (x + (x >> 4)) & 0x0f0f0f0f;
        x = (x + (x >> 8)) & 0x00ff00ff;
        x = (x + (x >> 16)) & 0x0000ffff;
        return x;
    }
#end

    public inline function copy_range(dst_offset, src:IntArray, src_offset, length)
    {
        haxe.ds.Vector.blit(src.get_real(), src_offset, this, dst_offset, length);
    }

    public inline function copy_from(dst_offset, src:IntArray)
    {
        copy_range(dst_offset, src, 0, src.length);
    }

    public var length(get, never):Int;

    public inline function get_length() {
        return this.length;
    }

    @:arrayAccess
    public inline function get(ofs) {
        return this[ofs];
    }

    @:arrayAccess
    public inline function set(ofs, value) {
        this[ofs] = value;
        return value;
    }

// end Vector-based implementation

#end

    private inline function get_real() {
        return this;
    }
}

class IntSet {
    static inline public var item_mask = IntArray.bits_per_item-1;

    /* Allocated space */
    var blocks : IntArray;
    var blocks_start : Int;

    /* Nonzero range within allocated space */
    var first_block : Int;
    var end_block : Int;

    var hash_code_cached : Bool;
    var hash_code : Int;

    var _count_cached : Bool;
    var _count : Int;
    public var count(get, never):Int;

    public function new() {
        blocks = null;
        blocks_start = 0;

        first_block = 0;
        end_block = 0;

        hash_code_cached = true;
        hash_code = 0;

        _count_cached = true;
        _count = 0;
    }

    private inline function modified() {
        hash_code_cached = false;
        _count_cached = false;
    }

    private static inline function blockof(x:Int) {
        return x >> IntArray.item_shift;
    }

    private static inline function shiftof(x:Int) {
        return x & item_mask;
    }

    private static inline function min(x:Int, y:Int) {
        if (x < y)
            return x;
        else
            return y;
    }

    private static inline function max(x:Int, y:Int) {
        if (x > y)
            return x;
        else
            return y;
    }

    private inline function get_block(block) {
        return blocks[block-blocks_start];
    }

    private inline function set_block(block, val) {
        blocks[block-blocks_start] = val;
    }

    public function alloc_range(first, last) {
        var range_first_block = blockof(first);
        var range_end_block = blockof(last)+1;
        if (blocks == null || end_block <= first_block) {
            blocks_start = range_first_block;
            blocks = new IntArray(range_end_block-range_first_block);
        }
        else {
            var blocks_end = blocks_start + blocks.get_length();
            if (range_first_block < blocks_start || range_end_block > blocks_end) {
                /* check e.g. first_block instead of blocks_start so we don't allocate unused space */
                var new_blocks_start = min(range_first_block, first_block);
                var new_blocks_end = max(range_end_block, end_block);

                var new_blocks = new IntArray(new_blocks_end - new_blocks_start);
                new_blocks.copy_range(first_block - new_blocks_start, blocks, first_block - blocks_start, end_block - first_block);
                blocks_start = new_blocks_start;
                blocks = new_blocks;
            }
        }
    }

    private function mark_block_used(block) {
        if (end_block <= first_block) {
            first_block = block;
            end_block = block+1;
        }
        else if (first_block > block) {
            first_block = block;
        }
        else if (end_block < block+1) {
            end_block = block+1;
        }
    }

    private function mark_block_maybe_unused(block) {
        if (block == first_block) {
            while (first_block < end_block && get_block(first_block) == 0)
                first_block++;
        }
        else if (block == end_block-1) {
            while (first_block < end_block && get_block(end_block-1) == 0)
                end_block--;
        }
    }

    public function add(x) {
        var block = blockof(x);
        alloc_range(x, x);
        var bit_mask = 1 << shiftof(x);
        set_block(block, get_block(block)|bit_mask);
        mark_block_used(block);
        modified();
    }

    public function remove(x) {
        var block = blockof(x);
        if (block >= first_block && block < end_block)
        {
            var bit_mask = 1 << shiftof(x);
            set_block(block, get_block(block)&(~bit_mask));
            mark_block_maybe_unused(block);
            modified();
        }
    }

    public function first() : Int {
        if (end_block <= first_block)
            return -1;
        var result = first_block << IntArray.item_shift;
        result += IntArray.least_set_bit(get_block(first_block));
        return result;
    }

    public function contains(x) {
        var block = blockof(x);
        if (block < first_block || block >= end_block)
            return false;
        var bit_mask = 1 << shiftof(x);
        return (get_block(block) & bit_mask) != 0;
    }

    public function hashCode() : Int {
        if (!hash_code_cached) {
            if (end_block <= first_block) {
                hash_code = 0;
            }
            else {
                hash_code = first_block & 2147483647;
                var block = first_block;
                while (block < end_block) {
                    hash_code = ((33 * hash_code) ^ (get_block(block) % 2147483647)) & 2147483647;
                    block++;
                }
            }
            hash_code_cached = true;
        }
        return hash_code;
    }

    public function get_count() : Int {
        if (!_count_cached) {
            var result : Int;
            if (end_block <= first_block) {
                result = 0;
            }
            else {
                result = 0;
                var block = first_block;
                while (block < end_block) {
                    result += IntArray.count_set_bits(get_block(block));
                    block++;
                }
            }
            _count = result;
            _count_cached = true;
        }
        return _count;
    }

    public function equals(other:IntSet) : Bool {
        if ((end_block <= first_block) || (other.end_block <= other.first_block))
            return (end_block <= first_block) && (other.end_block <= other.first_block);

        if (first_block != other.first_block || end_block != other.end_block)
            return false;

        var i = first_block - blocks_start;
        var j = first_block - other.blocks_start;
        var end = end_block - blocks_start;

        while (i < end) {
            if (blocks[i] != other.blocks[j])
                return false;
            i++;
            j++;
        }

        return true;
    }
}

