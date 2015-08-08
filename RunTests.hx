
class RunTests {
    static function main() {

#if node
        function t(v:Dynamic) {
            untyped console.log(v);
        }

        haxe.unit.TestRunner.print = t;
#end

        var r = new haxe.unit.TestRunner();
        r.add(new IntSetTest());
        if (!r.run()) {
#if node
            untyped process.exit(1);
#else
            Sys.exit(1);
#end
        }
    }
}
