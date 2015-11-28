
class Information {
    public var spaces(default, null) : IntSet;
    public var count(default, null) : Int;

    public function new(spaces : IntSet, count : Int)
    {
        this.spaces = spaces;
        this.count = count;
    }
}
