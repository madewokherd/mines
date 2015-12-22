
import haxe.ds.*;

private class Item<T> {
    public var value:T;
    public var next:Item<T>;
    public function new() { };
}

class HashSet<K:{ function hashCode():Int; function equals(key:K):Bool; }> {

    /* None of the "standard" Haxe data structures I can find will resolve
     * collisions based on an equality operator. This is unacceptable because
     * I can't guarantee a unique integer key. But for now I don't want to
     * rewrite it and have to find efficient implementations for each platform,
     * so for now I'll just implement my own collision resolution on
     * top of what's there. */

    var buckets:IntMap<Item<K>>;
    public var count(default, null):Int;

    public function new() {
        buckets = new IntMap<Item<K>>();
        count = 0;
    }

    public function contains(key:K):Bool {
        var hashcode = key.hashCode();
        var bucket = buckets.get(hashcode);
        while (bucket != null) {
            if (bucket.value == key || bucket.value.equals(key))
                return true;
            bucket = bucket.next;
        }
        return false;
    }

    public function add(key:K):Bool {
        var hashcode = key.hashCode();
        var bucket = buckets.get(hashcode);
        var node = bucket;
        while (node != null) {
            if (node.value == key || node.value.equals(key))
                return true;
            node = node.next;
        }
        node = new Item<K>();
        node.value = key;
        node.next = bucket;
        buckets.set(hashcode, node);
        count++;
        return false;
    }

    public function remove(key:K):Bool {
        var hashcode = key.hashCode();
        var bucket = buckets.get(hashcode);
        if (bucket != null) {
            if (bucket.value == key || bucket.value.equals(key))
            {
                if (bucket.next == null) buckets.remove(hashcode);
                else buckets.set(hashcode, bucket.next);
                count--;
                return true;
            }
            while (bucket.next != null) {
                if (bucket.next.value == key || bucket.next.value.equals(key))
                {
                    bucket.next = bucket.next.next;
                    count--;
                    return true;
                }
                bucket = bucket.next;
            }
        }
        return false;
    }
}

