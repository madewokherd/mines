
enum SolveResult {
    Solved; // There's exactly 1 solution, and it was successfully calculated
    Unsolveable;    // There is no solution
    Unknown;    // Could be 0, 1, or many solutions, did not do enough work to tell
    MultipleSolutions;  // There are many solutions
}

