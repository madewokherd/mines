
class Information {
    public var spaces(default, null) : IntSet;
    public var count(default, null) : Int;

    public function new(spaces : IntSet, count : Int)
    {
        this.spaces = spaces;
        this.count = count;
    }

    public function hashCode(): Int {
        return spaces.hashCode() + count;
    }

    public function equals(other: Information) : Bool {
        return count == other.count && (spaces == other.spaces || spaces.equals(other.spaces));
    }
}
