package msc;

import clustering.KMeans;
import java.util.concurrent.TimeUnit;
import parser.TextTools;
import parser.WikiParser;

public class Msc {

    public static void main(String[] args) {
        long parseTimeStart = 0, parseTimeStop = 0, parseTimeDelta;
        WikiParser wp;
        KMeans km;
        
        wp = new WikiParser();
        
        parseTimeStart = System.nanoTime();
        wp.Parse();
        km = new KMeans(wp.getArticles());
        km.InitializeGroupCenters();
        km.CalculateDistances();
        parseTimeStop = System.nanoTime();
        parseTimeDelta = parseTimeStop - parseTimeStart;

//        TextTools.PrintArticles(wp.getArticles());

        System.out.println("Elapsed: " + TimeUnit.NANOSECONDS.toMillis(parseTimeDelta) + " ms");
    }
}
