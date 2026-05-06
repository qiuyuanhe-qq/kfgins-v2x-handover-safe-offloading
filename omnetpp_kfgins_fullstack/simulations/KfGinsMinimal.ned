simple V2XTaskApp
{
    parameters:
        @class(V2XTaskApp);
        double taskInterval @unit(s) = default(1s);
        string tracePath = default("../data/trajectory.csv");
        string linkTracePath = default("../data/link_trace.csv");
        double cellSize = default(120);
        double gnssSigma = default(12);
        string algorithm = default("kfgins_risk");
}
network KfGinsMinimal
{
    submodules:
        app: V2XTaskApp { parameters: taskInterval = 1s; tracePath = "../data/trajectory.csv"; linkTracePath = "../data/link_trace.csv"; cellSize = 120; gnssSigma = 12; algorithm = default("kfgins_risk"); }
}
