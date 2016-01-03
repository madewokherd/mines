
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

    public function testHash() {
        var s = new IntSet();

        var empty_hash = s.hashCode();

        s.alloc_range(5,10);
        
        assertEquals(empty_hash, s.hashCode());

        s.add(7);

        var seven_hash = s.hashCode();

        s.remove(7);

        assertEquals(empty_hash, s.hashCode());

        s.add(60);        

        var sixty_hash = s.hashCode();

        s.add(7);

        var sixty_seven_hash = s.hashCode();

        s.remove(60);

        assertEquals(seven_hash, s.hashCode());

        s.remove(7);

        assertEquals(empty_hash, s.hashCode());

        s = new IntSet();
        s.add(7);

        assertEquals(seven_hash, s.hashCode());

        s.add(60);

        assertEquals(sixty_seven_hash, s.hashCode());

        s.remove(7);

        assertEquals(sixty_hash, s.hashCode());
    }
}

