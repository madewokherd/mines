
#if js
private abstract IntArray(js.html.Uint32Array) {
    static inline public var bits_per_item = 32;
    static inline public var item_shift = 4;
    
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

#else

// Vector-based implementation
#if hxcpp_api_level
private abstract IntArray(haxe.ds.Vector<cpp.Uint64>) {
    static inline public var bits_per_item = 64;
    static inline public var item_shift = 5;
    
    public inline function new(size:Int) {
        this = new haxe.ds.Vector<cpp.Int64>(size);
    }
#else
private abstract IntArray(haxe.ds.Vector<Int>) {
    static inline public var bits_per_item = 32;
    static inline public var item_shift = 4;
    
    public inline function new(size:Int) {
        this = new haxe.ds.Vector<Int>(size);
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

    public function new() {
        blocks = null;
        blocks_start = 0;

        first_block = 0;
        end_block = 0;
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
    }

    public function remove(x) {
        var block = blockof(x);
        if (block >= first_block && block < end_block)
        {
            var bit_mask = 1 << shiftof(x);
            set_block(block, get_block(block)&(~bit_mask));
            mark_block_maybe_unused(block);
        }
    }

    public function contains(x) {
        var block = blockof(x);
        if (block < first_block || block >= end_block)
            return false;
        var bit_mask = 1 << shiftof(x);
        return (get_block(block) & bit_mask) != 0;
    }
}

