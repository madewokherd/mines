
private class TestValue {
    public var val:Int;

    public function new(val:Int) {
        this.val = val;
    }

    public function hashCode():Int {
        return val & ~3; /* intentionally cause collisions */
    }

    public function equals(other:TestValue):Bool {
        return this.val == other.val;
    }
}

class HashSetTest extends haxe.unit.TestCase {
    public function testAddRemove() {
        var set = new HashSet<TestValue>();
        assertEquals(0, set.count);

        var zero = new TestValue(0);
        var one = new TestValue(1);
        var two = new TestValue(2);
        var three = new TestValue(3);
        var five = new TestValue(5);

        assertFalse(set.contains(zero));
        assertFalse(set.contains(one));
        assertFalse(set.contains(two));
        assertFalse(set.contains(three));
        assertFalse(set.contains(five));

        assertFalse(set.add(two));
        assertFalse(set.contains(zero));
        assertFalse(set.contains(one));
        assertTrue(set.contains(two));
        assertFalse(set.contains(three));
        assertFalse(set.contains(five));
        assertEquals(1, set.count);

        assertTrue(set.add(two));
        assertFalse(set.contains(zero));
        assertFalse(set.contains(one));
        assertTrue(set.contains(two));
        assertFalse(set.contains(three));
        assertFalse(set.contains(five));
        assertEquals(1, set.count);

        assertFalse(set.add(three));
        assertFalse(set.contains(zero));
        assertFalse(set.contains(one));
        assertTrue(set.contains(two));
        assertTrue(set.contains(three));
        assertFalse(set.contains(five));
        assertEquals(2, set.count);

        assertFalse(set.add(one));
        assertFalse(set.contains(zero));
        assertTrue(set.contains(one));
        assertTrue(set.contains(two));
        assertTrue(set.contains(three));
        assertFalse(set.contains(five));
        assertEquals(3, set.count);

        assertFalse(set.remove(zero));
        assertTrue(set.remove(three));
        assertFalse(set.remove(five));
        assertFalse(set.contains(zero));
        assertTrue(set.contains(one));
        assertTrue(set.contains(two));
        assertFalse(set.contains(three));
        assertFalse(set.contains(five));
        assertEquals(2, set.count);

        assertFalse(set.add(five));
        assertFalse(set.contains(zero));
        assertTrue(set.contains(one));
        assertTrue(set.contains(two));
        assertFalse(set.contains(three));
        assertTrue(set.contains(five));
        assertEquals(3, set.count);

        assertFalse(set.remove(three));
        assertTrue(set.remove(two));
        assertFalse(set.contains(zero));
        assertTrue(set.contains(one));
        assertFalse(set.contains(two));
        assertFalse(set.contains(three));
        assertTrue(set.contains(five));
        assertEquals(2, set.count);

        assertTrue(set.remove(one));
        assertFalse(set.contains(zero));
        assertFalse(set.contains(one));
        assertFalse(set.contains(two));
        assertFalse(set.contains(three));
        assertTrue(set.contains(five));
        assertEquals(1, set.count);
    }
}

