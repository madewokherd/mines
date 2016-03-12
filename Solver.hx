
import haxe.ds.*;

class Solver {
    public var spaces(default, null) : IntSet;
    public var solved_spaces(default, null) : IntSet;
    public var solved_space_values(default, null) : IntSet;
    public var information(default, null) : HashSet<Information>;
    public var informations_by_space(default, null) : Vector<Information>;
    public var clear_spaces_to_add(default, null) : Array<Int>;
    public var mine_spaces_to_add(default, null) : Array<Int>;
    public var informations_to_add(default, null) : Array<Information>;

    public function new(spaces : IntSet, max_informations_for_space: Int) {
        this.spaces = spaces;
        this.solved_spaces = new IntSet();
        this.solved_space_values = new IntSet();
        this.information = new HashSet<Information>();
        this.informations_by_space = new Vector<Information>((spaces.last() - spaces.first()) * max_informations_for_space);
        this.clear_spaces_to_add = new Array<Int>();
        this.mine_spaces_to_add = new Array<Int>();
        this.informations_to_add = new Array<Information>();
    }
}
