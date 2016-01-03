
class IntSetTest extends haxe.unit.TestCase {
    public function testAddRemove() {
        var s = new IntSet();
        assertFalse(s.contains(-10));
        assertFalse(s.contains(3));
        assertFalse(s.contains(100));
        assertFalse(s.contains(50));
        s.remove(100);
        assertFalse(s.contains(-10));
        assertFalse(s.contains(3));
        assertFalse(s.contains(100));
        assertFalse(s.contains(50));
        s.add(3);
        assertFalse(s.contains(-10));
        assertTrue(s.contains(3));
        assertFalse(s.contains(100));
        assertFalse(s.contains(50));
        s.add(100);
        assertFalse(s.contains(-10));
        assertTrue(s.contains(3));
        assertTrue(s.contains(100));
        assertFalse(s.contains(50));
        s.add(-10);
        assertTrue(s.contains(-10));
        assertTrue(s.contains(3));
        assertTrue(s.contains(100));
        assertFalse(s.contains(50));
        s.remove(3);
        assertTrue(s.contains(-10));
        assertFalse(s.contains(3));
        assertTrue(s.contains(100));
        assertFalse(s.contains(50));
        s.remove(-10);
        assertFalse(s.contains(-10));
        assertFalse(s.contains(3));
        assertTrue(s.contains(100));
        assertFalse(s.contains(50));
        s.remove(100);
        assertFalse(s.contains(-10));
        assertFalse(s.contains(3));
        assertFalse(s.contains(100));
        assertFalse(s.contains(50));
    }
}

