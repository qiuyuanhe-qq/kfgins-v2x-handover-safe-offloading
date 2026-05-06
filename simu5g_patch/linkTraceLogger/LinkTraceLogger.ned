package simu5g.simulations.NR.networks;

simple LinkTraceLogger
{
    parameters:
        @class(LinkTraceLogger);
        string outputPath;
        double interval @unit(s) = default(1s);
}
